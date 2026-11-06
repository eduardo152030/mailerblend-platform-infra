#!/usr/bin/env python3
"""D031: reentrada exclusiva623, backup nuevo, cadencia30s y rollback coordinado."""
import argparse
from datetime import datetime,timezone
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import tarfile
import tempfile
import time
import yaml

ROOT=Path(__file__).resolve().parents[1]
def load(name):
    s=importlib.util.spec_from_file_location(name,ROOT/'scripts'/name);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def reentry_gate(state,marker,registry):
    assert state['ct']==623 and state['result']=='BLOCKED_ROLLED_BACK' and state['safe_rollback_verified']
    assert marker=={'ct':623,'reason':'cpu_metric_data_stale','threshold_seconds':90},'Unknown/new HALT; do not archive it'
    assert set(registry['prometheus_integrated'])=={624,626,625,613,621,620,619}
    assert 623 in registry['remaining_order']

def safe_rollback(r,m):
    r.watch_mode=True
    if r.monitor.state.get('offhost_verified'):
        status=json.loads(r.monitor.p.remote(r.monitor.p.ct('import json\nfrom pathlib import Path\ns=json.loads((Path('+repr(r.monitor.p.CTDIR)+')/"state.json").read_text());print(json.dumps({"test":bool(s.get("test_sha256"))}))')))
        if status['test']:
            r.monitor.rule(False);deadline=time.monotonic()+120
            while True:
                alerts=r.monitor.p.get('http://192.168.1.110:9090','/api/v1/alerts')['data']['alerts']
                if not [a for a in alerts if a['labels'].get('alertname')=='LxcCpuIntegrationVerification' and a['labels'].get('ct_id')=='623']:break
                assert time.monotonic()<deadline,'Controlled test did not resolve';time.sleep(3)
            r.monitor.p.helper('remove-test')
        r.monitor.rollback()
    if r.state.get('revision_attempted'):
        r.helper('rollback')
    ready=load('exporter-http-readiness.py')
    # Original readiness may take a few seconds after a legitimate rollback.
    import inspect
    code='import json,subprocess,time,urllib.request\n'+inspect.getsource(ready.wait_http)+'''\nbase=json.load(open(DIRECTORY+'/baseline.json'))
for name,old in base['exporters'].items():
 now=json.loads(subprocess.check_output(['docker','inspect',name]))[0]
 assert now['Id']==old['Id'] and now['Image']==old['Image'] and now['State']['Running']
 wait_http('http://192.168.1.123:'+str(9100 if name=='node_exporter' else 8085)+'/metrics')
ns={'__name__':'rollback_application_check'}
exec(open(DIRECTORY+'/pilot.py').read(),ns);ns['unchanged'](__import__('pathlib').Path(DIRECTORY))
print('Originals and application baseline verified after rollback')
'''.replace('DIRECTORY',repr(r.directory))
    r.remote(r.ctcode(code))
    if 'cpu_history_started' in r.state['steps'][r.state['recovery_step_offset']:]:r.stop_cpu_history()
    r.state.update(result='BLOCKED_ROLLED_BACK',safe_rollback_verified=True,blocked_reason='D031 CT623 recovery gate failed; originals and seven-source checkpoint restored')
    m.save(r.here/'state.json',r.state)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run',required=True);p.add_argument('--execute',action='store_true');a=p.parse_args();assert a.execute;os.umask(0o077)
    m=load('rollout-approved-exporters.py');m.execution_gate(623)
    root=Path.home()/'.local/share/mailerblend-recovery/phase4'/a.run;here=root/'623';state=json.loads((here/'state.json').read_text());marker=root/'HALT.json';registry=yaml.safe_load((ROOT/'services/common/exporter-migration.yml').read_text());reentry_gate(state,json.loads(marker.read_text()),registry);marker_hash=m.digest(marker)
    assert m.digest(here/'exporters-before.tar')==state['backup']['sha256']
    r=object.__new__(m.Runner);r.ct=623;r.run=a.run;r.root=root;r.here=here;r.log=here/'private.log';r.watch_mode=True;r.directory='/opt/exporter-phase4-pilot/'+a.run+'-623';r.folder='/mnt/storage/mailerblend-recovery/phase4/'+a.run+'/623';r.state=state;r.start=time.monotonic();r.previous=r.start
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ');recovery='d031-'+stamp;mon_run='integration-'+stamp
    audit=next(x for x in json.loads((ROOT/'docs/roadmap/evidence/2026-11-02-rollout-authenticated-preflight.json').read_text()) if x['ct']==623)
    # Revalidate original apps/config, exporters and held candidates, not just image tags.
    code='''import json,subprocess,pathlib,shutil,re
d=pathlib.Path(DIRECTORY);base=json.loads((d/'baseline.json').read_text());records=json.loads((d/'applied.json').read_text())
ns={'__name__':'read_only_preflight'};exec((d/'pilot.py').read_text(),ns);ns['unchanged'](d)
for name,old in base['exporters'].items():
 now=json.loads(subprocess.check_output(['docker','inspect',name]))[0]
 assert now['Id']==old['Id'] and now['Image']==old['Image'] and now['State']['Running'] and not now['State']['OOMKilled']
 held=json.loads(subprocess.check_output(['docker','inspect',name+'-phase4-623-held']))[0]
 assert not held['State']['Running'] and held['Id']==records[name]['id']
assert not (d/'rejected-candidates.json').exists()
assert shutil.disk_usage('/').free>=1024**3
print('Original baseline, application config and held candidates revalidated')
'''.replace('DIRECTORY',repr(r.directory))
    r.remote(r.ctcode(code));r.namespace()
    allocation=audit['allocation']
    code='import pathlib,json,subprocess,shutil\nc=dict(l.split(": ",1) for l in subprocess.check_output(["pct","config","623"],text=True).splitlines() if ": " in l)\nassert {k:c.get(k) for k in '+repr(allocation)+'}=='+repr(allocation)+'\np=pathlib.Path("/sys/fs/cgroup/lxc/623");assert int((p/"memory.max").read_text())=='+str(int(allocation['memory'])*1024**2)+'\nassert (p/"cpu.max").read_text().split()[0]=="max"\nassert shutil.disk_usage("/mnt/storage").free>=2*1024**3\nimport re\nassert int(re.search(r"MemAvailable:\s+(\d+)",pathlib.Path("/proc/meminfo").read_text()).group(1))>=2*1024*1024\nprint(json.dumps({n:(p/n).read_text().strip() for n in ["memory.events","memory.pressure","memory.current","memory.max","cpu.stat"]}))'
    r.state['resources_before']=json.loads(r.remote(code));assert all(float(x)<=5 for x in m.re.findall(r'avg(?:10|60)=(\S+)',r.state['resources_before']['memory.pressure']))
    assert shutil.disk_usage(root).free>=2*1024**3
    chain=load('check-incremental-chain.py');services=load('prepare-incremental-monitoring.py').generator.load_services()
    for ct in registry['prometheus_integrated']:
        service=next(s['name'] for s in services if int(s['vmid'])==ct);assert not chain.assess(chain.collect('http://192.168.1.110:9090',ct,service))
    # Fresh byte-exact exporters/config/image backup, in addition to preserved originals.
    name='exporters-before-'+recovery+'.tar';remote_archive=r.folder+'/'+name
    code='import os,pathlib,subprocess,hashlib,json\np=pathlib.Path('+repr(remote_archive)+');fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)\nwith os.fdopen(fd,"wb") as f:x=subprocess.run(["pct","exec","623","--","tar","-C",'+repr(r.directory)+',"-cf","-","."],stdout=f,stderr=subprocess.PIPE,timeout=180)\nassert x.returncode==0\nprint(json.dumps({"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"bytes":p.stat().st_size}))'
    backup=json.loads(r.remote(code));target=here/name
    with target.open('xb') as out:copy=subprocess.run(m.SSH+['cat',remote_archive],stdout=out,stderr=subprocess.PIPE,timeout=180)
    assert copy.returncode==0 and m.digest(target)==backup['sha256']
    with tarfile.open(target) as t:
        base=json.load(t.extractfile('./baseline.json'))
        for n,info in base['archives'].items():
            import hashlib
            h=hashlib.sha256();stream=t.extractfile('./'+n)
            for b in iter(lambda:stream.read(1024*1024),b''):h.update(b)
            assert h.hexdigest()==info['sha256']
    r.state['recovery_backup']=backup|{'name':name,'offhost_verified':True}
    r.monitor=load('progressive-monitoring-transaction.py').Transaction(mon_run,623,here/('monitoring-'+recovery),lock_root=root);r.monitor.p.SSH=m.SSH
    r.monitor.prepare()  # Fresh Prom backup/restore-in-staging and promtool config/rules/SD.
    r.state['recovery_started_at_utc']=datetime.now(timezone.utc).isoformat();r.state['recovery_authorization']='D-031';r.state['recovery_step_offset']=len(r.state['steps'])
    old=state['manifest'];saved=here/recovery;saved.mkdir(mode=0o700,exist_ok=False);shutil.copy2(here/'state.json',saved/'state.json');shutil.copytree(here/'bundle',saved/'bundle')
    try:
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp);manifest=load('prepare-623-cadence.py').render(out,audit);changed={n for n,h in manifest['file_sha256'].items() if old['file_sha256'].get(n)!=h}
            assert changed<=set(['cadvisor.yml','pilot.py','sample.py','observe.py','cpu-alignment.py']) and {'cadvisor.yml','pilot.py'}<=changed
            code='from pathlib import Path\nimport hashlib,shutil\nd=Path('+repr(r.directory)+');s=d/'+repr(recovery)+';s.mkdir(mode=0o700,exist_ok=False)\n'
            for n in sorted(changed):
                assert m.digest(here/'bundle'/n)==old['file_sha256'][n]
                code+='p=d/'+repr(n)+'\nassert hashlib.sha256(p.read_bytes()).hexdigest()=='+repr(old['file_sha256'][n])+'\nshutil.copy2(p,s/p.name)\np.write_text('+repr((out/n).read_text())+')\np.chmod(0o600)\n'
            for n in ['cpu-history.jsonl','cpu-history-process.json','cpu-history.private.log','cpu-history-errors.jsonl','cpu-probe-failures.jsonl']:
                code+='p=d/'+repr(n)+'\nif p.exists():p.rename(s/p.name)\n'
            assert m.digest(marker)==marker_hash;marker.rename(root/('HALT.623-resolved-'+recovery+'.json'));r.watch_mode=False;r.remote(r.ctcode(code))
            for n in changed:shutil.copy2(out/n,here/'bundle'/n)
            manifest.update(status='APPROVED_D031',approval_required=False);r.manifest=manifest;r.state['manifest']=manifest;m.save(here/'bundle/manifest.json',manifest)
        if (here/'observations.jsonl').exists():(here/'observations.jsonl').rename(saved/'observations.jsonl')
        for key in ['failure_type','failed_observation','blocked_reason']:
            if key in state:r.state.setdefault('resolved_previous_fields',{})[key]=r.state.pop(key)
        r.state['result']='IN_PROGRESS';r.mark('d031_fresh_backups_and_compatibility_verified');r.start_cpu_history();r.state['revision_attempted']=True;m.save(here/'state.json',r.state)
        r.helper('revise-cadvisor');r.mark('previous_cadvisor_preserved_stopped');r.pull();r.mutate();r.observe_and_telegram();r.finish();m.start_watch(a.run,623,root)
    except BaseException as exc:
        r.state['result']='BLOCKED';r.state['failure_type']=type(exc).__name__;m.save(here/'state.json',r.state)
        if not marker.exists():m.save(marker,{'ct':623,'reason':'d031_reentry_failure','failure_type':type(exc).__name__})
        safe_rollback(r,m)
        raise
    finally:load('report-approved-rollout.py').update(a.run)

if __name__=='__main__':main()
