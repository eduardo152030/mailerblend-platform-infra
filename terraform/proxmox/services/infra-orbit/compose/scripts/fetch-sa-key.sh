#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${ROOT_DIR}/gcp/.env"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Missing ${ENV_FILE}. Create it from gcp/.env.example"
  exit 1
fi
# shellcheck disable=SC1090
source "$ENV_FILE"

mkdir -p "${ROOT_DIR}/secrets"
scp "root@${ORBIT_IP}:/root/gcp-secrets/sa.json" "${ROOT_DIR}/secrets/sa.json"
chmod 600 "${ROOT_DIR}/secrets/sa.json"
echo "Saved: ${ROOT_DIR}/secrets/sa.json (DO NOT COMMIT)"
