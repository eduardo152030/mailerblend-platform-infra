#!/usr/bin/env python3
"""Real server concurrency/409 and single-resident-model test, CT627 only."""
import json,time,urllib.request,urllib.error
from pathlib import Path
P=Path.home()/'.local/share/mailerblend-recovery/voicebox-d068';BASE='http://192.168.1.127:17493'
def api(path,value=None):
 with urllib.request.urlopen(urllib.request.Request(BASE+path,data=None if value is None else json.dumps(value).encode(),headers={'Content-Type':'application/json'}),timeout=20) as r:return json.load(r)
assert not (P/'concurrency.json').exists(),'Reconcile recorded IDs; do not repeat test'
text='Hoy vamos a explicar una idea de forma clara y sencilla. Primero comprobamos los detalles y preparamos los materiales. Después avanzamos paso a paso, con tiempo para revisar el resultado y mejorar lo que sea necesario.'
requests=[]
for pid,engine in [('6ab4fe0a-5a4f-4dc0-9b84-71b5173edfeb','piper'),('916ce396-1b15-4621-b63c-5eaf49f03b74','kokoro')]:
 g=api('/generate',{'profile_id':pid,'engine':engine,'text':text,'language':'es','seed':42,'personality':False});requests.append({'id':g['id'],'profile_id':pid,'engine':engine});(P/'concurrency-requests.json').write_text(json.dumps(requests,indent=2)+'\n')
try:api('/models/load',{'model_name':'kokoro'});raise AssertionError('Model mutation was not rejected during inference')
except urllib.error.HTTPError as e:assert e.code==409;blocked=409
start=time.monotonic();samples=[]
while time.monotonic()-start<180:
 models=[m['model_name'] for m in api('/models/status')['models'] if m['loaded']];assert len(models)<=1,models
 statuses=[api('/history/'+r['id'])['status'] for r in requests];samples.append({'elapsed':time.monotonic()-start,'loaded':models,'statuses':statuses})
 assert not any(s in ['failed','cancelled'] for s in statuses)
 if all(s=='completed' for s in statuses):break
 time.sleep(.5)
assert all(s=='completed' for s in statuses)
r={'result':'PASS','model_mutation_status':blocked,'jobs':requests,'samples':samples,'max_simultaneous_loaded_tts_models':max(len(x['loaded']) for x in samples),'elapsed':time.monotonic()-start};(P/'concurrency.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items() if k!='samples'}))
