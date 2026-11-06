#!/usr/bin/env python3
"""D025/D029: rollback coordinado del CT623 bloqueado, preservando siete cadenas."""
import argparse
import importlib.util
import inspect
import json
import os
from pathlib import Path
import subprocess
import time
import yaml

ROOT=Path(__file__).resolve().parents[1]
def load(name):
    s=importlib.util.spec_from_file_location(name,ROOT/'scripts'/name);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run',required=True);p.add_argument('--ct',type=int,choices=[623],required=True);p.add_argument('--execute',action='store_true');a=p.parse_args();assert a.execute;os.umask(0o077)
    m=load('rollout-approved-exporters.py');root=Path.home()/'.local/share/mailerblend-recovery/phase4'/a.run;here=root/str(a.ct);state=json.loads((here/'state.json').read_text());registry=yaml.safe_load((ROOT/'services/common/exporter-migration.yml').read_text())
    assert state['ct']==623 and state['result']=='BLOCKED' and state['steps'][-1]=='controlled_firing_rule'
    assert 623 not in registry['prometheus_integrated'] and set(registry['prometheus_integrated'])=={624,626,625,613,621,620,619}
    failed=state['failed_observation'];assert failed['result']=='FAIL' and failed['seconds']-failed['first_failure_seconds']>=600
    assert m.digest(here/'exporters-before.tar')==state['backup']['sha256']
    marker=root/'HALT.json'
    if marker.exists():assert json.loads(marker.read_text())['ct']==623,'Unrelated watcher anomaly: stop'
    else:m.save(marker,{'ct':623,'reason':'cpu_metric_data_stale','threshold_seconds':90})
    t=load('progressive-monitoring-transaction.py').Transaction(a.run,623,here/'monitoring');t.p.SSH=m.SSH;t.state=json.loads((here/'monitoring/state.json').read_text());assert t.state['offhost_verified']
    assert m.digest(here/'monitoring/integration-before.tar')==t.state['sha256']
    alerts=t.p.get('http://192.168.1.110:9090','/api/v1/alerts')['data']['alerts']
    assert not [x for x in alerts if x['labels'].get('alertname')=='LxcCpuIntegrationVerification' and x['labels'].get('ct_id')=='623'],'Resolve test before removing it'
    t.p.helper('remove-test');t.rollback()
    r=object.__new__(m.Runner);r.ct=623;r.run=a.run;r.root=root;r.here=here;r.log=here/'recovery.private.log';r.watch_mode=True;r.directory='/opt/exporter-phase4-pilot/'+a.run+'-623';r.helper('rollback')
    ready=load('exporter-http-readiness.py')
    probe='import json,subprocess,time,urllib.request\n'+inspect.getsource(ready.wait_http)+'''\nbase=json.load(open(DIRECTORY+'/baseline.json'))
for name,old in base['exporters'].items():
 now=json.loads(subprocess.check_output(['docker','inspect',name]))[0]
 assert now['Id']==old['Id'] and now['Image']==old['Image'] and now['State']['Running'] and not now['State']['OOMKilled']
 wait_http('http://192.168.1.123:'+str(9100 if name=='node_exporter' else 8085)+'/metrics')
with urllib.request.urlopen('http://127.0.0.1:8069/web/login',timeout=10) as response:assert response.status==200
assert subprocess.run(['docker','exec','infra-gestoria-db-1','pg_isready','-h','127.0.0.1','-p','5432'],capture_output=True,timeout=10).returncode==0
print('CT623 original identities/images/readiness and applications verified')
'''.replace('DIRECTORY',repr(r.directory))
    r.remote(r.ctcode(probe));r.stop_cpu_history()
    chain=load('check-incremental-chain.py');services=load('prepare-incremental-monitoring.py').generator.load_services()
    for ct in registry['prometheus_integrated']:
        svc=next(x['name'] for x in services if int(x['vmid'])==ct);assert not chain.assess(chain.collect('http://192.168.1.110:9090',ct,svc))
    state.update(result='BLOCKED_ROLLED_BACK',safe_rollback_verified=True,blocked_reason='CT623 explicit cAdvisor CPU timestamp exceeded90s; no tolerance relaxation; subsequent CTs not started',rollback_scope='CT623 original exporters and seven-source Prometheus checkpoint; applications/data/resources unchanged; candidates retained stopped')
    m.save(here/'state.json',state);load('report-approved-rollout.py').update(a.run)
    print('CT623 rollback PASS; seven corrected chains retained; sequence HALTED')

if __name__=='__main__':main()
