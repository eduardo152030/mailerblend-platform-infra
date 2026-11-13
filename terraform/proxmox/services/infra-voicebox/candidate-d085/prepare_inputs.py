"""Reproduce isolated inputs from verified official archive and local pinned uv.
No installation, downloads, inference or deployment. Run in private output path.
"""
import argparse,hashlib,json,tarfile,shutil,subprocess
from pathlib import Path
UV_SHA='b59310db262709ee92baf7954ef30820f1442ffa48b263f7001a236fe9004047'
def prepare(archive,uv,out):
    here=Path(__file__).resolve().parent;lock=json.loads((here/'sources.lock.json').read_text())
    assert not out.exists() and hashlib.sha256(archive.read_bytes()).hexdigest()==lock['chatterbox']['archive_sha256']
    assert hashlib.sha256(uv.read_bytes()).hexdigest()==UV_SHA
    out.mkdir(mode=0o700,parents=True);source=out/'chatterbox';source.mkdir()
    with tarfile.open(archive) as t:
        for m in t.getmembers():
            m.name='/'.join(m.name.split('/')[1:])
            if m.name:t.extract(m,source,filter='data')
    p=source/'pyproject.toml';s=p.read_text();needle='https://github.com/resemble-ai/Perth.git@master';assert s.count(needle)==1
    p.write_text(s.replace(needle,'https://github.com/resemble-ai/Perth.git@'+lock['perth']['commit']))
    for n in ['requirements.lock','build-constraints.txt','imports.py']:shutil.copy2(here/n,out/n)
    shutil.copy2(uv,out/'uv')
    return {'sources':lock,'uv_sha256':UV_SHA,'packaging_only_change':'Perth VCS ref replaced by exact commit; dependencies installed through hashed lock'}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source-archive',type=Path,required=True);p.add_argument('--uv',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();print(json.dumps(prepare(a.source_archive,a.uv,a.out)))
