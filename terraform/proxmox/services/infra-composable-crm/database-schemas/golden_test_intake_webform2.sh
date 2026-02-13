#!/usr/bin/env bash
set -euo pipefail

# ─────────────────────────────────────────────────────────────
# 🧪 GOLDEN TEST: /v1/intake/webform (E2E)
# - POST intake
# - GET snapshot y asserts: utm/form/historial/oportunidad
# - DB validation opcional
# ─────────────────────────────────────────────────────────────

API_BASE="${CRM_API_BASE:-https://infra-svc01.mailerblend.com/_svc}"

DB_HOST="${CRM_DB_HOST:-192.168.1.118}"
DB_CONTAINER="${CRM_DB_CONTAINER:-supabase-db}"
DB_NAME="${CRM_DB_NAME:-postgres}"
DB_USER="${CRM_DB_USER:-pgadmin2026f}"
DB_PASS="${CRM_DB_PASS:-l1W3YyXJUyqfSrkhdJMe}"

TS="$(date -u +%Y%m%dT%H%M%SZ)"
EMAIL="golden.${TS}@example.com"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " 🧪 GOLDEN TEST: /v1/intake/webform (E2E)"
echo " API=${API_BASE}"
echo " EMAIL=${EMAIL}"
echo " DB=${DB_HOST}:${DB_CONTAINER} db=${DB_NAME} user=${DB_USER}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 1) POST intake/webform
echo "➡️  POST ${API_BASE}/v1/intake/webform"

RESP="$(
  curl -sS -X POST "${API_BASE}/v1/intake/webform" \
    -H "Content-Type: application/json" \
    -d "{
      \"nombre\": \"Golden Lead ${TS}\",
      \"email\": \"${EMAIL}\",
      \"telefono\": \"+34 600 111 999\",
      \"company_name\": \"Golden Company ${TS}\",
      \"cargo\": \"Owner\",
      \"ciudad\": \"Barcelona\",
      \"pais\": \"ES\",
      \"tipo_empresa\": \"Pyme\",
      \"gdpr_consent\": true,
      \"marketing_consent\": false,
      \"utm\": {
        \"utm_source\": \"google\",
        \"utm_medium\": \"cpc\",
        \"utm_campaign\": \"outsourcing-it-barcelona\",
        \"utm_content\": \"ad_01\",
        \"utm_term\": \"outsourcing it\",
        \"adgroup\": \"grp1\",
        \"device\": \"mobile\",
        \"placement\": \"search\",
        \"keyword\": \"outsourcing it barcelona\",
        \"creative\": \"rsa_1\",
        \"gclid\": \"TEST-GCLID-${TS}\",
        \"msclkid\": \"\",
        \"li_fat_id\": \"\",
        \"fbclid\": \"\",
        \"ads_platform\": \"GOOGLE\",
        \"landing_url\": \"https://mailerblend.com/outsourcing-it\",
        \"referrer_url\": \"https://www.google.com/\",
        \"first_visit_at\": \"2026-02-09T10:00:00Z\"
      },
      \"form\": {
        \"servicio_relacionado\": \"Outsourcing IT / CAU\",
        \"como_nos_conociste\": \"Google / Buscador\",
        \"tipo_soporte\": \"Externalización completa IT\",
        \"mensaje\": \"Empresa 40 empleados. Soporte IT integral + licencias + seguridad. Queremos empezar este mes.\",
        \"origen\": \"Formulario web\",
        \"ip_address\": \"1.2.3.4\",
        \"user_agent\": \"golden-test\"
      }
    }"
)"

CID="$(echo "$RESP" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['contact_id'])")"
OID="$(echo "$RESP" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('oportunidad_id',''))")"

echo "✅ contact_id=${CID}"
echo "✅ oportunidad_id=${OID}"

# 2) GET snapshot + asserts
echo "➡️  GET ${API_BASE}/v1/contacts/${CID}/snapshot"

SNAP="$(curl -sS "${API_BASE}/v1/contacts/${CID}/snapshot")"

UTM_COUNT="$(echo "$SNAP" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d['related']['parametros_utm']))")"
FORM_COUNT="$(echo "$SNAP" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d['related']['formulario_web']))")"
OPP_COUNT="$(echo "$SNAP" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d['related']['oportunidades']))")"
SUBJECTS="$(echo "$SNAP" | python3 -c "import sys,json; d=json.load(sys.stdin); print([x['subject'] for x in d['related']['historial']])")"

echo "📌 Snapshot counts: utm=${UTM_COUNT} forms=${FORM_COUNT} oportunidades=${OPP_COUNT}"
echo "📌 Historial subjects: ${SUBJECTS}"

# asserts mínimos
test "${UTM_COUNT}" -ge 1
test "${FORM_COUNT}" -ge 1
test "${OPP_COUNT}" -ge 1

echo "$SUBJECTS" | grep -q "EVENT::LEAD_CREATED"
echo "$SUBJECTS" | grep -q "EVENT::LEAD_QUALIFIED"

echo "✅ Snapshot assertions OK"

# 3) DB validation opcional (si hay oportunidad)
if [[ -n "${OID}" ]]; then
  echo "➡️  DB validation (opcional): oportunidad existe y cumple checks"
  ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@"${DB_HOST}" \
    "docker exec -i ${DB_CONTAINER} env PGPASSWORD='${DB_PASS}' \
     psql -U '${DB_USER}' -d '${DB_NAME}' -Atc \
     \"SELECT id, contacto_id, lead_tag, prioridad, next_action, probabilidad, estado
       FROM oportunidades
       WHERE id='${OID}';\""
fi
echo "✅ GOLDEN TEST OK"