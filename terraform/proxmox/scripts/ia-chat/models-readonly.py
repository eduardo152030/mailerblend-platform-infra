#!/usr/bin/env python3
"""PVE: valida manifiesto de4descargas antes delcambioRO; soloCT630."""
import subprocess,json,pathlib,datetime
def run(*a):return subprocess.run(a,text=True,capture_output=True,check=True).stdout.strip()
verified=json.loads(run('pct','exec','630','--','cat','/root/ia-models-verified.json'));assert len(verified)==4
assert sum(x['bytes'] for x in verified)==34071899360
cfg=run('pct','config','630');mp=next(x.split(': ',1)[1] for x in cfg.splitlines() if x.startswith('mp0:'))
if 'ro=1' not in mp:
 run('pct','shutdown','630','--timeout','60');run('pct','set','630','--mp0',mp+',ro=1');run('pct','start','630')
options=run('pct','exec','630','--','findmnt','-no','OPTIONS','/models');assert 'ro' in options.split(',')
print(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'models':verified,'mount_options':options,'config':run('pct','config','630')},indent=2))
