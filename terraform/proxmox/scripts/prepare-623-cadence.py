#!/usr/bin/env python3
"""D030: propuesta local exclusiva623; sin SSH ni despliegue, aprobación nueva requerida."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import yaml

ROOT=Path(__file__).resolve().parents[1]
def render(out,audit):
    assert audit['ct']==623 and audit['hostname']=='infra-gestoria'
    spec=importlib.util.spec_from_file_location('approved',ROOT/'scripts/prepare-approved-exporters.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    out=Path(out);assert not out.exists() or not any(out.iterdir()),'Only an empty proposal directory may be used'
    manifest=m.render(623,out,audit)
    path=out/'cadvisor.yml';config=yaml.safe_load(path.read_text());args=config['services']['cadvisor']['command']
    assert '--housekeeping_interval=30s' in args
    args+=['--allow_dynamic_housekeeping=false','--max_housekeeping_interval=30s','--jitter_factor=0','--initial_splay_factor=0']
    path.write_text(yaml.safe_dump(config,sort_keys=False))
    # Renaming a held container does not remove its Compose project labels.
    helper=out/'pilot.py';body=helper.read_text();old="return PROJECT + '-cadvisor-containerd' if name == 'cadvisor'";assert body.count(old)==1
    body=body.replace(old,"return PROJECT + '-cadvisor-containerd-cadence30' if name == 'cadvisor'")
    old="[PROJECT, PROJECT+'-cadvisor-containerd', PROJECT+'-node-cgroup']";assert body.count(old)==1
    body=body.replace(old,"[PROJECT, PROJECT+'-cadvisor-containerd', PROJECT+'-cadvisor-containerd-cadence30', PROJECT+'-node-cgroup']");helper.write_text(body)
    manifest.update(status='PREPARED_NOT_DEPLOYED_D030',approval_required=True,initial_seconds=600,initial_minimum_samples=21,automatic_continuation=False)
    manifest['file_sha256']={n:hashlib.sha256((out/n).read_bytes()).hexdigest() for n in manifest['file_sha256']}
    for n in manifest['file_sha256']:
        if n.endswith('.py'):compile((out/n).read_text(),n,'exec')
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');return manifest

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    rows=json.loads((ROOT/'docs/roadmap/evidence/2026-11-02-rollout-authenticated-preflight.json').read_text())
    print(json.dumps(render(a.output,next(r for r in rows if r['ct']==623)),indent=2))
