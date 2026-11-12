#!/usr/bin/env python3
"""Snapshot de datos Voicebox en CT627; no elimina originales ni backups anteriores."""
import argparse,datetime,hashlib,json,shutil,socket,sqlite3,tarfile
from pathlib import Path
assert socket.gethostname()=='infra-voicebox','Ejecutar solo en627'
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve();assert out.is_relative_to(Path('/opt/voicebox/backups')),'Usar directorio privado de backups Voicebox';out.parent.mkdir(parents=True,exist_ok=True);out.parent.chmod(0o700);assert not out.exists(),'No sobrescribir backups';assert not out.is_relative_to(Path('/srv/voicebox')),'Backup fuera de datos';out.mkdir(parents=True,mode=0o700)
# Ejecutar sin trabajos activos: coordinar audio/perfiles con copia SQLite consistente.
src=Path('/srv/voicebox/data');db=sqlite3.connect('file:'+str(src/'voicebox.db')+'?mode=ro',uri=True)
assert db.execute("select count(*) from generations where status='generating'").fetchone()[0]==0,'Hay generaciones activas; detener snapshot dependiente'
shutil.copytree(src,out/'data',ignore=shutil.ignore_patterns('voicebox.db','voicebox.db-wal','voicebox.db-shm'))
dst=sqlite3.connect(out/'data/voicebox.db');db.backup(dst);assert dst.execute('PRAGMA integrity_check').fetchone()[0]=='ok';dst.close();db.close()
shutil.copytree('/srv/voicebox/huggingface',out/'huggingface',symlinks=True)
# Owner originals are private outside the API volume; preserve them when provided.
originals=Path('/srv/voicebox/private-originals')
if originals.exists():
 assert originals.is_dir() and not originals.is_symlink()
 shutil.copytree(originals,out/'private-originals')
for name in ['compose.yml','Dockerfile.cpu','deploy.sh','lan-only.sh','voicebox-lan-only.service','prepare-models.py','model-lock.json','image-lock.json','image-id.txt','requirements-observed.txt']:
 shutil.copy2(Path('/opt/voicebox')/name,out/name)
def digest(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
# Preserve the exact reviewed overlay, offline wheels and owner-only workflow too.
for version in ['d068','d069']:
 overlay=Path('/opt/voicebox/pilot-'+version)
 if overlay.is_dir():shutil.copytree(overlay,out/('overlay-'+version),symlinks=True)
manifest={str(f.relative_to(out)):digest(f) for f in out.rglob('*') if f.is_file() and not f.is_symlink()};(out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
archive=out.with_suffix('.tar.gz')
with archive.open('xb') as stream:
 archive.chmod(0o600)
 with tarfile.open(fileobj=stream,mode='w:gz') as bundle:bundle.add(out,arcname='snapshot')
print(json.dumps({'result':'PASS','files':len(manifest),'archive':str(archive),'sha256':digest(archive),'observed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}))
