"""PVE CT627-only bounded selective download; never loads tensors or touches Qwen."""
import subprocess,json,hashlib,os,time,urllib.request,datetime
from pathlib import Path
LOCK=Path('/mnt/storage/d085-model-input.json')  # orchestration passes selected manifest on stdin instead
manifest=json.load(__import__('sys').stdin)
pid=subprocess.check_output(['lxc-info','-n','627','-pH'],text=True).strip();root=Path('/proc',pid,'root')
assert (root/'etc/hostname').read_text().strip()=='infra-voicebox'
base=root/'srv/voicebox/chatterbox-d085';models=base/'models';models.mkdir(mode=0o700,exist_ok=True);os.chown(models,999,999)
health=json.load(urllib.request.urlopen('http://192.168.1.127:17493/health',timeout=10));assert health['status']=='healthy' and not health['model_loaded']
assert not any(json.loads(p.read_text()).get('status') in ['queued','running'] for p in (root/'srv/voicebox/qwen-worker/jobs').glob('*/state.json'))
def capacity():
 t=subprocess.check_output(['dmsetup','status','/dev/mapper/pve-data-tpool'],text=True).split();used,total=map(int,t[5].split('/'));free=(total-used)*65536;assert free>=total*65536*.2
 s=os.statvfs(models);assert s.f_bavail*s.f_frsize>20*2**30
 return {'pool_free_bytes':free,'rootfs_available_bytes':s.f_bavail*s.f_frsize}
initial=capacity();records=[]
for item in manifest['files']:
 name=item['name'];assert '/' not in name and name!='conds.pt'
 dst=models/name;assert not dst.exists() and not dst.with_suffix(dst.suffix+'.partial').exists()
 part=dst.with_suffix(dst.suffix+'.partial');h=hashlib.sha256();git=hashlib.sha1(('blob '+str(item['bytes'])+'\0').encode());count=0;next_check=0
 with urllib.request.urlopen(f"https://huggingface.co/{manifest['model_repo']}/resolve/{manifest['model_revision']}/{name}",timeout=60) as source,part.open('xb') as target:
  os.chmod(part,0o600);os.chown(part,999,999)
  for chunk in iter(lambda:source.read(1024*1024),b''):
   count+=len(chunk);assert count<=item['bytes'];h.update(chunk);git.update(chunk);target.write(chunk)
   if count>=next_check:
    m=capacity();assert initial['pool_free_bytes']-m['pool_free_bytes']<12*2**30
    records.append(dict(file=name,bytes=count,**m));next_check=count+64*2**20
  target.flush();os.fsync(target.fileno())
 assert count==item['bytes']
 if item.get('lfs_sha256'):assert h.hexdigest()==item['lfs_sha256']
 else:assert git.hexdigest()==item['git_blob_id']
 os.replace(part,dst);item['sha256']=h.hexdigest()
 print(json.dumps({'file':name,'bytes':count,'sha256':h.hexdigest(),'capacity':capacity()}),flush=True)
manifest['status']='DOWNLOADED_VERIFIED_NOT_LOADED';manifest['at_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();manifest['capacity_initial']=initial;manifest['capacity_final']=capacity();manifest['capacity_samples']=records
f=models/'manifest.json';f.write_text(json.dumps(manifest,indent=2));os.chown(f,999,999);f.chmod(0o600)
print(json.dumps({'result':'PASS','download_bytes':sum(x['bytes'] for x in manifest['files']),'capacity_final':capacity(),'no_models_loaded':True}),flush=True)
