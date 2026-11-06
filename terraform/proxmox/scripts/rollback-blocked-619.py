#!/usr/bin/env python3
"""D025 planned safe rollback after failed CT619 observation. No app/data/resource changes."""
import argparse,hashlib,importlib.util,inspect,json,os,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(n):
 s=importlib.util.spec_from_file_location(n,ROOT/'scripts'/n);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run',required=True);p.add_argument('--execute',action='store_true');p.add_argument('--reason',choices=['memory128','cpu256'],default='memory128');a=p.parse_args();assert a.execute;os.umask(0o077)
 root=Path.home()/'.local/share/mailerblend-recovery/phase4'/a.run;here=root/'619';state=json.loads((here/'state.json').read_text());assert state['ct']==619 and state['result']=='BLOCKED' and state['steps'][-1]=='controlled_firing_rule';assert json.loads((root/'HALT.json').read_text())['ct']==619
 m=load('rollout-approved-exporters.py');assert m.digest(here/'exporters-before.tar')==state['backup']['sha256'];mon=load('run-incremental-p0.py');mon.HERE=here/'monitoring';mon.CTDIR='/opt/infra-prom/.runtime/'+a.run+'-619';mon.SSH=m.SSH
 # The controlled test has already been resolved and removed; checked() refuses otherwise.
 with load('monitoring-transaction-lock.py').monitoring_lock(root,exclusive=True):mon.helper('rollback')
 directory='/opt/exporter-phase4-pilot/'+a.run+'-619';cmd=['python3',directory+'/pilot.py','rollback','--directory',directory,'--execute','--allow-containerd-socket','--use-lxc-cgroup-cpu']
 probe='import subprocess\nr=subprocess.run('+repr(cmd)+',capture_output=True,text=True,timeout=300)\nprint(r.stdout+r.stderr);assert r.returncode==0'
 wrap=lambda body:'import subprocess\nr=subprocess.run(["pct","exec","619","--","python3","-"],input='+repr(body)+',capture_output=True,text=True,timeout=360)\nprint(r.stdout+r.stderr);assert r.returncode==0'
 def remote(code,timeout=400):
  r=subprocess.run(m.SSH+['python3','-'],input=code,capture_output=True,text=True,timeout=timeout)
  with (here/'recovery.private.log').open('a') as f:f.write(r.stdout+r.stderr)
  assert r.returncode==0,'Planned rollback failure: stop and retain evidence';return r.stdout
 remote(wrap(probe));ready=load('exporter-http-readiness.py')
 verify='import json,subprocess,urllib.request,time\n'+inspect.getsource(ready.wait_http)+'''\nbase=json.load(open(DIR+'/baseline.json'))
for name,old in base['exporters'].items():
 now=json.loads(subprocess.check_output(['docker','inspect',name]))[0]
 assert now['Id']==old['Id'] and now['Image']==old['Image'] and now['State']['Running'] and not now['State']['OOMKilled']
 wait_http('http://192.168.1.119:'+str(9100 if name=='node_exporter' else 8085)+'/metrics')
with urllib.request.urlopen('http://192.168.1.119:15678/healthz',timeout=10) as response:assert response.status==200
assert subprocess.run(['docker','exec','infra-pulpo-postgres-1','pg_isready','-h','127.0.0.1','-p','5432'],capture_output=True,timeout=10).returncode==0
print('Original exporter IDs/images/readiness and n8n/PostgreSQL availability verified')
'''.replace('DIR',repr(directory));remote(wrap(verify))
 state['result']='BLOCKED_ROLLED_BACK';state['safe_rollback_verified']=True;state['blocked_reason']=('cadvisor128MiB reaches memory.max repeatedly, PSI>5 and CPU comparison failures' if a.reason=='memory128' else 'D028 cadvisor256MiB: repeated cAdvisor/Docker CPU comparison failures; extended observation failed; no subsequent CT');state['new_candidates_preserved_stopped']=True;m.save(here/'state.json',state)
 load('report-approved-rollout.py').update(a.run);print('CT619 safe rollback PASS; six corrected contracts retained; CT623 and later not started')
if __name__=='__main__':main()
