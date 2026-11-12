#!/usr/bin/env python3
"""Download exactly the pinned Piper files; no model instantiated, no repository snapshot."""
import argparse,hashlib,json,urllib.request
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
lock=json.loads(Path(__file__).with_name('model-lock.json').read_text());results=[]
for f in lock['files']:
 name=Path(f['rfilename']).name;target=a.output/name
 url='https://huggingface.co/'+lock['repo']+'/resolve/'+lock['revision']+'/'+f['rfilename']
 if not target.exists():
  with urllib.request.urlopen(url,timeout=60) as source,target.open('xb') as dest:
   for chunk in iter(lambda:source.read(1024**2),b''):dest.write(chunk)
 assert target.stat().st_size==f['size']
 digest=hashlib.sha256(target.read_bytes()).hexdigest();expected=f.get('lfs',{}).get('sha256')
 if expected:assert digest==expected
 results.append({'name':name,'bytes':target.stat().st_size,'sha256':digest,'lfs_sha_verified':bool(expected)})
print(json.dumps({'result':'PASS','repo':lock['repo'],'revision':lock['revision'],'files':results,'model_loaded':False},indent=2))
