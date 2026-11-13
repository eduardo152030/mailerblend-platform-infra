"""PVE read-only final D087b checks: successful Qwen, disabled failed CB, no residual."""
from pathlib import Path
import json,subprocess,hashlib,time,urllib.request,datetime
APP='sha256:212703647c03d428adc30f8bf4b864af82690eb41f4fe8ca052ff10dbaa45386'
def ct(*a):return subprocess.check_output(['pct','exec','627','--',*a],text=True,timeout=30)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
c=json.loads(ct('docker','inspect','voicebox'))[0];assert c['Image']==APP and c['State']['Health']['Status']=='healthy' and c['Config']['User']=='999:999' and c['RestartCount']==0
assert not c['HostConfig']['Privileged'] and not c['HostConfig']['CapAdd']
status=dict(l.split(':',1) for l in ct('docker','exec','voicebox','cat','/proc/1/status').splitlines() if ':' in l);assert status['Uid'].split()==['999']*4 and status['Gid'].split()==['999']*4 and int(status['CapEff'],16)==0
cfg=dict(l.split(': ',1) for l in subprocess.check_output(['pct','config','627'],text=True).splitlines() if ': ' in l);assert cfg['memory']=='20480' and cfg['cores']=='3' and cfg['swap']=='2048' and cfg['rootfs']=='local-lvm:vm-627-disk-0,size=100G'
pid=subprocess.check_output(['lxc-info','-n','627','-pH'],text=True).strip();root=Path('/proc',pid,'root');jobs=root/'srv/voicebox/qwen-worker/jobs'
assert not any(json.loads(p.read_text()).get('status') in ['running','queued'] for p in jobs.glob('*/state.json'))
names=ct('docker','ps','--format','{{.Names}}').splitlines();assert not any(n.startswith(('qwen-','chatterbox-')) for n in names)
h=json.loads((jobs/'agent-heartbeat.json').read_text());assert h['status']=='healthy' and time.time()-h['timestamp']<8 and not h['chatterbox']['ready']
health=json.load(urllib.request.urlopen('http://192.168.1.127:17493/health'));assert health['status']=='healthy' and not health['model_loaded']
caps=json.load(urllib.request.urlopen('http://192.168.1.127:17493/tts-capabilities'));assert caps['qwen']['ready'] and caps['qwen']['languages']==['es','en'] and not caps['chatterbox']['ready']
assert subprocess.check_output(['systemctl','is-active','voicebox-qwen-627.service'],text=True).strip()=='active'
release=json.loads(Path('/opt/voicebox-qwen-627/chatterbox-release.json').read_text());assert not release['enabled']
for folder,key in [(Path('/opt/voicebox-qwen-627'),'source_hashes'),(root/'srv/voicebox/qwen-worker/src','worker_hashes')]:
 for n,digest in release[key].items():assert sha(folder/n)==digest
base=root/'opt/voicebox/backups/d087b-before-deploy';manifest=json.loads((base/'manifest.json').read_text());count=0
for name,digest in manifest.items():
 if name.startswith(('data/','private-originals/','qwen-jobs/')) and name not in ['data/voicebox.db','qwen-jobs/agent-heartbeat.json']:
  group,rest=name.split('/',1);source={'data':'/srv/voicebox/data','private-originals':'/srv/voicebox/private-originals','qwen-jobs':'/srv/voicebox/qwen-worker/jobs'}[group];assert sha(root/source.lstrip('/')/rest)==digest;count+=1
checkpoint={}
for ident in ['7f348e9777214f4e827dcf7e1458c045','baa61a95c7b445248229aa697b941710','d7f2f5da9dfd49eab7df678ff1e25b82']:
 p=jobs/ident/'checkpoint';m=json.loads((p/'manifest.json').read_text());assert sha(p/'manifest.json')==json.loads((p/'COMMITTED.json').read_text())['manifest_sha256'] and sha(p/'codes.npy')==m['codes']['sha256'] and m['generation']['eos_emitted'];checkpoint[ident]={'integrity':True,'eos':True,'shape':m['codes']['shape']}
cg=Path('/sys/fs/cgroup/lxc/627');events=dict((k,int(v)) for k,v in (l.split() for l in (cg/'memory.events').read_text().splitlines()));assert events['oom']==events['oom_kill']==0
mem=dict((k,int(v)) for k,v in (l.split() for l in (cg/'memory.stat').read_text().splitlines()));m={l.split(':')[0]:int(l.split()[1])*1024 for l in Path('/proc/meminfo').read_text().splitlines() if l.startswith(('MemTotal:','MemAvailable:'))}
t=subprocess.check_output(['dmsetup','status','/dev/mapper/pve-data-tpool'],text=True).split();used,total=map(int,t[5].split('/'));assert used/total<.8
print(json.dumps({'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'app_image':APP,'app_id':c['Id'],'started_at':c['State']['StartedAt'],'healthy':True,'restart_count':c['RestartCount'],'uid':999,'gid':999,'cap_eff':status['CapEff'].strip(),'capabilities':caps,'resources':{k:cfg[k] for k in ['memory','cores','swap','rootfs']},'ct_pid':pid,'ct_current':int((cg/'memory.current').read_text()),'ct_stat':{k:mem[k] for k in ['anon','file','kernel']},'ct_swap':int((cg/'memory.swap.current').read_text()),'ct_psi':(cg/'memory.pressure').read_text(),'ct_events':events,'host':m,'pool_free_gib':(total-used)*65536/2**30,'pool_free_pct':(total-used)/total*100,'protected_files_checked':count,'protected_files_unchanged':True,'checkpoints':checkpoint,'no_residual_inference':True,'agent_active':True,'source_hashes_verified':True,'configs':{p.stem:sha(p) for p in Path('/etc/pve/lxc').glob('*.conf')}}))
