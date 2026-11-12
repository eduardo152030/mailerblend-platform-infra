"""Strict SSH launcher. Bundles versioned supervisor/guards; default remains plan-only."""
from pathlib import Path
import shlex
import subprocess
import sys

root = Path(__file__).parent
bootstrap = "import sys,types\nm=types.ModuleType('guards')\n" + \
    "exec(compile(" + repr((root / "guards.py").read_text()) + ", 'guards.py', 'exec'),m.__dict__)\n" + \
    "sys.modules['guards']=m\nexec(compile(" + repr((root / "supervise.py").read_text()) + \
    ", 'supervise.py', 'exec'),{'__name__':'__main__','__file__':'supervise.py'})\n"
ssh = ["ssh", "-o", "UserKnownHostsFile=" + str(Path.home() / ".ssh/known_hosts"),
       "-o", "StrictHostKeyChecking=yes", "-o", "BatchMode=yes", "pve",
       shlex.join(["python3", "-", *sys.argv[1:]])]
raise SystemExit(subprocess.run(ssh, input=bootstrap, text=True).returncode)
