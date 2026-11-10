#!/usr/bin/env python3
"""D051 targeted healthcheck repair. Preserve stopped originals, images, volumes and other containers.
Local actions: prepare/apply/verify NAME. Never invoke general deploy or Compose down.
"""
import argparse,copy,hashlib,io,json,os,shlex,subprocess,tarfile,time,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PRIVATE=Path.home()/'.local/share/mailerblend-recovery/healthchecks/d051'
TARGETS={'crm-api':618,'focalboard':622,'budibase-app':618}
RUN='d051'
REMOTE=Path('/opt/healthcheck-d051')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2)+'\n');p.chmod(0o600)
def call(args,log,timeout=180,input=None):
 r=subprocess.run(args,input=input,capture_output=True,timeout=timeout)
 with log.open('ab') as f:f.write(r.stdout+r.stderr+b'\n')
 assert r.returncode==0,'Command failed; details retained privately'
 return r.stdout

def inspect():
 return {c['Name'].lstrip('/'):c for c in json.loads(subprocess.check_output(['docker','inspect']+subprocess.check_output(['docker','ps','-aq']).decode().split()))}
def identity(c):return [c['Id'],c['Image'],c['State']['StartedAt'],c['RestartCount'],c['State']['Running']]
def invariant(old,new):
 for key in ['Env','Cmd','Entrypoint','WorkingDir','User','ExposedPorts','StopSignal','Volumes']:
  a,b=old['Config'].get(key),new['Config'].get(key)
  if key=='Env':a,b=sorted(a or []),sorted(b or [])
  assert a==b,'Application config changed: '+key
 keys=['Memory','MemorySwap','MemoryReservation','NanoCpus','CpuPeriod','CpuQuota','CpuShares','CpusetCpus','PidsLimit','OomKillDisable','Privileged','ReadonlyRootfs','CapAdd','CapDrop','SecurityOpt','NetworkMode','PortBindings','Dns','DnsSearch','ExtraHosts','RestartPolicy','LogConfig','Devices','GroupAdd','ShmSize','PidMode','IpcMode','Init']
 for k in keys:
  a,b=old['HostConfig'].get(k),new['HostConfig'].get(k)
  if k in ['Dns','DnsSearch','ExtraHosts','Devices','GroupAdd','SecurityOpt','Binds']:a,b=a or [],b or []
  if k=='Init':a,b=bool(a),bool(b)
  assert a==b,'Host config changed: '+k
 assert old['Image']==new['Image'],'Image changed'
 def mounts(c):return sorted((m['Type'],m['Source'],m['Destination'],m['RW'],m.get('Propagation','')) for m in c['Mounts'])
 assert mounts(old)==mounts(new),'Data/readonly mount identity changed'
 assert set(old['NetworkSettings']['Networks'])==set(new['NetworkSettings']['Networks']),'Network changed'
 assert not new['State'].get('OOMKilled'),'New OOM kill'
def others(before,after,name):
 accepted={}
 for peer in TARGETS:
  proof=REMOTE/peer/'applied.json';baseline=REMOTE/peer/'before.private.json'
  if peer!=name and proof.is_file() and baseline.is_file():
   state=json.loads(proof.read_text());prior=json.loads(baseline.read_text())['containers'][peer]
   assert peer in after and identity(after[peer])==state['identity'] and after[peer]['State']['Health']['Status']=='healthy','Accepted peer drift'
   invariant(prior,after[peer]);held=peer+'-'+RUN+'-original'
   assert held in after and after[held]['Id']==prior['Id'] and not after[held]['State']['Running']
   accepted[peer]=held
 for n,c in before.items():
  if n!=name and n not in accepted:assert n in after and identity(c)==identity(after[n]),'Other container changed: '+n
 assert set(after)-set(before) <= {name+'-'+RUN+'-original'}|set(accepted.values()),'Unexpected new container'
def archive(directory,files,dest):
 with tarfile.open(dest,'w') as a:
  for i,p in enumerate(files):a.add(p,arcname=str(i)+'-'+Path(p).name)
 dest.chmod(0o600)
def worker(action,name):
 assert name in TARGETS
 here=REMOTE/name;here.mkdir(parents=True,exist_ok=True,mode=0o700);here.chmod(0o700)
 log=here/'commands.private.log';beforefile=here/'before.private.json'
 def run(args,**kw):return call(args,log,**kw)
 def compose(*args):return run(['docker','compose','--project-name',RUN+'-'+name,'--project-directory',str(here),'-f',str(here/'compose.private.json')]+list(args))
 if action=='snapshot':
  assert not beforefile.exists(),'Baseline exists; do not overwrite'
  cs=inspect();c=cs[name];assert c['State']['Running']
  assert name+'-'+RUN+'-original' not in cs
  lab=c['Config']['Labels'];folder=Path(lab['com.docker.compose.project.working_dir']);files=[Path(p) for p in lab['com.docker.compose.project.config_files'].split(',')]
  args=['docker','compose','--project-name',lab['com.docker.compose.project'],'--project-directory',str(folder)]
  envfiles=[folder/n for n in ['.env','recovery.env'] if (folder/n).is_file()]
  for p in envfiles:args+=['--env-file',str(p)]
  for p in files:args+=['-f',str(p)]
  model=json.loads(run(args+['config','--format','json']));service=lab['com.docker.compose.service'];s=model['services'][service]
  image=json.loads(run(['docker','image','inspect',s['image']]))[0];assert image['Id']==c['Image'],'Source image tag drift'
  env=dict(v.split('=',1) for v in image['Config'].get('Env',[]));env.update({k:str(v) for k,v in s.get('environment',{}).items()})
  assert env==dict(v.split('=',1) for v in c['Config']['Env']),'Source env drift'
  assert set(s.get('networks',{}))==set(model.get('networks',{})) or all(n in model.get('networks',{}) for n in s.get('networks',{}))
  planned=copy.deepcopy(model);planned['name']=RUN+'-'+name;planned['services']={service:copy.deepcopy(s)}
  planned['services'][service].pop('depends_on',None)
  recipe=json.loads((here/'recipe.json').read_text());planned['services'][service]['healthcheck']=recipe
  # Same immutable image ID; no tag resolution or pull during apply.
  planned['services'][service]['image']=c['Image']
  planned['networks']={n:{'external':True,'name':model['networks'][n]['name']} for n in s.get('networks',{})}
  assert {x['name'] for x in planned['networks'].values()}==set(c['NetworkSettings']['Networks'])
  used={v['source'] for v in s.get('volumes',[]) if v['type']=='volume'}
  planned['volumes']={n:{'external':True,'name':model['volumes'][n]['name']} for n in used}
  assert {v['name'] for v in planned['volumes'].values()}=={m['Name'] for m in c['Mounts'] if m['Type']=='volume'}
  for v in s.get('volumes',[]):
   observed=next(m for m in c['Mounts'] if m['Destination']==v['target'])
   assert observed['RW']==(not v.get('read_only',False)),'Source mount permission drift'
   if v['type']=='bind':assert observed['Source']==v['source'],'Source bind path drift'
  # Protect literal dollar signs in rendered environment and healthcheck command.
  def escape(x):
   if isinstance(x,str):return x.replace('$','$$')
   if isinstance(x,list):return [escape(v) for v in x]
   if isinstance(x,dict):return {k:escape(v) for k,v in x.items()}
   return x
  save(here/'compose.private.json',escape(planned));normalized=json.loads(compose('config','--format','json'))
  assert normalized['services'][service]['environment']==s.get('environment',{}),'Candidate env interpolation drift'
  rendered_check=normalized['services'][service]['healthcheck'];rendered_check['test']=[v.replace('$$','$') for v in rendered_check['test']]
  assert rendered_check==recipe,'Healthcheck normalization drift'
  # Run candidate check inside the ORIGINAL running application before touching it.
  assert recipe['test'][0]=='CMD'
  run(['docker','exec',name]+recipe['test'][1:])
  inputs=files+envfiles;save(here/'before.private.json',{'containers':cs,'source_hashes':{str(p):sha(p) for p in inputs},'service':service,'planned':planned,'recipe':recipe,'compose_sha256':sha(here/'compose.private.json'),'created':time.time()})
  archive(here,inputs+[beforefile,here/'compose.private.json',here/'recipe.json'],here/'before.tar')
  print(json.dumps({'backup_sha256':sha(here/'before.tar'),'bytes':(here/'before.tar').stat().st_size,'candidate_check_passed_in_original':True,'source_env_image_and_networks_match':True}))
  return
 b=json.loads(beforefile.read_text());old=b['containers'][name];original=name+'-'+RUN+'-original'
 if action=='cold-backup':
  proof=json.loads((here/'verified.json').read_text());assert proof['config_sha256']==sha(here/'before.tar') and proof['config_offhost_restore_verified']
  current=inspect();assert identity(current[name])==identity(old);others(b['containers'],current,name)
  assert all(sha(p)==v for p,v in b['source_hashes'].items()),'Source drift'
  assert sha(here/'compose.private.json')==b['compose_sha256']
  # Stop gracefully without an eventual SIGKILL; preserve original container/image.
  run(['docker','stop','--time','-1',name],timeout=120)
  run(['docker','rename',name,original])
  data=[Path(m['Source']) for m in old['Mounts'] if m['Destination'] in ['/data','/opt/focalboard/data','/opt/focalboard/config.json']]
  try:
   archive(here,data,here/'data.tar')
   save(here/'cold.json',{'sha256':sha(here/'data.tar'),'sources':{str(p):p.exists() for p in data}})
  except Exception:
   run(['docker','rename',original,name]);run(['docker','start',name]);raise
  print(json.dumps({'data_sha256':sha(here/'data.tar'),'bytes':(here/'data.tar').stat().st_size,'original_stopped_preserved':True}))
  return
 def restore():
  current=inspect()
  if original not in current:
   assert name in current and current[name]['Id']==old['Id'],'Original not found for rollback'
   if not current[name]['State']['Running']:run(['docker','start',name])
   return
  if name in current:
   assert current[name]['Image']==old['Image'] and current[name]['Config']['Labels'].get('com.docker.compose.project')==RUN+'-'+name
   run(['docker','stop','--time','-1',name],timeout=120)
   rejected=name+'-'+RUN+'-rejected-'+str(int(time.time()));run(['docker','rename',name,rejected])
  run(['docker','rename',original,name]);run(['docker','start',name])
 if action=='rollback':restore();print('Original restored; candidate retained stopped');return
 assert action in ['apply','verify','adopt']
 proof=json.loads((here/'verified.json').read_text());assert proof.get('data_sha256')==sha(here/'data.tar') and proof.get('data_offhost_restore_verified')
 assert sha(here/'compose.private.json')==b['compose_sha256']
 if action=='apply':
  current=inspect();assert name not in current and not current[original]['State']['Running'] and current[original]['Id']==old['Id']
  for n,c in b['containers'].items():
   if n!=name:assert identity(current[n])==identity(c),'Dependency/other container changed'
  try:
   compose('up','-d','--no-deps','--no-build','--pull','never',b['service'])
   deadline=time.monotonic()+120
   while time.monotonic()<deadline:
    current=inspect();new=current[name];invariant(old,new);others(b['containers'],current,name)
    assert new['Config']['Healthcheck']['Test']==b['recipe']['test'],'Runtime healthcheck differs from recipe'
    assert not current[original]['State']['Running'],'Original running concurrently'
    if new['State'].get('Health',{}).get('Status')=='healthy':break
    time.sleep(2)
   else:raise RuntimeError('Healthcheck did not become healthy')
   initial=identity(new);compose('up','-d','--no-deps','--no-build','--pull','never',b['service'])
   current=inspect();assert identity(current[name])==initial,'Second application recreated/restarted target'
   invariant(old,current[name]);others(b['containers'],current,name)
   save(here/'applied.json',{'identity':initial,'healthy':True,'idempotent':True,'time':time.time()})
  except Exception:
   restore();raise
 current=inspect();new=current[name];invariant(old,new);others(b['containers'],current,name)
 if action=='adopt':
  initial=identity(new);compose('up','-d','--no-deps','--no-build','--pull','never',b['service']);current=inspect();new=current[name]
  assert identity(new)==initial,'Adoption idempotence failed'
  invariant(old,new);others(b['containers'],current,name)
  save(here/'applied.json',{'identity':initial,'healthy':True,'idempotent':True,'time':time.time(),'adopted_after_empty_dns_normalization':True})
 proof_applied=json.loads((here/'applied.json').read_text());assert proof_applied['idempotent'] and proof_applied['identity']==identity(new)
 assert new['State']['Health']['Status']=='healthy' and not current[original]['State']['Running']
 assert current[original]['Id']==old['Id']
 print(json.dumps({'name':name,'healthy':True,'image_id_unchanged':True,'env_resources_mounts_networks_unchanged':True,'other_containers_unchanged':True,'original_stopped_preserved':True,'idempotent':True,'id':new['Id']}))

def remote(ct,args,input=None):
 r=subprocess.run(['ssh','-o','UserKnownHostsFile='+str(Path.home()/'.ssh/known_hosts'),'-o','StrictHostKeyChecking=yes','-o','BatchMode=yes','pve',shlex.join(['pct','exec',str(ct),'--']+args)],input=input,capture_output=True,timeout=180)
 PRIVATE.mkdir(parents=True,exist_ok=True,mode=0o700);PRIVATE.chmod(0o700)
 with (PRIVATE/'transport.private.log').open('ab') as f:f.write(r.stderr+b'\n')
 assert r.returncode==0,'Remote action failed; private output retained; inspect before advancing'
 return r.stdout
def transfer_verified(ct,name,kind):
 body=remote(ct,['cat',str(REMOTE/name/(kind+'.tar'))]);path=PRIVATE/(name+'-'+kind+'.tar');path.write_bytes(body);path.chmod(0o600)
 expected=remote(ct,['sha256sum',str(REMOTE/name/(kind+'.tar'))]).decode().split()[0];assert sha(path)==expected
 dest=PRIVATE/(name+'-'+kind+'-restored');dest.mkdir(exist_ok=False,mode=0o700)
 with tarfile.open(path) as a:
  for entry in a:
   assert not Path(entry.name).is_absolute() and '..' not in Path(entry.name).parts and not entry.issym() and not entry.islnk(),'Unsafe archive link/path'
  a.extractall(dest,filter='data')
  for entry in a:
   if entry.isfile():assert hashlib.sha256(a.extractfile(entry).read()).hexdigest()==sha(dest/entry.name)
 return expected

def local(action,name):
 import importlib.util
 ct=TARGETS[name];here=REMOTE/name
 def run(a):return remote(ct,['python3',str(REMOTE/'worker.py'),'--run',RUN,'--worker',a,name])
 if action=='prepare':
  remote(ct,['mkdir','-p',str(here)]);remote(ct,['chmod','700',str(REMOTE),str(here)])
  remote(ct,['tee',str(REMOTE/'worker.py')],Path(__file__).read_bytes());remote(ct,['chmod','700',str(REMOTE/'worker.py')])
  spec=importlib.util.spec_from_file_location('recipes',ROOT/'scripts/generate-d051-healthchecks.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
  remote(ct,['tee',str(here/'recipe.json')],json.dumps(m.recipes()[name]).encode())
  result=json.loads(run('snapshot'));sha256=transfer_verified(ct,name,'before');assert sha256==result['backup_sha256']
  proof={'config_sha256':sha256,'config_offhost_restore_verified':True};save(PRIVATE/(name+'-verified.json'),proof)
  remote(ct,['tee',str(here/'verified.json')],json.dumps(proof).encode());print(json.dumps(result));return
 if action=='apply':
  try:
   result=json.loads(run('cold-backup'));sha256=transfer_verified(ct,name,'data');assert sha256==result['data_sha256']
   proof=json.loads((PRIVATE/(name+'-verified.json')).read_text());proof.update(data_sha256=sha256,data_offhost_restore_verified=True);save(PRIVATE/(name+'-verified.json'),proof)
   remote(ct,['tee',str(here/'verified.json')],json.dumps(proof).encode())
  except Exception:
   # If already stopped/renamed, recover original immediately; never leave an app down for a backup gate.
   try:print(run('rollback').decode())
   except Exception:print('Recovery requires inspection; no further target may advance')
   raise
  result=run('apply');save(PRIVATE/(name+'-result.json'),json.loads(result));print(result.decode());return
 if action in ['verify','rollback','adopt']:
  remote(ct,['tee',str(REMOTE/'worker.py')],Path(__file__).read_bytes())
  result=run(action);print(result.decode())
  if action!='rollback':save(PRIVATE/(name+'-result.json'),json.loads(result))
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--worker',action='store_true');p.add_argument('--run',choices=['d051','d051b'],default='d051');p.add_argument('action',choices=['prepare','snapshot','cold-backup','apply','verify','rollback','adopt']);p.add_argument('name',choices=list(TARGETS));a=p.parse_args()
 RUN=a.run
 if RUN!='d051':
  REMOTE=Path('/opt/healthcheck-'+RUN);PRIVATE=PRIVATE/('attempt-'+RUN)
 if a.worker:worker(a.action,a.name)
 else:local(a.action,a.name)
