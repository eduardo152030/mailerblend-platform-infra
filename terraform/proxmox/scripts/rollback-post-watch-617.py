#!/usr/bin/env python3
"""D031: revocar PASS provisional617 tras watcher FAIL y restaurar solo617/checkpoint8."""
import argparse
import importlib.util
import json
from pathlib import Path
import yaml

ROOT=Path(__file__).resolve().parents[1]
def load(name):
    s=importlib.util.spec_from_file_location(name,ROOT/'scripts'/name);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def rollback_gate(state,watch,registry):
    assert state['ct']==617 and state['result']=='PASS'
    assert watch['result']=='FAIL' and watch['seconds']>=900
    assert set(registry['prometheus_integrated'])=={624,626,625,613,621,620,619,623,617}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run',required=True);p.add_argument('--execute',action='store_true');p.add_argument('--evidence-output',type=Path);a=p.parse_args();assert a.execute
    m=load('rollout-approved-exporters.py');m.execution_gate(617,recovery=True)
    root=Path.home()/'.local/share/mailerblend-recovery/phase4'/a.run;here=root/'617';state=json.loads((here/'state.json').read_text());watch=json.loads((here/'post-watch-result.json').read_text());regpath=ROOT/'services/common/exporter-migration.yml';registry=yaml.safe_load(regpath.read_text());rollback_gate(state,watch,registry)
    if state.get('manifest',{}).get('memory_alignment'):
        assert a.evidence_output and not a.evidence_output.exists(),'Memory reentry needs a new evidence path; preserve D031 mirror'
    rows=[json.loads(line) for line in (here/'post-watch.jsonl').read_text().splitlines()];first=next(x['elapsed_seconds'] for x in rows if not x['checks_passed']);assert watch['seconds']-first>=600
    r=object.__new__(m.Runner);r.ct=617;r.run=a.run;r.root=root;r.here=here;r.log=here/'post-watch-recovery.private.log';r.watch_mode=True;r.directory='/opt/exporter-phase4-pilot/'+a.run+'-617';r.state=state;r.manifest=state['manifest']
    assert r.identities()==state['exporters'],'Candidate identity changed; inspect before recovery'
    r.monitor=load('progressive-monitoring-transaction.py').Transaction(a.run,617,here/'monitoring',lock_root=root);r.monitor.p.SSH=m.SSH;r.monitor.state=json.loads((here/'monitoring/state.json').read_text())
    baseline=json.loads((here/'monitoring/baseline.json').read_text());groups=json.loads(baseline['files']['targets/node-exporter.json']);before={int(g['labels']['vmid']) for g in groups if g['labels'].get('cpu_contract')=='lxc_cgroup_v1'};assert before==set(registry['prometheus_integrated'])-{617},'Wrong rollback checkpoint'
    state['initial_result']='PASS';state['post_watch']=watch;state['failure_type']='POST_WATCH_RAM_MISMATCH';state['result']='BLOCKED_POST_WATCH';m.save(here/'state.json',state)
    load('recover-approved-wave.py').recover(r,m)
    services=load('prepare-incremental-monitoring.py').generator.load_services();chain=load('check-incremental-chain.py')
    for ct in before:
        name=next(s['name'] for s in services if int(s['vmid'])==ct);assert not chain.assess(chain.collect('http://192.168.1.110:9090',ct,name))
    for key in ['exporters_validated','cpu_contract_verified']:registry[key].pop('617')
    for key in ['prometheus_integrated','telegram_chain_verified']:registry[key].remove(617)
    registry['remaining_order'].insert(0,617);regpath.write_text(yaml.safe_dump(registry,sort_keys=False))
    state['blocked_reason']='D031 post-watch RAM comparison failed for analytics-ingest-gateway; candidates stopped, original exporters and eight-source checkpoint restored';m.save(here/'state.json',state)
    paths=[ROOT/'docs/roadmap/evidence/2026-11-02-rollout-617.json']
    if a.evidence_output:
        assert not a.evidence_output.exists(),'Preserve prior evidence'
        paths.append(a.evidence_output)
    else:paths.append(ROOT/'docs/roadmap/evidence/2026-11-05-617-execution.json')
    source=json.loads(paths[0].read_text())
    for path in paths:
        data=dict(source);data.update(initial_result='PASS',result='BLOCKED_ROLLED_BACK',post_watch=watch,final_acceptance=False,post_watch_rollback_verified=True);path.write_text(json.dumps(data,indent=2)+'\n')
    load('report-approved-rollout.py').update(a.run)
    print('CT617 ROLLED BACK; provisional acceptance revoked; CT623 and seven predecessors retained (8/17)')

if __name__=='__main__':main()
