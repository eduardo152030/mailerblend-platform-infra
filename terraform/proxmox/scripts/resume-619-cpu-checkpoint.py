#!/usr/bin/env python3
"""D029: reparar solo el lector y reanudar validación sin reiniciar exporters/apps."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import shutil
import tempfile
import time
import yaml

ROOT=Path(__file__).resolve().parents[1]
def load(name):
    spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/name);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run',required=True);p.add_argument('--execute',action='store_true');a=p.parse_args();assert a.execute;os.umask(0o077)
    m=load('rollout-approved-exporters.py');root=Path.home()/'.local/share/mailerblend-recovery/phase4'/a.run;here=root/'619'
    state=json.loads((here/'state.json').read_text());assert state['ct']==619 and state['result']=='BLOCKED' and state['steps'][-1]=='resume_and_idempotence' and state['recovery_authorization']=='D-029'
    marker=root/'HALT.json';assert json.loads(marker.read_text())=={'ct':619,'reason':'d028_recovery_gate_failure','failure_type':'RuntimeError'};marker_hash=m.digest(marker)
    r=object.__new__(m.Runner);r.ct=619;r.run=a.run;r.root=root;r.here=here;r.log=here/'private.log';r.watch_mode=True;r.directory='/opt/exporter-phase4-pilot/'+a.run+'-619';r.folder='/mnt/storage/mailerblend-recovery/phase4/'+a.run+'/619';r.state=state;r.start=time.monotonic();r.previous=r.start;r.manifest=state['manifest']
    assert m.digest(here/'exporters-before.tar')==state['backup']['sha256']
    assert r.identities()==state['exporters'],'Candidate changed since idempotence gate'
    r.helper('check');r.namespace(True)
    r.monitor=load('progressive-monitoring-transaction.py').Transaction(a.run,619,here/'monitoring');r.monitor.p.SSH=m.SSH;r.monitor.registry=yaml.safe_load((ROOT/'services/common/exporter-migration.yml').read_text());r.monitor.baseline=json.loads((here/'monitoring/baseline.json').read_text());r.monitor.state=json.loads((here/'monitoring/state.json').read_text());assert r.monitor.state['offhost_verified']
    assert m.digest(here/'monitoring/integration-before.tar')==r.monitor.state['sha256']
    r.monitor.manifest=json.loads(r.monitor.p.remote(r.monitor.p.ct('from pathlib import Path\nprint((Path('+repr(r.monitor.p.CTDIR)+')/"manifest.json").read_text())')))
    r.monitor.wait_check();r.monitor.idempotence()
    probe='''from pathlib import Path
import json,hashlib
p=Path(DIRECTORY)
assert 'FileNotFoundError' in (p/'cpu-history.private.log').read_text() and '/proc/0/cgroup' in (p/'cpu-history.private.log').read_text()
process=Path('/proc')/str(json.loads((p/'cpu-history-process.json').read_text())['pid'])/'cmdline'
assert not process.exists() or not process.read_bytes(),'Original collector must have exited'
print('Exited collector race confirmed; exporters untouched')
'''.replace('DIRECTORY',repr(r.directory))
    r.remote(r.ctcode(probe))
    audit=next(x for x in json.loads((ROOT/'docs/roadmap/evidence/2026-11-02-rollout-authenticated-preflight.json').read_text()) if x['ct']==619)
    saved=here/'before-d029-collector-fix';saved.mkdir(mode=0o700,exist_ok=False);shutil.copy2(here/'state.json',saved/'state.json');shutil.copytree(here/'bundle',saved/'bundle')
    with tempfile.TemporaryDirectory() as tmp:
        out=Path(tmp);manifest=load('prepare-619-recovery.py').render(out,audit)
        changed={n for n,h in manifest['file_sha256'].items() if state['manifest']['file_sha256'].get(n)!=h};assert changed=={'cpu-alignment.py','observe.py'}
        code='from pathlib import Path\nimport hashlib,shutil\nd=Path('+repr(r.directory)+')\ns=d/"before-d029-collector-fix";s.mkdir(mode=0o700,exist_ok=False)\n'
        for name in changed:
            assert m.digest(here/'bundle'/name)==state['manifest']['file_sha256'][name]
            code+='p=d/'+repr(name)+'\nassert hashlib.sha256(p.read_bytes()).hexdigest()=='+repr(state['manifest']['file_sha256'][name])+'\nshutil.copy2(p,s/p.name)\np.write_text('+repr((out/name).read_text())+')\np.chmod(0o600)\n'
        for name in ['cpu-history.jsonl','cpu-history-process.json','cpu-history.private.log']:
            code+='(d/'+repr(name)+').rename(s/'+repr(name)+')\n'
        assert m.digest(marker)==marker_hash;marker.rename(root/'HALT.619-cpu-collector-transition-resolved.json');r.watch_mode=False
        try:
            r.remote(r.ctcode(code))
            for name in changed:shutil.copy2(out/name,here/'bundle'/name)
            manifest.update(status='APPROVED_D029',approval_required=False);r.manifest=manifest;r.state['manifest']=manifest;m.save(here/'bundle/manifest.json',manifest)
            r.state['result']='IN_PROGRESS';r.state.pop('failure_type',None);r.mark('cpu_collector_transition_fix_staged');r.start_cpu_history()
            end=time.monotonic()+120
            while True:
                try:r.sample();break
                except RuntimeError:
                    lines=r.log.read_text().splitlines();failure=next(json.loads(l)['ct_traceback'] for l in reversed(lines) if l.startswith('{"probe_error"'))
                    assert 'CPU timeline does not bracket metric timestamp' in failure,'New discrepancy: do not retry or relax'
                    assert time.monotonic()<end,'Timeline warmup failed';time.sleep(3)
            assert r.identities()==state['exporters'],'No exporter restart permitted'
            r.mark('cpu_timeline_warm_no_exporter_changes');r.observe_and_telegram();r.finish();m.start_watch(a.run,619,root)
        except BaseException as exc:
            r.state['result']='BLOCKED';r.state['failure_type']=type(exc).__name__;m.save(here/'state.json',r.state)
            if not (root/'HALT.json').exists():m.save(root/'HALT.json',{'ct':619,'reason':'d029_cpu_checkpoint_failure','failure_type':type(exc).__name__})
            raise
        finally:load('report-approved-rollout.py').update(a.run)

if __name__=='__main__':main()
