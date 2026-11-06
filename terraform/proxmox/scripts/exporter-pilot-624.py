#!/usr/bin/env python3
"""Conservative exporter-only pilot. Must run inside CT 624; never removes a container."""
import argparse
import hashlib
import json
import itertools
import os
from pathlib import Path
import re
import shutil
import socket
import subprocess
import tarfile
import time
import urllib.request

IP = '192.168.1.124'
NODE_IMAGE = 'prom/node-exporter@sha256:3ac34ce007accad95afed72149e0d2b927b7e42fd1c866149b945b84737c62c3'
CAD_IMAGE = 'ghcr.io/google/cadvisor@sha256:b8e7d1093144fd088f425ff003d75a4aa405de075db78dae3bc563730b1bd07a'
SERVICES = {'node_exporter': ('node.yml', 'node-limits.yml', NODE_IMAGE, 9100),
            'cadvisor': ('cadvisor.yml', 'cadvisor-limits.yml', CAD_IMAGE, 8085)}
PROJECT = 'exporter-pilot-624'
ALLOW_CONTAINERD_SOCKET = False
USE_LXC_CGROUP_CPU = False


def run(args, **kwargs):
    r = subprocess.run(args, capture_output=True, timeout=180, **kwargs)
    if r.returncode:
        raise RuntimeError('Command failed: ' + args[0] + ' ' + args[1])
    return r.stdout


def docker_info(name):
    r = subprocess.run(['docker', 'inspect', name], capture_output=True, timeout=15)
    return json.loads(r.stdout)[0] if r.returncode == 0 else None


def save(path, data):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, 'w') as f:
        json.dump(data, f, indent=2); f.write('\n')


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''):h.update(b)
    return h.hexdigest()


def config_hash(c, mounts=None):
    mounts = sorted(c['Mounts'], key=lambda m: (m.get('Destination',''), m.get('Source',''))) if mounts is None else mounts
    return hashlib.sha256(json.dumps([c['Config'],c['HostConfig'],mounts],sort_keys=True).encode()).hexdigest()


def identities():
    ids = run(['docker', 'ps', '-aq']).decode().split()
    data = json.loads(run(['docker', 'inspect'] + ids)) if ids else []
    return sorted([{'name': c['Name'].lstrip('/'), 'id': c['Id'], 'image': c['Image'],
             'started_at': c['State']['StartedAt'], 'running': c['State']['Running'],
             'config_hash': config_hash(c)}
            for c in data if not c['Name'].lstrip('/').startswith(('node_exporter', 'cadvisor'))], key=lambda c: c['name'])


def web():
    with urllib.request.urlopen('http://' + IP + ':8090/', timeout=5) as r:
        assert r.status == 200
        return {'status': r.status, 'sha256': hashlib.sha256(r.read()).hexdigest()}


def scope_guard():
    assert socket.gethostname() == 'infra-journal-web', 'Wrong target hostname'
    links = json.loads(run(['ip', '-j', 'addr']))
    assert any(a.get('local') == IP for n in links for a in n.get('addr_info', [])), 'Wrong target IP'


def capacity():
    mem = dict((k, int(v)) for k, v in re.findall(r'^(MemTotal|MemAvailable):\s+(\d+)', Path('/proc/meminfo').read_text(), re.M))
    cpus = len(re.findall(r'^cpu\d+ ', Path('/proc/stat').read_text(), re.M))
    free = shutil.disk_usage('/').free
    assert mem['MemTotal'] == 512 * 1024 and cpus == 1, 'Unexpected CT allocation'
    assert mem['MemAvailable'] >= 128 * 1024 and free >= 1024 ** 3, 'Insufficient memory/storage margin'
    return {'lxc_mem_total_kib': mem['MemTotal'], 'lxc_mem_available_kib': mem['MemAvailable'], 'lxc_cpus': cpus, 'free_bytes': free}


def project(name):
    if name == 'node_exporter' and USE_LXC_CGROUP_CPU:return PROJECT + '-node-cgroup'
    return PROJECT + '-cadvisor-containerd' if name == 'cadvisor' and ALLOW_CONTAINERD_SOCKET else PROJECT


def managed(c):
    return (c['Config'].get('Labels') or {}).get('com.docker.compose.project') in [PROJECT, PROJECT+'-cadvisor-containerd', PROJECT+'-node-cgroup']


def compose(directory, name):
    config, limits, _, _ = SERVICES[name]
    cmd = ['docker', 'compose', '--project-name', project(name), '--project-directory', str(directory),
            '-f', str(directory / config), '-f', str(directory / limits)]
    if name == 'cadvisor' and ALLOW_CONTAINERD_SOCKET:
        assert (directory / 'cadvisor-containerd.yml').is_file(), 'Missing reviewed socket overlay'
        cmd += ['-f', str(directory / 'cadvisor-containerd.yml')]
    if name == 'node_exporter' and USE_LXC_CGROUP_CPU:
        assert (directory / 'node-cgroup.yml').is_file() and (directory / 'node-cgroup.sh').is_file()
        cmd += ['-f', str(directory / 'node-cgroup.yml')]
    return cmd


def model(directory, name):
    env = dict(os.environ, EXPORTER_BIND_IP=IP, NODE_EXPORTER_IMAGE=NODE_IMAGE)
    data = json.loads(run(compose(directory, name) + ['config', '--format', 'json'], env=env))
    assert set(data['services']) == {name}, 'Refusing non-exporter service'
    s = data['services'][name]
    assert s['image'] == SERVICES[name][2] and s['pull_policy'] == 'never'
    assert s.get('container_name') == name
    assert not any(s.get(k) for k in ['cap_add', 'security_opt', 'devices', 'network_mode']), 'Unreviewed privileges'
    assert bool(s.get('privileged')) == (name == 'cadvisor')
    if name == 'cadvisor':assert s['cgroup'] == 'host'
    assert all(v.get('read_only') for v in s.get('volumes', [])), 'Writable host mount refused'
    assert int(s['mem_limit']) == (48 if name == 'node_exporter' else 128) * 1024 * 1024, 'Unexpected exporter memory limit'
    fingerprint = json.dumps(data, sort_keys=True).encode()
    if name == 'node_exporter' and USE_LXC_CGROUP_CPU:fingerprint += digest(directory / 'node-cgroup.sh').encode()
    return data, hashlib.sha256(fingerprint).hexdigest()


def verify_archive(path):
    count = 0
    with tarfile.open(path) as archive:
        for member in archive:
            if not member.isfile():continue
            stream = archive.extractfile(member); h = hashlib.sha256()
            for chunk in iter(lambda: stream.read(1024 * 1024), b''):h.update(chunk)
            if re.fullmatch(r'blobs/sha256/[a-f0-9]{64}', member.name):
                assert h.hexdigest() == member.name.rsplit('/', 1)[1], 'Image blob checksum mismatch'
            count += 1
    assert count > 0
    return {'sha256': digest(path), 'bytes': path.stat().st_size, 'verified_files': count}


def snapshot(directory):
    assert not (directory / 'baseline.json').exists(), 'Use a fresh snapshot directory'
    directory.mkdir(parents=True, mode=0o700, exist_ok=True); directory.chmod(0o700)
    baseline = {'ct': 624, 'capacity': capacity(), 'applications': identities(), 'web': web(), 'exporters': {}, 'archives': {}}
    for name in SERVICES:
        model(directory, name)
        original = docker_info(name)
        baseline['exporters'][name] = original
        if original:
            assert original['State']['Running'], 'Original exporter not running'
            if name == 'cadvisor':assert original['HostConfig']['Privileged'], 'Privilege increase refused'
            assert (original['Config'].get('Labels') or {}).get('com.docker.compose.project') != PROJECT
            image = original['Image']
            archive = directory / ('original-' + name + '.tar')
            with archive.open('wb') as f:
                result = subprocess.run(['docker', 'image', 'save', image], stdout=f, stderr=subprocess.PIPE, timeout=180)
                assert result.returncode == 0, 'Image backup failed'
            archive.chmod(0o600)
            baseline['archives'][archive.name] = verify_archive(archive)
            # Re-load the verified archive into the store without restarting any service.
            run(['docker', 'image', 'load', '--input', str(archive)])
            assert docker_info(name)['Image'] == image
    for name in ['cadvisor', 'node-exporter']:
        src = Path('/opt/common') / name
        if src.is_dir():shutil.copytree(src, directory / ('config-' + name))
    save(directory / 'baseline.json', baseline)
    print('Snapshot verified: original image archive/load, private configs and application identities.')


def unchanged(directory):
    baseline = json.loads((directory / 'baseline.json').read_text())
    actual = {x['name']:x for x in identities()}
    expected = {x['name']:x for x in baseline['applications']}
    assert actual.keys() == expected.keys(), 'Application set changed'
    for name, previous in expected.items():
        now = actual[name]
        assert {k:v for k,v in now.items() if k!='config_hash'} == {k:v for k,v in previous.items() if k!='config_hash'}, 'Application identity/state changed'
        if now['config_hash'] != previous['config_hash']:
            # The initial snapshot used Docker's unstable mount-array order. Accept
            # only an exact prior hash of the same Config/HostConfig/mount contents.
            c = docker_info(name)
            assert len(c['Mounts']) <= 4
            compatible = {config_hash(c,list(order)) for order in itertools.permutations(c['Mounts'])}
            assert previous['config_hash'] in compatible, 'Application configuration changed'
    assert web() == baseline['web'], 'Journal Web response changed'


def stop(name):
    c = docker_info(name)
    if c and c['State']['Running']:
        # No SIGKILL fallback.
        r = subprocess.run(['docker', 'stop', '-t', '-1', name], capture_output=True, timeout=60)
        assert r.returncode == 0, 'Orderly stop failed'


def metrics(name):
    with urllib.request.urlopen('http://' + IP + ':' + str(SERVICES[name][3]) + '/metrics', timeout=5) as r:
        assert r.status == 200
        return r.read().decode()


def ready(name):
    deadline = time.monotonic() + int(os.environ.get('READINESS_TIMEOUT', '120'))
    while time.monotonic() < deadline:
        try:
            c = docker_info(name)
            assert c and c['State']['Running'] and c['State']['OOMKilled'] is False
            text = metrics(name)
            if name == 'node_exporter':
                if USE_LXC_CGROUP_CPU:
                    def value(metric):
                        return float(re.search(r'^'+metric+r'(?:\{[^}]*\})? (\S+)',text,re.M).group(1))
                    assert not re.search(r'^node_cpu_seconds_total\{',text,re.M)
                    assert value('lxc_cpu_collector_success')==1 and value('lxc_cpu_capacity_cores')==1
                    age=time.time()-value('lxc_cpu_collector_timestamp_seconds')
                    assert -2<=age<=15
                    direct=dict(l.split() for l in Path('/sys/fs/cgroup/cpu.stat').read_text().splitlines())
                    assert abs(value('lxc_cpu_usage_seconds_total')-int(direct['usage_usec'])/1e6)<=max(1,age+1)
                else:
                    assert len(re.findall(r'^node_cpu_seconds_total\{[^\n]*mode="idle"', text, re.M)) == 1
                assert float(re.search(r'^node_memory_MemTotal_bytes (\S+)', text, re.M).group(1)) == 512 * 1024 * 1024
            else:
                ids=run(['docker','ps','-q']).decode().split()
                expected={x['Id'] for x in json.loads(run(['docker','inspect']+ids))}
                for prefix in ['container_memory_usage_bytes{', 'container_cpu_usage_seconds_total{']:
                    metric_ids = {m.group(1) for line in text.splitlines() if line.startswith(prefix)
                             if (m := re.search(r'(?:^|[,{}])id="([^"\n]+)"', line))}
                    assert all(any(cid in path for path in metric_ids) for cid in expected)
            return
        except (AssertionError, OSError, ValueError, AttributeError):time.sleep(2)
    raise RuntimeError('Readiness/metric-quality timeout: ' + name)


def apply(directory):
    baseline = json.loads((directory / 'baseline.json').read_text())
    proof = json.loads((directory / 'external-backup-verified.json').read_text())
    assert proof['offhost_verified'] is True and proof['archives'] == baseline['archives']
    unchanged(directory); capacity()
    records = json.loads((directory / 'applied.json').read_text()) if (directory / 'applied.json').exists() else {}
    for name in SERVICES:
        _, planned = model(directory, name)
        image = json.loads(run(['docker', 'image', 'inspect', SERVICES[name][2]]))[0]

        current = docker_info(name)
        preserved = name + '-pre-phase4-624'
        held = name + '-phase4-624-held'
        if current and (current['Config'].get('Labels') or {}).get('com.docker.compose.project') != project(name):
            assert baseline['exporters'][name] and current['Id'] == baseline['exporters'][name]['Id']
            assert not docker_info(preserved), 'Original name already occupied'
            stop(name); run(['docker', 'rename', name, preserved]); current = None
        if not current and docker_info(held):
            h = docker_info(held)
            assert records.get(name) == {'hash': planned, 'id': h['Id']}, 'Held candidate differs'
            run(['docker', 'rename', held, name]); current = docker_info(name)
        if current:
            assert records.get(name) == {'hash': planned, 'id': current['Id']}, 'Refusing implicit recreation/model drift'
        env = dict(os.environ, EXPORTER_BIND_IP=IP, NODE_EXPORTER_IMAGE=NODE_IMAGE)
        run(compose(directory, name) + ['up', '-d', '--no-deps', '--no-recreate', '--no-build', '--pull', 'never', name], env=env)
        current = docker_info(name)
        assert current['Image'] == image['Id'], 'Unexpected image identity'
        assert current['HostConfig']['Memory'] == (48 if name == 'node_exporter' else 128) * 1024 * 1024
        assert current['HostConfig']['NanoCpus'] == (200000000 if name == 'node_exporter' else 500000000)
        assert all(not m['RW'] for m in current['Mounts']), 'Writable runtime mount'
        records[name] = {'hash': planned, 'id': current['Id']}
        save(directory / 'applied.json', records)
        ready(name); unchanged(directory)
        print('Applied and checked:', name)


def rollback(directory):
    baseline = json.loads((directory / 'baseline.json').read_text())
    # Rollback must remain usable when an application readiness check has failed.
    rejected = directory / 'rejected-candidates.json'
    if rejected.exists():
        for item in json.loads(rejected.read_text()):
            c = docker_info(item['name'])
            assert c and c['Id'] == item['id'] and managed(c)
            stop(item['name'])
    for name in reversed(list(SERVICES)):
        current = docker_info(name)
        if current and managed(current):
            assert not docker_info(name + '-phase4-624-held')
            stop(name); run(['docker', 'rename', name, name + '-phase4-624-held'])
        original = baseline['exporters'][name]
        if original:
            kept = docker_info(name + '-pre-phase4-624')
            if kept:
                assert kept['Id'] == original['Id']; run(['docker', 'rename', kept['Id'], name])
            assert docker_info(name)['Id'] == original['Id']
            run(['docker', 'start', name])
        else:assert docker_info(name) is None
    unchanged(directory)
    print('Rollback verified: original identities restored, new exporters retained stopped.')


def revise_cadvisor(directory):
    assert ALLOW_CONTAINERD_SOCKET, 'Explicit socket approval flag required'
    unchanged(directory)
    baseline = json.loads((directory / 'baseline.json').read_text())
    records = json.loads((directory / 'applied.json').read_text())
    current = docker_info('cadvisor')
    assert current and current['Id'] == baseline['exporters']['cadvisor']['Id'], 'Restore original first'
    held = docker_info('cadvisor-phase4-624-held')
    assert held and not held['State']['Running'] and held['Id'] == records['cadvisor']['id']
    _, planned = model(directory, 'cadvisor')
    assert planned != records['cadvisor']['hash'], 'No revision needed'
    file = directory / 'rejected-candidates.json'
    rejected = json.loads(file.read_text()) if file.exists() else []
    name = 'cadvisor-phase4-624-rejected-' + str(len(rejected)+1)
    assert not docker_info(name)
    run(['docker','rename',held['Id'],name])
    rejected.append({'name':name,'id':held['Id'],'image':held['Image'],'previous_model':records['cadvisor']['hash']})
    save(file,rejected)
    print('Previous candidate preserved stopped; explicit revised model can now be applied.')


def revise_node(directory):
    assert USE_LXC_CGROUP_CPU, 'Explicit cgroup-CPU variant required'
    unchanged(directory)
    records=json.loads((directory/'applied.json').read_text())
    current=docker_info('node_exporter')
    assert current and managed(current) and current['Id']==records['node_exporter']['id']
    assert (current['Config'].get('Labels') or {}).get('com.docker.compose.project')!=project('node_exporter')
    _, planned=model(directory,'node_exporter')
    assert planned!=records['node_exporter']['hash']
    file=directory/'rejected-candidates.json'
    rejected=json.loads(file.read_text()) if file.exists() else []
    name='node_exporter-phase4-624-rejected-'+str(len(rejected)+1)
    assert not docker_info(name)
    stop('node_exporter');run(['docker','rename','node_exporter',name])
    rejected.append({'name':name,'id':current['Id'],'image':current['Image'],'previous_model':records['node_exporter']['hash']})
    save(file,rejected)
    print('Physical-CPU candidate preserved stopped; explicit LXC CPU revision prepared.')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('action', choices=['snapshot', 'apply', 'rollback', 'check', 'revise-cadvisor', 'revise-node'])
    p.add_argument('--directory', type=Path, required=True)
    p.add_argument('--execute', action='store_true')
    p.add_argument('--allow-containerd-socket', action='store_true', help='Use only after explicit approval of the socket overlay')
    p.add_argument('--use-lxc-cgroup-cpu', action='store_true', help='Pilot-only nonprivileged CPU textfile collector; never change PVE/LXCFS')
    args = p.parse_args()
    if not args.execute:p.error('Explicit --execute required')
    scope_guard()
    global ALLOW_CONTAINERD_SOCKET, USE_LXC_CGROUP_CPU
    ALLOW_CONTAINERD_SOCKET = args.allow_containerd_socket
    USE_LXC_CGROUP_CPU = args.use_lxc_cgroup_cpu
    directory = args.directory.resolve()
    assert directory.is_relative_to('/opt/exporter-phase4-pilot'), 'Wrong pilot directory'
    if args.action == 'snapshot':snapshot(directory)
    elif args.action == 'apply':apply(directory)
    elif args.action == 'rollback':rollback(directory)
    elif args.action == 'revise-cadvisor':revise_cadvisor(directory)
    elif args.action == 'revise-node':revise_node(directory)
    else:
        unchanged(directory)
        for name in SERVICES:ready(name)
        print('Application identities/web and exporter metric quality verified.')


if __name__ == '__main__':
    try:main()
    except Exception as exc:
        import traceback
        line = traceback.extract_tb(exc.__traceback__)[-1].lineno
        print('Pilot stopped safely at helper line', line, type(exc).__name__, str(exc) if isinstance(exc, (AssertionError, RuntimeError)) else 'private details withheld', flush=True)
        raise SystemExit(1)
