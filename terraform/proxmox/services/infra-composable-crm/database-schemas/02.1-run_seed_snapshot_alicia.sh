cat > services/infra-composable-crm/database-schemas/run_seed_snapshot_alicia.sh <<'BASH'
#!/usr/bin/env bash
set -euo pipefail

CRM_DB_HOST="${CRM_DB_HOST:-192.168.1.118}"
CRM_DB_CONTAINER="${CRM_DB_CONTAINER:-supabase-db}"

CRM_DB_NAME="$(ssh root@${CRM_DB_HOST} "docker inspect ${CRM_DB_CONTAINER} --format '{{range .Config.Env}}{{println .}}{{end}}' | awk -F= '/^POSTGRES_DB=/{print \$2}'")"
CRM_DB_USER="$(ssh root@${CRM_DB_HOST} "docker inspect ${CRM_DB_CONTAINER} --format '{{range .Config.Env}}{{println .}}{{end}}' | awk -F= '/^POSTGRES_USER=/{print \$2}'")"
CRM_DB_PASS="$(ssh root@${CRM_DB_HOST} "docker inspect ${CRM_DB_CONTAINER} --format '{{range .Config.Env}}{{println .}}{{end}}' | awk -F= '/^POSTGRES_PASSWORD=/{print \$2}'")"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SQL_FILE="${SCRIPT_DIR}/04_seed_snapshot_alicia.sql"

echo "Seeding snapshot story (Alicia) into ${CRM_DB_HOST}:${CRM_DB_CONTAINER} db=${CRM_DB_NAME} user=${CRM_DB_USER}"

cat "${SQL_FILE}" | ssh root@${CRM_DB_HOST} \
  "docker exec -i ${CRM_DB_CONTAINER} env PGPASSWORD='${CRM_DB_PASS}' psql -U '${CRM_DB_USER}' -d '${CRM_DB_NAME}' -v ON_ERROR_STOP=1"
BASH

#chmod +x services/infra-composable-crm/database-schemas/run_seed_snapshot_alicia.sh
# Ejecutar seed “historia”
# services/infra-composable-crm/database-schemas/run_seed_snapshot_alicia.sh
# Verificar snapshot ya con datos
# curl -sS "https://infra-svc01.mailerblend.com/_svc/v1/contacts/a87ccd90-8f62-4416-b30b-d17cdc4a09f2/snapshot" | python3 -m json.tool

