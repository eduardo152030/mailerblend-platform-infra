"""PVE read-only collection of completed single D080 job; private metrics only."""
from pathlib import Path
import subprocess,json,hashlib,sys,re
pid=subprocess.check_output(['lxc-info','-n','627','-pH'],text=True).strip();root=Path('/proc',pid,'root');assert re.fullmatch('[a-f0-9]{32}',sys.argv[1]);job=root/'srv/voicebox/qwen-worker/jobs'/sys.argv[1]
state=json.loads((job/'state.json').read_text());assert state['status'] in ['completed','failed','cancelled']
result={}
for name in ['state.json','talker-supervisor.json','decoder-supervisor.json','talker-release.json','checkpoint/manifest.json','checkpoint/COMMITTED.json']:
 if (job/name).is_file():result[name]=json.loads((job/name).read_text())
result['checkpoint_integrity']=False
if 'checkpoint/COMMITTED.json' in result:
 m=result['checkpoint/manifest.json'];assert hashlib.sha256((job/'checkpoint/manifest.json').read_bytes()).hexdigest()==result['checkpoint/COMMITTED.json']['manifest_sha256'];assert hashlib.sha256((job/'checkpoint/codes.npy').read_bytes()).hexdigest()==m['codes']['sha256'];result['checkpoint_integrity']=True
print(json.dumps(result))
