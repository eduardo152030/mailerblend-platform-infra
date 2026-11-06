#!/usr/bin/env python3
"""D025 disabled controlled-rule diagnostic. No notification and no exporter/app changes."""
import argparse,importlib.util,json,os,threading,time,urllib.request
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[1]
def load(n):
 s=importlib.util.spec_from_file_location(n,ROOT/'scripts'/n);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run',required=True);p.add_argument('--execute',action='store_true');a=p.parse_args();assert a.execute;os.umask(0o077)
 root=Path.home()/'.local/share/mailerblend-recovery/phase4'/a.run;state=json.loads((root/'620/state.json').read_text());assert state['result']=='BLOCKED_ROLLED_BACK' and state['safe_rollback_verified']
 mon=load('run-incremental-p0.py');mon.HERE=root/'620/monitoring';mon.CTDIR='/opt/infra-prom/.runtime/'+a.run+'-620';mon.SSH=load('rollout-approved-exporters.py').SSH
 rule=load('check-incremental-chain.py').verification_rule(621,a.run.replace('-','_')+'_diagnosis',False)
 mon.remote(mon.ct('import pathlib\np=pathlib.Path('+repr(mon.CTDIR+'/verification.yml')+');p.write_text('+repr(yaml.safe_dump(rule,allow_unicode=True,sort_keys=False))+');p.chmod(0o600)'))
 stop=threading.Event();rows=[];trace=root/'diagnostic-rule-transition.jsonl';assert not trace.exists()
 def poll():
  with trace.open('x') as out:
   while not stop.is_set():
    try:
     with urllib.request.urlopen('http://192.168.1.110:9090/api/v1/rules',timeout=5) as response:groups=json.load(response)['data']['groups']
     health={}
     for group in groups:
      for r in group['rules']:health[r['health']]=health.get(r['health'],0)+1
     row={'time':time.time(),'health_counts':health};rows.append(row);out.write(json.dumps(row)+'\n');out.flush()
    except Exception as exc:rows.append({'error_type':type(exc).__name__})
    stop.wait(.5)
 thread=threading.Thread(target=poll);thread.start();before=load('rollout-approved-exporters.py').telemetry()
 try:
  with load('monitoring-transaction-lock.py').monitoring_lock(root,exclusive=True):
   mon.helper('test');mon.helper('remove-test')
 finally:stop.set();thread.join(10)
 after=load('rollout-approved-exporters.py').telemetry();assert after['alertmanager_notifications_failed_total']==before['alertmanager_notifications_failed_total']
 report={'disabled_rule_only':True,'rule_removed':True,'unknown_health_observed':any('unknown' in x.get('health_counts',{}) for x in rows),'bad_health_observed':any(any(k not in ['ok','unknown'] for k in x.get('health_counts',{})) for x in rows),'polls':len(rows),'telegram_attempts_delta':after['alertmanager_notifications_total']-before['alertmanager_notifications_total'],'telegram_failures_delta':after['alertmanager_notifications_failed_total']-before['alertmanager_notifications_failed_total'],'post_watch_probe_serialized_with_transaction':True}
 (ROOT/'docs/roadmap/evidence/2026-11-02-rule-transition-diagnosis.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
if __name__=='__main__':main()
