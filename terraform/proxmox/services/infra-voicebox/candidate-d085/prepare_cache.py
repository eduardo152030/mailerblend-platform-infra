"""Seed only the fixed Cangjie lookup expected by upstream's offline loader.
Hard link to the already verified selected file; no copied weights/downloads.
"""
from pathlib import Path
import json,hashlib,os,sys

def prepare(models):
    m=json.loads((models/'manifest.json').read_text());rev=m['model_revision'];assert rev=='5bb1f6ee58e50c3b8d408bc82a6d3740c2db6e18'
    src=models/'Cangjie5_TC.json';entry=next(x for x in m['files'] if x['name']==src.name);assert hashlib.sha256(src.read_bytes()).hexdigest()==entry['sha256']
    base=models/'models--ResembleAI--chatterbox';snap=base/'snapshots'/rev;refs=base/'refs'
    for d in [base,base/'snapshots',snap,refs]:
        d.mkdir(mode=0o700,exist_ok=True);os.chown(d,999,999)
    dst=snap/src.name
    if not dst.exists():os.link(src,dst)
    assert os.stat(dst).st_ino==os.stat(src).st_ino
    p=refs/'main'
    if p.exists():assert p.read_text()==rev
    else:p.write_text(rev);p.chmod(0o600);os.chown(p,999,999)
    return {'result':'PASS','reference':rev,'hardlink_only':True,'downloaded_bytes':0}
if __name__=='__main__':print(json.dumps(prepare(Path(sys.argv[1]))))
