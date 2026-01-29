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

ssh "root@${ORBIT_IP}" "bash -lc '
set -euo pipefail
export PROJECT_ID=${PROJECT_ID@Q}
echo \"Project: \$(gcloud config get-value project)\"
bq query --use_legacy_sql=false \
\"SELECT event_id,event_name,event_timestamp,page_path,lead_source
 FROM \\\`\${PROJECT_ID}.${DATASET_RAW}.${TABLE_RAW}\\\`
 ORDER BY event_timestamp DESC
 LIMIT 10\"
'"
