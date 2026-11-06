#!/usr/bin/env python3
"""Fase 4: auditoría de cierre, solo lectura; no envía mensajes ni aplica configuraciones."""
import argparse
from datetime import datetime,timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tarfile
import urllib.request
import yaml

ROOT=Path(__file__).resolve().parents[1]
def load(name):
    s=importlib.util.spec_from_file_location(name,ROOT/'scripts'/name);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def get(path):
    with urllib.request.urlopen('http://192.168.1.110:9090'+path,timeout=15) as r:return json.load(r)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--runtime',type=Path,default=ROOT/'docs/roadmap/evidence/2026-11-03-phase4-close-runtime.json');a=p.parse_args()
    m=load('rollout-approved-exporters.py');registry=yaml.safe_load((ROOT/'services/common/exporter-migration.yml').read_text());runtime=json.loads(a.runtime.read_text());private=Path.home()/'.local/share/mailerblend-recovery/phase4'
    backups=[]
    for run in private.iterdir():
        if not run.is_dir():continue
        for path in run.rglob('*'):
            if not path.is_file() or not path.name.endswith(('.tar','.tar.gz')):continue
            with tarfile.open(path) as t:members=len(t.getmembers())
            backups.append({'relative_path':str(path.relative_to(private)),'sha256':digest(path),'bytes':path.stat().st_size,'members_readable':members})
    contracts={624:{'urls':['http://192.168.1.124:8090/']},626:{'urls':['http://192.168.1.126:3000/health']},625:{'pg':'infra-journal-db-db-1'},613:{'no_application':True},621:{'urls':['http://192.168.1.121:8081/']},620:{'urls':['http://192.168.1.120:3000/health','http://192.168.1.120:3001/health'],'redis':'infra-excraper-redis-1'},619:{'urls':['http://192.168.1.119:15678/healthz'],'pg':'infra-pulpo-postgres-1'},623:{'urls':['http://127.0.0.1:8069/web/login'],'pg':'infra-gestoria-db-1'}}
    contracts[623]['accepted']=623 in registry['exporters_validated'] or '623' in registry['exporters_validated']
    contracts[617]={'helper_application_dir':'/opt/exporter-phase4-pilot/integration-20261102T223431Z-617'}
    contracts[615]={'urls':['http://127.0.0.1:18092/healthy','http://127.0.0.1:18091/healthy']}
    collector='''import json,subprocess,urllib.request,urllib.error,pathlib,time
contract=CONTRACT
checks={}
for url in contract.get('urls',[]):
 try:
  with urllib.request.urlopen(url,timeout=8) as r:checks[url]=r.status
 except urllib.error.HTTPError as exc:checks[url]=exc.code
 except Exception as exc:checks[url]=type(exc).__name__
for key,args in [('pg',['pg_isready','-h','127.0.0.1','-p','5432']),('redis',['redis-cli','ping'])]:
 if key in contract:checks[key]=subprocess.run(['docker','exec',contract[key]]+args,capture_output=True,timeout=10).returncode==0
if contract.get('no_application'):checks['no_application']='baseline sin aplicaciones'
if contract.get('helper_application_dir'):
 d=pathlib.Path(contract['helper_application_dir']);ns={'__name__':'audit_apps_only'};exec((d/'pilot.py').read_text(),ns);ns['unchanged'](d);checks['helper_application_baseline_unchanged']=True;checks['application_probe']=ns['application_probe']()
out={'checks':checks}
ids=subprocess.check_output(['docker','inspect','node_exporter','cadvisor'],text=True)
configs={}
import hashlib
for c in json.loads(ids):
 files=(c['Config'].get('Labels') or {}).get('com.docker.compose.project.config_files','').split(',')
 files += [m['Source'] for m in c['Mounts'] if m['Source'].endswith('/node-cgroup.sh')]
 for name in files:
  path=pathlib.Path(name)
  if name and path.is_file():configs[name]=hashlib.sha256(path.read_bytes()).hexdigest()
out['active_input_sha256']=configs
if CT==623:
 d=pathlib.Path('/opt/exporter-phase4-pilot/integration-20261102T223431Z-623');base=json.loads((d/'baseline.json').read_text());ns={'__name__':'audit_readonly'};exec((d/'pilot.py').read_text(),ns);ns['unchanged'](d)
 out['application_baseline_unchanged']=True
 if contract.get('accepted'):
  out['originals_preserved_stopped']=all((lambda now,old:now['Id']==old['Id'] and now['Image']==old['Image'] and not now['State']['Running'])(json.loads(subprocess.check_output(['docker','inspect',name+'-pre-phase4-623']))[0],old) for name,old in base['exporters'].items())
 else:
  out['originals_verified']=all((lambda now,old:now['Id']==old['Id'] and now['Image']==old['Image'] and now['State']['Running'])(json.loads(subprocess.check_output(['docker','inspect',name]))[0],old) for name,old in base['exporters'].items())
  out['candidates_stopped']=all(not c['State']['Running'] for name in ['node_exporter-phase4-623-held','cadvisor-phase4-623-held'] for c in json.loads(subprocess.check_output(['docker','inspect',name])))
 out['resources']={name:(pathlib.Path('/sys/fs/cgroup')/name).read_text().strip() for name in ['memory.events','memory.pressure','memory.current','memory.max']}
print(json.dumps(out))
'''
    remote='''import pathlib,hashlib,json,subprocess
expected=BACKUPS
base=pathlib.Path('/mnt/storage/mailerblend-recovery/phase4')
index={}
for path in base.rglob('*'):
 if path.is_file() and path.name.endswith(('.tar','.tar.gz')):index.setdefault(path.name,[]).append(path)
proof=[]
for item in expected:
 path=base/item['relative_path'];paths=[path] if path.exists() else index.get(path.name,[])
 matches=[]
 for candidate in paths:
  h=hashlib.sha256()
  with candidate.open('rb') as f:
   for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
  if h.hexdigest()==item['sha256']:matches.append(str(candidate))
 proof.append({'relative_path':item['relative_path'],'remote_hash_matches':matches})
checks={}
pve_resources={}
for ct,contract in CONTRACTS.items():
 code=COLLECTOR.replace('CONTRACT',repr(contract)).replace('CT',str(ct))
 r=subprocess.run(['pct','exec',str(ct),'--','python3','-'],input=code,text=True,capture_output=True,timeout=90)
 checks[ct]=json.loads(r.stdout) if r.returncode==0 else {'error':'read-only application/baseline check failed'}
 cg=pathlib.Path('/sys/fs/cgroup/lxc')/str(ct)
 pve_resources[ct]={n:(cg/n).read_text().strip() for n in ['memory.events','memory.pressure','memory.current','memory.max','cpu.stat','cpu.max']}
print(json.dumps({'backup_proof':proof,'applications':checks,'pve_resources':pve_resources}))
'''.replace('BACKUPS',repr(backups)).replace('CONTRACTS',repr(contracts)).replace('COLLECTOR',repr(collector))
    r=subprocess.run(m.SSH+['python3','-'],input=remote,capture_output=True,text=True,timeout=300);assert r.returncode==0,'Read-only audit failed; no remote mutation attempted'
    remote_data=json.loads(r.stdout)
    for entry,proof in zip(backups,remote_data['backup_proof']):entry.update(proof)
    targets=get('/api/v1/targets')['data']['activeTargets'];rules=get('/api/v1/rules')['data']['groups'];chain=load('check-incremental-chain.py')
    qualities={}
    for ct in registry['prometheus_integrated']:
        svc=next(s['service'] for s in runtime['services'] if int(s['ct'])==ct);qualities[ct]=chain.assess(chain.collect('http://192.168.1.110:9090',ct,svc))
    out={'observed_utc':datetime.now(timezone.utc).isoformat(),'scope':'Phase4 read-only closure','backups':backups,'applications':remote_data['applications'],'pve_resources':remote_data['pve_resources'],'accepted_chain_issues':qualities,'target_counts':{job:len([t for t in targets if t['labels']['job']==job]) for job in ['node_exporter','cadvisor','blackbox']},'targets_up':{job:len([t for t in targets if t['labels']['job']==job and t['health']=='up']) for job in ['node_exporter','cadvisor','blackbox']},'unhealthy_rules':[r['name'] for g in rules for r in g['rules'] if r['health']!='ok'],'controlled_test_rules':[r['name'] for g in rules for r in g['rules'] if r['name']=='LxcCpuIntegrationVerification'],'telegram_counters':m.telemetry(),'telegram_sent_this_audit':False,'deployment_or_reload_performed':False}
    a.output.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'backup_archives':len(backups),'remote_hash_matches':sum(bool(b['remote_hash_matches']) for b in backups),'accepted_chain_issues':qualities,'targets_up':out['targets_up'],'applications':remote_data['applications']}))

if __name__=='__main__':main()
