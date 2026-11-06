#!/usr/bin/env python3
"""Resume only the verified D025 CT621 rollback-readiness checkpoint; never redo backups."""
import argparse,hashlib,json,os,time
from datetime import datetime,timezone
from pathlib import Path
import yaml
import importlib.util
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('rollout',ROOT/'scripts/rollout-approved-exporters.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def restore(run,ct):
 assert ct==621
 root=Path.home()/'.local/share/mailerblend-recovery/phase4'/run;r=object.__new__(m.Runner);r.ct=ct;r.run=run;r.root=root;r.here=root/str(ct);r.directory='/opt/exporter-phase4-pilot/'+run+'-'+str(ct);r.folder='/mnt/storage/mailerblend-recovery/phase4/'+run+'/'+str(ct);r.log=r.here/'private.log';r.state=json.loads((r.here/'state.json').read_text())
 assert r.state['result']=='BLOCKED' and r.state['steps'][-1]=='incremental_integration','Only rollback-readiness checkpoint allowed'
 r.manifest=r.state['manifest'];r.start=time.monotonic()-(datetime.now(timezone.utc)-datetime.fromisoformat(r.state['started_at_utc'])).total_seconds();r.previous=time.monotonic()
 for name,h in r.manifest['file_sha256'].items():assert hashlib.sha256((r.here/'bundle'/name).read_bytes()).hexdigest()==h
 assert m.digest(r.here/'exporters-before.tar')==r.state['backup']['sha256']
 r.monitor=m.load('progressive-monitoring-transaction.py').Transaction(run,ct,r.here/'monitoring');r.monitor.p.SSH=m.SSH;r.monitor.baseline=json.loads((r.here/'monitoring/baseline.json').read_text());r.monitor.registry=yaml.safe_load((ROOT/'services/common/exporter-migration.yml').read_text());r.monitor.state=json.loads((r.here/'monitoring/state.json').read_text());assert r.monitor.state['integrated'] and r.monitor.state['offhost_verified']
 r.monitor.manifest=json.loads(r.monitor.p.remote(r.monitor.p.ct('import pathlib\nprint((pathlib.Path('+repr(r.monitor.p.CTDIR)+')/"manifest.json").read_text())')))
 return r

def resume(r):
 # Verify original IDs/images/running and bounded readiness, then restore Prometheus checkpoint.
 code='''import json,pathlib,subprocess,urllib.request,time
base=json.load(open(DIR+'/baseline.json'))
for name,old in base['exporters'].items():
 if old:
  now=json.loads(subprocess.check_output(['docker','inspect',name]))[0]
  assert now['Id']==old['Id'] and now['Image']==old['Image'] and now['State']['Running'] and not now['State']['OOMKilled']
  end=time.monotonic()+120
  while True:
   try:
    with urllib.request.urlopen('http://IP:'+str(9100 if name=='node_exporter' else 8085)+'/metrics',timeout=8) as response:assert response.status==200
    break
   except (OSError,AssertionError):
    assert time.monotonic()<end,'Original readiness timeout';time.sleep(2)
print(json.dumps(json.load(open(DIR+'/applied.json'))))
'''.replace('DIR',repr(r.directory)).replace('IP',r.manifest['ip'])
 expected=json.loads(r.remote(r.ctcode(code)));r.monitor.rollback();r.mark('coordinated_rollback_ready_verified')
 r.state['result']='IN_PROGRESS';r.helper('apply');r.helper('check');r.namespace(True);r.monitor.integrate(r.point(),True)
 first=r.identities();assert all(first[n]['id']==expected[n]['id'] for n in expected)
 r.helper('apply');r.helper('check');assert r.identities()==first;r.monitor.idempotence();r.state['exporters']=first;r.mark('resume_and_idempotence')
 r.observe_and_telegram();r.finish()
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run',required=True);p.add_argument('--execute',action='store_true');a=p.parse_args();assert a.execute;os.umask(0o077);r=restore(a.run,621)
 try:resume(r)
 except BaseException as exc:r.state['result']='BLOCKED';r.state['failure_type']=type(exc).__name__;m.save(r.here/'state.json',r.state);raise
