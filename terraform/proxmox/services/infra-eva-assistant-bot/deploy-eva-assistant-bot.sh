#!/bin/bash
# deploy-eva-assistant-bot.sh - Despliega Eva Assistant Bot al servidor
# Uso: ./deploy-eva-assistant-bot.sh
#      ./services/infra-eva-assistant-bot/scripts/deploy-eva-assistant-bot.sh
#
# Debug útil:
#   ssh root@192.168.1.122 'docker ps --filter name=eva'
#   ssh root@192.168.1.122 'docker logs --tail 50 eva-api'
#   ssh root@192.168.1.122 'docker logs --tail 50 eva-scheduler'
#   ssh root@192.168.1.122 'docker exec eva-api env | grep EVA'

set -e  # Exit on error

EVA_HOST="${EVA_HOST:-192.168.1.122}"
SSH_OPTS="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR"

LOCAL_API_PATH="services/infra-eva-assistant-bot/compose/api"
LOCAL_COMPOSE_DIR="services/infra-eva-assistant-bot/compose"

REMOTE_API_PATH="/opt/infra-eva-assistant-bot/api"
REMOTE_COMPOSE_DIR="/opt/infra-eva-assistant-bot"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🤖 Desplegando Eva Assistant Bot"
echo "  📍 Host: ${EVA_HOST}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 0. Validar que .env existe y tiene las variables requeridas
echo "🔍 0/4 Validando .env..."
ENV_FILE="${LOCAL_COMPOSE_DIR}/.env"

if [ ! -f "$ENV_FILE" ]; then
  echo "❌ Error: No se encontró ${ENV_FILE}"
  echo "   Copia .env.example → .env y rellena los valores"
  exit 1
fi

REQUIRED_VARS=("TELEGRAM_BOT_TOKEN" "DATABASE_URL")
MISSING=()
for VAR in "${REQUIRED_VARS[@]}"; do
  if ! grep -q "^${VAR}=" "$ENV_FILE" && ! grep -q "^${VAR}=\"" "$ENV_FILE"; then
    MISSING+=("$VAR")
  fi
done

if [ ${#MISSING[@]} -gt 0 ]; then
  echo "❌ Error: Faltan variables en ${ENV_FILE}:"
  for VAR in "${MISSING[@]}"; do
    echo "   - $VAR"
  done
  exit 1
fi
echo "   ✅ .env válido (${#REQUIRED_VARS[@]} variables OK)"
echo ""

# 1. Sync configuración al servidor (.env + docker-compose.yml)
echo "📦 1/4 Sincronizando configuración..."

# .env
rsync -av \
  -e "ssh ${SSH_OPTS}" \
  ${LOCAL_COMPOSE_DIR}/.env \
  root@${EVA_HOST}:${REMOTE_COMPOSE_DIR}/.env

# docker-compose.yml
rsync -av \
  -e "ssh ${SSH_OPTS}" \
  ${LOCAL_COMPOSE_DIR}/docker-compose.yml \
  root@${EVA_HOST}:${REMOTE_COMPOSE_DIR}/docker-compose.yml

echo ""

# 2. Sync código API
echo "📦 2/4 Sincronizando código API..."
rsync -av --delete \
  -e "ssh ${SSH_OPTS}" \
  ${LOCAL_API_PATH}/ \
  root@${EVA_HOST}:${REMOTE_API_PATH}/

echo ""

# 3. Build + Deploy
echo "🔨 3/4 Construyendo y desplegando..."
ssh ${SSH_OPTS} root@${EVA_HOST} << 'ENDSSH'
cd /opt/infra-eva-assistant-bot
docker compose build --no-cache eva-api eva-scheduler
docker compose up -d
ENDSSH

echo ""

# 4. Verificar estado
echo "⏳ 4/4 Verificando despliegue..."
sleep 5

ssh ${SSH_OPTS} root@${EVA_HOST} << 'ENDSSH'
echo "📊 Estado de los contenedores:"
docker ps --filter name=eva --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "📜 Logs recientes eva-api:"
docker logs --tail 30 eva-api

echo ""
echo "📜 Logs recientes eva-scheduler:"
docker logs --tail 30 eva-scheduler
ENDSSH

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅ Despliegue completado"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

#./services/infra-eva-assistant-bot/deploy-eva-assistant-bot.sh