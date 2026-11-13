"""Local context only. No production data, secrets or inference."""
from pathlib import Path
import argparse,hashlib,json,shutil,tarfile
p=argparse.ArgumentParser();p.add_argument('--ui',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(mode=0o700)
here=Path(__file__).resolve().parent;root=here.parent
shutil.copytree(a.ui/'web/dist',a.out/'frontend');shutil.copy2(root/'candidate-d085/engine_policy.py',a.out/'engine_policy.py');shutil.copy2(here/'Dockerfile',a.out/'Dockerfile')
# Separate target controller/worker policy; 19GiB aggregate guard remains unchanged.
shutil.copy2(root/'maintenance-d087/engine_policy.py',a.out/'controller-engine_policy.py')
manifest={'source_commit':'3987cabf9be44ed362c3a86c8a5924bd7a76ee04','base_image_id':'sha256:212703647c03d428adc30f8bf4b864af82690eb41f4fe8ca052ff10dbaa45386','candidate_tag':'local/voicebox:input1200-3987cab','files':{str(p.relative_to(a.out)):hashlib.sha256(p.read_bytes()).hexdigest() for p in a.out.rglob('*') if p.is_file()}}
(a.out/'context-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
with tarfile.open(a.out.with_suffix('.tar'),'w') as t:t.add(a.out,arcname='context')
print(json.dumps(manifest))
