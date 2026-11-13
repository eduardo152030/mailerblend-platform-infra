"""Create private candidate image context. No build/deploy/inference operations."""
from pathlib import Path
import argparse,shutil,hashlib,json
BASE='sha256:09774c5b7c535185c901557ddb6c69a4f8bb38ceff2c6998e19bab403b8e94ea'
def stage(dist,out):
    here=Path(__file__).resolve().parent;old=here.parent/'candidate-d083'
    assert (dist/'index.html').is_file() and not out.exists()
    (out/'backend').mkdir(parents=True,mode=0o700);(out/'patches').mkdir()
    for n in ['isolated_backend.py','qwen_language_policy.py','d077_contract.py']:shutil.copy2(old/n,out/'backend'/n)
    for n in ['isolated_chatterbox_backend.py','engine_policy.py']:shutil.copy2(here/n,out/'backend'/n)
    for folder,name in [(old,'d083.py'),(here,'d085.py')]:shutil.copy2(folder/'patch.py',out/'patches'/name)
    (out/'controller').mkdir();(out/'worker').mkdir()
    for n in ['agent.py','engine_policy.py','readiness.py','supervise_chatterbox.py']:shutil.copy2(here/n,out/'controller'/n)
    shutil.copy2(old/'qwen_language_policy.py',out/'controller/qwen_language_policy.py')
    for n in ['worker.py','qwen_language_policy.py','d077_contract.py']:shutil.copy2(old/n,out/'worker'/n)
    for n in ['chatterbox_worker.py','engine_policy.py']:shutil.copy2(here/n,out/'worker'/n)
    shutil.copy2(here/'Dockerfile',out/'Dockerfile');shutil.copytree(dist,out/'frontend')
    manifest={'base_image':BASE,'files':{str(p.relative_to(out)):hashlib.sha256(p.read_bytes()).hexdigest() for p in out.rglob('*') if p.is_file()}}
    (out/'context-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');return manifest
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--dist',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();print(json.dumps(stage(a.dist,a.out)))
