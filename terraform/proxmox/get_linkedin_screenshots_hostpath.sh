#!/usr/bin/env bash
set -euo pipefail

REMOTE_HOST="${1:-root@192.168.1.120}"
REMOTE_PATH="${2:-/opt/infra-excraper/data/screenshots}"
LOCAL_DIR="${3:-linkeding_test_image}"

STAMP="$(date +%Y%m%d_%H%M%S)"
REMOTE_TAR="/root/host_screenshots_${STAMP}.tar.gz"

mkdir -p "${LOCAL_DIR}"

echo "==> Tarring remote folder: ${REMOTE_HOST}:${REMOTE_PATH}"
ssh "${REMOTE_HOST}" "tar -C '${REMOTE_PATH}' -czf '${REMOTE_TAR}' ."

echo "==> Downloading..."
scp "${REMOTE_HOST}:${REMOTE_TAR}" "./${LOCAL_DIR}/"

echo "==> Extracting..."
tar -xzf "./${LOCAL_DIR}/$(basename "${REMOTE_TAR}")" -C "./${LOCAL_DIR}"
rm -f "./${LOCAL_DIR}/$(basename "${REMOTE_TAR}")"

echo "==> Cleaning remote tar..."
ssh "${REMOTE_HOST}" "rm -f '${REMOTE_TAR}'"

echo "✅ Done. Files in: ./${LOCAL_DIR}"
# ./services/infra-excraper/notas_\&_scripts/get_linkedin_screenshots_hostpath.sh 
