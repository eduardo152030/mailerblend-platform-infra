"""Prepared PVE supervisor: one isolated CB process, bounded and cancelable.
Only --execute-real launches an inference. Preparation must NEVER pass this flag.
"""
import argparse,fcntl,json,os,re,signal,subprocess,time
from pathlib import Path
import supervise as metrics  # Existing production D081 sampler only; not its guards.
from engine_policy import CB,preflight,stop_reason
from readiness import chatterbox_ready
CG=Path('/sys/fs/cgroup/lxc/627');ROOT='/srv/voicebox/qwen-worker'
ENV='/srv/voicebox/chatterbox-d085';IMAGE='sha256:bcc5c14f88064ffa76f813d788d183918b208deba45075d8118a2b07c60c248b'
REFERENCE='/srv/voicebox/data/profiles/1fd00418-2a79-4178-883f-af6c3f5e07ee/8840f5e1-990b-463e-b94e-e72beef61917.wav'
STOP=False

def ct(*args):return metrics.ct(*args)

def main():
    p=argparse.ArgumentParser();p.add_argument('--job',required=True);p.add_argument('--execute-real',action='store_true');a=p.parse_args()
    if not re.fullmatch('[a-f0-9]{32}',a.job):p.error('Invalid job identifier')
    if not a.execute_real:p.error('Explicit acoustic authorization and --execute-real required')
    result={'success':False,'processes_released':False,'measurements':[]};cid=None;worker=None
    # Same lock used by the unchanged Qwen supervisor. Keep it until PID0/cgroup empty.
    with open('/run/lock/qwen-d077-627.lock','a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        pid=subprocess.check_output(['lxc-info','-n','627','-pH'],text=True).strip()
        jobs=Path('/proc',pid,'root')/ROOT.lstrip('/')/'jobs';job=jobs/a.job
        try:
            assert job.is_dir() and not job.is_symlink()
            from engine_policy import validate
            r=validate(json.loads((job/'request.json').read_text()));assert r['engine']=='chatterbox'
            assert not (job/'checkpoint').exists(),'Never decode a Qwen checkpoint as Chatterbox'
            assert chatterbox_ready(jobs,Path(__file__).parent)['ready']
            for other in jobs.glob('*/state.json'):
                if other.parent!=job:assert json.loads(other.read_text()).get('status')!='running','Other engine job remains active'
            names=ct('docker','ps','--format','{{.Names}}').splitlines()
            assert not any(n.startswith(('qwen-','chatterbox-')) for n in names),'Residual inference container'
            baseline=metrics.sample();assert preflight(baseline),'Chatterbox predictive headroom/pressure preflight failed'
            assert int((CG/'memory.max').read_text())==15*2**30 and int((CG/'memory.swap.max').read_text())==2*2**30
            assert metrics.health()['status']=='healthy' and not metrics.health()['model_loaded']
            name='chatterbox-d085-'+a.job
            cmd=['docker','run','-d','--name',name,'--network','none','--no-healthcheck',
                 '--label','d077.root='+ROOT,'--label','voicebox.engine=chatterbox','--cpus','3',
                 '--memory','8g','--memory-swap','8g','--pids-limit','128','--user','999:999',
                 '--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--tmpfs','/tmp:rw,size=256m',
                 '-e','HF_HUB_OFFLINE=1','-e','TRANSFORMERS_OFFLINE=1','-e','HF_HOME=/tmp/hf',
                 '-e','NUMBA_CACHE_DIR=/tmp/numba','-e','OMP_NUM_THREADS=3','-e','MKL_NUM_THREADS=3',
                 '-e','TOKENIZERS_PARALLELISM=false','-e','PYTHONDONTWRITEBYTECODE=1',
                 '-v',ENV+':/cb:ro','-v',ENV+'/models:/models:ro','-v',ROOT+'/src:/src:ro',
                 '-v',ROOT+'/jobs/'+a.job+':/job:rw','-v',REFERENCE+':/reference/eduardo.wav:ro',
                 '--entrypoint','/cb/venv/bin/python',IMAGE,'/src/chatterbox_worker.py','--execute-real',
                 '--job','/job','--models','/models','--reference','/reference/eduardo.wav']
            cid=ct(*cmd).strip();assert re.fullmatch('[a-f0-9]{64}',cid)
            worker=next(CG.rglob('docker-'+cid+'.scope'),None);assert worker is not None
            start=time.monotonic()
            while True:
                current=metrics.sample(worker);result['measurements'].append(current)
                reason=stop_reason(current,baseline)
                if STOP or (job/'cancel.flag').exists():reason='CANCELLED';result['cancelled']=True
                if time.monotonic()-start>=CB['timeout_seconds']:reason='TIMEOUT_300_SECONDS'
                if reason:raise RuntimeError(reason)
                state=json.loads(ct('docker','inspect','--format','{{json .State}}',cid))
                if not state['Running']:
                    if state['ExitCode'] or state.get('OOMKilled'):raise RuntimeError('Worker exit/OOM: inspect retained result')
                    data=json.loads((job/'chatterbox-result.json').read_text());assert data['success']
                    result.update(success=True,worker_result=data);break
                time.sleep(.5)
        except Exception as exc:result.update(success=False,error=str(exc))
        finally:
            # Never release the shared slot before all inference processes have died.
            if cid:
                subprocess.run(['pct','exec','627','--','docker','kill',cid],capture_output=True,timeout=15)
                state=json.loads(ct('docker','inspect','--format','{{json .State}}',cid))
                assert not state['Running'] and state['Pid']==0
                deadline=time.monotonic()+10
                while worker and worker.exists() and (worker/'cgroup.procs').read_text().strip():
                    if time.monotonic()>deadline:raise RuntimeError('Residual cgroup: keep worker evidence and do not advance')
                    time.sleep(.1)
                result['processes_released']=True
                ct('docker','rm',cid)  # Owned stopped ephemeral worker only; never image/data.
            else:result['processes_released']=True
            print(json.dumps(result),flush=True)

if __name__=='__main__':
    def cancel(signum,frame):
        global STOP
        STOP=True
    signal.signal(signal.SIGTERM,cancel);signal.signal(signal.SIGINT,cancel);main()
