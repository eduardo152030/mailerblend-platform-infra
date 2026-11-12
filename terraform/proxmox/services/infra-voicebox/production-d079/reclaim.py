"""PVE-only D079 selective advice. PLAN is injected from the exact D078 manifest."""
import argparse,datetime,fcntl,json,os,re,stat,subprocess,time
from pathlib import Path

CG=Path('/sys/fs/cgroup/lxc/627')
def ct(*args):return subprocess.check_output(['pct','exec','627','--',*args],text=True,timeout=20)
def measure():
 stats=dict((k,int(v)) for k,v in (x.split() for x in (CG/'memory.stat').read_text().splitlines()))
 return {'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'current':int((CG/'memory.current').read_text()),'anon':stats['anon'],'file':stats['file'],'kernel':stats['kernel'],'swap':int((CG/'memory.swap.current').read_text()),'psi':(CG/'memory.pressure').read_text(),'events':(CG/'memory.events').read_text()}
def resident(paths):
 d=json.loads(subprocess.check_output(['fincore','--json','--bytes','-o','RES,SIZE,FILE',*[str(p) for p in paths]],text=True,timeout=20))
 return [{'file':Path(x['file']).name,'resident_bytes':int(x['res']),'size_bytes':int(x['size'])} for x in d['fincore']]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--execute',action='store_true');args=ap.parse_args()
 assert len(PLAN['candidates'])==5
 if not args.execute:return {'plan_only':True,'candidates':PLAN['candidates']}
 lock=open('/run/lock/qwen-d077-627.lock','a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 pid=subprocess.check_output(['lxc-info','-n','627','-pH'],text=True).strip();assert pid.isdigit();root=Path('/proc',pid,'root');assert (root/'etc/hostname').read_text().strip()=='infra-voicebox'
 assert int((CG/'memory.max').read_text())==10*2**30 and int((CG/'memory.swap.max').read_text())==2*2**30
 names=ct('docker','ps','--format','{{.Names}}').splitlines();assert not any(n.startswith('qwen-') for n in names),'Active inference'
 active=int(ct('python3','-c',"from pathlib import Path;import json;print(sum(json.loads(p.read_text()).get('status') in ['queued','running'] for p in Path('/srv/voicebox/qwen-worker/jobs').glob('*/state.json')))").strip());assert active==0,'Active queue'
 scan="""import subprocess,re,json
lines=subprocess.check_output(['ps','-eo','comm=,args='],text=True).splitlines()
hits=[]
for line in lines:
 parts=line.split()
 if parts and parts[0] in ['docker','ctr','nerdctl','buildctl','docker-buildx','buildx'] and any(x in ['save','load','export','import','build','pull','push','commit'] for x in parts[1:]):hits.append(parts[0])
print(json.dumps({'incompatible':hits}))
"""
 assert not json.loads(ct('python3','-c',scan))['incompatible'],'Active incompatible Docker operation'
 paths=[];fingerprints={}
 for item in PLAN['candidates']:
  name=item['path_in_CT627'];assert re.fullmatch(r'/var/lib/containerd/io.containerd.content.v1.content/blobs/sha256/[a-f0-9]{64}',name)
  p=root/name.lstrip('/');s=p.lstat();assert stat.S_ISREG(s.st_mode) and s.st_size==item['size_bytes'];paths.append(p);fingerprints[p]=(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns)
 keys={(v[0],v[1]) for v in fingerprints.values()};pids=set()
 for p in CG.rglob('cgroup.procs'):
  try:pids.update(p.read_text().split())
  except OSError:pass
 users=[]
 for p in pids:
  try:
   for fd in Path('/proc',p,'fd').iterdir():
    try:
     s=fd.stat()
     if (s.st_dev,s.st_ino) in keys:users.append({'pid':p,'kind':'open_fd'})
    except OSError:pass
   for line in Path('/proc',p,'maps').read_text().splitlines():
    fields=line.split();dev=fields[3].split(':');ino=int(fields[4]);device=os.makedev(int(dev[0],16),int(dev[1],16))
    if (device,ino) in keys:users.append({'pid':p,'kind':'mapping'})
  except OSError:pass
 assert not users,'Candidate used by active process'
 images=ct('docker','image','ls','--no-trunc','-q').splitlines()
 result={'before':measure(),'resident_before':resident(paths),'checks':{'no_inference':True,'no_active_queue':True,'no_incompatible_operations':True,'no_open_fds_or_mappings':True},'advice_calls':[]}
 for p in paths:
  fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW)
  try:
   s=os.fstat(fd);assert (s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns)==fingerprints[p]
   os.posix_fadvise(fd,0,0,os.POSIX_FADV_DONTNEED)
   result['advice_calls'].append({'path_in_CT627':'/'+str(p.relative_to(root)),'operation':'POSIX_FADV_DONTNEED','once':True})
  finally:os.close(fd)
 result['after_samples']=[]
 for _ in range(6):time.sleep(.5);result['after_samples'].append(measure())
 result['after']=result['after_samples'][-1];result['resident_after']=resident(paths)
 for p in paths:
  s=p.stat();assert (s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns)==fingerprints[p]
 assert images==ct('docker','image','ls','--no-trunc','-q').splitlines()
 result.update(success=True,file_bytes_reclaimed_observed=result['before']['file']-result['after']['file'],current_bytes_recovered_observed=result['before']['current']-result['after']['current'],candidate_residency_reduced_bytes=sum(x['resident_bytes'] for x in result['resident_before'])-sum(x['resident_bytes'] for x in result['resident_after']),files_and_images_unchanged=True,no_global_drop_caches=True)
 lock.close();return result
if __name__=='__main__':print(json.dumps(main()),flush=True)
