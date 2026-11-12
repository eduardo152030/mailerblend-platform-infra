#!/usr/bin/env python3
"""Restauración aislada: paths confinados, sin devices/hardlinks ni extracción permisiva."""
import argparse,hashlib,json,shutil,sqlite3,tarfile,wave
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--archive',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve();assert not out.exists();out.mkdir(parents=True,mode=0o700)
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
with tarfile.open(a.archive) as bundle:
 members=bundle.getmembers();links=[]
 for m in members:
  assert not Path(m.name).is_absolute() and '..' not in Path(m.name).parts
  target=out/m.name;assert target.resolve().is_relative_to(out)
  if m.isdir():target.mkdir(parents=True,exist_ok=True)
  elif m.isreg():
   target.parent.mkdir(parents=True,exist_ok=True)
   with bundle.extractfile(m) as src,target.open('xb') as dst:shutil.copyfileobj(src,dst)
   target.chmod(0o600)
  elif m.issym():
   assert not Path(m.linkname).is_absolute();resolved=(target.parent/m.linkname).resolve();assert resolved.is_relative_to(out);links.append((target,m.linkname,resolved))
  else:raise AssertionError('Tipo de archivo no admitido')
 for target,link,resolved in links:
  assert resolved.is_file();target.parent.mkdir(parents=True,exist_ok=True);target.symlink_to(link)
snapshot=out/'snapshot';manifest=json.loads((snapshot/'manifest.json').read_text())
assert all(digest(snapshot/name)==expected for name,expected in manifest.items())
db=sqlite3.connect('file:'+str(snapshot/'data/voicebox.db')+'?mode=ro',uri=True);assert db.execute('pragma integrity_check').fetchone()[0]=='ok';completed=db.execute("select id,audio_path,engine from generations where status='completed'").fetchall()
references=db.execute('select audio_path from profile_samples').fetchall()
assert completed or references,'No completed audio or reference to verify'
for (stored,) in references:
 path=Path(stored)
 if path.is_absolute():path=path.relative_to('/app/data')
 elif path.parts[0]=='data':path=Path(*path.parts[1:])
 audio=snapshot/'data'/path;assert audio.resolve().is_relative_to(snapshot/'data') and audio.is_file()
 with wave.open(str(audio)) as w:assert w.getnframes()>0 and w.getnchannels()==1 and w.getsampwidth()==2 and 8000<=w.getframerate()<=96000
sample_rates=set()
for ident,stored,engine in completed:
 path=Path(stored)
 if path.is_absolute():path=path.relative_to('/app/data')
 elif path.parts[0]=='data':path=Path(*path.parts[1:])
 audio=snapshot/'data'/path;assert audio.resolve().is_relative_to(snapshot/'data') and audio.is_file()
 with wave.open(str(audio)) as w:
  assert w.getnframes()>0 and w.getnchannels()==1 and w.getsampwidth()==2
  expected={'kokoro':24000,'piper':22050,'qwen':24000,'qwen_custom_voice':24000}.get(engine)
  assert w.getframerate()==expected if expected else 8000<=w.getframerate()<=96000
  sample_rates.add(w.getframerate())
result={'result':'PASS','archive_sha256':digest(a.archive),'files_verified':len(manifest),'symlinks_confined':len(links),'sqlite_integrity':'ok','completed_audio_files':len(completed),'reference_audio_files':len(references),'sample_rates_verified':sorted(sample_rates),'mode':'isolated restoration outside PVE; original data and archives preserved'}
(out/'restore-check.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
