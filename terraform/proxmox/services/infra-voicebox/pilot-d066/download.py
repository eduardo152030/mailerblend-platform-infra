#!/usr/bin/env python3
"""Download a single pinned model into the isolated persistent pilot cache; never load it."""
import hashlib,json,os,time,resource
from pathlib import Path
from huggingface_hub import snapshot_download
lock=json.loads(Path('/model-lock.json').read_text());start=time.monotonic()
folder=Path(snapshot_download(repo_id=lock['repo'],revision=lock['revision'],allow_patterns=[f['rfilename'] for f in lock['files']],max_workers=1))
for f in lock['files']:
 p=folder/f['rfilename'];assert p.stat().st_size==f['size']
 with p.open('rb') as stream:
  h=hashlib.sha256()
  for b in iter(lambda:stream.read(1024*1024),b''):h.update(b)
  if f['lfs']:assert h.hexdigest()==f['lfs']['sha256']
  # Only this helper's downloaded file pages, no global drop_caches.
  if hasattr(os,'posix_fadvise'):os.posix_fadvise(stream.fileno(),0,0,os.POSIX_FADV_DONTNEED)
refs=folder.parent.parent/'refs';refs.mkdir(exist_ok=True);(refs/'main').write_text(lock['revision'])
print(json.dumps({'result':'PASS','stage':'download only; no model instantiated','revision':lock['revision'],'bytes':sum(f['size'] for f in lock['files']),'seconds':time.monotonic()-start,'helper_peak_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024}))
