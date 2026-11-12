#!/usr/bin/env python3
"""PVE controlled production acceptance; no user auditory acceptance implied."""
import os
import array,hashlib,io,json,subprocess,time,urllib.request,urllib.error,wave
from pathlib import Path
CG=Path('/sys/fs/cgroup/lxc/627');ATTEMPT=os.environ.get('D068_ACTIVATION','02');assert ATTEMPT.isdigit();OUT=Path('/root/voicebox-d068/production'+ATTEMPT);OUT.mkdir(mode=0o700,parents=True,exist_ok=False);started=time.monotonic();sw=int((CG/'memory.swap.current').read_text());events=dict(x.split() for x in (CG/'memory.events').read_text().splitlines());peak=0;result={'result':'IN_PROGRESS','samples':[]}
def api(path,value=None):
 req=urllib.request.Request('http://192.168.1.127:17493'+path,data=None if value is None else json.dumps(value).encode(),headers={'Content-Type':'application/json'})
 with urllib.request.urlopen(req,timeout=15) as r:return json.load(r)
def check():
 global peak
 cur=int((CG/'memory.current').read_text());peak=max(peak,cur);ev=dict(x.split() for x in (CG/'memory.events').read_text().splitlines())
 assert cur<int(6.5*2**30) and int((CG/'memory.swap.current').read_text())-sw<64*2**20 and all(int(ev[k])==int(events[k]) for k in ['oom','oom_kill','oom_group_kill']),'Memory safety stop'
 with urllib.request.urlopen('http://192.168.1.110:9090/api/v1/targets',timeout=5) as r:t=json.load(r)
 assert all(t['health']=='up' for t in t['data']['activeTargets'] if t['labels'].get('service')!='infra-voicebox')
try:
 before=api('/profiles');assert not any(x['name']=='Eduardo — Personal Voice' for x in before)
 subprocess.run(['pct','exec','627','--','bash','-c','cp /opt/voicebox/pilot-d068/release/compose.yml /opt/voicebox/compose.yml && cp /opt/voicebox/pilot-d068/release/image-lock.json /opt/voicebox/image-lock.json && cp /opt/voicebox/pilot-d068/release/deploy.sh /opt/voicebox/deploy.sh && docker compose -f /opt/voicebox/compose.yml up -d --no-deps --no-build voicebox'],check=True,timeout=120)
 for _ in range(60):
  try:
   if api('/health')['status']=='healthy':break
  except Exception:pass
  time.sleep(1)
 else:raise RuntimeError('Candidate startup failed')
 profiles=api('/profiles');assert {x['id'] for x in profiles}=={x['id'] for x in before}
 existing=[x for x in profiles if x['name']=='ES Female — Narrator · Piper es_ES'];assert len(existing)<=1
 female=existing[0] if existing else api('/profiles',{'name':'ES Female — Narrator · Piper es_ES','description':'D068: Piper es_ES-sharvard, speaker1 F, fuente español de España y femenina; edad25–45, naturalidad y calidad pendientes de escucha. Dataset CC-BY3.0; ver MODEL_CARD.','language':'es','voice_type':'preset','preset_engine':'piper','preset_voice_id':'es_ES-sharvard-medium:F','default_engine':'piper'})
 result['female_profile_id']=female['id'];(OUT/'result.json').write_text(json.dumps(result)+'\n')
 text='Hola, bienvenidos a nuestro canal. Hoy vamos a explicar cómo funciona esta tecnología y por qué puede ayudarnos a trabajar mejor.'
 for key,pid,engine in [('female_es',female['id'],'piper'),('male_es','916ce396-1b15-4621-b63c-5eaf49f03b74','kokoro'),('alex','250f2938-c396-47e8-8b75-0bf9179d0252','kokoro')]:
  t=time.monotonic();g=api('/generate',{'profile_id':pid,'engine':engine,'language':'es','text':text,'seed':42,'personality':False});ident=g['id'];(OUT/(key+'-request.json')).write_text(json.dumps({'id':ident,'profile_id':pid})+'\n')
  while time.monotonic()-t<120:
   check();g=api('/history/'+ident)
   if g['status'] in ['completed','failed','cancelled']:break
   time.sleep(.5)
  assert g['status']=='completed',g.get('error')
  seconds=time.monotonic()-t
  with urllib.request.urlopen('http://192.168.1.127:17493/audio/'+ident,timeout=15) as r:audio=r.read()
  with wave.open(io.BytesIO(audio)) as w:
   rate=w.getframerate();duration=w.getnframes()/rate;signal=array.array('h',w.readframes(w.getnframes()));assert duration>2 and max(abs(x) for x in signal)>100
  loaded=[m['model_name'] for m in api('/models/status')['models'] if m['loaded']];assert loaded==(['piper-es-es'] if engine=='piper' else ['kokoro'])
  sample={'identity':key,'profile_id':pid,'generation_id':ident,'audio_url':'http://192.168.1.127:17493/audio/'+ident,'audio_seconds':duration,'generation_seconds_observed':seconds,'sample_rate':rate,'sha256':hashlib.sha256(audio).hexdigest(),'loaded_models':loaded};result['samples'].append(sample);(OUT/(key+'.wav')).write_bytes(audio)
 # Actual owner recording guard: no load/download or fictitious personal profile.
 try:api('/models/load',{'model_name':'qwen-tts-0.6B'});raise AssertionError('Base unexpectedly loaded without owner references')
 except urllib.error.HTTPError as e:
  assert e.code==500;result['base_preflight_error']=e.read().decode();assert 'Real owner reference' in result['base_preflight_error']
 assert all(m['model_name']=='kokoro' for m in api('/models/status')['models'] if m['loaded']), 'No Base may load before real owner references'
 api('/models/load',{'model_name':'kokoro'})
 result.update({'result':'PASS','profiles':len(api('/profiles')),'preexisting_profiles_preserved':len(before),'peak_ct_sampled_bytes':peak,'personal_guard':'BASE_NOT_LOADED_NO_OWNER_PROFILE_OR_WEIGHTS','elapsed':time.monotonic()-started})
 (OUT/'technical-pass').write_text('PASS; auditory acceptance pending\n')
except BaseException as e:result.update({'result':'FAIL','error':str(e)});raise
finally:(OUT/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
