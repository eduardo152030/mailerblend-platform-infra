import json,hashlib,urllib.request,os
from pathlib import Path
lock=json.loads(Path('/model-lock.json').read_text());root=Path('/models');root.mkdir(exist_ok=True)
assert sum(x['bytes'] for x in lock['files'])<400*1024**2
for f in lock['files']:
 p=root/f['target'];p.parent.mkdir(parents=True,exist_ok=True)
 if not p.exists():
  tmp=p.with_suffix(p.suffix+'.partial')
  with urllib.request.urlopen('https://huggingface.co/'+f['repo']+'/resolve/'+f['revision']+'/'+f['name'],timeout=90) as src,tmp.open('wb') as out:
   while True:
    b=src.read(1024**2)
    if not b:break
    out.write(b)
  assert tmp.stat().st_size==f['bytes'];tmp.rename(p)
 assert p.stat().st_size==f['bytes']
 h=hashlib.sha256(p.read_bytes()).hexdigest()
 if f['sha256']:assert h==f['sha256']
 f['sha256']=h;p.chmod(0o644)
root.joinpath('verified-lock.json').write_text(json.dumps(lock,indent=2)+'\n');print(json.dumps({'result':'PASS','files':len(lock['files']),'bytes':sum(x['bytes'] for x in lock['files']),'model_loaded':False}))
