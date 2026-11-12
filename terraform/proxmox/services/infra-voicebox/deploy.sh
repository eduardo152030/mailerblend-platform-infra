#!/usr/bin/env bash
# Ejecutar exclusivamente DENTRO de CT627 tras bootstrap SSH D062.
set -euo pipefail
[[ $(hostname) == infra-voicebox ]] || { echo 'Identidad CT incorrecta'; exit 1; }
revision=8af7efe62fab8d33e2a5dfbedabaa45f68a5184f
base=/opt/voicebox
image=local/voicebox:8af7efe62fab-cpu-d063
if [[ -f "$base/image-lock.json" ]]; then
  image=$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["image"])' "$base/image-lock.json")
fi
mkdir -p "$base" /srv/voicebox/data /srv/voicebox/huggingface
cd "$base"
# D077: the isolated Qwen supervisor is managed from PVE by production-d077.
# A routine app-only reconciliation must not run the historical model preparation.
if [[ -f image-lock.json ]] && python3 -c 'import json,sys;sys.exit(0 if json.load(open("image-lock.json")).get("integration") in ("d077-isolated", "d079-isolated") else 1)'; then
  python3 - <<'PYD077'
from pathlib import Path
import json,time,subprocess,hashlib
p=Path('/opt/voicebox');lock=json.loads((p/'image-lock.json').read_text())
assert json.loads(subprocess.check_output(['docker','image','inspect',lock['image']]))[0]['Id']==lock['image_id']
for name,digest in lock['overlay_files'].items():
 assert hashlib.sha256((p/name).read_bytes()).hexdigest()==digest,'D077 overlay differs: '+name
data=Path('/srv/voicebox/data')
for name,digest in lock.get('persistent_files',{}).items():
 target=(data/name).resolve();assert target.is_relative_to(data)
 assert hashlib.sha256(target.read_bytes()).hexdigest()==digest,'Managed file differs: '+name
h=json.loads(Path('/srv/voicebox/qwen-worker/jobs/agent-heartbeat.json').read_text())
assert h['status']=='healthy' and time.time()-h['timestamp']<8,'Use production-d077 from the control workspace to recover supervisor627'
PYD077
  docker compose -f compose.yml config --quiet
  docker compose -f compose.yml up -d --no-build --pull never --no-deps voicebox
  exit 0
fi
if [[ ! -d source/.git ]]; then
  git clone --no-checkout https://github.com/eduardo152030/voicebox.git source
fi
[[ -z $(git -C source status --porcelain) ]] || { echo 'Checkout modificado: conservar y revisar'; exit 1; }
git -C source checkout --detach "$revision"
[[ $(git -C source rev-parse HEAD) == "$revision" ]]
docker compose -f compose.yml config --quiet
build_input=$(sha256sum Dockerfile.cpu | cut -d' ' -f1)
if [[ -f image-lock.json ]]; then
  python3 - <<'PYLOCK'
from pathlib import Path
import json,hashlib
base=Path('/opt/voicebox').resolve();lock=json.loads((base/'image-lock.json').read_text())
for rel,wanted in lock.get('overlay_files',{}).items():
 p=(base/rel).resolve();assert p.is_relative_to(base) and p.is_file(),rel
 assert hashlib.sha256(p.read_bytes()).hexdigest()==wanted,'Overlay differs from reviewed image: '+rel
for rel,wanted in lock.get('persistent_files',{}).items():
 p=(Path('/srv/voicebox/data')/rel).resolve();assert p.is_relative_to(Path('/srv/voicebox/data'))
 assert hashlib.sha256(p.read_bytes()).hexdigest()==wanted,'Managed Piper file differs: '+rel
PYLOCK
  expected_image=$(python3 -c 'import json;print(json.load(open("image-lock.json"))["image_id"])')
  expected_dockerfile=$(python3 -c 'import json;print(json.load(open("image-lock.json"))["dockerfile_sha256"])')
  [[ "$build_input" == "$expected_dockerfile" ]] || { echo 'Dockerfile distinto de la imagen aprobada; preparar candidato y revisar lock'; exit 1; }
  if ! docker image inspect "$image" >/dev/null 2>&1; then
    [[ -n "${VOICEBOX_IMAGE_ARCHIVE:-}" ]] || { echo 'Para restaurar: indicar VOICEBOX_IMAGE_ARCHIVE con el archivo aprobado'; exit 1; }
    expected_archive=$(python3 -c 'import json;print(json.load(open("image-lock.json"))["archive_sha256"])')
    [[ $(sha256sum "$VOICEBOX_IMAGE_ARCHIVE" | cut -d' ' -f1) == "$expected_archive" ]]
    gzip -dc "$VOICEBOX_IMAGE_ARCHIVE" | docker image load
  fi
  [[ $(docker image inspect "$image" --format '{{.Id}}') == "$expected_image" ]] || { echo 'Imagen distinta de la aprobada; no desplegar'; exit 1; }
else
  # Solo preparación inicial de candidato. No sustituye revisión de imagen/lock.
  if ! docker image inspect "$image" >/dev/null 2>&1 || [[ ! -f build-input.sha256 ]] || [[ $(cat build-input.sha256) != "$build_input" ]]; then
    if previous=$(docker image inspect "$image" --format '{{.Id}}' 2>/dev/null); then
      docker tag "$previous" "local/voicebox:rollback-${previous#sha256:}"
    fi
    docker compose -f compose.yml build
    printf '%s\n' "$build_input" > build-input.sha256
  fi
fi
if ! cmp -s voicebox-lan-only.service /etc/systemd/system/voicebox-lan-only.service; then
  install -m 0644 voicebox-lan-only.service /etc/systemd/system/voicebox-lan-only.service
  systemctl daemon-reload
fi
bash lan-only.sh
systemctl enable --now voicebox-lan-only.service
docker run --rm --no-healthcheck --name voicebox-models-prepare-d063 --memory=900m --memory-swap=1200m --cpus=3 \
  -v /srv/voicebox/huggingface:/home/voicebox/.cache/huggingface \
  -v "$base/prepare-models.py:/prepare-models.py:ro" \
  -v "$base/model-lock.json:/model-lock.json:ro" \
  "$image" python /prepare-models.py
docker compose -f compose.yml up -d --no-deps voicebox
# Unhealthy no implica reinicio automático; revisar salud JSON y prueba TTS aparte.
docker image inspect "$image" --format '{{.Id}}' > image-id.candidate
cmp -s image-id.candidate image-id.txt || cp image-id.candidate image-id.txt
docker exec voicebox python -m pip freeze > requirements-observed.candidate
cmp -s requirements-observed.candidate requirements-observed.txt || cp requirements-observed.candidate requirements-observed.txt

# D069: reconcile only the existing owner identity/settings, never create profiles.
if [[ -f "$base/pilot-d069/personal-config.py" ]]; then
  python3 "$base/pilot-d069/personal-config.py"
fi
