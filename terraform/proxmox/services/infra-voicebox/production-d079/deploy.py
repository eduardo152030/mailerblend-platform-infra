"""Deploy only authorized Voicebox/CT627 integration, with automatic app rollback."""
from pathlib import Path
import json
import subprocess
import yaml

HERE = Path(__file__).parent
compose = yaml.safe_load((HERE.parent / "compose.yml").read_text())
service = compose["services"]["voicebox"]
service["image"] = "local/voicebox:qwen-isolated-d079"
service["build"] = {"context": "./production-d079", "dockerfile": "Dockerfile"}
mount = "/srv/voicebox/qwen-worker/jobs:/qwen-jobs"
if mount not in service["volumes"]:
    service["volumes"].append(mount)
assert service["cpus"] == 3 and service["mem_limit"] == "6200m" and service["memswap_limit"] == "6600m"
text = yaml.safe_dump(compose, sort_keys=False, allow_unicode=True)
unit = (HERE / "voicebox-qwen-627.service").read_text()
code = """from pathlib import Path
import json,subprocess,time,urllib.request,hashlib
def ct(*args):return subprocess.check_output(['pct','exec','627','--',*args],text=True,timeout=30)
def py(s):return ct('python3','-c',s)
result={'scope':'CT627 Voicebox and dedicated PVE supervisor'}
""" + "compose=" + repr(text) + "\nunit=" + repr(unit) + "\n" + """
before=json.loads(ct('docker','inspect','voicebox'))[0]
assert before['State']['Health']['Status']=='healthy'
assert py("from pathlib import Path;print((Path('/opt/voicebox/backups/d079-production-before')/'manifest.json').is_file())").strip()=='True'
# This mandatory runtime gate runs before any unit/Compose mutation, as UID999.
smoke="import os;from backend.backends import get_tts_backend_for_engine;from backend.models import GenerationRequest;assert os.geteuid()==999;b=get_tts_backend_for_engine('qwen');assert type(b).__name__=='IsolatedQwenBackend' and not b.is_loaded() and b.model is None;assert GenerationRequest(profile_id='x',text='x').model_size=='0.6B';print('candidate_runtime_PASS')"
assert ct('docker','run','--rm','--network','none','--cpus','3','--memory','2g','--memory-swap','2g','--pids-limit','96','--user','999:999','--read-only','--tmpfs','/tmp:rw,size=64m','-e','HF_HUB_OFFLINE=1','-e','PYTHONDONTWRITEBYTECODE=1','--entrypoint','python','local/voicebox:qwen-isolated-d079','-c',smoke).strip()=='candidate_runtime_PASS'
result['candidate_runtime_UID999_passed']=True
unitpath=Path('/etc/systemd/system/voicebox-qwen-627.service')
changed=not unitpath.exists() or unitpath.read_text()!=unit
if changed:unitpath.write_text(unit);unitpath.chmod(0o644)
try:
 if changed:subprocess.run(['systemctl','daemon-reload'],check=True,capture_output=True)
 subprocess.run(['systemd-analyze','verify',str(unitpath)],check=True,capture_output=True)
 subprocess.run(['systemctl','enable','--now','voicebox-qwen-627.service'],check=True,capture_output=True)
 for n in range(40):
  try:
   ready=py("from pathlib import Path;import json,time;p=Path('/srv/voicebox/qwen-worker/jobs/agent-heartbeat.json');v=json.loads(p.read_text());assert time.time()-v['timestamp']<8;print(v['status'])").strip()
   if ready=='healthy':break
  except Exception:pass
  time.sleep(.5)
 else:raise RuntimeError('PVE supervisor heartbeat not ready')
 current=ct('cat','/opt/voicebox/compose.yml')
 target=json.loads(ct('docker','image','inspect','local/voicebox:qwen-isolated-d079'))[0]['Id']
 if current==compose and before['Image']==target:
  result['idempotent_no_recreate']=True
 else:
  py("from pathlib import Path;import os;p=Path('/opt/voicebox/compose-d079-candidate.yml');p.write_text("+repr(compose)+");p.chmod(0o600)")
  ct('docker','compose','-f','/opt/voicebox/compose-d079-candidate.yml','config','--quiet')
  py("from pathlib import Path;import os;p=Path('/opt/voicebox/compose.yml');t=p.with_suffix('.d079-new');t.write_text("+repr(compose)+");t.chmod(0o600);os.replace(t,p)")
  ct('docker','compose','-f','/opt/voicebox/compose.yml','up','-d','--no-build','--pull','never','voicebox')
  result['idempotent_no_recreate']=False
 for n in range(120):
  current=json.loads(ct('docker','inspect','voicebox'))[0]
  if current['State'].get('Health',{}).get('Status')=='healthy':
   with urllib.request.urlopen('http://192.168.1.127:17493/qwen-worker/health',timeout=5) as f:assert json.load(f)['status']=='healthy'
   break
  time.sleep(1)
 else:raise RuntimeError('New Voicebox did not become healthy')
 assert current['Image']==target
 assert json.loads(ct('docker','image','inspect','local/voicebox:8af7efe62fab-personal-d069'))[0]['Id']=='sha256:bcc5c14f88064ffa76f813d788d183918b208deba45075d8118a2b07c60c248b'
 result.update(status='PASS',image_id=target,old_image_retained=True,container_id=current['Id'],started_at=current['State']['StartedAt'],healthy=True,supervisor_active=True)
except Exception as exc:
 result.update(status='FAILED',error=type(exc).__name__,rollback_attempted=True)
 py("from pathlib import Path;import shutil;shutil.copy2('/opt/voicebox/backups/d079-production-before/compose.yml','/opt/voicebox/compose.yml')")
 ct('docker','compose','-f','/opt/voicebox/compose.yml','up','-d','--no-build','--pull','never','voicebox')
 subprocess.run(['systemctl','stop','voicebox-qwen-627.service'],capture_output=True)
 import shutil
 for name in ['agent.py','supervise.py','guards.py']:
  shutil.copy2(Path('/opt/voicebox-qwen-627/backups/d079-before')/name,Path('/opt/voicebox-qwen-627')/name)
 py("from pathlib import Path;import os;p=Path('/srv/voicebox/qwen-worker');old=Path('/opt/voicebox/backups/d079-production-before/worker-source-target.txt').read_text().strip();t=p/'rollback-src';t.symlink_to(old);os.replace(t,p/'src')")
 subprocess.run(['systemctl','start','voicebox-qwen-627.service'],check=True,capture_output=True)
 result['rollback_image']=json.loads(ct('docker','inspect','voicebox'))[0]['Image']
print(json.dumps(result))
raise SystemExit(0 if result['status']=='PASS' else 1)
"""
ssh = ["ssh", "-o", "UserKnownHostsFile=" + str(Path.home() / ".ssh/known_hosts"),
       "-o", "StrictHostKeyChecking=yes", "-o", "BatchMode=yes", "pve", "python3 -"]
r = subprocess.run(ssh, input=code, text=True)
if r.returncode:
    raise SystemExit(r.returncode)
(HERE.parent / "compose.yml").write_text(text)
