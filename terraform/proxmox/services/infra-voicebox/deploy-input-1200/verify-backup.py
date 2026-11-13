"""PVE: verify fresh backup and isolated restore on HDD before deploy."""
from pathlib import Path
import subprocess,hashlib,json,tarfile,sqlite3,shutil
pid=subprocess.check_output(['lxc-info','-n','627','-pH'],text=True).strip();root=Path('/proc',pid,'root');base=Path('/mnt/storage/input1200-deploy')
assert subprocess.check_output(['findmnt','-no','SOURCE','/mnt/storage'],text=True).strip()=='/dev/sdb'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return h.hexdigest()
a=root/'opt/voicebox/backups/input1200-before-deploy.tar.gz';b=base/'application.tar.gz';assert not b.exists();shutil.copy2(a,b);assert sha(a)==sha(b)
out=base/'restored';out.mkdir(mode=0o700)
with tarfile.open(b,'r:gz') as t:
 for m in t.getmembers():assert not m.issym() and not m.islnk() and not m.isdev() and (out/m.name).resolve().is_relative_to(out.resolve())
 t.extractall(out)
snapshot=out/'snapshot';manifest=json.loads((snapshot/'manifest.json').read_text())
for n,h in manifest.items():assert sha(snapshot/n)==h
with sqlite3.connect('file:'+str(snapshot/'data/voicebox.db')+'?mode=ro',uri=True) as db:
 assert db.execute('pragma integrity_check').fetchone()[0]=='ok'
 counts={n:db.execute('select count(*) from '+n).fetchone()[0] for n in ['profiles','profile_samples','generations']}
r={'result':'PASS','archive_sha256':sha(b),'files_verified':len(manifest),'sqlite_integrity':'ok','database_counts':counts,'restored_outside_production':True};(base/'backup-verified.json').write_text(json.dumps(r));print(json.dumps(r))
