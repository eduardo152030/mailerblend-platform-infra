"""PVE supervisor: bounded CLI diagnostic, no production mutations."""
import subprocess,json,time,argparse,uuid
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--label',required=True);p.add_argument('--seconds',type=int,default=240);a=p.parse_args()
CG=Path('/sys/fs/cgroup/lxc/627');out=Path('/root/voicebox-d072')/a.label;out.mkdir(mode=0o700,parents=True,exist_ok=False)
def ct(*args,**kw):return subprocess.check_output(['pct','exec','627','--',*args],text=True,timeout=15,**kw)
def kv(path):return dict((x.split()[0],int(x.split()[1])) for x in path.read_text().splitlines())
def sample():
 av=int(next(x.split()[1] for x in Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')))*1024
 pressure=Path('/proc/pressure/memory').read_text();full=float(pressure.splitlines()[1].split()[1].split('=')[1])
 r={'elapsed':time.monotonic()-start,'ct_memory':int((CG/'memory.current').read_text()),'ct_swap':int((CG/'memory.swap.current').read_text()),'ct_events':kv(CG/'memory.events'),'ct_cpu':kv(CG/'cpu.stat'),'host_available':av,'host_full_avg10':full}
 if worker_cg and worker_cg.exists():
  r['worker_memory']=int((worker_cg/'memory.current').read_text());r['worker_swap']=int((worker_cg/'memory.swap.current').read_text());r['worker_events']=kv(worker_cg/'memory.events');r['worker_cpu']=kv(worker_cg/'cpu.stat')
  r['rss_bytes']=sum(int(Path(f'/proc/{pid}/status').read_text().split('VmRSS:')[1].split()[0])*1024 for pid in (worker_cg/'cgroup.procs').read_text().split() if Path(f'/proc/{pid}/status').exists() and 'VmRSS:' in Path(f'/proc/{pid}/status').read_text())
 return r
start=time.monotonic();worker_cg=None;name='qwen-d072-'+a.label;result={'status':'IN_PROGRESS','measurements':[],'limits':{'worker_bytes':5*2**30,'ct_stop_bytes':6.25*2**30,'swap_growth_stop_bytes':64*2**20,'host_available_min_bytes':1.5*2**30,'host_psi_stop':'full avg10>=2% sustained 10s','timeout_seconds':a.seconds}}
baseline=sample();result['baseline']=baseline;pressure_since=None
try:
 assert baseline['host_available']>6*2**30,'Host insufficient available memory'
 assert baseline['host_full_avg10']<2,'Host pressure preflight'
 running=ct('docker','ps','--format','{{.Names}}').splitlines();assert not any(x.startswith('qwen-d072-') or x=='voicebox-openvoice' for x in running)
 ct('docker','run','-d','--name',name,'--network','none','--cpus','3','--memory','5g','--memory-swap','5g','--pids-limit','64','--user','999:999','--cap-drop','ALL','--security-opt','no-new-privileges','--read-only','--tmpfs','/tmp:rw,size=128m','-v','/srv/voicebox/huggingface:/cache:ro','-v','/srv/voicebox/pilot-d072/private:/private:ro','-v','/srv/voicebox/pilot-d072/infer.py:/infer.py:ro','-v',f'/srv/voicebox/pilot-d072/jobs/{a.label}:/job:rw','local/qwen-c:d072','python','/infer.py')
 pid=int(ct('docker','inspect','-f','{{.State.Pid}}',name));hostpid=None
 # Container's PID returned is in CT namespace; locate exact Docker cgroup beneath CT.
 cid=ct('docker','inspect','-f','{{.Id}}',name).strip()
 worker_cg=next(CG.rglob('docker-'+cid+'.scope'),None)
 if worker_cg is None:worker_cg=next((x for x in CG.rglob(cid) if x.is_dir()),None)
 assert worker_cg is not None,'Cannot monitor worker cgroup'
 while time.monotonic()-start<a.seconds:
  m=sample();result['measurements'].append(m);(out/'result.json').write_text(json.dumps(result))
  assert m['ct_memory']<6.25*2**30,'CT memory safety stop'
  assert m.get('worker_memory',0)<4.75*2**30,'Worker memory safety stop'
  assert m['ct_swap']-baseline['ct_swap']<64*2**20,'CT swap safety stop'
  assert m['host_available']>1.5*2**30,'Host available safety stop'
  assert all(m['ct_events'][k]==baseline['ct_events'][k] for k in ['oom','oom_kill']),'CT OOM'
  assert not any(m.get('worker_events',{}).get(k,0) for k in ['oom','oom_kill']),'Worker OOM'
  if m['host_full_avg10']>=2:pressure_since=pressure_since or time.monotonic()
  else:pressure_since=None
  assert pressure_since is None or time.monotonic()-pressure_since<10,'Host sustained PSI safety stop'
  state=json.loads(ct('docker','inspect','-f','{{json .State}}',name))
  if not state['Running']:
   result['container_state']=state
   r=json.loads(ct('cat',f'/srv/voicebox/pilot-d072/jobs/{a.label}/result.json'));result['job']=r
   assert state['ExitCode']==0 and r.get('frames',0)>0,'No valid WAV'
   result['status']='TECHNICAL_PASS';break
  time.sleep(1)
 else:raise TimeoutError('Generation deadline')
except BaseException as e:
 result.update(status='STOPPED',reason=str(e))
finally:
 if name in ct('docker','ps','-a','--format','{{.Names}}').splitlines():
  t=time.monotonic();ct('docker','stop','--time','2',name);result['stop_seconds']=time.monotonic()-t
 result['elapsed']=time.monotonic()-start;(out/'result.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='measurements'}),flush=True)
