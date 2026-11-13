"""One explicitly authorized Spanish inference; unchanged production guard functions."""
from pathlib import Path
import fcntl,hashlib,json,subprocess,sys,time,os,signal
sys.dont_write_bytecode=True
sys.path.insert(0,'/opt/voicebox-qwen-627')
import supervise as metrics
from engine_policy import preflight,stop_reason
CG=Path('/sys/fs/cgroup/lxc/627');BASE='/srv/voicebox/validation-d089';ENV='/srv/voicebox/chatterbox-d085'
IMAGE='sha256:bcc5c14f88064ffa76f813d788d183918b208deba45075d8118a2b07c60c248b'
REFERENCE='/srv/voicebox/data/profiles/1fd00418-2a79-4178-883f-af6c3f5e07ee/8840f5e1-990b-463e-b94e-e72beef61917.wav'
STOP=False

def ct(*args):return subprocess.check_output(['pct','exec','627','--',*args],text=True,timeout=30)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):
 tmp=p.with_suffix('.partial');tmp.write_text(json.dumps(d));tmp.chmod(0o600)
 with tmp.open('rb') as f:os.fsync(f.fileno())
 os.replace(tmp,p)
def main():
 assert sys.argv[1:]==['--execute-once']
 pid=subprocess.check_output(['lxc-info','-n','627','-pH'],text=True).strip();root=Path('/proc',pid,'root');base=root/BASE.lstrip('/');job=base/'job';src=base/'source';cid=None;cg=None
 result={'success':False,'measurements':[],'tts_attempts':0};baseline=None
 with open('/run/lock/qwen-d077-627.lock','a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  try:
   assert not (job/'started.json').exists(),'No retries'
   lockdata=json.loads((src/'source-lock.json').read_text())
   for n,h in lockdata['files'].items():assert sha(src/n)==h
   for n,h in lockdata['production_controls'].items():assert sha(Path('/opt/voicebox-qwen-627')/n)==h
   assert sha(root/(ENV+'/models/manifest.json').lstrip('/'))==lockdata['model_manifest_sha256']
   assert sha(root/(ENV+'/environment-receipt.json').lstrip('/'))==lockdata['environment_receipt_sha256']
   assert sha(root/REFERENCE.lstrip('/'))==lockdata['reference_sha256']
   assert int((CG/'memory.max').read_text())==20*2**30 and int((CG/'memory.swap.max').read_text())==2*2**30
   assert not any(json.loads(p.read_text()).get('status') in ['running','queued'] for p in (root/'srv/voicebox/qwen-worker/jobs').glob('*/state.json'))
   assert not any(n.startswith(('qwen-','chatterbox-','d088-memory-','d089-inference-')) for n in ct('docker','ps','--format','{{.Names}}').splitlines())
   assert metrics.health()['status']=='healthy' and not metrics.health()['model_loaded']
   baseline=metrics.sample();assert preflight(baseline),'Predictive preflight failed'
   save(job/'started.json',{'at':time.time(),'authorized_attempt':1});result['tts_attempts']=1
   cmd=['docker','run','-d','--name','d089-inference-isolated','--network','none','--no-healthcheck','--cpus','3','--memory','8g','--memory-swap','8g','--pids-limit','128','--user','999:999','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--tmpfs','/tmp:rw,size=256m',
        '-e','HF_HUB_OFFLINE=1','-e','TRANSFORMERS_OFFLINE=1','-e','HF_HOME=/tmp/hf','-e','NUMBA_CACHE_DIR=/tmp/numba','-e','OMP_NUM_THREADS=3','-e','MKL_NUM_THREADS=3','-e','TORCH_NUM_THREADS=3','-e','TOKENIZERS_PARALLELISM=false','-e','PYTHONDONTWRITEBYTECODE=1',
        '-v',ENV+'/venv:/cb/venv:ro','-v',ENV+'/models:/models:ro','-v',BASE+'/source:/src:ro','-v',BASE+'/job:/job:rw','-v',REFERENCE+':/reference/eduardo.wav:ro',
        '--entrypoint','/cb/venv/bin/python',IMAGE,'/src/chatterbox_worker.py','--execute-real','--job','/job','--models','/models','--reference','/reference/eduardo.wav']
   start=time.monotonic();cid=ct(*cmd).strip();assert len(cid)==64
   deadline=time.monotonic()+5
   while cg is None and time.monotonic()<deadline:cg=next(CG.rglob('docker-'+cid+'.scope'),None);time.sleep(.01)
   assert cg is not None
   result['effective_limits']={n:(cg/n).read_text().strip() for n in ['memory.max','memory.swap.max','cpu.max']}
   assert result['effective_limits']['memory.max']==str(8*2**30) and result['effective_limits']['memory.swap.max']=='0'
   quota,period=map(int,result['effective_limits']['cpu.max'].split());assert quota/period==3
   nextinspect=0;phase='startup'
   while True:
    now=time.monotonic();sample=metrics.sample(cg)
    if (job/'events.jsonl').exists():
     lines=(job/'events.jsonl').read_text().splitlines()
     if lines:
      try:phase=json.loads(lines[-1])['phase']
      except json.JSONDecodeError:pass
    sample['phase']=phase;sample['elapsed_seconds']=now-start
    try:sample['worker_peak']=int((cg/'memory.peak').read_text())
    except OSError:pass
    result['measurements'].append(sample)
    reason=stop_reason(sample,baseline)
    if sample.get('worker_swap',0):reason='WORKER_SWAP_NONZERO'
    if STOP or (job/'cancel.flag').exists():reason='CANCELLED'
    if now-start>=300:reason='TIMEOUT_300_SECONDS'
    if reason:raise RuntimeError(reason)
    if now>=nextinspect:
     state=json.loads(ct('docker','inspect','--format','{{json .State}}',cid));nextinspect=now+.25
     if not state['Running']:
      assert not state.get('OOMKilled') and state['ExitCode']==0,'Worker error; retained private stderr'
      data=json.loads((job/'chatterbox-result.json').read_text());assert data['success'];result.update(success=True,worker_result=data);break
    time.sleep(.025)
  except BaseException as exc:result.update(success=False,error=str(exc))
  finally:
   if cid:
    subprocess.run(['pct','exec','627','--','docker','kill',cid],capture_output=True,timeout=15)
    state=json.loads(ct('docker','inspect','--format','{{json .State}}',cid));assert not state['Running'] and state['Pid']==0
    if cg and cg.exists():assert not (cg/'cgroup.procs').read_text().strip()
    result['processes_released']=True;result['container_state']=state
    logs=subprocess.check_output(['pct','exec','627','--','docker','logs',cid],stderr=subprocess.STDOUT)
    (job/'worker.private.log').write_bytes(logs);(job/'worker.private.log').chmod(0o600)
   result['final_host_ct']=metrics.sample();save(job/'supervisor-result.json',result)
 print(json.dumps({k:v for k,v in result.items() if k not in ['measurements','final_host_ct','container_state']}))
if __name__=='__main__':
 def stop(*args):
  global STOP
  STOP=True
 signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop);main()
