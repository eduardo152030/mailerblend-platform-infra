"""Read the one D081 job from PVE; append private measurements, print brief status."""
from pathlib import Path
import subprocess,json,uuid
p=Path.home()/'.local/share/mailerblend-recovery/voicebox-d081';ident=uuid.UUID(json.loads((p/'submission.json').read_text())['id']).hex
r=subprocess.run(['ssh','-o','UserKnownHostsFile='+str(Path.home()/'.ssh/known_hosts'),'-o','StrictHostKeyChecking=yes','-o','BatchMode=yes','pve','python3 - '+ident],input=(Path(__file__).parent/'observe.py').read_text(),text=True,capture_output=True,check=True);d=json.loads(r.stdout)
with (p/'observations.jsonl').open('a') as f:f.write(r.stdout)
print(json.dumps({k:v for k,v in d.items() if k!='events'}));print(json.dumps({'events':[{k:x[k] for k in ['stage','elapsed','eos_emitted','sequence_tokens','seconds','shape'] if k in x} for x in d['events']]}))
