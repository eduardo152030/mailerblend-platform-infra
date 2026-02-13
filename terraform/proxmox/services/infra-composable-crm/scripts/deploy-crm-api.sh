#!/bin/bash
# deploy-crm-api.sh - Despliega CRM API al servidor
# Uso: ./deploy-crm-api.sh
#      ./services/infra-composable-crm/scripts/deploy-crm-api.sh
#
# Debug útil:
#   ssh root@192.168.1.118 'docker ps --filter name=crm-api'
#   ssh root@192.168.1.118 'docker logs --tail 50 crm-api'
#   ssh root@192.168.1.118 'docker exec crm-api env | grep CRM'

set -e  # Exit on error

CRM_HOST="${CRM_HOST:-192.168.1.118}"
SSH_OPTS="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR"

LOCAL_API_PATH="services/infra-composable-crm/api"
LOCAL_COMPOSE_DIR="services/infra-composable-crm/compose/crm-api"

REMOTE_API_PATH="/opt/infra-composable-crm/api"
REMOTE_COMPOSE_DIR="/opt/infra-composable-crm/crm-api"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🚀 Desplegando CRM API"
echo "  📍 Host: ${CRM_HOST}"
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

REQUIRED_VARS=("CRM_DB_DSN" "CRM_API_KEY" "CRM_BASE_PATH" "CRM_INGEST_SECRET")
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

# 1. Sync configuración al servidor (.env + docker-compose.host.yml)
echo "📦 1/4 Sincronizando configuración..."

# .env
rsync -av \
  -e "ssh ${SSH_OPTS}" \
  ${LOCAL_COMPOSE_DIR}/.env \
  root@${CRM_HOST}:${REMOTE_COMPOSE_DIR}/.env

# docker-compose.host.yml → docker-compose.yml en el servidor
rsync -av \
  -e "ssh ${SSH_OPTS}" \
  ${LOCAL_COMPOSE_DIR}/docker-compose.host.yml \
  root@${CRM_HOST}:${REMOTE_COMPOSE_DIR}/docker-compose.yml

echo ""

# 2. Sync código API
echo "📦 2/4 Sincronizando código API..."
rsync -av --delete \
  -e "ssh ${SSH_OPTS}" \
  ${LOCAL_API_PATH}/ \
  root@${CRM_HOST}:${REMOTE_API_PATH}/

echo ""

# 3. Build + Deploy
echo "🔨 3/4 Construyendo y desplegando..."
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR \
  root@${CRM_HOST} << 'ENDSSH'
cd /opt/infra-composable-crm
docker compose -f crm-api/docker-compose.yml build crm-api
docker compose -f crm-api/docker-compose.yml up -d crm-api
ENDSSH

echo ""

# 4. Verificar estado
echo "⏳ 4/4 Verificando despliegue..."
sleep 5

ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR \
  root@${CRM_HOST} << 'ENDSSH'
echo "📊 Estado del contenedor:"
docker ps --filter name=crm-api --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "🔑 Variables de entorno CRM:"
docker exec crm-api env | grep CRM | sort

echo ""
echo "📜 Logs recientes:"
docker logs --tail 50 crm-api
ENDSSH

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅ Despliegue completado"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🌐 API disponible en:"
echo "   http://192.168.1.118:18088"
echo "   http://192.168.1.118:18088/docs"
echo ""