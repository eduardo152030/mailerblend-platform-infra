#!/usr/bin/env python3
"""Finite owner Base0.6B pilot on PVE; always restore stable image on failure."""
import json,time,subprocess,urllib.request,datetime,os,wave,io,hashlib
from pathlib import Path
OUT=Path('/root/voicebox-d069');OUT.mkdir(mode=0o700,exist_ok=True)
RESULT=OUT/'pilot.json';assert not RESULT.exists(),'No silent retries'
CG=Path('/sys/fs/cgroup/lxc/627');OWNER='1fd00418-2a79-4178-883f-af6c3f5e07ee'
def api(path,data=None):
 req=urllib.request.Request('http://192.168.1.127:17493'+path,data=None if data is None else json.dumps(data).encode(),headers={'Content-Type':'application/json'})
 with urllib.request.urlopen(req,timeout=8) as r:return json.load(r)
def run(*cmd):return subprocess.run(['pct','exec','627','--',*cmd],check=True,capture_output=True,timeout=100)
def ready():
 for _ in range(45):
  try:
   if api('/health')['status']=='healthy':return
  except Exception:pass
  time.sleep(1)
 raise RuntimeError('Service not healthy')
def observe():
 d={n:(CG/n).read_text() for n in ['memory.current','memory.swap.current','memory.events','cpu.stat']}
 d['host_pressure']=Path('/proc/pressure/memory').read_text();d['host_available']=int(next(x.split()[1] for x in Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')))*1024
 c=json.loads(run('docker','inspect','voicebox').stdout)[0];init=subprocess.check_output(['lxc-info','-n','627','-pH'],text=True).strip();p=Path('/proc')/init/'root/proc'/str(c['State']['Pid'])
 st=(p/'stat').read_text().split(') ',1)[1].split();d['main_cpu_usec']=(int(st[11])+int(st[12]))*1000000//os.sysconf('SC_CLK_TCK')
 d['process_memory']={x.split(':')[0]:x.split(':',1)[1].strip() for x in (p/'status').read_text().splitlines() if x.startswith(('VmRSS:','VmHWM:','VmSwap:'))}
 return d
result={'status':'IN_PROGRESS','observed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'measurements':[]};start=time.monotonic();candidate=False
try:
 profiles=api('/profiles');assert len(profiles)==1 and profiles[0]['id']==OWNER
 assert api('/profiles/'+OWNER+'/samples')[0]['id']=='8840f5e1-990b-463e-b94e-e72beef61917'
 candidate=True;run('docker','compose','-f','/opt/voicebox/compose.yml','-f','/opt/voicebox/pilot-d069/compose-pilot.yml','up','-d','--no-deps','--no-build','voicebox');ready()
 for m in api('/models/status')['models']:
  if m['loaded']:api('/models/'+m['model_name']+'/unload',{})
 base=observe();swap=int(base['memory.swap.current']);events=dict(x.split() for x in base['memory.events'].splitlines());cpu=base['main_cpu_usec'];last=time.monotonic()
 assert base['host_available']>1.5*2**30 and float(base['host_pressure'].splitlines()[1].split()[1].split('=')[1])<2,'Unsafe host preflight'
 t=time.monotonic();g=api('/generate',{'profile_id':OWNER,'engine':'qwen','model_size':'0.6B','language':'es','text':'Ningún trader opera sin perder, ni siquiera los mejores. La diferencia no está en evitar las pérdidas, sino en cómo las gestionas.','seed':42,'personality':False,'max_chunk_chars':200});ident=g['id'];result['generation_id']=ident
 while time.monotonic()-t<180:
  m=observe();m['elapsed_seconds']=time.monotonic()-t;result['measurements'].append(m);RESULT.write_text(json.dumps(result,indent=2));RESULT.chmod(0o600)
  if m['main_cpu_usec']-cpu>1000000:cpu=m['main_cpu_usec'];last=time.monotonic()
  ev=dict(x.split() for x in m['memory.events'].splitlines());psi=float(m['host_pressure'].splitlines()[1].split()[1].split('=')[1])
  if int(m['memory.current'])>=6.5*2**30:raise RuntimeError('SAFETY_STOP_CGROUP_6.5GiB')
  if int(m['memory.swap.current'])-swap>64*2**20:raise RuntimeError('SAFETY_STOP_SWAP_64MiB')
  if any(int(ev[k])>int(events[k]) for k in ['oom','oom_kill','oom_group_kill']):raise RuntimeError('SAFETY_STOP_OOM')
  if m['host_available']<1.5*2**30 or psi>=2:raise RuntimeError('SAFETY_STOP_HOST_PRESSURE')
  if time.monotonic()-last>45:raise RuntimeError('SAFETY_STOP_NO_CPU_PROGRESS_45s')
  g=api('/history/'+ident)
  if g['status'] in ['failed','cancelled']:raise RuntimeError('GENERATION_FAILED: '+str(g.get('error')))
  if g['status']=='completed':break
  time.sleep(2)
 else:raise RuntimeError('TIMEOUT_180s')
 with urllib.request.urlopen('http://192.168.1.127:17493/audio/'+ident,timeout=10) as r:raw=r.read()
 with wave.open(io.BytesIO(raw)) as w:assert w.getnchannels()==1 and w.getsampwidth()==2 and w.getnframes()>0;seconds=w.getnframes()/w.getframerate()
 f=OUT/'personal.wav';f.write_bytes(raw);f.chmod(0o600)
 result.update({'status':'TECHNICAL_AUDIO_PASS_PENDING_OWNER_LISTENING','audio_seconds':seconds,'generation_seconds':time.monotonic()-t,'sha256':hashlib.sha256(raw).hexdigest(),'audio_url':'http://192.168.1.127:17493/audio/'+ident})
except BaseException as e:result.update({'status':'FAIL','reason':str(e)})
finally:
 if candidate:
  try:
   log=run('docker','logs','voicebox');result['stages']=[x for x in (log.stdout+log.stderr).decode(errors='replace').splitlines() if 'D069 stage=' in x]
  except Exception as e:result['log_capture_error']=type(e).__name__
  # No DB rollback: preserve owner references and the recorded generation ID.
  if result['status']=='FAIL':
   try:
    run('docker','compose','-f','/opt/voicebox/compose.yml','up','-d','--no-deps','--no-build','voicebox');ready();api('/models/load',{'model_name':'kokoro'});result['rollback']='PASS_ORIGINAL_IMAGE_AND_HEALTH'
   except BaseException as e:result['rollback']='FAILED: '+str(e)
 result['elapsed_seconds']=time.monotonic()-start;RESULT.write_text(json.dumps(result,indent=2));RESULT.chmod(0o600)
 print(json.dumps({k:v for k,v in result.items() if k!='measurements'}),flush=True)
