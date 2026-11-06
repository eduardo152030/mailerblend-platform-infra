#!/usr/bin/env bash
# Orderly application stop; two narrowly scoped owner-authorized idle exceptions.
set -euo pipefail
[[ "${1:-}" == --execute && -n "${2:-}" && -n "${3:-}" ]] || {
  echo 'Usage: stop-eva-container.sh --execute <verified-record.json> <container>' >&2; exit 2;
}
python3 - "$2" <<'PY'
import json,sys
r=json.load(open(sys.argv[1]));assert all(r.get(k) is True for k in ['backup_verified','offhost_verified','restore_verified'])
PY
NAME="$3"
case "$NAME" in eva-api|eva-postgres|eva-scheduler|eva-sync|eva-cron-digest|eva-docker-cleanup|focalboard) ;; *) exit 2 ;; esac
[[ "$(docker inspect --format '{{.State.Running}}' "$NAME")" == true ]] || exit 0
SIGNAL=SIGTERM
if [[ "$NAME" == eva-scheduler || "$NAME" == eva-sync ]]; then
  # CPython registers SIGINT/KeyboardInterrupt; these processes have no SIGTERM handler.
  docker exec "$NAME" cat /proc/1/status | python3 -c 'import sys; d=dict(x.split(":",1) for x in sys.stdin if ":" in x); assert int(d["SigCgt"].strip(),16)&2, "No SIGINT handler; refusing unverified shutdown"'
  SIGNAL=SIGINT
fi
ALLOW_IDLE_FORCE=0
[[ "$NAME" != eva-docker-cleanup || "${ALLOW_FORCE_MAINTENANCE:-0}" != 1 ]] || ALLOW_IDLE_FORCE=1
[[ "$NAME" != eva-cron-digest || "${ALLOW_FORCE_CRON:-0}" != 1 ]] || ALLOW_IDLE_FORCE=1
if [[ "$ALLOW_IDLE_FORCE" == 1 ]]; then
  # No application-data mounts or active maintenance/job processes may be present.
  python3 - "$NAME" <<'PY_IDLE'
import json,subprocess,sys
name=sys.argv[1]
assert name in ['eva-docker-cleanup','eva-cron-digest']
c=json.loads(subprocess.check_output(['docker','inspect',name],text=True))[0]
assert c['State']['Running']
allowed=['/etc/localtime','/etc/timezone']+(['/var/run/docker.sock'] if name=='eva-docker-cleanup' else [])
assert all(m['Destination'] in allowed for m in c['Mounts'])
commands=subprocess.check_output(['docker','top',name,'-eo','pid,comm'],text=True).splitlines()[1:]
expected=['sh','sleep'] if name=='eva-docker-cleanup' else ['crond']
assert sorted(x.split()[-1] for x in commands)==expected,'Container is not idle; refusing forced stop'
if name=='eva-cron-digest':
    api=json.loads(subprocess.check_output(['docker','inspect','eva-api'],text=True))[0]
    assert not api['State']['Running'],'API must be stopped before the cron exception'
print('Owner-authorized idle-only exception:',name)
PY_IDLE
  docker kill --signal=KILL "$NAME" >/dev/null
else
  timeout 120 docker stop --signal="$SIGNAL" -t -1 "$NAME" >/dev/null
fi
