"""PVE supervisor for exactly one FP32 worker, killable independently of Voicebox."""
from pathlib import Path
import subprocess,json,time,urllib.request,datetime
CG=Path('/sys/fs/cgroup/lxc/627');name='qwen-d075-b-fp32-03';start=time.monotonic();worker=None;result={'measurements':[],'classification':None,'timeout_max_seconds':300,'soft_external_deadline':295,'guard_swap_growth_mib':32,'guard_swap_absolute_mib':480}
def ct(*a,timeout=12):return subprocess.check_output(['pct','exec','627','--',*a],text=True,timeout=timeout)
def kv(p):return dict((x.split()[0],int(x.split()[1])) for x in p.read_text().splitlines())
def full(s):return float(s.splitlines()[-1].split()[1].split('=')[1])
def health():return json.load(urllib.request.urlopen('http://192.168.1.127:17493/health',timeout=5))
def sample():
 m={'elapsed':time.monotonic()-start,'ct_current':int((CG/'memory.current').read_text()),'ct_swap':int((CG/'memory.swap.current').read_text()),'ct_memory_stat':{k:v for k,v in kv(CG/'memory.stat').items() if k in ['anon','file','kernel','active_file','inactive_file','file_dirty']},'ct_cpu':kv(CG/'cpu.stat'),'ct_events':kv(CG/'memory.events'),'ct_pressure':(CG/'memory.pressure').read_text(),'host_pressure':Path('/proc/pressure/memory').read_text(),'host_available':int(next(x.split()[1] for x in Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')))*1024,'vmstat':{k:v for k,v in kv(Path('/proc/vmstat')).items() if k in ['pswpin','pswpout','oom_kill']}}
 if worker and worker.exists():
  m['worker_current']=int((worker/'memory.current').read_text());m['worker_swap']=int((worker/'memory.swap.current').read_text());m['worker_memory_stat']={k:v for k,v in kv(worker/'memory.stat').items() if k in ['anon','file','kernel']};m['worker_cpu']=kv(worker/'cpu.stat');m['worker_events']=kv(worker/'memory.events');m['worker_pressure']=(worker/'memory.pressure').read_text();rss=0
  for pid in (worker/'cgroup.procs').read_text().split():
   try:
    info=Path('/proc/'+pid+'/status').read_text();rss+=int(info.split('VmRSS:')[1].split()[0])*1024 if 'VmRSS:' in info else 0
   except OSError:pass
  m['rss_bytes']=rss
 return m
base=sample();result['baseline']=base;host_pressure_since=None;ct_pressure_since=None
try:
 assert base['host_available']>6*2**30 and full(base['host_pressure'])<2,'preflight pressure'
 assert base['ct_swap']<464*2**20,'Preflight swap headroom below16MiB'
 assert health()['status']=='healthy' and not health()['model_loaded']
 assert name not in ct('docker','ps','-a','--format','{{.Names}}').splitlines(),'Unique attempt already exists'
 result['at_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
 ct('docker','run','-d','--name',name,'--network','none','--no-healthcheck','--cpus','3','--memory','6g','--memory-swap','6g','--pids-limit','96','--user','999:999','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--tmpfs','/tmp:rw,size=128m','-e','NUMBA_CACHE_DIR=/tmp/numba','-e','HF_HUB_OFFLINE=1','-e','HF_HOME=/cache','-e','OMP_NUM_THREADS=2','-e','MKL_NUM_THREADS=2','-e','TOKENIZERS_PARALLELISM=false','-e','PYTHONDONTWRITEBYTECODE=1','-v','/srv/voicebox/huggingface:/cache:ro','-v','/srv/voicebox/pilot-d072/private:/private:ro','-v','/srv/voicebox/pilot-d075-b/infer-gradual.py:/infer.py:ro','-v','/srv/voicebox/pilot-d075-b/job03:/job:rw','--workdir','/job','--entrypoint','python','local/voicebox:8af7efe62fab-personal-d069','/infer.py')
 cid=ct('docker','inspect','-f','{{.Id}}',name).strip();worker=next(CG.rglob('docker-'+cid+'.scope'));state=None
 while time.monotonic()-start<295:
  m=sample();result['measurements'].append(m)
  if m['ct_current']>=6.6*2**30 or m.get('worker_current',0)>=5.75*2**30 or m.get('rss_bytes',0)>=5.6*2**30:raise RuntimeError('RESOURCE_MEMORY_GUARD')
  if m['ct_swap']>=480*2**20:raise RuntimeError('RESOURCE_SWAP_ABSOLUTE_480_MIB')
  if m['ct_swap']-base['ct_swap']>=32*2**20:raise RuntimeError('RESOURCE_SWAP_GROWTH_32_MIB')
  if m['host_available']<2*2**30:raise RuntimeError('RESOURCE_HOST_AVAILABLE')
  if any(m['ct_events'][k]>base['ct_events'][k] for k in ['oom','oom_kill']) or any(m.get('worker_events',{}).get(k,0)>0 for k in ['oom','oom_kill']):raise RuntimeError('RESOURCE_OOM_GUARD')
  if full(m['host_pressure'])>=2:host_pressure_since=host_pressure_since or time.monotonic()
  else:host_pressure_since=None
  if full(m['ct_pressure'])>=1:ct_pressure_since=ct_pressure_since or time.monotonic()
  else:ct_pressure_since=None
  if (host_pressure_since and time.monotonic()-host_pressure_since>=10) or (ct_pressure_since and time.monotonic()-ct_pressure_since>=5):raise RuntimeError('RESOURCE_PSI_GUARD')
  state=json.loads(ct('docker','inspect','-f','{{json .State}}',name))
  if not state['Running']:
   result['container_state']=state
   try:result['job']=json.loads(ct('cat','/srv/voicebox/pilot-d075-b/job03/result.json'))
   except Exception:pass
   result['classification']=result.get('job',{}).get('classification','F');break
  if int(m['elapsed'])%4==0 and health().get('model_loaded'):raise RuntimeError('PRODUCTIVE_ENGINE_STARTED')
  time.sleep(.4)
 else:raise TimeoutError('EXTERNAL_295S_DEADLINE')
except BaseException as e:
 result['reason']=str(e);result['classification']='E' if str(e).startswith('RESOURCE') else 'F'
finally:
 if name in ct('docker','ps','-a','--format','{{.Names}}').splitlines():
  t=time.monotonic()
  if result.get('reason') and worker and worker.exists():
   assert worker.is_relative_to(CG) and worker.name=='docker-'+cid+'.scope'
   try:(worker/'cgroup.kill').write_text('1');result['worker_cgroup_kill']=True
   except OSError:result['worker_cgroup_kill']=False
  ct('docker','stop','--time','1',name,timeout=8);result['stop_seconds']=time.monotonic()-t
  state=json.loads(ct('docker','inspect','-f','{{json .State}}',name));result['container_state']=state;assert state['Pid']==0 and not state['Running']
 result['elapsed_total']=time.monotonic()-start;print(json.dumps(result),flush=True)
