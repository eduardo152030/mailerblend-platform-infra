#!/usr/bin/env python3
"""Prepare a fresh read-only CT61211 audit after verified D035 rollback. No apply/restart/write on servers."""
import argparse
from datetime import datetime,timezone
import importlib.util
import json
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parents[1]

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--ct',type=int,choices=[61211],required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists()
 wave=json.loads((ROOT/'docs/roadmap/evidence/2026-11-06-d035-wave.json').read_text());old=next(r for r in wave['results'] if r['ct']==61211);assert old['evidence']['state']=='BLOCKED_ROLLED_BACK' and old['evidence']['originals_verified'] and old['evidence']['application_working']
 run=old['evidence']['run'];directory='/opt/exporter-phase4-pilot/'+run+'-61211'
 collector='''import pathlib,json,subprocess,re,stat,shutil
p=pathlib.Path(DIRECTORY);base=json.loads((p/'baseline.json').read_text());records=json.loads((p/'applied.json').read_text());ns={'__name__':'readonly'};exec((p/'pilot.py').read_text(),ns);ns['unchanged'](p);ns['application_probe']()
for name,old in base['exporters'].items():
 current=json.loads(subprocess.check_output(['docker','inspect',name]))[0]
 assert current['Id']==old['Id'] and current['Image']==old['Image'] and current['State']['Running'],'Original exporter drift'
 held=json.loads(subprocess.check_output(['docker','inspect',name+'-phase4-61211-ram-v1-held']))[0]
 assert held['Id']==records[name]['id'] and not held['State']['Running'],'D035 candidate drift'
ids=subprocess.check_output(['docker','ps','-aq'],text=True).split();containers=[]
for c in json.loads(subprocess.check_output(['docker','inspect']+ids)):
 labels=c['Config'].get('Labels') or {};containers.append({'name':c['Name'].lstrip('/'),'id':c['Id'],'started_at':c['State']['StartedAt'],'image':c['Image'],'running':c['State']['Running'],'compose_service':labels.get('com.docker.compose.service'),'compose_project':labels.get('com.docker.compose.project'),'privileged':c['HostConfig']['Privileged'],'cgroupns':c['HostConfig'].get('CgroupnsMode')})
mem=pathlib.Path('/proc/meminfo').read_text()
print(json.dumps({'containers':containers,'memory_kib':{k:int(v) for k,v in re.findall(r'^(MemTotal|MemAvailable):\\s+(\\d+)',mem,re.M)},'disk_free':shutil.disk_usage('/').free,'socket_exists':stat.S_ISSOCK(pathlib.Path('/run/containerd/containerd.sock').stat().st_mode),'docker_version':subprocess.check_output(['docker','version','--format','{{.Server.Version}}'],text=True).strip()}))
'''.replace('DIRECTORY',repr(directory))
 remote='''import json,pathlib,subprocess
conf=dict(l.split(': ',1) for l in subprocess.check_output(['pct','config','61211'],text=True).splitlines() if ': ' in l)
r=subprocess.run(['pct','exec','61211','--','python3','-'],input=COLLECTOR,text=True,capture_output=True,timeout=50);assert r.returncode==0,'Reentry original/apps/held gate failed'
j=json.loads(r.stdout);j.update(ct=61211,hostname=conf['hostname'],allocation={k:conf[k] for k in ['hostname','cores','memory','swap']})
p=pathlib.Path('/sys/fs/cgroup/lxc/61211');j['cgroup']={n:(p/n).read_text().strip() for n in ['memory.events','memory.pressure','memory.current','memory.max','cpu.max']}
print(json.dumps(j))
'''.replace('COLLECTOR',repr(collector))
 s=importlib.util.spec_from_file_location('r',ROOT/'scripts/rollout-approved-exporters.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 r=subprocess.run(m.SSH+['python3','-'],input=remote,text=True,capture_output=True,timeout=75);assert r.returncode==0,'Strict SSH/read-only audit failed; no mutation'
 j=json.loads(r.stdout);j.update(mode='read-only',observed_at_utc=datetime.now(timezone.utc).isoformat(),previous_run=run);m.save(a.output,[j]);print('Fresh61211 audit saved; originals/apps/old-held verified; no production changes')

if __name__=='__main__':main()
