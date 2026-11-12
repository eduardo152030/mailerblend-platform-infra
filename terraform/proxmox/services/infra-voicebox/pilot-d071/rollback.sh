#!/usr/bin/env bash
# D071 recovery: code/config only, keep every profile/reference/generated audio.
set -euo pipefail
[[ $(hostname) == infra-voicebox ]]
base=/opt/voicebox
backup=$base/backups/d071-before
for file in compose.yml image-lock.json deploy.sh voice-identities.yml; do
  install -m 0600 "$backup/$file" "$base/$file"
done
# The recovered image must not resume QwenCPU generation.
python3 - <<'PY'
from pathlib import Path
p=Path('/opt/voicebox/compose.yml');s=p.read_text().replace("VOICEBOX_BASE_CPU_ENABLED: '1'","VOICEBOX_BASE_CPU_ENABLED: '0'");p.write_text(s)
PY
docker stop --timeout 10 voicebox-openvoice >/dev/null || true
docker compose -p voicebox -f "$base/compose.yml" up -d --no-deps --no-build voicebox
python3 - <<'PY'
import urllib.request,json,time
base='http://192.168.1.127:17493'
def api(path,data=None,method=None):
 with urllib.request.urlopen(urllib.request.Request(base+path,data=None if data is None else json.dumps(data).encode(),headers={'Content-Type':'application/json'},method=method),timeout=10) as r:return json.load(r)
for _ in range(50):
 try:
  if api('/health')['status']=='healthy':break
 except Exception:pass
 time.sleep(1)
else:raise RuntimeError('Rollback API unhealthy')
p=api('/profiles/1fd00418-2a79-4178-883f-af6c3f5e07ee');schema=api('/openapi.json')['components']['schemas']['VoiceProfileCreate']['properties'];d={k:v for k,v in p.items() if k in schema};d['default_engine']='qwen';api('/profiles/'+p['id'],d,'PUT');assert api('/profiles/'+p['id']+'/samples');print('PASS rollback original image/API/profile; QwenCPU remains disabled')
PY
