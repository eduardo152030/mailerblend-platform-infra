#!/bin/bash
# ============================================================
# 🧹 CLEAN + 🧪 RE-TEST - Pipeline LinkedIn Sourcing
# ✅ INTELIGENTE: Auto-descubre IDs por linkedin_url de test.
#    Ejecutar todas las veces que quieras sin cambiar nada.
#
# Uso:
#   bash services/infra-composable-crm/scripts/LinkedIn_Stealth_Sourcing_test_all_state.sh             # limpia + re-test
#   bash services/infra-composable-crm/scripts/LinkedIn_Stealth_Sourcing_test_all_state.sh --only-clean # solo limpia
#   bash services/infra-composable-crm/scripts/LinkedIn_Stealth_Sourcing_test_all_state.sh --only-test  # solo crea datos
# ============================================================

BASE_URL="https://infra-svc01.mailerblend.com/_svc/v1/linkedin-sourcing"
H="X-Api-Key: ${CRM_API_KEY}"
MODE="${1:---all}"

# ── URLs de test: el script siempre las busca y elimina ──────
TEST_URLS=(
  "https://linkedin.com/in/test-new-001"
  "https://linkedin.com/in/test-queued-001"
  "https://linkedin.com/in/test-sent-001"
  "https://linkedin.com/in/test-accepted-001"
  "https://linkedin.com/in/test-conv-001"
  "https://linkedin.com/in/test-booked-001"
  "https://linkedin.com/in/test-converted-001"
  "https://linkedin.com/in/test-noaccept-001"
  "https://linkedin.com/in/test-later-001"
  # Runs anteriores con URLs distintas
  "https://linkedin.com/in/lead-nuevo-test"
  "https://linkedin.com/in/lead-encola-test"
  "https://linkedin.com/in/lead-enviado-test"
  "https://linkedin.com/in/lead-aceptado-test"
  "https://linkedin.com/in/lead-conversacion-test"
  "https://linkedin.com/in/lead-booked-test"
  "https://linkedin.com/in/lead-convertido-test"
  "https://linkedin.com/in/lead-archivado-test"
  "https://linkedin.com/in/test-user-jainer"
)

# ============================================================
# HELPER: busca el ID de un lead por su linkedin_url exacta
# ============================================================
find_lead_id_by_url() {
  local URL="$1"
  local ENCODED=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$URL'))" 2>/dev/null)
  curl -sS "$BASE_URL/leads?limit=200" -H "$H" \
    | python3 -c "
import sys, json
data = json.load(sys.stdin)
for item in data.get('items', []):
    if item.get('linkedin_url') == '$URL':
        print(item['id'])
        break
" 2>/dev/null
}

# ============================================================
# FUNCIÓN: LIMPIEZA INTELIGENTE
# ============================================================
run_clean() {
  echo ""
  echo "╔══════════════════════════════════════════════════╗"
  echo "║         🧹 LIMPIEZA INTELIGENTE DE TEST          ║"
  echo "╚══════════════════════════════════════════════════╝"
  echo ""

  DELETED=0
  NOT_FOUND=0

  for URL in "${TEST_URLS[@]}"; do
    SLUG=$(echo "$URL" | sed 's|https://linkedin.com/in/||')
    LEAD_ID=$(find_lead_id_by_url "$URL")

    if [ -n "$LEAD_ID" ]; then
      HTTP=$(curl -sS -o /dev/null -w "%{http_code}" \
        -X DELETE "$BASE_URL/leads/$LEAD_ID" -H "$H")
      if [ "$HTTP" = "200" ]; then
        echo "  🗑️  $SLUG → eliminado ($LEAD_ID)"
        DELETED=$((DELETED + 1))
      else
        echo "  ❌  $SLUG → error HTTP $HTTP"
      fi
    else
      NOT_FOUND=$((NOT_FOUND + 1))
    fi
  done

  echo ""
  echo "  ✅ Eliminados:  $DELETED"
  echo "  ⏭️  No existían: $NOT_FOUND"

  REMAINING=$(curl -sS "$BASE_URL/dashboard" -H "$H" \
    | python3 -c "import sys,json; print(json.load(sys.stdin)['total_leads'])" 2>/dev/null)
  echo "  👥 Leads restantes en el sistema: $REMAINING"
  echo ""
}

# ============================================================
# FUNCIÓN: CREAR DATOS DE TEST
# ============================================================
run_test() {
  echo "╔══════════════════════════════════════════════════╗"
  echo "║      🧪 CREANDO DATOS DE TEST (9 ESTADOS)       ║"
  echo "╚══════════════════════════════════════════════════╝"
  echo ""

  # ── 1. NEW ──────────────────────────────────────────────
  echo "📥 [1/9] NEW → Nuevos"
  LEAD_NEW_ID=$(curl -sS -X POST "$BASE_URL/leads/import" \
    -H "$H" -H "Content-Type: application/json" \
    -d '{
      "leads": [{"linkedin_url":"https://linkedin.com/in/test-new-001",
        "full_name":"Ana García","title":"Founder",
        "company":"PanaderíaOnline SL","location":"Barcelona, Spain",
        "pack_candidate":"GUARDIAN","segment":"A_<50reviews"}],
      "auto_classify": false
    }' | python3 -c "import sys,json; print(json.load(sys.stdin)['imported_ids'][0])" 2>/dev/null)
  echo "  ✅ Ana García (GUARDIAN, 50) → $LEAD_NEW_ID"

  # ── 2. INVITE_QUEUED ────────────────────────────────────
  echo "⏳ [2/9] INVITE_QUEUED → En Cola"
  LEAD_QUEUED_ID=$(curl -sS -X POST "$BASE_URL/leads/import" \
    -H "$H" -H "Content-Type: application/json" \
    -d '{
      "leads": [{"linkedin_url":"https://linkedin.com/in/test-queued-001",
        "full_name":"Carlos Martín","title":"CEO",
        "company":"Gestoría Digital SL","location":"Valencia, Spain",
        "pack_candidate":"GUARDIAN","segment":"A_<50reviews"}],
      "auto_classify": false
    }' | python3 -c "import sys,json; print(json.load(sys.stdin)['imported_ids'][0])" 2>/dev/null)
  curl -sS -X PATCH "$BASE_URL/leads/$LEAD_QUEUED_ID" \
    -H "$H" -H "Content-Type: application/json" \
    -d '{"status":"INVITE_QUEUED"}' > /dev/null
  echo "  ✅ Carlos Martín (GUARDIAN, 50) → $LEAD_QUEUED_ID"

  # ── 3. INVITE_SENT ──────────────────────────────────────
  echo "📤 [3/9] INVITE_SENT → Enviados"
  LEAD_SENT_ID=$(curl -sS -X POST "$BASE_URL/leads/import" \
    -H "$H" -H "Content-Type: application/json" \
    -d '{
      "leads": [{"linkedin_url":"https://linkedin.com/in/test-sent-001",
        "full_name":"Laura Sánchez","title":"Directora Operaciones",
        "company":"Clínica Dental Norte","location":"Bilbao, Spain",
        "pack_candidate":"MOTOR","segment":"Pack2_Services_BIL"}],
      "auto_classify": false
    }' | python3 -c "import sys,json; print(json.load(sys.stdin)['imported_ids'][0])" 2>/dev/null)
  curl -sS -X PATCH "$BASE_URL/leads/$LEAD_SENT_ID" \
    -H "$H" -H "Content-Type: application/json" \
    -d '{"status":"INVITE_SENT"}' > /dev/null
  echo "  ✅ Laura Sánchez (MOTOR, 60) → $LEAD_SENT_ID"

  # ── 4. ACCEPTED + APPROVAL ──────────────────────────────
  echo "✅ [4/9] ACCEPTED + APPROVAL PENDIENTE → Aceptados"
  LEAD_ACCEPTED_ID=$(curl -sS -X POST "$BASE_URL/leads/import" \
    -H "$H" -H "Content-Type: application/json" \
    -d '{
      "leads": [{"linkedin_url":"https://linkedin.com/in/test-accepted-001",
        "full_name":"Miguel Torres","title":"CTO",
        "company":"Agencia Digital MKT","location":"Madrid, Spain",
        "pack_candidate":"MOTOR","segment":"Pack2_Services_MAD"}],
      "auto_classify": false
    }' | python3 -c "import sys,json; print(json.load(sys.stdin)['imported_ids'][0])" 2>/dev/null)
  curl -sS -X PATCH "$BASE_URL/leads/$LEAD_ACCEPTED_ID" \
    -H "$H" -H "Content-Type: application/json" \
    -d '{"status":"ACCEPTED","lead_score":78}' > /dev/null
  APPROVAL_ID=$(curl -sS -X POST "$BASE_URL/approvals" \
    -H "$H" -H "Content-Type: application/json" \
    -d "{
      \"linkedin_lead_id\": \"$LEAD_ACCEPTED_ID\",
      \"draft_message\": \"Hola Miguel, vi que Agencia Digital MKT lleva varios proyectos de eCommerce en paralelo. Con ese ritmo, ¿cómo lleváis la parte de integraciones entre herramientas? Muchas agencias en ese punto nos cuentan que el mayor cuello de botella no es la ejecución sino que nada habla con nada.\",
      \"ai_rationale\": \"Lead score: 78. Pack MOTOR. Señal: agencia con múltiples clientes y stack SaaS disperso. Dolor probable: fragmentación de herramientas.\"
    }" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])" 2>/dev/null)
  echo "  ✅ Miguel Torres (MOTOR, 78) → $LEAD_ACCEPTED_ID"
  echo "  🔔 Approval pendiente → $APPROVAL_ID"

  # ── 5. CONVERSACIÓN ACTIVA ──────────────────────────────
  echo "💬 [5/9] CONVERSACIÓN → Conversación activa"
  LEAD_CONV_ID=$(curl -sS -X POST "$BASE_URL/leads/import" \
    -H "$H" -H "Content-Type: application/json" \
    -d '{
      "leads": [{"linkedin_url":"https://linkedin.com/in/test-conv-001",
        "full_name":"Sofía Romero","title":"Gerente General",
        "company":"Transportes Romero SA","location":"Zaragoza, Spain",
        "pack_candidate":"FORTALEZA","segment":"Pack3_Logistics_ZAR"}],
      "auto_classify": false
    }' | python3 -c "import sys,json; print(json.load(sys.stdin)['imported_ids'][0])" 2>/dev/null)
  curl -sS -X PATCH "$BASE_URL/leads/$LEAD_CONV_ID" \
    -H "$H" -H "Content-Type: application/json" \
    -d '{"status":"ACCEPTED","lead_score":85}' > /dev/null
  curl -sS -X POST "$BASE_URL/conversations" -H "$H" -H "Content-Type: application/json" \
    -d "{\"linkedin_lead_id\":\"$LEAD_CONV_ID\",\"message_text\":\"Hola Sofía, vi que Transportes Romero gestiona rutas en 3 provincias. ¿Cómo tenéis montada la parte de monitoring de sistemas?\",\"direction\":\"SENT\",\"sent_by\":\"Jainer\"}" > /dev/null
  curl -sS -X POST "$BASE_URL/conversations" -H "$H" -H "Content-Type: application/json" \
    -d "{\"linkedin_lead_id\":\"$LEAD_CONV_ID\",\"message_text\":\"Hola! Sí, tenemos ese problema. El mes pasado tuvimos una caída que no detectamos hasta 2 horas después. ¿Qué soluciones trabajáis?\",\"direction\":\"RECEIVED\",\"sent_by\":\"Sofía Romero\",\"sentiment\":\"POSITIVE\",\"intent\":\"INTERESTED\"}" > /dev/null
  echo "  ✅ Sofía Romero (FORTALEZA, 85) → $LEAD_CONV_ID"
  echo "     💬 1 msg enviado + respuesta POSITIVE del lead"

  # ── 6. BOOKED ───────────────────────────────────────────
  echo "📅 [6/9] BOOKED → Booked"
  LEAD_BOOKED_ID=$(curl -sS -X POST "$BASE_URL/leads/import" \
    -H "$H" -H "Content-Type: application/json" \
    -d '{
      "leads": [{"linkedin_url":"https://linkedin.com/in/test-booked-001",
        "full_name":"Roberto Jiménez","title":"Director IT",
        "company":"Distribuidora AlimSur","location":"Sevilla, Spain",
        "pack_candidate":"FORTALEZA","segment":"Pack3_Industry_SEV"}],
      "auto_classify": false
    }' | python3 -c "import sys,json; print(json.load(sys.stdin)['imported_ids'][0])" 2>/dev/null)
  curl -sS -X PATCH "$BASE_URL/leads/$LEAD_BOOKED_ID" \
    -H "$H" -H "Content-Type: application/json" \
    -d '{"status":"ACCEPTED","lead_score":91}' > /dev/null
  curl -sS -X POST "$BASE_URL/outcomes" -H "$H" -H "Content-Type: application/json" \
    -d "{\"linkedin_lead_id\":\"$LEAD_BOOKED_ID\",\"outcome\":\"BOOKED\",\"outcome_notes\":\"Call agendada. Muy interesado en monitorización 24/7.\",\"calendar_event_id\":\"cal_roberto_001\",\"calendar_event_url\":\"https://cal.com/nucleotecnologico/diagnostico\",\"scheduled_at\":\"2026-02-25T10:00:00Z\"}" > /dev/null
  echo "  ✅ Roberto Jiménez (FORTALEZA, 91) → $LEAD_BOOKED_ID"

  # ── 7. CONVERTED ────────────────────────────────────────
  echo "⚡ [7/9] CONVERTED → Convertidos"
  LEAD_CONV2_ID=$(curl -sS -X POST "$BASE_URL/leads/import" \
    -H "$H" -H "Content-Type: application/json" \
    -d '{
      "leads": [{"linkedin_url":"https://linkedin.com/in/test-converted-001",
        "full_name":"Elena Vidal","title":"CEO",
        "company":"LogiTech Solutions SL","location":"Madrid, Spain",
        "pack_candidate":"MOTOR","segment":"Pack2_Tech_MAD"}],
      "auto_classify": false
    }' | python3 -c "import sys,json; print(json.load(sys.stdin)['imported_ids'][0])" 2>/dev/null)
  curl -sS -X PATCH "$BASE_URL/leads/$LEAD_CONV2_ID" \
    -H "$H" -H "Content-Type: application/json" \
    -d '{"status":"ACCEPTED","lead_score":88}' > /dev/null
  curl -sS -X POST "$BASE_URL/outcomes" -H "$H" -H "Content-Type: application/json" \
    -d "{\"linkedin_lead_id\":\"$LEAD_CONV2_ID\",\"outcome\":\"CONVERTED\",\"outcome_notes\":\"Firmaron Pack MOTOR 1.200€/mes. Inicio en marzo.\"}" > /dev/null
  echo "  ✅ Elena Vidal (MOTOR, 88) → $LEAD_CONV2_ID"

  # ── 8. NO_ACCEPT ────────────────────────────────────────
  echo "📦 [8/9] NO_ACCEPT → Archivados"
  LEAD_NOACCEPT_ID=$(curl -sS -X POST "$BASE_URL/leads/import" \
    -H "$H" -H "Content-Type: application/json" \
    -d '{
      "leads": [{"linkedin_url":"https://linkedin.com/in/test-noaccept-001",
        "full_name":"Pedro Blanco","title":"Autónomo",
        "company":"Freelance","location":"Málaga, Spain",
        "pack_candidate":"NONE","segment":"descartado"}],
      "auto_classify": false
    }' | python3 -c "import sys,json; print(json.load(sys.stdin)['imported_ids'][0])" 2>/dev/null)
  curl -sS -X PATCH "$BASE_URL/leads/$LEAD_NOACCEPT_ID" \
    -H "$H" -H "Content-Type: application/json" \
    -d '{"status":"NO_ACCEPT","lead_score":15}' > /dev/null
  echo "  ✅ Pedro Blanco (NONE, 15) → $LEAD_NOACCEPT_ID"

  # ── 9. ENGAGE_LATER ─────────────────────────────────────
  echo "🔄 [9/9] ENGAGE_LATER → Archivados"
  LEAD_LATER_ID=$(curl -sS -X POST "$BASE_URL/leads/import" \
    -H "$H" -H "Content-Type: application/json" \
    -d '{
      "leads": [{"linkedin_url":"https://linkedin.com/in/test-later-001",
        "full_name":"Carmen López","title":"Directora Comercial",
        "company":"Inmobiliaria López SA","location":"Alicante, Spain",
        "pack_candidate":"GUARDIAN","segment":"A_<50reviews"}],
      "auto_classify": false
    }' | python3 -c "import sys,json; print(json.load(sys.stdin)['imported_ids'][0])" 2>/dev/null)
  curl -sS -X PATCH "$BASE_URL/leads/$LEAD_LATER_ID" \
    -H "$H" -H "Content-Type: application/json" \
    -d '{"status":"ENGAGE_LATER","lead_score":42}' > /dev/null
  echo "  ✅ Carmen López (GUARDIAN, 42) → $LEAD_LATER_ID"

  # ── VERIFICACIÓN FINAL ──────────────────────────────────
  echo ""
  echo "── Verificando dashboard ──"
  sleep 1
  DASHBOARD=$(curl -sS "$BASE_URL/dashboard" -H "$H")
  TOTAL_F=$(echo "$DASHBOARD"  | python3 -c "import sys,json; print(json.load(sys.stdin)['total_leads'])" 2>/dev/null)
  CHAT_F=$(echo "$DASHBOARD"   | python3 -c "import sys,json; print(json.load(sys.stdin)['active_conversations'])" 2>/dev/null)
  BOOKED_F=$(echo "$DASHBOARD" | python3 -c "import sys,json; print(json.load(sys.stdin)['booked_calls'])" 2>/dev/null)
  CONV_F=$(echo "$DASHBOARD"   | python3 -c "import sys,json; print(json.load(sys.stdin)['converted_opportunities'])" 2>/dev/null)
  PEND_F=$(echo "$DASHBOARD"   | python3 -c "import sys,json; print(json.load(sys.stdin).get('pending_approvals','?'))" 2>/dev/null)

  echo ""
  echo "╔══════════════════════════════════════════════════╗"
  echo "║            📊 ESTADO FINAL DEL SISTEMA          ║"
  echo "╚══════════════════════════════════════════════════╝"
  echo ""
  printf "  %-30s %s\n" "👥 Total leads:"           "$TOTAL_F  (esperado: 9)"
  printf "  %-30s %s\n" "💬 Conversaciones activas:" "$CHAT_F   (esperado: 1)"
  printf "  %-30s %s\n" "📅 Booked calls:"           "$BOOKED_F (esperado: 1)"
  printf "  %-30s %s\n" "⚡ Convertidos:"            "$CONV_F   (esperado: 1)"
  printf "  %-30s %s\n" "🔔 Approvals pendientes:"   "$PEND_F   (esperado: 1)"
  echo ""
  echo "╔══════════════════════════════════════════════════╗"
  echo "║          ✅ QUÉ VER EN LA UI AHORA              ║"
  echo "╚══════════════════════════════════════════════════╝"
  echo ""
  echo "  Pipeline Kanban:"
  echo "  ┌──────────────┬─────────────────────────────────┐"
  echo "  │ Nuevos       │ Ana García (GUARDIAN, 50)       │"
  echo "  │ En Cola      │ Carlos Martín (GUARDIAN, 50)    │"
  echo "  │ Enviados     │ Laura Sánchez (MOTOR, 60)       │"
  echo "  │ Aceptados    │ Miguel Torres (MOTOR, 78) 🔔    │"
  echo "  │ Conversación │ Sofía Romero (FORTALEZA, 85)    │"
  echo "  │ Booked       │ Roberto Jiménez (FORTALEZA, 91) │"
  echo "  │ Convertidos  │ Elena Vidal (MOTOR, 88)         │"
  echo "  │ Archivados   │ Pedro Blanco + Carmen López     │"
  echo "  └──────────────┴─────────────────────────────────┘"
  echo ""
  echo "  🔔 Para aprobar el draft de Miguel Torres:"
  echo "     Dashboard → tarjeta 'Approvals pendientes'"
  echo "     O: Pipeline → Aceptados → Miguel Torres → tab Approvals"
  echo ""
}

# ── MAIN ────────────────────────────────────────────────────
case "$MODE" in
  --only-clean) run_clean ;;
  --only-test)  run_test  ;;
  *)            run_clean && run_test ;;
esac
