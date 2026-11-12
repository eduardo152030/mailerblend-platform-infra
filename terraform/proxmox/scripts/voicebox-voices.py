#!/usr/bin/env python3
"""D064: alta aditiva de presets reales y muestras comparables, sin editar perfiles previos."""
import argparse,array,datetime,hashlib,io,json,math,shutil,time,urllib.request,wave
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[1];PRIVATE=Path.home()/'.local/share/mailerblend-recovery/voicebox-d064';BASE='http://192.168.1.127:17493'
def api(path,data=None):
 raw=None if data is None else json.dumps(data).encode()
 with urllib.request.urlopen(urllib.request.Request(BASE+path,data=raw,headers={'Content-Type':'application/json'}),timeout=30) as r:return json.load(r)
def save(name,obj):
 p=PRIVATE/name;p.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n');p.chmod(0o600)
def metrics():
 import re
 with urllib.request.urlopen('http://192.168.1.127:9100/metrics',timeout=10) as r:b=r.read().decode()
 def v(n):return float(re.search('^'+n+r'(?:\{[^\n]*\})? ([^\s]+)',b,re.M)[1])
 total=v('node_memory_MemTotal_bytes');available=v('node_memory_MemAvailable_bytes')
 return {'used_bytes':total-available,'available_percent':100*available/total,'cpu_seconds':v('lxc_cpu_usage_seconds_total')}
def profiles(spec):
 assert json.loads((PRIVATE/'restore-before/restore-check.json').read_text())['result']=='PASS','Backup restaurado requerido antes de mutaciones'
 before=api('/profiles');created=0;mapping={}
 presets=api('/profiles/presets/kokoro');rows=presets if isinstance(presets,list) else presets.get('voices',presets.get('presets',[]));allowed={p.get('id',p.get('voice_id',p.get('preset_voice_id'))) for p in rows}
 for c in spec['candidates']:
  assert c['engine']=='kokoro' and c['preset_voice_id'] in allowed
  desired={'name':c['name'],'description':'Candidatura D064: español soportado; acento peninsular, edad y estilo pendientes de escucha. Sin aceptación auditiva.','language':'es','voice_type':'preset','preset_engine':'kokoro','preset_voice_id':c['preset_voice_id'],'default_engine':'kokoro'}
  matches=[p for p in before if p['name']==desired['name']];assert len(matches)<=1
  if matches:profile=matches[0];assert all(profile.get(k)==v for k,v in desired.items()),'Perfil existente diferente; no modificar'
  else:profile=api('/profiles',desired);created+=1
  mapping[c['key']]=profile['id']
 final=api('/profiles');original=json.loads((PRIVATE/'profiles-before.json').read_text())
 static=['id','name','description','language','voice_type','preset_engine','preset_voice_id','default_engine','created_at','updated_at','effects_chain','personality','design_prompt']
 for p in original:
  after=next(x for x in final if x['id']==p['id']);assert all(after.get(k)==p.get(k) for k in static),'Perfil original alterado'
 save('catalog-profiles.json',mapping);print(json.dumps({'profiles_created':created,'original_profiles_preserved':len(original),'ids':mapping}))
def samples(spec):
 mapping=json.loads((PRIVATE/'catalog-profiles.json').read_text());results=[]
 for c in spec['candidates']:
  name=c['key']+'-request.json';path=PRIVATE/name
  if path.exists():record=json.loads(path.read_text());ident=record['generation_id'];assert record['profile_id']==mapping[c['key']]
  else:
   baseline=metrics();assert baseline['available_percent']>=20,'Falta margen de RAM; no iniciar siguiente candidato'
   started=time.time();g=api('/generate',{'profile_id':mapping[c['key']],'text':spec['text'],'language':'es','engine':'kokoro','seed':42,'personality':False,'normalize':True,'effects_chain':[]});ident=g['id'];record={'generation_id':ident,'profile_id':mapping[c['key']],'requested_at_unix':started,'baseline':baseline};save(name,record)
  observed=[metrics()];g=api('/history/'+ident)
  while g['status'] not in ['completed','failed','cancelled'] and time.time()-record['requested_at_unix']<600:
   time.sleep(2);g=api('/history/'+ident);observed.append(metrics())
  assert g['status']=='completed',g.get('error') or g['status']
  with urllib.request.urlopen(BASE+'/audio/'+ident,timeout=20) as r:audio=r.read()
  (PRIVATE/(c['key']+'.wav')).write_bytes(audio)
  with wave.open(io.BytesIO(audio)) as w:
   rate=w.getframerate();channels=w.getnchannels();width=w.getsampwidth();duration=w.getnframes()/rate;pcm=array.array('h',w.readframes(w.getnframes()))
  assert rate==24000 and channels==1 and width==2 and 2<duration<180 and max(abs(x) for x in pcm)>100
  result={'key':c['key'],'engine':'kokoro','preset_voice_id':c['preset_voice_id'],'profile_id':mapping[c['key']],'generation_id':ident,'audio_url':BASE+'/audio/'+ident,'seconds_to_completion_observed':round(time.time()-record['requested_at_unix'],2),'duration_seconds':duration,'format':'WAV PCM16 mono 24kHz','sha256':hashlib.sha256(audio).hexdigest(),'peak_sampled_ct_used_bytes':max(x['used_bytes'] for x in observed),'cpu_seconds':observed[-1]['cpu_seconds']-record['baseline']['cpu_seconds'],'source_gender':c['source_gender'],'perceived_gender_age_accent_style':'PENDING_USER_LISTENING','accepted':False}
  existing=PRIVATE/(c['key']+'-sample.json')
  if existing.exists():result=json.loads(existing.read_text());assert result['sha256']==hashlib.sha256(audio).hexdigest()
  else:save(c['key']+'-sample.json',result)
  results.append(result);print(json.dumps(result),flush=True)
 save('samples.json',{'result':'PASS technical generation only','text':spec['text'],'samples':results,'auditory_acceptance':'PENDING_USER_LISTENING'})
def reference(spec):
 global PRIVATE
 previous=PRIVATE;PRIVATE=previous/'after3072';PRIVATE.mkdir(mode=0o700,exist_ok=True)
 source=previous/'catalog-profiles.json';dest=PRIVATE/'catalog-profiles.json'
 if not dest.exists():shutil.copy2(source,dest)
 selected=dict(spec);selected['candidates']=[spec['candidates'][0]]
 try:samples(selected)
 finally:PRIVATE=previous
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action',choices=['profiles','samples','reference']);a=p.parse_args();spec=yaml.safe_load((ROOT/'services/infra-voicebox/voices-catalog.yml').read_text());assert spec.get('policy')!='PERSONAL_ONLY_D069','D069 personal-only policy: historical candidate workflow disabled';globals()[a.action](spec)
