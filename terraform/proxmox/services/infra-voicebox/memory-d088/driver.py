"""A thin PID1, no ML imports. Sequential children share cgroup/page-cache ownership."""
from pathlib import Path
import json,subprocess,os,time,signal
ROOT=Path('/job');PYTHON='/cb/venv/bin/python';child=None

def write(path,data):
    tmp=path.with_suffix('.partial')
    with tmp.open('x') as f:os.chmod(tmp,0o600);json.dump(data,f);f.flush();os.fsync(f.fileno())
    os.replace(tmp,path)

def kill():
    if child and child.poll() is None:
        try:os.killpg(child.pid,signal.SIGKILL)
        except ProcessLookupError:pass
        child.wait(timeout=10)

def stop(*args):kill();raise SystemExit(0)
signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
try:
    for variant in (['contracts','candidate'] if os.environ.get('D088_CANDIDATE_ONLY')=='1' else ['contracts','original','candidate']):
        start=time.monotonic();command=ROOT/(variant+'.go')
        while not command.exists():
            if (ROOT/'stop.flag').exists() or time.monotonic()-start>360:raise SystemExit(0)
            time.sleep(.05)
        folder=ROOT/variant
        args=[PYTHON,'/src/contracts.py'] if variant=='contracts' else [PYTHON,'/src/load_probe.py','--execute-load','--variant',variant,'--models','/models','--job',str(folder)]
        with (folder/'stdout.private.log').open('xb') as out,(folder/'stderr.private.log').open('xb') as err:
            child=subprocess.Popen(args,stdout=out,stderr=err,start_new_session=True)
            write(folder/'driver-started.json',{'pid':child.pid,'variant':variant,'started_at':time.time()})
            started=time.monotonic();reason=None
            while child.poll() is None:
                if (folder/'cancel.flag').exists():reason='GUARD_CANCELLED';kill();break
                if (ROOT/'stop.flag').exists():reason='STOPPED';kill();break
                if time.monotonic()-started>=300:reason='TIMEOUT_300_SECONDS';kill();break
                time.sleep(.025)
            code=child.wait();write(folder/'driver-result.json',{'variant':variant,'exit_code':code,'reason':reason,'seconds':time.monotonic()-started,'child_reaped':True});child=None
        if (ROOT/'stop.flag').exists():break
    # Keep cache accounting stable until the host has captured the final result.
    while not (ROOT/'stop.flag').exists():time.sleep(.05)
finally:kill()
