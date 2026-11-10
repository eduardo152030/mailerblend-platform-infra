#!/usr/bin/env python3
"""Prepare an isolated copy of the SAME Terraform inventory module; never apply or reserve IPs."""
import argparse,copy,hashlib,json,os,shutil,subprocess,sys,re
from pathlib import Path
import yaml
from lxc_provisioning import validate,render_monitoring,inventory_document
ROOT=Path(__file__).resolve().parents[1]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def run(args,cwd):
 p=subprocess.run(args,cwd=cwd,capture_output=True,text=True)
 if p.returncode:
  log=Path(cwd).parent/'preparation.log';log.write_text(p.stdout+p.stderr);log.chmod(0o600)
  raise RuntimeError('Validation failed: '+args[0]+' '+args[1]+'; output stored only in bundle')
 return p.stdout+p.stderr

def prepare(spec,output):
 data=validate(yaml.safe_load(spec.read_text()));s=data['service'];key=s['name'];output=output.resolve()
 assert not output.exists(),'Output must be new; do not overwrite prior bundles'
 assert not output.is_relative_to(ROOT.resolve()),'Use a private staging path outside the working module'
 for f in (ROOT/'inventory/services').glob('*.yml'):
  old=yaml.safe_load(f.read_text())['service']
  assert s['vmid']!=old['vmid'] and s['name']!=old['name'] and s['ip'].split('/')[0]!=old['ip'].split('/')[0],'Existing identity/IP collision'
 output.mkdir(parents=True,mode=0o700);module=output/'terraform';module.mkdir()
 # Sources are copied, not a second hand-written Terraform module or state.
 sources=json.loads((ROOT/'inventory/generated/lxc-notes-manifest.json').read_text())
 metadata=yaml.safe_load((ROOT/'inventory/documentation.yml').read_text())
 names=set(sources)|{x['runbook'] for x in metadata['services'].values()}|{str(p.relative_to(ROOT)) for p in ROOT.glob('*.tf')}|{'inventory/generated/lxc-notes.json','inventory/generated/lxc-notes-manifest.json','.terraform.lock.hcl','templates/provisioning/install-monitoring.py'}
 for name in sorted(names):
  src=(ROOT/name).resolve();assert src.is_relative_to(ROOT.resolve())
  dest=module/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest)
 data=copy.deepcopy(data);data['documentation']={'inventory_file':f'docs/inventory/{s["vmid"]}-LXC-INVENTORY.md'}
 (module/f'inventory/services/{key}.yml').write_text(yaml.safe_dump(data,sort_keys=False))
 doc=module/f'docs/inventory/{s["vmid"]}-LXC-INVENTORY.md';doc.parent.mkdir(parents=True,exist_ok=True);doc.write_text(inventory_document(data,key))
 run(['python3',str(module/'scripts/generate-lxc-inventory.py'),'--root',str(module)],module)
 render_monitoring(data,output/'monitoring',ROOT)
 tests=module/'tests/provisioning';tests.mkdir(parents=True)
 (tests/'new-lxc.tftest.hcl').write_text('''# Offline test. mock_provider prevents Proxmox calls; command=plan only.
mock_provider "proxmox" {}
run "new_ct_plan" {
  command = plan
  plan_options { target = [proxmox_virtual_environment_container.svc["KEY"]] }
  variables {
    proxmox_endpoint  = "https://192.0.2.254:8006/"
    proxmox_api_token = "fixture-not-a-credential"
    node_name        = "fixture-node"
  }
  assert {
    condition = proxmox_virtual_environment_container.svc["KEY"].vm_id == CT
    error_message = "Wrong CT identity"
  }
  assert {
    condition = proxmox_virtual_environment_container.svc["KEY"].cpu[0].cores == CORES
    error_message = "Wrong CPU allocation"
  }
  assert {
    condition = strcontains(proxmox_virtual_environment_container.svc["KEY"].description, "PENDING VERIFICATION")
    error_message = "Undeployed state must remain explicit"
  }
  assert {
    condition = proxmox_virtual_environment_container.svc["KEY"].features[0].nesting == DOCKER
    error_message = "Docker capability mismatch"
  }
}
'''.replace('KEY',key).replace('CT',str(s['vmid'])).replace('CORES',str(data['resources']['cpu'])).replace('DOCKER',str(data['monitoring']['docker']).lower()))
 run(['terraform','fmt','-recursive'],module)
 manifest={'schema':1,'status':'PREPARED_NOT_DEPLOYED','service_key':key,'ct_id':s['vmid'],'hostname':s['name'],'declared':data,'provider_version':re.search(r'provider "registry.terraform.io/bpg/proxmox" \{.*?version\s*=\s*"([^"]+)"',(ROOT/'.terraform.lock.hcl').read_text(),re.S).group(1),'same_module_source_hashes':{p.name:sha(p) for p in ROOT.glob('*.tf')},'files':{str(p.relative_to(output)):sha(p) for p in output.rglob('*') if p.is_file() and '__pycache__' not in str(p)},'fixture':s['ip'].startswith(('192.0.2.','198.51.100.','203.0.113.')),'no_production_state_copied':True}
 (output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print('PREPARED',output,'CT',s['vmid'],'(not deployed)')

def validate_bundle(output):
 output=output.resolve();manifest=json.loads((output/'manifest.json').read_text());assert manifest['status']=='PREPARED_NOT_DEPLOYED'
 for name,digest in manifest['files'].items():assert sha(output/name)==digest,'Bundle drift: '+name
 module=output/'terraform';log=output/'validation.log'
 # Reuse installed provider binaries, but never the production Terraform state.
 providers=ROOT/'.terraform/providers';target=module/'.terraform/providers'
 if providers.exists() and not target.exists():target.parent.mkdir(exist_ok=True);target.symlink_to(providers.resolve(),target_is_directory=True)
 transcript=[]
 try:
  for args in [['terraform','fmt','-check','-recursive'],['terraform','init','-backend=false','-input=false','-upgrade=false'],['terraform','validate','-no-color'],['terraform','test','-test-directory=tests/provisioning','-verbose','-no-color']]:
   p=subprocess.run(args,cwd=module,capture_output=True,text=True);transcript.append('$ '+' '.join(args)+'\n'+p.stdout+p.stderr);log.write_text('\n'.join(transcript));log.chmod(0o600)
   assert p.returncode==0,'Validation failed; inspect private validation.log'
 except Exception:raise
 actual=re.search(r'provider "registry.terraform.io/bpg/proxmox" \{.*?version\s*=\s*"([^"]+)"',(module/'.terraform.lock.hcl').read_text(),re.S).group(1);assert actual==manifest['provider_version'],'Provider version drift'
 plan=transcript[-1];assert '1 passed, 0 failed' in plan,'Terraform mock test was not executed'
 assert '1 to add, 0 to change, 0 to destroy' in plan,'Expected exactly one mocked create'
 assert not list(module.glob('*.tfstate*')),'Unexpected state file in fixture module'
 (output/'plan.mock.txt').write_text(plan);(output/'plan.mock.txt').chmod(0o600)
 manifest['files']['terraform/.terraform.lock.hcl']=sha(module/'.terraform.lock.hcl');(output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 result={'result':'PASS','ct_id':manifest['ct_id'],'status':'READY FOR FIRST REAL PROVISIONING TEST','terraform_test':'mock_provider, command=plan','plan':'1 add, 0 change, 0 destroy (mock)','production_calls':False,'infrastructure_created':False,'real_first_test':'NOT PERFORMED','log':'validation.log','reviewable_plan':'plan.mock.txt'}
 (output/'validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
def refresh_docs(output,receipt_path):
 manifest=json.loads((output/'manifest.json').read_text());receipt=json.loads(receipt_path.read_text());data=manifest['declared'];s=data['service']
 assert not manifest['fixture'],'No live observation can be attached to a TEST-NET fixture'
 assert receipt['result']=='PASS' and receipt['ct_id']==s['vmid'] and receipt['service']==s['name']
 assert receipt['cpu_source']=='cgroup_v2_textfile' and receipt['allocated_cores']==data['resources']['cpu'] and receipt['memory_mib']==data['resources']['memory']
 data['provisioning']['verification']=receipt
 module=output/'terraform';key=manifest['service_key']
 (module/f'inventory/services/{key}.yml').write_text(yaml.safe_dump(data,sort_keys=False))
 (module/f'docs/inventory/{s["vmid"]}-LXC-INVENTORY.md').write_text(inventory_document(data,key))
 run(['python3',str(module/'scripts/generate-lxc-inventory.py'),'--root',str(module)],module)
 manifest['files']={name:sha(output/name) for name in manifest['files']};(output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 print('Local Notes/inventory refreshed from verified receipt; no production writes. Stability acceptance remains pending.')

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='action',required=True)
 a=sub.add_parser('prepare');a.add_argument('--spec',type=Path,required=True);a.add_argument('--output',type=Path,required=True)
 a=sub.add_parser('validate');a.add_argument('--bundle',type=Path,required=True)
 a=sub.add_parser('refresh-docs');a.add_argument('--bundle',type=Path,required=True);a.add_argument('--receipt',type=Path,required=True)
 args=p.parse_args()
 if args.action=='prepare':prepare(args.spec,args.output)
 elif args.action=='validate':validate_bundle(args.bundle)
 else:refresh_docs(args.bundle,args.receipt)
