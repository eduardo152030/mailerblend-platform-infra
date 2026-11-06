#!/usr/bin/env python3
"""Read-only final acceptance evidence after scoped svc01 watcher and all acceptance gates."""
import argparse
from datetime import datetime,timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import tarfile
import yaml
ROOT=Path(__file__).resolve().parents[1]
def load(name):
 s=importlib.util.spec_from_file_location(name,ROOT/'scripts'/name);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--wave-evidence',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists()
 wave=json.loads(a.wave_evidence.read_text());row=next(r for r in wave['results'] if r['ct']==61211);assert row['result']=='DONE'
 run=row['evidence']['run'];assert re.fullmatch(r'integration-[0-9TZ]+',run)
 d=Path.home()/'.local/share/mailerblend-recovery/phase4'/run/'61211';state=json.loads((d/'state.json').read_text());mon=json.loads((d/'monitoring/state.json').read_text());watch=json.loads((d/'post-watch-result.json').read_text());assert state['result']=='PASS' and watch['result']=='PASS' and watch['seconds']>=900 and watch['samples']>=31
 assert state['observation']['seconds']>=180 and state['observation']['samples']>=7 and mon['rollback_verified'] and mon['idempotence_verified'] and state['telegram']['failures_delta']==0
 rmod=load('rollout-approved-exporters.py');r=object.__new__(rmod.Runner);r.ct=61211;r.run=run;r.root=d.parent;r.here=d;r.directory='/opt/exporter-phase4-pilot/'+run+'-61211';r.log=d/'final-audit.private.log';r.log.touch(mode=0o600);r.watch_mode=True;r.state=state;r.manifest=state['manifest'];r.helper('check');r.namespace(True)
 archives=[]
 for path,info in [(d/'exporters-before.tar',state['backup']),(d/'exporters-after.tar.gz',state['after_archive']),(d/'monitoring/integration-before.tar',mon),(d/'monitoring/integration-after.tar.gz',mon['after_archive'])]:
  assert hashlib.sha256(path.read_bytes()).hexdigest()==info['sha256']
  with tarfile.open(path) as t:
   for member in t:
    if member.isfile():assert len(t.extractfile(member).read())==member.size
  archives.append({'relative_path':str(path.relative_to(d)),'sha256':info['sha256'],'readable':True})
 hashes=state['manifest']['file_sha256']
 code='''import pathlib,json,hashlib,subprocess
base=pathlib.Path('/mnt/storage/mailerblend-recovery/phase4/RUN/61211');proof=ARCHIVES
for x in proof:assert hashlib.sha256((base/x['relative_path']).read_bytes()).hexdigest()==x['sha256']
probe="import pathlib,hashlib,json;d=pathlib.Path("+repr('/opt/exporter-phase4-pilot/RUN-61211')+");expected="+repr(HASHES)+";print(json.dumps({n:hashlib.sha256((d/n).read_bytes()).hexdigest()==h for n,h in expected.items()}))"
p=subprocess.run(['pct','exec','61211','--','python3','-c',probe],capture_output=True,text=True);assert p.returncode==0
source=json.loads(p.stdout);assert all(source.values())
out={}
for ct in [624,626,625,613,621,620,619,623,61211,610]:
 names=['prometheus','alertmanager'] if ct==610 else ['node_exporter','cadvisor']
 probe="import json,subprocess;cs=json.loads(subprocess.check_output(['docker','inspect']+"+repr(names)+"));print(json.dumps({c['Name'].lstrip('/'):{'id':c['Id'],'image':c['Image'],'started_at':c['State']['StartedAt'],'restarts':c['RestartCount'],'running':c['State']['Running']} for c in cs}))"
 p=subprocess.run(['pct','exec',str(ct),'--','python3','-c',probe],capture_output=True,text=True);assert p.returncode==0;out[ct]=json.loads(p.stdout)
print(json.dumps({'sources':source,'runtime':out,'remote_archives_verified':True}))
'''.replace('RUN',run).replace('ARCHIVES',repr(archives)).replace('HASHES',repr(hashes))
 p=subprocess.run(rmod.SSH+['python3','-'],input=code,text=True,capture_output=True,timeout=180);assert p.returncode==0,'Read-only completion audit failed';live=json.loads(p.stdout)
 old=json.loads((ROOT/'docs/roadmap/evidence/2026-11-05-runtime-final.json').read_text());unchanged={}
 for ct,containers in live['runtime'].items():
  if ct=='61211':continue
  before=next(s['runtime']['containers'] for s in old['services'] if int(s['ct'])==int(ct))
  unchanged[ct]=all(any(c['name']==name and c['id']==v['id'] and c['image_id']==v['image'] and c['started_at']==v['started_at'] and c['restarts']==v['restarts'] for c in before) for name,v in containers.items())
 assert all(unchanged.values())
 rows=[json.loads(l) for l in (d/'observations.jsonl').read_text().splitlines()]+[json.loads(l) for l in (d/'post-watch.jsonl').read_text().splitlines()];assert all(s['checks_passed'] and len(s['cpu_alignment'])==4 and len(s['memory_alignment'])==4 for s in rows)
 before=dict(l.split() for l in state['resources_before']['memory.events'].splitlines());after=dict(l.split() for l in rows[-1]['resources']['memory.events'].splitlines());delta={k:int(after[k])-int(v) for k,v in before.items()};assert all(delta[k]==0 for k in ['oom','oom_kill','oom_group_kill'])
 reg=yaml.safe_load((ROOT/'services/common/exporter-migration.yml').read_text());assert len(reg['prometheus_integrated'])==9 and 61211 in reg['prometheus_integrated']
 chain=load('check-incremental-chain.py');svcs=load('prepare-incremental-monitoring.py').generator.load_services();issues={ct:chain.assess(chain.collect('http://192.168.1.110:9090',ct,next(s['name'] for s in svcs if int(s['vmid'])==ct))) for ct in reg['prometheus_integrated']};assert not any(issues.values())
 targets=chain.fetch('http://192.168.1.110:9090','/api/v1/targets')['data']['activeTargets'];counts={job:sum(t['labels']['job']==job and t['health']=='up' for t in targets) for job in ['node_exporter','cadvisor','blackbox']};assert counts=={'node_exporter':17,'cadvisor':17,'blackbox':11}
 out={'observed_at_utc':datetime.now(timezone.utc).isoformat(),'ct':61211,'result':'DONE','run':run,'initial':state['observation'],'watch':watch,'telegram':state['telegram'],'archives':archives,'live':live,'accepted_and_monitoring_unchanged':unchanged,'memory_event_deltas':delta,'accepted_chain_issues':issues,'targets_up':counts,'rollback_verified':True,'idempotence_verified':True,'cpu_ram_aligned_containers':4,'all_samples_passed':len(rows),'human_telegram_receipt_confirmed':False}
 rmod.save(a.output,out);print(json.dumps({'ct':61211,'result':'DONE','accepted':9,'archives':len(archives),'samples':len(rows),'targets_up':counts}))

if __name__=='__main__':main()
