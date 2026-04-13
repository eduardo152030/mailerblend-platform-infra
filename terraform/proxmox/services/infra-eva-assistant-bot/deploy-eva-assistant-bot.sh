#!/bin/bash
# deploy-eva-assistant-bot.sh
# Despliegue IaC-friendly de EVA Assistant Bot
#
# Uso:
#   ./services/infra-eva-assistant-bot/deploy-eva-assistant-bot.sh
#
# Debug útil:
#   ssh root@192.168.1.122 "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'"
#   ssh root@192.168.1.122 "cd /opt/infra-eva-assistant-bot && docker compose logs --no-color --tail=100 eva-api"
#   ssh root@192.168.1.122 "cd /opt/infra-eva-assistant-bot && docker compose logs --no-color --tail=100 eva-scheduler"
#   ssh root@192.168.1.122 "cd /opt/infra-eva-assistant-bot && docker compose logs --no-color --tail=100 eva-sync"
#   ssh root@192.168.1.122 "curl -sS http://127.0.0.1:8001/health"
#   ssh root@192.168.1.122 "curl -sS http://127.0.0.1:8001/ready"

set -euo pipefail

EVA_HOST="${EVA_HOST:-192.168.1.122}"
SSH_OPTS="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR"

LOCAL_SERVICE_DIR="services/infra-eva-assistant-bot"
LOCAL_COMPOSE_DIR="${LOCAL_SERVICE_DIR}/compose"
REMOTE_BASE_DIR="/opt/infra-eva-assistant-bot"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🤖 Desplegando Eva Assistant Bot"
echo "  📍 Host: ${EVA_HOST}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# ── 0. Validar .env ────────────────────────────────────────────────────────
echo "🔍 0/6 Validando .env..."
ENV_FILE="${LOCAL_COMPOSE_DIR}/.env"

if [ ! -f "$ENV_FILE" ]; then
  echo "❌ Error: No se encontró ${ENV_FILE}"
  echo "   Copia .env.example → .env y rellena los valores"
  exit 1
fi

REQUIRED_VARS=(
  "TELEGRAM_BOT_TOKEN"
  "POSTGRES_DB"
  "POSTGRES_USER"
  "POSTGRES_PASSWORD"
  "ANTHROPIC_API_KEY"
  "FOCALBOARD_TOKEN"
  "FOCALBOARD_BOARD_ID"
)

MISSING=()
for VAR in "${REQUIRED_VARS[@]}"; do
  if ! grep -q "^${VAR}=" "$ENV_FILE" && ! grep -q "^${VAR}=\"" "$ENV_FILE"; then
    MISSING+=("$VAR")
  fi
done

if [ ${#MISSING[@]} -gt 0 ]; then
  echo "❌ Error: faltan variables en ${ENV_FILE}:"
  printf '   - %s\n' "${MISSING[@]}"
  exit 1
fi
echo "   ✅ .env válido (${#REQUIRED_VARS[@]} variables OK)"
echo ""

# ── 1. Preparar directorios remotos ───────────────────────────────────────
echo "📁 1/6 Preparando directorios remotos..."
ssh ${SSH_OPTS} root@${EVA_HOST} << 'ENDSSH'
set -euo pipefail
mkdir -p /opt/infra-eva-assistant-bot/{api,focalboard/data/files,postgres/{init,migrations},persona}
ENDSSH
echo ""

# ── 2. Sincronizar ficheros ────────────────────────────────────────────────
echo "📦 2/6 Sincronizando archivos..."

# .env — fuente de verdad: compose/.env → servidor
rsync -av -e "ssh ${SSH_OPTS}" \
  "${LOCAL_COMPOSE_DIR}/.env" \
  root@${EVA_HOST}:${REMOTE_BASE_DIR}/.env

rsync -av -e "ssh ${SSH_OPTS}" \
  "${LOCAL_COMPOSE_DIR}/docker-compose.yml" \
  root@${EVA_HOST}:${REMOTE_BASE_DIR}/docker-compose.yml

# Código API (incluyendo ai_parser.py, sync_service.py, etc.)
rsync -av --delete -e "ssh ${SSH_OPTS}" \
  "${LOCAL_COMPOSE_DIR}/api/" \
  root@${EVA_HOST}:${REMOTE_BASE_DIR}/api/

# Persona configs (ficheros JSON de personalidad por usuario)
if [ -d "${LOCAL_COMPOSE_DIR}/persona" ]; then
  rsync -av -e "ssh ${SSH_OPTS}" \
    "${LOCAL_COMPOSE_DIR}/persona/" \
    root@${EVA_HOST}:${REMOTE_BASE_DIR}/persona/
  echo "   ✅ persona configs sincronizados"
fi

# Focalboard config (excluir data/)
rsync -av --delete -e "ssh ${SSH_OPTS}" \
  --exclude 'data/' \
  "${LOCAL_COMPOSE_DIR}/focalboard/" \
  root@${EVA_HOST}:${REMOTE_BASE_DIR}/focalboard/

# Migraciones SQL
rsync -av --delete -e "ssh ${SSH_OPTS}" \
  "${LOCAL_COMPOSE_DIR}/postgres/init/" \
  root@${EVA_HOST}:${REMOTE_BASE_DIR}/postgres/init/

rsync -av --delete -e "ssh ${SSH_OPTS}" \
  "${LOCAL_COMPOSE_DIR}/postgres/migrations/" \
  root@${EVA_HOST}:${REMOTE_BASE_DIR}/postgres/migrations/
echo ""

# ── 3. Focalboard: permisos + renderizar config.json desde template ───────
echo "🔐 3/6 Configurando Focalboard (permisos + config.json)..."
ssh ${SSH_OPTS} root@${EVA_HOST} << 'ENDSSH'
set -euo pipefail
cd /opt/infra-eva-assistant-bot

# Permisos data/
mkdir -p /opt/infra-eva-assistant-bot/focalboard/data/files
chmod -R 777 /opt/infra-eva-assistant-bot/focalboard/data

# Limpiar si config.json es un directorio (bug de Docker bind mount)
if [ -d "focalboard/config.json" ]; then
  echo "⚠️  config.json es un directorio — limpiando..."
  rm -rf focalboard/config.json
fi

# Renderizar config.json desde template con las variables del .env
if [ -f "focalboard/config.json.tpl" ]; then
  set -a && source .env && set +a
  envsubst < focalboard/config.json.tpl > focalboard/config.json
  echo "✅ config.json renderizado"
  cat focalboard/config.json
else
  echo "❌ No se encontró focalboard/config.json.tpl"
  exit 1
fi
ENDSSH
echo ""

# ── 4. Build + Deploy ──────────────────────────────────────────────────────
echo "🔨 4/6 Build + Deploy..."
ssh ${SSH_OPTS} root@${EVA_HOST} << 'ENDSSH'
set -euo pipefail
cd /opt/infra-eva-assistant-bot

# Forzar rebuild de la imagen para incluir cambios de código
docker compose build --no-cache eva-api eva-scheduler eva-sync
docker compose up -d
ENDSSH
echo ""

# ── 5. Verificar servicios ─────────────────────────────────────────────────
echo "⏳ 5/6 Verificando servicios (espera 10s)..."
sleep 10

ssh ${SSH_OPTS} root@${EVA_HOST} << 'ENDSSH'
set -euo pipefail
cd /opt/infra-eva-assistant-bot

echo "📊 Estado de contenedores:"
docker compose ps

echo ""
echo "🧠 AI Parser activo:"
docker exec eva-api env | grep -E "ANTHROPIC_API_KEY|EVA_AI_PARSER" | sed 's/=.*/=***/'

echo ""
echo "🔗 Health checks:"
curl -sS http://127.0.0.1:8001/health && echo " ← eva-api OK"
curl -sS http://127.0.0.1:8001/ready  && echo " ← eva-api ready"

echo ""
echo "📜 Logs eva-api (últimas 15 líneas):"
docker logs --tail 15 eva-api || true

echo ""
echo "📜 Logs eva-sync (últimas 10 líneas):"
docker logs --tail 10 eva-sync || true
ENDSSH
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅ Despliegue completado"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🌐 EVA API:       http://192.168.1.122:8001"
echo "📋 Focalboard:    https://infra-focalboard.mailerblend.com"
echo ""
echo "📖 Comandos útiles:"
echo "  Logs API:       ssh root@192.168.1.122 \"cd /opt/infra-eva-assistant-bot && docker compose logs --no-color --tail=100 eva-api\""
echo "  Logs scheduler: ssh root@192.168.1.122 \"cd /opt/infra-eva-assistant-bot && docker compose logs --no-color --tail=100 eva-scheduler\""
echo "  Logs sync:      ssh root@192.168.1.122 \"cd /opt/infra-eva-assistant-bot && docker compose logs --no-color --tail=100 eva-sync\""
echo "  Estado:         ssh root@192.168.1.122 \"cd /opt/infra-eva-assistant-bot && docker compose ps\""
echo "  Reiniciar:      ssh root@192.168.1.122 \"cd /opt/infra-eva-assistant-bot && docker compose restart\""
#./services/infra-eva-assistant-bot/deploy-eva-assistant-bot.sh