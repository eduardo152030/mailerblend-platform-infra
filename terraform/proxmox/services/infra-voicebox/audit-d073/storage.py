"""CT627 read-only allocated disk accounting and sanitized Docker metadata."""
import os,subprocess,json,datetime,hashlib,sqlite3,wave,collections
from pathlib import Path

def run(args,timeout=50):
 r=subprocess.run(args,capture_output=True,text=True,timeout=timeout);return {'returncode':r.returncode,'stdout':r.stdout}
def du(path,depth=1):return run(['du','-x','-B1','--max-depth='+str(depth),path],90)
def filesummary(path):
 size=allocated=count=0;seen=set()
 for root,ds,fs in os.walk(path,followlinks=False):
  for name in fs:
   p=Path(root)/name
   try:
    st=p.lstat();key=(st.st_dev,st.st_ino)
    if key in seen:continue
    seen.add(key);count+=1;size+=st.st_size;allocated+=st.st_blocks*512
   except OSError:pass
 return {'file_count':count,'apparent_bytes':size,'allocated_file_bytes':allocated}
r={'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'df':run(['df','-B1','/']),'df_inodes':run(['df','-i','/']),'paths':{p:du(p,2 if p in ['/srv/voicebox','/opt/voicebox','/var/lib'] else 1) for p in ['/','/srv/voicebox','/opt/voicebox','/var/lib','/var/log','/tmp','/var/tmp','/var/cache']},'docker_summary':run(['docker','system','df']),'docker_verbose':run(['docker','system','df','-v']),'docker_cache':run(['docker','buildx','du','--verbose']),'journal_disk':run(['journalctl','--disk-usage'])}
ids=run(['docker','ps','-aq'])['stdout'].split();containers=json.loads(run(['docker','inspect',*ids])['stdout']) if ids else []
r['containers']=[{'id':c['Id'],'name':c['Name'],'image':c['Image'],'status':c['State']['Status'],'pid':c['State']['Pid'],'started_at':c['State']['StartedAt'],'restarts':c['RestartCount'],'health':c['State'].get('Health',{}).get('Status'),'oom_killed':c['State']['OOMKilled'],'memory_limit':c['HostConfig']['Memory'],'memory_swap_limit':c['HostConfig']['MemorySwap'],'nano_cpus':c['HostConfig']['NanoCpus'],'mounts':[{'type':m['Type'],'source':m['Source'],'destination':m['Destination'],'rw':m['RW']} for m in c['Mounts']],'log_bytes':Path(c['LogPath']).stat().st_size if c.get('LogPath') and Path(c['LogPath']).exists() else 0} for c in containers]
r['model_files']={}
for category,pattern in [('kokoro','/srv/voicebox/huggingface/hub/models--hexgrad--Kokoro*'),('qwen_base','/srv/voicebox/huggingface/hub/models--Qwen--*Base'),('qwen_cv','/srv/voicebox/pilot-d066/huggingface/hub/models--Qwen--*'),('openvoice','/srv/voicebox/openvoice/models'),('piper','/srv/voicebox/data/models/piper')]:
 import glob
 r['model_files'][category]={p:filesummary(p) for p in glob.glob(pattern)}
ref=Path('/srv/voicebox/data/profiles/1fd00418-2a79-4178-883f-af6c3f5e07ee/8840f5e1-990b-463e-b94e-e72beef61917.wav')
r['reference_sha256']=hashlib.sha256(ref.read_bytes()).hexdigest();r['original_hashes']=sorted(hashlib.sha256(p.read_bytes()).hexdigest() for p in Path('/srv/voicebox/private-originals').glob('*-original.wav'))
dbs=list(Path('/srv/voicebox/data').glob('*.db'));assert len(dbs)==1;c=sqlite3.connect('file:'+str(dbs[0])+'?mode=ro',uri=True)
r['sqlite']={'quick_check':c.execute('PRAGMA quick_check').fetchone()[0],'profile_count':c.execute('select count(*) from profiles').fetchone()[0]}
r['top_level_regular_files']={p:sorted([{'name':x.name,'bytes':x.stat().st_size,'allocated':x.stat().st_blocks*512} for x in Path(p).iterdir() if x.is_file()],key=lambda x:x['allocated'],reverse=True)[:20] for p in ['/srv/voicebox','/opt/voicebox','/tmp','/var/tmp']}
print(json.dumps(r))
