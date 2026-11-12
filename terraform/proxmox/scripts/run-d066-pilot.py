#!/usr/bin/env python3
"""Run only the authorized D066 pilot; always apply the pre-reviewed scoped RAM rollback."""
import argparse,json,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];PRIVATE=Path.home()/'.local/share/mailerblend-recovery/voicebox-d066';SSH=['ssh','-o','UserKnownHostsFile='+str(Path.home()/'.ssh/known_hosts'),'-o','StrictHostKeyChecking=yes','-o','BatchMode=yes','pve']
ap=argparse.ArgumentParser();ap.add_argument('--attempt',default='03');args=ap.parse_args();assert args.attempt.isdigit();remote_dir='/root/voicebox-d066/run'+args.attempt
plan=PRIVATE/'rollback3072.tfplan';d=json.loads(subprocess.check_output(['terraform','show','-json',str(plan)],cwd=ROOT));c=[x for x in d['resource_changes'] if x['change']['actions']!=['no-op']];assert len(c)==1 and c[0]['address']=='proxmox_virtual_environment_container.svc["infra-voicebox"]' and c[0]['change']['actions']==['update'];change=c[0]['change'];assert [k for k in change['after'] if change['before'].get(k)!=change['after'].get(k)]==['memory'];assert change['after']['memory']==[{'dedicated':3072,'swap':512}]
try:
 cmd=['systemd-run','--unit=voicebox-d066-pilot-'+args.attempt,'--collect','--wait','--setenv=D066_RESULT_DIR='+remote_dir,'--property=RuntimeMaxSec=1500','--property=TimeoutStopSec=120','--property=ExecStopPost=/bin/bash /root/voicebox-d066/restore.sh','/usr/bin/python3','-u','/root/voicebox-d066/run_on_pve.py']
 import shlex
 p=subprocess.run(SSH+[shlex.join(cmd)],cwd=ROOT,capture_output=True,text=True,timeout=1750);(PRIVATE/'systemd.private.log').write_text(p.stdout+p.stderr)
 result=subprocess.check_output(SSH+['cat '+remote_dir+'/result.json'],timeout=30);(PRIVATE/('pilot-attempt'+args.attempt+'.json')).write_bytes(result);(PRIVATE/'pilot-result.json').write_bytes(result);print(result.decode(),flush=True)
finally:
 with (PRIVATE/'rollback3072.apply.private.txt').open('w') as log:
  p=subprocess.run(['terraform','apply','-input=false','-parallelism=1',str(plan)],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
 (PRIVATE/'ram-rollback.json').write_text(json.dumps({'result':'PASS' if p.returncode==0 else 'FAIL','scope':'CT627 only','memory_mib':3072,'other_resources':False},indent=2)+'\n')
 print('RAM ROLLBACK',p.returncode,flush=True)
 if p.returncode:raise RuntimeError('Scoped RAM rollback failed; keep CT, no destroy/recreate')
