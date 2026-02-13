#!/usr/bin/env bash
set -euo pipefail

CRM_API_BASE="${CRM_API_BASE:-https://infra-svc01.mailerblend.com/_svc}"
CRM_DB_HOST="${CRM_DB_HOST:-192.168.1.118}"
CRM_DB_CONTAINER="${CRM_DB_CONTAINER:-supabase-db}"
CRM_DB_USER="${CRM_DB_USER:-pgadmin2026f}"
CRM_DB_NAME="${CRM_DB_NAME:-postgres}"
CRM_DB_PASS="${CRM_DB_PASS:-l1W3YyXJUyqfSrkhdJMe}"

REQ_TS="$(date -u +%Y%m%dT%H%M%SZ)"
EMAIL="golden.${REQ_TS}@example.com"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " 🧪 GOLDEN TEST: /v1/intake/webform (E2E)"
echo " API=$CRM_API_BASE"
echo " EMAIL=$EMAIL"
echo " DB=${CRM_DB_HOST}:${CRM_DB_CONTAINER} db=${CRM_DB_NAME} user=${CRM_DB_USER}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

JSON_PAYLOAD="$(cat <<JSON
{
  "nombre": "Golden Lead ${REQ_TS}",
  "email": "${EMAIL}",
  "telefono": "+34 600 123 999",
  "company_name": "Golden Company ${REQ_TS}",
  "cargo": "Owner",
  "ciudad": "Barcelona",
  "pais": "ES",
  "tipo_empresa": "Pyme",
  "gdpr_consent": true,
  "marketing_consent": false,
  "utm": {
    "utm_source": "google",
    "utm_medium": "cpc",
    "utm_campaign": "golden-test",
    "utm_content": "ad_golden",
    "utm_term": "golden lead",
    "adgroup": "grp_golden",
    "device": "mobile",
    "placement": "search",
    "keyword": "golden test lead",
    "creative": "rsa_golden",
    "gclid": "GOLDEN-GCLID-${REQ_TS}",
    "msclkid": "GOLDEN-MSCLKID-${REQ_TS}",
    "li_fat_id": "GOLDEN-LI-${REQ_TS}",
    "fbclid": "GOLDEN-FB-${REQ_TS}",
    "ads_platform": "GOOGLE",
    "landing_url": "https://mailerblend.com/outsourcing-it",
    "referrer_url": "https://www.google.com/",
    "first_visit_at": "2026-02-09T10:00:00Z"
  },
  "form": {
    "servicio_relacionado": "Outsourcing IT / CAU",
    "como_nos_conociste": "Google / Buscador",
    "tipo_soporte": "Externalización completa IT",
    "mensaje": "Golden test: 40 empleados, soporte integral + seguridad, queremos empezar este mes.",
    "origen": "Formulario web",
    "ip_address": "1.2.3.4",
    "user_agent": "golden-test/1.0"
  }
}
JSON
)"

echo "➡️  POST ${CRM_API_BASE}/v1/intake/webform"
RESP="$(curl -sS -X POST "${CRM_API_BASE}/v1/intake/webform" \
  -H "Content-Type: application/json" \
  -d "${JSON_PAYLOAD}")"

echo "$RESP" | python3 -m json.tool >/tmp/golden_resp.json

CID="$(python3 -c "import json; d=json.load(open('/tmp/golden_resp.json')); print(d['contact_id'])")"
OID="$(python3 -c "import json; d=json.load(open('/tmp/golden_resp.json')); print(d.get('oportunidad_id',''))")"

echo "✅ contact_id=$CID"
echo "✅ oportunidad_id=$OID"

echo "➡️  GET ${CRM_API_BASE}/v1/contacts/${CID}/snapshot"
SNAP="$(curl -sS "${CRM_API_BASE}/v1/contacts/${CID}/snapshot")"
echo "$SNAP" | python3 -m json.tool >/tmp/golden_snap.json

UTM_LEN="$(python3 -c "import json; d=json.load(open('/tmp/golden_snap.json')); print(len(d['related']['parametros_utm']))")"
FORM_LEN="$(python3 -c "import json; d=json.load(open('/tmp/golden_snap.json')); print(len(d['related']['formulario_web']))")"
HIST_SUBJ="$(python3 -c "import json; d=json.load(open('/tmp/golden_snap.json')); print([x.get('subject') for x in d['related']['historial']])")"
OPP_LEN="$(python3 -c "import json; d=json.load(open('/tmp/golden_snap.json')); print(len(d['related']['oportunidades']))")"

echo "📌 Snapshot counts: utm=${UTM_LEN} forms=${FORM_LEN} oportunidades=${OPP_LEN}"
echo "📌 Historial subjects: ${HIST_SUBJ}"

# Hard asserts (mínimo viable)
python3 - <<'PY'
import json, sys
snap=json.load(open('/tmp/golden_snap.json'))
utm=len(snap['related']['parametros_utm'])
forms=len(snap['related']['formulario_web'])
opps=len(snap['related']['oportunidades'])
subjects=[x.get('subject','') for x in snap['related']['historial']]

assert utm >= 1, "Expected >=1 UTM"
assert forms >= 1, "Expected >=1 formulario_web"
assert opps >= 1, "Expected >=1 oportunidad"
assert any(s=="EVENT::LEAD_CREATED" for s in subjects), "Missing EVENT::LEAD_CREATED"
assert any(s=="EVENT::LEAD_QUALIFIED" for s in subjects), "Missing EVENT::LEAD_QUALIFIED"
print("✅ Snapshot assertions OK")
PY

echo "➡️  DB validation (opcional): oportunidad existe y cumple checks"
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR root@${CRM_DB_HOST} \
"docker exec -i ${CRM_DB_CONTAINER} env PGPASSWORD='${CRM_DB_PASS}' \
psql -U '${CRM_DB_USER}' -d '${CRM_DB_NAME}' -Atc \
\"SELECT id, contacto_id, lead_tag, prioridad, next_action, probabilidad, estado
  FROM oportunidades
  WHERE id='${OID}';\""

echo "✅ GOLDEN TEST OK"
