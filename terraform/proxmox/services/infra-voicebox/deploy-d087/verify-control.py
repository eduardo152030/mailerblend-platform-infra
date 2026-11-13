"""PVE CT627-only synthetic hold cancellation and shared-slot test. No ML/audio."""
from pathlib import Path
import subprocess,json,time,fcntl,os
CODE=Path('/opt/voicebox-qwen-627')
ct=['pct','exec','627','--']
# Non-UUID job without request/state is never consumed by the production queue.
name='d087b-cancel-check'
subprocess.run(ct+['python3','-c',"from pathlib import Path;import os;p=Path('/srv/voicebox/qwen-worker/jobs/"+name+"');p.mkdir(mode=0o700);os.chown(p,999,999)"],check=True)
log=Path('/mnt/storage/d087b-staging/control-check.private.json')
with log.open('xb') as stream:
 child=subprocess.Popen(['python3',str(CODE/'supervise.py'),'hold','--job',name,'--attempt','01','--timeout','20','--cancel-after','5','--execute'],stdout=stream,stderr=subprocess.PIPE)
 blocked=False
 try:
  deadline=time.monotonic()+10
  while child.poll() is None and time.monotonic()<deadline:
   with open('/run/lock/qwen-d077-627.lock','a') as slot:
    try:fcntl.flock(slot,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(slot,fcntl.LOCK_UN)
    except BlockingIOError:blocked=True;break
   time.sleep(.05)
  child.communicate(timeout=35)
 except BaseException:
  child.terminate();child.communicate(timeout=25);raise
assert child.returncode==0
pid=subprocess.check_output(['lxc-info','-n','627','-pH'],text=True).strip();events=Path('/proc',pid,'root/srv/voicebox/qwen-worker/jobs',name,'events.jsonl').read_text();assert 'synthetic_parent_and_child_waiting' in events
value=json.loads(log.read_text());assert blocked and value.get('expected_synthetic_cancellation')
assert value['container_state']['Pid']==0 and not value['container_state']['Running'] and value['worker_cgroup_empty']
assert value.get('owned_container_removed')
with open('/run/lock/qwen-d077-627.lock','a') as slot:fcntl.flock(slot,fcntl.LOCK_EX|fcntl.LOCK_NB)
print(json.dumps({'synthetic_hold_only':True,'model_loaded':False,'audio_generated':False,'shared_lock_blocks_second_contender':blocked,'cancellation_effective':True,'all_processes_released':True,'owned_worker_removed':True,'persistent_synthetic_evidence_kept':True}))
