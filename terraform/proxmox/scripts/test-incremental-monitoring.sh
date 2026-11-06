#!/usr/bin/env bash
# Local-only; no deploy, restart, SSH, scraping or notification.
set -euo pipefail
cd "$(dirname "$0")/.."
umask 077
PROMTOOL="${PROMTOOL:-promtool}"
export PROMTOOL
"$PROMTOOL" --version 2>&1 | grep -q 'version 3.12.0'
python3 -m unittest discover -s tests/monitoring -p 'test_*.py'
"$PROMTOOL" check rules services/infra-prom/config/rules/*.yml
"$PROMTOOL" test rules tests/monitoring/alerts.test.yml tests/monitoring/lxc-cpu.test.yml tests/monitoring/incremental-cpu.test.yml
if [[ $# -eq 0 ]]; then exit 0; fi
BASELINE="$1"
WORK_DIR=$(mktemp -d)
trap 'rm -rf "$WORK_DIR"' EXIT
python3 scripts/prepare-incremental-monitoring.py --baseline "$BASELINE" --output "$WORK_DIR/config" --report "$WORK_DIR/report.json"
"$PROMTOOL" check config "$WORK_DIR/config/check-prometheus.yml"
for JOB in node cadvisor blackbox; do
  "$PROMTOOL" check service-discovery --timeout=1s "$WORK_DIR/config/check-prometheus.yml" "$JOB" > "$WORK_DIR/$JOB-discovery.json"
done
python3 - "$WORK_DIR" <<'PY'
import json,sys
from pathlib import Path
p=Path(sys.argv[1]);report=json.loads((p/'report.json').read_text())
for job,count in [('node',17),('cadvisor',17),('blackbox',11)]:
 rows=json.loads((p/(job+'-discovery.json')).read_text())
 assert len(rows)==count
 keys=[(r['labels']['job'],r['labels']['instance']) + ((r['labels'].get('module'),r['labels'].get('probe_type')) if job=='blackbox' else ()) for r in rows]
 assert len(set(keys))==count
 if job=='node':assert sum(r['labels'].get('cpu_contract')=='lxc_cgroup_v1' for r in rows)==len(report['reliable_exporters_cts'])
print('PASS: actual discovery/relabeling counts and unique target identities; no deployment')
PY
python3 scripts/prepare-r1-exporters.py --output "$WORK_DIR/r1" >/dev/null
bash -n "$WORK_DIR/r1/node-cgroup.sh"
