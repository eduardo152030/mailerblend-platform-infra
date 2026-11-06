#!/usr/bin/env python3
"""D025 continuation: wait for clean extended validation, reuse verified checkpoint620, then sequential wave."""
import argparse,json,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run',required=True);p.add_argument('--execute',action='store_true');a=p.parse_args();assert a.execute
 private=Path.home()/'.local/share/mailerblend-recovery/phase4'/a.run;result=private/'621/post-watch-serialized-check-result.json';trace=private/'621/post-watch-serialized-check.jsonl';deadline=time.monotonic()+900
 statepath=private/'620/state.json';state=json.loads(statepath.read_text())
 if state['result']=='IN_PROGRESS' and 'validator_fix_clean600_verified' in state['steps']:
  print('Waiting for already-running CT620 checkpoint; no duplicate execution',flush=True)
  deadline=time.monotonic()+1500
  while True:
   assert not (private/'HALT.json').exists(),'New post-watch HALT: stop'
   state=json.loads(statepath.read_text());assert state['result'] in ['IN_PROGRESS','PASS'],'CT620 did not pass; halt'
   if state['result']=='PASS' and (private/'620/watch-started.json').exists():break
   assert time.monotonic()<deadline,'CT620 checkpoint timeout';time.sleep(2)
 else:
  while not result.exists():
   if trace.exists():
    rows=[json.loads(l) for l in trace.read_text().splitlines()]
    assert rows and all(x['checks_passed'] for x in rows),'Extended check has anomaly: halt'
   assert time.monotonic()<deadline,'Extended watcher timeout; retain HALT'
   time.sleep(2)
  check=json.loads(result.read_text());assert check['result']=='PASS' and check['samples']>=21 and check['seconds']>=600
  print('Extended600s validation PASS; resuming existing CT620 checkpoint',flush=True)
  subprocess.run(['python3',str(ROOT/'scripts/resume-rolled-back-exporters.py'),'--run',a.run,'--execute'],check=True)
 subprocess.run(['python3',str(ROOT/'scripts/rollout-approved-exporters.py'),'--run',a.run,'--all','--execute'],check=True)
if __name__=='__main__':main()
