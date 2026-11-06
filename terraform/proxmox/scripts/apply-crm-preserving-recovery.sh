#!/usr/bin/env bash
# Run only inside the approved CRM target after validated backups/isolated restore.
set -euo pipefail
[[ "${1:-}" == --execute && -n "${2:-}" && -n "${3:-}" ]] || {
  echo 'Usage: apply-crm-preserving-recovery.sh --execute <verified-record.json> <compose-directory>' >&2; exit 2;
}
python3 - "$2" <<'PY'
import json,sys
record=json.load(open(sys.argv[1]))
assert all(record.get(k) is True for k in ['backup_verified','offhost_verified','restore_verified']), 'Verified recovery gates required.'
PY
cd "$3"
read -r IMAGE DATA_VOLUME < <(python3 - <<'PY'
from pathlib import Path
values=dict(l.split('=',1) for l in Path('recovery.env').read_text().splitlines() if l and not l.startswith('#'))
print(values['BUDIBASE_RECOVERY_IMAGE'],values['BUDIBASE_APP_DATA_VOLUME'])
PY
)
docker volume inspect "$DATA_VOLUME" >/dev/null
TARGET_IMAGE=$(docker image inspect --format '{{.Id}}' "$IMAGE")
COMPOSE=(docker compose --project-name budibase-recovery --env-file .env --env-file recovery.env -f docker-compose.yml -f docker-compose.recovery.yml)
"${COMPOSE[@]}" config --quiet
# -t -1 never escalates to SIGKILL. A CLI timeout stops this procedure, not the container forcibly.
if [[ "$(docker inspect --format '{{.State.Running}}' budibase-worker)" == true ]]; then
  timeout 120 docker stop -t -1 budibase-worker >/dev/null
fi
if docker inspect budibase-app >/dev/null 2>&1; then
  PROJECT=$(docker inspect --format '{{index .Config.Labels "com.docker.compose.project"}}' budibase-app)
  if [[ "$PROJECT" != budibase-recovery ]]; then
    [[ "$(docker inspect --format '{{.Image}}' budibase-app)" == "$TARGET_IMAGE" ]] || {
      echo 'Image differs from the approved installed image; refusing upgrade.' >&2; exit 1;
    }
    ! docker inspect budibase-app-pre-recovery >/dev/null 2>&1 || {
      echo 'Preserved original name already exists; inspect state before continuing.' >&2; exit 1;
    }
    timeout 120 docker stop -t -1 budibase-app >/dev/null
    docker rename budibase-app budibase-app-pre-recovery
  else
    # An identical second execution is allowed; an update that would delete/recreate is not.
    CURRENT_HASH=$(docker inspect --format '{{index .Config.Labels "com.docker.compose.config-hash"}}' budibase-app)
    PLANNED_HASH=$("${COMPOSE[@]}" config --hash budibase-app | awk '{print $2}')
    [[ "$CURRENT_HASH" == "$PLANNED_HASH" ]] || {
      echo 'Recovery container configuration differs; refusing an implicit recreation.' >&2; exit 1;
    }
  fi
else
  docker inspect budibase-app-pre-recovery >/dev/null
fi
"${COMPOSE[@]}" up -d --no-deps --no-build --pull never budibase-app
ACTUAL_VOLUME=$(docker inspect --format '{{range .Mounts}}{{if eq .Destination "/data"}}{{.Name}}{{end}}{{end}}' budibase-app)
[[ "$ACTUAL_VOLUME" == "$DATA_VOLUME" ]] || { echo 'Unexpected data-volume identity.' >&2; exit 1; }
[[ "$(docker inspect --format '{{.Image}}' budibase-app)" == "$TARGET_IMAGE" ]] || exit 1
echo 'Recovery app applied; original app and duplicate worker retained stopped, original data volume preserved.'
