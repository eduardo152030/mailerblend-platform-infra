#!/usr/bin/env python3
"""Verifica exactamente el archivo creado por este cierre; no el último arbitrario."""
import subprocess,shlex,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
ssh=['ssh','-o','UserKnownHostsFile='+str(Path.home()/'.ssh/known_hosts'),'-o','StrictHostKeyChecking=yes','-o','BatchMode=yes','pve']
code="import pathlib,re,json;s=pathlib.Path('/root/ia-local/backup-integrated-final.log').read_text();m=re.search(r'(/mnt/storage/dump/vzdump-lxc-631-[0-9_-]+[.]tar[.]zst)',s);assert m and 'Backup job finished successfully' in s;print(m.group(1))"
p=subprocess.check_output(ssh+[shlex.join(['python3','-c',code])],text=True).strip();print('Verificando '+p,flush=True)
body=subprocess.check_output(ssh+[shlex.join(['python3','/root/ia-local/verify-backup.py',p])]);d=json.loads(body);(ROOT/'docs/roadmap/evidence/ia-chat-2026-11-13/backup-integrated-final-verified.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(d,indent=2))
