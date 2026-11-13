"""PVE: capture private D084 baseline/final without service or storage mutations."""
import subprocess,json,hashlib,datetime
from pathlib import Path

def call(*a): return subprocess.check_output(a,text=True,timeout=45)
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
pid=call('lxc-info','-n','627','-pH').strip();root=Path('/proc',pid,'root')
paths=['srv/voicebox/data','srv/voicebox/private-originals','srv/voicebox/qwen-worker/jobs','srv/voicebox/qwen-worker/src']
files={str(p.relative_to(root)):sha(p) for d in paths for p in (root/d).rglob('*') if p.is_file() and p.name not in ['agent-heartbeat.json','voicebox.db-shm','voicebox.db-wal','voicebox.db']}
print(json.dumps({'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'ct_pid':pid,'configs':{p.stem:sha(p) for p in Path('/etc/pve/lxc').glob('*.conf')},'ct_config':call('pct','config','627'),'uuid':call('blkid','-s','UUID','-o','value','/dev/pve/vm-627-disk-0').strip(),'df':call('pct','exec','627','--','df','-B1','/'),'ct_events':Path('/sys/fs/cgroup/lxc/627/memory.events').read_text(),'host_mem':Path('/proc/meminfo').read_text(),'host_psi':Path('/proc/pressure/memory').read_text(),'files':files,'active_tasks':call('pvenode','task','list','--source','active'),'worker_containers':call('pct','exec','627','--','docker','ps','--format','{{.Names}}'),'agent_status':call('systemctl','is-active','voicebox-qwen-627.service')}))
