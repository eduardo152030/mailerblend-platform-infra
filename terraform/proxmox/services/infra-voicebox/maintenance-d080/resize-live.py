"""PVE: authorized CT627 live resize only, no restart or application changes."""
from pathlib import Path
import subprocess,json,hashlib,datetime
cg=Path('/sys/fs/cgroup/lxc/627')
def call(*a):return subprocess.check_output(a,text=True,timeout=30)
def identity():
 d=json.loads(call('pct','exec','627','--','docker','inspect','voicebox'))[0]
 return {'id':d['Id'],'image':d['Image'],'started':d['State']['StartedAt'],'restarts':d['RestartCount'],'health':d['State']['Health']['Status']}
before={p.stem:hashlib.sha256(p.read_bytes()).hexdigest() for p in Path('/etc/pve/lxc').glob('*.conf')};own=identity();assert own['health']=='healthy';cfg=dict(x.split(': ',1) for x in call('pct','config','627').splitlines() if ': ' in x)
assert cfg['cores']=='3' and int(cfg['memory']) in [10240,15360] and int(cfg['swap']) ==2048
mem=dict((x.split(':')[0],int(x.split()[1])*1024) for x in Path('/proc/meminfo').read_text().splitlines() if x.startswith(('MemTotal:','MemAvailable:')));assert mem['MemTotal']>30*2**30 and mem['MemAvailable']>15*2**30
changed=int(cfg['memory'])!=15360
if changed:
 backup=Path('/opt/voicebox-qwen-627/backups/d080-before');backup.mkdir(mode=0o700,parents=True,exist_ok=False)
 (backup/'627.conf').write_bytes(Path('/etc/pve/lxc/627.conf').read_bytes())
 for name in ['agent.py','supervise.py','guards.py']:(backup/name).write_bytes((Path('/opt/voicebox-qwen-627')/name).read_bytes())
 call('pct','set','627','--memory','15360','--swap','2048')
assert int((cg/'memory.max').read_text())==15*2**30 and int((cg/'memory.swap.max').read_text())==2*2**30
new=identity();assert own==new
others={p.stem:hashlib.sha256(p.read_bytes()).hexdigest() for p in Path('/etc/pve/lxc').glob('*.conf') if p.stem!='627'};assert others=={k:v for k,v in before.items() if k!='627'}
print(json.dumps({'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'before_resources':{k:cfg[k] for k in ['cores','memory','swap']},'after_memory_bytes':int((cg/'memory.max').read_text()),'after_swap_bytes':int((cg/'memory.swap.max').read_text()),'voicebox_identity':new,'changed':changed,'restart':False,'others_unchanged':True}))
