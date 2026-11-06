#!/usr/bin/env python3
"""D025 safe recovery of blocked CT620 only; original baseline and config checks remain enforced."""
import argparse,hashlib,importlib.util,inspect,json,os,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(n):
 s=importlib.util.spec_from_file_location(n,ROOT/'scripts'/n);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run',required=True);p.add_argument('--execute',action='store_true');a=p.parse_args();assert a.execute;os.umask(0o077)
 m=load('rollout-approved-exporters.py');root=Path.home()/'.local/share/mailerblend-recovery/phase4'/a.run;here=root/'620';state=json.loads((here/'state.json').read_text());assert state['ct']==620 and state['result']=='BLOCKED' and state['steps'][-1]=='apply_ready';assert (root/'HALT.json').exists()
 assert m.digest(here/'exporters-before.tar')==state['backup']['sha256'],'Verified original backup required'
 log=(here/'recovery.private.log').open('a')
 def remote(code,timeout=300):
  r=subprocess.run(m.SSH+['python3','-'],input=code,capture_output=True,text=True,timeout=timeout);log.write(r.stdout+r.stderr);log.flush();assert r.returncode==0,'Recovery failed; stop and retain private evidence';return r.stdout
 directory='/opt/exporter-phase4-pilot/'+a.run+'-620'
 cmd=['python3',directory+'/pilot.py','rollback','--directory',directory,'--execute','--allow-containerd-socket','--use-lxc-cgroup-cpu']
 probe='import subprocess\nr=subprocess.run('+repr(cmd)+',capture_output=True,text=True,timeout=300)\nprint(r.stdout+r.stderr);assert r.returncode==0'
 wrap=lambda body:'import subprocess\nr=subprocess.run(["pct","exec","620","--","python3","-"],input='+repr(body)+',capture_output=True,text=True,timeout=360)\nprint(r.stdout+r.stderr);assert r.returncode==0'
 remote(wrap(probe),400)
 ready=load('exporter-http-readiness.py')
 verify='import json,subprocess,urllib.request,time\n'+inspect.getsource(ready.wait_http)+'''\nbase=json.load(open(DIR+'/baseline.json'))
for name,old in base['exporters'].items():
 now=json.loads(subprocess.check_output(['docker','inspect',name]))[0]
 assert now['Id']==old['Id'] and now['Image']==old['Image'] and now['State']['Running'] and not now['State']['OOMKilled']
 wait_http('http://192.168.1.120:'+str(9100 if name=='node_exporter' else 8085)+'/metrics')
print('Both original exporter IDs/images/running/readiness verified')
'''.replace('DIR',repr(directory))
 remote(wrap(verify),300)
 mon=load('run-incremental-p0.py');mon.HERE=here/'monitoring';mon.CTDIR='/opt/infra-prom/.runtime/'+a.run+'-620';mon.SSH=m.SSH
 mon.helper('rollback')
 # Restore checkpoint includes CT621 contract; verify all previously integrated sources.
 chain=load('check-incremental-chain.py');services={624:'infra-journal-web',626:'infra-journal-api',625:'infra-journal-db',613:'infra-hola',621:'infra-project-gestion'};deadline=time.monotonic()+180
 while True:
  try:
   for ct,svc in services.items():assert not chain.assess(chain.collect('http://192.168.1.110:9090',ct,svc))
   break
  except (AssertionError,OSError):
   assert time.monotonic()<deadline,'Accepted-source checkpoint readiness timeout';time.sleep(3)
 state['safe_rollback_verified']=True;state['result']='BLOCKED_ROLLED_BACK';state['rollback_scope']='CT620 original exporters and Prometheus checkpoint5; candidates retained; no data changes';m.save(here/'state.json',state)
 print('CT620 safely rolled back: original exporters ready, five corrected contracts preserved; HALT retained')
if __name__=='__main__':main()
