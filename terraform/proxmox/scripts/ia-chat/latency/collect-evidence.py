#!/usr/bin/env python3
"""Copia solo JSON sintéticos de /root/ia-local/latency y métricas de benchmark completas."""
import subprocess,shlex,json,tarfile,io
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];DEST=ROOT/'docs/roadmap/evidence/ia-chat-latency-2026-11-13'
code="""import pathlib,tarfile,io,json,sys
root=pathlib.Path('/root/ia-local/latency');out=io.BytesIO()
with tarfile.open(fileobj=out,mode='w:gz') as t:
 for f in root.glob('*.json'):
  json.loads(f.read_text());t.add(f,arcname=f.name)
 for f in (root/'bench').glob('*.json'):
  if '-previous-' in f.name:continue
  if f.name.endswith('-memory.json'):
   partner=f.with_name(f.name.replace('-memory.json','.json'))
   if not partner.exists():continue
  else:
   partner=f.with_name(f.stem+'-memory.json')
   if not partner.exists():continue
  try:d=json.loads(f.read_text());json.loads(partner.read_text())
  except (ValueError,OSError):continue
  t.add(f,arcname='bench/'+f.name)
sys.stdout.buffer.write(out.getvalue())"""
ssh=['ssh','-o','UserKnownHostsFile='+str(Path.home()/'.ssh/known_hosts'),'-o','StrictHostKeyChecking=yes','-o','BatchMode=yes','pve'];body=subprocess.check_output(ssh+[shlex.join(['python3','-c',code])]);count=0
with tarfile.open(fileobj=io.BytesIO(body)) as t:
 for m in t.getmembers():
  assert m.isfile() and not m.name.startswith('/') and '..' not in Path(m.name).parts and m.name.endswith('.json')
  data=t.extractfile(m).read();json.loads(data);p=DEST/m.name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);count+=1
print(json.dumps({'public_json_files_copied':count,'secrets_or_databases_copied':False}))
