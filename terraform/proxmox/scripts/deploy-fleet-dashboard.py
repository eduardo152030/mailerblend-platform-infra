#!/usr/bin/env python3
"""D052: strict-SSH file provisioning transaction; no Compose/pull/restart.
Credentials remain local and private. Backup contains Grafana DB; never commit it.
"""
import fcntl,argparse,base64,hashlib,io,json,os,shlex,sqlite3,subprocess,tarfile,time,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PRIVATE=Path.home()/'.local/share/mailerblend-recovery/grafana/d052'
BASE='/opt/infra-grafana/'
FILES=['config/provisioning/dashboards/fleet.yml','config/provisioning/fleet-assets/proxmox-lxc-fleet.json']
URL='http://192.168.1.111:3010'
UID='proxmox-lxc-fleet'
def digest(b):return hashlib.sha256(b).hexdigest()
def remote(args,body=None):
 r=subprocess.run(['ssh','-o','UserKnownHostsFile='+str(Path.home()/'.ssh/known_hosts'),'-o','StrictHostKeyChecking=yes','-o','BatchMode=yes','pve',shlex.join(['pct','exec','611','--']+args)],input=body,capture_output=True,timeout=120)
 assert r.returncode==0,'CT611 remote operation failed; output withheld'
 return r.stdout
def py(code):return remote(['python3','-c',code])
def credentials():
 p=Path(os.environ.get('GRAFANA_CREDENTIAL_FILE',ROOT/'services/infra-grafana/config/.env'))
 lines=[s.strip() for s in p.read_text().splitlines() if s.strip() and not s.strip().startswith('#')]
 pairs={}
 for s in lines:
  sep='=' if '=' in s else ':'
  k,v=s.split(sep,1);pairs[k.strip().lower()]=v.strip().strip('\"\'')
 user=next((pairs[k] for k in ['gf_security_admin_user','grafana_user','user','username','usuario'] if k in pairs),None)
 password=next((pairs[k] for k in ['gf_security_admin_password','grafana_password','password','contraseña','contrasena'] if k in pairs),None)
 if not user or not password:
  assert len(lines)==2,'Unsupported credential file format'
  user,password=[s.split(':' if ':' in s else '=',1)[1].strip().strip('\"\'') for s in lines]
 return {'Authorization':'Basic '+base64.b64encode((user+':'+password).encode()).decode()}
def api(path,post=False):
 req=urllib.request.Request(URL+path,headers=credentials(),data=b'' if post else None)
 with urllib.request.urlopen(req,timeout=30) as r:return json.load(r)
def save(name,data):
 PRIVATE.mkdir(parents=True,exist_ok=True,mode=0o700);os.chmod(PRIVATE,0o700)
 p=PRIVATE/name;p.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n');os.chmod(p,0o600)
def state():
 return json.loads(py('''import subprocess,json,pathlib,hashlib
c=json.loads(subprocess.check_output(['docker','inspect','grafana']))[0]
p=pathlib.Path('/opt/infra-grafana')
print(json.dumps({'identity':[c['Id'],c['State']['StartedAt'],c['RestartCount']], 'mounts':c['Mounts'], 'hashes':{str(f.relative_to(p)):hashlib.sha256(f.read_bytes()).hexdigest() for f in p.glob('config/**/*') if f.is_file()}}))'''))
def dashboards():
 return {x['uid']:api('/api/dashboards/uid/'+x['uid'])['dashboard'] for x in api('/api/search?type=dash-db')}
def baseline():
 assert not (PRIVATE/'baseline.json').exists(),'Do not overwrite existing baseline'
 assert api('/api/health')['database']=='ok'
 ds=api('/api/datasources');assert any(x['name']=='Prometheus' and x['url']=='http://192.168.1.110:9090' for x in ds)
 s=state();assert all(f not in s['hashes'] for f in FILES),'Fleet files already exist; inspect before adopting'
 before=dashboards();assert UID not in before
 archive=py('''import sqlite3,subprocess,json,pathlib,tarfile,io,sys,os
p=pathlib.Path('/opt/infra-grafana/.runtime/d052');p.mkdir(parents=True,exist_ok=False);os.chmod(p,0o700)
c=json.loads(subprocess.check_output(['docker','inspect','grafana']))[0]
v=next(m['Source'] for m in c['Mounts'] if m['Destination']=='/var/lib/grafana')
src=sqlite3.connect('file:'+v+'/grafana.db?mode=ro',uri=True);dst=sqlite3.connect(str(p/'grafana.db'));src.backup(dst);assert dst.execute('pragma integrity_check').fetchone()[0]=='ok';dst.close();src.close()
b=io.BytesIO()
with tarfile.open(fileobj=b,mode='w:gz') as a:
 a.add('/opt/infra-grafana/config',arcname='config');a.add('/opt/infra-grafana/docker-compose.yml',arcname='docker-compose.yml');a.add(p/'grafana.db',arcname='grafana.db')
body=b.getvalue();(p/'before.tar.gz').write_bytes(body);os.chmod(p/'before.tar.gz',0o600);os.chmod(p/'grafana.db',0o600);sys.stdout.buffer.write(body)
''')
 PRIVATE.mkdir(parents=True,exist_ok=True,mode=0o700);os.chmod(PRIVATE,0o700)
 (PRIVATE/'before.tar.gz').write_bytes(archive);os.chmod(PRIVATE/'before.tar.gz',0o600)
 assert py("import hashlib;print(hashlib.sha256(open('/opt/infra-grafana/.runtime/d052/before.tar.gz','rb').read()).hexdigest())").decode().strip()==digest(archive)
 staging=PRIVATE/'restore-check';staging.mkdir(mode=0o700)
 with tarfile.open(fileobj=io.BytesIO(archive)) as a:
  a.extractall(staging,filter='data')
 for f,h in s['hashes'].items():assert digest((staging/f).read_bytes())==h
 db=sqlite3.connect('file:'+str(staging/'grafana.db')+'?mode=ro',uri=True);assert db.execute('pragma integrity_check').fetchone()[0]=='ok';db.close()
 save('baseline.json',{'state':s,'dashboards':before,'datasources':ds,'backup_sha256':digest(archive),'time':time.time()})
 print('PASS: authenticated baseline; CT/offhost backup SHA256 and SQLite/config restore-check')
def desired():return {f:digest((ROOT/'services/infra-grafana'/f).read_bytes()) for f in FILES}
def verify():
 b=json.loads((PRIVATE/'baseline.json').read_text());now=state();exp=dict(b['state']['hashes']);exp.update(desired())
 assert now['identity']==b['state']['identity'],'Grafana identity changed'
 assert sorted(now['mounts'],key=lambda x:x['Destination'])==sorted(b['state']['mounts'],key=lambda x:x['Destination']),'Mount changes'
 assert now['hashes']==exp,('Unexpected config hashes',[k for k in set(now['hashes'])|set(exp) if now['hashes'].get(k)!=exp.get(k)])
 assert api('/api/datasources')==b['datasources'],'Datasource drift'
 current=dashboards()
 assert set(current)==set(b['dashboards'])|{UID},'Dashboard set differs'
 assert all({a:z for a,z in current[k].items() if a!='version'}=={a:z for a,z in v.items() if a!='version'} for k,v in b['dashboards'].items()),'Existing dashboard content changed'
 d=api('/api/dashboards/uid/'+UID);assert d['meta']['provisioned']
 source=json.loads((ROOT/'services/infra-grafana'/FILES[1]).read_text())
 for k in ['panels','templating','title','uid']:assert d['dashboard'][k]==source[k],('Provisioned dashboard differs',k)
 h=api('/api/datasources/uid/PBFA97CFB590B2093/health');assert h['status']=='OK','Datasource health'
 result={'timestamp_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'url':URL+d['meta']['url']+'?theme=dark','provisioned':True,'old_dashboards_preserved':len(b['dashboards']),'datasources_unchanged':True,'identity_unchanged':True,'mounts_unchanged':True,'files':desired(),'backup_sha256':b['backup_sha256'],'datasource_health':h['status'],'existing_dashboard_version_changes':{k:[v.get('version'),current[k].get('version')] for k,v in b['dashboards'].items() if v.get('version')!=current[k].get('version')}}
 (ROOT/'docs/roadmap/evidence/2026-11-07-d052-deployment.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
def apply():
 b=json.loads((PRIVATE/'baseline.json').read_text());s=state();assert s['identity']==b['state']['identity']
 expected=dict(b['state']['hashes']);expected.update(desired())
 if s['hashes']==expected:
  verify();after=state();assert after['hashes']==s['hashes'] and after['identity']==s['identity']
  proof={'timestamp_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'result':'PASS','execution_branch':'already_current_readonly_verify','configuration_writes':0,'provisioning_reloads':0,'restarts':0,'hashes_unchanged':True,'identity_unchanged':True}
  (ROOT/'docs/roadmap/evidence/2026-11-07-d052-idempotence.json').write_text(json.dumps(proof,indent=2)+'\n')
  print('IDEMPOTENT: zero writes, zero reloads, zero restarts');return
 previous=dict(b['state']['hashes'])
 if (PRIVATE/'applied.json').exists():previous.update(json.loads((PRIVATE/'applied.json').read_text())['files'])
 assert s['hashes']==previous,'Config drift: stop'
 prior={f:remote(['cat',BASE+f]) for f in FILES if f in s['hashes']}
 changed_files=[f for f in FILES if s['hashes'].get(f)!=desired()[f]]
 assert digest((PRIVATE/'before.tar.gz').read_bytes())==b['backup_sha256']
 try:
  for f in changed_files:
   remote(['mkdir','-p',str(Path(BASE+f).parent)])
   remote(['tee',BASE+f],(ROOT/'services/infra-grafana'/f).read_bytes())
   remote(['chmod','644',BASE+f])
  if FILES[0] in changed_files:assert api('/api/admin/provisioning/dashboards/reload',post=True)
  end=time.monotonic()+45
  while True:
   try:verify();break
   except urllib.error.HTTPError as e:
    assert e.code==404 and time.monotonic()<end;time.sleep(1)
   except AssertionError as e:
    assert e.args and isinstance(e.args[0],tuple) and e.args[0][0]=='Provisioned dashboard differs' and time.monotonic()<end;time.sleep(1)
  save('applied.json',{'time':time.time(),'files':desired()})
 except Exception:
  for f in changed_files:
   if f in prior:remote(['tee',BASE+f],prior[f])
   else:py(f'from pathlib import Path;Path({BASE+f!r}).unlink(missing_ok=True)')
  api('/api/admin/provisioning/dashboards/reload',post=True)
  assert state()['hashes']==previous,'Recovery hash mismatch'
  print('SAFETY ROLLBACK: previous files restored; inspect owned dashboard API state before retry')
  raise
def rollback():
 b=json.loads((PRIVATE/'baseline.json').read_text());s=state();expected=dict(b['state']['hashes']);expected.update(desired())
 assert all(s['hashes'].get(k)==v for k,v in b['state']['hashes'].items()),'Other config changed; stop rollback'
 for f in FILES:
  if f in s['hashes']:
   assert s['hashes'][f]==desired()[f],'Owned file drift; stop rollback'
   py(f'from pathlib import Path;Path({BASE+f!r}).unlink()')
 api('/api/admin/provisioning/dashboards/reload',post=True)
 # disableDeletion preserves the owned DB model; explicitly delete only this task UID.
 try:
  req=urllib.request.Request(URL+'/api/dashboards/uid/'+UID,headers=credentials(),method='DELETE')
  urllib.request.urlopen(req,timeout=30).read()
 except urllib.error.HTTPError as e:
  assert e.code==404,'Remove the owned dashboard only after unprovisioning; inspect API state'
 assert state()['hashes']==b['state']['hashes']
 print('ROLLBACK: original configuration restored; backups retained')
if __name__=='__main__':
 PRIVATE.mkdir(parents=True,exist_ok=True,mode=0o700)
 lock=(PRIVATE/'transaction.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 p=argparse.ArgumentParser();p.add_argument('action',choices=['baseline','apply','verify','rollback']);a=p.parse_args();globals()[a.action]()
