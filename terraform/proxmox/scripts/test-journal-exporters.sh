#!/usr/bin/env bash
# Local-only validation; never invokes SSH, Docker, deployment or secret preparation.
set -euo pipefail
cd "$(dirname "$0")/.."
PROMTOOL="${PROMTOOL:-promtool}"
"$PROMTOOL" --version 2>&1 | grep -q 'version 3.12.0'
python3 -m unittest discover -s tests/monitoring -p 'test_*.py'
"$PROMTOOL" check rules services/infra-prom/config/rules/*.yml
"$PROMTOOL" test rules tests/monitoring/alerts.test.yml tests/monitoring/lxc-cpu.test.yml tests/monitoring/incremental-cpu.test.yml
CHECK_DIR=$(mktemp -d)
trap 'rm -rf "$CHECK_DIR"' EXIT
for CT in 625 626; do
  python3 scripts/prepare-journal-exporters.py --ct "$CT" --output "$CHECK_DIR/$CT" >/dev/null
  bash -n "$CHECK_DIR/$CT/node-cgroup.sh"
done
python3 - "$CHECK_DIR" <<'PY'
import ast, json, sys
from pathlib import Path
root=Path(sys.argv[1])
for p in root.rglob('*.py'):ast.parse(p.read_text())
base=Path('services/infra-prom/config')
config=(base/'prometheus.yml').read_text().replace('/etc/prometheus/',str(base.resolve())+'/')
(root/'prometheus.yml').write_text(config)
PY
"$PROMTOOL" check config "$CHECK_DIR/prometheus.yml"
