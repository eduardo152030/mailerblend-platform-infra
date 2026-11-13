"""CT627 D087b only: disable the failed CB release, preserving successful Qwen."""
from pathlib import Path
import subprocess,json,os,time,urllib.request
pid=subprocess.check_output(['lxc-info','-n','627','-pH'],text=True).strip();root=Path('/proc',pid,'root');jobs=root/'srv/voicebox/qwen-worker/jobs'
failed=jobs/'9eca224b23124b1a9cc0756c3251e5a4';state=json.loads((failed/'state.json').read_text());assert state['status']=='failed' and state['error']=='CHATTERBOX_WORKER_7_GIB'
names=subprocess.check_output(['pct','exec','627','--','docker','ps','--format','{{.Names}}'],text=True).splitlines();assert not any(n.startswith(('qwen-','chatterbox-')) for n in names)
p=Path('/opt/voicebox-qwen-627/chatterbox-release.json');backup=Path('/mnt/storage/d087b-staging/chatterbox-enabled-before-stop.json')
with backup.open('x') as f:os.chmod(backup,0o600);f.write(p.read_text())
v=json.loads(p.read_text());v.update(enabled=False,reason='D087b Spanish trial stopped by worker preventive7GiB; no retry; pending resource diagnosis',disabled_after_job=failed.name)
tmp=p.with_name('chatterbox-release.d087b-disabled.partial')
with tmp.open('x') as f:os.chmod(tmp,0o600);json.dump(v,f,indent=2);f.flush();os.fsync(f.fileno())
os.replace(tmp,p)
for _ in range(30):
 with urllib.request.urlopen('http://192.168.1.127:17493/tts-capabilities',timeout=10) as response:caps=json.load(response)
 if caps['qwen']['ready'] and not caps['chatterbox']['ready']:break
 time.sleep(.5)
else:raise RuntimeError('Release not reflected in readiness')
print(json.dumps({'chatterbox_disabled':True,'qwen_ready':True,'qwen_languages':caps['qwen']['languages'],'app_not_restarted':True,'failed_job_and_evidence_preserved':True}))
