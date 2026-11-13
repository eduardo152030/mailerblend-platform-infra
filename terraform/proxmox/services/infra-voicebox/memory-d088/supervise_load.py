"""PVE CT627-only two authorized load tests; no production writes or voice binds."""
from pathlib import Path
import argparse,fcntl,hashlib,json,os,subprocess,sys,time,signal
sys.dont_write_bytecode=True
sys.path.insert(0,'/opt/voicebox-qwen-627')
import supervise as metrics
from engine_policy import preflight,stop_reason
CG=Path('/sys/fs/cgroup/lxc/627');BASE='/srv/voicebox/memory-d088-candidate'
ENV='/srv/voicebox/chatterbox-d085'
IMAGE='sha256:bcc5c14f88064ffa76f813d788d183918b208deba45075d8118a2b07c60c248b'
STOP=False

def ct(*args):return subprocess.check_output(['pct','exec','627','--',*args],text=True,timeout=30)
def atomic(path,value):
    tmp=path.with_suffix('.partial')
    with tmp.open('x') as f:os.chmod(tmp,0o600);json.dump(value,f);f.flush();os.fsync(f.fileno())
    os.replace(tmp,path)
def driver_only(cgroup,proc=Path('/proc')):
    # Docker.inspect.Pid is in the CT namespace; cgroup.procs here uses PVE PIDs.
    pids=(cgroup/'cgroup.procs').read_text().split()
    return len(pids)==1 and b'/src/driver.py' in (proc/pids[0]/'cmdline').read_bytes().split(b'\0')

def probe(cg):
    value=metrics.sample(cg)
    if cg and cg.exists():
        try:value['worker_peak']=int((cg/'memory.peak').read_text())
        except OSError:pass
    return value

def run():
    p=argparse.ArgumentParser();p.add_argument('--execute-two-loads',action='store_true');p.add_argument('--candidate-only',action='store_true');a=p.parse_args();assert a.execute_two_loads or a.candidate_only
    pid=subprocess.check_output(['lxc-info','-n','627','-pH'],text=True).strip();root=Path('/proc',pid,'root');work=root/BASE.lstrip('/');job=work/'job';assert job.is_dir()
    source_lock=json.loads((work/'source/source-lock.json').read_text())
    for name,digest in source_lock['files'].items():assert hashlib.sha256((work/'source'/name).read_bytes()).hexdigest()==digest
    env=root/ENV.lstrip('/')
    assert hashlib.sha256((env/'models/manifest.json').read_bytes()).hexdigest()==source_lock['model_manifest_sha256']
    assert hashlib.sha256((env/'environment-receipt.json').read_bytes()).hexdigest()==source_lock['environment_receipt_sha256']
    result={'real_loads_authorized':1 if a.candidate_only else 2,'tts_inferences':0,'personal_reference_mounted':False,'tests':{}};cid=None;cg=None
    with open('/run/lock/qwen-d077-627.lock','a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        try:
            assert int((CG/'memory.max').read_text())==20*2**30 and int((CG/'memory.swap.max').read_text())==2*2**30
            assert not any(json.loads(p.read_text()).get('status') in ['running','queued'] for p in (root/'srv/voicebox/qwen-worker/jobs').glob('*/state.json'))
            assert not any(n.startswith(('qwen-','chatterbox-','d088-memory-')) for n in ct('docker','ps','--format','{{.Names}}').splitlines())
            baseline=probe(None);assert preflight(baseline);assert metrics.health()['status']=='healthy' and not metrics.health()['model_loaded']
            assert not json.loads(Path('/opt/voicebox-qwen-627/chatterbox-release.json').read_text())['enabled']
            name='d088-memory-627-candidate'
            cmd=['docker','run','-d','--name',name,'--network','none','--no-healthcheck',
                 '--label','voicebox.d088=load-only','--cpus','3','--memory','8g','--memory-swap','8g','--pids-limit','128',
                 '--user','999:999','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--tmpfs','/tmp:rw,size=256m',
                 '-e','D088_CANDIDATE_ONLY='+('1' if a.candidate_only else '0'),'-e','HF_HUB_OFFLINE=1','-e','TRANSFORMERS_OFFLINE=1','-e','HF_HOME=/tmp/hf','-e','NUMBA_CACHE_DIR=/tmp/numba',
                 '-e','OMP_NUM_THREADS=3','-e','MKL_NUM_THREADS=3','-e','TORCH_NUM_THREADS=3','-e','TOKENIZERS_PARALLELISM=false','-e','PYTHONDONTWRITEBYTECODE=1',
                 '-v',ENV+'/venv:/cb/venv:ro','-v',ENV+'/models:/models:ro','-v',BASE+'/source:/src:ro','-v',BASE+'/job:/job:rw',
                 '--entrypoint','/cb/venv/bin/python',IMAGE,'/src/driver.py']
            result['bind_destinations']=['/cb/venv:ro','/models:ro','/src:ro','/job:rw']
            cid=ct(*cmd).strip();assert len(cid)==64
            driver_pid=json.loads(ct('docker','inspect','--format','{{json .State}}',cid))['Pid']
            deadline=time.monotonic()+5
            while cg is None and time.monotonic()<deadline:cg=next(CG.rglob('docker-'+cid+'.scope'),None);time.sleep(.02)
            assert cg is not None
            result['shared_cgroup_for_comparison']=not a.candidate_only
            result['comparison_limitations']='Original session ended on tokenizer failure; remaining candidate uses new cgroup, compare storage/RSS/PSS at common component phases' if a.candidate_only else None
            for variant in (['contracts','candidate'] if a.candidate_only else ['contracts','original','candidate']):
                if STOP:raise RuntimeError('CANCELLED')
                current=probe(cg);reason=stop_reason(current,baseline)
                if reason:raise RuntimeError('Before '+variant+': '+reason)
                assert preflight(current),'Predictive host/CT pressure before '+variant
                assert metrics.health()['status']=='healthy' and not metrics.health()['model_loaded']
                folder=job/variant;assert not (folder/'driver-result.json').exists()
                (job/(variant+'.go')).touch(mode=0o600)
                start=time.monotonic();samples=[];reason=None;next_inspect=0
                while not (folder/'driver-result.json').exists():
                    sample=probe(cg);samples.append(sample)
                    reason=stop_reason(sample,baseline)
                    if STOP:reason='CANCELLED'
                    if time.monotonic()-start>=300:reason='TIMEOUT_300_SECONDS'
                    if reason:
                        (folder/'cancel.flag').touch(mode=0o600)
                        wait=time.monotonic()+12
                        while not (folder/'driver-result.json').exists() and time.monotonic()<wait:time.sleep(.025)
                        if not (folder/'driver-result.json').exists():raise RuntimeError('Child failed to terminate; stop entire container')
                        break
                    if not cg.exists() or not (cg/'cgroup.procs').read_text().strip():raise RuntimeError('Harness stopped/OOM')
                    time.sleep(.025)
                ended=json.loads((folder/'driver-result.json').read_text());one={'reason':reason,'driver':ended,'measurements':samples,'after':probe(cg)}
                if (folder/'result.json').exists():one['worker_result']=json.loads((folder/'result.json').read_text())
                if variant=='contracts':
                    assert ended['exit_code']==0 and not reason,(folder/'stderr.private.log').read_text()[-1500:]
                    one['contracts']=json.loads((folder/'stdout.private.log').read_text().splitlines()[-1]);assert one['contracts']['weight_loads']==0
                    assert one['contracts']['mtl_source_sha256']==source_lock['mtl_source_sha256'],'Installed source differs from pinned version'
                result['tests'][variant]=one;atomic(folder/'supervisor.json',one)
                # Heavy child has died before advancing. PID1 is the only intentional survivor.
                assert ended['child_reaped']
                assert driver_only(cg),'Residual child process: do not start another model'
                if reason and reason!='CHATTERBOX_WORKER_7_GIB':raise RuntimeError(reason)
                if ended['exit_code']!=0 and not reason:raise RuntimeError('Unexpected '+variant+' error; no next weight load')
                final=probe(cg)
                assert not final.get('worker_events',{}).get('oom',0) and final['ct_events']['oom']==baseline['ct_events']['oom']
                print(json.dumps({'variant':variant,'reason':reason,'exit':ended['exit_code'],'seconds':ended['seconds']}),flush=True)
                # Do not free page cache or move charges between tests. Child heaps are gone.
        finally:
            (job/'stop.flag').touch(mode=0o600)
            if cid:
                subprocess.run(['pct','exec','627','--','docker','stop','--time','3',cid],capture_output=True,timeout=15)
                state=json.loads(ct('docker','inspect','--format','{{json .State}}',cid));assert not state['Running'] and state['Pid']==0
                if cg and cg.exists():assert not (cg/'cgroup.procs').read_text().strip()
                result['processes_released']=True;result['container_state']=state
                # Preserve the stopped container and all artifacts; no removals or model writes.
            result['final_host_ct']=probe(None);atomic(job/'session-result.json',result)
    print(json.dumps({'session_completed':True,'tests':list(result['tests']),'all_processes_released':result.get('processes_released')}),flush=True)
if __name__=='__main__':
    def stop(*args):
        global STOP
        STOP=True
    signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop);run()
