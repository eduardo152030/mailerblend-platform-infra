#!/usr/bin/env python3
"""LOCAL ONLY proposal: CT619 cAdvisor256MiB. No SSH, downloads or deployment."""
import argparse,hashlib,importlib.util,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def render(output,audit):
 assert audit['ct']==619 and audit['hostname']=='infra-pulpo'
 spec=importlib.util.spec_from_file_location('approved',ROOT/'scripts/prepare-approved-exporters.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 output=Path(output);assert not any((output/n).exists() for n in ['baseline.json','applied.json','external-backup-verified.json'])
 manifest=m.render(619,output,audit)
 limits=output/'cadvisor-limits.yml';body=limits.read_text();assert 'mem_limit: 128m' in body;limits.write_text(body.replace('mem_limit: 128m','mem_limit: 256m'))
 helper=output/'pilot.py';body=helper.read_text();old="(48 if name == 'node_exporter' else 128)";assert body.count(old)==2;body=body.replace(old,"(48 if name == 'node_exporter' else 256)")
 # Compose finds renamed containers by labels: a revised model needs its own project.
 old_project="return PROJECT + '-cadvisor-containerd' if name == 'cadvisor'"
 assert body.count(old_project)==1
 body=body.replace(old_project,"return PROJECT + '-cadvisor-containerd-m256' if name == 'cadvisor'")
 old_managed="[PROJECT, PROJECT+'-cadvisor-containerd', PROJECT+'-node-cgroup']"
 assert body.count(old_managed)==1
 body=body.replace(old_managed,"[PROJECT, PROJECT+'-cadvisor-containerd', PROJECT+'-cadvisor-containerd-m256', PROJECT+'-node-cgroup']")
 helper.write_text(body)
 manifest.update(status='PROPOSED_NOT_DEPLOYED_APPROVAL_REQUIRED',cadvisor_memory_mib=256,previous_cadvisor_memory_mib=128,initial_seconds=600,initial_minimum_samples=21,approval_required=True,applications_or_proxmox_resources_changed=False)
 manifest['file_sha256']={n:hashlib.sha256((output/n).read_bytes()).hexdigest() for n in manifest['file_sha256']}
 for name in manifest['file_sha256']:
  if name.endswith('.py'):compile((output/name).read_text(),name,'exec')
 (output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');return manifest
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();audits=json.loads((ROOT/'docs/roadmap/evidence/2026-11-02-rollout-authenticated-preflight.json').read_text());print(json.dumps(render(a.output,next(r for r in audits if r['ct']==619)),indent=2))
