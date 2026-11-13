"""PVE CT627-only image build; no deployment or model loading."""
from pathlib import Path
import subprocess,json,hashlib
OLD='sha256:212703647c03d428adc30f8bf4b864af82690eb41f4fe8ca052ff10dbaa45386';BASE='/srv/voicebox/input1200-deploy/context';TAG='local/voicebox:input1200-3987cab'
def ct(*a):return subprocess.check_output(['pct','exec','627','--',*a],text=True,timeout=120)
pid=subprocess.check_output(['lxc-info','-n','627','-pH'],text=True).strip();root=Path('/proc',pid,'root');context=root/BASE.lstrip('/');m=json.loads((context/'context-manifest.json').read_text())
for n,h in m['files'].items():assert hashlib.sha256((context/n).read_bytes()).hexdigest()==h
old=json.loads(ct('docker','image','inspect','local/voicebox:d086-uid999-candidate'))[0];assert old['Id']==OLD
assert json.loads(ct('docker','inspect','voicebox'))[0]['State']['Health']['Status']=='healthy'
assert subprocess.run(['pct','exec','627','--','docker','image','inspect',TAG],capture_output=True).returncode!=0,'Tag already exists; no blind rebuild'
proc=subprocess.run(['pct','exec','627','--','docker','build','--network','none','--pull=false','--tag',TAG,BASE],check=True)
new=json.loads(ct('docker','image','inspect',TAG))[0]
for k in ['User','Entrypoint','Cmd','Env','Healthcheck','WorkingDir']:assert new['Config'].get(k)==old['Config'].get(k),'Image config drift: '+k
assert new['Config']['User']=='999:999';assert new['Config']['Labels']['voicebox.base.image']==OLD
r={'image':TAG,'image_id':new['Id'],'base_image_id':OLD,'user':new['Config']['User'],'entrypoint':new['Config']['Entrypoint'],'cmd':new['Config']['Cmd'],'context_manifest_sha256':hashlib.sha256((context/'context-manifest.json').read_bytes()).hexdigest(),'no_deployment_or_inference':True};Path('/mnt/storage/input1200-deploy/image.json').write_text(json.dumps(r));print(json.dumps(r))
