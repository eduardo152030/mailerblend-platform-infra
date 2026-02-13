#!/usr/bin/env bash
set -euo pipefail

CRM_DB_HOST="${CRM_DB_HOST:-192.168.1.118}"
CRM_DB_CONTAINER="${CRM_DB_CONTAINER:-supabase-db}"

CRM_DB_NAME="$(ssh root@${CRM_DB_HOST} "docker inspect ${CRM_DB_CONTAINER} --format '{{range .Config.Env}}{{println .}}{{end}}' | awk -F= '/^POSTGRES_DB=/{print \$2}'")"
CRM_DB_USER="$(ssh root@${CRM_DB_HOST} "docker inspect ${CRM_DB_CONTAINER} --format '{{range .Config.Env}}{{println .}}{{end}}' | awk -F= '/^POSTGRES_USER=/{print \$2}'")"
CRM_DB_PASS="$(ssh root@${CRM_DB_HOST} "docker inspect ${CRM_DB_CONTAINER} --format '{{range .Config.Env}}{{println .}}{{end}}' | awk -F= '/^POSTGRES_PASSWORD=/{print \$2}'")"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SQL_FILE="${SCRIPT_DIR}/03_seed_contactos.sql"

echo "Seeding contactos into ${CRM_DB_HOST}:${CRM_DB_CONTAINER} db=${CRM_DB_NAME} user=${CRM_DB_USER}"

cat "${SQL_FILE}" | ssh root@${CRM_DB_HOST} \
  "docker exec -i ${CRM_DB_CONTAINER} env PGPASSWORD='${CRM_DB_PASS}' psql -U '${CRM_DB_USER}' -d '${CRM_DB_NAME}' -v ON_ERROR_STOP=1"
