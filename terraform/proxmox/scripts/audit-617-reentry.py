#!/usr/bin/env python3
"""Read-only fresh CT617 reentry audit: originals/apps verified, held candidates retained."""
import argparse
from datetime import datetime,timezone
import importlib.util
import json
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parents[1]

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists()
 collector='''import json,pathlib,subprocess,shutil,re,stat
p=pathlib.Path('/opt/exporter-phase4-pilot/integration-20261102T223431Z-617')
base=json.loads((p/'baseline.json').read_text());records=json.loads((p/'applied.json').read_text());ns={'__name__':'readonly'};exec((p/'pilot.py').read_text(),ns);ns['unchanged'](p);ns['application_probe']()
for name,old in base['exporters'].items():
 now=json.loads(subprocess.check_output(['docker','inspect',name]))[0]
 assert now['Id']==old['Id'] and now['Image']==old['Image'] and now['State']['Running'],'Original identity drift'
 held=json.loads(subprocess.check_output(['docker','inspect',name+'-phase4-617-held']))[0]
 assert not held['State']['Running'] and held['Id']==records[name]['id'],'Held candidate drift'
ids=subprocess.check_output(['docker','ps','-aq'],text=True).split();out=[]
for c in json.loads(subprocess.check_output(['docker','inspect']+ids)):
 labels=c['Config'].get('Labels') or {}
 out.append({'name':c['Name'].lstrip('/'),'id':c['Id'],'started_at':c['State']['StartedAt'],'running':c['State']['Running'],'image':c['Image'],'compose_service':labels.get('com.docker.compose.service'),'compose_project':labels.get('com.docker.compose.project'),'privileged':c['HostConfig']['Privileged'],'cgroupns':c['HostConfig'].get('CgroupnsMode')})
mem=pathlib.Path('/proc/meminfo').read_text()
print(json.dumps({'containers':out,'memory_kib':{k:int(v) for k,v in re.findall(r'^(MemTotal|MemAvailable):\\s+(\\d+)',mem,re.M)},'disk_free':shutil.disk_usage('/').free,'socket_exists':stat.S_ISSOCK(pathlib.Path('/run/containerd/containerd.sock').stat().st_mode),'docker_version':subprocess.check_output(['docker','version','--format','{{.Server.Version}}'],text=True).strip()}))
'''
 remote='''import subprocess,json,pathlib
config=dict(l.split(': ',1) for l in subprocess.check_output(['pct','config','617'],text=True).splitlines() if ': ' in l)
r=subprocess.run(['pct','exec','617','--','python3','-'],input=COLLECTOR,text=True,capture_output=True,timeout=45)
assert r.returncode==0,'Reentry baseline drift or application failure; no changes'
out=json.loads(r.stdout);out.update(ct=617,hostname=config['hostname'],allocation={k:config[k] for k in ['hostname','cores','memory','swap']})
p=pathlib.Path('/sys/fs/cgroup/lxc/617');out['cgroup']={n:(p/n).read_text().strip() for n in ['memory.events','memory.pressure','memory.current','memory.max','cpu.max']}
print(json.dumps(out))
'''.replace('COLLECTOR',repr(collector))
 s=importlib.util.spec_from_file_location('runner',ROOT/'scripts/rollout-approved-exporters.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 r=subprocess.run(m.SSH+['python3','-'],input=remote,text=True,capture_output=True,timeout=60);assert r.returncode==0,'Fresh read-only CT617 audit failed; no mutation'
 data=json.loads(r.stdout);data.update(observed_at_utc=datetime.now(timezone.utc).isoformat(),mode='read-only')
 a.output.write_text(json.dumps([data],indent=2)+'\n');print('CT617 fresh audit PASS: originals/apps/held verified; no changes')

if __name__=='__main__':main()
