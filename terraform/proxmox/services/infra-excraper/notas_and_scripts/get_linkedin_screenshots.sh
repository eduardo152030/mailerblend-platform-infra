#!/usr/bin/env bash
set -euo pipefail

REMOTE_HOST="${1:-root@192.168.1.120}"
CONTAINER="${2:-infra-excraper-linkedin-worker-1}"
CONTAINER_PATH="${3:-/app/screenshots}"
LOCAL_DIR="${4:-linkeding_test_image}"

STAMP="$(date +%Y%m%d_%H%M%S)"
REMOTE_STAGE="/root/linkedin-screenshots"
REMOTE_TAR="/root/linkedin-screenshots_${STAMP}.tar.gz"

echo "==> Local folder: ./${LOCAL_DIR}"
mkdir -p "${LOCAL_DIR}"

echo "==> Copying from container to remote stage: ${REMOTE_HOST}:${REMOTE_STAGE}"
ssh "${REMOTE_HOST}" "rm -rf '${REMOTE_STAGE}' && mkdir -p '${REMOTE_STAGE}'"
ssh "${REMOTE_HOST}" "docker cp '${CONTAINER}:${CONTAINER_PATH}/.' '${REMOTE_STAGE}/'"

echo "==> Creating tar on remote: ${REMOTE_TAR}"
ssh "${REMOTE_HOST}" "tar -C '${REMOTE_STAGE}' -czf '${REMOTE_TAR}' ."

echo "==> Downloading tar to local..."
scp "${REMOTE_HOST}:${REMOTE_TAR}" "./${LOCAL_DIR}/"

echo "==> Extracting..."
tar -xzf "./${LOCAL_DIR}/$(basename "${REMOTE_TAR}")" -C "./${LOCAL_DIR}"
rm -f "./${LOCAL_DIR}/$(basename "${REMOTE_TAR}")"

echo "==> Cleaning remote temp..."
ssh "${REMOTE_HOST}" "rm -f '${REMOTE_TAR}' && rm -rf '${REMOTE_STAGE}'"

echo "✅ Done. Files in: ./${LOCAL_DIR}"
#./services/infra-excraper/notas_\&_scripts/get_linkedin_screenshots.sh