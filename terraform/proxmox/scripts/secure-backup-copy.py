#!/usr/bin/env python3
"""Copy an immutable approved PVE backup off-host, encrypted, then decrypt/hash verify it."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import secrets
import shlex
import subprocess
import sys


def gpg_args(key, action, target):
    descriptor=os.open(key,os.O_RDONLY)
    args=['gpg','--no-options','--batch','--yes','--pinentry-mode','loopback',
          '--no-symkey-cache','--passphrase-fd',str(descriptor)]
    if action=='encrypt':args+=['--cipher-algo','AES256','--compress-algo','none','--symmetric','--output',str(target)]
    else:args+=['--decrypt',str(target)]
    return descriptor,args


def decrypted_digest(path,key):
    fd,args=gpg_args(key,'decrypt',path)
    try:
        proc=subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,pass_fds=(fd,))
    finally:os.close(fd)
    h=hashlib.sha256()
    for chunk in iter(lambda:proc.stdout.read(1024*1024),b''):h.update(chunk)
    proc.stdout.close();error=proc.stderr.read();code=proc.wait()
    if code:raise ValueError('Encrypted backup verification failed; details withheld.')
    return h.hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',required=True)
    p.add_argument('--directory',type=Path,required=True)
    p.add_argument('--key-file',type=Path,required=True)
    p.add_argument('--execute',action='store_true')
    args=p.parse_args()
    if not args.execute:p.error('Explicit --execute required.')
    if not Path(args.source).is_absolute() or not Path(args.source).is_relative_to('/mnt/storage'):
        p.error('Only approved backups under /mnt/storage may be copied.')
    args.directory.mkdir(mode=0o700,parents=True,exist_ok=True);args.directory.chmod(0o700)
    args.key_file.parent.mkdir(mode=0o700,parents=True,exist_ok=True);args.key_file.parent.chmod(0o700)
    if not args.key_file.exists():
        fd=os.open(args.key_file,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
        with os.fdopen(fd,'w') as f:f.write(secrets.token_urlsafe(48)+'\n')
    if args.key_file.stat().st_mode & 0o077:raise ValueError('Key file permissions must be 0600.')
    ssh=['ssh','-o','BatchMode=yes','-o','ConnectTimeout=5','pve']
    digest=subprocess.check_output(ssh+[shlex.join(['sha256sum','--',args.source])],text=True).split()[0]
    target=args.directory/(Path(args.source).name+'.gpg')
    if not target.exists():
        reader=subprocess.Popen(ssh+[shlex.join(['cat','--',args.source])],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        fd,cmd=gpg_args(args.key_file,'encrypt',target)
        try:result=subprocess.run(cmd,stdin=reader.stdout,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,pass_fds=(fd,))
        finally:os.close(fd);reader.stdout.close()
        ssh_error=reader.stderr.read();remote_code=reader.wait()
        if result.returncode or remote_code:raise ValueError('Encrypted transfer failed; partial file retained for inspection.')
        target.chmod(0o600)
    actual=decrypted_digest(target,args.key_file)
    if actual!=digest:raise ValueError('Off-host decrypted checksum differs from source. Do not continue.')
    record={'source':args.source,'plaintext_sha256':actual,'encrypted_file':target.name,'cipher':'AES256-GnuPG','decryption_verified':True}
    report=target.with_suffix(target.suffix+'.verified.json');report.write_text(json.dumps(record,indent=2)+'\n');report.chmod(0o600)
    print('Verified encrypted off-host copy:',target.name)


if __name__=='__main__':
    try:main()
    except (OSError,ValueError,subprocess.SubprocessError):
        print('Backup copy/verification failed. No cleanup performed; inspect private artifacts before proceeding.',file=sys.stderr)
        sys.exit(1)
