"""CT627 read-only backup duplicate verifier. No extraction, no deletions."""
from pathlib import Path
import os,json,tarfile,hashlib,stat,time
os.nice(10)
base=Path('/opt/voicebox/backups')
def digest(f):
 h=hashlib.sha256()
 for b in iter(lambda:f.read(2**20),b''):h.update(b)
 return h.hexdigest()
for directory in sorted(base.iterdir()):
 archive=base/(directory.name+'.tar.gz')
 if not directory.is_dir() or not archive.is_file():continue
 start=time.monotonic();r={'name':directory.name,'archive_bytes':archive.stat().st_size,'expanded_allocated_bytes':0,'status':'IN_PROGRESS'}
 try:
  fs={}
  for p in directory.rglob('*'):
   st=p.lstat();r['expanded_allocated_bytes']+=st.st_blocks*512;name=str(p.relative_to(directory))
   if p.is_symlink():fs[name]={'type':'symlink','link':os.readlink(p),'mode':stat.S_IMODE(st.st_mode)}
   elif p.is_file():
    with p.open('rb') as f:sha=digest(f)
    fs[name]={'type':'file','bytes':st.st_size,'sha256':sha,'mode':stat.S_IMODE(st.st_mode)}
   elif p.is_dir():fs[name]={'type':'directory','mode':stat.S_IMODE(st.st_mode)}
   else:raise AssertionError('Unsupported file type')
  archived={}
  with archive.open('rb') as f:r['archive_sha256']=digest(f)
  with tarfile.open(archive,mode='r|gz') as t:
   for m in t:
    name=Path(m.name);assert not name.is_absolute() and '..' not in name.parts
    assert name.parts[0]=='snapshot';rel=str(Path(*name.parts[1:]))
    if rel=='.':continue
    if m.isdir():archived[rel]={'type':'directory','mode':m.mode}
    elif m.isreg():
     with t.extractfile(m) as f:sha=digest(f)
     archived[rel]={'type':'file','bytes':m.size,'sha256':sha,'mode':m.mode}
    elif m.issym():
     assert not Path(m.linkname).is_absolute();assert (directory/rel).resolve().is_relative_to(directory)
     archived[rel]={'type':'symlink','link':m.linkname,'mode':m.mode}
    else:raise AssertionError('Unsupported archive member')
  differences=[k for k in set(fs)|set(archived) if fs.get(k)!=archived.get(k)]
  r.update(status='IDENTICAL' if not differences else 'DIFFERENT',entries=len(fs),mismatches=len(differences),manifest_sha256=fs.get('manifest.json',{}).get('sha256'))
  # Content and symlink manifests remain private; never emit user recordings/text.
 except Exception as e:r.update(status='ERROR',error=type(e).__name__+': '+str(e))
 r['seconds']=time.monotonic()-start;print(json.dumps(r),flush=True)
