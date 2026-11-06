#!/usr/bin/env python3
"""Resume D025 CT620 from verified rollback after a diagnosed validator race and clean600s watch."""
import argparse,hashlib,importlib.util,json,os,time
from datetime import datetime,timezone
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[1]
def load(n):
 s=importlib.util.spec_from_file_location(n,ROOT/'scripts'/n);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def resolution_gate(root):
 state=json.loads((root/'620/state.json').read_text());local_resume=state['result']=='IN_PROGRESS' and state['steps'][-1]=='validator_fix_clean600_verified';assert (state['result']=='BLOCKED_ROLLED_BACK' or local_resume) and state['safe_rollback_verified']
 clean=json.loads((root/'621/post-watch-serialized-check-result.json').read_text());assert clean['result']=='PASS' and clean['seconds']>=600 and clean['samples']>=21,'Clean extended watch required'
 diag=json.loads((ROOT/'docs/roadmap/evidence/2026-11-02-rule-transition-diagnosis.json').read_text());assert diag['unknown_health_observed'] and not diag['bad_health_observed'] and diag['telegram_failures_delta']==0 and diag['rule_removed']
 marker=root/'HALT.json'
 if local_resume:
  assert not marker.exists(),'New HALT must not be overwritten';marker=root/'HALT.validator-race-resolved.json'
 original=json.loads(marker.read_text());assert original['ct']==621 and original['reason']=='post_watch_anomaly'
 return state,hashlib.sha256(marker.read_bytes()).hexdigest()

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run',required=True);p.add_argument('--execute',action='store_true');a=p.parse_args();assert a.execute;os.umask(0o077)
 m=load('rollout-approved-exporters.py');root=Path.home()/'.local/share/mailerblend-recovery/phase4'/a.run;state,marker_hash=resolution_gate(root);here=root/'620'
 assert m.digest(here/'exporters-before.tar')==state['backup']['sha256']
 chain=load('check-incremental-chain.py')
 for ct,svc in [(624,'infra-journal-web'),(626,'infra-journal-api'),(625,'infra-journal-db'),(613,'infra-hola'),(621,'infra-project-gestion')]:assert not chain.assess(chain.collect('http://192.168.1.110:9090',ct,svc))
 r=object.__new__(m.Runner);r.ct=620;r.run=a.run;r.root=root;r.here=here;r.log=here/'private.log';r.directory='/opt/exporter-phase4-pilot/'+a.run+'-620';r.folder='/mnt/storage/mailerblend-recovery/phase4/'+a.run+'/620';r.state=state;r.start=time.monotonic()-(datetime.now(timezone.utc)-datetime.fromisoformat(state['started_at_utc'])).total_seconds();r.previous=time.monotonic();r.manifest=state['manifest'];r.manifest['initial_seconds']=600;r.manifest['initial_minimum_samples']=21
 for name,h in r.manifest['file_sha256'].items():assert hashlib.sha256((here/'bundle'/name).read_bytes()).hexdigest()==h
 r.monitor=load('progressive-monitoring-transaction.py').Transaction(a.run,620,here/'monitoring');r.monitor.p.SSH=m.SSH;r.monitor.baseline=json.loads((here/'monitoring/baseline.json').read_text());r.monitor.registry=yaml.safe_load((ROOT/'services/common/exporter-migration.yml').read_text());r.monitor.state=json.loads((here/'monitoring/state.json').read_text())
 assert r.monitor.state['offhost_verified']
 r.monitor.manifest=json.loads(r.monitor.p.remote(r.monitor.p.ct('import pathlib\nprint((pathlib.Path('+repr(r.monitor.p.CTDIR)+')/"manifest.json").read_text())')))
 archived=root/'HALT.validator-race-resolved.json'
 if not archived.exists():os.rename(root/'HALT.json',archived)
 else:assert hashlib.sha256(archived.read_bytes()).hexdigest()==marker_hash and not (root/'HALT.json').exists()
 m.save(root/'validator-race-resolution.json',{'original_marker_sha256':marker_hash,'original_marker_preserved':True,'clean_observation_seconds':600,'synchronization':'shared/exclusive post-watch versus planned reload/readiness','authorization':'D025 correction inside approved exporter rollout; no new privileges or application changes'})
 r.state['result']='IN_PROGRESS';r.mark('validator_fix_clean600_verified');load('report-approved-rollout.py').update(a.run)
 try:
  r.namespace();r.helper('apply');r.helper('check');r.namespace(True);r.monitor.integrate(r.point());first=r.identities()
  r.helper('apply');r.helper('check');assert r.identities()==first;r.monitor.idempotence();r.state['exporters']=first;r.mark('resume_idempotent_existing_candidates')
  r.observe_and_telegram();r.finish();m.start_watch(a.run,620,root)
 except BaseException as exc:r.state['result']='BLOCKED';r.state['failure_type']=type(exc).__name__;m.save(here/'state.json',r.state);raise
 finally:load('report-approved-rollout.py').update(a.run)
if __name__=='__main__':main()
