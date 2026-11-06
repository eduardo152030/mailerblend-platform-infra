#!/usr/bin/env python3
"""D-028: recuperar CT619 con cAdvisor256MiB y gates D-025 completos."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import shutil
import tempfile
import time
import yaml

ROOT = Path(__file__).resolve().parents[1]

def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / name)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def resolution_gate(state, marker):
    assert state['ct']==619 and state['result']=='BLOCKED_ROLLED_BACK' and state['safe_rollback_verified']
    assert marker['ct']==619 and marker['reason']=='cadvisor_memory_pressure_and_cpu_consistency'
    assert marker['extended_seconds_completed']>=600 and marker['do_not_advance'] is True

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', required=True)
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--retry-compose-identity', action='store_true')
    parser.add_argument('--retry-cpu-alignment', action='store_true')
    args = parser.parse_args()
    assert args.execute
    os.umask(0o077)
    m = load('rollout-approved-exporters.py')
    root = Path.home() / '.local/share/mailerblend-recovery/phase4' / args.run
    here = root / '619'
    state = json.loads((here / 'state.json').read_text())
    marker = root / 'HALT.json'
    assert not (args.retry_compose_identity and args.retry_cpu_alignment)
    if args.retry_cpu_alignment:
        assert state['ct']==619 and state['result']=='BLOCKED_ROLLED_BACK' and state['safe_rollback_verified']
        assert json.loads(marker.read_text())=={'ct':619,'reason':'d028_recovery_gate_failure','failure_type':'RuntimeError'}
        assert state['steps'][-1]=='controlled_firing_rule'
        assert '### D-029' in (ROOT/'docs/roadmap/DECISIONS.md').read_text()
        proof=json.loads((ROOT/'docs/roadmap/evidence/2026-11-03-619-cpu-alignment-live-proof.json').read_text())
        assert len(proof['aligned_points'])>=2 and all(p['all_counter_checks_passed'] for p in proof['aligned_points'])
    elif args.retry_compose_identity:
        assert state['ct']==619 and state['result']=='BLOCKED' and state['safe_rollback_verified']
        assert json.loads(marker.read_text())=={'ct':619,'reason':'d028_recovery_gate_failure','failure_type':'AssertionError'}
        assert state['steps'][-1]=='cadvisor128_preserved_stopped'
    else:resolution_gate(state,json.loads(marker.read_text()))
    marker_hash=m.digest(marker)
    assert '### D-028' in (ROOT / 'docs/roadmap/DECISIONS.md').read_text()
    assert m.digest(here / 'exporters-before.tar') == state['backup']['sha256']
    registry = yaml.safe_load((ROOT / 'services/common/exporter-migration.yml').read_text())
    assert set(registry['prometheus_integrated']) == {624,626,625,613,621,620}
    chain = load('check-incremental-chain.py')
    audit = next(x for x in json.loads((ROOT / 'docs/roadmap/evidence/2026-11-02-rollout-authenticated-preflight.json').read_text()) if x['ct']==619)
    for ct, svc in [(624,'infra-journal-web'),(626,'infra-journal-api'),(625,'infra-journal-db'),(613,'infra-hola'),(621,'infra-project-gestion'),(620,'infra-focalboard')]:
        # Resolve inventory names instead of assuming historical aliases.
        services = load('prepare-incremental-monitoring.py').generator.load_services()
        svc = next(x['name'] for x in services if int(x['vmid']) == ct)
        assert not chain.assess(chain.collect('http://192.168.1.110:9090', ct, svc))
    r = object.__new__(m.Runner)
    r.ct=619; r.run=args.run; r.root=root; r.here=here; r.log=here/'private.log'
    r.directory='/opt/exporter-phase4-pilot/'+args.run+'-619'
    r.folder='/mnt/storage/mailerblend-recovery/phase4/'+args.run+'/619'
    r.state=state; r.start=time.monotonic(); r.previous=r.start
    r.watch_mode=True  # Only read-only preflight while the exact historical HALT remains.
    old = state['manifest']
    for name, digest in old['file_sha256'].items():
        assert m.digest(here/'bundle'/name)==digest
    r.monitor=load('progressive-monitoring-transaction.py').Transaction(args.run,619,here/'monitoring')
    r.monitor.p.SSH=m.SSH
    r.monitor.baseline=json.loads((here/'monitoring/baseline.json').read_text())
    r.monitor.registry=registry
    r.monitor.state=json.loads((here/'monitoring/state.json').read_text())
    assert r.monitor.state['offhost_verified']
    assert m.digest(here/'monitoring/integration-before.tar')==r.monitor.state['sha256']
    assert r.remote('import hashlib,pathlib\nprint(hashlib.sha256(pathlib.Path('+repr(r.monitor.folder+'/integration-before.tar')+').read_bytes()).hexdigest())').strip()==r.monitor.state['sha256']
    r.monitor.manifest=json.loads(r.monitor.p.remote(r.monitor.p.ct('from pathlib import Path\nprint((Path('+repr(r.monitor.p.CTDIR)+')/"manifest.json").read_text())')))
    r.monitor.p.helper('validate')  # Checks live configuration identities and backup proof.
    remote_digest=r.remote('import hashlib,pathlib\nprint(hashlib.sha256(pathlib.Path('+repr(r.folder+'/exporters-before.tar')+').read_bytes()).hexdigest())').strip()
    assert remote_digest==state['backup']['sha256']
    probe='''import pathlib,json,subprocess,urllib.request
d=pathlib.Path(DIRECTORY)
base=json.loads((d/'baseline.json').read_text())
for name, old in base['exporters'].items():
 now=json.loads(subprocess.check_output(['docker','inspect',name]))[0]
 assert now['Id']==old['Id'] and now['Image']==old['Image'] and now['State']['Running'] and not now['State']['OOMKilled']
for name in HELD_NAMES:
 held=json.loads(subprocess.check_output(['docker','inspect',name+'-phase4-619-held']))[0]
 assert not held['State']['Running']
REJECTED_CHECK
with urllib.request.urlopen('http://192.168.1.119:15678/healthz',timeout=10) as response:assert response.status==200
assert subprocess.run(['docker','exec','infra-pulpo-postgres-1','pg_isready','-h','127.0.0.1','-p','5432'],capture_output=True,timeout=10).returncode==0
print('Originals and applications ready; held candidates preserved')
'''.replace('DIRECTORY',repr(r.directory)).replace('HELD_NAMES',repr(['node_exporter'] if args.retry_compose_identity else ['node_exporter','cadvisor'])).replace('REJECTED_CHECK',"rejected=json.loads((d/'rejected-candidates.json').read_text());assert len(rejected)==1\nc=json.loads(subprocess.check_output(['docker','inspect',rejected[0]['name']]))[0]\nassert c['Id']==rejected[0]['id'] and not c['State']['Running']" if args.retry_compose_identity or args.retry_cpu_alignment else "assert not (d/'rejected-candidates.json').exists()")
    r.remote(r.ctcode(probe)); r.namespace()
    resources=json.loads(r.remote("import pathlib,json,subprocess\np=pathlib.Path('/sys/fs/cgroup/lxc/619')\nc=dict(l.split(': ',1) for l in subprocess.check_output(['pct','config','619'],text=True).splitlines() if ': ' in l)\nassert c['cores']=='2' and c['memory']=='2048'\nprint(json.dumps({n:(p/n).read_text().strip() for n in ['memory.events','memory.max','memory.pressure']}))"))
    assert int(resources['memory.max'])==2048*1024**2
    assert all(float(x)<=5 for x in m.re.findall(r'avg(?:10|60)=(\S+)',resources['memory.pressure']))
    def counters(text):return dict(line.split() for line in text.splitlines())
    assert all(counters(resources['memory.events'])[k]==counters(state['resources_before']['memory.events'])[k] for k in ['oom','oom_kill','oom_group_kill'])
    with tempfile.TemporaryDirectory() as tmp:
        out=Path(tmp)
        manifest=load('prepare-619-recovery.py').render(out,audit)
        changed={n for n in manifest['file_sha256'] if old['file_sha256'].get(n)!=manifest['file_sha256'][n]}
        assert changed==({'sample.py','observe.py','cpu-alignment.py'} if args.retry_cpu_alignment else {'pilot.py'} if args.retry_compose_identity else {'pilot.py','cadvisor-limits.yml'})
        saved=here/('before-d029-cpu-alignment' if args.retry_cpu_alignment else 'before-d028-compose-identity' if args.retry_compose_identity else 'before-d028')
        saved.mkdir(mode=0o700,exist_ok=False)
        for name in ['state.json','baseline-sample.json','observations.jsonl']:
            if (here/name).exists():shutil.copy2(here/name,saved/name)
        shutil.copytree(here/'bundle',saved/'bundle')
        code='from pathlib import Path\nimport hashlib\nd=Path('+repr(r.directory)+')\n'
        for name in sorted(changed):
            body=(out/name).read_text()
            code+='p=d/'+repr(name)+'\n'
            if name in old['file_sha256']:code+='assert hashlib.sha256(p.read_bytes()).hexdigest()=='+repr(old['file_sha256'][name])+'\n'
            else:code+='assert not p.exists()\n'
            code+='p.write_text('+repr(body)+')\np.chmod(0o600)\n'
        # Archive the exact resolved marker, without accepting any different anomaly.
        assert m.digest(marker)==marker_hash
        marker.rename(root/('HALT.619-d028-observation-resolved.json' if args.retry_cpu_alignment else 'HALT.619-compose-identity-resolved.json' if args.retry_compose_identity else 'HALT.619-memory128-resolved.json'))
        r.watch_mode=False
        r.remote(r.ctcode(code))
        for name in changed:shutil.copy2(out/name,here/'bundle'/name)
        manifest.update(status='APPROVED_D028',approval_required=False)
        m.save(here/'bundle/manifest.json',manifest)
        r.manifest=manifest; r.state['manifest']=manifest
    if (here/'observations.jsonl').exists():(here/'observations.jsonl').rename(saved/'observations-original.jsonl')
    r.state['result']='IN_PROGRESS'; r.state['recovery_authorization']='D-029' if args.retry_cpu_alignment else 'D-028'
    if args.retry_cpu_alignment:
        for field in ['blocked_reason','failure_type','failed_observation']:
            if field in r.state:r.state.setdefault('resolved_d028_fields',{})[field]=r.state.pop(field)
    r.mark('d028_preflight_and_backups_revalidated')
    try:
        if args.retry_cpu_alignment:r.start_cpu_history()
        elif not args.retry_compose_identity:r.helper('revise-cadvisor');r.mark('cadvisor128_preserved_stopped')
        r.mutate(); r.observe_and_telegram(); r.finish()
        m.start_watch(args.run,619,root)
    except BaseException as exc:
        r.state['result']='BLOCKED';r.state['failure_type']=type(exc).__name__
        m.save(here/'state.json',r.state)
        if not (root/'HALT.json').exists():m.save(root/'HALT.json',{'ct':619,'reason':'d028_recovery_gate_failure','failure_type':type(exc).__name__})
        raise
    finally:load('report-approved-rollout.py').update(args.run)

if __name__=='__main__':main()
