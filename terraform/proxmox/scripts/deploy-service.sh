#!/usr/bin/env bash
set -euo pipefail

SERVICE="${1:?Usage: deploy-service.sh <service-name> <target-ip>}"
TARGET_IP="${2:?Usage: deploy-service.sh <service-name> <target-ip>}"

SRC_DIR="services/${SERVICE}"
REMOTE_DIR="/opt/${SERVICE}"

if [[ ! -d "${SRC_DIR}" ]]; then
  echo "ERROR: Service folder not found: ${SRC_DIR}" >&2
  exit 1
fi

echo "==> Deploying ${SERVICE} to ${TARGET_IP}:${REMOTE_DIR}"

ssh "root@${TARGET_IP}" "mkdir -p ${REMOTE_DIR}/config"

# Copy compose + config (NO delete)
rsync -av "${SRC_DIR}/compose/" "root@${TARGET_IP}:${REMOTE_DIR}/"
rsync -av "${SRC_DIR}/config/"  "root@${TARGET_IP}:${REMOTE_DIR}/config/"

# Restart/update
ssh "root@${TARGET_IP}" "cd ${REMOTE_DIR} && docker compose up -d"

echo "==> Done. Test: http://${TARGET_IP}:9090"
