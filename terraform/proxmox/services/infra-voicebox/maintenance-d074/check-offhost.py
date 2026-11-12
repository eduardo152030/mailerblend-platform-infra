"""Local recovery archive index: sizes first, then SHA256; excludes extracted/private voice trees."""
from pathlib import Path
import os,json,hashlib
root=Path.home()/'.local/share/mailerblend-recovery';out=root/'voicebox-d074';old=json.loads((root/'voicebox-d073/storage-detail-private.json').read_text());sizes={x['bytes'] for x in old['backups'] if x['kind']=='file'}
r=[]
roots=[p for p in root.glob('voicebox-d0*') if p.is_dir()]+[root/'new-lxc/voicebox-d063']
for base in roots:
 for directory,dirs,files in os.walk(base):
  dirs[:]=[x for x in dirs if not x.startswith('restore') and x not in ['source','build','.git','node_modules','snapshot','originals','models']]
  for name in files:
   p=Path(directory)/name
   if not name.endswith('.tar.gz') or p.stat().st_size not in sizes:continue
   h=hashlib.sha256()
   with p.open('rb') as f:
    for b in iter(lambda:f.read(4*2**20),b''):h.update(b)
   r.append({'relative_path':str(p.relative_to(root)),'bytes':p.stat().st_size,'sha256':h.hexdigest()})
(out/'offhost-archives-private.json').write_text(json.dumps(r,indent=2));print('Offhost archives hashed',len(r))
