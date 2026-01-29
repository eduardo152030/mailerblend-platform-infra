#!/usr/bin/env bash
set -euo pipefail

# Run from laptop. Executes remotely on infra-orbit via SSH (no interactive login).
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${ROOT_DIR}/gcp/.env"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Missing ${ENV_FILE}. Create it from gcp/.env.example"
  exit 1
fi

# shellcheck disable=SC1090
source "$ENV_FILE"

: "${ORBIT_IP:?Missing ORBIT_IP}"
: "${PROJECT_ID:?Missing PROJECT_ID}"
: "${REGION:?Missing REGION}"
: "${BQ_LOCATION:?Missing BQ_LOCATION}"
: "${TOPIC:?Missing TOPIC}"
: "${SUB:?Missing SUB}"
: "${DATASET_RAW:?Missing DATASET_RAW}"
: "${TABLE_RAW:?Missing TABLE_RAW}"
: "${SA_PUB:?Missing SA_PUB}"
: "${DF_BUCKET:?Missing DF_BUCKET}"

ssh "root@${ORBIT_IP}" "bash -lc '
set -euo pipefail

export PROJECT_ID=${PROJECT_ID@Q}
export REGION=${REGION@Q}
export BQ_LOCATION=${BQ_LOCATION@Q}
export TOPIC=${TOPIC@Q}
export SUB=${SUB@Q}
export DATASET_RAW=${DATASET_RAW@Q}
export TABLE_RAW=${TABLE_RAW@Q}
export SA_PUB=${SA_PUB@Q}
export DF_BUCKET=${DF_BUCKET@Q}

gcloud config set project \"\$PROJECT_ID\" >/dev/null || true

echo \"== Pub/Sub ==\"
gcloud pubsub topics create \"\$TOPIC\" >/dev/null 2>&1 || true
gcloud pubsub subscriptions create \"\$SUB\" --topic \"\$TOPIC\" >/dev/null 2>&1 || true

echo \"== BigQuery dataset ==\"
bq --location=\"\$BQ_LOCATION\" mk -d \"\${PROJECT_ID}:\${DATASET_RAW}\" >/dev/null 2>&1 || true

echo \"== BigQuery table ==\"
# Eliminamos los backticks para evitar que el shell intente ejecutar el nombre como comando
cat > /tmp/create_events_raw.sql <<EOF
CREATE TABLE IF NOT EXISTS nt-serverside-analytics.analytics_raw.events_raw (
  event_id STRING,
  event_name STRING,
  event_timestamp TIMESTAMP,
  event_date DATE,
  page_path STRING,
  section STRING,
  element_id STRING,
  form_id STRING,
  lead_source STRING,
  conversion_type STRING,
  user_agent STRING,
  ip_country STRING,
  payload STRING,
  ingested_at TIMESTAMP,
  collector_version STRING
)
PARTITION BY event_date
CLUSTER BY event_name, lead_source, page_path;
EOF

sed -i \
  -e \"s/nt-serverside-analytics/\$PROJECT_ID/g\" \
  -e \"s/analytics_raw/\$DATASET_RAW/g\" \
  -e \"s/events_raw/\$TABLE_RAW/g\" \
  /tmp/create_events_raw.sql

bq query --use_legacy_sql=false < /tmp/create_events_raw.sql >/dev/null

echo \"== Service Account (publisher) ==\"
gcloud iam service-accounts create \"\$SA_PUB\" --display-name \"Analytics gateway Pub/Sub publisher\" >/dev/null 2>&1 || true
gcloud pubsub topics add-iam-policy-binding \"\$TOPIC\" \
  --member=\"serviceAccount:\${SA_PUB}@\${PROJECT_ID}.iam.gserviceaccount.com\" \
  --role=\"roles/pubsub.publisher\" >/dev/null 2>&1 || true

echo \"== SA key on host (for gateway) ==\"
mkdir -p /root/gcp-secrets
if [ ! -f /root/gcp-secrets/sa.json ]; then
  gcloud iam service-accounts keys create /root/gcp-secrets/sa.json \
    --iam-account \"\${SA_PUB}@\${PROJECT_ID}.iam.gserviceaccount.com\" >/dev/null
  chmod 600 /root/gcp-secrets/sa.json
  echo \"Created /root/gcp-secrets/sa.json\"
else
  echo \"Exists /root/gcp-secrets/sa.json\"
fi

echo \"== Dataflow staging bucket ==\"
gsutil mb -p \"\$PROJECT_ID\" -l \"\$REGION\" \"gs://\$DF_BUCKET\" >/dev/null 2>&1 || true

echo \"== Dataflow job (template) ==\"
OUTPUT_TABLE_SPEC=\"\${PROJECT_ID}:\${DATASET_RAW}.\${TABLE_RAW}\"
gcloud dataflow jobs run \"sgtm-ps-to-bq-\$(date +%Y%m%d-%H%M%S)\" \
  --region \"\$REGION\" \
  --gcs-location \"gs://dataflow-templates-\$REGION/latest/PubSub_Subscription_to_BigQuery\" \
  --staging-location \"gs://\$DF_BUCKET/staging\" \
  --parameters \"inputSubscription=projects/\$PROJECT_ID/subscriptions/\$SUB,outputTableSpec=\$OUTPUT_TABLE_SPEC\" \
  >/dev/null

echo \"OK: bootstrap complete\"
'"