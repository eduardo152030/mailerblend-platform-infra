"""PVE read-only D080 preflight. Do not load a model or submit a generation."""
from pathlib import Path
import json,subprocess,hashlib,time,sys
sys.path.insert(0,'/opt/voicebox-qwen-627')
from guards import predictive_preflight
cg=Path('/sys/fs/cgroup/lxc/627');st=dict((k,int(v)) for k,v in (x.split() for x in (cg/'memory.stat').read_text().splitlines()));current=int((cg/'memory.current').read_text());m=dict((x.split(':')[0],int(x.split()[1])*1024) for x in Path('/proc/meminfo').read_text().splitlines() if x.startswith(('MemTotal:','MemAvailable:')))
assert int((cg/'memory.max').read_text())==15*2**30 and int((cg/'memory.swap.max').read_text())==2*2**30
p=predictive_preflight({'ct_current':current});assert p['passed'];assert m['MemAvailable']>12*2**30
code="""from pathlib import Path
import hashlib,json,sqlite3,subprocess,urllib.request,os
b=Path('/opt/voicebox/backups/d081-functional-before');manifest=json.loads((b/'manifest.json').read_text());bad=[];count=0
for rel,digest in manifest.items():
 if rel.startswith(('data/','private-originals/','qwen-jobs/')) and rel not in ['data/voicebox.db','qwen-jobs/agent-heartbeat.json']:
  k,rest=rel.split('/',1);root={'data':'/srv/voicebox/data','private-originals':'/srv/voicebox/private-originals','qwen-jobs':'/srv/voicebox/qwen-worker/jobs'}[k];f=Path(root)/rest;count+=1
  if not f.is_file() or hashlib.sha256(f.read_bytes()).hexdigest()!=digest:bad.append(rel)
assert not bad,'Protected data changed'
a=sqlite3.connect(b/'data/voicebox.db');z=sqlite3.connect('file:/srv/voicebox/data/voicebox.db?mode=ro',uri=True)
assert a.execute('select * from profiles').fetchall()==z.execute('select * from profiles').fetchall()
assert a.execute('select * from profile_samples').fetchall()==z.execute('select * from profile_samples').fetchall()
assert not z.execute("select count(*) from generations where status in ('generating','loading_model')").fetchone()[0]
names=subprocess.check_output(['docker','ps','--format','{{.Names}}'],text=True).splitlines();assert not any(n.startswith('qwen-') for n in names)
assert not any(json.loads(f.read_text()).get('status') in ['queued','running'] for f in Path('/srv/voicebox/qwen-worker/jobs').glob('*/state.json'))
health=json.load(urllib.request.urlopen('http://192.168.1.127:17493/health'));assert health['status']=='healthy' and not health['model_loaded']
endpoints={}
for key,url in [('node','http://192.168.1.127:9100/metrics'),('cadvisor','http://192.168.1.127:8085/metrics')]:
 r=urllib.request.urlopen(url,timeout=8);endpoints[key]=r.status;r.close()
p=Path('/srv/voicebox/qwen-worker/jobs');space=os.statvfs(p).f_bavail*os.statvfs(p).f_frsize;assert space>10*2**30
print(json.dumps({'protected_files_checked':count,'protected_files_unchanged':True,'profile_and_samples_unchanged':True,'health':health,'exporters':endpoints,'free_disk_bytes':space,'no_active_inference':True}))
"""
checks=json.loads(subprocess.check_output(['pct','exec','627','--','python3','-c',code],text=True));assert subprocess.check_output(['systemctl','is-active','voicebox-qwen-627.service'],text=True).strip()=='active'
print(json.dumps({'predictive_preflight':p,'ct_memory_max':int((cg/'memory.max').read_text()),'ct_swap_max':int((cg/'memory.swap.max').read_text()),'anon':st['anon'],'file':st['file'],'kernel':st['kernel'],'swap':int((cg/'memory.swap.current').read_text()),'psi':(cg/'memory.pressure').read_text(),'events':(cg/'memory.events').read_text(),'host':m,'host_psi':Path('/proc/pressure/memory').read_text(),'checks':checks}))
