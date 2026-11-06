#!/usr/bin/env bash
# Apply one reviewed logging replacement; no removal, build, pull or orphan cleanup.
set -euo pipefail
[[ "${1:-}" == --execute && -n "${2:-}" && -n "${3:-}" ]] || {
  echo 'Usage: apply-eva-preserving-logging.sh --execute <verified-record.json> <service>' >&2; exit 2;
}
python3 - "$2" <<'PY'
import json,sys
r=json.load(open(sys.argv[1]));assert all(r.get(k) is True for k in ['backup_verified','offhost_verified','restore_verified'])
PY
SERVICE="$3"
case "$SERVICE" in
 postgres) NAME=eva-postgres ;;
 eva-api|eva-scheduler|eva-sync|eva-cron-digest) NAME="$SERVICE" ;;
 docker-cleanup) NAME=eva-docker-cleanup ;;
 focalboard) NAME=focalboard ;;
 *) echo 'Unknown EVA service.' >&2; exit 2 ;;
esac
cd /opt/infra-eva-assistant-bot
COMPOSE=(docker compose --project-name eva-storage-recovery --project-directory /opt/infra-eva-assistant-bot -f docker-compose.storage-recovery.yml)
"${COMPOSE[@]}" config --quiet
PLANNED_HASH=$("${COMPOSE[@]}" config --hash "$SERVICE" | awk '{print $2}')
install -d -m 700 .storage-recovery
RECORD_FILE=".storage-recovery/$SERVICE.json"
# Compare private runtime values in memory before stopping anything; never print them.
PRECHECK_NAME="$NAME"
if ! docker inspect "$PRECHECK_NAME" >/dev/null 2>&1; then
  PRECHECK_NAME="$NAME-pre-storage-recovery"
fi
python3 - "$SERVICE" "$PRECHECK_NAME" <<'PY_CHECK'
import json,subprocess,sys
service,name=sys.argv[1:]
model=json.loads(subprocess.check_output(['docker','compose','--project-name','eva-storage-recovery','--project-directory','/opt/infra-eva-assistant-bot','-f','docker-compose.storage-recovery.yml','config','--format','json'],text=True))['services'][service]
a=json.loads(subprocess.check_output(['docker','inspect',name],text=True))[0]
image=json.loads(subprocess.check_output(['docker','image','inspect',model['image']],text=True))[0]
assert a['Image']==image['Id'],'Installed image identity differs'
expected=dict(x.split('=',1) for x in image['Config'].get('Env',[]) if '=' in x)
expected.update(model.get('environment',{}))
actual=dict(x.split('=',1) for x in a['Config'].get('Env',[]) if '=' in x)
assert expected==actual,'Environment differs from preserved container; values withheld'
if service!='docker-cleanup':
    command=model.get('command')
    entrypoint=model.get('entrypoint')
    # An explicit Compose entrypoint clears the image's default command.
    if command is None and entrypoint is None: command=image['Config'].get('Cmd')
    if entrypoint is None: entrypoint=image['Config'].get('Entrypoint')
    assert command==a['Config'].get('Cmd'),'Application command differs'
    assert entrypoint==a['Config'].get('Entrypoint'),'Entrypoint differs'
PY_CHECK
if docker inspect "$NAME" >/dev/null 2>&1; then
  PROJECT=$(docker inspect --format '{{index .Config.Labels "com.docker.compose.project"}}' "$NAME")
  if [[ "$PROJECT" != eva-storage-recovery ]]; then
    ! docker inspect "$NAME-pre-storage-recovery" >/dev/null 2>&1 || exit 1
    bash "$(dirname -- "${BASH_SOURCE[0]}")/stop-eva-container.sh" --execute "$2" "$NAME"
    docker rename "$NAME" "$NAME-pre-storage-recovery"
  else
    # Compare the reviewed input recorded at application time. Compose's runtime
    # config-hash can differ from `config --hash` after applying CLI overrides.
    if [[ -f "$RECORD_FILE" ]]; then
      python3 - "$RECORD_FILE" "$PLANNED_HASH" "$NAME" <<'PY_RECORD'
import json,subprocess,sys
r=json.load(open(sys.argv[1]))
identity=subprocess.check_output(['docker','inspect','--format','{{.Id}}',sys.argv[3]],text=True).strip()
assert r['planned_hash']==sys.argv[2] and r['container_id']==identity,'Reviewed model or container identity changed; refusing implicit recreation'
PY_RECORD
    else
      [[ "${ALLOW_ADOPT_VERIFIED_RECOVERY:-0}" == 1 ]] || {
        echo 'Missing application record; verify the existing container before explicit adoption.' >&2; exit 1;
      }
    fi
  fi
else
  docker inspect "$NAME-pre-storage-recovery" >/dev/null
fi
"${COMPOSE[@]}" up -d --no-recreate --no-deps --no-build --pull never "$SERVICE"
python3 - "$NAME" <<'PY'
import json,subprocess,sys
name=sys.argv[1]
a=json.loads(subprocess.check_output(['docker','inspect',name],text=True))[0]
b=json.loads(subprocess.check_output(['docker','inspect',name+'-pre-storage-recovery'],text=True))[0]
assert a['Image']==b['Image'],'Installed image changed'
assert sorted(a['Config'].get('Env',[]))==sorted(b['Config'].get('Env',[])),'Environment changed'
for k in ['Memory','MemorySwap','NanoCpus','Privileged','RestartPolicy']:
    assert a['HostConfig'].get(k)==b['HostConfig'].get(k),'Resource/runtime policy changed: '+k
# Bind sources and destinations must be the preserved production paths.
assert sorted((m['Source'],m['Destination'],m['RW']) for m in a['Mounts'])==sorted((m['Source'],m['Destination'],m['RW']) for m in b['Mounts']),'Persistent mounts changed'
assert a['HostConfig']['LogConfig']=={'Type':'json-file','Config':{'max-file':'5','max-size':'20m'}}
print('Preserved image/data mounts and verified bounded logging:',name)
PY
python3 - "$RECORD_FILE" "$PLANNED_HASH" "$NAME" <<'PY_SAVE'
import json,os,subprocess,sys
identity=subprocess.check_output(['docker','inspect','--format','{{.Id}}',sys.argv[3]],text=True).strip()
fd=os.open(sys.argv[1],os.O_WRONLY|os.O_CREAT|os.O_TRUNC,0o600)
with os.fdopen(fd,'w') as f:json.dump({'planned_hash':sys.argv[2],'container_id':identity},f)
PY_SAVE
