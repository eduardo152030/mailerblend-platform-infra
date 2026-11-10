#!/usr/bin/env python3
"""D060 isolated cold-start from consistent DB snapshot and exact candidate provisioning.
Uses the already installed production image, network=none, no published ports.
Production Grafana is never stopped/recreated. Stopped rehearsal and snapshots retained.
"""
import importlib.util,json,time,os,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('f',ROOT/'scripts/phase6-grafana-final.py');f=importlib.util.module_from_spec(s);s.loader.exec_module(f)
g=f.g
RUN=os.environ.get("GRAFANA_REPLAY_ID","replay");assert re.fullmatch(r"[a-z0-9-]+",RUN)
candidate=json.loads((f.PRIVATE/'candidate.json').read_text())
# Stage private copies on the CT. No production config is written by this validator.
print(g.py('''import pathlib,subprocess,json,shutil,os
p=pathlib.Path('/opt/infra-grafana/.runtime/d060/replay');p.mkdir(mode=0o700,exist_ok=False)
shutil.copytree('/opt/infra-grafana/config',p/'config')
d=p/'data';d.mkdir();shutil.copy2('/opt/infra-grafana/.runtime/d060/grafana.db',d/'grafana.db')
os.chown(d,472,0);os.chmod(d,0o750);os.chown(d/'grafana.db',472,0)
print('PASS isolated data/config copies prepared; source snapshot untouched')
'''.replace('/d060/replay','/d060/'+RUN)).decode().strip())
for name,h in candidate.items():
 if not name.startswith('config/'):continue
 dest='/opt/infra-grafana/.runtime/d060/'+RUN+'/'+name
 g.remote(['mkdir','-p',str(Path(dest).parent)]);g.remote(['tee',dest],(f.PRIVATE/'candidate'/name).read_bytes())
code='''import subprocess,json,time,pathlib
name='grafana-d060-replay';base='/opt/infra-grafana/.runtime/d060/replay'
prod=json.loads(subprocess.check_output(['docker','inspect','grafana']))[0];image=prod['Image']
assert subprocess.run(['docker','inspect',name],capture_output=True).returncode!=0,'Replay container already exists'
args=['docker','create','--name',name,'--network','none','--restart','no','--user','472','--cap-drop','ALL','--security-opt','no-new-privileges:true','-e','GF_AUTH_ANONYMOUS_ENABLED=true','-e','GF_AUTH_ANONYMOUS_ORG_ROLE=Viewer','-e','GF_ANALYTICS_REPORTING_ENABLED=false','-e','GF_UNIFIED_ALERTING_ENABLED=false','-e','GF_PLUGINS_PREINSTALL_DISABLED=true','-v',base+'/config/provisioning:/etc/grafana/provisioning:ro','-v',base+'/config/dashboards:/var/lib/grafana/dashboards:ro','-v',base+'/data:/var/lib/grafana',image]
r=subprocess.run(args,capture_output=True);assert r.returncode==0,'Isolated container creation failed; output withheld'
def get(path):
 r=subprocess.run(['docker','exec',name,'wget','-qO-','http://127.0.0.1:3000'+path],capture_output=True,timeout=10)
 assert r.returncode==0,'Replay HTTP not ready';return json.loads(r.stdout)
try:
 assert subprocess.run(['docker','start',name],capture_output=True).returncode==0
 end=time.monotonic()+60
 while True:
  try:
   health=get('/api/health');assert health['database']=='ok';break
  except Exception:
   if time.monotonic()>end:raise
   time.sleep(2)
 found=get('/api/search?type=dash-db');uids=[x['uid'] for x in found]
 models={u:get('/api/dashboards/uid/'+u) for u in uids}
 c=json.loads(subprocess.check_output(['docker','inspect',name]))[0]
 assert c['HostConfig']['NetworkMode']=='none' and not c['HostConfig']['PortBindings']
 print(json.dumps({'health':health,'uid_count':len(uids),'models':models,'isolated_network':True,'published_ports':False,'image_matches_production':c['Image']==image,'actual_production_recreation':False}))
finally:
 subprocess.run(['docker','stop','--time','20',name],capture_output=True)
'''
code=code.replace('/d060/replay','/d060/'+RUN).replace('grafana-d060-replay','grafana-d060-'+RUN)
result=json.loads(g.py(code));b=json.loads((f.PRIVATE/'baseline.json').read_text());models=result.pop('models')
assert set(models)==set(b['dashboards'])|{'proxmox-lxc-details'}
assert all(v['meta']['provisioned'] for v in models.values()),'All nine dashboards must be provisioned'
for uid in ['proxmox-lxc-fleet','proxmox-lxc-details']:
 desired=json.loads((f.PRIVATE/'candidate/config/provisioning/fleet-assets'/(uid+'.json')).read_text());assert models[uid]['meta']['provisioned'];assert models[uid]['dashboard']['panels']==desired['panels']
for uid,prior in b['dashboards'].items():
 if uid in f.OWNED:continue
 assert {k:v for k,v in prior.items() if k!='version'}=={k:v for k,v in models[uid]['dashboard'].items() if k!='version'},'Legacy model differs after cold start'
 assert models[uid]['meta'].get('folderTitle')==b['metadata'][uid].get('folderTitle')
result.update({'timestamp_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'result':'PASS','candidate_hashes':candidate,'restored_legacy_dashboards':7,'new_dashboards_provisioned':2,'test_container_stopped_and_retained':True,'production_unchanged':g.state()['identity']==b['state']['identity']})
(f.EVIDENCE/(os.environ.get('GRAFANA_EVIDENCE_DATE','2026-11-09')+'-d060-recreation-'+RUN+'.json')).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
