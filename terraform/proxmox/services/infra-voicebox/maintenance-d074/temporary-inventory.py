"""CT627: exact public build/APT temporary file inventory; read-only."""
from pathlib import Path
import json,hashlib,subprocess
rows=[]
for base in ['/var/cache/apt','/var/lib/apt/lists']:
 for p in Path(base).rglob('*'):
  if not p.is_file() or p.is_symlink() or p.name=='lock' or any(x in ['partial','auxfiles'] for x in p.parts):continue
  st=p.stat();h=hashlib.sha256()
  with p.open('rb') as f:
   for b in iter(lambda:f.read(2**20),b''):h.update(b)
  rows.append({'path':str(p),'bytes':st.st_size,'allocated_bytes':st.st_blocks*512,'sha256':h.hexdigest(),'function':'APT regenerated index/cache','dependencies':'No APT/dpkg active operation at removal; retain locks/directories','recovery':'apt-get update or cache regeneration; no installed packages removed'})
for name in ['/srv/voicebox/pilot-d072/build','/srv/voicebox/pilot-d072/build.tar.gz']:
 p=Path(name);st=p.stat();allocated=int(subprocess.check_output(['du','-sx','-B1',name],text=True).split()[0]);rows.append({'path':name,'bytes':st.st_size if p.is_file() else None,'allocated_bytes':allocated,'function':'Public source Docker build context/archive D072','dependencies':'Not mounted by running Voicebox; exclude private/ and jobs/','recovery':'Verified public source archive and build context outside CT627'})
print(json.dumps({'files':rows,'total_allocated_bytes':sum(x['allocated_bytes'] for x in rows),'apt_processes':subprocess.check_output(['ps','-eo','comm='],text=True).splitlines().count('apt-get')}))
