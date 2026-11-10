#!/usr/bin/env python3
"""D056: dedicated PVEAuditor identity + one central exporter; no existing restarts.
Never print credentials, raw subprocess errors or authentication responses.
"""
import re,argparse,fcntl,hashlib,importlib.util,io,json,os,shlex,subprocess,tarfile,time,urllib.parse,urllib.request
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[1]
PRIVATE=Path.home()/'.local/share/mailerblend-recovery/phase6/d056'
s=importlib.util.spec_from_file_location('stage_a',ROOT/'scripts/phase6-stage-a.py');t=importlib.util.module_from_spec(s);s.loader.exec_module(t)
EXPORTER=ROOT/'services/infra-pve-uptime';PVEPRIVATE='/var/lib/mailerblend-recovery/d056';USER='prometheus-uptime@pve';TOKEN='uptime'
FILES={610:'config/prometheus.yml',611:'config/provisioning/fleet-assets/proxmox-lxc-fleet.json'}
def digest(b):return hashlib.sha256(b).hexdigest()
def pve(code):
 r=subprocess.run(['ssh','-o','UserKnownHostsFile='+str(Path.home()/'.ssh/known_hosts'),'-o','StrictHostKeyChecking=yes','-o','BatchMode=yes','pve',shlex.join(['python3','-c',code])],capture_output=True,timeout=120)
 assert r.returncode==0,'PVE operation failed; sensitive output withheld'
 return r.stdout
def save(name,d):
 p=PRIVATE/name;p.parent.mkdir(parents=True,exist_ok=True,mode=0o700);p.write_text(json.dumps(d,indent=2)+'\n');os.chmod(p,0o600)
def baseline():
 assert not (PRIVATE/'baseline.json').exists(),'Baseline exists'
 b={'started':time.time(),'states':{},'targets':t.api('/api/v1/targets')['activeTargets'],'rules':t.api('/api/v1/rules'),'dashboards':t.g.dashboards(),'datasources':t.g.api('/api/datasources'),'backups':{}}
 for ct in FILES:
  b['states'][str(ct)]=t.state(ct)
  body=t.py(ct,f'''import pathlib,tarfile,io,sys,os
base=pathlib.Path({t.BASES[ct]!r});p=base/'.runtime/d056';p.mkdir(parents=True,exist_ok=False);os.chmod(p,0o700);stream=io.BytesIO()
with tarfile.open(fileobj=stream,mode='w:gz') as a:a.add(base/'config',arcname='config')
body=stream.getvalue();(p/'before.tar.gz').write_bytes(body);os.chmod(p/'before.tar.gz',0o600);sys.stdout.buffer.write(body)''')
  (PRIVATE/f'{ct}-before.tar.gz').write_bytes(body);os.chmod(PRIVATE/f'{ct}-before.tar.gz',0o600)
  check=t.py(ct,f'import hashlib;print(hashlib.sha256(open({t.BASES[ct]+"/.runtime/d056/before.tar.gz"!r},"rb").read()).hexdigest())').decode().strip();assert check==digest(body)
  dest=PRIVATE/'before'/str(ct);dest.mkdir(parents=True,mode=0o700)
  with tarfile.open(fileobj=io.BytesIO(body)) as a:a.extractall(dest,filter='data')
  assert all(digest((dest/f).read_bytes())==h for f,h in b['states'][str(ct)]['hashes'].items())
  b['backups'][str(ct)]=digest(body)
 # Read-only snapshot of all application identities on the five direct dependencies.
 b['apps']=t.app_identities();save('baseline.json',b);print('PASS current baseline + CT/offhost backups and restore-check')
def identity():
 code=r'''
import subprocess,json,pathlib,os,tarfile
U='prometheus-uptime@pve';T='uptime';P=pathlib.Path('/var/lib/mailerblend-recovery/d056');P.mkdir(parents=True,exist_ok=True);os.chmod(P,0o700)
def run(args):
 r=subprocess.run(args,capture_output=True,text=True)
 assert r.returncode==0,'PVE identity step failed; output withheld'
 return json.loads(r.stdout) if r.stdout.strip().startswith(('[','{')) else None
users=run(['pveum','user','list','--output-format','json'])
if not (P/'identity-created.json').exists():
 assert U not in [x['userid'] for x in users],'Existing identity not owned by this transaction'
 with tarfile.open(P/'auth-before.tar.gz','w:gz') as a:
  for name in ['user.cfg','priv/token.cfg']:
   f=pathlib.Path('/etc/pve')/name
   if f.exists():a.add(f,arcname=name)
 os.chmod(P/'auth-before.tar.gz',0o600)
 run(['pveum','user','add',U,'--enable','1','--comment','D056 Prometheus read-only PVE uptime'])
 result=run(['pveum','user','token','add',U,T,'--privsep','1','--output-format','json'])
 value=result['value'];fd=os.open(P/'pve_token',os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o400)
 with os.fdopen(fd,'w') as f:f.write(value+'\n')
 (P/'identity-created.json').write_text(json.dumps({'user':U,'token':T,'privsep':1}));os.chmod(P/'identity-created.json',0o600)
 run(['pveum','acl','modify','/','--users',U,'--roles','PVEAuditor','--propagate','1'])
 run(['pveum','acl','modify','/','--tokens',U+'!'+T,'--roles','PVEAuditor','--propagate','1'])
acl=run(['pveum','acl','list','--output-format','json']);own=[x for x in acl if x['ugid'] in [U,U+'!'+T]]
assert len(own)==2 and all(x['roleid']=='PVEAuditor' and x['path']=='/' and x['propagate']==1 for x in own),'Unexpected ACL'
tokens=run(['pveum','user','token','list',U,'--output-format','json']);assert len(tokens)==1 and tokens[0]['privsep']==1
user=run(['pveum','user','permissions',U,'--path','/','--output-format','json'])
token=run(['pveum','user','token','permissions',U,T,'--path','/','--output-format','json'])
roles=run(['pveum','role','list','--output-format','json']);role=next(x for x in roles if x['roleid']=='PVEAuditor');allowed=set(role['privs'].split(',')) if isinstance(role['privs'],str) else set(role['privs'])
for permissions in [user,token]:
 effective={k for values in permissions.values() for k,v in values.items() if v}
 assert effective and effective<=allowed and all(k.endswith('.Audit') for k in effective),'Permissions exceed read-only PVEAuditor'
print(json.dumps({'user':U,'token_id':U+'!'+T,'privsep':1,'acl':own,'user_effective':user,'token_effective':token,'read_only_verified':True}))
'''
 proof=json.loads(pve(code));save('permissions.json',proof)
 (ROOT/'docs/roadmap/evidence/2026-11-07-d056-permissions.json').write_text(json.dumps(proof,indent=2)+'\n');print('PASS exclusive PVEAuditor ACL and effective read-only user/token permissions; secret withheld')
def exporter():
 if (PRIVATE/'exporter-created.json').exists():
  marker=json.loads((PRIVATE/'exporter-created.json').read_text());assert marker['compose_sha256']==digest((EXPORTER/'compose/docker-compose.yml').read_bytes())
  for filename,h in marker.get('build_assets',{}).items():
   assert digest((EXPORTER/filename).read_bytes())==h
   assert t.py(610,f'import hashlib;print(hashlib.sha256(open({"/opt/infra-pve-uptime/"+filename!r},"rb").read()).hexdigest())').decode().strip()==h
  current=json.loads(t.py(610,"import subprocess,json;c=json.loads(subprocess.check_output(['docker','inspect','pve-uptime-exporter']))[0];print(json.dumps([c['Id'],c['State']['StartedAt'],c['RestartCount']]))"));assert current==marker['identity']
  print('IDEMPOTENT exporter unchanged; no pull/write/up/recreate');return
 assert json.loads((PRIVATE/'permissions.json').read_text())['read_only_verified']
 # Secrets travel only in captured memory and restrictive private files, never argv or public output.
 secret=pve(f'from pathlib import Path;import sys;sys.stdout.buffer.write(Path({PVEPRIVATE+"/pve_token"!r}).read_bytes())')
 if (PRIVATE/'pve_token').exists():assert (PRIVATE/'pve_token').read_bytes()==secret
 else:(PRIVATE/'pve_token').write_bytes(secret)
 os.chmod(PRIVATE/'pve_token',0o400)
 ca=pve('import pathlib,sys;sys.stdout.buffer.write(pathlib.Path("/etc/pve/pve-root-ca.pem").read_bytes())')
 compose=(EXPORTER/'compose/docker-compose.yml').read_bytes();base='/opt/infra-pve-uptime'
 for name,body,owner,mode in [('docker-compose.yml',compose,'root:root','644'),('.runtime/pve_token',secret,'65534:65534','400'),('.runtime/pve-root-ca.pem',ca,'root:root','444')]:
  t.remote(610,['mkdir','-p',str(Path(base+'/'+name).parent)])
  exists=json.loads(t.py(610,f'from pathlib import Path;import json,hashlib;p=Path({base+"/"+name!r});print(json.dumps(hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None))'))
  if exists is not None:assert exists==digest(body),'Unexpected exporter file drift'
  else:t.remote(610,['tee',base+'/'+name],body)
  t.remote(610,['chown',owner,base+'/'+name]);t.remote(610,['chmod',mode,base+'/'+name])
 t.remote(610,['chmod','700',base+'/.runtime'])
 # Validate TLS with the dedicated token, from the actual central host, before starting anything.
 proof=json.loads(t.py(610,r'''import ssl,urllib.request,json,pathlib,stat
base=pathlib.Path('/opt/infra-pve-uptime/.runtime');token=(base/'pve_token').read_text().strip();ctx=ssl.create_default_context(cafile=str(base/'pve-root-ca.pem'))
r=urllib.request.urlopen(urllib.request.Request('https://192.168.1.100:8006/api2/json/cluster/resources',headers={'Authorization':'PVEAPIToken=prometheus-uptime@pve!uptime='+token}),context=ctx,timeout=15)
d=json.load(r)['data'];print(json.dumps({'tls_verified':True,'api_read_status':r.status,'lxc_discovered':len([x for x in d if x.get('type')=='lxc']),'secret_mode':oct(stat.S_IMODE((base/'pve_token').stat().st_mode)),'token_readable_by_owner':(base/'pve_token').stat().st_uid==65534}))'''))
 assert proof['tls_verified'] and proof['api_read_status']==200 and proof['secret_mode']=='0o400'
 save('tls.json',proof)
 t.remote(610,['docker','compose','-f',base+'/docker-compose.yml','config','-q'])
 # Build only the new pinned Python/package runtime. Never restart an existing service.
 for filename in ['Dockerfile','requirements.lock']:t.remote(610,['tee',base+'/'+filename],(EXPORTER/filename).read_bytes())
 t.remote(610,['docker','build','-t','mailerblend/pve-uptime:3.11.0-py312-d056','-f',base+'/Dockerfile',base])
 t.remote(610,['docker','compose','-f',base+'/docker-compose.yml','up','-d','--no-deps','--pull','never','pve-exporter'])
 identity=json.loads(t.py(610,"import subprocess,json;c=json.loads(subprocess.check_output(['docker','inspect','pve-uptime-exporter']))[0];print(json.dumps([c['Id'],c['State']['StartedAt'],c['RestartCount']]))"))
 save('exporter-created.json',{'created':time.time(),'compose_sha256':digest(compose),'identity':identity,'build_assets':{name:digest((EXPORTER/name).read_bytes()) for name in ['Dockerfile','requirements.lock']}})
 print('PASS token API read/TLS; only the new pinned exporter service started')
def raw_metrics():
 return t.py(610,r'''import subprocess,json,urllib.request,sys
c=json.loads(subprocess.check_output(['docker','inspect','pve-uptime-exporter']))[0];ip=c['NetworkSettings']['Networks']['infra-prom_default']['IPAddress'];r=urllib.request.urlopen('http://'+ip+':9221/pve?target=192.168.1.100&cluster=1&node=0',timeout=20);sys.stdout.buffer.write(r.read())''')
def preflight():
 end=time.monotonic()+40
 while True:
  try:
   metrics=raw_metrics().decode();break
  except Exception:
   if time.monotonic()>end:raise
   time.sleep(2)
 samples=[line for line in metrics.splitlines() if line and not line.startswith('#')];uptime=[line for line in samples if line.startswith('pve_uptime_seconds{') and re.search(r'id="lxc/[0-9]+"',line)];assert len(uptime)>=17,'Missing LXC metrics'
 proof={'timestamp_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'lxc_uptime_series':len(uptime),'families':sorted(set(line.split('{',1)[0] for line in samples if line.split('{',1)[0] in ['pve_uptime_seconds','pve_guest_info','pve_up'])),'tls':json.loads((PRIVATE/'tls.json').read_text()),'source':'central exporter /pve'}
 assert len(proof['families'])==3
 (ROOT/'docs/roadmap/evidence/2026-11-07-d056-exporter.json').write_text(json.dumps(proof,indent=2)+'\n');print('PASS central non-root exporter: real LXC uptime/info/status metrics')
def prepare():
 b=json.loads((PRIVATE/'baseline.json').read_text())
 for ct in FILES:
  s=t.state(ct);expected_identity=dict(b['states'][str(ct)]['identity'])
  if ct==610:s['identity'].pop('/pve-uptime-exporter',None)
  assert s==b['states'][str(ct)],'Unexpected baseline drift'
 conf=yaml.safe_load((PRIVATE/'before/610'/FILES[610]).read_text());assert not any(j['job_name']=='pve_uptime' for j in conf['scrape_configs']);conf['scrape_configs'].append(yaml.safe_load((EXPORTER/'scrape.yml').read_text()))
 (PRIVATE/'candidate').mkdir(exist_ok=True);(PRIVATE/'candidate/prometheus.yml').write_text(yaml.safe_dump(conf,sort_keys=False))
 model=json.loads((ROOT/'services/infra-grafana'/FILES[611]).read_text());old=b['dashboards']['proxmox-lxc-fleet'];assert model['panels']!=old['panels'],'Uptime generator has not changed'
 (PRIVATE/'candidate/dashboard.json').write_text(json.dumps(model,indent=2,ensure_ascii=False)+'\n')
 import shutil
 staging=PRIVATE/'validation';shutil.copytree(PRIVATE/'before/610/config',staging/'config',dirs_exist_ok=True);p=staging/'config/prometheus.yml';p.write_text((PRIVATE/'candidate/prometheus.yml').read_text().replace('/etc/prometheus/',str(staging/'config')+'/'))
 pt=Path.home()/'.local/share/mailerblend-recovery/phase5/d050/promtool';r=subprocess.run([str(pt),'check','config',str(p)],capture_output=True);assert r.returncode==0,'promtool failed'
 save('validated.json',{'prometheus.yml':digest((PRIVATE/'candidate/prometheus.yml').read_bytes()),'dashboard.json':digest((PRIVATE/'candidate/dashboard.json').read_bytes())});print('PASS additive Prometheus candidate and updated IaC dashboard validated')
def verify():
 b=json.loads((PRIVATE/'baseline.json').read_text());targets=t.api('/api/v1/targets')['activeTargets'];old={(json.dumps(x['labels'],sort_keys=True),x['scrapeUrl']) for x in b['targets']};now={(json.dumps(x['labels'],sort_keys=True),x['scrapeUrl']) for x in targets};assert old<=now and len(now-old)==1,'Target set changed';assert all(x['health']=='up' for x in targets),'Target not UP'
 for ct in FILES:
  s=t.state(ct);before=b['states'][str(ct)];ids=dict(s['identity']);ids.pop('/pve-uptime-exporter',None);assert ids==before['identity'],'Existing container changed'
  expected=dict(before['hashes']);expected[FILES[ct]]=digest((PRIVATE/'candidate'/('prometheus.yml' if ct==610 else 'dashboard.json')).read_bytes());assert s['hashes']==expected,'Config drift'
 assert t.app_identities()==b['apps'],'Application drift'
 def defs(data):return [(r['name'],r['query'],r.get('duration'),r.get('labels'),r.get('annotations')) for group in data['groups'] for r in group['rules']]
 rules=t.api('/api/v1/rules');assert defs(rules)==defs(b['rules']) and all(r['health']=='ok' for x in rules['groups'] for r in x['rules'])
 assert not t.query('ALERTS{alertstate="firing"}')
 for job in ['node_exporter','cadvisor','blackbox']:assert int(float(t.query('count(up{job="'+job+'"} == 1)')[0]['value'][1]))==17
 assert all(float(x['value'][1])==1 for x in t.query('probe_success{job="blackbox"}'))
 dashboards=t.g.dashboards();assert set(dashboards)==set(b['dashboards'])
 for uid,model in b['dashboards'].items():
  if uid!='proxmox-lxc-fleet':assert dashboards[uid]==model,'Other dashboard changed'
 live=t.g.api('/api/dashboards/uid/proxmox-lxc-fleet');model=json.loads((PRIVATE/'candidate/dashboard.json').read_text());assert live['meta']['provisioned']
 for key in ['panels','templating']:assert live['dashboard'][key]==model[key],'Waiting for Grafana polling'
 assert t.g.api('/api/datasources')==b['datasources']
 table=next(p for p in model['panels'] if p['title'].startswith('LXC health'));expr=next(x['expr'] for x in table['targets'] if x['refId']=='J');uptimes=t.query(expr.replace('${lxc:regex}','.*').replace('${service:regex}','.*'));assert len(uptimes)==17 and len({x['metric']['ct_id'] for x in uptimes})==17 and all(float(x['value'][1])>0 for x in uptimes),'Uptime not ready'
 result={'timestamp_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'uptime_real_count':17,'uptime_values':uptimes,'old_targets_preserved':True,'old_container_identities_preserved':True,'apps_unchanged':True,'rules_unchanged':True,'unrelated_dashboards_preserved':7,'all_prior_exporters_probes_up':True,'firing':[]}
 (ROOT/'docs/roadmap/evidence/2026-11-07-d056-deployment.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS 17 real uptimes, all previous monitoring/rules/dashboards/apps preserved')
def apply():
 v=json.loads((PRIVATE/'validated.json').read_text())
 assert all(digest((PRIVATE/'candidate'/f).read_bytes())==h for f,h in v.items())
 b=json.loads((PRIVATE/'baseline.json').read_text());states={ct:t.state(ct) for ct in FILES};expected={}
 for ct in FILES:
  expected[ct]=dict(b['states'][str(ct)]['hashes']);expected[ct][FILES[ct]]=v['prometheus.yml' if ct==610 else 'dashboard.json']
 if all(states[ct]['hashes']==expected[ct] for ct in FILES):
  verify();save('idempotence.json',{'writes':0,'reloads':0,'existing_restarts':0,'exporter_recreated':False});print('IDEMPOTENT zero writes/reloads/restarts');return
 assert all(states[ct]['hashes']==b['states'][str(ct)]['hashes'] for ct in FILES),'Config drift before apply'
 try:
  for ct in [610,611]:t.remote(ct,['tee',t.BASES[ct]+'/'+FILES[ct]],(PRIVATE/'candidate'/('prometheus.yml' if ct==610 else 'dashboard.json')).read_bytes())
  t.reload(610)
  end=time.monotonic()+95
  while True:
   try:verify();break
   except AssertionError:
    if time.monotonic()>end:raise
    time.sleep(3)
  save('applied.json',{'time':time.time()})
 except Exception:
  for ct in FILES:t.remote(ct,['tee',t.BASES[ct]+'/'+FILES[ct]],(PRIVATE/'before'/str(ct)/FILES[ct]).read_bytes())
  t.reload(610);print('Safety rollback restored original Prometheus/Grafana files; dedicated exporter/identity retained for diagnosis');raise
if __name__=='__main__':
 PRIVATE.mkdir(parents=True,exist_ok=True,mode=0o700);os.chmod(PRIVATE,0o700);lock=(PRIVATE/'transaction.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 p=argparse.ArgumentParser();p.add_argument('action',choices=['baseline','identity','exporter','preflight','prepare','apply','verify']);args=p.parse_args();globals()[args.action]()
