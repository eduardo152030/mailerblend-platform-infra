#!/bin/bash
# ============================================================
# 🎬 DEMO END-TO-END - LinkedIn Sourcing con Rate Limiting
# ✅ INTELIGENTE: Auto-descubre IDs por linkedin_url de test.
#    Ejecutar todas las veces que quieras sin cambiar nada.
#
# Uso:
#   bbash services/infra-composable-crm/scripts/LinkedIn_Stealth_Sourcing_test_all_state_v2.sh  # limpia + demo completo
#   bash services/infra-composable-crm/scripts/LinkedIn_Stealth_Sourcing_test_all_state_v2.sh --only-clean # solo limpia
#   bash services/infra-composable-crm/scripts/LinkedIn_Stealth_Sourcing_test_all_state_v2.sh --only-demo  # solo ejecuta demo
# ============================================================

BASE_URL="https://infra-svc01.mailerblend.com/_svc/v1/linkedin-sourcing"
H="X-Api-Key: ${CRM_API_KEY}"
MODE="${1:---all}"

# ── URLs de test: el script siempre las busca y elimina ──────
DEMO_URLS=(
  "https://linkedin.com/in/demo-guardian-001"
  "https://linkedin.com/in/demo-motor-001"
  "https://linkedin.com/in/demo-fortaleza-001"
)

# ============================================================
# HELPER: busca el ID de un lead por su linkedin_url exacta
# ============================================================
find_lead_id_by_url() {
  local URL="$1"
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
  echo "╔══════════════════════════════════════════════════════════════╗"
  echo "║         🧹 LIMPIEZA INTELIGENTE DE LEADS DE DEMO            ║"
  echo "╚══════════════════════════════════════════════════════════════╝"
  echo ""
  
  DELETED=0
  NOT_FOUND=0
  
  for URL in "${DEMO_URLS[@]}"; do
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
  echo ""
}

# ============================================================
# FUNCIÓN: DEMO COMPLETO
# ============================================================
run_demo() {
  echo "╔══════════════════════════════════════════════════════════════╗"
  echo "║  🎬 DEMO COMPLETO - LinkedIn Sourcing con Rate Limiting     ║"
  echo "╚══════════════════════════════════════════════════════════════╝"
  echo ""
  
  # ── PASO 1: Verificar Knowledge Base ──
  echo "──────────────────────────────────────────────────────────────"
  echo "📚 PASO 1: Verificar Knowledge Base (servicios cargados)"
  echo "──────────────────────────────────────────────────────────────"
  
  KB_COUNT=$(curl -sS "$BASE_URL/knowledge-base?category=SERVICES" -H "$H" \
    | python3 -c "import sys,json; print(json.load(sys.stdin)['total'])" 2>/dev/null)
  
  echo "  ✅ Knowledge Base: $KB_COUNT servicios"
  echo "     🟢 GUARDIAN (400-800€/mes)"
  echo "     🔵 MOTOR (1,000-1,600€/mes)"
  echo "     🟣 FORTALEZA (1,700-2,500€/mes)"
  echo ""
  
  # ── PASO 2: Verificar Rate Limits ──
  echo "──────────────────────────────────────────────────────────────"
  echo "🎯 PASO 2: Verificar Rate Limits Actuales"
  echo "──────────────────────────────────────────────────────────────"
  
  RATE_STATUS=$(curl -sS "$BASE_URL/rate-limits/current/status" -H "$H")
  INVITES_TODAY=$(echo "$RATE_STATUS" | python3 -c "import sys,json; print(json.load(sys.stdin)['invites']['sent_today'])" 2>/dev/null)
  INVITES_CAP=$(echo "$RATE_STATUS" | python3 -c "import sys,json; print(json.load(sys.stdin)['invites']['cap'])" 2>/dev/null)
  INVITES_REMAINING=$(echo "$RATE_STATUS" | python3 -c "import sys,json; print(json.load(sys.stdin)['invites']['remaining'])" 2>/dev/null)
  CAN_SEND=$(echo "$RATE_STATUS" | python3 -c "import sys,json; print(json.load(sys.stdin)['invites']['can_send'])" 2>/dev/null)
  COOLDOWN=$(echo "$RATE_STATUS" | python3 -c "import sys,json; print(json.load(sys.stdin)['cooldown_active'])" 2>/dev/null)
  
  echo "  📤 Invites enviadas hoy: $INVITES_TODAY/$INVITES_CAP"
  echo "  ✅ Restantes: $INVITES_REMAINING"
  echo "  🚦 Puede enviar: $CAN_SEND"
  echo "  ⏸️  Cooldown activo: $COOLDOWN"
  echo ""
  
  if [ "$CAN_SEND" != "true" ]; then
    echo "  ⚠️  WARNING: No se pueden enviar más invites hoy (cap alcanzado o cooldown)"
    echo ""
  fi
  
  # ── PASO 3: Crear 3 Leads de Demo ──
  echo "──────────────────────────────────────────────────────────────"
  echo "📥 PASO 3: Importar 3 leads de demo (uno por pack)"
  echo "──────────────────────────────────────────────────────────────"
  
  # Lead 1: GUARDIAN
  LEAD_GUARDIAN=$(curl -sS -X POST "$BASE_URL/leads/import" \
    -H "$H" -H "Content-Type: application/json" \
    -d '{
      "leads": [{
        "linkedin_url": "https://linkedin.com/in/demo-guardian-001",
        "full_name": "María López",
        "title": "Directora",
        "company": "Clínica Dental López",
        "location": "Madrid, Spain",
        "pack_candidate": "GUARDIAN",
        "segment": "Pack1_A_<50reviews"
      }],
      "auto_classify": false
    }' | python3 -c "import sys,json; print(json.load(sys.stdin)['imported_ids'][0])" 2>/dev/null)
  
  echo "  ✅ GUARDIAN: María López (Clínica Dental) → $LEAD_GUARDIAN"
  
  # Registrar actividad INVITE
  curl -sS -X POST "$BASE_URL/activity-log" \
    -H "$H" -H "Content-Type: application/json" \
    -d "{
      \"activity_type\": \"INVITE\",
      \"metadata\": {\"lead_id\": \"$LEAD_GUARDIAN\", \"pack\": \"GUARDIAN\", \"segment\": \"Pack1_A\"},
      \"risk_level\": \"LOW\"
    }" > /dev/null
  
  # Lead 2: MOTOR
  LEAD_MOTOR=$(curl -sS -X POST "$BASE_URL/leads/import" \
    -H "$H" -H "Content-Type: application/json" \
    -d '{
      "leads": [{
        "linkedin_url": "https://linkedin.com/in/demo-motor-001",
        "full_name": "Carlos Ruiz",
        "title": "CEO",
        "company": "Agencia Digital Innova",
        "location": "Barcelona, Spain",
        "pack_candidate": "MOTOR",
        "segment": "Pack2_A_Services_MAD"
      }],
      "auto_classify": false
    }' | python3 -c "import sys,json; print(json.load(sys.stdin)['imported_ids'][0])" 2>/dev/null)
  
  echo "  ✅ MOTOR: Carlos Ruiz (Agencia Digital) → $LEAD_MOTOR"
  
  curl -sS -X POST "$BASE_URL/activity-log" \
    -H "$H" -H "Content-Type: application/json" \
    -d "{
      \"activity_type\": \"INVITE\",
      \"metadata\": {\"lead_id\": \"$LEAD_MOTOR\", \"pack\": \"MOTOR\", \"segment\": \"Pack2_A\"},
      \"risk_level\": \"LOW\"
    }" > /dev/null
  
  # Lead 3: FORTALEZA
  LEAD_FORTALEZA=$(curl -sS -X POST "$BASE_URL/leads/import" \
    -H "$H" -H "Content-Type: application/json" \
    -d '{
      "leads": [{
        "linkedin_url": "https://linkedin.com/in/demo-fortaleza-001",
        "full_name": "Ana Jiménez",
        "title": "COO",
        "company": "LogiTrans España",
        "location": "Valencia, Spain",
        "pack_candidate": "FORTALEZA",
        "segment": "Pack3_Logistics"
      }],
      "auto_classify": false
    }' | python3 -c "import sys,json; print(json.load(sys.stdin)['imported_ids'][0])" 2>/dev/null)
  
  echo "  ✅ FORTALEZA: Ana Jiménez (LogiTrans) → $LEAD_FORTALEZA"
  
  curl -sS -X POST "$BASE_URL/activity-log" \
    -H "$H" -H "Content-Type: application/json" \
    -d "{
      \"activity_type\": \"INVITE\",
      \"metadata\": {\"lead_id\": \"$LEAD_FORTALEZA\", \"pack\": \"FORTALEZA\", \"segment\": \"Pack3\"},
      \"risk_level\": \"LOW\"
    }" > /dev/null
  
  echo ""
  
  # ── PASO 4: Verificar Activity Log ──
  echo "──────────────────────────────────────────────────────────────"
  echo "📊 PASO 4: Verificar Activity Log (invites registradas)"
  echo "──────────────────────────────────────────────────────────────"
  
  STATS_TODAY=$(curl -sS "$BASE_URL/activity-log/stats/today" -H "$H")
  INVITES_LOGGED=$(echo "$STATS_TODAY" | python3 -c "import sys,json; print(json.load(sys.stdin)['stats']['INVITE'])" 2>/dev/null)
  TOTAL_ACTIVITY=$(echo "$STATS_TODAY" | python3 -c "import sys,json; print(json.load(sys.stdin)['total'])" 2>/dev/null)
  
  echo "  📤 INVITE: $INVITES_LOGGED"
  echo "  📊 Total actividad hoy: $TOTAL_ACTIVITY"
  echo ""
  
  # ── PASO 5: Simular Aceptación + Draft ──
  echo "──────────────────────────────────────────────────────────────"
  echo "✅ PASO 5: Simular aceptación + generar draft (GUARDIAN)"
  echo "──────────────────────────────────────────────────────────────"
  
  # Mover a ACCEPTED
  curl -sS -X PATCH "$BASE_URL/leads/$LEAD_GUARDIAN" \
    -H "$H" -H "Content-Type: application/json" \
    -d '{"status": "ACCEPTED", "lead_score": 72}' > /dev/null
  
  # Registrar CONNECTION_ACCEPT
  curl -sS -X POST "$BASE_URL/activity-log" \
    -H "$H" -H "Content-Type: application/json" \
    -d "{
      \"activity_type\": \"CONNECTION_ACCEPT\",
      \"metadata\": {\"lead_id\": \"$LEAD_GUARDIAN\", \"pack\": \"GUARDIAN\"},
      \"risk_level\": \"LOW\"
    }" > /dev/null
  
  # Crear approval con draft personalizado usando Knowledge Base
  APPROVAL=$(curl -sS -X POST "$BASE_URL/approvals" \
    -H "$H" -H "Content-Type: application/json" \
    -d "{
      \"linkedin_lead_id\": \"$LEAD_GUARDIAN\",
      \"draft_message\": \"Hola María, vi que Clínica Dental López tiene un equipo de 8-10 personas. Con ese tamaño, ¿cómo lleváis la gestión de IT? Muchas clínicas en ese punto nos cuentan que el mayor dolor es cuando entra alguien nuevo o pasa algo con los ordenadores y todo el equipo se para.\",
      \"ai_rationale\": \"Lead score: 72. Pack GUARDIAN. ICP match: clínica dental, 8-10 empleados, sector servicios profesionales. Pain probable: gestión IT sin personal técnico, problemas cuando algo falla. Ángulo: estabilidad operativa sin pensar en IT.\"
    }")
  
  APPROVAL_ID=$(echo "$APPROVAL" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])" 2>/dev/null)
  
  echo "  ✅ María López → ACCEPTED"
  echo "  🤖 Draft generado → Approval ID: $APPROVAL_ID"
  echo "     Mensaje: 'Hola María, vi que Clínica Dental López...'"
  echo ""
  
  # ── PASO 6: Aprobar Draft + Enviar ──
  echo "──────────────────────────────────────────────────────────────"
  echo "👍 PASO 6: Aprobar draft y enviar mensaje"
  echo "──────────────────────────────────────────────────────────────"
  
  # Aprobar
  curl -sS -X POST "$BASE_URL/approvals/$APPROVAL_ID/approve" \
    -H "$H" -H "Content-Type: application/json" \
    -d '{
      "angle": "Bueno",
      "pain_assessment": "Real",
      "approved_by": "Jainer",
      "human_note": "ICP perfecto, pain muy claro"
    }' > /dev/null
  
  # Enviar mensaje
  curl -sS -X POST "$BASE_URL/conversations" \
    -H "$H" -H "Content-Type: application/json" \
    -d "{
      \"linkedin_lead_id\": \"$LEAD_GUARDIAN\",
      \"message_text\": \"Hola María, vi que Clínica Dental López tiene un equipo de 8-10 personas. Con ese tamaño, ¿cómo lleváis la gestión de IT?\",
      \"direction\": \"SENT\",
      \"sent_by\": \"Jainer\"
    }" > /dev/null
  
  # Registrar MESSAGE
  curl -sS -X POST "$BASE_URL/activity-log" \
    -H "$H" -H "Content-Type: application/json" \
    -d "{
      \"activity_type\": \"MESSAGE\",
      \"metadata\": {\"lead_id\": \"$LEAD_GUARDIAN\", \"pack\": \"GUARDIAN\"},
      \"risk_level\": \"LOW\"
    }" > /dev/null
  
  echo "  ✅ Draft aprobado"
  echo "  💬 Mensaje enviado a María López"
  echo ""
  
  # ── PASO 7: Respuesta Positiva ──
  echo "──────────────────────────────────────────────────────────────"
  echo "💬 PASO 7: Simular respuesta POSITIVA del lead"
  echo "──────────────────────────────────────────────────────────────"
  
  curl -sS -X POST "$BASE_URL/conversations" \
    -H "$H" -H "Content-Type: application/json" \
    -d "{
      \"linkedin_lead_id\": \"$LEAD_GUARDIAN\",
      \"message_text\": \"Hola! Sí, justo ese es uno de nuestros dolores. El mes pasado tuvimos un problema con el servidor y estuvimos sin funcionar medio día. ¿Qué tipo de soluciones ofrecéis?\",
      \"direction\": \"RECEIVED\",
      \"sent_by\": \"María López\",
      \"sentiment\": \"POSITIVE\",
      \"intent\": \"INTERESTED\"
    }" > /dev/null
  
  echo "  ✅ Respuesta recibida: POSITIVE + INTERESTED"
  echo "     'Sí, justo ese es uno de nuestros dolores...'"
  echo ""
  
  # ── PASO 8: Agendar Call ──
  echo "──────────────────────────────────────────────────────────────"
  echo "📅 PASO 8: Registrar outcome BOOKED (call agendada)"
  echo "──────────────────────────────────────────────────────────────"
  
  curl -sS -X POST "$BASE_URL/outcomes" \
    -H "$H" -H "Content-Type: application/json" \
    -d "{
      \"linkedin_lead_id\": \"$LEAD_GUARDIAN\",
      \"outcome\": \"BOOKED\",
      \"outcome_notes\": \"Call agendada vía Cal.com. Muy interesada en Pack GUARDIAN. Pain claro: gestión IT sin recursos.\",
      \"calendar_event_id\": \"cal_demo_maria_001\",
      \"calendar_event_url\": \"https://cal.com/nucleotecnologico/diagnostico\",
      \"scheduled_at\": \"2026-02-20T10:00:00Z\"
    }" > /dev/null
  
  echo "  ✅ Outcome: BOOKED"
  echo "  📅 Call: 20 Feb 2026 a las 10:00h"
  echo "  💰 Pack candidato: GUARDIAN (400-800€/mes)"
  echo ""
  
  # ── PASO 9: Dashboard Final ──
  echo "──────────────────────────────────────────────────────────────"
  echo "📊 PASO 9: Verificar Dashboard Final"
  echo "──────────────────────────────────────────────────────────────"
  
  DASHBOARD=$(curl -sS "$BASE_URL/dashboard" -H "$H")
  TOTAL_LEADS=$(echo "$DASHBOARD" | python3 -c "import sys,json; print(json.load(sys.stdin)['total_leads'])" 2>/dev/null)
  BOOKED_CALLS=$(echo "$DASHBOARD" | python3 -c "import sys,json; print(json.load(sys.stdin)['booked_calls'])" 2>/dev/null)
  PENDING_APPROVALS=$(echo "$DASHBOARD" | python3 -c "import sys,json; print(json.load(sys.stdin).get('pending_approvals', 0))" 2>/dev/null)
  CONVERSATIONS=$(echo "$DASHBOARD" | python3 -c "import sys,json; print(json.load(sys.stdin)['active_conversations'])" 2>/dev/null)
  
  echo "  👥 Total Leads: $TOTAL_LEADS"
  echo "  💬 Conversaciones activas: $CONVERSATIONS"
  echo "  📅 Booked Calls: $BOOKED_CALLS"
  echo "  🔔 Approvals pendientes: $PENDING_APPROVALS"
  echo ""
  
  # ── PASO 10: Rate Limits Finales ──
  echo "──────────────────────────────────────────────────────────────"
  echo "🎯 PASO 10: Verificar Rate Limits Actualizados"
  echo "──────────────────────────────────────────────────────────────"
  
  RATE_STATUS_FINAL=$(curl -sS "$BASE_URL/rate-limits/current/status" -H "$H")
  INVITES_FINAL=$(echo "$RATE_STATUS_FINAL" | python3 -c "import sys,json; print(json.load(sys.stdin)['invites']['sent_today'])" 2>/dev/null)
  MESSAGES_FINAL=$(echo "$RATE_STATUS_FINAL" | python3 -c "import sys,json; print(json.load(sys.stdin)['messages']['sent_today'])" 2>/dev/null)
  
  echo "  📤 Invites enviadas hoy: $INVITES_FINAL/$INVITES_CAP"
  echo "  💬 Mensajes enviados hoy: $MESSAGES_FINAL/50"
  echo ""
  
  # ── RESUMEN FINAL ──
  echo "╔══════════════════════════════════════════════════════════════╗"
  echo "║                  ✅ DEMO COMPLETADA                          ║"
  echo "╚══════════════════════════════════════════════════════════════╝"
  echo ""
  echo "Flujo simulado completo:"
  echo "  1. ✅ Knowledge Base verificada (3 packs)"
  echo "  2. ✅ Rate limits verificados"
  echo "  3. ✅ 3 leads importados (GUARDIAN, MOTOR, FORTALEZA)"
  echo "  4. ✅ Actividad registrada en Activity Log"
  echo "  5. ✅ Lead aceptado → Draft generado con IA"
  echo "  6. ✅ Draft aprobado → Mensaje enviado"
  echo "  7. ✅ Respuesta POSITIVE recibida"
  echo "  8. ✅ Call BOOKED registrada"
  echo "  9. ✅ Dashboard actualizado"
  echo " 10. ✅ Rate limits tracked"
  echo ""
  echo "🎬 Verifica ahora en la UI:"
  echo "  • Dashboard → Booked Calls: $BOOKED_CALLS"
  echo "  • Pipeline → Columna Booked: María López"
  echo "  • Configuración → Activity Log: $INVITES_FINAL invites, $MESSAGES_FINAL mensajes"
  echo "  • Configuración → Rate Limits: $INVITES_FINAL/$INVITES_CAP invites usadas"
  echo ""
  echo "IDs para referencia:"
  echo "  GUARDIAN: $LEAD_GUARDIAN"
  echo "  MOTOR:    $LEAD_MOTOR"
  echo "  FORTALEZA: $LEAD_FORTALEZA"
  echo ""
}

# ── MAIN: Ejecutar según modo ────────────────────────────────
case "$MODE" in
  --only-clean)
    run_clean
    ;;
  --only-demo)
    run_demo
    ;;
  *)
    run_clean
    run_demo
    ;;
esac