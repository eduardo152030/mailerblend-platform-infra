#!/usr/bin/env python3
"""D060 Grafana-only provisioning transaction. Strict SSH, private restore-checked backup.
No production restarts, Terraform, applications, secrets, rules or Telegram changes.
"""
import argparse,fcntl,importlib.util,io,json,os,sqlite3,subprocess,tarfile,time
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('g',ROOT/'scripts/deploy-fleet-dashboard.py');g=importlib.util.module_from_spec(s);s.loader.exec_module(g)
s=importlib.util.spec_from_file_location('stage',ROOT/'scripts/phase6-stage-a.py');t=importlib.util.module_from_spec(s);s.loader.exec_module(t)
PRIVATE=Path.home()/'.local/share/mailerblend-recovery/grafana/d060'
BASE='/opt/infra-grafana';EVIDENCE=ROOT/'docs/roadmap/evidence'
ASSETS=ROOT/'services/infra-grafana'
OWNED={'proxmox-lxc-fleet','proxmox-lxc-details'}
def save(name,data):
 p=PRIVATE/name;p.parent.mkdir(parents=True,exist_ok=True,mode=0o700);p.write_text(json.dumps(data,indent=2)+'\n');os.chmod(p,0o600)
def baseline():
 assert not (PRIVATE/'baseline.json').exists(),'Baseline already exists; do not overwrite'
 assert g.api('/api/health')['database']=='ok'
 b={'started':time.time(),'state':g.state(),'dashboards':g.dashboards(),'metadata':{},'datasources':g.api('/api/datasources'),'targets':t.api('/api/v1/targets'),'rules':t.api('/api/v1/rules')}
 for uid in b['dashboards']:b['metadata'][uid]=g.api('/api/dashboards/uid/'+uid)['meta']
 body=g.py('''import sqlite3,subprocess,json,pathlib,tarfile,io,sys,os
p=pathlib.Path('/opt/infra-grafana/.runtime/d060');p.mkdir(parents=True,exist_ok=False);os.chmod(p,0o700)
c=json.loads(subprocess.check_output(['docker','inspect','grafana']))[0];v=next(m['Source'] for m in c['Mounts'] if m['Destination']=='/var/lib/grafana')
src=sqlite3.connect('file:'+v+'/grafana.db?mode=ro',uri=True);dst=sqlite3.connect(str(p/'grafana.db'));src.backup(dst);assert dst.execute('pragma integrity_check').fetchone()[0]=='ok';dst.close();src.close()
stream=io.BytesIO()
with tarfile.open(fileobj=stream,mode='w:gz') as a:
 a.add('/opt/infra-grafana/config',arcname='config');a.add('/opt/infra-grafana/docker-compose.yml',arcname='docker-compose.yml');a.add(p/'grafana.db',arcname='grafana.db')
body=stream.getvalue();(p/'before.tar.gz').write_bytes(body);os.chmod(p/'before.tar.gz',0o600);os.chmod(p/'grafana.db',0o600);sys.stdout.buffer.write(body)
''')
 p=PRIVATE/'before.tar.gz';p.write_bytes(body);os.chmod(p,0o600)
 assert g.py("import hashlib;print(hashlib.sha256(open('/opt/infra-grafana/.runtime/d060/before.tar.gz','rb').read()).hexdigest())").decode().strip()==g.digest(body)
 dest=PRIVATE/'before';dest.mkdir(mode=0o700)
 with tarfile.open(fileobj=io.BytesIO(body)) as a:a.extractall(dest,filter='data')
 assert all(g.digest((dest/f).read_bytes())==h for f,h in b['state']['hashes'].items())
 db=sqlite3.connect('file:'+str(dest/'grafana.db')+'?mode=ro',uri=True);assert db.execute('pragma integrity_check').fetchone()[0]=='ok';db.close()
 b['backup_sha256']=g.digest(body);b['compose_hash']=g.digest((dest/'docker-compose.yml').read_bytes());save('baseline.json',b)
 print('PASS fresh baseline; CT/offhost config+Compose+SQLite backup; restore-check')
def prepare():
 b=json.loads((PRIVATE/'baseline.json').read_text())
 now=g.state();assert now['identity']==b['state']['identity']
 if now['hashes']!=b['state']['hashes']:
  matched=False
  for manifest in ['candidate.json','previous-candidate.json']:
   path=PRIVATE/manifest
   if not path.exists():continue
   prior=json.loads(path.read_text());expected=dict(b['state']['hashes']);expected.update({k:v for k,v in prior.items() if k.startswith('config/')})
   if now['hashes']==expected:
    assert g.digest(g.remote(['cat',BASE+'/docker-compose.yml']))==prior['docker-compose.yml'];matched=True;break
  assert matched,'Config drift'
  save('previous-candidate.json',prior)
 # Export only previously provisioned legacy dashboards, keeping UID/content/folder.
 for uid,meta in b['metadata'].items():
  if uid in OWNED:continue
  folder=meta.get('folderTitle');sub='Infra/' if folder=='Infra' else ''
  assert folder in ['Infra','General']
  filename=Path(meta['provisionedExternalId']).name if meta.get('provisionedExternalId') else uid+'.json'
  def sensitive_keys(obj):
   if isinstance(obj,dict):
    return any(k.lower() in {'password','token','apikey','clientsecret','private_key','authorization','securejsondata'} and bool(v) for k,v in obj.items()) or any(sensitive_keys(v) for v in obj.values())
   return isinstance(obj,list) and any(sensitive_keys(x) for x in obj)
  assert not sensitive_keys(b['dashboards'][uid]),'Possible credentials in dashboard model; do not export'
  out=ASSETS/'config/provisioning/legacy-assets'/sub/filename;out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(b['dashboards'][uid],indent=2,ensure_ascii=False)+'\n')
 provider={'apiVersion':1,'providers':[{'name':'default','orgId':1,'type':'file','disableDeletion':True,'allowUiUpdates':False,'updateIntervalSeconds':30,'options':{'path':'/etc/grafana/provisioning/legacy-assets','foldersFromFilesStructure':True}}]}
 (ASSETS/'config/provisioning/dashboards/default.yml').write_text(yaml.safe_dump(provider,sort_keys=False))
 (ASSETS/'config/provisioning/dashboards/provider.yml').write_text('# Retired duplicate provider; legacy dashboards use the unique default provider.\napiVersion: 1\nproviders: []\n')
 # Compose is a cold-start recipe only. No up/recreate/pull is executed.
 image=json.loads(g.py("import subprocess,json;c=json.loads(subprocess.check_output(['docker','inspect','grafana']))[0];print(json.dumps(json.loads(subprocess.check_output(['docker','image','inspect',c['Image']]))[0]['RepoDigests'][0]))"))
 compose=yaml.safe_load((PRIVATE/'before/docker-compose.yml').read_text());svc=compose['services']['grafana'];svc['image']=image
 svc['volumes']=['/opt/infra-grafana/config/provisioning:/etc/grafana/provisioning:ro','/opt/infra-grafana/config/dashboards:/var/lib/grafana/dashboards:ro','grafana_data:/var/lib/grafana']
 cp=PRIVATE/'candidate/docker-compose.yml';cp.parent.mkdir(exist_ok=True);cp.write_text(yaml.safe_dump(compose,sort_keys=False));os.chmod(cp,0o600)
 local=yaml.safe_load((ASSETS/'compose/docker-compose.yml').read_text());local['services']['grafana']['image']=image;local['services']['grafana']['volumes']=svc['volumes'];(ASSETS/'compose/docker-compose.yml').write_text(yaml.safe_dump(local,sort_keys=False))
 paths=['config/provisioning/dashboards/default.yml','config/provisioning/dashboards/provider.yml','config/provisioning/fleet-assets/proxmox-lxc-fleet.json','config/provisioning/fleet-assets/proxmox-lxc-details.json']+[str(p.relative_to(ASSETS)) for p in sorted((ASSETS/'config/provisioning/legacy-assets').rglob('*.json'))]
 for name in paths:
  out=PRIVATE/'candidate'/name;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes((ASSETS/name).read_bytes())
 paths+=['docker-compose.yml'];save('candidate.json',{name:g.digest((PRIVATE/'candidate'/name).read_bytes()) for name in paths})
 print('Prepared Grafana-only candidate: two fleet dashboards, unique providers, preserved legacy, matching Compose mounts/image')
def defs(data):return [(r['name'],r['query'],r.get('duration'),r.get('labels'),r.get('annotations')) for group in data['groups'] for r in group['rules']]
def validate():
 c=json.loads((PRIVATE/'candidate.json').read_text());names=[];paths=[]
 for name,h in c.items():
  body=(PRIVATE/'candidate'/name).read_bytes();assert g.digest(body)==h
  if name.endswith('.json'):d=json.loads(body);assert d['uid']
  if 'dashboards/' in name and name.endswith('.yml'):
   for p in yaml.safe_load(body).get('providers',[]):names.append(p['name']);paths.append(p['options']['path'])
 # fleet.yml is unchanged and included in checks of all providers.
 for p in yaml.safe_load((ASSETS/'config/provisioning/dashboards/fleet.yml').read_text())['providers']:names.append(p['name']);paths.append(p['options']['path'])
 assert len(names)==len(set(names)) and len(paths)==len(set(paths))
 config=yaml.safe_load((PRIVATE/'candidate/docker-compose.yml').read_text());assert len(config['services']['grafana']['volumes'])==3
 r=g.remote(['docker','compose','-f','/opt/infra-grafana/docker-compose.yml','config','--quiet']);assert r is not None
 save('validated.json',c);print('PASS JSON/YAML/provider uniqueness; deterministic candidate hashes; Compose parser')
def verify():
 b=json.loads((PRIVATE/'baseline.json').read_text());c=json.loads((PRIVATE/'candidate.json').read_text());expected=dict(b['state']['hashes']);expected.update({k:v for k,v in c.items() if k.startswith('config/')})
 now=g.state();assert now['identity']==b['state']['identity'],'Grafana was restarted';assert now['hashes']==expected,'Configuration drift'
 assert sorted(now['mounts'],key=lambda x:x['Destination'])==sorted(b['state']['mounts'],key=lambda x:x['Destination'])
 assert g.digest(g.remote(['cat',BASE+'/docker-compose.yml']))==c['docker-compose.yml']
 assert g.api('/api/datasources')==b['datasources'];assert g.api('/api/health')['database']=='ok'
 current=g.dashboards();assert set(current)==set(b['dashboards'])|{'proxmox-lxc-details'}
 assert all(g.api('/api/dashboards/uid/'+uid)['meta']['provisioned'] for uid in current),'Dashboard not provisioned'
 def content(m):return {k:v for k,v in m.items() if k!='version'}
 for uid,old in b['dashboards'].items():
  if uid not in OWNED:
   assert content(current[uid])==content(old),'Existing dashboard changed: '+uid
   assert g.api('/api/dashboards/uid/'+uid)['meta'].get('folderTitle')==b['metadata'][uid].get('folderTitle'),'Folder moved'
 for uid in OWNED:
  live=g.api('/api/dashboards/uid/'+uid);assert live['meta']['provisioned']
  local=json.loads((PRIVATE/'candidate/config/provisioning/fleet-assets'/(uid+'.json')).read_text())
  assert live['dashboard']['panels']==local['panels'] and live['dashboard']['templating']==local['templating'],'Waiting for provisioned model'
 assert defs(t.api('/api/v1/rules'))==defs(b['rules']),'Rule changes'
 old={(json.dumps(x['labels'],sort_keys=True),x['scrapeUrl']) for x in b['targets']['activeTargets']};now={(json.dumps(x['labels'],sort_keys=True),x['scrapeUrl']) for x in t.api('/api/v1/targets')['activeTargets']};assert old==now,'Target set changed'
 assert all(x['health']=='up' for x in t.api('/api/v1/targets')['activeTargets'])
 print('PASS provisioned dashboards, seven legacy models/folders, datasources, target set and F5 rules preserved; zero restarts')
def rollback():
 b=json.loads((PRIVATE/'baseline.json').read_text());c=json.loads((PRIVATE/'candidate.json').read_text());protected={}
 # Retain dashboards while removing their provisioning associations. The original
 # providers had disableDeletion=false and could otherwise delete adopted models.
 for name in c:
  prior=PRIVATE/'before'/name
  if prior.exists():
   body=prior.read_bytes()
   if 'config/provisioning/dashboards/' in name:
    doc=yaml.safe_load(body)
    for provider in doc.get('providers',[]):provider['disableDeletion']=True
    protected[name]=body;body=yaml.safe_dump(doc,sort_keys=False).encode()
   g.remote(['tee',BASE+'/'+name],body)
  else:g.py('from pathlib import Path;Path('+repr(BASE+'/'+name)+').unlink(missing_ok=True)')
 g.api('/api/admin/provisioning/dashboards/reload',post=True)
 assert set(b['dashboards'])<=set(g.dashboards()),'Stop: retain snapshot and inspect dashboard associations'
 for name,body in protected.items():g.remote(['tee',BASE+'/'+name],body)
 g.api('/api/admin/provisioning/dashboards/reload',post=True)
 assert g.state()['hashes']==b['state']['hashes']
 assert set(b['dashboards'])<=set(g.dashboards())
 print('ROLLBACK previous config restored with deletion protection; backups retained. New Details model retained; no automatic UID deletion.')
def apply():
 b=json.loads((PRIVATE/'baseline.json').read_text());c=json.loads((PRIVATE/'candidate.json').read_text());assert c==json.loads((PRIVATE/'validated.json').read_text())
 for name,h in c.items():assert g.digest((PRIVATE/'candidate'/name).read_bytes())==h
 expected=dict(b['state']['hashes']);expected.update({k:v for k,v in c.items() if k.startswith('config/')})
 if g.state()['hashes']==expected:
  verify();save('idempotence.json',{'writes':0,'reloads':0,'restarts':0,'result':'PASS'});print('IDEMPOTENT zero writes/reloads/restarts');return
 prior_hashes=dict(b['state']['hashes']);prior_compose=b['compose_hash']
 if (PRIVATE/'previous-candidate.json').exists():
  prior=json.loads((PRIVATE/'previous-candidate.json').read_text());prior_hashes.update({k:v for k,v in prior.items() if k.startswith('config/')});prior_compose=prior['docker-compose.yml']
 assert g.state()['hashes']==prior_hashes,'Drift before apply'
 assert g.digest(g.remote(['cat',BASE+'/docker-compose.yml']))==prior_compose
 try:
  changed=[]
  for name,h in c.items():
   old=(prior_hashes.get(name) if name.startswith('config/') else prior_compose)
   if old==h:continue
   g.remote(['mkdir','-p',str(Path(BASE+'/'+name).parent)]);g.remote(['tee',BASE+'/'+name],(PRIVATE/'candidate'/name).read_bytes());changed.append(name)
  assert g.api('/api/admin/provisioning/dashboards/reload',post=True)
  end=time.monotonic()+50
  while True:
   try:verify();break
   except (AssertionError,Exception):
    if time.monotonic()>end:raise
    time.sleep(2)
  event={'writes':len(changed),'reloads':1,'restarts':0,'changed_files':changed,'time':time.time()}
  prior_events=json.loads((PRIVATE/'apply-history.json').read_text()) if (PRIVATE/'apply-history.json').exists() else []
  save('apply-history.json',prior_events+[event]);save('applied.json',event)
 except Exception:rollback();raise
if __name__=='__main__':
 PRIVATE.mkdir(parents=True,exist_ok=True,mode=0o700);os.chmod(PRIVATE,0o700);lock=(PRIVATE/'transaction.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 p=argparse.ArgumentParser();p.add_argument('action',choices=['baseline','prepare','validate','apply','verify','rollback']);a=p.parse_args();globals()[a.action]()
