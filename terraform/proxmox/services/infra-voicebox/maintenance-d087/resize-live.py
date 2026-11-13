"""PVE: authorized CT627 live resize only, no restart or application changes."""
from pathlib import Path
import subprocess,json,hashlib,datetime
cg=Path('/sys/fs/cgroup/lxc/627')
def call(*a):return subprocess.check_output(a,text=True,timeout=30)
def identity():
 d=json.loads(call('pct','exec','627','--','docker','inspect','voicebox'))[0]
 return {'id':d['Id'],'image':d['Image'],'started':d['State']['StartedAt'],'restarts':d['RestartCount'],'health':d['State']['Health']['Status']}
before={p.stem:hashlib.sha256(p.read_bytes()).hexdigest() for p in Path('/etc/pve/lxc').glob('*.conf')};own=identity();assert own['health']=='healthy';cfg=dict(x.split(': ',1) for x in call('pct','config','627').splitlines() if ': ' in x)
assert cfg['cores']=='3' and int(cfg['memory']) in [15360,20480] and int(cfg['swap']) ==2048
mem=dict((x.split(':')[0],int(x.split()[1])*1024) for x in Path('/proc/meminfo').read_text().splitlines() if x.startswith(('MemTotal:','MemAvailable:')));assert mem['MemTotal']>30*2**30 and mem['MemAvailable']>15*2**30
# Operational CT guard19GiB, plus6GiB physical host reserve (existing runtime floor4GiB).
assert mem['MemAvailable']-max(0,19*2**30-int((cg/'memory.current').read_text()))>6*2**30,'Insufficient physical host margin at CT guard19GiB'
assert not any(n.startswith(('qwen-','chatterbox-')) for n in call('pct','exec','627','--','docker','ps','--format','{{.Names}}').splitlines())
pid=call('lxc-info','-n','627','-pH').strip();root=Path('/proc',pid,'root');jobs=root/'srv/voicebox/qwen-worker/jobs'
assert not any(json.loads(p.read_text()).get('status') in ['running','queued'] for p in jobs.glob('*/state.json'))
changed=int(cfg['memory'])!=20480
if changed:
 backup=Path('/opt/voicebox-qwen-627/backups/d087-resource-before');backup.mkdir(mode=0o700,parents=True,exist_ok=False)
 (backup/'627.conf').write_bytes(Path('/etc/pve/lxc/627.conf').read_bytes())
 for name in ['agent.py','supervise.py','guards.py']:(backup/name).write_bytes((Path('/opt/voicebox-qwen-627')/name).read_bytes())
 hdd=Path('/mnt/storage/d087-resource-before');hdd.mkdir(mode=0o700,exist_ok=False)
 import shutil
 assert call('findmnt','-no','SOURCE','/mnt/storage').strip()=='/dev/sdb'
 for p in backup.iterdir():shutil.copy2(p,hdd/p.name)
 archive=root/'opt/voicebox/backups/d087-before-deploy.tar.gz';assert archive.is_file()
 expected='466deaa31ef647b277d3559198b577b364754d0fae9c02979936b76db2b005ab'
 assert hashlib.sha256(archive.read_bytes()).hexdigest()==expected
 shutil.copy2(archive,hdd/'application.tar.gz')
 call('pct','set','627','--memory','20480','--swap','2048')
assert int((cg/'memory.max').read_text())==20*2**30 and int((cg/'memory.swap.max').read_text())==2*2**30
new=identity();assert own==new
others={p.stem:hashlib.sha256(p.read_bytes()).hexdigest() for p in Path('/etc/pve/lxc').glob('*.conf') if p.stem!='627'};assert others=={k:v for k,v in before.items() if k!='627'}
print(json.dumps({'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'before_resources':{k:cfg[k] for k in ['cores','memory','swap']},'after_memory_bytes':int((cg/'memory.max').read_text()),'after_swap_bytes':int((cg/'memory.swap.max').read_text()),'voicebox_identity':new,'changed':changed,'restart':False,'others_unchanged':True}))
