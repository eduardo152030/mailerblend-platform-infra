"""Explicit single Voicebox request, identical private D078 trading text. No retries."""
from pathlib import Path
import json,hashlib,subprocess,urllib.request,os
p=Path.home()/'.local/share/mailerblend-recovery/voicebox-d080'
assert not (p/'submission-started.json').exists(),'An attempt already exists; inspect instead of retrying'
assert json.loads((p/'preflight-final.json').read_text())['predictive_preflight']['passed']
ssh=['ssh','-o','UserKnownHostsFile='+str(Path.home()/'.ssh/known_hosts'),'-o','StrictHostKeyChecking=yes','-o','BatchMode=yes','pve']
text=subprocess.check_output(ssh+['pct exec 627 -- cat /srv/voicebox/qwen-worker/jobs/73a3755f5b194d33aba379e43bf6d72b/text.txt']).decode()
assert len(text)==573 and hashlib.sha256(text.encode()).hexdigest()=='c09d243905eac563e8379e6bc496a32347f3c1dc445ed577e8240baacfc47972'
body={'profile_id':'1fd00418-2a79-4178-883f-af6c3f5e07ee','text':text,'language':'es','seed':42,'model_size':'0.6B','engine':'qwen','personality':False,'max_chunk_chars':800,'normalize':True}
(p/'request.private.json').write_text(json.dumps(body));(p/'request.private.json').chmod(0o600)
with (p/'submission-started.json').open('x') as f:json.dump({'submitted_once':True,'text_sha256':hashlib.sha256(text.encode()).hexdigest(),'chars':573},f)
req=urllib.request.Request('http://192.168.1.127:17493/generate',data=json.dumps(body).encode(),headers={'Content-Type':'application/json'},method='POST')
with urllib.request.urlopen(req,timeout=30) as r:data=json.load(r)
(p/'submission.json').write_text(json.dumps(data));(p/'submission.json').chmod(0o600)
print(json.dumps({k:v for k,v in data.items() if k in ['id','status','created_at','engine','model_size']}))
