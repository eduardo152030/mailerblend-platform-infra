#!/usr/bin/env python3
"""Verify original production API and Alex after RAM/image rollback, preserving prior records."""
import array,hashlib,io,json,time,urllib.request,wave
from pathlib import Path
ROOT=Path.home()/'.local/share/mailerblend-recovery/voicebox-d066';BASE='http://192.168.1.127:17493'
def api(path,data=None):
 with urllib.request.urlopen(urllib.request.Request(BASE+path,data=None if data is None else json.dumps(data).encode(),headers={'Content-Type':'application/json'}),timeout=15) as r:return json.load(r)
for i in range(45):
 try:
  if api('/health')['status']=='healthy':break
 except Exception:pass
 time.sleep(2)
else:raise RuntimeError('Original API not recovered')
profiles=api('/profiles');before=json.loads((ROOT/'profiles-before.json').read_text());keys=['id','name','description','language','voice_type','preset_engine','preset_voice_id','default_engine','created_at','updated_at']
for p in before:
 after=next(x for x in profiles if x['id']==p['id']);assert all(after.get(k)==p.get(k) for k in keys)
assert len(profiles)==len(before),'Production profile set changed'
p=next(x for x in profiles if x['id']=='250f2938-c396-47e8-8b75-0bf9179d0252');assert p['preset_engine']=='kokoro' and p['preset_voice_id']=='em_alex'
request=ROOT/'alex-recovery-request.json'
if request.exists():record=json.loads(request.read_text());ident=record['generation_id'];started=record['started']
else:
 started=time.time();g=api('/generate',{'profile_id':p['id'],'engine':'kokoro','language':'es','seed':42,'personality':False,'text':'Hola, bienvenidos a nuestro canal. Hoy vamos a descubrir cómo funciona esta tecnología y por qué puede cambiar nuestra forma de trabajar. Vamos a comenzar.'});ident=g['id'];request.write_text(json.dumps({'generation_id':ident,'started':started},indent=2)+'\n')
for i in range(90):
 g=api('/history/'+ident)
 if g['status'] in ['completed','failed','cancelled']:break
 time.sleep(2)
assert g['status']=='completed',g.get('error')
with urllib.request.urlopen(BASE+'/audio/'+ident,timeout=15) as r:audio=r.read()
(ROOT/'alex-after-pilot.wav').write_bytes(audio)
with wave.open(io.BytesIO(audio)) as w:rate=w.getframerate();duration=w.getnframes()/rate;signal=array.array('h',w.readframes(w.getnframes()))
assert rate==24000 and duration>2 and max(abs(x) for x in signal)>100
result={'result':'PASS','engine':'kokoro','preset':'em_alex','generation_id':ident,'audio_url':BASE+'/audio/'+ident,'audio_seconds':duration,'observed_generation_seconds':time.time()-started,'sha256':hashlib.sha256(audio).hexdigest(),'all_production_profiles_preserved':True};(ROOT/'alex-recovery.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
