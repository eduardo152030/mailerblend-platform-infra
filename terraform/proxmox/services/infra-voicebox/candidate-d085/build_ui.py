"""Reproduce candidate UI from exact fork archive; never deploy or call TTS."""
import argparse,hashlib,json,tarfile,shutil,subprocess
from pathlib import Path
from effects_ui_patch import apply

def build(archive,bun,out):
    here=Path(__file__).resolve().parent;lock=json.loads((here/'ui-source.lock.json').read_text())
    assert not out.exists() and hashlib.sha256(archive.read_bytes()).hexdigest()==lock['archive_sha256']
    assert hashlib.sha256(bun.read_bytes()).hexdigest()==lock['bun_sha256'] and subprocess.check_output([str(bun),'--version'],text=True).strip()==lock['bun_version']
    out.mkdir(mode=0o700,parents=True)
    with tarfile.open(archive) as t:
        for m in t.getmembers():
            m.name='/'.join(m.name.split('/')[1:])
            if m.name:t.extract(m,out,filter='data')
    for base in [here.parent/'candidate-d083/ui',here/'ui']:
        for p in base.rglob('*'):
            if p.is_file():dest=out/'app/src'/p.relative_to(base);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
    apply(out/'app/src')
    subprocess.run([str(bun),'install','--frozen-lockfile','--ignore-scripts'],cwd=out,check=True)
    subprocess.run([str(bun),'run','build:web'],cwd=out,check=True)
    return {'result':'PASS','source':lock,'bun_lock_sha256':hashlib.sha256((out/'bun.lock').read_bytes()).hexdigest()}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--archive',type=Path,required=True);p.add_argument('--bun',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();print(json.dumps(build(a.archive,a.bun,a.out)))
