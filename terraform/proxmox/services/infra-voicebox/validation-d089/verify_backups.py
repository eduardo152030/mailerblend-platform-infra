"""Verify HDD recovery bytes; never restore a database over production."""
from pathlib import Path
import hashlib,json,subprocess,tarfile,sqlite3,shutil
BASE=Path('/mnt/storage/d089');BASE.mkdir(mode=0o700,exist_ok=True)
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return h.hexdigest()
assert subprocess.check_output(['findmnt','-no','SOURCE','/mnt/storage'],text=True).strip()=='/dev/sdb'
checks={}
for name,p,expected in [
 ('D084',Path('/mnt/storage/dump/vzdump-lxc-627-2026_11_12-15_49_14.tar.zst'),'3fa4107c8566fa9b0c4cd22b21a7423cc16901245ae613bf52f983bcd790afcb'),
 ('D085',Path('/mnt/storage/d085-before-deploy/application.tar.gz'),'9ac082cf85ac771a632abc4000b2f198b1de7b6c95c896aeae131d6021a390d1'),
 ('D087',Path('/mnt/storage/d087b-before-deploy/application.tar.gz'),'a090fdab2af2ad0932a73bc4d3815a460f0bfb0873bf74ccf509904ae86d536c')]:
 actual=sha(p);assert actual==expected,name+' archive changed';checks[name]={'bytes':p.stat().st_size,'sha256':actual,'unchanged_since_verified_restore':True}
 print(json.dumps({'backup_verified':name}),flush=True)
rest=Path('/mnt/storage/d084-627/restore-rootfs');assert (rest/'etc/vzdump/pct.conf').is_file()
db=sqlite3.connect('file:'+str(rest/'srv/voicebox/data/voicebox.db')+'?mode=ro',uri=True);assert db.execute('pragma integrity_check').fetchone()[0]=='ok';db.close()
pid=subprocess.check_output(['lxc-info','-n','627','-pH'],text=True).strip();root=Path('/proc',pid,'root');original=root/'opt/voicebox/backups/d089-before-deploy.tar.gz';target=BASE/'application.tar.gz';assert not target.exists();shutil.copy2(original,target);assert sha(original)==sha(target)
out=BASE/'restore';out.mkdir(mode=0o700)
with tarfile.open(target,'r:gz') as t:
 for m in t.getmembers():
  assert not m.issym() and not m.islnk() and not m.isdev()
  assert (out/m.name).resolve().is_relative_to(out.resolve())
 t.extractall(out)
snapshot=out/'snapshot';manifest=json.loads((snapshot/'manifest.json').read_text())
for n,h in manifest.items():assert sha(snapshot/n)==h
with sqlite3.connect('file:'+str(snapshot/'data/voicebox.db')+'?mode=ro',uri=True) as db:assert db.execute('pragma integrity_check').fetchone()[0]=='ok'
checks['D089']={'sha256':sha(target),'files_verified':len(manifest),'isolated_restore':True,'sqlite_integrity':'ok','no_production_restore':True}
result={'result':'PASS','backups':checks};(BASE/'backups-verified.json').write_text(json.dumps(result));print(json.dumps(result))
