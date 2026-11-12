#!/usr/bin/env python3
"""Descargar solo el modelo y voces fijados; verificar hashes antes del modo offline."""
import hashlib,json,os
from pathlib import Path
from huggingface_hub import snapshot_download
lock=json.loads(Path('/model-lock.json').read_text())
folder=Path(snapshot_download(repo_id=lock['repo'],revision=lock['revision'],allow_patterns=[x['rfilename'] for x in lock['files']]))
for item in lock['files']:
 p=folder/item['rfilename'];assert p.stat().st_size==item['size'],item['rfilename']
 if item['lfs']:
  h=hashlib.sha256()
  with p.open('rb') as f:
   for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
  assert h.hexdigest()==item['lfs']['sha256'],item['rfilename']
refs=folder.parent.parent/'refs';refs.mkdir(exist_ok=True);p=refs/'main'
if not p.exists() or p.read_text()!=lock['revision']:p.write_text(lock['revision'])
print(json.dumps({'result':'PASS','repo':lock['repo'],'revision':lock['revision'],'bytes':sum(x['size'] for x in lock['files']),'files':len(lock['files'])}))
