"""Install only D087 supervisor resource changes; no app recreation or model loading."""
from pathlib import Path
import subprocess,json,hashlib
PILOT=Path(__file__).resolve().parent
ssh=['ssh','-o','UserKnownHostsFile='+str(Path.home()/'.ssh/known_hosts'),'-o','StrictHostKeyChecking=yes','-o','BatchMode=yes','pve']
files={n:(PILOT/n).read_text() for n in ['supervise.py','guards.py']}
code='files='+repr(files)+'\n'+'''from pathlib import Path
import subprocess,json,os,hashlib
cg=Path('/sys/fs/cgroup/lxc/627');assert int((cg/'memory.max').read_text())==20*2**30
names=subprocess.check_output(['pct','exec','627','--','docker','ps','--format','{{.Names}}'],text=True).splitlines();assert not any(n.startswith('qwen-') for n in names)
pid=subprocess.check_output(['lxc-info','-n','627','-pH'],text=True).strip();root=Path('/proc',pid,'root');jobs=root/'srv/voicebox/qwen-worker/jobs'
assert not any(json.loads(p.read_text()).get('status') in ['running','queued'] for p in jobs.glob('*/state.json'))
backup=Path('/opt/voicebox-qwen-627/backups/d087-resource-before');assert backup.is_dir()
current=root/'srv/voicebox/qwen-worker/src';prior=current.parent/os.readlink(current);owner=prior.stat()
if not (backup/'worker-source-target.txt').exists():(backup/'worker-source-target.txt').write_text(os.readlink(current))
core={p.name:p.read_text() for p in prior.glob('*.py')};core.update(files)
digest=hashlib.sha256(json.dumps(core,sort_keys=True).encode()).hexdigest();target=current.parent/('src-'+digest[:16]);target.mkdir(mode=0o700,exist_ok=True);os.chown(target,owner.st_uid,owner.st_gid)
for name,text in core.items():
 p=target/name
 if p.exists():assert p.read_text()==text
 else:p.write_text(text);p.chmod(0o600);os.chown(p,owner.st_uid,owner.st_gid)
if os.readlink(current)!=target.name:
 tmp=current.with_name('src-d087-resource-pending');assert not tmp.exists();tmp.symlink_to(target.name);os.replace(tmp,current)
changed=any((Path('/opt/voicebox-qwen-627')/n).read_text()!=t for n,t in files.items())
if changed:subprocess.run(['systemctl','stop','voicebox-qwen-627.service'],check=True)
try:
 for name,text in files.items():
  compile(text,name,'exec');p=Path('/opt/voicebox-qwen-627')/name;tmp=p.with_suffix('.d087-resource-partial');tmp.write_text(text);tmp.chmod(0o600);os.replace(tmp,p)
 if changed:subprocess.run(['systemctl','start','voicebox-qwen-627.service'],check=True)
 assert subprocess.check_output(['systemctl','is-active','voicebox-qwen-627.service'],text=True).strip()=='active'
except BaseException:
 for name in files:(Path('/opt/voicebox-qwen-627')/name).write_bytes((backup/name).read_bytes())
 subprocess.run(['systemctl','start','voicebox-qwen-627.service'],check=True);raise
print(json.dumps({'files':{n:hashlib.sha256(t.encode()).hexdigest() for n,t in files.items()},'ct_guard_gib':19,'ct_ram_gib':20,'worker_hard_gib':9,'worker_stop_gib':8.2,'app_recreated':False,'agent_active':True,'agent_restart_needed':changed,'ct_source_revision':target.name}))
'''
r=subprocess.run(ssh+['python3 -'],input=code,text=True,capture_output=True);
if r.returncode:raise RuntimeError(r.stderr)
print(r.stdout,end='')
