#!/usr/bin/env python3
"""Preserve originals; archive only selected post-deployment configuration, never live data."""
import argparse
import hashlib
import importlib.util
import inspect
import json
import os
from pathlib import Path
import re
import subprocess
import tarfile

ROOT=Path(__file__).resolve().parents[1]
def load(n):
 s=importlib.util.spec_from_file_location(n,ROOT/'scripts'/n);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def select_configuration_paths(base):
    candidates=[n for n in ['docker-compose.yml','compose.yml','compose.yaml','docker-compose.yaml'] if (base/n).is_file()]
    if not candidates and (base/'compose').is_dir():candidates=['compose']
    assert len(candidates)==1, 'Missing or ambiguous Compose mechanism; stop for review'
    names=['config',candidates[0],'.runtime/alertmanager.yml','.runtime/telegram_bot_token']
    assert all((base/n).exists() for n in names), 'Required configuration/secret backup path missing'
    return names+[n for n in ['.env','perm.env'] if (base/n).is_file()]

def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def planned_archives(state,mon,monitoring_only):
    tasks=[(610,'/opt/infra-prom',mon['pve_directory'],'integration-after-v2.tar.gz')]
    if not monitoring_only:tasks.insert(0,(613,state['ct_directory'],state['pve_directory'],'exporters-after-config.tar.gz'))
    return tasks

def local_copy(target,expected,fetch):
    if target.exists():
        assert digest(target)==expected,'Existing local archive differs; never overwrite it'
        return
    fd=os.open(target,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'wb') as out:fetch(out)
    assert digest(target)==expected,'Offhost checksum differs'

def archive(run,monitoring_only=False):
    assert re.fullmatch(r'integration-[0-9TZ]+',run);os.umask(0o077)
    here=Path.home()/'.local/share/mailerblend-recovery/phase4'/run/'613'
    state=json.loads((here/'state.json').read_text());mon=json.loads((here/'monitoring/state.json').read_text())
    assert state['observation']['seconds']>=600 and state['observation']['samples']>=21
    assert mon['recipient_confirmation']['confirmed'] and mon['test_removed']
    p=load('run-incremental-p0.py');p.HERE=here
    for ct,src,folder,destination in planned_archives(state,mon,monitoring_only):
        if ct==610:
            selector='from pathlib import Path\nimport json\n'+inspect.getsource(select_configuration_paths)+'\nprint(json.dumps(select_configuration_paths(Path("/opt/infra-prom"))))'
            selection='r=subprocess.run(["pct","exec","610","--","python3","-c",'+repr(selector)+'],text=True,capture_output=True);assert r.returncode==0,"Path selection failed"\nargs=["pct","exec","610","--","tar","-C","/opt/infra-prom","-czf","-"]+json.loads(r.stdout)'
        else:
            selection='args='+repr(['pct','exec','613','--','tar','--exclude=original-*.tar','-C',src,'-czf','-','.'])
        code='''import pathlib,subprocess,hashlib,json,os
f=pathlib.Path(PATH)
SELECTION
if not f.exists():
 fd=os.open(f,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
 with os.fdopen(fd,'wb') as out:r=subprocess.run(args,stdout=out,stderr=subprocess.PIPE,timeout=120)
 assert r.returncode==0, 'Archive failed; preserve partial and stop'
print(json.dumps({'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bytes':f.stat().st_size}))
'''.replace('PATH',repr(folder+'/'+destination)).replace('SELECTION',selection)
        info=json.loads(p.remote(code));target=here/destination
        def fetch(out):
            r=subprocess.run(p.SSH+['cat',folder+'/'+destination],stdout=out,stderr=subprocess.PIPE,timeout=120)
            assert r.returncode==0,'External copy failed'
        local_copy(target,info['sha256'],fetch)
        with tarfile.open(target) as a:
            if ct==613:
                for name,h in state['manifest']['files'].items():assert hashlib.sha256(a.extractfile('./'+name).read()).hexdigest()==h
            else:
                assert 'docker-compose.yml' in a.getnames(),'Actual root Compose file absent'
                for name,h in mon['manifest']['candidate_sha256'].items():assert hashlib.sha256(a.extractfile('config/'+name).read()).hexdigest()==h
            # Read every regular member fully so a truncated archive cannot pass.
            for member in a.getmembers():
                if member.isfile():assert len(a.extractfile(member).read())==member.size
        info.update(offhost_verified=True,archive_readable_and_complete=True,filename=destination)
        state['exporter_after_archive' if ct==613 else 'monitoring_after_archive']=info
    # Recover metadata of the previously verified exporter archive read-only, without recreating it.
    if monitoring_only and not state.get('exporter_after_archive'):
        target=here/'exporters-after-config.tar.gz'
        code='import pathlib,hashlib\nf=pathlib.Path('+repr(state['pve_directory']+'/exporters-after-config.tar.gz')+');print(hashlib.sha256(f.read_bytes()).hexdigest())'
        assert digest(target)==p.remote(code).strip()
        with tarfile.open(target) as a:
            for name,h in state['manifest']['files'].items():assert hashlib.sha256(a.extractfile('./'+name).read()).hexdigest()==h
        state['exporter_after_archive']={'sha256':digest(target),'bytes':target.stat().st_size,'offhost_verified':True,'existing_archive_preserved':True}
    (here/'state.json').write_text(json.dumps(state,indent=2)+'\n')
    print('PASS: selected archive readable/complete, source and offhost hashes equal; existing archives preserved')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run',required=True);p.add_argument('--monitoring-only',action='store_true');a=p.parse_args();archive(a.run,a.monitoring_only)
