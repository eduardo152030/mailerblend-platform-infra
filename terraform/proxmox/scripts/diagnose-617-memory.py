#!/usr/bin/env python3
"""D032: bounded read-only CT617 memory evidence. No remote files, deployment or reload."""
import argparse
from datetime import datetime,timezone
import importlib.util
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--seconds',type=int,default=60);p.add_argument('--ct',type=int,choices=[617,623],default=617);a=p.parse_args()
    assert 3<=a.seconds<=90 and not a.output.exists()
    spec_contract=importlib.util.spec_from_file_location('metric_contract',ROOT/'scripts/exporter_metric_contract.py');metric_contract_module=importlib.util.module_from_spec(spec_contract);spec_contract.loader.exec_module(metric_contract_module)
    library=metric_contract_module.render_alignment_source('memory').split("\nif __name__=='__main__':")[0]
    inside=library+'''
import urllib.request,hashlib
names=[n.lstrip('/') for c in api('/containers/json') for n in c['Names']]
def identities():
 out=[]
 for item in api('/containers/json?all=true'):
  c=api('/containers/'+item['Id']+'/json')
  out.append({'name':c['Name'].lstrip('/'),'id':c['Id'],'image':c['Image'],'running':c['State']['Running'],'started_at':c['State']['StartedAt'],'restarts':c['RestartCount'],'oom_killed':c['State']['OOMKilled']})
 return sorted(out,key=lambda c:c['name'])
def endpoint(port):
 with urllib.request.urlopen('http://127.0.0.1:'+str(port)+'/metrics',timeout=8) as r:text=r.read().decode()
 allowed=('node_memory_','container_memory_','container_last_seen','node_exporter_build_info','cadvisor_version_info')
 return {'observed':time.time(),'lines':[l for l in text.splitlines() if l.startswith(allowed)]}
def resources():
 cg=Path('/sys/fs/cgroup')
 return {n:(cg/n).read_text().strip() for n in ['memory.current','memory.max','memory.stat','memory.swap.current','memory.events','memory.pressure']}
out={'identities_before':identities(),'resources_before':resources(),'node':endpoint(9100),'cadvisor_before':endpoint(8085),'proc_meminfo':Path('/proc/meminfo').read_text(),'points':[]}
end=time.monotonic()+SECONDS
while time.monotonic()<end:
 tick=time.monotonic();out['points']+=collect_once(names);time.sleep(max(.01,.5-(time.monotonic()-tick)))
out.update(identities_after=identities(),resources_after=resources(),cadvisor_after=endpoint(8085))
print(json.dumps(out))
'''.replace('SECONDS',str(a.seconds)).replace('127.0.0.1', '192.168.1.'+str(a.ct-500))
    remote='''import pathlib,subprocess,json,time,socket
cg=pathlib.Path('/sys/fs/cgroup/lxc/617')
def outer():
 status=json.loads(subprocess.check_output(['pvesh','get','/nodes/'+socket.gethostname()+'/lxc/617/status/current','--output-format','json']))
 return {'time':time.time(),'proxmox_status':{k:status.get(k) for k in ['mem','maxmem','swap','maxswap','status','uptime']},'cgroup':{n:(cg/n).read_text().strip() for n in ['memory.current','memory.max','memory.stat','memory.swap.current','memory.events','memory.pressure']}}
out={'pve_before':outer()}
r=subprocess.run(['pct','exec','617','--','python3','-'],input=CODE,text=True,capture_output=True,timeout=120)
if r.returncode:print(json.dumps({'diagnostic_error':r.stderr.splitlines()[-1] if r.stderr else 'CT collector failed'}));raise SystemExit(0)
out['ct']=json.loads(r.stdout);out['pve_after']=outer()
print(json.dumps(out))
'''.replace('617',str(a.ct)).replace('CODE',repr(inside))
    m=importlib.util.spec_from_file_location('rollout',ROOT/'scripts/rollout-approved-exporters.py');runner=importlib.util.module_from_spec(m);m.loader.exec_module(runner)
    r=subprocess.run(runner.SSH+['python3','-'],input=remote,capture_output=True,text=True,timeout=150)
    assert r.returncode==0,'Read-only SSH diagnostic failed; details withheld'
    out=json.loads(r.stdout);assert 'diagnostic_error' not in out,out.get('diagnostic_error');out.update(observed_at_utc=datetime.now(timezone.utc).isoformat(),mode='read-only',seconds_requested=a.seconds)
    a.output.write_text(json.dumps(out,indent=2)+'\n');a.output.chmod(0o600)
    print(json.dumps({'points':len(out['ct']['points']),'identity_unchanged':out['ct']['identities_before']==out['ct']['identities_after'],'output':str(a.output)}))

if __name__=='__main__':main()
