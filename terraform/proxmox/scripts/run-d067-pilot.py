#!/usr/bin/env python3
"""D067: CT627-only reviewed RAM plans; independent service recovery and failure RAM rollback.
No automatic rerun. Requires previously validated backup and exclusive plans.
"""
import argparse,json,subprocess,shlex,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PRIVATE=Path.home()/'.local/share/mailerblend-recovery/voicebox-d067'
SSH=['ssh','-o','UserKnownHostsFile='+str(Path.home()/'.ssh/known_hosts'),'-o','StrictHostKeyChecking=yes','-o','BatchMode=yes','pve']
parser=argparse.ArgumentParser();parser.add_argument('--attempt',default='02');parser.add_argument('--resume-prepared',action='store_true');cli=parser.parse_args();assert cli.attempt.isdigit()
BOOT=Path.home()/'.local/share/mailerblend-recovery/new-lxc/voicebox-d063/terraform/ssh-bootstrap.auto.tfvars.json'
def review(plan,before,after):
 d=json.loads(subprocess.check_output(['terraform','show','-json',str(plan)],cwd=ROOT))
 rows=[x for x in d['resource_changes'] if x['change']['actions']!=['no-op']]
 assert len(rows)==1 and rows[0]['address']=='proxmox_virtual_environment_container.svc["infra-voicebox"]'
 c=rows[0]['change'];assert c['actions']==['update']
 assert [k for k in c['after'] if c['before'].get(k)!=c['after'].get(k)]==['memory']
 assert c['before']['memory']==[{'dedicated':before,'swap':512}] and c['after']['memory']==[{'dedicated':after,'swap':512}]
def apply(plan,label):
 with (PRIVATE/(label+'.apply.private.txt')).open('w') as log:
  subprocess.run(['terraform','apply','-input=false','-parallelism=1',str(plan)],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
assert json.loads((PRIVATE/'restore-before/restore-check.json').read_text())['result']=='PASS'
assert cli.resume_prepared or not (PRIVATE/'execution-started.json').exists(),'Reconcile existing attempt; never repeat generation silently'
review(PRIVATE/'to6144.tfplan',3072,6144)
(PRIVATE/'execution-started.json').write_text('{"decision":"D067"}\n')
passed=False;rollback=None
try:
 if not cli.resume_prepared:apply(PRIVATE/'to6144.tfplan','to6144')
 else:
  current=subprocess.check_output(SSH+['pct config 627'],text=True);assert '\nmemory: 6144\n' in current
  subprocess.run(SSH+['test ! -e /root/voicebox-d067/run'+cli.attempt],check=True)
 rollback=PRIVATE/'rollback3072.tfplan'
 args=['terraform','plan','-input=false','-parallelism=1','-target=proxmox_virtual_environment_container.svc["infra-voicebox"]','-var-file='+str(BOOT),'-var=voicebox_pilot_memory_mib=3072','-out='+str(rollback)]
 with (PRIVATE/'rollback3072.plan.private.txt').open('w') as log:subprocess.run(args,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
 review(rollback,6144,3072)
 cmd=['systemd-run','--unit=voicebox-d067-pilot-'+cli.attempt,'--collect','--wait','--setenv=D067_RESULT_DIR=/root/voicebox-d067/run'+cli.attempt,'--property=RuntimeMaxSec=7200','--property=TimeoutStopSec=150','--property=ExecStopPost=/bin/bash /root/voicebox-d067/restore.sh','/usr/bin/python3','-u','/root/voicebox-d067/run_on_pve.py']
 r=subprocess.run(SSH+[shlex.join(cmd)],capture_output=True,text=True,timeout=7500)
 (PRIVATE/'systemd.private.log').write_text(r.stdout+r.stderr)
 data=subprocess.check_output(SSH+['cat /root/voicebox-d067/run'+cli.attempt+'/result.json'],timeout=30);(PRIVATE/'pilot-result.json').write_bytes(data)
 result=json.loads(data);passed=result['result']=='PASS' and 'original_restored' in result and not result.get('recovery_error');print(data.decode(),flush=True)
finally:
 if not passed:
  # ExecStopPost also covers remote supervisor termination; ensure it has stopped before RAM rollback.
  subprocess.run(SSH+['systemctl stop voicebox-d067-pilot-'+cli.attempt+'.service'],capture_output=True,timeout=180)
  if rollback and rollback.exists():
   review(rollback,6144,3072)
   try:apply(rollback,'rollback3072')
   except subprocess.CalledProcessError:
    # Saved plans evaluate file() again. If docs/manifests changed, refresh and
    # re-review only the exact authorized memory rollback; never broaden scope.
    refreshed=PRIVATE/'rollback3072-refreshed.tfplan'
    cmd=['terraform','plan','-input=false','-parallelism=1','-target=proxmox_virtual_environment_container.svc["infra-voicebox"]','-var-file='+str(BOOT),'-var=voicebox_pilot_memory_mib=3072','-out='+str(refreshed)]
    with (PRIVATE/'rollback3072-refreshed.plan.private.txt').open('w') as log:subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
    review(refreshed,6144,3072);apply(refreshed,'rollback3072-refreshed')
   shutil.copyfile(PRIVATE/'inventory-before.yml',ROOT/'inventory/services/infra-voicebox.yml')
   subprocess.run(['python3','scripts/generate-lxc-inventory.py'],cwd=ROOT,check=True)
   (PRIVATE/'ram-result.json').write_text(json.dumps({'result':'PASS','memory_mib':3072,'reason':'pilot did not pass; previous allocation restored'})+'\n')
  else:raise RuntimeError('No reviewed rollback plan prepared: inspect CT627 before further operations')
 else:(PRIVATE/'ram-result.json').write_text(json.dumps({'result':'PASS','memory_mib':6144,'reason':'authorized allocation; pilot PASS'})+'\n')
 print('D067 finished; retained6GiB' if passed else 'D067 failed; rolled back3GiB',flush=True)
