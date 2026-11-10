#!/usr/bin/env python3
"""D044/D048: recover only selected CT614/615 Preview then serving from ACTIVE Compose.
Secrets and raw inspect/config/CLI output remain in private backups, never stdout.
"""
import argparse,hashlib,json,os,re,subprocess,tarfile,time,urllib.request,urllib.error,urllib.parse
from pathlib import Path
BASE=Path('/opt/infra-nucleoedge/docker-compose.yml')
OVERLAY=BASE.parent/'healthcheck.native.yml'
NAMES={'sgtm_preview':'infra-nucleoedge-sgtm_preview-1','sgtm':'infra-nucleoedge-sgtm-1'}
RECIPE=Path(__file__).resolve().parents[1]/'services/infra-nucleoedge/proposals/d043/healthcheck.native.yml'
CT=614
PROJECT='infra-nucleoedge'
PORTS={'sgtm_preview':8092,'sgtm':8091}
PUBLIC_BASE='https://edge.nucleotecnologico.es'
PREVIEW_HEALTH_PATH='/preview/healthz'
PREVIEW_ROUTING_HEADERS={}
PROBE_SERVICE='edge-nucleotecnologico-collect'
EXPECTED_PROBES=2
RUN_PREFIX='sgtm-614-d044-'
def configure_target(ct):
 global CT,BASE,OVERLAY,NAMES,PROJECT,PORTS,PUBLIC_BASE,PROBE_SERVICE,EXPECTED_PROBES,RUN_PREFIX,PREVIEW_HEALTH_PATH,PREVIEW_ROUTING_HEADERS
 assert ct in [614,615], 'Unapproved sGTM recovery target'
 CT=ct
 PROJECT='infra-nucleoedge' if ct==614 else 'infra-mailerblend-edge'
 BASE=Path('/opt')/PROJECT/'docker-compose.yml';OVERLAY=BASE.parent/'healthcheck.native.yml'
 NAMES=({'sgtm_preview':'infra-nucleoedge-sgtm_preview-1','sgtm':'infra-nucleoedge-sgtm-1'} if ct==614 else {'sgtm_preview':'mailerblend-sgtm-preview','sgtm':'mailerblend-sgtm-serving'})
 PORTS={'sgtm_preview':8092 if ct==614 else 18092,'sgtm':8091 if ct==614 else 18091}
 PUBLIC_BASE='https://edge.nucleotecnologico.es' if ct==614 else 'https://edge.mailerblend.com'
 PREVIEW_HEALTH_PATH='/preview/healthz' if ct==614 else '/gtm/healthz'
 PREVIEW_ROUTING_HEADERS={} if ct==614 else {'X-Gtm-Server-Preview':'1'}
 PROBE_SERVICE='edge-nucleotecnologico-collect' if ct==614 else 'edge-mailerblend-collect'
 EXPECTED_PROBES=2 if ct==614 else 1
 RUN_PREFIX='sgtm-614-d044-' if ct==614 else 'sgtm-615-d048-'
HOST_KEYS=['Memory','MemorySwap','MemoryReservation','NanoCpus','CpuPeriod','CpuQuota','CpuShares','CpusetCpus','PidsLimit','OomKillDisable','Privileged','ReadonlyRootfs','CapAdd','CapDrop','SecurityOpt','NetworkMode','PortBindings','Binds','Dns','DnsSearch','ExtraHosts','RestartPolicy']
class ProbeReadiness(AssertionError):
 pass

CONFIG_KEYS=['Image','Env','Entrypoint','Cmd','WorkingDir','User','ExposedPorts','StopSignal','Volumes']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,data):
 p=Path(p);p.write_text(json.dumps(data,indent=2)+'\n');p.chmod(0o600)
def cmd(args,here,timeout=180,input=None,include_stderr=False):
 r=subprocess.run(args,input=input,capture_output=True,text=True,timeout=timeout)
 with (here/'commands.private.log').open('a') as f:f.write(json.dumps({'command':args,'returncode':r.returncode})+'\n'+r.stdout+r.stderr+'\n')
 assert r.returncode==0,'Command failed; private output retained'
 return r.stdout+r.stderr if include_stderr else r.stdout
def inspect_all(here):
 ids=cmd(['docker','ps','-aq'],here).split()
 return {c['Name'].lstrip('/'):c for c in json.loads(cmd(['docker','inspect']+ids,here))}
def model(here,overlay=False):
 args=['docker','compose','--project-directory',str(BASE.parent),'-f',str(BASE)]
 if overlay:args+=['-f',str(OVERLAY)]
 return json.loads(cmd(args+['config','--format','json'],here))
def compose(here,services,force=False,original=False):
 args=['docker','compose','--project-name',PROJECT,'--project-directory',str(BASE.parent),'-f',str(BASE)]
 if not original:args+=['-f',str(OVERLAY)]
 args+=['up','-d','--no-deps','--no-build','--pull','never']
 if force:args+=['--force-recreate']
 return cmd(args+services,here,timeout=180)
def http(url,headers=None):
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers=headers or {}),timeout=8) as r:r.read(1024);return r.status
 except urllib.error.HTTPError as e:e.read(1024);return e.code
 except (OSError,ValueError):return None
def equivalent(old,new):
 for key in CONFIG_KEYS:
  a,b=old['Config'].get(key),new['Config'].get(key)
  if key=='Env':a,b=sorted(a or []),sorted(b or [])
  assert a==b,'Immutable service config drift: '+key
 for key in HOST_KEYS:
  a,b=old['HostConfig'].get(key),new['HostConfig'].get(key)
  if key in ['Dns','DnsSearch']:a,b=a or [],b or []
  assert a==b,'Host config drift: '+key
 def mounts(c):return sorted((m['Type'],m['Source'],m['Destination'],m['RW']) for m in c['Mounts'])
 assert mounts(old)==mounts(new),'Data/secret mounts drift'
 assert old['Image']==new['Image'],'Image changed'
 assert set(old['NetworkSettings']['Networks'])==set(new['NetworkSettings']['Networks']),'Networks changed'
def others_unchanged(old,new):
 names=set(old)-set(NAMES.values());assert set(new)-set(NAMES.values())==names,'Other container inventory changed'
 for n in names:
  a,b=old[n],new[n]
  assert a['Id']==b['Id'] and a['Image']==b['Image'] and a['State']['StartedAt']==b['State']['StartedAt'] and a['RestartCount']==b['RestartCount'] and a['State']['Running']==b['State']['Running'],'Other container drift'
def remote_action(action,here):
 state_path=here/'state.json';state=json.loads(state_path.read_text()) if state_path.exists() else {'steps':[]}
 if action=='snapshot':
  assert not state_path.exists() and BASE.is_file() and not OVERLAY.exists(),'Unexpected existing recovery/config state'
  all_before=inspect_all(here);assert all(all_before[n]['State']['Running'] for n in NAMES.values())
  before=model(here);assert set(before['services'])==set(NAMES),'Active Compose includes unexpected services'
  assert (here/'overlay.yml').read_text().count('/app/health_checker_bin.js')==2
  files=[BASE]+[p for p in [BASE.parent/'.env'] if p.is_file()]
  for n in NAMES:
   c=all_before[NAMES[n]];assert (c['Config'].get('Labels') or {}).get('com.docker.compose.project')==PROJECT
   image=json.loads(cmd(['docker','image','inspect',before['services'][n]['image']],here))[0]
   assert image['Id']==c['Image'],'Local image tag no longer matches running image'
   assert not c['Mounts'],'Unexpected application data mounts require a recovery review'
   assert c['Config']['Entrypoint'] and any('node' in x for x in c['Config']['Entrypoint'])
  save(here/'baseline.private.json',{'containers':all_before,'model':before,'file_hashes':{str(p):sha(p) for p in files}})
  for i,p in enumerate(files):(here/('source-'+str(i))).write_bytes(p.read_bytes());(here/('source-'+str(i))).chmod(0o600)
  ids=sorted({all_before[n]['Image'] for n in NAMES.values()});assert len(ids)==1,'Unexpected image mismatch between services'
  cmd(['docker','image','save','--output',str(here/'image-original.tar')]+ids,here,timeout=240)
  # Verify saved image content and all archive members before permitting changes.
  with tarfile.open(here/'image-original.tar') as a:
   for member in a:
    if member.isfile():assert len(a.extractfile(member).read())==member.size
   manifest=json.load(a.extractfile('manifest.json'));assert len(manifest)==1
   config=a.extractfile(manifest[0]['Config']).read();assert json.loads(config).get('config') is not None
   hashes={hashlib.sha256(a.extractfile(member).read()).hexdigest() for member in a if member.isfile()}
   assert ids[0].split(':')[1] in hashes,'Image digest not represented by saved archive'
  with tarfile.open(here/'backup.tar','w') as a:
   for p in [here/'baseline.private.json',here/'image-original.tar']+[here/('source-'+str(i)) for i in range(len(files))]:a.add(p,arcname=p.name)
  (here/'backup.tar').chmod(0o600)
  state.update(backup_sha256=sha(here/'backup.tar'),image_ids=ids,steps=['snapshot_verified'])
 elif action=='install':
  proof=json.loads((here/'external-backup-verified.json').read_text());assert proof['sha256']==state['backup_sha256'] and proof['offhost_verified']
  old=json.loads((here/'baseline.private.json').read_text());assert all(sha(p)==h for p,h in old['file_hashes'].items())
  OVERLAY.write_text((here/'overlay.yml').read_text());OVERLAY.chmod(0o600)
  candidate=model(here,True);prior=old['model']
  for n in NAMES:
   before=dict(prior['services'][n]);after=dict(candidate['services'][n]);before.pop('healthcheck',None);health=after.pop('healthcheck');assert before==after,'Candidate changes more than healthcheck'
   assert health['test']==['CMD','/nodejs/bin/node','/app/health_checker_bin.js']
  state['overlay_sha256']=sha(OVERLAY);state['current_attempt_services']=[];state['preview_accepted_current']=False;state['serving_accepted_current']=False;state['steps'].append('health_only_candidate_verified')
 elif action in ['apply-preview','apply-main']:
  service='sgtm_preview' if action=='apply-preview' else 'sgtm'
  assert 'health_only_candidate_verified' in state['steps']
  if service=='sgtm':assert state.get('preview_accepted_current') is True,'Current Preview acceptance required before serving'
  old=json.loads((here/'baseline.private.json').read_text());assert all(sha(p)==h for p,h in old['file_hashes'].items())
  assert sha(OVERLAY)==state['overlay_sha256']
  if service=='sgtm_preview':state['serving_id_before_preview']=inspect_all(here)[NAMES['sgtm']]['Id']
  state.setdefault('current_attempt_services',[]).append(service);state['attempted_service']=service;state['steps'].append(action+'_started');save(state_path,state)
  compose(here,[service],force=True);state['steps'].append(action+'_completed')
 elif action in ['check-preview','check-main']:
  service='sgtm_preview' if action=='check-preview' else 'sgtm';port=PORTS[service]
  old=json.loads((here/'baseline.private.json').read_text());end=time.monotonic()+150
  while True:
   current=inspect_all(here);c=current[NAMES[service]];equivalent(old['containers'][NAMES[service]],c);others_unchanged(old['containers'],current)
   if service=='sgtm_preview':assert current[NAMES['sgtm']]['Id']==state['serving_id_before_preview'],'Serving changed before Preview acceptance'
   public=PUBLIC_BASE+(PREVIEW_HEALTH_PATH if service=='sgtm_preview' else '/healthz')
   assert not c['State']['OOMKilled'] and c['RestartCount']==0,'New container unstable'
   if c['State']['Running'] and c['State'].get('Health',{}).get('Status')=='healthy' and http('http://127.0.0.1:'+str(port)+'/healthz')==200 and http(public,PREVIEW_ROUTING_HEADERS if service=='sgtm_preview' else None)==200:break
   assert time.monotonic()<end,'Native/public health readiness timeout';time.sleep(5)
  cmd(['docker','exec',NAMES[service],'/nodejs/bin/node','/app/health_checker_bin.js'],here,timeout=20)
  logs=cmd(['docker','logs','--tail','200',NAMES[service]],here,include_stderr=True)
  severe=['SyntaxError','ReferenceError','UnhandledPromiseRejection','uncaughtException','EADDRINUSE','Server failed to start','Error loading remote']
  assert not any(s.lower() in logs.lower() for s in severe),'Startup error; private logs retained'
  state[service]={'id':c['Id'],'image_id':c['Image'],'health':'healthy','local_healthz':200,'public_healthz':200,'restarts':0,'startup_errors':False}
  state['preview_accepted_current' if service=='sgtm_preview' else 'serving_accepted_current']=True
  state['steps'].append('preview_healthy' if service=='sgtm_preview' else 'serving_healthy')
 elif action=='idempotence':
  assert state.get('serving_accepted_current') is True;before=inspect_all(here);compose(here,list(NAMES));after=inspect_all(here)
  assert all(before[n]['Id']==after[n]['Id'] and before[n]['State']['StartedAt']==after[n]['State']['StartedAt'] for n in before),'Unnecessary service recreation'
  old=json.loads((here/'baseline.private.json').read_text());others_unchanged(old['containers'],after)
  state['idempotence_verified']=True;state['steps'].append('idempotence_verified')
 elif action=='verify-recovery':
  old=json.loads((here/'baseline.private.json').read_text());after=inspect_all(here)
  for n in NAMES:
   before=old['containers'][NAMES[n]];current=after[NAMES[n]];equivalent(before,current)
   assert current['State']['Running'] and current['Config']['Healthcheck']['Test']==before['Config']['Healthcheck']['Test']
  others_unchanged(old['containers'],after);assert all(sha(p)==h for p,h in old['file_hashes'].items())
  state['recovered_original_configuration']=True;state['steps'].append('original_configuration_restored_verified')
 elif action=='recover':
  old=json.loads((here/'baseline.private.json').read_text());assert all(sha(p)==h for p,h in old['file_hashes'].items())
  # Recreate only services that have already been attempted, restoring the active original Compose.
  attempted=state.get('current_attempt_services',[])
  assert all(s in NAMES for s in attempted)
  for service in attempted:compose(here,[service],force=True,original=True)
  after=inspect_all(here)
  for n in NAMES:equivalent(old['containers'][NAMES[n]],after[NAMES[n]]);assert after[NAMES[n]]['State']['Running']
  others_unchanged(old['containers'],after);state['recovered_original_configuration']=True;state['steps'].append('original_configuration_restored')
 elif action=='final':
  assert state.get('preview_accepted_current') and state.get('serving_accepted_current')
  old=json.loads((here/'baseline.private.json').read_text());current=inspect_all(here)
  for n in NAMES:equivalent(old['containers'][NAMES[n]],current[NAMES[n]]);assert current[NAMES[n]]['State']['Health']['Status']=='healthy'
  others_unchanged(old['containers'],current);assert all(sha(p)==h for p,h in old['file_hashes'].items());assert sha(OVERLAY)==state['overlay_sha256']
  save(here/'after.private.json',current);state['result']='DONE'
 else:raise ValueError('Unknown action')
 save(state_path,state)
 # Strictly sanitized output; never print raw models/config/env/logs/CLI exceptions.
 return {k:state[k] for k in ['steps','backup_sha256','image_ids','sgtm_preview','sgtm','overlay_sha256','idempotence_verified','recovered_original_configuration','result'] if k in state}

def local_execute(args):
 import importlib.util,shutil
 root=Path(__file__).resolve().parents[1]
 spec=importlib.util.spec_from_file_location('runner',root/'scripts/rollout-approved-exporters.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);ssh=module.SSH
 local=Path.home()/'.local/share/mailerblend-recovery'/('sgtm'+str(CT))/args.run;local.mkdir(mode=0o700,parents=True,exist_ok=args.resume)
 directory=str(BASE.parent/'.runtime'/args.run);pve='/mnt/storage/mailerblend-recovery/'+args.run
 result={'run':args.run,'started_at_utc':__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),'result':'IN_PROGRESS','steps':[]}
 def write():save(args.output,result)
 def remote(code,timeout=300):
  r=subprocess.run(ssh+['python3','-'],input=code,text=True,capture_output=True,timeout=timeout)
  with (local/'orchestrator.private.log').open('a') as f:f.write(r.stdout+r.stderr)
  assert r.returncode==0,'Remote step failed; private evidence retained'
  return r.stdout
 def ct(code):return 'import subprocess\nr=subprocess.run('+repr(['pct','exec',str(CT),'--','python3','-'])+',input='+repr(code)+',capture_output=True,text=True,timeout=550)\nprint(r.stdout,end="");assert r.returncode==0,"CT614 step failed; details private"'
 def action(name):
  invocation='import subprocess\nr=subprocess.run('+repr(['python3',directory+'/recover.py','--ct',str(CT),'--remote-action',name,'--directory',directory])+',capture_output=True,text=True,timeout=500)\nprint(r.stdout,end="");assert r.returncode==0,"Scoped service action failed"'
  data=json.loads(remote(ct(invocation),560));result['steps'].append(name);result['service_state']=data;write();print('CT'+str(CT),name,'PASS',flush=True);return data
 def guard():
  def get(path):
   with urllib.request.urlopen('http://192.168.1.110:9090'+path,timeout=10) as r:return json.load(r)
  for port in [9090,9093]:
   with urllib.request.urlopen('http://192.168.1.110:'+str(port)+'/-/ready',timeout=10) as r:assert r.status==200
  targets=get('/api/v1/targets')['data']['activeTargets'];counts={j:sum(t['labels']['job']==j and t['health']=='up' for t in targets) for j in ['node_exporter','cadvisor','blackbox']};assert counts=={'node_exporter':17,'cadvisor':17,'blackbox':11}
  def query(expr):return get('/api/v1/query?'+urllib.parse.urlencode({'query':expr}))['data']['result']
  probes=query('probe_success{service="'+PROBE_SERVICE+'"}');codes=query('probe_http_status_code{service="'+PROBE_SERVICE+'"}');timestamps=query('timestamp(probe_success{service="'+PROBE_SERVICE+'"})')
  if not (len(probes)==EXPECTED_PROBES and all(float(p['value'][1])==1 for p in probes) and len(codes)==EXPECTED_PROBES and all(float(p['value'][1]) in [200,204] for p in codes)):raise ProbeReadiness('Blackbox has not yet reported all expected successful probes')
  telemetry=module.telemetry()
  return {'targets_up':counts,'prometheus_alertmanager_ready':True,'blackbox_success':EXPECTED_PROBES,'blackbox_http_status':[int(float(p['value'][1])) for p in codes],'blackbox_sample_times':[float(p['value'][1]) for p in timestamps],'telegram':telemetry}
 def wait_monitoring():
  since=time.time();end=time.monotonic()+90;result['monitoring_transition_retries']=0
  while True:
   try:
    status=guard()
    assert status['telegram']['alertmanager_notifications_failed_total']==result['monitoring_before']['telegram']['alertmanager_notifications_failed_total'],'New Telegram error'
    if len(status['blackbox_sample_times'])==EXPECTED_PROBES and min(status['blackbox_sample_times'])>=since:return status
   except ProbeReadiness:
    result['monitoring_transition_retries']+=1;write()
   assert time.monotonic()<end,'Fresh successful Blackbox samples unavailable after startup deadline'
   time.sleep(5)
 def pve_state():
  probe="from pathlib import Path;import json,hashlib,subprocess;conf=dict(l.split(': ',1) for l in subprocess.check_output(['pct','config','614'],text=True).splitlines() if ': ' in l);p=Path('/sys/fs/cgroup/lxc/614');print(json.dumps({'resources':{k:conf.get(k) for k in ['hostname','cores','memory','swap','net0']},'events':dict(l.split() for l in (p/'memory.events').read_text().splitlines())}))"
  probe=probe.replace("'614'",repr(str(CT))).replace('lxc/614','lxc/'+str(CT))
  return json.loads(remote(probe))
 stage='preflight';attempted=False;staged=False;write()
 try:
  assert shutil.disk_usage(local).free>=2*1024**3
  result['monitoring_before']=guard();result['pve_before']=pve_state();write()
  if args.resume:
   prior=json.loads(args.resume_evidence.read_text());assert prior['run']==args.run and prior['backup']['offhost_verified']
   result['monitoring_before']=prior['monitoring_before'];result['pve_before']=prior['pve_before'];result['backup']=prior['backup'];result['resumed_after_safe_original_config_restore']=True
   assert sha(result['backup']['local_path'])==result['backup']['sha256']
   code='from pathlib import Path;import hashlib;expected='+repr(result['backup']['sha256'])+';assert hashlib.sha256(Path('+repr(result['backup']['pve_path'])+').read_bytes()).hexdigest()==expected\n'
   remote(code)
   # Preserve the original helper version; update only operational code in the private staging directory.
   code='from pathlib import Path;import hashlib\nd=Path('+repr(directory)+');p=d/"recover.py";old=p.read_bytes();v=d/("recover-previous-"+hashlib.sha256(old).hexdigest()[:12]+".py");v.write_bytes(old) if not v.exists() else None;v.chmod(0o600);p.write_text('+repr(Path(__file__).read_text())+');p.chmod(0o600)'
   remote(ct(code));action('verify-recovery');stage='install';action('install')
   stage='preview';attempted=True;action('apply-preview');action('check-preview')
   stage='serving';action('apply-main');action('check-main')
   stage='idempotence';action('idempotence')
   stage='monitoring';status=wait_monitoring()
   result['monitoring_after']=status;result['pve_after']=pve_state();assert result['pve_after']['resources']==result['pve_before']['resources']
   result['oom_deltas']={k:int(result['pve_after']['events'][k])-int(result['pve_before']['events'][k]) for k in ['oom','oom_kill','oom_group_kill']};assert not any(result['oom_deltas'].values())
   action('final');result.update(result='DONE',overlay_path=str(OVERLAY),no_image_pull_or_update=True,no_automatic_restarts_installed=True,duration_seconds=round(time.time()-__import__('datetime').datetime.fromisoformat(result['started_at_utc']).timestamp(),3));write();print(json.dumps({'result':'DONE','resumed':True,'service_state':result['service_state']}));return
  # TLS read-only bootstrap connectivity from the LXC, before restarting anything.
  code="import urllib.request;from pathlib import Path;import shutil;assert shutil.disk_usage('/').free>=2*1024**3\nwith urllib.request.urlopen('https://www.googletagmanager.com/static/serverjs/latest/server_bootstrap.js',timeout=12) as r:assert r.status==200 and r.read(64)\nd=Path("+repr(directory)+");assert not d.exists();d.mkdir(parents=True,mode=0o700)\n"
  code+='p=d/"recover.py";p.write_text('+repr(Path(__file__).read_text())+');p.chmod(0o600)\np=d/"overlay.yml";p.write_text('+repr(RECIPE.read_text())+');p.chmod(0o600)\n'
  remote(ct(code));staged=True
  stage='backup';snap=action('snapshot')
  # Second copy on PVE plus verified off-host copy; no service change before both hashes agree.
  code='from pathlib import Path\nimport subprocess,hashlib,json\nd=Path('+repr(pve)+');assert not d.exists();d.mkdir(mode=0o700)\nf=d/"backup.tar"\nr=subprocess.run('+repr(['pct','pull',str(CT),directory+'/backup.tar',pve+'/backup.tar'])+',capture_output=True);assert r.returncode==0;f.chmod(0o600)\nprint(json.dumps({"sha256":hashlib.sha256(f.read_bytes()).hexdigest(),"bytes":f.stat().st_size}))'
  info=json.loads(remote(code));assert info['sha256']==snap['backup_sha256']
  target=local/'backup.tar'
  with target.open('xb') as out:r=subprocess.run(ssh+['cat',pve+'/backup.tar'],stdout=out,stderr=subprocess.PIPE,timeout=180)
  target.chmod(0o600);assert r.returncode==0 and sha(target)==info['sha256']
  with tarfile.open(target) as a:
   for member in a:
    if member.isfile():assert len(a.extractfile(member).read())==member.size
  result['backup']={'local_path':str(target),'pve_path':pve+'/backup.tar','ct_path':directory+'/backup.tar','sha256':info['sha256'],'bytes':info['bytes'],'offhost_verified':True,'archive_readable':True};write()
  remote(ct('from pathlib import Path\np=Path('+repr(directory+'/external-backup-verified.json')+');p.write_text('+repr(json.dumps({'sha256':info['sha256'],'offhost_verified':True}))+');p.chmod(0o600)'))
  stage='install';action('install')
  stage='preview';attempted=True;action('apply-preview');action('check-preview')
  stage='serving';action('apply-main');action('check-main')
  stage='idempotence';action('idempotence')
  stage='monitoring';status=wait_monitoring()
  result['monitoring_after']=status;result['pve_after']=pve_state();assert result['pve_after']['resources']==result['pve_before']['resources']
  result['oom_deltas']={k:int(result['pve_after']['events'][k])-int(result['pve_before']['events'][k]) for k in ['oom','oom_kill','oom_group_kill']};assert not any(result['oom_deltas'].values())
  action('final');result.update(result='DONE',duration_seconds=round(time.time()-__import__('datetime').datetime.fromisoformat(result['started_at_utc']).timestamp(),3),overlay_path=str(OVERLAY),no_image_pull_or_update=True,no_automatic_restarts_installed=True);write()
 except BaseException as error:
  result.update(result='HALT',failed_stage=stage,failure_type=type(error).__name__);write()
  if attempted:
   try:result['recovery']=action('recover');result['recovery_monitoring']=guard();result['result']='ROLLED_BACK';write()
   except Exception as recovery_error:result['recovery_failure_type']=type(recovery_error).__name__;write()
  raise RuntimeError('Controlled intervention stopped; see sanitized result/private backup') from None
 print(json.dumps({'result':result['result'],'duration_seconds':result['duration_seconds'],'backup_verified':True,'preview':result['service_state']['sgtm_preview'],'serving':result['service_state']['sgtm'],'monitoring':result['monitoring_after']}))

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--ct',type=int,choices=[614,615],default=614);parser.add_argument('--remote-action',choices=['snapshot','install','apply-preview','check-preview','apply-main','check-main','idempotence','recover','verify-recovery','final']);parser.add_argument('--directory',type=Path);parser.add_argument('--run');parser.add_argument('--output',type=Path);parser.add_argument('--execute',action='store_true');parser.add_argument('--resume',action='store_true');parser.add_argument('--resume-evidence',type=Path);args=parser.parse_args();configure_target(args.ct);os.umask(0o077)
 if args.remote_action:
  import socket
  assert socket.gethostname()==PROJECT,'Wrong host'
  assert args.directory and args.directory.parent==BASE.parent/'.runtime' and re.fullmatch(re.escape(RUN_PREFIX)+r'[0-9TZ]+',args.directory.name)
  print(json.dumps(remote_action(args.remote_action,args.directory)))
 else:
  assert args.execute and args.run and re.fullmatch(re.escape(RUN_PREFIX)+r'[0-9TZ]+',args.run) and args.output and not args.output.exists()
  assert not args.resume or (args.resume_evidence and args.resume_evidence.is_file())
  local_execute(args)
if __name__=='__main__':main()
