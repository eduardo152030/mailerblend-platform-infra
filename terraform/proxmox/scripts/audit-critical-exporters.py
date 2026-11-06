#!/usr/bin/env python3
"""Fresh read-only inventory for the five authorized D039 critical CTs."""
import argparse,importlib.util,json,subprocess
from pathlib import Path
from datetime import datetime,timezone
import yaml
ROOT=Path(__file__).resolve().parents[1]

def audit(ct):
 s=importlib.util.spec_from_file_location('runner',ROOT/'scripts/rollout-approved-exporters.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 probe='''import pathlib,subprocess,json,re,stat,shutil,hashlib
cs=json.loads(subprocess.check_output(['docker','inspect']+subprocess.check_output(['docker','ps','-aq'],text=True).split()))
out=[]
for c in cs:
 labels=c['Config'].get('Labels') or {}
 out.append({'name':c['Name'].lstrip('/'),'id':c['Id'],'started_at':c['State']['StartedAt'],'image':c['Image'],'image_ref':c['Config']['Image'],'running':c['State']['Running'],'restarts':c['RestartCount'],'health':c['State'].get('Health',{}).get('Status'),'oom_killed':c['State']['OOMKilled'],'compose_service':labels.get('com.docker.compose.service'),'compose_project':labels.get('com.docker.compose.project'),'config_hash':hashlib.sha256(json.dumps([c['Config'],c['HostConfig'],sorted(c['Mounts'],key=lambda m:(m.get('Destination',''),m.get('Source','')))],sort_keys=True).encode()).hexdigest()})
mem=pathlib.Path('/proc/meminfo').read_text()
print(json.dumps({'containers':out,'memory_kib':{k:int(v) for k,v in re.findall(r'^(MemTotal|MemAvailable):\\s+(\\d+)',mem,re.M)},'disk_free':shutil.disk_usage('/').free,'socket_exists':stat.S_ISSOCK(pathlib.Path('/run/containerd/containerd.sock').stat().st_mode),'docker_version':subprocess.check_output(['docker','version','--format','{{.Server.Version}}'],text=True).strip()}))
'''
 remote="import pathlib,json,subprocess\nct="+str(ct)+"\nconf=dict(l.split(': ',1) for l in subprocess.check_output(['pct','config',str(ct)],text=True).splitlines() if ': ' in l)\nr=subprocess.run(['pct','exec',str(ct),'--','python3','-'],input="+repr(probe)+",text=True,capture_output=True,timeout=45);assert r.returncode==0,'Inventory failed'\nj=json.loads(r.stdout);j.update(ct=ct,hostname=conf['hostname'],allocation={k:conf[k] for k in ['hostname','cores','memory','swap']});p=pathlib.Path('/sys/fs/cgroup/lxc')/str(ct);j['cgroup']={n:(p/n).read_text().strip() for n in ['memory.events','memory.pressure','memory.current','memory.max','cpu.max']};print(json.dumps(j))"
 r=subprocess.run(m.SSH+['python3','-'],input=remote,text=True,capture_output=True,timeout=65);assert r.returncode==0,'Strict SSH inventory failed'
 j=json.loads(r.stdout);j.update(mode='read-only',observed_at_utc=datetime.now(timezone.utc).isoformat());return j

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists();rows=[audit(c) for c in [618,622,611,616,610]];a.output.write_text(json.dumps(rows,indent=2)+'\n');a.output.chmod(0o600)
 for r in rows:print(r['ct'],r['hostname'],[(c['name'],c['running'],c['health'],c['image_ref']) for c in r['containers']])
