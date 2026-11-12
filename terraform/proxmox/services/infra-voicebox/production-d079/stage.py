"""Stage reproducible CT627/PVE sources and build candidate; never replace running app."""
from pathlib import Path
import hashlib
import json
import shlex
import subprocess

HERE = Path(__file__).parent
PILOT = HERE.parent / "pilot-d077"
SSH = ["ssh", "-o", "UserKnownHostsFile=" + str(Path.home() / ".ssh/known_hosts"),
       "-o", "StrictHostKeyChecking=yes", "-o", "BatchMode=yes", "pve"]
core = {p.name: p.read_text() for p in PILOT.glob("*.py") if p.name in ["worker.py", "checkpoint.py", "runtime.py", "validation.py", "guards.py", "supervise.py"]}
s = core["supervise.py"]
assert s.count('ROOT = "/srv/voicebox/pilot-d077"') == 1
s = s.replace('ROOT = "/srv/voicebox/pilot-d077"', 'ROOT = "/srv/voicebox/qwen-worker"')
assert s.count('"--label", "d077.owner=" + owner,') == 1
s = s.replace('"--label", "d077.owner=" + owner,', '"--label", "d077.owner=" + owner, "--label", "d077.root=" + ROOT,')
core["supervise.py"] = s
overlay = {p.name: p.read_text() for p in HERE.iterdir() if p.is_file() and p.suffix in [".py", ".service"] or p.name == "Dockerfile"}
digest = hashlib.sha256(json.dumps(core, sort_keys=True).encode()).hexdigest()
code = """from pathlib import Path
import os,json,subprocess
assert json.loads(subprocess.check_output(['docker','image','inspect','local/voicebox:8af7efe62fab-personal-d069']))[0]['Id']=='sha256:bcc5c14f88064ffa76f813d788d183918b208deba45075d8118a2b07c60c248b'
root=Path('/srv/voicebox/qwen-worker');root.mkdir(mode=0o700,exist_ok=True)
""" + "files=" + repr(core) + "\noverlay=" + repr(overlay) + "\ndigest=" + repr(digest) + "\n" + """
src=root/('src-'+digest[:16]);src.mkdir(mode=0o700,exist_ok=True);os.chown(src,999,999)
for name,text in files.items():
 p=src/name
 if p.exists():assert p.read_text()==text
 else:p.write_text(text);os.chmod(p,0o600);os.chown(p,999,999)
current=root/'src'
if not current.is_symlink() or current.resolve()!=src:
 link=root/'src-pending';assert not link.exists();link.symlink_to(src.name);os.replace(link,current)
jobs=root/'jobs';jobs.mkdir(mode=0o700,exist_ok=True);os.chown(jobs,999,999)
dest=Path('/opt/voicebox/production-d079');dest.mkdir(mode=0o700,exist_ok=True)
for name,text in overlay.items():
 p=dest/name;p.write_text(text);p.chmod(0o600)
print(json.dumps({'revision':src.name,'overlay_files':len(overlay),'model_weights_changed':False,'application_replaced':False}))
"""
r = subprocess.run(SSH + ["pct exec 627 -- python3 -"], input=code, text=True, capture_output=True, timeout=30)
if r.returncode:
    raise RuntimeError(r.stderr)
print(r.stdout, end="")
host = {"agent.py": (HERE / "agent.py").read_text(), "supervise.py": s, "guards.py": core["guards.py"]}
code = "from pathlib import Path\nimport os\nfiles=" + repr(host) + "\np=Path('/opt/voicebox-qwen-627');p.mkdir(mode=0o700,exist_ok=True)\nfor name,text in files.items():\n f=p/name;f.write_text(text);f.chmod(0o600)\nprint('PVE sources staged; service not started')\n"
r = subprocess.run(SSH + ["python3 -"], input=code, text=True, capture_output=True, timeout=20)
if r.returncode:
    raise RuntimeError(r.stderr)
print(r.stdout, end="")
r = subprocess.run(SSH + ["pct exec 627 -- docker build --network none -t local/voicebox:qwen-isolated-d079 /opt/voicebox/production-d079"], text=True)
raise SystemExit(r.returncode)
