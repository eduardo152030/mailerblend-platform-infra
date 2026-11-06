#!/usr/bin/env python3
"""D025 sequential rollout. Only exporter mutations; a failed gate permanently halts this run."""
import argparse,ast,hashlib,importlib.util,inspect,json,os,re,subprocess,tarfile,time,traceback,urllib.request
from datetime import datetime,timezone
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[1]
ORDER=[621,620,619,623,617,615,614,61211,611,616,610]
EXCLUDED={618,622}
SSH=['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile='+str(Path.home()/'.ssh/known_hosts'),'-o','ConnectTimeout=10','-o','ServerAliveInterval=30','pve']
def load(name):
 s=importlib.util.spec_from_file_location(name,ROOT/'scripts'/name);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def save(path,data):path.write_text(json.dumps(data,indent=2)+'\n');path.chmod(0o600)
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def allowed(ct):
 if ct in [618,622]:
  policy=yaml.safe_load((ROOT/'services/common/phase4-execution-policy.yml').read_text())
  assert policy.get('decision') in ['D-039','D-041'] and ct in policy.get('allowed_mutation_cts',[]),'Critical target requires scoped D039 authorization'
  return
 assert ct in ORDER and ct not in EXCLUDED,'Unapproved target'
def execution_gate(ct,all_mode=False,recovery=False):
 policy=yaml.safe_load((ROOT/'services/common/phase4-execution-policy.yml').read_text())
 if recovery and ct in policy.get('allowed_recovery_cts',[]):return
 if policy['status']!='AUTHORIZED' or ct not in policy['allowed_mutation_cts'] or (all_mode and not policy['automatic_rollout']):
  raise RuntimeError('D-030: execution suspended; read PHASE4-HANDOFF and obtain new scope authorization')
def failed_observation(sample,exc):
 return dict(sample,checks_passed=False,failure_type=type(exc).__name__,private_failure_message=str(exc),private_traceback=traceback.format_exc())
def telemetry():
 p=load('run-incremental-p0.py');return {k:sum(float(x['value'][1]) for x in v) for k,v in p.telemetry().items()}
class Runner:
 def __init__(self,run,ct,root):
  allowed(ct);assert re.fullmatch(r'integration-[0-9TZ]+',run)
  self.ct=ct;self.run=run;self.root=root;self.here=root/str(ct);self.here.mkdir(mode=0o700,exist_ok=False)
  self.log=self.here/'private.log';self.log.touch(mode=0o600);self.directory='/opt/exporter-phase4-pilot/'+run+'-'+str(ct);self.folder='/mnt/storage/mailerblend-recovery/phase4/'+run+'/'+str(ct)
  self.start=time.monotonic();self.state={'ct':ct,'run':run,'result':'IN_PROGRESS','started_at_utc':datetime.now(timezone.utc).isoformat(),'steps':[],'timings_seconds':{}};self.previous=self.start
  self.monitor=load('progressive-monitoring-transaction.py').Transaction(run,ct,self.here/'monitoring');self.monitor.p.SSH=SSH
  original_remote=self.monitor.p.remote
  def guarded_remote(*args,**kwargs):
   assert not (self.root/'HALT.json').exists(),'Prior CT watch halted sequence'
   return original_remote(*args,**kwargs)
  self.monitor.p.remote=guarded_remote
 def remote(self,code,timeout=240):
  if not getattr(self,'watch_mode',False):assert not (self.root/'HALT.json').exists(),'Prior CT post-watch anomaly: halt sequence'
  r=subprocess.run(SSH+['python3','-'],input=code,text=True,capture_output=True,timeout=timeout)
  with self.log.open('a') as f:f.write(r.stdout+r.stderr)
  assert r.returncode==0,'Remote step failed; private evidence preserved'
  return r.stdout
 def ctcode(self,code):
  allowed(self.ct)
  return 'import subprocess\nr=subprocess.run('+repr(['pct','exec',str(self.ct),'--','python3','-'])+',input='+repr(code)+',capture_output=True,text=True,timeout=550)\nprint(r.stdout+r.stderr,end="");assert r.returncode==0,"CT step failed; stop (details private)"'
 def mark(self,name):
  now=time.monotonic();self.state['steps'].append(name);self.state['timings_seconds'][name]=round(now-self.previous,3);self.previous=now;save(self.here/'state.json',self.state);print('CT',self.ct,name,flush=True)
 def namespace(self,candidate=False):
  probe="import pathlib,subprocess,json;pid=subprocess.check_output(['pgrep','-xo','dockerd'],text=True).strip();d={'init':str(pathlib.Path('/proc/1/ns/cgroup').readlink()),'daemon':str((pathlib.Path('/proc')/pid/'ns/cgroup').readlink())};"+("c=json.loads(subprocess.check_output(['docker','inspect','cadvisor']))[0];d['candidate']=str((pathlib.Path('/proc')/str(c['State']['Pid'])/'ns/cgroup').readlink());" if candidate else '')+"print(json.dumps(d))"
  code='import pathlib,subprocess,json\npve=str(pathlib.Path("/proc/1/ns/cgroup").readlink())\nr=subprocess.run('+repr(['pct','exec',str(self.ct),'--','python3','-c',probe])+',capture_output=True,text=True);assert r.returncode==0\nd=json.loads(r.stdout);assert d["init"]==d["daemon"] and d["init"]!=pve\n'+('assert d["candidate"]==d["init"]\n' if candidate else '')+'print(json.dumps(d|{"pve":pve}))'
  self.state['namespaces']=json.loads(self.remote(code))
 def helper(self,action):
  if action in ['apply','rollback','revise-cadvisor','revise-node','snapshot']:execution_gate(self.ct,recovery=action=='rollback')
  cmd=['python3',self.directory+'/pilot.py',action,'--execute','--directory',self.directory,'--allow-containerd-socket','--use-lxc-cgroup-cpu']
  self.remote(self.ctcode('import subprocess\nr=subprocess.run('+repr(cmd)+',capture_output=True,text=True,timeout=420)\nprint(r.stdout+r.stderr,end="");assert r.returncode==0,"Exporter helper failed"'),560)
 def preflight(self):
  source=getattr(self,'preflight_audit_path',ROOT/'services/infra-prom/.runtime/autonomous-preflight-authenticated.json')
  rows=json.loads(source.read_text());self.audit=next(r for r in rows if r['ct']==self.ct)
  if self.ct in [617,61211]:
   assert hasattr(self,'preflight_audit_path'),'Reentry requires a fresh read-only audit'
   assert self.audit['mode']=='read-only' and 0<=(datetime.now(timezone.utc)-datetime.fromisoformat(self.audit['observed_at_utc'])).total_seconds()<=300,'Reentry audit stale'
  code='''import pathlib,subprocess,json,shutil,re
ct=CT
conf=dict(l.split(': ',1) for l in subprocess.check_output(['pct','config',str(ct)],text=True).splitlines() if ': ' in l)
assert subprocess.check_output(['pct','status',str(ct)],text=True).strip()=='status: running'
assert {k:conf.get(k) for k in ALLOCATION}==ALLOCATION
cg=pathlib.Path('/sys/fs/cgroup/lxc')/str(ct)
assert int((cg/'memory.max').read_text())==MEMORY
assert (cg/'cpu.max').read_text().split()[0]=='max','Quota not covered by existing contract'
mem=int(re.search(r'MemAvailable:\\s+(\\d+)',pathlib.Path('/proc/meminfo').read_text()).group(1));assert mem>=2*1024*1024
assert shutil.disk_usage('/mnt/storage').free>=2*1024**3
print(json.dumps({n:(cg/n).read_text().strip() for n in ['memory.events','memory.pressure','memory.current','memory.max','cpu.stat']}))
'''.replace('CT',str(self.ct)).replace('ALLOCATION',repr(self.audit['allocation'])).replace('MEMORY',str(int(self.audit['allocation']['memory'])*1024**2))
  self.state['resources_before']=json.loads(self.remote(code));assert all(float(x)<=5 for x in re.findall(r'avg(?:10|60)=(\S+)',self.state['resources_before']['memory.pressure']))
  assert __import__('shutil').disk_usage(self.root).free>=2*1024**3
  expected={c['name']:c['image'] for c in self.audit['containers']}
  probe='import subprocess,json\nids=subprocess.check_output(["docker","ps","-aq"],text=True).split();print(json.dumps({c["Name"].lstrip("/"):c["Image"] for c in json.loads(subprocess.check_output(["docker","inspect"]+ids))}))'
  actual=json.loads(self.remote(self.ctcode(probe)));assert actual==expected,'Application/exporter inventory or image drift since authenticated audit'
  self.namespace()
  self.manifest=self.render_bundle()
  source=(self.here/'bundle/pilot.py').read_text();tree=ast.parse(source);function=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='application_probe')
  probe='import json,subprocess,urllib.request,urllib.error\n'+ast.get_source_segment(source,function)+"\ntry:print(json.dumps({'ok':True,'checks':application_probe()}))\nexcept urllib.error.HTTPError as exc:print(json.dumps({'ok':False,'error_type':type(exc).__name__,'http_status':exc.code,'endpoint':exc.url}))\nexcept Exception as exc:print(json.dumps({'ok':False,'error_type':type(exc).__name__}))"
  self.state['application_preflight']=json.loads(self.remote(self.ctcode(probe)))
  if not self.state['application_preflight']['ok']:self.state['blocked_reason']={'stage':'application_preflight',**self.state['application_preflight']}
  assert self.state['application_preflight']['ok'],'Application preflight failed; no exporter changes permitted'
  self.mark('preflight')
 def render_bundle(self):
  if self.ct in [618,622,617,615,614,61211,611,616,610]:return load('prepare-aligned-exporters.py').render(self.here/'bundle',self.audit)
  return load('prepare-approved-exporters.py').render(self.ct,self.here/'bundle',self.audit)
 def prepare(self):
  if not getattr(self,'manifest',None):self.manifest=self.render_bundle()
  assert self.manifest.get('measurement_contract_schema')==1 and 'memory_alignment' in self.manifest,'Common CPU/RAM contract required before any staging'
  self.state['manifest']=self.manifest
  payload={n:(self.here/'bundle'/n).read_text() for n in self.manifest['file_sha256']}
  code='import pathlib,hashlib\np=pathlib.Path('+repr(self.directory)+');assert not p.exists();p.mkdir(parents=True,mode=0o700)\n'
  for n,body in payload.items():code+='f=p/'+repr(n)+';f.write_text('+repr(body)+');f.chmod('+('0o644' if n=='node-cgroup.sh' else '0o600')+');assert hashlib.sha256(f.read_bytes()).hexdigest()=='+repr(self.manifest['file_sha256'][n])+'\n'
  self.remote(self.ctcode(code));self.remote('import pathlib\np=pathlib.Path('+repr(self.folder)+');p.mkdir(parents=True,mode=0o700,exist_ok=False)')
  self.mark('staging');self.helper('snapshot');self.mark('image_archive_restore_and_snapshot')
  code='import pathlib,subprocess,hashlib,json,os\np=pathlib.Path('+repr(self.folder+'/exporters-before.tar')+');fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)\nwith os.fdopen(fd,"wb") as out:r=subprocess.run('+repr(['pct','exec',str(self.ct),'--','tar','-C',self.directory,'-cf','-','.'])+',stdout=out,stderr=subprocess.PIPE,timeout=180)\nassert r.returncode==0\nprint(json.dumps({"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"bytes":p.stat().st_size}))'
  self.state['backup']=json.loads(self.remote(code));target=self.here/'exporters-before.tar'
  with target.open('xb') as out:r=subprocess.run(SSH+['cat',self.folder+'/exporters-before.tar'],stdout=out,stderr=subprocess.PIPE,timeout=180)
  assert r.returncode==0 and digest(target)==self.state['backup']['sha256'],'External exporter backup failed'
  with tarfile.open(target) as archive:
   base=json.load(archive.extractfile('./baseline.json'))
   for n,info in base['archives'].items():
    h=hashlib.sha256();stream=archive.extractfile('./'+n)
    for b in iter(lambda:stream.read(1024*1024),b''):h.update(b)
    assert h.hexdigest()==info['sha256'],'Nested backup checksum failure'
  self.original=base;proof={'offhost_verified':True,'archives':base['archives'],'bundle_sha256':self.state['backup']['sha256']}
  self.remote(self.ctcode('import pathlib\np=pathlib.Path('+repr(self.directory+'/external-backup-verified.json')+');p.write_text('+repr(json.dumps(proof))+');p.chmod(0o600)'))
  self.mark('external_backup_verified');self.monitor.prepare();self.mark('monitoring_backup_verified')
 def pull(self):
  images=[self.manifest['node_image'],self.manifest['cadvisor_image']]
  code='import subprocess,json\nfor image in '+repr(images)+':\n r=subprocess.run(["docker","image","pull",image],capture_output=True,timeout=240);assert r.returncode==0,"Exact image pull failed"\n d=json.loads(subprocess.check_output(["docker","image","inspect",image]))[0];assert d["Architecture"]=="amd64" and image in d["RepoDigests"]\n'
  self.remote(self.ctcode(code),550);self.mark('pinned_images')
 def identities(self):
  return json.loads(self.remote(self.ctcode('import subprocess,json\nprint(json.dumps({n:{"id":c["Id"],"image":c["Image"],"started_at":c["State"]["StartedAt"],"restarts":c["RestartCount"]} for n in ["node_exporter","cadvisor"] for c in json.loads(subprocess.check_output(["docker","inspect",n]))}))')))
 def sample(self):
  probe='CPU_HISTORY_PATH='+repr(self.directory+'/cpu-history.jsonl')+'\n'+(self.here/'bundle/sample.py').read_text() if (self.here/'bundle/cpu-alignment.py').exists() else (self.here/'bundle/sample.py').read_text()
  code='''import pathlib,subprocess,json
root=pathlib.Path('/sys/fs/cgroup/lxc/CT')
def cg(p):return {n:(p/n).read_text().strip() for n in ['memory.current','memory.max','memory.swap.current','memory.events','memory.pressure','cpu.stat','cpu.max','cpuset.cpus.effective'] if (p/n).exists()}
r=subprocess.run(['pct','exec','CT','--','python3','-'],input=PROBE,capture_output=True,text=True,timeout=45)
if r.returncode:
 print(json.dumps({'probe_error':True,'ct_return_code':r.returncode,'ct_traceback':r.stderr}));raise SystemExit(0)
s=json.loads(r.stdout);s['resources']=cg(root)
for c in s['containers']:
 if c['running']:
  paths=list(root.rglob('docker-'+c['id']+'.scope')) or list(root.rglob(c['id']));assert len(paths)==1;c['cgroup']=cg(paths[0])
print(json.dumps(s))
'''.replace('CT',str(self.ct)).replace('PROBE',repr(probe))
  if getattr(self,'watch_mode',False):
   with load('monitoring-transaction-lock.py').monitoring_lock(self.root,exclusive=False):result=json.loads(self.remote(code,70))
  else:result=json.loads(self.remote(code,70))
  if result.get('probe_error'):
   lines=re.findall(r'line (\d+)',result.get('ct_traceback',''));raise RuntimeError('Read-only probe failed; private traceback retained; line '+(lines[-1] if lines else 'unknown'))
  return result
 def start_cpu_history(self):
  if not (self.here/'bundle/cpu-alignment.py').exists():return
  code='''from pathlib import Path
import subprocess,json
d=Path(DIRECTORY)
assert not (d/'cpu-history-process.json').exists()
assert not (d/'cpu-history.jsonl').exists()
log=(d/'cpu-history.private.log').open('xb')
process=subprocess.Popen(['python3',str(d/'cpu-alignment.py'),'--directory',str(d),'--names']+NAMES+['--seconds','2700'],stdin=subprocess.DEVNULL,stdout=log,stderr=log,start_new_session=True)
(d/'cpu-history-process.json').write_text(json.dumps({'pid':process.pid}))
print('Read-only CPU timeline started')
'''.replace('DIRECTORY',repr(self.directory)).replace('NAMES',repr(list(self.manifest['apps'])+['node_exporter','cadvisor']))
  self.remote(self.ctcode(code));self.mark('cpu_history_started')
  if (self.here/'bundle/memory-alignment.py').exists():self.memory_history_process(start=True)
 def memory_history_process(self,start):
  if not (self.here/'bundle/memory-alignment.py').exists():return
  code='''from pathlib import Path
import json,subprocess,os,signal
d=Path(DIRECTORY);marker=d/'memory-history-process.json';script=d/'memory-alignment.py'
if START:
 assert not marker.exists() and not (d/'memory-history.jsonl').exists()
 log=(d/'memory-history.private.log').open('xb')
 process=subprocess.Popen(['python3',str(script),'--directory',str(d),'--names']+NAMES+['--seconds','2700','--interval',str(INTERVAL)],stdin=subprocess.DEVNULL,stdout=log,stderr=log,start_new_session=True)
 marker.write_text(json.dumps({'pid':process.pid}));marker.chmod(0o600)
else:
 if marker.exists():
  pid=json.loads(marker.read_text())['pid'];p=Path('/proc')/str(pid)
  if p.exists():
   raw=(p/'cmdline').read_bytes()
   if raw:
    assert str(script).encode() in raw.split(bytes([0])),'RAM collector PID identity changed'
    os.kill(pid,signal.SIGTERM)
print('RAM collector lifecycle controlled; evidence retained')
'''.replace('DIRECTORY',repr(self.directory)).replace('START',repr(start)).replace('INTERVAL',repr(self.manifest.get('memory_alignment',{}).get('history_interval_seconds',.5)) if start else '.5').replace('NAMES',repr(list(self.manifest['apps'])+['node_exporter','cadvisor']) if start else '[]')
  self.remote(self.ctcode(code))

 def stop_cpu_history(self):
  if not (self.here/'bundle/cpu-alignment.py').exists():return
  code='''from pathlib import Path
import json,os,signal
d=Path(DIRECTORY);pid=json.loads((d/'cpu-history-process.json').read_text())['pid']
p=Path('/proc')/str(pid)
if p.exists():
 raw=(p/'cmdline').read_bytes()
 if raw:
  args=raw.split(bytes([0]))
  assert str(d/'cpu-alignment.py').encode() in args,'CPU collector PID identity changed'
  os.kill(pid,signal.SIGTERM)
print('Read-only CPU collector stopped; history retained')
'''.replace('DIRECTORY',repr(self.directory))
  self.remote(self.ctcode(code))
  self.memory_history_process(start=False)
 def point(self):
  self.namespace(True)
  # The source itself is checked before enabling its contract in Prometheus.
  code=r'''import urllib.request,re,time,json,pathlib
with urllib.request.urlopen('http://IP:9100/metrics',timeout=8) as r:text=r.read().decode()
def val(n):return float(re.search(r'^'+n+r'(?:\{[^}]*\})? (\S+)',text,re.M).group(1))
assert val('lxc_cpu_capacity_cores')==CORES and val('node_memory_MemTotal_bytes')==MEMORY
assert val('lxc_cpu_collector_success')==1 and -2<=time.time()-val('lxc_cpu_collector_timestamp_seconds')<=15
assert not re.search('^node_cpu_seconds_total',text,re.M)
cg=dict(x.split() for x in pathlib.Path('/sys/fs/cgroup/cpu.stat').read_text().splitlines());assert abs(val('lxc_cpu_usage_seconds_total')-int(cg['usage_usec'])/1e6)<=CORES*17
print(json.dumps({'ct':CT,'result':'PASS','cpu_source':'cgroup_v2_textfile','allocated_cores':CORES,'memory_total_bytes':MEMORY}))
'''.replace('IP',self.manifest['ip']).replace('CORES',str(self.manifest['cores'])).replace('MEMORY',str(self.manifest['memory_mib']*1024**2)).replace('CT',str(self.ct))
  return json.loads(self.remote(self.ctcode(code)))
 def mutate(self):
  self.namespace();self.helper('apply');self.helper('check');self.mark('apply_ready');point=self.point();self.monitor.integrate(point);self.mark('incremental_integration')
  first=self.identities();self.monitor.rollback();self.helper('rollback')
  code='''import json,subprocess,urllib.request,time
base=json.load(open(DIR+'/baseline.json'))
for name,c in base['exporters'].items():
 r=subprocess.run(['docker','inspect',name],capture_output=True,text=True)
 if c:
  now=json.loads(r.stdout)[0];assert now['Id']==c['Id'] and now['Image']==c['Image'] and now['State']['Running']
  wait_http('http://IP:'+str(9100 if name=='node_exporter' else 8085)+'/metrics')
 else:assert r.returncode!=0
'''.replace('DIR',repr(self.directory)).replace('IP',self.manifest['ip'])
  readiness=load('exporter-http-readiness.py');code='import time,urllib.request\n'+inspect.getsource(readiness.wait_http)+'\n'+code
  self.remote(self.ctcode(code));self.mark('coordinated_rollback')
  self.helper('apply');self.helper('check');self.namespace(True);self.monitor.integrate(self.point(),True)
  resumed=self.identities();assert all(first[n]['id']==resumed[n]['id'] for n in first)
  self.helper('apply');self.helper('check');assert self.identities()==resumed
  self.monitor.idempotence();self.state['exporters']=resumed;self.mark('resume_and_idempotence')
 def observe_and_telegram(self):
  import sys
  spec=importlib.util.spec_from_file_location('approved_observer',self.here/'bundle/observe.py');obs=importlib.util.module_from_spec(spec);spec.loader.exec_module(obs)
  end=time.monotonic()+100
  while True:
   try:initial=self.sample();initial['resources']['memory.events']=self.state['resources_before']['memory.events'];obs.validate(initial,initial);break
   except AssertionError:
    assert time.monotonic()<end,'Initial metric validation failed';time.sleep(3)
  save(self.here/'baseline-sample.json',initial)
  # Start exporter-backed Telegram test and overlap its routing waits with observation.
  before=telemetry();self.monitor.rule(True);test_start=time.monotonic();self.mark('controlled_firing_rule')
  seconds=self.manifest['initial_seconds'];minimum=self.manifest['initial_minimum_samples'];previous=None;samples=[];failed=None;extended_until=None;resolved=False;firing=False
  with (self.here/'observations.jsonl').open('x') as out:
   while True:
    tick=time.monotonic();elapsed=tick-test_start
    s={}
    try:
     s=self.sample();obs.validate(s,initial,previous);previous=s;s['checks_passed']=True
     now=telemetry();assert now['alertmanager_notifications_failed_total']==before['alertmanager_notifications_failed_total'],'New Telegram delivery error'
    except Exception as exc:
     s=failed_observation(s,exc);failed=type(exc).__name__;extended_until=extended_until or tick+600
    s['elapsed_seconds']=elapsed;out.write(json.dumps(s)+'\n');out.flush();samples.append(s)
    if not failed:
     p=self.monitor.p;alerts=p.get('http://192.168.1.110:9090','/api/v1/alerts')['data']['alerts'];test=[x for x in alerts if x['labels'].get('alertname')=='LxcCpuIntegrationVerification' and x['labels'].get('ct_id')==str(self.ct)]
     if any(x['state']=='firing' for x in test) and now['alertmanager_notifications_total']>=before['alertmanager_notifications_total']+1:
      firing=True
      if not resolved:self.monitor.rule(False);resolved=True
     if elapsed>=seconds and len(samples)>=minimum and firing and resolved and now['alertmanager_notifications_total']>=before['alertmanager_notifications_total']+2 and not test:break
     assert elapsed<=720,'Controlled delivery or observation timeout'
    elif time.monotonic()>=extended_until:
     self.state['failed_observation']={'result':'FAIL','samples':len(samples),'seconds':elapsed,'first_failure_seconds':next(s['elapsed_seconds'] for s in samples if not s['checks_passed']),'failed_samples':sum(not s['checks_passed'] for s in samples),'sha256':digest(self.here/'observations.jsonl')}
     save(self.here/'state.json',self.state)
     raise RuntimeError('Anomaly; extended600s evidence retained; sequence halted')
    time.sleep(max(.1,30-(time.monotonic()-tick)))
  self.monitor.p.helper('remove-test');self.monitor.state['test_removed']=True;self.monitor.state['telegram_attempts_delta']=now['alertmanager_notifications_total']-before['alertmanager_notifications_total'];self.monitor.state['telegram_failures_delta']=now['alertmanager_notifications_failed_total']-before['alertmanager_notifications_failed_total'];self.monitor.persist()
  self.state['observation']={'samples':len(samples),'seconds':samples[-1]['elapsed_seconds'],'initial_seconds_required':seconds,'initial_minimum_samples':minimum,'sha256':digest(self.here/'observations.jsonl'),'alert_high_cpu_for_runtime_proven':False}
  self.state['telegram']={'firing_and_resolved_accepted_by_api':True,'human_receipt_confirmed':False,'attempts_delta':self.monitor.state['telegram_attempts_delta'],'failures_delta':self.monitor.state['telegram_failures_delta']};self.mark('observation_and_telegram')
 def finish(self):
  self.helper('check');self.monitor.wait_check();self.monitor.after_archive()
  # Exporter post-config archive deliberately excludes unchanged image archives already verified.
  code='import pathlib,subprocess,hashlib,json,os\np=pathlib.Path('+repr(self.folder+'/exporters-after.tar.gz')+');fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)\nwith os.fdopen(fd,"wb") as out:r=subprocess.run('+repr(['pct','exec',str(self.ct),'--','tar','--exclude=original-*.tar','-C',self.directory,'-czf','-','.'])+',stdout=out,stderr=subprocess.PIPE,timeout=120)\nassert r.returncode==0\nprint(json.dumps({"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"bytes":p.stat().st_size}))'
  info=json.loads(self.remote(code));target=self.here/'exporters-after.tar.gz'
  with target.open('xb') as out:r=subprocess.run(SSH+['cat',self.folder+'/exporters-after.tar.gz'],stdout=out,stderr=subprocess.PIPE,timeout=120)
  assert r.returncode==0 and digest(target)==info['sha256'],'Post backup failed'
  with tarfile.open(target) as a:
   for n,h in self.manifest['file_sha256'].items():assert hashlib.sha256(a.extractfile('./'+n).read()).hexdigest()==h
   for item in a:
    if item.isfile():assert len(a.extractfile(item).read())==item.size
  self.state['after_archive']=info|{'offhost_verified':True};self.state['result']='PASS';self.state['duration_seconds']=round(time.monotonic()-self.start,3);self.mark('completed')
  public={k:self.state[k] for k in ['ct','run','result','duration_seconds','timings_seconds','observation','telegram','backup','after_archive','exporters','namespaces']};public.update(cpu_source='cgroup_v2_textfile',backup_external_verified=True,rollback_verified=self.monitor.state.get('rollback_verified',False),idempotence_verified=self.monitor.state.get('idempotence_verified',False))
  public.update(observed_at_utc=datetime.now(timezone.utc).isoformat(),decision=yaml.safe_load((ROOT/'services/common/phase4-execution-policy.yml').read_text())['decision'])
  if 'recovery_started_at_utc' in self.state:public['recovery_started_at_utc']=self.state['recovery_started_at_utc']
  if (self.here/'bundle/cpu-alignment.py').exists():
   rows=[json.loads(line) for line in (self.here/'observations.jsonl').read_text().splitlines()]
   intervals=[]
   for cid,first in rows[0]['cpu_alignment'].items():
    last=rows[-1]['cpu_alignment'][cid];dt=last['time']-first['time'];assert dt>0
    rates={field:(last[field]-first[field])/dt for field in ['cadvisor_seconds','docker_seconds','cgroup_seconds']}
    intervals.append({'id':cid,'name':first['name'],'first':first,'last':last,'window_seconds':dt,'rates_cores':rates,'percent_one_core':{k:100*v for k,v in rates.items()},'percent_allocated_lxc':{k:100*v/self.manifest['cores'] for k,v in rates.items()}})
   public['cpu_alignment_verification']={'threshold_unchanged':'max(1 CPU second, 3% reference counter); both timestamp bounds and delta windows','identity':'full Docker ID and StartedAt','no_missing_or_stale_timestamps':True,'containers':intervals}
  evidence=ROOT/'docs/roadmap/evidence'/('2026-11-02-rollout-'+str(self.ct)+'.json');evidence.write_text(json.dumps(public,indent=2)+'\n')
  registry=ROOT/'services/common/exporter-migration.yml';d=yaml.safe_load(registry.read_text());ref=str(evidence.relative_to(ROOT))
  for k in ['cpu_contract_verified','exporters_validated']:d[k][str(self.ct)]=ref
  for k in ['prometheus_integrated','telegram_chain_verified']:
   if self.ct not in d[k]:d[k].append(self.ct)
  d['remaining_order'].remove(self.ct);registry.write_text(yaml.safe_dump(d,sort_keys=False))
  load('report-approved-rollout.py').update(self.run)
  print('PASS CT',self.ct,'duration',self.state['duration_seconds'],'coverage',len(d['telegram_chain_verified']),'/17',flush=True)
 def execute(self):
  try:
   execution_gate(self.ct)
   self.preflight();self.prepare();self.start_cpu_history();self.pull();self.mutate();self.observe_and_telegram();self.finish()
  except BaseException as exc:
   self.state['result']='BLOCKED';self.state['failure_type']=type(exc).__name__;self.state['duration_seconds']=round(time.monotonic()-self.start,3) if hasattr(self,'start') else 0;save(self.here/'state.json',self.state);print('HALT CT',self.ct,type(exc).__name__,'private state retained; no further CT',flush=True)
   if self.ct in [617,615,614,61211]:
    api=__import__('types').SimpleNamespace(execution_gate=execution_gate,digest=digest,load=load,SSH=SSH,save=save)
    load('recover-approved-wave.py').recover(self,api)
   raise

def start_watch(run,ct,root):
 here=root/str(ct);marker=here/'watch-started.json'
 if marker.exists():return
 log=(here/'watch-driver.private.log').open('ab');os.chmod(here/'watch-driver.private.log',0o600)
 process=subprocess.Popen(['python3',str(ROOT/'scripts/watch-approved-exporters.py'),'--run',run,'--ct',str(ct)],stdin=subprocess.DEVNULL,stdout=log,stderr=log,start_new_session=True)
 log.close();save(marker,{'pid':process.pid,'watch_seconds':900})

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run',required=True);p.add_argument('--execute',action='store_true');p.add_argument('--preflight-audit',type=Path);group=p.add_mutually_exclusive_group(required=True);group.add_argument('--ct',type=int,choices=ORDER);group.add_argument('--all',action='store_true');a=p.parse_args();assert a.execute
 if a.preflight_audit:assert a.ct in [617,61211] and not a.all,'Fresh audit override is scoped to reviewed reentries'
 os.umask(0o077);root=Path.home()/'.local/share/mailerblend-recovery/phase4'/a.run;root.mkdir(parents=True,mode=0o700,exist_ok=True)
 while True:
  assert not (root/'HALT.json').exists(),'Post-watch halted sequence'
  registry=yaml.safe_load((ROOT/'services/common/exporter-migration.yml').read_text());pending=[c for c in ORDER if c not in registry['prometheus_integrated']]
  if not pending:break
  ct=pending[0];assert a.all or a.ct==ct,'Strict sequential gate; no repeats'
  if a.all and ct not in yaml.safe_load((ROOT/'services/common/phase4-execution-policy.yml').read_text())['allowed_mutation_cts']:
   print('Authorized wave complete; next CT',ct,'outside scope; no changes',flush=True);break
  execution_gate(ct,a.all)
  if ct==619 and not (root/'memory-transition-compat-applied.json').exists():subprocess.run(['python3',str(ROOT/'scripts/apply-memory-transition-compat.py'),'--run',a.run,'--execute'],check=True)
  if ct==611:subprocess.run(['python3',str(ROOT/'scripts/check-excluded-services.py'),'--baseline',str(ROOT/'services/infra-prom/.runtime/d025-excluded-baseline.json')],check=True)
  runner=Runner(a.run,ct,root)
  if a.preflight_audit:runner.preflight_audit_path=a.preflight_audit
  try:runner.execute()
  finally:load('report-approved-rollout.py').update(a.run)
  start_watch(a.run,ct,root)
  print('NEXT',pending[1] if len(pending)>1 else 'global validation',flush=True)
  if not a.all:break
if __name__=='__main__':main()
