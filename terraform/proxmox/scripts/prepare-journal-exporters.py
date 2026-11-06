#!/usr/bin/env python3
"""Render ONLY local, CT-specific exporter bundles. Never connects or deploys."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

ROOT=Path(__file__).resolve().parents[1]
TARGETS={625:('infra-journal-db','192.168.1.125'),626:('infra-journal-api','192.168.1.126')}


def render(ct,output):
    if ct not in TARGETS:raise ValueError('Only CT 625/626 may be prepared')
    output=Path(output)
    hostname,ip=TARGETS[ct]
    # Preserve the accepted CT624 helper and its exact deployed inputs unchanged.
    original=ROOT/'scripts/exporter-pilot-624.py'
    evidence=json.loads((ROOT/'docs/roadmap/evidence/2026-11-02-pilot624-artifacts.json').read_text())
    assert hashlib.sha256(original.read_bytes()).hexdigest()==evidence['sha256']['scripts/exporter-pilot-624.py']
    helper=original.read_text().replace('624',str(ct)).replace('192.168.1.124',ip).replace('infra-journal-web',hostname)
    helper=helper.replace("mem['MemTotal'] == 512 * 1024 and cpus == 1","mem['MemTotal'] == 2048 * 1024 and cpus == 2")
    helper=helper.replace("mem['MemAvailable'] >= 128 * 1024","mem['MemAvailable'] >= 512 * 1024")
    helper=helper.replace("value('lxc_cpu_capacity_cores')==1","value('lxc_cpu_capacity_cores')==2")
    helper=helper.replace("== 512 * 1024 * 1024","== 2048 * 1024 * 1024")
    helper=helper.replace('== 1\n                assert float(re.search', '== 2\n                assert float(re.search')
    if ct==626:
        helper=helper.replace(":8090/",":3000/health")
    else:
        a=helper.index('def web():');b=helper.index('\n\ndef scope_guard',a)
        helper=helper[:a]+'''def web():
    # Local, read-only PostgreSQL readiness; not a SQL integrity/restore claim.
    result=subprocess.run(['docker','exec','infra-journal-db-db-1','pg_isready','-h','127.0.0.1','-p','5432'],capture_output=True,timeout=10)
    assert result.returncode==0, 'PostgreSQL readiness failed'
    return {'postgres_ready':True}
''' +helper[b:]
    helper=helper.replace("def apply(directory):\n", "def containerd_socket_ready():\n    import stat\n    return stat.S_ISSOCK(Path('/run/containerd/containerd.sock').stat().st_mode)\n\ndef apply(directory):\n    assert ALLOW_CONTAINERD_SOCKET and USE_LXC_CGROUP_CPU, 'Reviewed socket and CPU contract flags required'\n    assert containerd_socket_ready(), 'Missing containerd socket'\n")
    # Readiness counter tolerance accounts for two assigned cores over writer age.
    helper=helper.replace('<=max(1,age+1)','<=max(1,2*(age+1))')
    files={'pilot.py':helper}
    for name,source in [('node.yml','services/common/node-exporter/docker-compose.phase4.yml'),('cadvisor.yml','services/common/cadvisor/docker-compose.phase4.yml')]:files[name]=(ROOT/source).read_text()
    for name in ['node-limits.yml','cadvisor-limits.yml','cadvisor-containerd.yml','node-cgroup.yml']:
        files[name]=(ROOT/'services/common/pilot-624'/name).read_text()
    collector=(ROOT/'services/common/pilot-624/node-cgroup.sh').read_text().replace('infra-journal-web',hostname).replace('624',str(ct)).replace(' = 1 ]',' = 2 ]').replace('cores%s 1\\n','cores%s 2\\n')
    # Reject malformed or negative counters rather than coercing them to zero in awk.
    collector=collector.replace('if (!have_total || !have_user || !have_system) exit 1','if (!have_total || !have_user || !have_system || total !~ /^[0-9]+$/ || user !~ /^[0-9]+$/ || system_cpu !~ /^[0-9]+$/) exit 1')
    files['node-cgroup.sh']=collector
    sampler=(ROOT/'scripts/sample-exporter-pilot-624.py').read_text().replace('624',str(ct)).replace('192.168.1.124',ip).replace('infra-journal-web',hostname)
    if ct==626:sampler=sampler.replace(':8090/',':3000/health')
    else:
        sampler=sampler.replace("    web=fetch('http://'+IP+':8090/')\n    out['web']={'status':200,'sha256':hashlib.sha256(web).hexdigest()}","    ready=subprocess.run(['docker','exec','infra-journal-db-db-1','pg_isready','-h','127.0.0.1','-p','5432'],capture_output=True,timeout=10)\n    assert ready.returncode==0, 'PostgreSQL readiness failed'\n    out['web']={'status':200,'postgres_ready':True}")
    files['sample.py']=sampler
    observer=(ROOT/'scripts/observe-exporter-pilot-624.py').read_text().replace('624',str(ct)).replace('512*1024*1024','2048*1024*1024').replace("['cpu_count']==1","['cpu_count']==2").replace("node_value('lxc_cpu_capacity_cores')==1","node_value('lxc_cpu_capacity_cores')==2").replace('max(1,age+2)','max(1,2*(age+2))').replace('64*1024*1024','256*1024*1024')
    if ct==625:observer=observer.replace('infra-journal-web-web-1','infra-journal-db-db-1').replace("=='web'","=='db'").replace("=='infra-journal-web'","=='infra-journal-db'")
    else:observer=observer.replace('infra-journal-web-web-1','infra-journal-api-api-1').replace("=='web'","=='api'").replace("=='infra-journal-web'","=='infra-journal-api'")
    files['observe.py']=observer

    output.mkdir(parents=True,exist_ok=True)
    # Refuse accidental reuse of a production/private snapshot directory.
    assert not any((output/n).exists() for n in ['baseline.json','applied.json','external-backup-verified.json']), 'Not a preparation-only directory'
    for name,body in files.items():(output/name).write_text(body)
    manifest={'ct':ct,'hostname':hostname,'ip':ip,'allocated_cores':2,'allocated_memory_mib':2048,'status':'PREPARED_NOT_DEPLOYED','containerd_socket_approval_required':True,'files':{name:hashlib.sha256(body.encode()).hexdigest() for name,body in sorted(files.items())}}
    (output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--ct',type=int,choices=TARGETS,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();print(json.dumps(render(a.ct,a.output),indent=2))
