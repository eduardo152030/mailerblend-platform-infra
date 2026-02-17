#!/bin/bash
# deploy-prom.sh - Despliega Prometheus + Alertmanager al servidor
# Uso: ./deploy-prom.sh
#      ./services/infra-prom/scripts/deploy-prom.sh
#
# Debug útil:
#   ssh root@192.168.1.110 'docker ps --filter name=prometheus --filter name=alertmanager'
#   ssh root@192.168.1.110 'docker logs --tail 50 prometheus'
#   ssh root@192.168.1.110 'docker logs --tail 50 alertmanager'
#   ssh root@192.168.1.110 'curl -s http://localhost:9090/-/healthy'
#   ssh root@192.168.1.110 'curl -s http://localhost:9093/-/healthy'

set -e  # Exit on error

PROM_HOST="${PROM_HOST:-192.168.1.110}"
SSH_OPTS="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR"

LOCAL_BASE="services/infra-prom"
REMOTE_BASE="/opt/infra-prom"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🚀 Desplegando Prometheus + Alertmanager"
echo "  📍 Host: ${PROM_HOST}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 0. Validar que perm.env existe
echo "🔍 0/4 Validando perm.env..."
PERM_ENV="${LOCAL_BASE}/perm.env"

if [ ! -f "$PERM_ENV" ]; then
  echo "❌ Error: No se encontró ${PERM_ENV}"
  exit 1
fi
echo "   ✅ perm.env encontrado"
echo ""

# 1. Sync configuración al servidor
echo "📦 1/4 Sincronizando configuración..."

# docker-compose.yml
rsync -av \
  -e "ssh ${SSH_OPTS}" \
  ${LOCAL_BASE}/compose/docker-compose.yml \
  root@${PROM_HOST}:${REMOTE_BASE}/docker-compose.yml

# perm.env
rsync -av \
  -e "ssh ${SSH_OPTS}" \
  ${LOCAL_BASE}/perm.env \
  root@${PROM_HOST}:${REMOTE_BASE}/perm.env

# prometheus.yml
rsync -av \
  -e "ssh ${SSH_OPTS}" \
  ${LOCAL_BASE}/config/prometheus.yml \
  root@${PROM_HOST}:${REMOTE_BASE}/config/prometheus.yml

# alertmanager.yml
rsync -av \
  -e "ssh ${SSH_OPTS}" \
  ${LOCAL_BASE}/config/alertmanager/alertmanager.yml \
  root@${PROM_HOST}:${REMOTE_BASE}/config/alertmanager/alertmanager.yml

# rules/ — con --delete (todo versionado en repo)
rsync -av --delete \
  -e "ssh ${SSH_OPTS}" \
  ${LOCAL_BASE}/config/rules/ \
  root@${PROM_HOST}:${REMOTE_BASE}/config/rules/

# targets/ — sin --delete (hay archivos remotos no versionados)
rsync -av \
  -e "ssh ${SSH_OPTS}" \
  ${LOCAL_BASE}/config/targets/ \
  root@${PROM_HOST}:${REMOTE_BASE}/config/targets/

echo ""

# 2. Asegurar que los contenedores están levantados
echo "🔨 2/4 Asegurando contenedores en marcha..."
ssh ${SSH_OPTS} root@${PROM_HOST} << 'ENDSSH'
cd /opt/infra-prom
docker compose up -d prometheus alertmanager
ENDSSH
echo ""

# 3. Recargar configuración
# - Prometheus: necesita restart para recargar prometheus.yml principal
# - Alertmanager: acepta SIGHUP para reload en caliente
echo "🔄 3/4 Recargando configuración..."
ssh ${SSH_OPTS} root@${PROM_HOST} << 'ENDSSH'
echo "   → Reiniciando prometheus (necesario para recargar prometheus.yml)..."
docker restart prometheus

echo "   → Enviando SIGHUP a alertmanager (reload en caliente)..."
docker kill --signal=SIGHUP alertmanager
ENDSSH
echo ""

# 4. Verificar health
echo "⏳ 4/4 Verificando estado..."
sleep 5

ssh ${SSH_OPTS} root@${PROM_HOST} << 'ENDSSH'
echo "📊 Estado de contenedores:"
docker ps --filter name=prometheus --filter name=alertmanager \
  --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "🏥 Health checks:"

PROM_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:9090/-/healthy)
if [ "$PROM_HEALTH" = "200" ]; then
  echo "   ✅ Prometheus healthy (HTTP ${PROM_HEALTH})"
else
  echo "   ❌ Prometheus NO responde (HTTP ${PROM_HEALTH})"
fi

ALERT_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:9093/-/healthy)
if [ "$ALERT_HEALTH" = "200" ]; then
  echo "   ✅ Alertmanager healthy (HTTP ${ALERT_HEALTH})"
else
  echo "   ❌ Alertmanager NO responde (HTTP ${ALERT_HEALTH})"
fi

echo ""
echo "📜 Logs recientes Prometheus:"
docker logs --tail 20 prometheus

echo ""
echo "📜 Logs recientes Alertmanager:"
docker logs --tail 20 alertmanager
ENDSSH

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅ Despliegue completado"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🌐 Servicios disponibles en:"
echo "   http://192.168.1.110:9090        ← Prometheus"
echo "   http://192.168.1.110:9090/-/healthy"
echo "   http://192.168.1.110:9093        ← Alertmanager"
echo "   http://192.168.1.110:9093/-/healthy"
echo ""