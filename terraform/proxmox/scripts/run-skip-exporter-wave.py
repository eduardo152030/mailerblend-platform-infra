#!/usr/bin/env python3
"""Scoped sequential wave with D035 baseline-aware cases. Each CT keeps its HALT; advancement needs positive safety proof."""
import argparse
import ast
from datetime import datetime,timezone
import hashlib
import importlib.util
import json
import os
import re
from pathlib import Path
import subprocess
import time
import urllib.request
import yaml
ROOT=Path(__file__).resolve().parents[1]

def load(name):
 s=importlib.util.spec_from_file_location(name,ROOT/'scripts'/name);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def snapshot_ct(r):
 code='''import json,subprocess,hashlib
ids=subprocess.check_output(['docker','ps','-aq'],text=True).split();out={}
for c in json.loads(subprocess.check_output(['docker','inspect']+ids)):
 out[c['Name'].lstrip('/')]={'id':c['Id'],'image':c['Image'],'running':c['State']['Running'],'started_at':c['State']['StartedAt'],'restarts':c['RestartCount'],'oom_killed':c['State']['OOMKilled'],'config_hash':hashlib.sha256(json.dumps(c['Config'],sort_keys=True).encode()).hexdigest()}
print(json.dumps(out))
'''
 return json.loads(r.remote(r.ctcode(code)))

def original_proof(before,after):
 apps={n:c for n,c in before.items() if not n.startswith(('node_exporter','cadvisor'))}
 app_same=bool(apps) and all(after.get(n)==c for n,c in apps.items())
 original=all(n in after and all(after[n][k]==before[n][k] for k in ['id','image','restarts','oom_killed','config_hash']) and after[n]['running'] for n in ['node_exporter','cadvisor'])
 active={n for n,c in after.items() if c['running']}
 return original and app_same and active=={n for n,c in before.items() if c['running']}

def application_working(r):
 source=(r.here/'bundle/pilot.py').read_text();tree=ast.parse(source);function=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='application_probe')
 code='import json,subprocess,urllib.request,urllib.error\n'+ast.get_source_segment(source,function)+"\ntry:application_probe();print(json.dumps({'working':True}))\nexcept Exception as exc:print(json.dumps({'working':False,'failure_type':type(exc).__name__}))"
 return json.loads(r.remote(r.ctcode(code)))['working']

def require_application_working(r):
 if not application_working(r):raise RuntimeError('Application regressed after observation')
 return True

class Wave:
 def __init__(self,run,policy,output):
  self.m=load('rollout-approved-exporters.py');self.run=run;self.policy=policy;self.output=output;self.root=Path.home()/'.local/share/mailerblend-recovery/phase4'/('wave-'+run)
  self.root.mkdir(mode=0o700,exist_ok=False);self.guard_index=0;self.rows=[]
 def guard(self):
  path=self.root/('global-'+str(self.guard_index)+'.json');self.guard_index+=1
  subprocess.run(['python3',str(ROOT/'scripts/snapshot-incremental-monitoring.py'),'--output',str(path)],check=True,capture_output=True)
  baseline=json.loads(path.read_text());configs={n:hashlib.sha256(text.encode()).hexdigest() for n,text in baseline['files'].items()}
  chain=load('check-incremental-chain.py');base='http://192.168.1.110:9090';registry=yaml.safe_load((ROOT/'services/common/exporter-migration.yml').read_text());services=load('prepare-incremental-monitoring.py').generator.load_services()
  issues={ct:chain.assess(chain.collect(base,ct,next(s['name'] for s in services if int(s['vmid'])==ct))) for ct in registry['prometheus_integrated']}
  assert not any(issues.values()),'Accepted source degraded'
  targets=chain.fetch(base,'/api/v1/targets')['data']['activeTargets'];coverage=sorted((json.dumps(t['labels'],sort_keys=True),t['scrapeUrl'],t['health']) for t in targets)
  for job,count in [('node_exporter',17),('cadvisor',17),('blackbox',11)]:assert sum(t['labels']['job']==job and t['health']=='up' for t in targets)==count,'Prior target coverage lost'
  rules=chain.fetch(base,'/api/v1/rules')['data']['groups'];assert all(r['health']=='ok' for g in rules for r in g['rules'])
  for port in [9090,9093]:
   with urllib.request.urlopen('http://192.168.1.110:'+str(port)+'/-/ready',timeout=10) as response:assert response.status==200
  legacy={name:[g for g in json.loads(baseline['files'][name]) if g.get('labels',{}).get('service')=='infra-nucleoedge'] for name in ['targets/node-exporter.json','targets/cadvisor.json']}
  assert all(legacy.values()),'Legacy614 target missing'
  return {'config_hashes':configs,'coverage':coverage,'legacy614':legacy,'telegram':self.m.telemetry(),'accepted':list(registry['prometheus_integrated'])}
 def record(self,row):
  self.rows.append(row);self.m.save(self.output,{'run':self.run,'decision':self.policy['decision'],'results':self.rows,'halt_global':row['result']=='HALT GLOBAL','observed_at_utc':datetime.now(timezone.utc).isoformat()})
  if row['result']=='HALT GLOBAL':self.m.save(self.root/'HALT-GLOBAL.json',row)
 def attempt(self,ct):
  assert ct in self.policy['order'];self.m.execution_gate(ct)
  attempt_run=self.run[:-1]+str(ct)+'Z';private=Path.home()/'.local/share/mailerblend-recovery/phase4'/attempt_run;private.mkdir(mode=0o700,exist_ok=False)
  r=self.m.Runner(attempt_run,ct,private);r.preflight_audit_path=self.preflight_audit_path;stage='global_preflight';before=None;guard=None
  prior_registry=yaml.safe_load((ROOT/'services/common/exporter-migration.yml').read_text())
  try:
   guard=self.guard();assert self.prerequisite['critical_dependencies_verified'] is True,'Critical dependency verification missing'
   before=snapshot_ct(r);self.m.save(r.here/'originals-before.json',before)
   for stage,operation in [('preflight',r.preflight),('backup',r.prepare),('instrumentation',r.start_cpu_history),('images',r.pull),('apply_integration_rollback_idempotence',r.mutate),('observation_telegram',r.observe_and_telegram)]:
    operation()
    if stage=='preflight':assert r.manifest['initial_seconds']==self.policy['initial_seconds'] and r.manifest['initial_minimum_samples']==self.policy['initial_minimum_samples'] and 'memory_alignment' in r.manifest,'Common validation contract mismatch'
   # No registry promotion before the full synchronous watch.
   stage='watch';r.state['result']='PASS';self.m.save(r.here/'state.json',r.state)
   subprocess.run(['python3',str(ROOT/'scripts/watch-approved-exporters.py'),'--run',attempt_run,'--ct',str(ct),'--seconds',str(self.policy['watch_seconds'])],check=True)
   watch=json.loads((r.here/'post-watch-result.json').read_text());assert watch['result']=='PASS' and watch['seconds']>=900 and watch['samples']>=31
   stage='post_watch_application';require_application_working(r)
   stage='acceptance_archive';r.finish();after=self.guard();assert after['telegram']['alertmanager_notifications_failed_total']==guard['telegram']['alertmanager_notifications_failed_total']
   assert after['legacy614']==guard['legacy614'],'Deferred legacy614 coverage changed'
   require_application_working(r)
   return {'completed':True,'all_acceptance_gates':True,'initial_observation_pass':True,'watch_pass':True,'global_monitoring_healthy':True,'application_healthy_before':r.state['application_preflight']['ok'],'application_healthy_after':True,'critical_dependencies_verified':self.prerequisite['critical_dependencies_verified'],'run':attempt_run}
  except BaseException as exc:
   r.state.update(result='BLOCKED',failure_type=type(exc).__name__,failed_stage=stage);self.m.save(r.here/'state.json',r.state)
   category='unknown_state';isolated=False
   if stage=='preflight' and r.state.get('application_preflight',{}).get('ok') is False:category='application_preflight';isolated=True
   elif stage=='post_watch_application':category='application_regression';isolated=True
   elif stage=='backup':category='backup'
   elif stage in ['instrumentation','images','apply_integration_rollback_idempotence','acceptance_archive']:category='common_iac'
   elif stage in ['watch','observation_telegram']:category='validator' # Never infer exporter defect from validator exception alone.
   evidence={'completed':False,'category':category,'isolated':isolated,'run':attempt_run,'failed_stage':stage,'failure_type':type(exc).__name__}
   try:
    load('recover-approved-wave.py').recover(r,self.m);r.watch_mode=True
    after=snapshot_ct(r);self.m.save(r.here/'originals-after-recovery.json',after)
    # Promotion, if reached, belongs to this CT only; remove it after verified rollback.
    registry_path=ROOT/'services/common/exporter-migration.yml';current_registry=yaml.safe_load(registry_path.read_text())
    if ct in current_registry['prometheus_integrated'] and ct not in prior_registry['prometheus_integrated']:
     cleaned=json.loads(json.dumps(current_registry))
     for k in ['cpu_contract_verified','exporters_validated']:cleaned[k].pop(str(ct),None)
     for k in ['prometheus_integrated','telegram_chain_verified']:cleaned[k].remove(ct)
     cleaned['remaining_order']=list(prior_registry['remaining_order'])
     assert cleaned==json.loads(json.dumps(prior_registry)),'Registry drift during recovery'
     registry_path.write_text(yaml.safe_dump(prior_registry,sort_keys=False))
    current=self.guard()
    no_mutation=r.state.get('no_active_exporter_or_monitoring_changes') is True
    restored=original_proof(before,after) if before else False
    application=application_working(r) if (r.here/'bundle/pilot.py').exists() else False
    coverage=guard is not None and current['coverage']==guard['coverage'] and current['config_hashes']==guard['config_hashes'] and current['accepted']==guard['accepted']
    healthy=guard is not None and current['telegram']['alertmanager_notifications_failed_total']==guard['telegram']['alertmanager_notifications_failed_total']
    evidence.update(originals_verified=restored,application_working=application,prior_coverage_unchanged=coverage,global_monitoring_healthy=healthy,recovery_complete=no_mutation or r.state.get('safe_rollback_verified') is True,data_safe=restored,backups_recoverable=no_mutation or (r.monitor.state.get('offhost_verified') is True and self.m.digest(r.here/'exporters-before.tar')==r.state['backup']['sha256']),state=r.state['result'],no_active_changes=no_mutation,critical_dependencies_verified=self.prerequisite['critical_dependencies_verified'])
    if category=='application_regression':evidence.update(baseline_health_restored=application,regression_contained=restored and application and coverage and healthy)
    if category=='application_preflight' and no_mutation and before==after:
     evidence.update(category='pre_existing_application',preexisting_before_mutation=True,legacy_and_alerts_preserved=coverage)
   except BaseException as recovery_exc:evidence.update(category='rollback',recovery_complete=False,recovery_failure_type=type(recovery_exc).__name__)
   r.state['skip_evidence']=evidence;self.m.save(r.here/'state.json',r.state)
   return evidence

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run',required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--execute',action='store_true');p.add_argument('--prerequisite-evidence',type=Path,required=True);p.add_argument('--preflight-audit',type=Path,required=True);a=p.parse_args();assert a.execute and not a.output.exists() and re.fullmatch(r'integration-[0-9TZ]+',a.run);os.umask(0o077)
 policy=yaml.safe_load((ROOT/'services/common/phase4-skip-policy.yml').read_text());execution=yaml.safe_load((ROOT/'services/common/phase4-execution-policy.yml').read_text());assert execution['decision']==policy['decision'] and execution['status']=='AUTHORIZED' and policy['order']==[61211] and execution['allowed_mutation_cts']==policy['order']
 prerequisite=json.loads(a.prerequisite_evidence.read_text());assert prerequisite['decision']=='D-035' and prerequisite['ct614_case']=='B' and prerequisite['ct61211_independent_of_614'] is True and prerequisite['critical_dependencies_verified'] is True
 assert 0<=(datetime.now(timezone.utc)-datetime.fromisoformat(prerequisite['observed_at_utc'])).total_seconds()<=300,'Prerequisite proof stale'
 halted=True
 try:
  wave=Wave(a.run,policy,a.output);wave.prerequisite=prerequisite;wave.preflight_audit_path=a.preflight_audit
  guard=wave.guard();assert len(guard['accepted'])==8,'Unexpected acceptance baseline'
  deferred=dict(prerequisite,completed=False,category='pre_existing_application',isolated=True,prior_coverage_unchanged=True,legacy_and_alerts_preserved=True,global_monitoring_healthy=True,data_safe=True)
  decision=load('phase4-skip-policy.py').decide(deferred,policy);assert decision['result']=='BLOCKED / PRE-EXISTING ISSUE' and decision['continue']
  wave.record({'ct':614,'evidence':deferred,**decision})
  results=load('phase4-skip-policy.py').sequence(policy,wave.attempt,wave.record)
  halted=results[-1]['result']=='HALT GLOBAL';print(json.dumps({'run':a.run,'results':[{k:r[k] for k in ['ct','result','reason']} for r in results],'halt_global':halted}))
 finally:
  execution.update(status='BLOCKED' if halted else 'COMPLETED',automatic_rollout=False,allowed_mutation_cts=[],allowed_recovery_cts=[],prometheus_config_for_cts=[],reason='D035 wave closed; '+('global halt safety conditions unmet' if halted else 'scoped sequence complete')+'; no further CT execution authorized')
  (ROOT/'services/common/phase4-execution-policy.yml').write_text(yaml.safe_dump(execution,sort_keys=False))
 raise SystemExit(2 if halted else 0)

if __name__=='__main__':main()
