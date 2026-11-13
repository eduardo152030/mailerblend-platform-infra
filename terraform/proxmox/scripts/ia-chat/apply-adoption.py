#!/usr/bin/env python3
"""Aplica exclusivamente el plan de adopción630/631 revisado y sin recreaciones."""
import json,os,subprocess
from pathlib import Path
P=Path.home()/'.local/share/mailerblend-recovery/ia-chat/terraform';env=dict(os.environ,SSL_CERT_FILE=str(P/'pve-ca.pem'),TF_VAR_proxmox_tls_insecure='false')
d=json.loads(subprocess.check_output(['terraform','show','-json',str(P/'adoption.tfplan')],env=env))
allowed={'description','features','start_on_boot','tags','timeout_clone','timeout_create','timeout_delete','timeout_start','timeout_update','vm_id'}
for r in d['resource_changes']:
 assert r['address'] in ['proxmox_virtual_environment_container.svc["infra-llm"]','proxmox_virtual_environment_container.svc["infra-webui"]']
 c=r['change'];assert c['actions'] in [['update'],['no-op']]
 assert {k for k in c['after'] if c['before'].get(k)!=c['after'].get(k)}<=allowed
p=subprocess.run(['terraform','apply','-no-color',str(P/'adoption.tfplan')],capture_output=True,env=env);(P/'apply.log').write_bytes(p.stdout+p.stderr);(P/'apply.log').chmod(0o600);assert p.returncode==0,'Apply failed; inspect private apply.log';print('PASS: adopción630/631 aplicada sin recrear, sin tocar recursos/volúmenes/red')
