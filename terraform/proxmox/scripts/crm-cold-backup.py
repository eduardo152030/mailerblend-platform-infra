#!/usr/bin/env python3
"""Offline CRM data bundles. No stop/start, mount, cleanup, image or Proxmox resource operations."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile

PLAN = Path(__file__).resolve().parents[1] / 'services/infra-composable-crm/recovery/plan.json'


def sha256(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def require_empty(path):
    if path.is_symlink():
        raise ValueError('Symlink destinations are forbidden.')
    if path.exists() and any(path.iterdir()):
        raise ValueError('Destination must be absent or empty; overwriting is forbidden.')


def archive_safe(path):
    # Refuse links/devices/traversal rather than risk writing outside an isolated restore.
    with tarfile.open(path, 'r:') as archive:
        for member in archive:
            parts = Path(member.name).parts
            if member.name.startswith('/') or '..' in parts or not (member.isfile() or member.isdir()):
                raise ValueError('Archive contains traversal, links or special files; manual review required.')


def backup(root, dest, plan):
    if dest.exists() and any(dest.iterdir()):
        existing = verify(dest)
        if existing['volumes'] != plan['volumes'] or existing['image'] != plan['image']:
            raise ValueError('Existing bundle belongs to a different recovery point/topology.')
        return existing  # Idempotent recheck, not a new backup of changed source data.
    root = root.resolve()
    sources = {k: root/'var/lib/docker/volumes'/v/'_data' for k, v in plan['volumes'].items()}
    sources['configuration'] = root/plan['configuration_path']
    for source in sources.values():
        if not source.is_dir() or not source.resolve().is_relative_to(root):
            raise ValueError('Expected data source missing or outside the mounted rootfs.')
        if dest.resolve().is_relative_to(source.resolve()) or dest.resolve().is_relative_to(root):
            raise ValueError('Backup destination must be outside the source rootfs.')
    dest.mkdir(mode=0o700, parents=True, exist_ok=True)
    dest.chmod(0o700)
    manifest = {'format':1, 'created_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(), 'ct_id':plan['ct_id'], 'image':plan['image'], 'volumes':plan['volumes'], 'archives':{}}
    for name, source in sources.items():
        path = dest/(name+'.tar')
        with path.open('xb') as stream:
            os.chmod(path, 0o600)
            subprocess.run(['tar','--numeric-owner','--acls','--xattrs','--sparse','-cpf','-','-C',str(source),'.'],
                           stdout=stream,check=True)
        archive_safe(path)
        manifest['archives'][name] = {'file':path.name,'sha256':sha256(path),'bytes':path.stat().st_size}
    path = dest/'manifest.json'
    path.write_text(json.dumps(manifest,indent=2)+'\n')
    path.chmod(0o600)
    return verify(dest)


def verify(bundle):
    manifest = json.loads((bundle/'manifest.json').read_text())
    expected = set(manifest['volumes']) | {'configuration'}
    if manifest.get('format') != 1 or set(manifest['archives']) != expected:
        raise ValueError('Unexpected/incomplete bundle manifest.')
    for name, entry in manifest['archives'].items():
        if entry['file'] != name+'.tar' or Path(name).name != name:
            raise ValueError('Unsafe manifest archive path.')
        path = bundle/entry['file']
        if path.is_symlink() or path.stat().st_size != entry['bytes'] or sha256(path) != entry['sha256']:
            raise ValueError('Backup size/checksum mismatch.')
        archive_safe(path)
    return manifest


def restore(bundle, dest):
    manifest = verify(bundle)
    require_empty(dest)
    # Never overwrite original volumes or live Docker data. Restore to a NEW staging tree only.
    if str(dest.resolve()).startswith(('/var/lib/docker','/var/lib/lxc','/proc','/sys','/dev')):
        raise ValueError('Live-system restore destinations are forbidden; use a new isolated staging directory.')
    dest.mkdir(mode=0o700,parents=True,exist_ok=True)
    dest.chmod(0o700)
    for name, entry in manifest['archives'].items():
        target=dest/name
        target.mkdir(mode=0o700)
        subprocess.run(['tar','--numeric-owner','--same-owner','--acls','--xattrs','-xpf',str(bundle/entry['file']),'-C',str(target)],check=True)
    return manifest


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('action',choices=['plan','backup','verify','restore'])
    p.add_argument('--rootfs',type=Path)
    p.add_argument('--bundle',type=Path)
    p.add_argument('--destination',type=Path)
    p.add_argument('--execute',action='store_true')
    args=p.parse_args()
    plan=json.loads(PLAN.read_text())
    if args.action=='plan':
        print('CT',plan['ct_id'],'archives:',', '.join(plan['volumes']),'and protected configuration. No production changes.')
        return
    if args.action=='verify':
        if not args.bundle:p.error('--bundle required')
        verify(args.bundle)
    else:
        if not args.execute:p.error('Writes require --execute and prior operator approval.')
        if args.action=='backup':
            if not args.rootfs or not args.destination:p.error('--rootfs and --destination required')
            state=subprocess.check_output(['pct','status',str(plan['ct_id'])],text=True,timeout=10).strip()
            if state!='status: stopped':raise ValueError('CT must already be stopped; script will not stop it.')
            backup(args.rootfs,args.destination,plan)
        else:
            if not args.bundle or not args.destination:p.error('--bundle and --destination required')
            restore(args.bundle,args.destination)
    print('Completed. Integrity checks passed; database/application consistency still requires isolated restore testing.')


if __name__=='__main__':
    try:main()
    except (ValueError,OSError,subprocess.SubprocessError,tarfile.TarError):
        print('Operation failed safely. Check permissions, CT state, paths, available space and bundle integrity. No overwrite/cleanup was attempted.',file=sys.stderr)
        sys.exit(1)
