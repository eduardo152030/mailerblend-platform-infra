#!/usr/bin/env python3
"""D032: compare only eight accepted exporters and reverted CT617, read-only/sanitized."""
import argparse
from datetime import datetime,timezone
import importlib.util
import json
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parents[1]

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists()
    collector='''import json,subprocess,pathlib,hashlib
ids=subprocess.check_output(['docker','ps','-aq'],text=True).split();out=[]
for c in json.loads(subprocess.check_output(['docker','inspect']+ids)):
 name=c['Name'].lstrip('/')
 if not name.startswith(('node_exporter','cadvisor')):continue
 h=c['HostConfig'];labels=c['Config'].get('Labels') or {};hashes={}
 files=labels.get('com.docker.compose.project.config_files','').split(',')+[m['Source'] for m in c['Mounts'] if m['Source'].endswith('node-cgroup.sh')]
 for f in files:
  p=pathlib.Path(f)
  if f and p.is_file():hashes[f]=hashlib.sha256(p.read_bytes()).hexdigest()
 out.append({'name':name,'id':c['Id'],'running':c['State']['Running'],'image':c['Image'],'image_reference':c['Config']['Image'],'started_at':c['State']['StartedAt'],'restarts':c['RestartCount'],'oom_killed':c['State']['OOMKilled'],'command':c['Config'].get('Cmd'),'memory_limit':h['Memory'],'nano_cpus':h['NanoCpus'],'privileged':h['Privileged'],'pid_mode':h['PidMode'],'cgroupns':h.get('CgroupnsMode'),'project':labels.get('com.docker.compose.project'),'mounts':[{'source':m['Source'],'target':m['Destination'],'rw':m['RW']} for m in c['Mounts']],'active_input_sha256':hashes})
print(json.dumps(out))
'''
    remote='''import subprocess,json
out={}
for ct in [624,626,625,613,621,620,619,623,617]:
 r=subprocess.run(['pct','exec',str(ct),'--','python3','-'],input=COLLECTOR,capture_output=True,text=True,timeout=30)
 assert r.returncode==0,'Read-only template audit failed'
 out[ct]=json.loads(r.stdout)
print(json.dumps(out))
'''.replace('COLLECTOR',repr(collector))
    s=importlib.util.spec_from_file_location('r',ROOT/'scripts/rollout-approved-exporters.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
    r=subprocess.run(m.SSH+['python3','-'],input=remote,text=True,capture_output=True,timeout=300);assert r.returncode==0,'Read-only SSH audit failed; details withheld'
    data={'observed_at_utc':datetime.now(timezone.utc).isoformat(),'mode':'read-only','exporters':json.loads(r.stdout)}
    a.output.write_text(json.dumps(data,indent=2)+'\n');print('Read-only exporter comparison saved:9 CT; no deploy/reload')

if __name__=='__main__':main()
