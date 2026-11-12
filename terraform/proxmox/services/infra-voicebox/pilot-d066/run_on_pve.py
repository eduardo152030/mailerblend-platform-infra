#!/usr/bin/env python3
"""D066 supervisor on PVE: CT627 only, guarded isolated API; always restore original service."""
import array,concurrent.futures,datetime,hashlib,io,json,os,resource,signal,socket,subprocess,time,traceback,urllib.request,wave
from pathlib import Path
CT='627';NAME='voicebox-qwen-pilot-d066';BASE=Path(os.environ.get('D066_RESULT_DIR','/root/voicebox-d066/run'));CG=Path('/sys/fs/cgroup/lxc/627');COMPOSE='/opt/voicebox/pilot-d066/compose.yml'
assert socket.gethostname()=='pve' and os.geteuid()==0
BASE.mkdir(mode=0o700,parents=True,exist_ok=True);LOG=BASE/'samples.jsonl';pool=concurrent.futures.ThreadPoolExecutor(2)
result={'decision':'D066','started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'result':'IN PROGRESS','stages':{},'threshold_bytes':int(3.5*2**30),'threshold_swap_growth_bytes':64*2**20}
PROC=None;candidate_pid=None;phase='baseline';last_log=0;count=0;maxima={};baseline_swap=int((CG/'memory.swap.current').read_text());baseline_oom=dict(l.split() for l in (CG/'memory.events').read_text().splitlines());external_future=None;external_started=0;external_checks=0;initial_cpu=dict(l.split() for l in (CG/'cpu.stat').read_text().splitlines());start=time.monotonic()
def ct(args,timeout=30):return subprocess.check_output(['pct','exec',CT,'--']+args,timeout=timeout)
def api(path,data=None,pilot=True,timeout=30):
 code='''import urllib.request,urllib.error,json,sys
try:
 req=urllib.request.Request(URL,data=BODY,headers={'Content-Type':'application/json'})
 with urllib.request.urlopen(req,timeout=TIMEOUT) as r:
  b=r.read()
  print(json.dumps({'ok':True,'data':json.loads(b)}))
except urllib.error.HTTPError as e:print(json.dumps({'ok':False,'status':e.code,'error':e.read().decode()[:2000]}))
'''.replace('URL',repr(('http://127.0.0.1:17494' if pilot else 'http://192.168.1.127:17493')+path)).replace('BODY',repr(None if data is None else json.dumps(data).encode())).replace('TIMEOUT',str(timeout))
 d=json.loads(ct(['python3','-c',code],timeout+15))
 if not d['ok']:raise RuntimeError('API '+str(d.get('status'))+': '+d.get('error',''))
 return d['data']
def inspect(name):return json.loads(ct(['docker','inspect',name]))[0]
def rss(pid):
 if not pid:return {}
 try:
  d={}
  for l in (PROC/str(pid)/'status').read_text().splitlines():
   k,_,v=l.partition(':')
   if k in ['VmRSS','VmHWM','RssAnon','RssFile','VmSwap']:d[k+'_bytes']=int(v.split()[0])*1024
  return d
 except FileNotFoundError:return {}
def external_check():
 with urllib.request.urlopen('http://192.168.1.110:9090/api/v1/targets',timeout=4) as r:d=json.load(r)
 others=[t for t in d['data']['activeTargets'] if t['labels'].get('service')!='infra-voicebox']
 assert all(t['health']=='up' for t in others),'Other monitoring target not UP'
 assert not any(m['loaded'] for m in api('/models/status',pilot=False,timeout=3)['models']),'Single-model policy: original service loaded a model'
 return len(others)
def snapshot(enforce=True):
 global last_log,count,external_future,external_started,external_checks
 now=time.monotonic();events=dict(l.split() for l in (CG/'memory.events').read_text().splitlines());st=dict(l.split() for l in (CG/'memory.stat').read_text().splitlines());current=int((CG/'memory.current').read_text());swap=int((CG/'memory.swap.current').read_text());d={'elapsed_seconds':round(now-start,3),'phase':phase,'ct_memory_current_bytes':current,'ct_memory_peak_bytes':int((CG/'memory.peak').read_text()),'ct_inactive_file_bytes':int(st.get('inactive_file',0)),'ct_working_set_bytes':current-int(st.get('inactive_file',0)),'ct_swap_bytes':swap,'memory_events':events,**rss(candidate_pid)}
 for k,v in d.items():
  if isinstance(v,(int,float)) and k!='elapsed_seconds':maxima[k]=max(maxima.get(k,0),v)
 count+=1
 with LOG.open('a') as f:f.write(json.dumps(d)+'\n')
 if now-last_log>=10:print(json.dumps(d),flush=True);last_log=now
 if enforce:
  if external_future is not None and external_future.done():
   external_future.result();external_checks+=1;external_future=None
  if external_future is None and now-external_started>=10:
   external_future=pool.submit(external_check);external_started=now
  if external_future is not None and now-external_started>12:raise RuntimeError('External health check stalled')
  if current>result['threshold_bytes']:raise RuntimeError('HALT: CT memory.current exceeds3.5GiB safety threshold')
  if swap-baseline_swap>result['threshold_swap_growth_bytes']:raise RuntimeError('HALT: swap grew beyond64MiB')
  if any(int(events[k])>int(baseline_oom[k]) for k in ['oom','oom_kill','oom_group_kill']):raise RuntimeError('HALT: OOM event; trial failed')
 return d
def guarded(fn,timeout):
 f=pool.submit(fn);deadline=time.monotonic()+timeout
 while not f.done():
  snapshot();
  if time.monotonic()>deadline:raise RuntimeError('HALT: '+phase+' timeout '+str(timeout)+'s')
  time.sleep(.2)
 snapshot();return f.result()
def set_phase(s):
 global phase
 phase=s;print('PHASE '+s,flush=True)
def get_audio(ident):return ct(['python3','-c','import urllib.request,sys;sys.stdout.buffer.write(urllib.request.urlopen("http://127.0.0.1:17494/audio/'+ident+'",timeout=20).read())'])
def generate(label,text,profile,timeout):
 set_phase(label);t=time.monotonic();before=dict(l.split() for l in (CG/'cpu.stat').read_text().splitlines());g=guarded(lambda:api('/generate',{'profile_id':profile,'text':text,'language':'es','engine':'qwen_custom_voice','model_size':'0.6B','seed':42,'max_chunk_chars':200,'crossfade_ms':50,'personality':False,'normalize':True,'effects_chain':[]}),20);ident=g['id'];(BASE/(label+'-request.json')).write_text(json.dumps({'profile_id':profile,'generation_id':ident,'text':text},indent=2)+'\n');deadline=t+timeout
 while True:
  g=guarded(lambda:api('/history/'+ident),15)
  if g['status'] in ['completed','failed','cancelled']:break
  if time.monotonic()>deadline:raise RuntimeError('HALT: generation deadline '+label)
  for _ in range(5):snapshot();time.sleep(.2)
 if g['status']!='completed':raise RuntimeError('Generation failed: '+str(g.get('error')))
 elapsed=time.monotonic()-t;audio=guarded(lambda:get_audio(ident),20)
 with wave.open(io.BytesIO(audio)) as w:
  duration=w.getnframes()/w.getframerate();rate=w.getframerate();width=w.getsampwidth();ch=w.getnchannels();pcm=array.array('h',w.readframes(w.getnframes()))
 assert width==2 and ch==1 and duration>1 and max(abs(x) for x in pcm)>100,'Audio invalid/silent'
 (BASE/(label+'.wav')).write_bytes(audio);after=dict(l.split() for l in (CG/'cpu.stat').read_text().splitlines());out={'result':'PASS','profile_id':profile,'generation_id':ident,'generation_seconds':elapsed,'audio_seconds':duration,'sample_rate':rate,'format':'WAV PCM16 mono','sha256':hashlib.sha256(audio).hexdigest(),'text_words':len(text.split()),'rtf':elapsed/duration,'ct_cpu_seconds':(int(after['usage_usec'])-int(before['usage_usec']))/1e6};result['stages'][label]=out;return out

def restore():
 set_phase('restore_original')
 subprocess.run(['pct','exec',CT,'--','docker','stop','--time','5',NAME],timeout=20,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 original=inspect('voicebox');assert original['Image']=='sha256:7f2e6f7e6a2d09c77ebd35424a7641249e51b8ff0374bc9c4acb1f7393cfcd4c'
 if not original['State']['Running']:ct(['docker','start','voicebox'])
 api('/models/load',{'model_name':'kokoro'},pilot=False,timeout=90)
 d=api('/models/status',pilot=False);assert any(m['model_name']=='kokoro' and m['loaded'] for m in d['models']);assert not any(m['loaded'] and m['model_name']!='kokoro' for m in d['models'])
 result['original_restored']={'image':original['Image'],'kokoro_loaded':True,'pilot_stopped':True,'profiles_original_data_untouched':True}

def handle_signal(signum,frame):raise RuntimeError('Supervisor signal '+str(signum))
for sig in [signal.SIGTERM,signal.SIGINT,signal.SIGHUP]:signal.signal(sig,handle_signal)
try:
 initpid=subprocess.check_output(['lxc-info','-n',CT,'-pH'],text=True).strip();PROC=Path('/proc')/initpid/'root/proc'
 assert int((CG/'memory.max').read_text())==4*2**30,'CT not exactly4GiB'
 if LOG.exists():raise RuntimeError('Existing log: do not overwrite pilot evidence')
 original=inspect('voicebox');result['original_image']=original['Image'];assert result['original_image']=='sha256:7f2e6f7e6a2d09c77ebd35424a7641249e51b8ff0374bc9c4acb1f7393cfcd4c'
 set_phase('original_ready')
 for i in range(45):
  try:
   if api('/health',pilot=False,timeout=2)['status']=='healthy':break
  except Exception:pass
  time.sleep(2)
 else:raise RuntimeError('Original API not ready before trial')
 set_phase('unload_kokoro');api('/models/kokoro/unload',{},pilot=False)
 models=api('/models/status',pilot=False);assert not any(m['loaded'] for m in models['models']),'Another model remains loaded'
 result['baseline_original_rss']=rss(original['State']['Pid']);snapshot()
 set_phase('candidate_start');ct(['docker','compose','-f',COMPOSE,'up','-d','--no-deps','qwen-pilot'],timeout=60)
 c=inspect(NAME);candidate_pid=c['State']['Pid'];assert rss(candidate_pid).get('VmRSS_bytes',0)>0,'Cannot sample candidate RSS';result['candidate_image']=c['Image'];assert c['Image']=='sha256:4de8a649d267fb9f4fa9d7049f264a1e6896718c7892f70706abb4a46d75430d';assert c['HostConfig']['MemorySwap']==c['HostConfig']['Memory']
 ready=False
 for i in range(30):
  snapshot()
  try:ready=api('/health',timeout=2)['status']=='healthy'
  except Exception:pass
  if ready:break
  time.sleep(1)
 assert ready,'Candidate API failed to start'
 set_phase('load');t=time.monotonic();guarded(lambda:api('/models/load',{'model_name':'qwen-custom-voice-0.6B'},timeout=240),240);result['stages']['load']={'result':'PASS','api_load_seconds':time.monotonic()-t}
 facts=json.loads(ct(['cat','/srv/voicebox/pilot-d066/data/d066-load-facts.json']));assert set(facts['main_parameters'])=={'torch.bfloat16'} and set(facts['codec_parameters'])=={'torch.bfloat16'} and facts['attention']=='sdpa';result['load_facts']=facts
 models=api('/models/status');assert [m['model_name'] for m in models['models'] if m['loaded']]==['qwen-custom-voice-0.6B'];assert not any(m['loaded'] for m in api('/models/status',pilot=False)['models'])
 profile=guarded(lambda:api('/profiles',{'name':'D066 PILOTO Ryan CustomVoice0.6B','description':'Isolated copy only; not auditory accepted','language':'es','voice_type':'preset','preset_engine':'qwen_custom_voice','preset_voice_id':'Ryan','default_engine':'qwen_custom_voice'}),15)
 short='Hola, esta es una prueba controlada de narración en español. Vamos a comprobar la estabilidad y la claridad de esta voz.'
 pilot=generate('short',short,profile['id'],120);assert pilot['audio_seconds']<30
 text=('Hoy vamos a explicar cómo funciona una tecnología que transforma texto en voz dentro de nuestra propia infraestructura. El objetivo es crear narraciones claras y útiles para acompañar vídeos, sin depender de una conexión permanente a servicios comerciales. Antes de comenzar, revisamos los recursos disponibles y conservamos una copia de seguridad. Después preparamos el contenido, elegimos una voz y comprobamos que cada frase se entienda con naturalidad. No basta con que el programa arranque: necesitamos escuchar un archivo real, medir su duración y conocer cuánto tiempo tarda en generarse. También observamos la memoria, el procesador y la estabilidad del sistema durante todo el trabajo. Si aparece un problema, detenemos la prueba y recuperamos la versión anterior. Esta forma de trabajar permite avanzar paso a paso, comparar resultados y tomar decisiones basadas en datos. La automatización puede ahorrar muchas tareas repetitivas, pero la revisión humana sigue siendo importante para valorar el acento, el ritmo y la calidad de una narración. Gracias por acompañarnos en esta demostración; seguiremos mejorando el proceso con pruebas reproducibles y resultados que cualquier persona del equipo pueda verificar.').split()
 n=max(100,min(len(text),round(60*len(short.split())/pilot['audio_seconds'])));long=' '.join(text[:n]).rstrip('.,;:')+'.';out=generate('narration',long,profile['id'],900);out['approximate_minute']=45<=out['audio_seconds']<=80
 result['result']='PASS' if out['approximate_minute'] else 'PARTIAL_DURATION';result['recommendation']='evaluate retain candidate' if out['approximate_minute'] else 'adjust duration'
except BaseException as e:
 result['result']='FAIL';result['failure_phase']=phase;result['error']=str(e);(BASE/'exception.private.txt').write_text(traceback.format_exc());print('FAIL '+str(e),flush=True)
finally:
 result['other_target_checks']=external_checks;result['samples']=count;result['maxima']=maxima;result['elapsed_seconds']=time.monotonic()-start;result['oom_events_final']=dict(l.split() for l in (CG/'memory.events').read_text().splitlines())
 try:restore()
 except Exception as e:result['recovery_error']=str(e);print('RECOVERY ERROR '+str(e),flush=True)
 (BASE/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True);pool.shutdown(wait=False,cancel_futures=True)
