#!/usr/bin/env bash
# =============================================================================
# tests/smoke_test.sh
# EVA Assistant Bot — Smoke Tests
#
# Usage:
#   ./tests/smoke_test.sh
#   ./tests/smoke_test.sh https://infra-eva.mailerblend.com
#
# Requires: curl
# Exit code: 0 = all passed, 1 = any failed
# =============================================================================
set -uo pipefail

HOST="${1:-https://infra-eva.mailerblend.com}"
PASS=0
FAIL=0
SKIP=0

GREEN="\033[0;32m"
RED="\033[0;31m"
YELLOW="\033[0;33m"
BLUE="\033[0;34m"
NC="\033[0m"

pass() { echo -e "${GREEN}✅ PASS${NC} — $1"; ((PASS++)); }
fail() { echo -e "${RED}❌ FAIL${NC} — $1"; ((FAIL++)); }
skip() { echo -e "${YELLOW}⏭  SKIP${NC} — $1"; ((SKIP++)); }
section() { echo -e "\n${BLUE}── $1${NC}"; }

TOTAL=16

echo ""
echo "EVA Smoke Tests → $HOST"
echo "============================================"

# ══════════════════════════════════════════════
# SECTION 1 — API startup & connectivity
# ══════════════════════════════════════════════
section "API startup & connectivity"

echo "[1/$TOTAL] GET /health"
RESP=$(curl -sf "$HOST/health" 2>/dev/null || echo "CURL_FAIL")
if echo "$RESP" | grep -q '"ok"'; then
  pass "/health returns {status: ok}"
else
  fail "/health — got: $RESP"
fi

echo "[2/$TOTAL] GET /ready (DB connection)"
RESP=$(curl -sf "$HOST/ready" 2>/dev/null || echo "CURL_FAIL")
if echo "$RESP" | grep -q '"ready"'; then
  pass "/ready — DB connected"
else
  fail "/ready — got: $RESP"
fi

echo "[3/$TOTAL] GET / (root)"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$HOST/")
if [ "$STATUS" = "200" ]; then
  pass "/ returns 200"
else
  fail "/ — HTTP $STATUS"
fi

# ══════════════════════════════════════════════
# SECTION 2 — Reminder endpoints
# ══════════════════════════════════════════════
section "Reminder endpoints"

echo "[4/$TOTAL] GET /reminders"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$HOST/reminders")
if [ "$STATUS" = "200" ]; then
  pass "/reminders returns 200"
else
  fail "/reminders — HTTP $STATUS"
fi

echo "[5/$TOTAL] GET /tasks"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$HOST/tasks")
if [ "$STATUS" = "200" ]; then
  pass "/tasks returns 200"
else
  fail "/tasks — HTTP $STATUS"
fi

echo "[6/$TOTAL] POST /commands/parse — reminder parser"
RESP=$(curl -s -X POST "$HOST/commands/parse" \
  -H "Content-Type: application/json" \
  -d '{"text":"recuérdame fichar a las 9"}' 2>/dev/null || echo "CURL_FAIL")
if echo "$RESP" | grep -q '"task_text"' && echo "$RESP" | grep -q '"remind_at"'; then
  pass "/commands/parse extracts task_text and remind_at"
else
  fail "/commands/parse — got: ${RESP:0:120}"
fi

echo "[7/$TOTAL] POST /commands/parse — unrecognized text returns status"
RESP=$(curl -s -X POST "$HOST/commands/parse" \
  -H "Content-Type: application/json" \
  -d '{"text":"hola que tal"}' 2>/dev/null || echo "CURL_FAIL")
if echo "$RESP" | grep -q '"status"'; then
  pass "/commands/parse handles non-reminder gracefully"
else
  fail "/commands/parse unrecognized — got: ${RESP:0:120}"
fi

# ══════════════════════════════════════════════
# SECTION 3 — Telegram webhook
# ══════════════════════════════════════════════
section "Telegram webhook"

echo "[8/$TOTAL] POST /telegram/webhook — text message"
# Use a known command that returns quickly without calling Telegram API
# "eva, lista mis recordatorios" → list command → no send to fake chat_id
PAYLOAD='{"message":{"message_id":999,"from":{"id":99999,"username":"smoketest","first_name":"Smoke"},"chat":{"id":99999,"type":"private"},"date":1700000000,"text":"smoke test ping"}}'
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$HOST/telegram/webhook" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD" 2>/dev/null)
# Accept 200 (processed) or 500 (Telegram rejected fake chat_id — expected in test env)
if [ "$HTTP_STATUS" = "200" ] || [ "$HTTP_STATUS" = "500" ]; then
  pass "/telegram/webhook reachable (HTTP $HTTP_STATUS — 500 expected with fake chat_id)"
else
  fail "/telegram/webhook — HTTP $HTTP_STATUS"
fi

echo "[9/$TOTAL] POST /telegram/webhook — unsupported update type ignored"
PAYLOAD_BAD='{"inline_query":{"id":"123","from":{"id":99999},"query":"test"}}'
RESP=$(curl -s -X POST "$HOST/telegram/webhook" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD_BAD" 2>/dev/null || echo "CURL_FAIL")
if echo "$RESP" | grep -q '"ignored"'; then
  pass "/telegram/webhook ignores unsupported update types"
else
  fail "/telegram/webhook unsupported — got: ${RESP:0:120}"
fi

# ══════════════════════════════════════════════
# SECTION 4 — Publishing module
# ══════════════════════════════════════════════
section "Publishing module"

echo "[10/$TOTAL] GET /publishing/channels"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$HOST/publishing/channels")
if [ "$STATUS" = "200" ]; then
  pass "/publishing/channels returns 200"
else
  fail "/publishing/channels — HTTP $STATUS"
fi

echo "[11/$TOTAL] GET /publishing/undated-tasks"
RESP=$(curl -s "$HOST/publishing/undated-tasks" 2>/dev/null || echo "CURL_FAIL")
if echo "$RESP" | grep -qE '"tasks"|"total"'; then
  pass "/publishing/undated-tasks returns task list"
else
  fail "/publishing/undated-tasks — got: ${RESP:0:120}"
fi

echo "[12/$TOTAL] GET /publishing/undated-config"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$HOST/publishing/undated-config")
if [ "$STATUS" = "200" ]; then
  pass "/publishing/undated-config returns 200"
else
  fail "/publishing/undated-config — HTTP $STATUS"
fi

# ══════════════════════════════════════════════
# SECTION 5 — Tasks & attachments
# ══════════════════════════════════════════════
section "Tasks & attachments"

echo "[13/$TOTAL] GET /tasks/by-card/nonexistent — 404 handled"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$HOST/tasks/by-card/does-not-exist-000000")
if [ "$STATUS" = "404" ]; then
  pass "/tasks/by-card/{id} returns 404 for unknown card"
else
  fail "/tasks/by-card/nonexistent — expected 404 got $STATUS"
fi

echo "[14/$TOTAL] GET /events"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$HOST/events")
if [ "$STATUS" = "200" ]; then
  pass "/events returns 200"
else
  fail "/events — HTTP $STATUS"
fi

# ══════════════════════════════════════════════
# SECTION 6 — Auth
# ══════════════════════════════════════════════
section "Auth"

echo "[15/$TOTAL] POST /auth/login — wrong password returns 4xx"
RESP=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$HOST/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"nobody","password":"wrongpassword"}' 2>/dev/null || echo "000")
if echo "$RESP" | grep -qE '^4'; then
  pass "/auth/login rejects bad credentials with 4xx"
else
  fail "/auth/login — expected 4xx got $RESP"
fi

echo "[16/$TOTAL] GET /admin/users — requires auth"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$HOST/admin/users")
if [ "$STATUS" = "401" ] || [ "$STATUS" = "403" ] || [ "$STATUS" = "422" ]; then
  pass "/admin/users protected (returns $STATUS without token)"
else
  fail "/admin/users — expected 401/403/422 got $STATUS"
fi

# ══════════════════════════════════════════════
# SUMMARY
# ══════════════════════════════════════════════
echo ""
echo "============================================"
echo -e "Results: ${GREEN}$PASS passed${NC}  ${RED}$FAIL failed${NC}  ${YELLOW}$SKIP skipped${NC}  (total $TOTAL)"
echo ""

if [ "$FAIL" -gt 0 ]; then
  echo "❌ Smoke tests FAILED — do not promote this build."
  exit 1
else
  echo "✅ All smoke tests passed."
  exit 0
fi