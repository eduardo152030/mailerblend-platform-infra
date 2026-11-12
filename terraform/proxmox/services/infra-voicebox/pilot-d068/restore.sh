#!/usr/bin/env bash
# Independent recovery, only CT627; preserve images, volumes, profiles and samples.
set -euo pipefail
[[ $(hostname) == pve ]]
pct exec 627 -- python3 - <<'PY'
import json,subprocess,time,urllib.request
ids=subprocess.check_output(['docker','ps','-q','--filter','label=voicebox.pilot=D068'],text=True).split()
for ident in ids:subprocess.run(['docker','stop','--time','5',ident],check=True,timeout=20,stdout=subprocess.DEVNULL)
assert not subprocess.check_output(['docker','ps','-q','--filter','label=voicebox.pilot=D068'],text=True).strip()
c=json.loads(subprocess.check_output(['docker','inspect','voicebox']))[0]
assert c['Image']=='sha256:7f2e6f7e6a2d09c77ebd35424a7641249e51b8ff0374bc9c4acb1f7393cfcd4c'
if not c['State']['Running']:subprocess.run(['docker','start','voicebox'],check=True)
for _ in range(40):
 try:
  req=urllib.request.Request('http://192.168.1.127:17493/models/load',data=b'{"model_name":"kokoro"}',headers={'Content-Type':'application/json'})
  with urllib.request.urlopen(req,timeout=60) as r:assert r.status==200
  print('PASS original image and Kokoro restored; no data deleted');break
 except Exception:time.sleep(2)
else:raise RuntimeError('Kokoro recovery failed')
PY
