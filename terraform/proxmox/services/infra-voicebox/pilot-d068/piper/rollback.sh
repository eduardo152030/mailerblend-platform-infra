#!/usr/bin/env bash
# Restore the exact last stable recipe/image, preserving every DB/profile/audio file.
set -euo pipefail
[[ $(hostname) == pve ]]
attempt=${D068_ACTIVATION:-02}
[[ "$attempt" =~ ^[0-9]+$ ]]
if [[ -f /root/voicebox-d068/production${attempt}/technical-pass ]]; then exit 0; fi
pct exec 627 -- python3 - <<'PYOVERLAY'
from pathlib import Path
import shutil
base=Path('/opt/voicebox');overlay=base/'d068-rollback/overlay'
if overlay.exists():
 for src in overlay.rglob('*'):
  if src.is_file():
   target=base/src.relative_to(overlay);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,target)
PYOVERLAY
pct exec 627 -- bash -c 'cp /opt/voicebox/d068-rollback/compose.yml /opt/voicebox/compose.yml; cp /opt/voicebox/d068-rollback/image-lock.json /opt/voicebox/image-lock.json; cp /opt/voicebox/d068-rollback/deploy.sh /opt/voicebox/deploy.sh; docker compose -f /opt/voicebox/compose.yml up -d --no-deps --no-build voicebox'
pct exec 627 -- python3 - <<'PY'
import json,subprocess,time,urllib.request
from pathlib import Path
expected=json.loads(Path('/opt/voicebox/d068-rollback/image-lock.json').read_text())['image_id'];c=json.loads(subprocess.check_output(['docker','inspect','voicebox']))[0];assert c['Image']==expected
for _ in range(40):
 try:
  req=urllib.request.Request('http://192.168.1.127:17493/models/load',data=b'{"model_name":"kokoro"}',headers={'Content-Type':'application/json'})
  with urllib.request.urlopen(req,timeout=30) as r:assert r.status==200
  print('PASS last stable image and Kokoro restored; profiles/audio untouched');break
 except Exception:time.sleep(2)
else:raise RuntimeError('Stable Kokoro did not recover')
PY
