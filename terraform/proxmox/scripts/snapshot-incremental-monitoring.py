#!/usr/bin/env python3
"""Read-only snapshot of CT610 config to a private local file. Not a verified rollback backup."""
import argparse
from datetime import datetime,timezone
import json
import os
from pathlib import Path
import subprocess

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 code="""import subprocess
probe='''import pathlib,json\nb=pathlib.Path('/opt/infra-prom/config');files={'prometheus.yml':(b/'prometheus.yml').read_text()}\nfor sub in ['rules','targets']:\n for p in sorted((b/sub).iterdir()):\n  if p.is_file() and p.suffix in ['.yml','.yaml','.json']:files[str(p.relative_to(b))]=p.read_text()\nprint(json.dumps({'files':files}))'''
p=subprocess.run(['pct','exec','610','--','python3','-'],input=probe,text=True,capture_output=True,timeout=25)
assert p.returncode==0,'Read-only config snapshot failed';print(p.stdout,end='')
"""
 r=subprocess.run(['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile='+str(Path.home()/'.ssh/known_hosts'),'pve','python3','-'],input=code,text=True,capture_output=True,timeout=45)
 assert r.returncode==0,'Read-only SSH snapshot failed; details withheld'
 d=json.loads(r.stdout);d['observed_at']=datetime.now(timezone.utc).isoformat();d['mode']='read-only snapshot, not rollback backup'
 os.umask(0o077);a.output.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
 fd=os.open(a.output,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
 with os.fdopen(fd,'w') as f:json.dump(d,f,indent=2);f.write('\n')
 print('Private config snapshot saved; no remote files written')
