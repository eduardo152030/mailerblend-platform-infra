"""D031: detener un CT fallido y restaurar su checkpoint, sin avanzar a otro."""
import json
import time

def needs_rollback(state):
    return 'external_backup_verified' in state.get('steps',[])

def recover(r,m):
    m.execution_gate(r.ct,recovery=True)
    assert r.ct in [618,622,611,616,610,617,615,614,61211]
    if not needs_rollback(r.state):
        r.state.update(result='BLOCKED_NO_CHANGES',no_active_exporter_or_monitoring_changes=True)
    else:
        assert m.digest(r.here/'exporters-before.tar')==r.state['backup']['sha256']
        r.watch_mode=True
        if r.monitor.state.get('offhost_verified'):
            # Recovery must be possible even when the previous CT watcher raised HALT.
            raw=m.load('run-incremental-p0.py');raw.HERE=r.monitor.here;raw.CTDIR=r.monitor.p.CTDIR;raw.SSH=m.SSH;r.monitor.p.remote=raw.remote
            status=json.loads(raw.remote(raw.ct('import json\nfrom pathlib import Path\ns=json.loads((Path('+repr(raw.CTDIR)+')/"state.json").read_text());print(json.dumps({"test":bool(s.get("test_sha256"))}))')))
            if status['test']:
                r.monitor.rule(False);end=time.monotonic()+120
                while True:
                    alerts=raw.get('http://192.168.1.110:9090','/api/v1/alerts')['data']['alerts']
                    if not [a for a in alerts if a['labels'].get('alertname')=='LxcCpuIntegrationVerification' and a['labels'].get('ct_id')==str(r.ct)]:break
                    assert time.monotonic()<end,'Controlled test failed to resolve';time.sleep(3)
                r.monitor.p.helper('remove-test')
            r.monitor.rollback()
        r.helper('rollback')
        import inspect
        ready=m.load('exporter-http-readiness.py')
        code='import json,subprocess,time,urllib.request\n'+inspect.getsource(ready.wait_http)+'''\nbase=json.load(open(DIRECTORY+'/baseline.json'))
for name,old in base['exporters'].items():
 now=json.loads(subprocess.check_output(['docker','inspect',name]))[0]
 assert now['Id']==old['Id'] and now['Image']==old['Image'] and now['State']['Running']
 wait_http('http://IP:'+str(9100 if name=='node_exporter' else 8085)+'/metrics')
print('Original exporter identities/images/readiness verified')
'''.replace('DIRECTORY',repr(r.directory)).replace('IP',r.manifest['ip'])
        r.remote(r.ctcode(code))
        if 'cpu_history_started' in r.state['steps']:r.stop_cpu_history()
        r.state.update(result='BLOCKED_ROLLED_BACK',safe_rollback_verified=True,rollback_scope='Current CT originals and preceding accepted Prometheus checkpoint; data/images preserved')
    m.save(r.here/'state.json',r.state)
    if not (r.root/'HALT.json').exists():m.save(r.root/'HALT.json',{'ct':r.ct,'reason':'d031_gate_failure','state':r.state['result']})
