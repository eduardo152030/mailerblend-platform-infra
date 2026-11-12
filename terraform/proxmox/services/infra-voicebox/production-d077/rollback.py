"""Restore only the previous Voicebox image/Compose; retain all voice data and jobs."""
from pathlib import Path
import subprocess

code = """import subprocess,json,time,urllib.request
def ct(*args):return subprocess.check_output(['pct','exec','627','--',*args],text=True,timeout=30)
subprocess.run(['systemctl','disable','--now','voicebox-qwen-627.service'],check=True,capture_output=True)
ct('python3','-c',"import shutil;shutil.copy2('/opt/voicebox/backups/d077-production-before/compose.yml','/opt/voicebox/compose.yml')")
ct('docker','compose','-f','/opt/voicebox/compose.yml','up','-d','--no-build','--pull','never','voicebox')
for n in range(120):
 c=json.loads(ct('docker','inspect','voicebox'))[0]
 if c['State'].get('Health',{}).get('Status')=='healthy':break
 time.sleep(1)
else:raise RuntimeError('Rollback health failed')
assert c['Image']=='sha256:bcc5c14f88064ffa76f813d788d183918b208deba45075d8118a2b07c60c248b'
print(json.dumps({'rollback':'PASS','image':c['Image'],'data_and_checkpoints_retained':True}))
"""
ssh = ["ssh", "-o", "UserKnownHostsFile=" + str(Path.home() / ".ssh/known_hosts"),
       "-o", "StrictHostKeyChecking=yes", "-o", "BatchMode=yes", "pve", "python3 -"]
raise SystemExit(subprocess.run(ssh, input=code, text=True).returncode)
