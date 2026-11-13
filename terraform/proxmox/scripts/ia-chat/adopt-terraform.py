#!/usr/bin/env python3
"""Adopción sin apply: importa solo630/631 y genera plan acotado con TLS verificado.
Guarda estado y planes sensibles fuera Git. Nunca realiza destroy ni apply global.
"""
import os,subprocess,json,shlex
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];private=Path.home()/'.local/share/mailerblend-recovery/ia-chat/terraform';private.mkdir(parents=True,exist_ok=True,mode=0o700);os.chmod(private,0o700)
ssh=['ssh','-o','UserKnownHostsFile='+str(Path.home()/'.ssh/known_hosts'),'-o','StrictHostKeyChecking=yes','-o','BatchMode=yes','pve']
ca=subprocess.check_output(ssh+['cat /etc/pve/pve-root-ca.pem']);(private/'pve-ca.pem').write_bytes(ca)
env=dict(os.environ,SSL_CERT_FILE=str(private/'pve-ca.pem'),TF_VAR_proxmox_tls_insecure='false')
def run(args):
 p=subprocess.run(['terraform']+args,cwd=ROOT,env=env,capture_output=True)
 if p.returncode not in [0,2]:
  (private/'last-error.log').write_bytes(p.stdout+p.stderr);os.chmod(private/'last-error.log',0o600);raise RuntimeError('Terraform falló; detalle privado en '+str(private/'last-error.log'))
 return p.stdout
state=run(['state','pull']);p=private/'before-import.tfstate'
if not p.exists():p.write_bytes(state);p.chmod(0o600)
existing=run(['state','list']).decode().splitlines()
for name,ct in [('infra-llm',630),('infra-webui',631)]:
 address='proxmox_virtual_environment_container.svc["'+name+'"]'
 if address not in existing:run(['import','-no-color','-var-file='+str(private.parent/'ssh-bootstrap.auto.tfvars.json'),address,'pve/'+str(ct)])
args=['plan','-no-color','-var-file='+str(private.parent/'ssh-bootstrap.auto.tfvars.json'),'-detailed-exitcode','-out='+str(private/'adoption.tfplan')]+['-target=proxmox_virtual_environment_container.svc["'+n+'"]' for n in ['infra-llm','infra-webui']]
run(args);data=json.loads(run(['show','-json',str(private/'adoption.tfplan')]))
changes=[{'address':r['address'],'actions':r['change']['actions'],'fields':[k for k in (r['change'].get('after') or {}) if (r['change'].get('before') or {}).get(k)!=(r['change'].get('after') or {}).get(k)]} for r in data.get('resource_changes',[])]
assert all('delete' not in r['actions'] and 'create' not in r['actions'] for r in changes),'Plan would recreate CT: STOP'
print(json.dumps({'imported_only':[630,631],'tls_verified':True,'changes':changes},indent=2))
(private/'plan-summary.json').write_text(json.dumps(changes,indent=2)+'\n')
