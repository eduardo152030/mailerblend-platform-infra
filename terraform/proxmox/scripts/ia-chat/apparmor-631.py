#!/usr/bin/env python3
"""Excepción631 explícitamente aprobada; no modifica perfil global ni otrosCT."""
import pathlib,hashlib,subprocess,json,datetime
p=pathlib.Path('/etc/pve/lxc/631.conf');original=p.read_text();assert 'hostname: infra-webui' in original and 'unprivileged: 1' in original
protected=lambda:{str(x):hashlib.sha256(x.read_bytes()).hexdigest() for x in [*pathlib.Path('/etc/pve/lxc').glob('*.conf'),pathlib.Path('/etc/pve/storage.cfg'),pathlib.Path('/etc/network/interfaces')] if x.stem not in ['630','631']}
before=protected();root=pathlib.Path('/root/ia-local')
if 'lxc.apparmor.profile: unconfined' not in original:
 assert 'lxc.apparmor.profile:' not in original
 (root/'631-before-apparmor.conf').write_text(original)
 subprocess.run(['pct','shutdown','631','--timeout','60'],check=True)
 p.write_text(original+'\nlxc.apparmor.profile: unconfined\n')
 subprocess.run(['pct','start','631'],check=True)
assert protected()==before
print(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'ct':631,'profile':'unconfined','approved':True,'protected_unchanged':True}))
