#!/usr/bin/env python3
"""Prepared standalone API client; does not integrate Pipeline_videos_modulares.
Only identities explicitly marked TECHNICAL_SAMPLE_PASS may generate. Serializes
this client's requests, unloads previous models and preserves checkpoints on disk.
D068 server serializes jobs; local lock prevents duplicate submissions by this client.
"""
import argparse,fcntl,json,time,urllib.request,urllib.error
from pathlib import Path
import yaml
p=argparse.ArgumentParser();p.add_argument('identity',choices=['personal']);p.add_argument('--text-file',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--timeout',type=int,default=3600);a=p.parse_args()
root=Path(__file__).resolve().parents[1];d=yaml.safe_load((root/'services/infra-voicebox/voice-identities.yml').read_text())['identities'][a.identity]
assert d['profile_id'] and d['status']=='TECHNICAL_SAMPLE_PASS','Identity pending recordings, engine validation or complete sample; do not substitute a voice'
assert not a.output.exists(),'Preserve existing audio'
text=a.text_file.read_text().strip();assert 1<=len(text)<=50000
BASE='http://192.168.1.127:17493'
def api(path,data=None):
 for attempt in range(6):
  try:
   with urllib.request.urlopen(urllib.request.Request(BASE+path,data=None if data is None else json.dumps(data).encode(),headers={'Content-Type':'application/json'}),timeout=30) as r:return json.load(r)
  except urllib.error.HTTPError as e:
   # Only model operations are safely retried; never repeat POST/generate.
   if e.code!=409 or not path.startswith('/models/') or attempt==5:raise
   time.sleep(.5)

private=Path.home()/'.local/share/mailerblend-recovery/voicebox-client';private.mkdir(parents=True,exist_ok=True,mode=0o700)
with (private/'generation.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 # Also refuse a job from the UI or another machine observed at this instant.
 history=api('/history?limit=100')
 rows=history if isinstance(history,list) else history.get('items',history.get('generations',[]))
 assert not any(x['status'] in ['generating','pending','queued'] for x in rows),'Active/queued generation; wait before switching models'
 expected={'kokoro':'kokoro','piper':'piper-es-es','qwen_custom_voice':'qwen-custom-voice-0.6B','qwen':'qwen-tts-0.6B'}[d['engine']]
 for m in api('/models/status')['models']:
  if m['loaded'] and m['model_name']!=expected:api('/models/'+m['model_name']+'/unload',{})
 assert not any(m['loaded'] and m['model_name']!=expected for m in api('/models/status')['models'])
 api('/models/load',{'model_name':expected})
 request={'profile_id':d['profile_id'],'engine':d['engine'],'language':'es','text':text,'personality':False}
 if d['engine'] in ['qwen','qwen_custom_voice']:request['model_size']=d['model_size']
 g=api('/generate',request);ident=g['id'];receipt=private/(ident+'.json');receipt.write_text(json.dumps({'generation_id':ident,'identity':a.identity,'profile_id':d['profile_id']})+'\n');receipt.chmod(0o600)
 started=time.monotonic()
 while time.monotonic()-started<a.timeout:
  g=api('/history/'+ident)
  if g['status'] in ['completed','failed','cancelled']:break
  time.sleep(2)
 assert g['status']=='completed','Job not completed; reconcile recorded ID before another request'
 with urllib.request.urlopen(BASE+'/audio/'+ident,timeout=30) as r:audio=r.read()
 with a.output.open('xb') as f:f.write(audio)
 a.output.chmod(0o600);print(json.dumps({'generation_id':ident,'profile_id':d['profile_id'],'output':str(a.output)}))
