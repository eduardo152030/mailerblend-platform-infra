#!/usr/bin/env python3
"""Incremental per-CT transaction; exports no secrets and never restarts monitoring."""
import hashlib,importlib.util,inspect,json,os,subprocess,tarfile,time
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[1]
def load(name):
 s=importlib.util.spec_from_file_location(name,ROOT/'scripts'/name);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def save(p,data):p.write_text(json.dumps(data,indent=2)+'\n');p.chmod(0o600)
class Transaction:
 def __init__(self,run,ct,here,lock_root=None):
  assert ct in [618,622,621,620,619,623,617,615,614,61211,611,616,610]
  self.ct=ct;self.run=run;self.here=here;self.lock_root=lock_root or here.parents[1];here.mkdir(mode=0o700,exist_ok=True)
  self.p=load('run-incremental-p0.py');self.p.HERE=here;self.p.CTDIR='/opt/infra-prom/.runtime/'+run+'-'+str(ct)
  original_helper=self.p.helper
  def serialized_helper(action):
   lock=load('monitoring-transaction-lock.py')
   with lock.monitoring_lock(self.lock_root,exclusive=True):return original_helper(action)
  self.p.helper=serialized_helper
  self.prep=load('prepare-incremental-monitoring.py');self.state={};self.folder='/mnt/storage/mailerblend-recovery/phase4/'+run+'/'+str(ct)+'/monitoring'
 def stage(self,files,manifest,initial=False):
  code='import pathlib\nd=pathlib.Path('+repr(self.p.CTDIR)+')\n'
  if initial:code+='assert not d.exists()\nd.mkdir(parents=True,mode=0o700)\n'
  payload={'manifest.json':json.dumps(manifest),**{'candidate/'+k:v for k,v in files.items()}}
  if initial:payload['apply.py']=(ROOT/'scripts/apply-incremental-config.py').read_text()
  for name,body in payload.items():code+='f=d/'+repr(name)+'\nf.parent.mkdir(parents=True,exist_ok=True)\nf.write_text('+repr(body)+')\nf.chmod('+('0o644' if name.startswith('candidate/') else '0o600')+')\n'
  code+='for f in (d/"candidate").rglob("*"):\n if f.is_dir():f.chmod(0o755)\n(d/"candidate").chmod(0o755)\n'
  self.p.remote(self.p.ct(code));self.manifest=manifest
 def prepare(self):
  subprocess.run(['python3',str(ROOT/'scripts/snapshot-incremental-monitoring.py'),'--output',str(self.here/'baseline.json')],check=True)
  self.baseline=json.loads((self.here/'baseline.json').read_text());self.registry=yaml.safe_load((ROOT/'services/common/exporter-migration.yml').read_text())
  files,manifest=self.prep.build(self.baseline,self.registry,self.prep.generator.load_services());self.stage(files,manifest,True)
  snap=json.loads(self.p.helper('snapshot'));self.state.update(snap)
  code='import pathlib,subprocess,hashlib\np=pathlib.Path('+repr(self.folder)+');p.mkdir(parents=True,mode=0o700,exist_ok=False)\nf=p/"integration-before.tar"\nr=subprocess.run(["pct","pull","610",'+repr(self.p.CTDIR+'/integration-before.tar')+',str(f)],capture_output=True);assert r.returncode==0\nf.chmod(0o600)\nprint(hashlib.sha256(f.read_bytes()).hexdigest())'
  assert self.p.remote(code).strip()==snap['sha256'];self.copy('integration-before.tar',snap['sha256'])
  self.p.remote(self.p.ct('import pathlib\np=pathlib.Path('+repr(self.p.CTDIR+'/backup-verified.json')+');p.write_text('+repr(json.dumps({'offhost_verified':True,'sha256':snap['sha256']}))+');p.chmod(0o600)'))
  self.p.helper('validate');self.state.update(offhost_verified=True);self.persist()
 def copy(self,name,expected):
  target=self.here/name;fd=os.open(target,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
  with os.fdopen(fd,'wb') as out:r=subprocess.run(self.p.SSH+['cat',self.folder+'/'+name],stdout=out,stderr=subprocess.PIPE,timeout=120)
  assert r.returncode==0 and hashlib.sha256(target.read_bytes()).hexdigest()==expected,'Monitoring external backup failure'
  with tarfile.open(target) as a:
   for member in a:
    if member.isfile():assert len(a.extractfile(member).read())==member.size
 def integrate(self,point,resume=False):
  if not resume:
   save(self.here/'cpu-point.json',point);s=json.loads(json.dumps(self.registry));s['cpu_contract_verified'][str(self.ct)]=str(self.here/'cpu-point.json');s['remaining_order'].remove(self.ct)
   files,manifest=self.prep.build(self.baseline,s,self.prep.generator.load_services());self.stage(files,manifest)
  self.p.helper('validate');self.p.helper('rules');self.p.helper('targets');self.wait_check();self.state['integrated']=True;self.persist()
 def wait_check(self):
  chain=load('check-incremental-chain.py');svcs={int(x['vmid']):x['name'] for x in self.prep.generator.load_services()};end=time.monotonic()+180
  while True:
   try:
    for ct in set(self.registry['prometheus_integrated'])|{self.ct}:
     d=chain.collect('http://192.168.1.110:9090',ct,svcs[ct]);assert not chain.assess(d),str(ct)+':'+','.join(chain.assess(d))
    t=self.p.get('http://192.168.1.110:9090','/api/v1/targets')['data']['activeTargets']
    for job,n in [('node_exporter',17),('cadvisor',17),('blackbox',11)]:assert len([x for x in t if x['labels']['job']==job])==n
    return
   except (AssertionError,OSError,ValueError):
    assert time.monotonic()<end,'Monitoring integration readiness timeout';time.sleep(3)
 def rollback(self):self.p.helper('rollback');self.state['rollback_verified']=True;self.persist()
 def idempotence(self):
  for action in ['rules','targets']:
   result=json.loads(self.p.helper(action));assert not result['changed'] and not result['reloaded']
  self.state['idempotence_verified']=True;self.persist()
 def rule(self,enabled):
  chain=load('check-incremental-chain.py');rule=chain.verification_rule(self.ct,self.run.replace('-','_')+'_'+str(self.ct),enabled)
  self.p.remote(self.p.ct('import pathlib\np=pathlib.Path('+repr(self.p.CTDIR+'/verification.yml')+');p.write_text('+repr(yaml.safe_dump(rule,allow_unicode=True,sort_keys=False))+');p.chmod(0o600)'))
  self.p.helper('test')
 def persist(self):save(self.here/'state.json',self.state)
 def after_archive(self):
  module=load('archive-r1-execution.py');selector='from pathlib import Path\nimport json\n'+inspect.getsource(module.select_configuration_paths)+'\nprint(json.dumps(select_configuration_paths(Path("/opt/infra-prom"))))'
  code='''import pathlib,subprocess,hashlib,json,os
r=subprocess.run(['pct','exec','610','--','python3','-c',SELECTOR],capture_output=True,text=True);assert r.returncode==0
f=pathlib.Path(FOLDER)/'integration-after.tar.gz'
fd=os.open(f,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
with os.fdopen(fd,'wb') as out:r=subprocess.run(['pct','exec','610','--','tar','-C','/opt/infra-prom','-czf','-']+json.loads(r.stdout),stdout=out,stderr=subprocess.PIPE,timeout=120)
assert r.returncode==0
print(json.dumps({'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bytes':f.stat().st_size}))
'''.replace('SELECTOR',repr(selector)).replace('FOLDER',repr(self.folder))
  info=json.loads(self.p.remote(code));self.copy('integration-after.tar.gz',info['sha256'])
  with tarfile.open(self.here/'integration-after.tar.gz') as a:
   for name,h in self.manifest['candidate_sha256'].items():assert hashlib.sha256(a.extractfile('config/'+name).read()).hexdigest()==h
  self.state['after_archive']=info|{'offhost_verified':True};self.persist()
