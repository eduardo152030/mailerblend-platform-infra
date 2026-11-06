#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
BASE="$PWD/services/infra-prom"
# Use the official binaries matching the pinned container versions.
PROMTOOL="${PROMTOOL:-promtool}"
AMTOOL="${AMTOOL:-amtool}"
command -v "$PROMTOOL" >/dev/null
command -v "$AMTOOL" >/dev/null
python3 scripts/validate-blackbox-targets.py
python3 tests/monitoring/test_blackbox_catalog.py
python3 scripts/prepare-telegram.py
"$PROMTOOL" check rules "$BASE"/config/rules/*.yml
"$PROMTOOL" test rules "$PWD/tests/monitoring/alerts.test.yml" "$PWD/tests/monitoring/lxc-cpu.test.yml" "$PWD/tests/monitoring/incremental-cpu.test.yml"
# Rewrite only container paths into a temporary local validation config.
CHECK_DIR=$(mktemp -d)
trap 'rm -rf "$CHECK_DIR"' EXIT
python3 - "$BASE" "$CHECK_DIR" <<'PY'
from pathlib import Path
import sys
base, out = map(Path, sys.argv[1:])
p = (base/'config/prometheus.yml').read_text().replace('/etc/prometheus/', str(base/'config') + '/')
(out/'prometheus.yml').write_text(p)
a = (base/'.runtime/alertmanager.yml').read_text().replace('/run/secrets/telegram_bot_token', str(base/'.runtime/telegram_bot_token')).replace('/etc/alertmanager/templates/', str(base/'config/alertmanager/templates') + '/')
(out/'alertmanager.yml').write_text(a)
PY
"$PROMTOOL" check config "$CHECK_DIR/prometheus.yml"
"$AMTOOL" check-config "$CHECK_DIR/alertmanager.yml"

for STATE in firing resolved; do
  "$AMTOOL" template render \
    --template.glob="$BASE/config/alertmanager/templates/*.tmpl" \
    --template.text='{{ template "telegram.message" . }}' \
    --template.type=html \
    --template.data="$PWD/tests/monitoring/telegram-$STATE.json" > "$CHECK_DIR/$STATE.txt"
  case "$STATE" in
    firing) grep -q FIRING "$CHECK_DIR/$STATE.txt" ;;
    resolved) grep -q RESOLVED "$CHECK_DIR/$STATE.txt" ;;
  esac
done
