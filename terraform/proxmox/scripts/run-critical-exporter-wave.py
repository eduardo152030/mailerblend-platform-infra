#!/usr/bin/env python3
"""D039 scoped adaptation of proven exporter/Prometheus transactions; per-CT observation windows, no extra blocking watch."""
import argparse,ast,copy,hashlib,importlib.util,json,subprocess,time,threading,urllib.request
from pathlib import Path
from datetime import datetime,timezone
import yaml
ROOT=Path(__file__).resolve().parents[1]
ORDER=[618,622,611,616,610]
def load(name):
 s=importlib.util.spec_from_file_location(name,ROOT/'scripts'/name);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
base=load('rollout-approved-exporters.py');wave_tools=load('run-skip-exporter-wave.py')


def application_proof(r,audit):
 now=load('audit-critical-exporters.py').audit(r.ct)
 before={c['name']:c for c in audit['containers'] if not c['name'].startswith(('node_exporter','cadvisor'))}
 after={c['name']:c for c in now['containers'] if not c['name'].startswith(('node_exporter','cadvisor'))}
 assert before.keys()==after.keys(),'Application inventory changed'
 for n,c in before.items():
  assert all(c[k]==after[n][k] for k in ['id','image','started_at','running','restarts','oom_killed','config_hash']),'Application identity/config/resource regression'
  if c['health']=='healthy':assert after[n]['health']=='healthy','Application health regressed'
 assert now['allocation']==audit['allocation'],'LXC resources changed'
 if r.state.get('application_preflight',{}).get('ok') is True:assert wave_tools.application_working(r),'Application endpoint regression'
 return True


def verify_recovery_procedure(r):
 evidence=json.loads((ROOT/'docs/roadmap/evidence/2026-11-06-d037-completion.json').read_text())
 assert evidence['rollback_verified'] and evidence['idempotence_verified']
 old=Path.home()/'.local/share/mailerblend-recovery/phase4'/evidence['run']/'61211/bundle/pilot.py'
 def body(path,name):
  tree=ast.parse(path.read_text());node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name)
  # CT and held revision literals vary; the operations and guards must remain identical.
  class Normalize(ast.NodeTransformer):
   def visit_Constant(self,n):
    if isinstance(n.value,str):return ast.copy_location(ast.Constant('STRING'),n)
    return n
  return ast.dump(Normalize().visit(node),include_attributes=False)
 for name in ['rollback','stop','unchanged']:
  assert body(old,name)==body(r.here/'bundle/pilot.py',name),'Recovery mechanism changed; previous proof not applicable'
 state=json.loads((old.parent.parent/'monitoring/state.json').read_text());archive=old.parent.parent/'monitoring/integration-before.tar'
 assert base.digest(archive)==state['sha256'],'Historical recovery proof is not verified'
 r.state['recovery_procedure']={'available':True,'prior_real_rollback':'D037 CT61211','unchanged_operation_bodies':['rollback','stop','unchanged'],'current_backup_verified':True,'rehearsed_this_ct':False}


class ExternalWatch:
 """Local watchdog using PVE state and direct HTTP; never queries Prometheus APIs for its verdict."""
 def __init__(self,r,accepted):
  self.r=r;self.accepted=accepted;self.stop=threading.Event();self.rows=[];self.thread=threading.Thread(target=self.loop,daemon=True)
 def sample(self):
  ct=self.r.ct
  code="import subprocess,json\nassert subprocess.check_output(['pct','status','610'],text=True).strip()=='status: running'\nr=subprocess.run(['pct','exec','610','--','docker','inspect','prometheus','alertmanager'],capture_output=True,text=True);assert r.returncode==0\ncs=json.loads(r.stdout);print(json.dumps({c['Name']:{'id':c['Id'],'started_at':c['State']['StartedAt'],'running':c['State']['Running']} for c in cs}))"
  rr=subprocess.run(base.SSH+['python3','-'],input=code,text=True,capture_output=True,timeout=30);assert rr.returncode==0,'External PVE continuity check failed'
  identities=json.loads(rr.stdout);assert all(c['running'] for c in identities.values())
  if self.rows:assert identities==self.rows[0]['monitoring_identity'],'Monitoring process restarted'
  for url in ['http://192.168.1.110:9090/-/ready','http://192.168.1.110:9093/-/ready']:
   with urllib.request.urlopen(url,timeout=8) as res:assert res.status==200
  services=load('prepare-incremental-monitoring.py').generator.load_services()
  for cid in self.accepted:
   svc=next(s for s in services if int(s['vmid'])==cid)
   for port in [9100,8085]:
    with urllib.request.urlopen('http://'+svc['ip']+':'+str(port)+'/metrics',timeout=8) as res:assert res.status==200
  return {'observed_at_utc':datetime.now(timezone.utc).isoformat(),'ok':True,'monitoring_identity':identities,'direct_exporter_cts':self.accepted,'prometheus_api_dependency':False}
 def loop(self):
  while not self.stop.is_set():
   try:row=self.sample()
   except Exception as e:row={'observed_at_utc':datetime.now(timezone.utc).isoformat(),'ok':False,'failure_type':type(e).__name__}
   self.rows.append(row)
   with (self.r.here/'external-watch.jsonl').open('a') as f:f.write(json.dumps(row)+'\n')
   if self.stop.wait(30):break
 def start(self):
  row=self.sample();self.rows.append(row);base.save(self.r.here/'external-watch-initial.json',row);self.thread.start()
 def check(self):assert self.rows and all(r['ok'] for r in self.rows),'Independent external observation failed'
 def close(self):self.stop.set();self.thread.join(timeout=45);assert not self.thread.is_alive();self.check()


class CriticalRunner(base.Runner):
 def render_bundle(self):
  audit=dict(self.audit,deployment_revision=self.run)
  return load('prepare-aligned-exporters.py').render(self.here/'bundle',audit)
 def mutate(self):
  verify_recovery_procedure(self)
  self.namespace();self.helper('apply');self.helper('check');self.mark('apply_ready')
  self.monitor.integrate(self.point());self.mark('incremental_integration')
  first=self.identities();self.helper('apply');self.helper('check');assert self.identities()==first
  self.monitor.idempotence();self.state['exporters']=first;self.mark('idempotence')
 def observe(self,batch_end=False):
  # Snapshot at observation entry: future config changes cannot shorten an active window.
  window=load('phase4-validation-profiles.py').profile_for(self.ct,[self.ct])
  seconds=window['observation_seconds'];minimum=window['minimum_samples']
  self.manifest.update(initial_seconds=seconds,initial_minimum_samples=minimum)
  self.state['observation_policy']={'decision':'D-040','seconds':seconds,'minimum_samples':minimum,'frozen_at_observation_start':True}
  base.save(self.here/'state.json',self.state)
  if batch_end:
   self.observe_and_telegram();self.state['batch_delivery_verified']=True;return
  obs=load_observer(self)
  deadline=time.monotonic()+100
  while True:
   try:
    first=self.sample();initial=copy.deepcopy(first);initial['resources']['memory.events']=self.state['resources_before']['memory.events'];obs.validate(first,initial);break
   except AssertionError:
    assert time.monotonic()<deadline,'Initial metric validation failed';time.sleep(3)
  before=base.telemetry();start=time.monotonic();rows=[];previous=None
  with (self.here/'observations.jsonl').open('x') as out:
   while True:
    tick=time.monotonic();s=self.sample();obs.validate(s,initial,previous)
    assert base.telemetry()['alertmanager_notifications_failed_total']==before['alertmanager_notifications_failed_total'],'New Telegram error'
    if getattr(self,'external',None):self.external.check()
    s.update(checks_passed=True,elapsed_seconds=tick-start);out.write(json.dumps(s)+'\n');out.flush();rows.append(s);previous=s
    print('CT',self.ct,'sample',len(rows),'elapsed',round(s['elapsed_seconds']),flush=True)
    if s['elapsed_seconds']>=seconds and len(rows)>=minimum:break
    time.sleep(max(.1,30-(time.monotonic()-tick)))
  self.state['observation']={'samples':len(rows),'seconds':rows[-1]['elapsed_seconds'],'initial_seconds_required':seconds,'initial_minimum_samples':minimum,'sha256':base.digest(self.here/'observations.jsonl')}
  self.state['telegram']={'firing_and_resolved_accepted_by_api':False,'human_receipt_confirmed':False,'attempts_delta':0,'failures_delta':0,'delivery_test':'deferred_to_batch_end'}
  self.mark('observation_no_regression')

def load_observer(r):
 s=importlib.util.spec_from_file_location('critical_observer',r.here/'bundle/observe.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m


def run(args):
 policy=yaml.safe_load((ROOT/'services/common/phase4-execution-policy.yml').read_text());decision=policy['decision'];recovery_wave=decision=='D-041'
 order=[617,618,615,614] if recovery_wave else ORDER
 start_ct=args.start_ct if args.start_ct is not None else order[0]
 assert decision in ['D-039','D-041'] and policy['allowed_mutation_cts']==order[order.index(start_ct):] and policy['status']=='AUTHORIZED'
 if start_ct!=order[0]:
  proof=json.loads(args.isolation_evidence.read_text());assert proof['isolated_local_measurement'] and proof['state_safe_verified'] and proof['prior_coverage_unchanged'] and not proof['common_framework_defect_demonstrated']
  assert proof['ct']==order[order.index(start_ct)-1]
 root=Path.home()/'.local/share/mailerblend-recovery/phase4'/args.run;root.mkdir(mode=0o700,exist_ok=False)
 guarder=wave_tools.Wave(args.run,{'decision':decision},args.output);rows=[];halt=False;batch_success=[]
 def record():base.save(args.output,{'decision':decision,'run':args.run,'results':rows,'halt_global':halt,'observed_at_utc':datetime.now(timezone.utc).isoformat()})
 try:
  for ct in order[order.index(start_ct):]:
   prior_registry=yaml.safe_load((ROOT/'services/common/exporter-migration.yml').read_text())
   start=time.monotonic();stage='global_preflight';r=None;audit=None;before=None;external=None
   try:
    before=guarder.guard();audit=load('audit-critical-exporters.py').audit(ct)
    audit_path=root/('audit-'+str(ct)+'.json');base.save(audit_path,[audit])
    if ct==618:
     bud=next(c for c in audit['containers'] if c['name']=='budibase-app');assert bud['image_ref']=='budibase/budibase@sha256:5c5c995643132864ea017af2b838e35506b37977ea5c0f379c059d9cce1f0bfa'
     assert all(not c['running'] for c in audit['containers'] if c['name'] in ['budibase-worker','budibase-app-pre-recovery'])
    attempt_run=args.run[:-1]+str(ct)+'Z';ctroot=root.parent/attempt_run;ctroot.mkdir(mode=0o700,exist_ok=False)
    r=CriticalRunner(attempt_run,ct,ctroot);r.preflight_audit_path=audit_path
    stage='preflight';r.preflight();window=load('phase4-validation-profiles.py').profile_for(ct,order);assert r.manifest['initial_seconds']==window['observation_seconds'] and r.manifest['initial_minimum_samples']==window['minimum_samples']
    if ct==610:
     external=ExternalWatch(r,before['accepted']);r.external=external;external.start()
    stage='backup';r.prepare()
    stage='instrumentation';r.start_cpu_history();r.pull()
    stage='apply';r.mutate()
    stage='observe';r.observe(batch_end=(not recovery_wave and ct in [622,610]));application_proof(r,audit)
    if recovery_wave:r.state['telegram']['delivery_test']='Unchanged channel verified D039; no new delivery test; no new errors'
    if external:external.check()
    stage='finish';r.stop_cpu_history();r.finish();application_proof(r,audit)
    after=guarder.guard();assert ct==614 or after['legacy614']==before['legacy614'];assert after['telegram']['alertmanager_notifications_failed_total']==before['telegram']['alertmanager_notifications_failed_total']
    if external:external.close();external=None
    batch_success.append(ct)
    if not recovery_wave and ct in [622,610]:
     assert r.state.get('batch_delivery_verified')
     # Each member's source/integration was observed; the last member supplies batch delivery proof.
     for prior in batch_success:
      pp=ROOT/'docs/roadmap/evidence'/('2026-11-02-rollout-'+str(prior)+'.json');e=json.loads(pp.read_text());e['batch_telegram_delivery_evidence']={'ct':ct,'run':args.run,'attempts_delta':r.state['telegram']['attempts_delta'],'failures_delta':0};pp.write_text(json.dumps(e,indent=2)+'\n')
     batch_success=[]
    rows.append({'ct':ct,'result':'DONE','seconds':round(time.monotonic()-start,3),'observation':r.state['observation'],'rollback_rehearsed_this_ct':False,'backup_verified':True,'application_no_regression':True,'evidence':'docs/roadmap/evidence/2026-11-02-rollout-'+str(ct)+'.json'});record()
   except BaseException as exc:
    category='global';safe=False
    if r:
     r.state.update(result='BLOCKED',failed_stage=stage,failure_type=type(exc).__name__);base.save(r.here/'state.json',r.state)
     try:
      load('recover-approved-wave.py').recover(r,base)
      application_proof(r,audit)
      registry_path=ROOT/'services/common/exporter-migration.yml'
      current_registry=yaml.safe_load(registry_path.read_text())
      if ct in current_registry['prometheus_integrated'] and ct not in prior_registry['prometheus_integrated']:
       registry_path.write_text(yaml.safe_dump(prior_registry,sort_keys=False))
      current=guarder.guard();assert current['coverage']==before['coverage'] and current['config_hashes']==before['config_hashes']
      assert current['telegram']['alertmanager_notifications_failed_total']==before['telegram']['alertmanager_notifications_failed_total']
      safe=True
     except Exception as recovery_error:
      r.state['recovery_failure_type']=type(recovery_error).__name__;base.save(r.here/'state.json',r.state)
     if stage=='preflight' and r.state.get('application_preflight',{}).get('ok') is False:category='isolated_application'
    if external:
     try:external.close()
     except Exception:safe=False
    isolation=None
    if safe and stage=='observe':
     try:
      isolation=load('diagnose-critical-ram.py').diagnose(ct,r.run);isolation.update(state_safe_verified=True,prior_coverage_unchanged=True);base.save(r.here/'local-isolation.json',isolation);category='isolated_measurement'
     except Exception:pass
    isolated=category in ['isolated_application','isolated_measurement'] and safe
    rows.append({'ct':ct,'result':'BLOCKED' if isolated else 'HALT GLOBAL','stage':stage,'failure_type':type(exc).__name__,'state_safe_verified':safe,'seconds':round(time.monotonic()-start,3)});halt=not isolated;record()
    if halt:break
   # A CT-local HALT is kept in its private evidence; no global HALT is removed.
   # This adapter uses a distinct root per CT for continuation after verified recovery.
 finally:
  policy.update(status='BLOCKED' if halt else 'COMPLETED',allowed_mutation_cts=[],allowed_recovery_cts=[],prometheus_config_for_cts=[],automatic_rollout=False,reason=decision+' scoped wave closed; see current evidence')
  (ROOT/'services/common/phase4-execution-policy.yml').write_text(yaml.safe_dump(policy,sort_keys=False))
 print(json.dumps({'results':rows,'halt_global':halt}),flush=True)

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run',required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--execute',action='store_true');p.add_argument('--start-ct',type=int,choices=ORDER+[617,615,614],default=None);p.add_argument('--isolation-evidence',type=Path);a=p.parse_args();assert a.execute and not a.output.exists();run(a)
