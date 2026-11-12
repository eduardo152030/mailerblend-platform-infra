"""Read-only integrity validation of expanded duplicate backups, no restore in CT."""
from pathlib import Path
import json,hashlib,sqlite3,os
os.nice(10)
for directory in sorted(Path('/opt/voicebox/backups').iterdir()):
 if not directory.is_dir() or not directory.with_suffix('.tar.gz').exists():continue
 manifest=json.loads((directory/'manifest.json').read_text());valid=True
 for name,expected in manifest.items():
  p=directory/name;assert p.resolve().is_relative_to(directory)
  h=hashlib.sha256()
  with p.open('rb') as f:
   for b in iter(lambda:f.read(2**20),b''):h.update(b)
  valid=valid and h.hexdigest()==expected
 db=sqlite3.connect('file:'+str(directory/'data/voicebox.db')+'?mode=ro&immutable=1',uri=True);integrity=db.execute('PRAGMA integrity_check').fetchone()[0];db.close()
 print(json.dumps({'name':directory.name,'manifest_files':len(manifest),'manifest_valid':valid,'sqlite_integrity':integrity}),flush=True)
