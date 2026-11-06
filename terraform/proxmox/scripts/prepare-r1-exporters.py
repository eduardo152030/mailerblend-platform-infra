#!/usr/bin/env python3
"""Prepare CT613 only, locally. Requires approval before any use on the server."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def render(output):
    output=Path(output)
    original=ROOT/'scripts/exporter-pilot-624.py'
    approved=json.loads((ROOT/'docs/roadmap/evidence/2026-11-02-pilot624-artifacts.json').read_text())
    assert hashlib.sha256(original.read_bytes()).hexdigest()==approved['sha256']['scripts/exporter-pilot-624.py']
    lock=json.loads((ROOT/'services/common/phase4-images.json').read_text())
    assert lock['node']['infra-hola']['image']=='prom/node-exporter@sha256:3ac34ce007accad95afed72149e0d2b927b7e42fd1c866149b945b84737c62c3'
    def adapt(s):return s.replace('624','613').replace('192.168.1.124','192.168.1.113').replace('infra-journal-web','infra-hola')
    helper=adapt(original.read_text());a=helper.index('def web():');b=helper.index('\n\ndef scope_guard',a)
    helper=helper[:a]+'''def web():
    assert not identities(), 'Unexpected application: review scope before deployment'
    assert set(run(['docker','ps','--format','{{.Names}}']).decode().split()) <= {'node_exporter','cadvisor'}, 'Unexpected running container, including exporter-like names'
    return {'no_application_baseline':True}
''' +helper[b:]
    helper=helper.replace('def apply(directory):\n',"def apply(directory):\n    assert ALLOW_CONTAINERD_SOCKET and USE_LXC_CGROUP_CPU, 'Explicit reviewed socket/CPU flags required'\n    assert Path('/run/containerd/containerd.sock').is_socket(), 'Socket missing; never create it'\n    assert all(Path(p).is_dir() for p in ['/var/lib/docker','/var/lib/containerd','/sys']), 'Required host directory absent; never create it'\n")
    files={'pilot.py':helper}
    for name,source in [('node.yml','node-exporter/docker-compose.phase4.yml'),('cadvisor.yml','cadvisor/docker-compose.phase4.yml')]:files[name]=(ROOT/'services/common'/source).read_text()
    for n in ['node-limits.yml','cadvisor-limits.yml','cadvisor-containerd.yml','node-cgroup.yml']:files[n]=(ROOT/'services/common/pilot-624'/n).read_text()
    files['node-cgroup.sh']=adapt((ROOT/'services/common/pilot-624/node-cgroup.sh').read_text()).replace('if (!have_total || !have_user || !have_system) exit 1','if (!have_total || !have_user || !have_system || total !~ /^[0-9]+$/ || user !~ /^[0-9]+$/ || system_cpu !~ /^[0-9]+$/) exit 1')
    sample=adapt((ROOT/'scripts/sample-exporter-pilot-624.py').read_text())
    sample=sample.replace("    web=fetch('http://'+IP+':8090/')\n    out['web']={'status':200,'sha256':hashlib.sha256(web).hexdigest()}","    assert all(c['name'].startswith(('node_exporter','cadvisor')) for c in out['containers']), 'Unexpected application'\n    out['web']={'status':200,'type':'no_applications_in_baseline_not_http'}")
    files['sample.py']=sample
    observer=adapt((ROOT/'scripts/observe-exporter-pilot-624.py').read_text());a=observer.index("    web=next(r for r in sample['cadvisor']['container_memory_usage_bytes']")
    b=observer.index('\n\ndef main',a)
    observer=observer[:a]+'''    assert set(active)=={'node_exporter','cadvisor'}, 'Unexpected application'
    for name in active:
        r=next(x for x in sample['cadvisor']['container_memory_usage_bytes'] if x['labels'].get('name','').lstrip('/')==name)
        assert r['labels'].get('container_label_com_docker_compose_service')==name
''' +observer[b:];files['observe.py']=observer
    output.mkdir(parents=True,exist_ok=True)
    assert not any((output/f).exists() for f in ['baseline.json','applied.json']), 'Preparation must not overwrite a live run'
    for n,s in files.items():(output/n).write_text(s)
    manifest={'ct':613,'hostname':'infra-hola','ip':'192.168.1.113','status':'PREPARED_NOT_DEPLOYED','cores':1,'memory_mib':512,'original_exporters_to_preserve':['node_exporter','cadvisor'],'application_probe':'No application in audited baseline; abort if one appears','socket_approval':'PENDING_CT613','files':{n:hashlib.sha256(s.encode()).hexdigest() for n,s in files.items()}}
    (output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');return manifest


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();print(json.dumps(render(a.output),indent=2))
