#!/usr/bin/env bash
# Independent systemd ExecStopPost recovery: only CT627; never deletes data.
set -euo pipefail
[[ $(hostname) == pve ]]
pct exec 627 -- docker stop --time 5 voicebox-qwen-pilot-d067 >/dev/null 2>&1 || true
pct exec 627 -- python3 - <<'PY'
import json,subprocess,time,urllib.request
pilot=json.loads(subprocess.check_output(['docker','inspect','voicebox-qwen-pilot-d067']))[0]
assert not pilot['State']['Running'],'Do not load Kokoro until candidate stops'
c=json.loads(subprocess.check_output(['docker','inspect','voicebox']))[0]
assert c['Image']=='sha256:7f2e6f7e6a2d09c77ebd35424a7641249e51b8ff0374bc9c4acb1f7393cfcd4c'
if not c['State']['Running']:subprocess.run(['docker','start','voicebox'],check=True)
for i in range(20):
 try:
  req=urllib.request.Request('http://192.168.1.127:17493/models/load',data=b'{"model_name":"kokoro"}',headers={'Content-Type':'application/json'})
  with urllib.request.urlopen(req,timeout=90) as r:assert r.status==200
  break
 except Exception:
  if i==19:raise
  time.sleep(2)
print('D067 original image and Kokoro restored; no data removed')
PY
