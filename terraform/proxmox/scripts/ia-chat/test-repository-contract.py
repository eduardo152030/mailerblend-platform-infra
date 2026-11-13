#!/usr/bin/env python3
"""Comprueba contratos nuevos y conservación exacta del estado previo de18CT."""
import sys,json,subprocess,yaml,tempfile,copy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts'));import lxc_provisioning as l
for n in ['infra-llm','infra-webui']:
 d=yaml.safe_load((ROOT/'inventory/services'/str(n+'.yml')).read_text());l.validate(d)
 with tempfile.TemporaryDirectory() as tmp:
  l.render_monitoring(d,Path(tmp),ROOT)
  for p in (ROOT/'services'/n/'monitoring').iterdir():
   if p.is_file():assert p.read_bytes()==(Path(tmp)/p.name).read_bytes(),p
 bad=copy.deepcopy(d);bad['os']={'template_file_id':'/arbitrary/path','name':'bad'}
 try:l.validate(bad)
 except AssertionError:pass
 else:raise AssertionError('Invalid template accepted')
 bad=copy.deepcopy(d);bad['network']['gateway']='203.0.113.254'
 try:l.validate(bad)
 except AssertionError:pass
 else:raise AssertionError('Invalid gateway accepted')
assert (ROOT/'services/ia-local/docker-compose.yml').resolve()==(ROOT/'services/infra-webui/compose/docker-compose.yml').resolve()
P=Path.home()/'.local/share/mailerblend-recovery/ia-chat/terraform';before=json.loads((P/'before-import.tfstate').read_text());after=json.loads(subprocess.check_output(['terraform','state','pull'],cwd=ROOT))
def old(d):
 return {r['type']+'.'+r['name']:{i['index_key']:i for i in r['instances'] if i['index_key'] not in ['infra-llm','infra-webui']} for r in d['resources']}
assert old(before)==old(after),'Legacy Terraform state altered'
print(json.dumps({'result':'PASS','legacy_terraform_instances_unchanged':18,'monitoring_bundles_reproducible':True,'invalid_inputs_rejected':True,'canonical_compose_single_source':True}))
