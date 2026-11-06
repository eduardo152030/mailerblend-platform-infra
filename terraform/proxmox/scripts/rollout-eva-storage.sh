#!/usr/bin/env bash
# Run inside the approved EVA target, with the reviewed model already staged.
set -euo pipefail
[[ "${1:-}" == --execute && -n "${2:-}" && -n "${3:-}" ]] || {
  echo 'Usage: rollout-eva-storage.sh --execute <verified-record.json> <baseline.json>' >&2; exit 2;
}
HELPERS=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
RECORD="$2"
BASELINE="$3"
READINESS_TIMEOUT=${READINESS_TIMEOUT:-120}
READINESS_INTERVAL=${READINESS_INTERVAL:-2}
[[ "$READINESS_TIMEOUT" =~ ^[1-9][0-9]*$ && "$READINESS_INTERVAL" =~ ^[1-9][0-9]*$ ]] || exit 2
python3 - "$RECORD" "$BASELINE" <<'PY'
import json,sys
r=json.load(open(sys.argv[1]));json.load(open(sys.argv[2]))
assert all(r.get(k) is True for k in ['backup_verified','offhost_verified','restore_verified'])
PY
diagnose() {
  echo 'EVA rollout failed; no forced stop or data removal performed. Inspect the current stage before resuming.' >&2
  docker ps -a --format 'table {{.Names}}\t{{.State}}\t{{.Status}}' >&2 || true
}
trap diagnose ERR
apply() { bash "$HELPERS/apply-eva-preserving-logging.sh" --execute "$RECORD" "$1"; }
probe() {
  case "$1" in
    postgres) docker exec eva-postgres sh -c 'pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"' >/dev/null 2>&1 ;;
    cron)
      docker exec eva-cron-digest sh -c 'command -v curl >/dev/null && test -s /etc/periodic/daily/send-digest' >/dev/null 2>&1 &&
        docker top eva-cron-digest -eo pid,comm | awk 'NR>1 {if ($2=="crond") ok=1} END {exit !ok}'
      ;;
    api|focalboard)
      python3 - "$1" <<'PY' >/dev/null 2>&1
import sys,urllib.request
port,path=(8001,'/health') if sys.argv[1]=='api' else (8002,'/')
with urllib.request.urlopen('http://192.168.1.122:'+str(port)+path,timeout=5) as r:
    assert r.status==200
PY
      ;;
  esac
}
wait_ready() {
  local deadline=$((SECONDS+READINESS_TIMEOUT))
  until probe "$1"; do
    if ((SECONDS>=deadline)); then
      echo "Readiness timeout (${READINESS_TIMEOUT}s): $1" >&2
      return 1
    fi
    sleep "$READINESS_INTERVAL"
  done
  echo "Readiness passed: $1"
}
# Pilot a stateless service before the coordinated database window.
apply eva-api
wait_ready api
apply docker-cleanup
PROJECT=$(docker inspect --format '{{index .Config.Labels "com.docker.compose.project"}}' eva-postgres)
if [[ "$PROJECT" != eva-storage-recovery ]]; then
  # No escalation to SIGKILL. A timeout aborts the rollout.
  for name in eva-api eva-scheduler eva-sync eva-cron-digest focalboard; do
    bash "$HELPERS/stop-eva-container.sh" --execute "$RECORD" "$name"
  done
fi
apply postgres
wait_ready postgres
apply focalboard
wait_ready focalboard
apply eva-api
wait_ready api
for service in eva-scheduler eva-sync eva-cron-digest; do apply "$service"; done
wait_ready cron
python3 "$HELPERS/check-eva-functional.py" "$BASELINE"
echo 'EVA storage logging rollout validated; preserved originals remain stopped.'
