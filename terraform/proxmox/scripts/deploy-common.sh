#!/usr/bin/env bash
set -euo pipefail

COMMON="${1:?Usage: deploy-common.sh <common-name> <target-ip>}"
TARGET_IP="${2:?Usage: deploy-common.sh <common-name> <target-ip>}"

SRC_DIR="services/common/${COMMON}"
REMOTE_DIR="/opt/common/${COMMON}"

if [[ ! -d "${SRC_DIR}" ]]; then
  echo "ERROR: Common folder not found: ${SRC_DIR}" >&2
  exit 1
fi

echo "==> Deploying common/${COMMON} to ${TARGET_IP}:${REMOTE_DIR}"

ssh "root@${TARGET_IP}" "mkdir -p ${REMOTE_DIR}"

rsync -av "${SRC_DIR}/" "root@${TARGET_IP}:${REMOTE_DIR}/"

ssh "root@${TARGET_IP}" "cd ${REMOTE_DIR} && docker compose up -d"

echo "==> Done. Common ${COMMON} deployed to ${TARGET_IP}"
