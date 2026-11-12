#!/usr/bin/env python3
"""PVE-side D068 direct-library diagnosis; guarded, finite, one resident TTS model."""
import datetime,json,os,shlex,signal,socket,subprocess,time,urllib.request,traceback
from pathlib import Path
assert socket.gethostname()=='pve' and os.geteuid()==0
ATTEMPT=os.environ.get('D068_ATTEMPT','02');assert ATTEMPT.isdigit()
BASE=Path('/root/voicebox-d068/run'+ATTEMPT);BASE.mkdir(mode=0o700,parents=True,exist_ok=False)
CG=Path('/sys/fs/cgroup/lxc/627');INIT=subprocess.check_output(['lxc-info','-n','627','-pH'],text=True).strip();PROC=Path('/proc')/INIT/'root/proc';start=time.monotonic();last_health=0;active=None;safety=False
result={'decision':'D068','started_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'result':'IN PROGRESS','trials':[]};maxima={};baseline_swap=int((CG/'memory.swap.current').read_text());baseline_oom={k:int(v) for k,v in (x.split() for x in (CG/'memory.events').read_text().splitlines())}
def ct(args,body=None,timeout=30):return subprocess.check_output(['pct','exec','627','--']+args,input=body,timeout=timeout)
def api(path,data=None):
 code="import urllib.request,json;req=urllib.request.Request("+repr('http://192.168.1.127:17493'+path)+",data="+repr(None if data is None else json.dumps(data).encode())+",headers={'Content-Type':'application/json'});print(urllib.request.urlopen(req,timeout=6).read().decode())"
 return json.loads(ct(['python3','-c',code],timeout=12))
def sample(pid=0):
 global last_health,safety
 now=time.monotonic();cur=int((CG/'memory.current').read_text());swap=int((CG/'memory.swap.current').read_text());events={k:int(v) for k,v in (x.split() for x in (CG/'memory.events').read_text().splitlines())};mem={k:int(v.split()[0])*1024 for k,v in (x.split(':',1) for x in Path('/proc/meminfo').read_text().splitlines()) if k=='MemAvailable'}
 row={'elapsed':now-start,'trial':active,'current':cur,'peak':int((CG/'memory.peak').read_text()),'swap':swap,'events':events,'cpu':dict(x.split() for x in (CG/'cpu.stat').read_text().splitlines()),'host_available':mem['MemAvailable'],'host_pressure':Path('/proc/pressure/memory').read_text()}
 if pid:
  try:
   for line in (PROC/str(pid)/'status').read_text().splitlines():
    key,_,value=line.partition(':')
    if key in ['VmRSS','VmHWM','VmSwap']:row[key]=int(value.split()[0])*1024
  except FileNotFoundError:pass
 for key in ['current','peak','swap','VmRSS','VmHWM','VmSwap']:maxima[key]=max(maxima.get(key,0),row.get(key,0))
 with (BASE/'samples.jsonl').open('a') as f:f.write(json.dumps(row)+'\n')
 pressure={x.split()[0]:float(x.split()[1].split('=')[1]) for x in row['host_pressure'].splitlines()}
 if cur>=int(6.5*2**30) or swap-baseline_swap>64*2**20 or mem['MemAvailable']<int(1.5*2**30) or pressure['full']>=2 or any(events[k]>baseline_oom[k] for k in ['oom','oom_kill','oom_group_kill']):
  safety=True;raise RuntimeError('SAFETY: memory/pressure/swap/OOM threshold')
 if now-last_health>=10:
  with urllib.request.urlopen('http://192.168.1.110:9090/api/v1/targets',timeout=5) as r:d=json.load(r)
  assert all(t['health']=='up' for t in d['data']['activeTargets'] if t['labels'].get('service')!='infra-voicebox'),'External target down'
  assert api('/health')['status']=='healthy'
  assert not any(m['loaded'] for m in api('/models/status')['models']),'Single resident model policy'
  last_health=now
 return row

def run(label,dtype,tokens,text,speaker='Ryan',wall=180,attention='sdpa'):
 global active
 active=label;directory='/srv/voicebox/pilot-d068/'+ATTEMPT+'-'+label;name='voicebox-d068-'+ATTEMPT+'-'+label
 ct(['install','-d','-o','1000','-g','1000','-m','700',directory]);cmd=['docker','run','-d','--name',name,'--label','voicebox.pilot=D068','--restart','no','--no-healthcheck','--network','none','--entrypoint','python','--user','1000:1000','--cpus','2','--memory','6200m','--memory-swap','6200m','-e','NUMBA_CACHE_DIR=/diag/numba','-e','HF_HOME=/models','-e','OMP_NUM_THREADS=2','-e','MKL_NUM_THREADS=2','-e','HF_HUB_OFFLINE=1','-v','/opt/voicebox/pilot-d068/probe.py:/probe.py:ro','-v',directory+':/diag','-v','/srv/voicebox/pilot-d066/huggingface:/models:ro','local/voicebox:8af7efe62fab-bf16-sdpa-d066','-u','/probe.py','--dtype',dtype,'--attention',attention,'--tokens',str(tokens),'--text',text,'--speaker',speaker,'--codec-dtype','float32']
 ct(cmd);c=json.loads(ct(['docker','inspect',name]))[0];pid=c['State']['Pid']
 progress=Path('/proc')/INIT/'root'/directory.lstrip('/')/'progress.json';factsdir=progress.parent;t=time.monotonic();last_progress=t;last_marker=None
 try:
  while True:
   sample(pid)
   if progress.exists():
    try:
     event=json.loads(progress.read_text());marker=(event['elapsed'],event['stage'])
     if marker!=last_marker:last_progress=time.monotonic();last_marker=marker
    except json.JSONDecodeError:pass
   if (factsdir/'result.json').exists():
    data=json.loads((factsdir/'result.json').read_text());data.update({'label':label,'wall_seconds':time.monotonic()-t});result['trials'].append(data);return data
   if time.monotonic()-last_progress>45:raise RuntimeError('NO_PROGRESS45s '+label)
   if time.monotonic()-t>wall:raise RuntimeError('BOUNDED_DIAGNOSTIC_WALL '+label)
   if (factsdir/'exception.private.txt').exists():raise RuntimeError('Worker exception '+label)
   if time.monotonic()-t>5 and not progress.exists():
    state=json.loads(ct(['docker','inspect',name]))[0]['State']
    if not state['Running']:raise RuntimeError('Worker exited before model load: '+str(state['ExitCode']))
   time.sleep(.2)
 finally:
  ct(['docker','stop','--time','5',name],timeout=20)
  assert not json.loads(ct(['docker','inspect',name]))[0]['State']['Running']
  result['peak_after_stop']=int((CG/'memory.peak').read_text())

def stop(signum,frame):raise RuntimeError('Supervisor signal'+str(signum))
for sig in [signal.SIGTERM,signal.SIGINT,signal.SIGHUP]:signal.signal(sig,stop)
try:
 assert int((CG/'memory.max').read_text())==7*2**30
 for _ in range(50):
  try:
   if api('/health')['status']=='healthy':break
  except Exception:pass
  time.sleep(2)
 else:raise RuntimeError('Stable API not ready')
 api('/models/kokoro/unload',{});assert not any(m['loaded'] for m in api('/models/status')['models'])
 minimum='Hola, soy una voz generada mediante inteligencia artificial.'
 # Diagnostic caps are not an accepted synthesis test: compare identical16-frame workloads.
 mixed=run('diagnostic-mixed','bfloat16',16,minimum,wall=120)
 chosen='bfloat16'
 result['chosen_dtype']=chosen
 a=run('minimum',chosen,192,minimum,wall=180);assert a['result']=='PASS','Minimum did not terminate before token cap'
 btext='Hoy vamos a descubrir cómo funciona una tecnología que transforma texto en voz. Primero preparamos el contenido y elegimos una voz clara. Después revisamos la pronunciación y el ritmo de cada frase. El objetivo es crear narraciones naturales para vídeos educativos y explicativos, con resultados que podamos escuchar, comparar y mejorar paso a paso.'
 b=run('short',chosen,512,btext,wall=480);assert b['result']=='PASS' and 15<=b['audio_seconds']<=35,'Short result/duration not accepted'
 ctext='Hoy vamos a explicar cómo funciona una tecnología que transforma texto en voz dentro de nuestra propia infraestructura. El objetivo es crear narraciones claras para acompañar vídeos educativos y explicativos. Antes de comenzar, revisamos los recursos disponibles y conservamos una copia de seguridad. Después preparamos el contenido, elegimos una voz y comprobamos que cada frase se entienda con naturalidad. No basta con que el programa arranque: necesitamos escuchar un archivo real y conocer cuánto tiempo tarda en generarse. También observamos la memoria, el procesador y la estabilidad del sistema durante todo el trabajo. Si aparece un problema, detenemos la prueba y recuperamos la versión anterior. Esta forma de trabajar permite avanzar paso a paso, comparar resultados y tomar decisiones basadas en datos. La revisión humana sigue siendo importante para valorar el acento y el ritmo de cada narración.'
 assert 120<=len(ctext.split())<=150
 c=run('minute',chosen,1024,ctext,wall=900);assert c['result']=='PASS' and 45<=c['audio_seconds']<=80,'Minute result/duration not accepted'
 female=run('female',chosen,192,minimum,speaker='Serena',wall=180);assert female['result']=='PASS'
 result['result']='PASS'
except BaseException as e:
 result.update({'result':'FAIL','failure_phase':active,'error':str(e)});(BASE/'exception.private.txt').write_text(traceback.format_exc())
finally:
 result['safety_failure']=safety;result['maxima']=maxima;result['elapsed_seconds']=time.monotonic()-start
 try:subprocess.run(['/bin/bash','/root/voicebox-d068/restore.sh'],check=True,timeout=180);result['original_restored']=True
 except Exception as e:result['recovery_error']=str(e)
 (BASE/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
