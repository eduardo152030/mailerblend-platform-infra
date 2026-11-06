#!/usr/bin/env python3
"""Archive verified Journal exporter configuration after a successful per-CT rollout."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import tarfile

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('rollout',ROOT/'scripts/rollout-journal-exporters.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)


def archive(run,ct):
    assert ct in [625,626] and re.fullmatch(r'journal-[0-9TZ+-]+',run)
    os.umask(0o077)
    here=Path.home()/'.local/share/mailerblend-recovery/phase4'/run/str(ct)
    state=json.loads((here/'state.json').read_text());assert state['ct']==ct and state['result']=='PASS'
    if state.get('after_configuration'):
        assert m.sha(here/'exporters-after-config.tar.gz')==state['after_configuration']['sha256']
        return state['after_configuration']
    code='import pathlib,subprocess,hashlib,json\np=pathlib.Path('+repr(state['pve_directory'])+')/"exporters-after-config.tar.gz"\nassert not p.exists()\nwith p.open("xb") as f:\n r=subprocess.run('+repr(['pct','exec',str(ct),'--','tar','--exclude=original-*.tar','-C',state['ct_directory'],'-czf','-','.'])+',stdout=f,stderr=subprocess.PIPE,timeout=180)\nassert r.returncode==0\np.chmod(0o600)\nprint(json.dumps({"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"bytes":p.stat().st_size}))\n'
    info=json.loads(m.remote(code,here/'execution.private.log'))
    target=here/'exporters-after-config.tar.gz'
    with target.open('xb') as f:r=subprocess.run(m.SSH+['cat',state['pve_directory']+'/exporters-after-config.tar.gz'],stdout=f,stderr=subprocess.PIPE,timeout=120)
    assert r.returncode==0 and m.sha(target)==info['sha256']
    with tarfile.open(target) as a:
        for name,digest in state['manifest']['files'].items():
            import hashlib
            assert hashlib.sha256(a.extractfile('./'+name).read()).hexdigest()==digest
        applied=json.load(a.extractfile('./applied.json'))
        assert all(applied[n]['id']==d['Id'] for n,d in state['exporters'].items())
    info['offhost_verified']=True;state['after_configuration']=info;m.write(here/'state.json',state)
    return info


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run',required=True);p.add_argument('--ct',type=int,choices=[625,626],required=True);a=p.parse_args()
    print(json.dumps(archive(a.run,a.ct)))
