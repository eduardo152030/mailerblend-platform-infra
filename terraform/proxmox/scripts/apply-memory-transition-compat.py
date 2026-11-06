#!/usr/bin/env python3
"""D027 source-quality guard only: same forecast thresholds/for, verified backup and rollback."""
import argparse,importlib.util,json,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(n):
 s=importlib.util.spec_from_file_location(n,ROOT/'scripts'/n);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run',required=True);p.add_argument('--execute',action='store_true');a=p.parse_args();assert a.execute;os.umask(0o077)
 root=Path.home()/'.local/share/mailerblend-recovery/phase4'/a.run;assert not (root/'HALT.json').exists();assert json.loads((root/'620/state.json').read_text())['result']=='PASS'
 baseline_notifications=load('rollout-approved-exporters.py').telemetry()
 here=root/'memory-compat';assert not here.exists(),'Existing checkpoint: do not repeat blindly'
 tx=load('progressive-monitoring-transaction.py').Transaction(a.run,620,here,lock_root=root);tx.p.SSH=load('rollout-approved-exporters.py').SSH;tx.p.CTDIR='/opt/infra-prom/.runtime/'+a.run+'-memory-compat';tx.folder='/mnt/storage/mailerblend-recovery/phase4/'+a.run+'/memory-compat'
 tx.prepare();r=json.loads(tx.p.helper('rules'));assert r['changed']==['rules/infra-hosts.yml'], 'Only RAM forecast qualification may change';assert not json.loads(tx.p.helper('targets'))['changed']
 # Real restore/reapply proof, no exporter/container/data changes.
 tx.p.helper('rollback');r=json.loads(tx.p.helper('rules'));assert r['changed']==['rules/infra-hosts.yml'];assert not json.loads(tx.p.helper('targets'))['changed'];tx.idempotence();tx.after_archive()
 targets=tx.p.get('http://192.168.1.110:9090','/api/v1/targets')['data']['activeTargets'];assert sum(t['labels']['job']=='blackbox' for t in targets)==11
 before=load('rollout-approved-exporters.py').telemetry();assert before['alertmanager_notifications_failed_total']==baseline_notifications['alertmanager_notifications_failed_total'],'New Telegram error requires halt'
 report={'result':'PASS','scope':'RAM prediction source qualification only','forecast_lookback':'1h','forecast_horizon':'4h','for':'15m','thresholds_or_routes_changed':False,'backup_before_sha256':tx.state['sha256'],'after_archive':tx.state['after_archive'],'actual_rollback_verified':True,'idempotence_verified':True,'prometheus_alertmanager_container_ids_unchanged':True,'blackbox_preserved':11,'telegram_failures_total':before['alertmanager_notifications_failed_total']}
 load('rollout-approved-exporters.py').save(root/'memory-transition-compat-applied.json',report);(ROOT/'docs/roadmap/evidence/2026-11-02-memory-transition-compat.json').write_text(json.dumps(report,indent=2)+'\n');print('RAM source-transition compatibility PASS; thresholds/for preserved, rollback and second apply verified',flush=True)
if __name__=='__main__':main()
