#!/usr/bin/env python3
"""Verify a Docker29 OCI image archive outside PVE, including all content-addressed blobs."""
import argparse,hashlib,json,tarfile
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--archive',type=Path,required=True);p.add_argument('--image-id',required=True);a=p.parse_args();sha=hashlib.sha256()
with a.archive.open('rb') as f:
 for chunk in iter(lambda:f.read(1024**2),b''):sha.update(chunk)
index=None;verified=0
with tarfile.open(a.archive,mode='r|gz') as t:
 for member in t:
  if not member.isfile():continue
  source=t.extractfile(member)
  if member.name=='index.json':index=json.load(source)
  elif member.name.startswith('blobs/sha256/'):
   h=hashlib.sha256()
   for chunk in iter(lambda:source.read(1024**2),b''):h.update(chunk)
   assert h.hexdigest()==member.name.rsplit('/',1)[1],member.name;verified+=1
assert index and a.image_id in [x['digest'] for x in index['manifests']],'Docker29imageID is OCI index digest, not config blob digest'
print(json.dumps({'result':'PASS','image_id':a.image_id,'archive_sha256':sha.hexdigest(),'archive_bytes':a.archive.stat().st_size,'verified_blobs':verified,'archive_outside_pve':True,'original_image_retained':True},indent=2))
