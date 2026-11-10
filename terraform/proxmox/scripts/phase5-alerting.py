#!/usr/bin/env python3
"""D050: CT610-only config transaction; strict SSH, verified backups, no restarts.
Run baseline, prepare, validate, apply, verify, test-on/test-off, cleanup, rollback.
Private baseline includes secrets and MUST stay outside Git.
"""
import argparse,hashlib,io,json,os,shlex,subprocess,tarfile,time,urllib.request,urllib.parse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PRIVATE=Path.home()/'.local/share/mailerblend-recovery/phase5/d050'
BASE=Path('/opt/infra-prom')
def digest(b): return hashlib.sha256(b).hexdigest()
def remote(args,input=None):
    cmd=['ssh','-o','UserKnownHostsFile='+str(Path.home()/'.ssh/known_hosts'),'-o','StrictHostKeyChecking=yes','-o','BatchMode=yes','pve',shlex.join(['pct','exec','610','--']+args)]
    r=subprocess.run(cmd,input=input,capture_output=True,timeout=180)
    if r.returncode: raise RuntimeError('Remote operation failed; output withheld: '+args[0])
    return r.stdout
def py(code):return remote(['python3','-c',code])
def save(p,d): p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
def fetch(port,path):
    with urllib.request.urlopen(f'http://192.168.1.110:{port}'+path,timeout=15) as r:return r.read()
def api(path):return json.loads(fetch(9090,path))['data']
def query(expr):return api('/api/v1/query?'+urllib.parse.urlencode({'query':expr}))['result']
def identities():
    return json.loads(py('import subprocess,json; cs=json.loads(subprocess.check_output(["docker","inspect"]+subprocess.check_output(["docker","ps","-aq"]).decode().split())); print(json.dumps({c["Name"]:[c["Id"],c["State"]["StartedAt"],c["RestartCount"],c["State"]["Running"]] for c in cs}))'))
def hashes():
    return json.loads(py('from pathlib import Path;import hashlib,json;p=Path("/opt/infra-prom");print(json.dumps({str(f.relative_to(p)):hashlib.sha256(f.read_bytes()).hexdigest() for d in [p/"config",p/".runtime/alertmanager.yml",p/".runtime/telegram_bot_token",p/"docker-compose.yml"] for f in (d.rglob("*") if d.is_dir() else [d]) if f.is_file()}))'))
def metrics():
    return {'failed':query('sum(alertmanager_notifications_failed_total{integration="telegram"})'), 'sent':query('sum(alertmanager_notifications_total{integration="telegram"})')}
def baseline():
    assert not (PRIVATE/'baseline.json').exists(),'Existing baseline: do not overwrite'
    PRIVATE.mkdir(parents=True,exist_ok=True,mode=0o700);os.chmod(PRIVATE,0o700)
    start=time.time(); ids=identities(); hs=hashes()
    archive=py('import io,tarfile,sys;from pathlib import Path;b=io.BytesIO();p=Path("/opt/infra-prom");a=tarfile.open(fileobj=b,mode="w");[a.add(p/n,arcname=n) for n in ["config",".runtime/alertmanager.yml",".runtime/telegram_bot_token","docker-compose.yml"]];a.close();sys.stdout.buffer.write(b.getvalue())')
    (PRIVATE/'before.tar').write_bytes(archive);os.chmod(PRIVATE/'before.tar',0o600)
    remote(['mkdir','-p','/opt/infra-prom/.runtime/phase5-d050'])
    remote(['tee','/opt/infra-prom/.runtime/phase5-d050/before.tar'],archive)
    remote(['chmod','600','/opt/infra-prom/.runtime/phase5-d050/before.tar'])
    assert py('import hashlib;print(hashlib.sha256(open("/opt/infra-prom/.runtime/phase5-d050/before.tar","rb").read()).hexdigest())').decode().strip()==digest(archive)
    with tarfile.open(fileobj=io.BytesIO(archive)) as a:
        for m in a:
            assert not Path(m.name).is_absolute() and '..' not in Path(m.name).parts and not m.issym() and not m.islnk()
            if m.isfile():
                body=a.extractfile(m).read();assert digest(body)==hs[m.name]
                p=PRIVATE/'before'/m.name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(body);os.chmod(p,0o600)
    for container,binary in [('prometheus','promtool'),('alertmanager','amtool')]:
        p=PRIVATE/binary;p.write_bytes(remote(['docker','exec',container,'cat','/bin/'+binary]));os.chmod(p,0o700)
    save(PRIVATE/'baseline.json',{'started':start,'identity':ids,'hashes':hs,'backup_sha256':digest(archive),'metrics':metrics(),'targets':api('/api/v1/targets')['activeTargets'],'rules':api('/api/v1/rules')})
    print('Baseline + CT/offhost SHA256 + archive restore-check PASS; secrets private')
def prepare():
    assert (PRIVATE/'baseline.json').exists()
    with tarfile.open(PRIVATE/'before.tar') as a:
        dest=PRIVATE/'candidate';dest.mkdir(exist_ok=True)
        a.extractall(dest,filter='data')
    dest=PRIVATE/'candidate'
    for p in (ROOT/'services/infra-prom/config/rules').glob('*.yml'):
        # Do not replace live CPU inventory, generated during F4.
        (dest/'config/rules'/p.name).write_bytes(p.read_bytes())
    for p in (ROOT/'services/infra-prom/config/alertmanager/templates').glob('*.tmpl'):
        (dest/'config/alertmanager/templates'/p.name).write_bytes(p.read_bytes())
    # Preserve the active chat ID privately; no token is rendered into YAML.
    import yaml
    original=yaml.safe_load((dest/'.runtime/alertmanager.yml').read_text())
    chat=original['receivers'][0]['telegram_configs'][0]['chat_id']
    source=ROOT/'services/infra-prom/config/alertmanager/alertmanager.yml'
    body=source.read_text().replace('__TELEGRAM_CHAT_ID__',str(chat))
    (dest/'.runtime/alertmanager.yml').write_text(body)
    (dest/'config/alertmanager/alertmanager.yml').write_bytes(source.read_bytes())
    assert hashes()==json.loads((PRIVATE/'baseline.json').read_text())['hashes'],'Drift since baseline'
    print('Candidate prepared from active baseline; targets and Prometheus config preserved')
def tool(args):
    r=subprocess.run(args,capture_output=True,text=True)
    (PRIVATE/'validation.private.log').open('a').write(shlex.join(list(map(str,args)))+'\n'+r.stdout+r.stderr+'\n')
    assert r.returncode==0,'Validation failed; see private validation log'
    return r.stdout
def validate():
    dest=PRIVATE/'candidate';conf=dest/'config';pt=str(PRIVATE/'promtool');at=str(PRIVATE/'amtool')
    tool([pt,'check','rules']+[str(p) for p in (conf/'rules').glob('*.yml')])
    text=(conf/'prometheus.yml').read_text().replace('/etc/prometheus/',str(conf)+'/');(PRIVATE/'prom-check.yml').write_text(text)
    tool([pt,'check','config',str(PRIVATE/'prom-check.yml')])
    text=(dest/'.runtime/alertmanager.yml').read_text().replace('/run/secrets/telegram_bot_token',str(dest/'.runtime/telegram_bot_token')).replace('/etc/alertmanager/templates/',str(conf/'alertmanager/templates')+'/');(PRIVATE/'am-check.yml').write_text(text)
    tool([at,'check-config',str(PRIVATE/'am-check.yml')])
    for state in ['firing','resolved']:
        text=tool([at,'template','render','--template.glob='+str(conf/'alertmanager/templates/*.tmpl'),'--template.text={{ template "telegram.message" . }}','--template.type=html','--template.data='+str(ROOT/f'tests/monitoring/telegram-{state}.json')]); assert state.upper() in text
        (PRIVATE/f'template-{state}.html').write_text(text)
    for test in ['alerts.test.yml','lxc-cpu.test.yml','incremental-cpu.test.yml','phase5.test.yml']:
        tool([pt,'test','rules',str(ROOT/'tests/monitoring'/test)])
    for severity in ['critical','warning','info','unknown']:
        tool([at,'config','routes','test','--config.file='+str(PRIVATE/'am-check.yml'),'--verify.receivers=telegram','severity='+severity,'service=test','instance=test'])
    save(PRIVATE/'validated.json',changed())
    print('promtool config/rules/fixtures + amtool config/templates/routes PASS')
def changed():
    old=json.loads((PRIVATE/'baseline.json').read_text())['hashes']; dest=PRIVATE/'candidate'
    return {str(p.relative_to(dest)):digest(p.read_bytes()) for d in [dest/'config',dest/'.runtime/alertmanager.yml'] for p in (d.rglob('*') if d.is_dir() else [d]) if p.is_file() and digest(p.read_bytes())!=old.get(str(p.relative_to(dest)))}
def reload(names):
    def metric(port,key):
        return float(next(l.split()[1] for l in fetch(port,'/metrics').decode().splitlines() if l.startswith(key+' ')))
    for n in names:
        port=9090 if n=='prometheus' else 9093
        key=n+'_config_last_reload_success_timestamp_seconds'
        old=metric(port,key)
        remote(['docker','kill','--signal=SIGHUP',n])
        end=time.monotonic()+20
        while time.monotonic()<end:
            if metric(port,n+'_config_last_reload_successful')==1 and metric(port,key)>old:break
            time.sleep(.5)
        else:raise RuntimeError('Reload not confirmed: '+n)
def apply(rollback=False):
    baseline=json.loads((PRIVATE/'baseline.json').read_text());changes=changed();current=hashes()
    expected=dict(baseline['hashes']);expected.update(changes)
    if rollback and (PRIVATE/'test-state.json').exists():
        test=json.loads((PRIVATE/'test-state.json').read_text());with_test=dict(expected)
        with_test['config/rules/phase5-delivery-test.yml']=test['sha256']
        assert current==with_test and identities()==baseline['identity'],'Drift before recovery'
        py('from pathlib import Path;Path("/opt/infra-prom/config/rules/phase5-delivery-test.yml").unlink()')
        (PRIVATE/'test-state.json').unlink();current=hashes()
    assert current in [baseline['hashes'],expected],'Unexpected drift: refusing overwrite'
    assert identities()==baseline['identity'],'Container identity changed'
    assert digest((PRIVATE/'before.tar').read_bytes())==baseline['backup_sha256']
    assert json.loads((PRIVATE/'validated.json').read_text())==changes,'Candidate changed since validation'
    paths=changes
    if current==expected and not rollback:print('Idempotent: no writes, no reload');return
    # Alertmanager is a single-file bind mount: preserve its inode when writing.
    # All replacements are backed up; rollback immediately if reload/health fails.
    source=PRIVATE/('before' if rollback else 'candidate')
    try:
        for name in paths:
            target=BASE/name; p=source/name
            if p.exists():remote(['tee',str(target)],p.read_bytes())
            elif rollback: remote(['python3','-c',f'from pathlib import Path;Path({str(target)!r}).unlink()'])
        assert hashes()==(baseline['hashes'] if rollback else expected),'Readback hashes differ'
        reload(['alertmanager','prometheus'])
        time.sleep(3);verify(check_delivery=not rollback)
    except Exception:
        if not rollback:
            for name in paths:
                p=PRIVATE/'before'/name
                if p.exists():remote(['tee',str(BASE/name)],p.read_bytes())
                else:py(f'from pathlib import Path;Path({str(BASE/name)!r}).unlink(missing_ok=True)')
            reload(['alertmanager','prometheus']);time.sleep(3)
            print('Safety rollback restored baseline; dependent work stopped')
        raise
    save(PRIVATE/('rollback.json' if rollback else 'applied.json'),{'time':time.time(),'changes':paths})
    print('Rollback complete' if rollback else 'Controlled reload complete')
def verify(check_delivery=True):
    for port in [9090,9093]:assert fetch(port,'/-/ready')
    assert identities()==json.loads((PRIVATE/'baseline.json').read_text())['identity']
    targets=api('/api/v1/targets')['activeTargets'];baseline=json.loads((PRIVATE/'baseline.json').read_text())['targets']
    def keys(rows):return sorted((json.dumps(t['labels'],sort_keys=True),t['scrapeUrl']) for t in rows)
    assert keys(targets)==keys(baseline),'Target coverage changed'
    assert all(t['health']=='up' for t in targets),'Target not UP'
    for expr in ['prometheus_config_last_reload_successful','alertmanager_config_last_reload_successful']:
        assert all(float(r['value'][1])==1 for r in query(expr))
    deadline=time.monotonic()+65
    while True:
        rules=api('/api/v1/rules');pending=[r for g in rules['groups'] for r in g['rules'] if r['health']!='ok']
        if not pending:break
        save(PRIVATE/'rule-health-observation.json',{'time':time.time(),'rules':pending})
        assert not any(r.get('lastError') for r in pending),'Rule evaluation error'
        assert time.monotonic()<deadline,'Rule first evaluation timed out'
        time.sleep(2)
    assert not check_delivery or metrics()['failed'][0]['value'][1]==json.loads((PRIVATE/'baseline.json').read_text())['metrics']['failed'][0]['value'][1],'New Telegram failures'
    result={'time':time.time(),'counts':{j:sum(t['labels']['job']==j for t in targets) for j in ['node_exporter','cadvisor','blackbox']},'alert_rules':sum(r['type']=='alerting' for g in rules['groups'] for r in g['rules']),'recording_rules':sum(r['type']=='recording' for g in rules['groups'] for r in g['rules']),'firing':[(r['metric'],r['value'][1]) for r in query('ALERTS{alertstate="firing"}')],'metrics':metrics(),'identities_unchanged':True}
    save(PRIVATE/'verification.json',result);print(json.dumps(result,ensure_ascii=False))
def test_rule(enabled):
    import yaml
    assert (PRIVATE/'applied.json').exists(),'Deploy and verify before delivery test'
    if enabled:verify()
    state=PRIVATE/'test-state.json'
    expected=dict(json.loads((PRIVATE/'baseline.json').read_text())['hashes']);expected.update(changed())
    relative='config/rules/phase5-delivery-test.yml'
    if state.exists():expected[relative]=json.loads(state.read_text())['sha256']
    assert hashes()==expected,'Unexpected drift before test rule mutation'
    name='rules/phase5-delivery-test.yml'
    r={'groups':[{'name':'phase5_delivery','rules':[{'alert':'Phase5DeliveryVerification','expr':'lxc:cpu_usage:percent{ct_id="610"} '+('>= 0' if enabled else '< 0'),'for':'30s','labels':{'severity':'info','service':'infra-prom','phase5_test':'d050'},'annotations':{'summary':'Prueba Fase 5 sin incidencia real','description':'CPU real disponible; no se ha generado carga ni eventos Analytics.','value':'{{ printf "%.2f" $value }}%','threshold':'>=0% (solo ensayo)','ct_id':'{{ $labels.ct_id }}','dashboard_url':'http://192.168.1.110:9090/alerts'}}]}]}
    body=yaml.safe_dump(r,allow_unicode=True).encode()
    remote(['tee',str(BASE/'config'/name)],body);save(state,{'sha256':digest(body),'enabled':enabled});reload(['prometheus']);print('Temporary exporter-backed rule '+('enabled' if enabled else 'resolved expression'))
def cleanup():
    state=json.loads((PRIVATE/'test-state.json').read_text())
    assert not state['enabled'],'Resolve test and verify delivery before cleanup'
    assert hashes()['config/rules/phase5-delivery-test.yml']==state['sha256']
    assert not query('ALERTS{alertname="Phase5DeliveryVerification",alertstate="firing"}')
    py('from pathlib import Path;p=Path("/opt/infra-prom/config/rules/phase5-delivery-test.yml");p.unlink()')
    reload(['prometheus']);(PRIVATE/'test-state.json').unlink();print('Only temporary test rule removed')
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['baseline','prepare','validate','apply','verify','rollback','test-on','test-off','cleanup']);a=p.parse_args()
    if a.action=='rollback':apply(True)
    elif a.action in ['test-on','test-off']:test_rule(a.action=='test-on')
    else:globals()[a.action]()
