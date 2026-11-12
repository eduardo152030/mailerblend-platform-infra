"""Prepare versioned isolated sources and synthetic jobs on CT627; never run models."""
import hashlib
import argparse
import json
from pathlib import Path
import subprocess
import re

ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument("--job", help="Prepare a new private future real job, without running it")
ap.add_argument("--text-file", type=Path)
args = ap.parse_args()
if bool(args.job) != bool(args.text_file) or (args.job and not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,35}", args.job)):
    ap.error("--job and --text-file must be supplied together, with a safe job identifier")

ROOT = "/srv/voicebox/pilot-d077"
NAMES = ["checkpoint.py", "runtime.py", "worker.py", "guards.py", "supervise.py", "validation.py"]
files = {name: (Path(__file__).parent / name).read_text() for name in NAMES}
digest = hashlib.sha256(json.dumps(files, sort_keys=True).encode()).hexdigest()
# No credentials, recording or transcript enters this payload.
code = """from pathlib import Path
import os,json,hashlib,subprocess
root=Path('/srv/voicebox/pilot-d077')
running=subprocess.check_output(['docker','ps','--format','{{.Names}}'],text=True).splitlines()
assert not any(x.startswith('qwen-d077-') for x in running),'Prepared workers are active'
root.mkdir(mode=0o700,exist_ok=True)
""" + "files=" + repr(files) + "\ndigest=" + repr(digest) + "\n" + """
revision=root/('src-'+digest[:16]);new=not revision.exists()
revision.mkdir(mode=0o700,exist_ok=True);os.chown(revision,999,999)
for name,content in files.items():
 p=revision/name
 if p.exists():assert p.read_text()==content
 else:p.write_text(content);os.chmod(p,0o600);os.chown(p,999,999)
current=root/'src'
if not current.is_symlink() or current.resolve()!=revision:
 pending=root/('link-'+digest[:16]);assert not pending.exists();pending.symlink_to(revision.name);os.replace(pending,current)
jobs=root/'jobs';jobs.mkdir(mode=0o700,exist_ok=True)
for name in ['synthetic01','imports01','cancel01']:
 p=jobs/name;p.mkdir(mode=0o700,exist_ok=True);os.chown(p,999,999)
print(json.dumps({'source_sha256':digest,'revision':revision.name,'new_revision':new,'jobs':['synthetic01','imports01','cancel01'],'no_model_loaded':True,'production_changed':False}))
"""
if args.job:
    text = args.text_file.read_text().strip()
    if not text or len(text) > 10000:
        raise ValueError("Invalid future generation text")
    code += f"""
p=jobs/{args.job!r};p.mkdir(mode=0o700,exist_ok=True);os.chown(p,999,999)
text={text!r};target=p/'text.txt'
if target.exists():assert target.read_text()==text,'Never overwrite a prior job text'
else:target.write_text(text);os.chown(target,999,999);os.chmod(target,0o600)
"""
ssh = ["ssh", "-o", "UserKnownHostsFile=" + str(Path.home() / ".ssh/known_hosts"),
       "-o", "StrictHostKeyChecking=yes", "-o", "BatchMode=yes", "pve", "pct exec 627 -- python3 -"]
result = subprocess.run(ssh, input=code, text=True, capture_output=True, timeout=30)
if result.returncode:
    raise RuntimeError(result.stderr)
print(result.stdout, end="")
