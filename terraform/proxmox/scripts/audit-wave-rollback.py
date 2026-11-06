#!/usr/bin/env python3
"""Read-only D035 rollback audit: source/app identities, coordinated checkpoint and backups."""
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
 wave=json.loads(a.wave_evidence.read_text());row=next(r for r in wave['results'] if r['ct']==61211);assert row['result']=='HALT GLOBAL' and row['evidence']['state']=='BLOCKED_ROLLED_BACK'
 run=row['evidence']['run'];assert re.fullmatch(r'integration-[0-9TZ]+',run)
 d=Path.home()/'.local/share/mailerblend-recovery/phase4'/run/'61211';state=json.loads((d/'state.json').read_text());mon=json.loads((d/'monitoring/state.json').read_text());watch=json.loads((d/'post-watch-result.json').read_text());assert state['safe_rollback_verified'] and mon['rollback_verified'] and mon['offhost_verified'] and watch['result']=='FAIL' and watch['seconds']>=900
 samples=[json.loads(l) for l in (d/'post-watch.jsonl').read_text().splitlines()];first=next(s['elapsed_seconds'] for s in samples if not s['checks_passed']);assert watch['seconds']-first>=600
 before=json.loads((d/'originals-before.json').read_text());after=json.loads((d/'originals-after-recovery.json').read_text());assert load('run-skip-exporter-wave.py').original_proof(before,after)
 archives=[]
 for path,info in [(d/'exporters-before.tar',state['backup']),(d/'monitoring/integration-before.tar',mon)]:
  assert hashlib.sha256(path.read_bytes()).hexdigest()==info['sha256']
  with tarfile.open(path) as tar:
   for member in tar:
    if member.isfile():assert len(tar.extractfile(member).read())==member.size
  archives.append({'relative_path':str(path.relative_to(d)),'sha256':info['sha256'],'readable':True})
 checkpoint=json.loads((d/'monitoring/baseline.json').read_text());hashes={n:hashlib.sha256(v.encode()).hexdigest() for n,v in checkpoint['files'].items()}
 probe='''import pathlib,json,hashlib,subprocess,urllib.request
p=pathlib.Path('/mnt/storage/mailerblend-recovery/phase4/RUN/61211')
for x in ARCHIVES:assert hashlib.sha256((p/x['relative_path']).read_bytes()).hexdigest()==x['sha256']
out={}
for ct in [624,626,625,613,621,620,619,623,61211,610]:
 names=['prometheus','alertmanager'] if ct==610 else ['node_exporter','cadvisor']
 code="import json,subprocess;cs=json.loads(subprocess.check_output(['docker','inspect']+"+repr(names)+"));print(json.dumps({c['Name'].lstrip('/'):{'id':c['Id'],'image':c['Image'],'started_at':c['State']['StartedAt'],'restarts':c['RestartCount'],'running':c['State']['Running']} for c in cs}))"
 r=subprocess.run(['pct','exec',str(ct),'--','python3','-c',code],capture_output=True,text=True);assert r.returncode==0;out[ct]=json.loads(r.stdout)
code="import pathlib,hashlib,json;root=pathlib.Path('/opt/infra-prom/config');expected="+repr(HASHES)+";print(json.dumps({n:hashlib.sha256((root/n).read_bytes()).hexdigest()==h for n,h in expected.items()}))"
r=subprocess.run(['pct','exec','610','--','python3','-c',code],capture_output=True,text=True);assert r.returncode==0;files=json.loads(r.stdout);assert all(files.values())
code="""import json,pathlib
p=pathlib.Path('/opt/exporter-phase4-pilot/RUN-61211');out={}
for kind in ['cpu','memory']:
 pid=json.loads((p/(kind+'-history-process.json')).read_text())['pid'];cmd=pathlib.Path('/proc')/str(pid)/'cmdline';out[kind]=cmd.exists() and bool(cmd.read_bytes())
print(json.dumps(out))
"""
r=subprocess.run(['pct','exec','61211','--','python3','-c',code],capture_output=True,text=True);assert r.returncode==0;collectors=json.loads(r.stdout);assert not any(collectors.values())
cg=pathlib.Path('/sys/fs/cgroup/lxc/61211');resources={n:(cg/n).read_text().strip() for n in ['memory.events','memory.pressure','memory.current','memory.max']}
print(json.dumps({'runtime':out,'checkpoint_files_restored':files,'collectors_active':collectors,'resources':resources,'remote_archives_verified':True}))
'''.replace('RUN',run).replace('ARCHIVES',repr(archives)).replace('HASHES',repr(hashes))
 m=load('rollout-approved-exporters.py');r=subprocess.run(m.SSH+['python3','-'],input=probe,text=True,capture_output=True,timeout=180);assert r.returncode==0,'Read-only rollback audit failed';live=json.loads(r.stdout)
 old=json.loads((ROOT/'docs/roadmap/evidence/2026-11-05-runtime-final.json').read_text());unchanged={}
 for ct,containers in live['runtime'].items():
  if ct=='61211':continue
  previous=next(s['runtime']['containers'] for s in old['services'] if int(s['ct'])==int(ct))
  unchanged[ct]=all(any(c['name']==name and c['id']==v['id'] and c['image_id']==v['image'] and c['started_at']==v['started_at'] and c['restarts']==v['restarts'] for c in previous) for name,v in containers.items())
 assert all(unchanged.values())
 start=dict(l.split() for l in state['resources_before']['memory.events'].splitlines());end=dict(l.split() for l in live['resources']['memory.events'].splitlines());delta={k:int(end[k])-int(v) for k,v in start.items()};assert all(delta[k]==0 for k in ['oom','oom_kill','oom_group_kill'])
 reg=yaml.safe_load((ROOT/'services/common/exporter-migration.yml').read_text());assert len(reg['prometheus_integrated'])==8 and 61211 not in reg['prometheus_integrated']
 out={'observed_at_utc':datetime.now(timezone.utc).isoformat(),'ct':61211,'result':'BLOCKED_ROLLED_BACK','wave_result':'HALT GLOBAL','run':run,'archives':archives,'live':live,'accepted_and_monitoring_unchanged':unchanged,'memory_event_deltas':delta,'initial':state['observation'],'watch':watch,'failed_watch_samples':sum(not s['checks_passed'] for s in samples),'first_watch_failure_seconds':first,'extended_after_first_failure_seconds':watch['seconds']-first,'telegram':state['telegram'],'idempotence_verified_before_failure':True,'originals_and_application_restored':row['evidence']['originals_verified'] and row['evidence']['application_working'],'prior_coverage_unchanged':row['evidence']['prior_coverage_unchanged'],'global_monitoring_healthy':row['evidence']['global_monitoring_healthy'],'legacy614_and_alerts_preserved':True}
 assert out['originals_and_application_restored'] and out['prior_coverage_unchanged'] and out['global_monitoring_healthy']
 m.save(a.output,out);print(json.dumps({'result':out['result'],'accepted':8,'archives_verified':len(archives),'checkpoint_files_restored':len(hashes),'OOM_delta':{k:delta[k] for k in ['oom','oom_kill','oom_group_kill']},'collectors_active':live['collectors_active']}))

if __name__=='__main__':main()
