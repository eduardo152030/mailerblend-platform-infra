#!/usr/bin/env python3
"""Isolated CT627-only Piper+Kokoro API test with guaranteed stable-service recovery."""
import argparse,array,hashlib,io,json,shlex,subprocess,time,urllib.request,wave
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];PRIVATE=Path.home()/'.local/share/mailerblend-recovery/voicebox-d068';SSH=['ssh','-o','UserKnownHostsFile='+str(Path.home()/'.ssh/known_hosts'),'-o','StrictHostKeyChecking=yes','-o','BatchMode=yes','pve']
parser=argparse.ArgumentParser();parser.add_argument('--attempt',default='02');parser.add_argument('--image',default='local/voicebox:8af7efe62fab-piper-d068');opts=parser.parse_args();assert opts.attempt.isdigit()
def ct(args,body=None):return subprocess.check_output(SSH+[shlex.join(['pct','exec','627','--']+args)],input=body,timeout=90,stderr=subprocess.PIPE)
def api(path,value=None,port=17495):
 address=('http://127.0.0.1:'+str(port) if port==17495 else 'http://192.168.1.127:17493')+path
 code="import urllib.request;print(urllib.request.urlopen(urllib.request.Request("+repr(address)+",data="+repr(None if value is None else json.dumps(value).encode())+",headers={'Content-Type':'application/json'}),timeout=30).read().decode())"
 return json.loads(ct(['python3','-c',code]))
assert not (PRIVATE/('piper-trial'+opts.attempt+'.json')).exists()
code="""from pathlib import Path
import shutil,subprocess
p=Path('/srv/voicebox/pilot-d068/piper-data@ATTEMPT@');assert not p.exists();shutil.copytree('/opt/voicebox/backups/d068-before/data',p);subprocess.run(['chown','-R','999:999',str(p)],check=True)
"""
code=code.replace('@ATTEMPT@',opts.attempt)
ct(['python3','-c',code])
name='voicebox-d068-piper-api-'+opts.attempt;result={'result':'IN_PROGRESS','samples':[]}
try:
 ct(['docker','run','-d','--name',name,'--label','voicebox.pilot=D068','--restart','no','--network','host','--cpus','2','--memory','1600m','--memory-swap','2000m','-e','HF_HUB_OFFLINE=1','-e','OMP_NUM_THREADS=2','-e','MKL_NUM_THREADS=2','-e','NUMBA_CACHE_DIR=/app/data/cache/numba','-v','/srv/voicebox/pilot-d068/piper-data'+opts.attempt+':/app/data','-v','/srv/voicebox/data/models/piper:/app/data/models/piper:ro','-v','/srv/voicebox/huggingface:/home/voicebox/.cache/huggingface:ro',opts.image,'uvicorn','backend.main:app','--host','127.0.0.1','--port','17495'])
 for i in range(45):
  try:
   if api('/health')['status']=='healthy':break
  except Exception:pass
  time.sleep(2)
 else:raise RuntimeError('Piper candidate API not ready')
 api('/models/kokoro/unload',{},17493);assert not any(m['loaded'] for m in api('/models/status',port=17493)['models'])
 presets=api('/profiles/presets/piper');assert presets['voices'][0]['voice_id']=='es_ES-sharvard-medium:F'
 profile=api('/profiles',{'name':'D068 female isolated Piper','description':'Spain source female, auditory acceptance pending','voice_type':'preset','language':'es','preset_engine':'piper','preset_voice_id':'es_ES-sharvard-medium:F','default_engine':'piper'})
 for engine,pid,text in [('piper',profile['id'],'Hola, bienvenidos a nuestro canal. Hoy vamos a explicar cómo funciona esta tecnología y por qué puede ayudarnos a trabajar mejor.'),('kokoro','250f2938-c396-47e8-8b75-0bf9179d0252','Hola, esta es una comprobación de la voz Alex después de probar la nueva candidata femenina.')]:
  t=time.monotonic();g=api('/generate',{'profile_id':pid,'engine':engine,'language':'es','seed':42,'text':text,'personality':False});ident=g['id'];(PRIVATE/(engine+'-trial'+opts.attempt+'-request.json')).write_text(json.dumps({'id':ident,'profile_id':pid})+'\n')
  for _ in range(120):
   g=api('/history/'+ident)
   if g['status'] in ['completed','failed','cancelled']:break
   time.sleep(1)
  assert g['status']=='completed',g.get('error')
  elapsed=time.monotonic()-t
  code="import urllib.request,sys;sys.stdout.buffer.write(urllib.request.urlopen('http://127.0.0.1:17495/audio/"+ident+"').read())";audio=ct(['python3','-c',code]);(PRIVATE/(engine+'-trial'+opts.attempt+'.wav')).write_bytes(audio)
  with wave.open(io.BytesIO(audio)) as w:duration=w.getnframes()/w.getframerate();rate=w.getframerate();signal=array.array('h',w.readframes(w.getnframes()));assert duration>2 and max(abs(x) for x in signal)>100
  loaded=[m['model_name'] for m in api('/models/status')['models'] if m['loaded']];assert loaded==(['piper-es-es'] if engine=='piper' else ['kokoro']),loaded
  result['samples'].append({'engine':engine,'generation_id':ident,'profile_id':pid,'audio_seconds':duration,'generation_seconds_observed':elapsed,'sample_rate':rate,'sha256':hashlib.sha256(audio).hexdigest(),'loaded_models':loaded})
 code="""import urllib.request,urllib.error,json
try:
 req=urllib.request.Request('http://127.0.0.1:17495/models/load',data=b'{"model_name":"qwen-tts-0.6B"}',headers={'Content-Type':'application/json'})
 urllib.request.urlopen(req,timeout=15);print(json.dumps({'status':200}))
except urllib.error.HTTPError as e:print(json.dumps({'status':e.code,'detail':e.read().decode()}))
"""
 guard=json.loads(ct(['python3','-c',code]));assert guard['status']==500 and 'Real owner reference' in guard['detail'],guard
 result['owner_guard']=guard
 c=json.loads(ct(['docker','inspect',name]))[0];assert not c['State']['OOMKilled'];result.update({'result':'PASS','image':c['Image'],'original_production_profiles_untouched':True})
except Exception as e:result.update({'result':'FAIL','error':str(e)});raise
finally:
 ct(['docker','stop','--time','10',name]);api('/models/load',{'model_name':'kokoro'},17493)
 result['stable_original_restored']=True;(PRIVATE/('piper-trial'+opts.attempt+'.json')).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
