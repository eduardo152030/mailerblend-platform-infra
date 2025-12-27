#!/usr/bin/env bash
set -euo pipefail

SERVICE="${1:?Usage: deploy-service.sh <service-name> <target-ip>}"
TARGET_IP="${2:?Usage: deploy-service.sh <service-name> <target-ip>}"

SRC_DIR="services/${SERVICE}"
REMOTE_DIR="/opt/${SERVICE}"

# Flags para evitar el error de "Host Identification Changed"
SSH_OPTS="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR"

if [[ ! -d "${SRC_DIR}" ]]; then
  echo "ERROR: Service folder not found: ${SRC_DIR}" >&2
  exit 1
fi

echo "==> Deploying ${SERVICE} to ${TARGET_IP}:${REMOTE_DIR}"

# Crear directorios remotos
ssh $SSH_OPTS "root@${TARGET_IP}" "mkdir -p ${REMOTE_DIR}"

# Copy compose y config usando los mismos SSH_OPTS
rsync -av -e "ssh $SSH_OPTS" "${SRC_DIR}/compose/" "root@${TARGET_IP}:${REMOTE_DIR}/"

# Si existe carpeta config, copiarla
if [[ -d "${SRC_DIR}/config" ]]; then
    rsync -av -e "ssh $SSH_OPTS" "${SRC_DIR}/config/" "root@${TARGET_IP}:${REMOTE_DIR}/config/"
fi

echo "==> Pulling and Starting containers..."
ssh $SSH_OPTS "root@${TARGET_IP}" "cd ${REMOTE_DIR} && docker compose pull && docker compose up -d --remove-orphans"

echo "==> Done. Service ${SERVICE} should be up at http://${TARGET_IP}"