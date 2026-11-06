#!/usr/bin/env python3
"""Resume a completed PVE ciphertext copy and verify its decrypted plaintext hash."""
import argparse
import importlib.util
import json
from pathlib import Path
import re
import shlex
import subprocess
import sys

sys.dont_write_bytecode=True

spec=importlib.util.spec_from_file_location('backup_crypto',Path(__file__).with_name('secure-backup-copy.py'))
crypto=importlib.util.module_from_spec(spec);spec.loader.exec_module(crypto)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',required=True,help='Immutable plaintext backup on PVE; corresponding .gpg must be complete.')
    p.add_argument('--directory',type=Path,required=True)
    p.add_argument('--key-file',type=Path,required=True)
    p.add_argument('--execute',action='store_true')
    args=p.parse_args()
    try:
        if not args.execute or not Path(args.source).is_relative_to('/mnt/storage'):
            raise ValueError('Explicit execution and approved backup path required.')
        if args.key_file.stat().st_mode & 0o077:raise ValueError('Private key permissions required.')
        ssh=['ssh','-o','BatchMode=yes','-o','ServerAliveInterval=30','-o','ServerAliveCountMax=6','pve']
        digest=subprocess.check_output(ssh+[shlex.join(['cat',args.source+'.sha256'])],text=True).split()[0]
        if not re.fullmatch('[0-9a-f]{64}',digest):raise ValueError('Invalid source checksum record.')
        subprocess.run(ssh+['test -f '+shlex.quote(args.source+'.gpg.ready')],check=True)
        args.directory.mkdir(mode=0o700,parents=True,exist_ok=True);args.directory.chmod(0o700)
        remote=args.source+'.gpg';target=args.directory/Path(remote).name
        transport='ssh -o BatchMode=yes -o ServerAliveInterval=30 -o ServerAliveCountMax=6'
        subprocess.run(['rsync','-a','--partial','--append-verify','--timeout=120','-e',transport,'pve:'+remote,str(args.directory)+'/'],check=True)
        target.chmod(0o600)
        if crypto.decrypted_digest(target,args.key_file)!=digest:raise ValueError('Decrypted checksum mismatch.')
        record={'source':args.source,'plaintext_sha256':digest,'decryption_verified':True,'resumable_transfer':True}
        report=target.with_suffix(target.suffix+'.verified.json');report.write_text(json.dumps(record,indent=2)+'\n');report.chmod(0o600)
        print('Verified resumable encrypted off-host backup:',target.name)
    except (ValueError,OSError,subprocess.SubprocessError):
        print('Resumable backup not verified. Partial ciphertext retained; cleanup remains forbidden.',file=sys.stderr)
        sys.exit(1)
