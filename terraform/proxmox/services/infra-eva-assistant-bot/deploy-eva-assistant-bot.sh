#!/bin/bash
# deploy-eva-assistant-bot.sh
# Despliegue IaC-friendly de EVA Assistant Bot

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

ENV_FILE="${LOCAL_COMPOSE_DIR}/.env"

echo "🔍 0/6 Validando .env..."
if [ ! -f "$ENV_FILE" ]; then
  echo "❌ Error: No se encontró ${ENV_FILE}"
  exit 1
fi

REQUIRED_VARS=(
  "TELEGRAM_BOT_TOKEN"
  "DATABASE_URL"
  "POSTGRES_DB"
  "POSTGRES_USER"
  "POSTGRES_PASSWORD"
)

MISSING=()
for VAR in "${REQUIRED_VARS[@]}"; do
  if ! grep -q "^${VAR}=" "$ENV_FILE" && ! grep -q "^${VAR}=\"" "$ENV_FILE"; then
    MISSING+=("$VAR")
  fi
done

if [ ${#MISSING[@]} -gt 0 ]; then
  echo "❌ Error: faltan variables en ${ENV_FILE}:"
  printf ' - %s\n' "${MISSING[@]}"
  exit 1
fi
echo "   ✅ .env válido"
echo ""

echo "📁 1/6 Preparando directorios remotos..."
ssh ${SSH_OPTS} root@${EVA_HOST} <<'ENDSSH'
set -euo pipefail

mkdir -p /opt/infra-eva-assistant-bot
mkdir -p /opt/infra-eva-assistant-bot/api
mkdir -p /opt/infra-eva-assistant-bot/focalboard
mkdir -p /opt/infra-eva-assistant-bot/focalboard/data/files
mkdir -p /opt/infra-eva-assistant-bot/postgres/init
mkdir -p /opt/infra-eva-assistant-bot/postgres/migrations
ENDSSH
echo ""

echo "📦 2/6 Sincronizando archivos declarativos..."
rsync -av -e "ssh ${SSH_OPTS}" \
  "${LOCAL_COMPOSE_DIR}/.env" \
  root@${EVA_HOST}:${REMOTE_BASE_DIR}/.env

rsync -av -e "ssh ${SSH_OPTS}" \
  "${LOCAL_COMPOSE_DIR}/docker-compose.yml" \
  root@${EVA_HOST}:${REMOTE_BASE_DIR}/docker-compose.yml

rsync -av --delete -e "ssh ${SSH_OPTS}" \
  "${LOCAL_COMPOSE_DIR}/api/" \
  root@${EVA_HOST}:${REMOTE_BASE_DIR}/api/

rsync -av --delete -e "ssh ${SSH_OPTS}" \
  --exclude 'data/' \
  "${LOCAL_COMPOSE_DIR}/focalboard/" \
  root@${EVA_HOST}:${REMOTE_BASE_DIR}/focalboard/

rsync -av --delete -e "ssh ${SSH_OPTS}" \
  "${LOCAL_COMPOSE_DIR}/postgres/init/" \
  root@${EVA_HOST}:${REMOTE_BASE_DIR}/postgres/init/

rsync -av --delete -e "ssh ${SSH_OPTS}" \
  "${LOCAL_COMPOSE_DIR}/postgres/migrations/" \
  root@${EVA_HOST}:${REMOTE_BASE_DIR}/postgres/migrations/
echo ""

echo "🔐 3/6 Ajustando permisos runtime de Focalboard..."
ssh ${SSH_OPTS} root@${EVA_HOST} <<'ENDSSH'
set -euo pipefail

mkdir -p /opt/infra-eva-assistant-bot/focalboard/data/files
chmod -R 777 /opt/infra-eva-assistant-bot/focalboard/data
ENDSSH
echo ""

echo "🔨 4/6 Build + Deploy..."
ssh ${SSH_OPTS} root@${EVA_HOST} <<'ENDSSH'
set -euo pipefail
cd /opt/infra-eva-assistant-bot

docker compose build --no-cache eva-api eva-scheduler eva-sync
docker compose up -d
ENDSSH
echo ""

echo "🧪 5/6 Verificando servicios..."
sleep 8
ssh ${SSH_OPTS} root@${EVA_HOST} <<'ENDSSH'
set -euo pipefail
cd /opt/infra-eva-assistant-bot

echo "📊 Estado:"
docker compose ps

echo ""
echo "📜 Logs eva-api:"
docker logs --tail 20 eva-api || true

echo ""
echo "📜 Logs eva-scheduler:"
docker logs --tail 20 eva-scheduler || true

echo ""
echo "📜 Logs focalboard:"
docker logs --tail 20 focalboard || true
ENDSSH
echo ""

echo "✅ 6/6 Despliegue completado"

#./services/infra-eva-assistant-bot/deploy-eva-assistant-bot.sh