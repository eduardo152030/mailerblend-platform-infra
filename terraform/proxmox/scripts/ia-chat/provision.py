#!/usr/bin/env python3
"""Ejecutar en PVE. Alta solo630/631 desde inventario JSON preparado con YAML.
No modifica CT existentes. Una reaplicación verifica y no recrea ni reinicia.
"""
import pathlib,json,subprocess,hashlib,datetime,sys
root=pathlib.Path('/root/ia-local');root.mkdir(exist_ok=True,mode=0o700)
assert not (root/'TERRAFORM-MANAGED').exists(),'Bootstrap histórico deshabilitado: recursos adoptados por Terraform'
spec=json.loads((root/'inventory.json').read_text());assert {c['id'] for c in spec['containers']}=={630,631}
def run(*args):return subprocess.run(args,check=True,text=True,capture_output=True).stdout.strip()
def baseline():
 return {str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [*pathlib.Path('/etc/pve/lxc').glob('*.conf'),pathlib.Path('/etc/pve/storage.cfg'),pathlib.Path('/etc/network/interfaces')] if p.stem not in ['630','631']}
before=baseline()
if not (root/'protected-before.json').exists():(root/'protected-before.json').write_text(json.dumps(before,indent=2)+'\n')
reference=run('pct','config','624');assert 'firewall=1' in next(x for x in reference.splitlines() if x.startswith('net0:'))
tpl=spec['template'];target=pathlib.Path('/var/lib/vz/template/cache')/tpl
if not target.is_file():print(run('pveam','download','local',tpl),flush=True)
for c in spec['containers']:
 id=str(c['id']);conf=pathlib.Path('/etc/pve/lxc')/(id+'.conf');created=False
 if not conf.exists():
  args=['pct','create',id,'local:vztmpl/'+tpl,'--hostname',c['hostname'],'--unprivileged','1','--cores',str(c['cores']),'--memory',str(c['memory']),'--swap',str(c['swap']),'--rootfs',spec['storage']+':'+str(c['rootfs_gib']),'--net0','name=eth0,bridge=vmbr0,ip=dhcp,firewall=1','--onboot','1','--timezone',spec['timezone'],'--ostype','debian','--tags','infra;ia-chat']
  if 'features' in c:args+=['--features',c['features']]
  print(run(*args),flush=True);created=True
  if c.get('apparmor_profile'):
   assert c['id']==631 and c['apparmor_profile']=='unconfined'
   conf.write_text(conf.read_text()+'\nlxc.apparmor.profile: unconfined\n')
  if c.get('models_gib'):print(run('pct','set',id,'--mp0',f"local-lvm:{c['models_gib']},mp=/models,backup=0"),flush=True)
 else:
  current=run('pct','config',id)
  assert f"hostname: {c['hostname']}" in current and 'unprivileged: 1' in current,'CT existente inesperado'
 current=run('pct','config',id)
 for k,v in [('cores',c['cores']),('memory',c['memory']),('swap',c['swap']),('onboot',1),('timezone',spec['timezone'])]:assert f'{k}: {v}' in current,(id,k,'deriva')
 assert 'ip=dhcp' in current and 'firewall=1' in current
 assert f"size={c['rootfs_gib']}G" in current
 if c.get('apparmor_profile'):assert 'lxc.apparmor.profile: unconfined' in current
 if c.get('models_gib'):assert 'backup=0' in current and 'mp=/models' in current
 if created:print(run('pct','start',id),flush=True)
 assert baseline()==before,'Cambió una configuración protegida: STOP'
print(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'protected_unchanged':baseline()==before,'configs':{str(c['id']):run('pct','config',str(c['id'])) for c in spec['containers']}}),flush=True)
