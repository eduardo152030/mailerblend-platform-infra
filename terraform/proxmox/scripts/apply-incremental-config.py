#!/usr/bin/env python3
"""CT610-only, content-addressed integration. Never Compose-up, restart or touch volumes."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess
import tarfile
import time
import urllib.request

BASE=Path('/opt/infra-prom')
RULES=['rules/infra-hosts.yml','rules/lxc-cpu.yml','rules/lxc-cpu-targets.yml','rules/lxc-cpu-inventory.yml']
TARGETS=['targets/node-exporter.json','targets/cadvisor.json']
TEST='rules/incremental-delivery-test.yml'


def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,d):
    fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_TRUNC,0o600)
    with os.fdopen(fd,'w') as f:json.dump(d,f,indent=2);f.write('\n')
def run(args,timeout=120):
    r=subprocess.run(args,capture_output=True,timeout=timeout)
    assert r.returncode==0,'Command failed: '+args[0]+' '+args[1]+' (details withheld)'
    return r.stdout

def ids():
    return {n:json.loads(run(['docker','inspect',n]))[0] for n in ['prometheus','alertmanager']}
def identity():
    return {n:{'id':c['Id'],'started_at':c['State']['StartedAt'],'running':c['State']['Running']} for n,c in ids().items()}
def get(path):
    with urllib.request.urlopen('http://127.0.0.1:9090'+path,timeout=8) as r:return r.read().decode()
def reload():
    before=identity();assert all(c['running'] for c in before.values())
    def metric(name):
        return float(next(l.split()[1] for l in get('/metrics').splitlines() if l.startswith(name+' ')))
    old=metric('prometheus_config_last_reload_success_timestamp_seconds')
    run(['docker','exec','prometheus','promtool','check','config','/etc/prometheus/prometheus.yml'])
    run(['docker','kill','--signal=SIGHUP','prometheus'])
    end=time.monotonic()+120
    while time.monotonic()<end:
        try:
            assert metric('prometheus_config_last_reload_successful')==1
            assert metric('prometheus_config_last_reload_success_timestamp_seconds')>old
            get('/-/ready')
            rules=json.loads(get('/api/v1/rules'))['data']['groups']
            assert all(r['health']=='ok' for g in rules for r in g['rules'])
            assert identity()==before,'Container identity/start changed'
            return
        except (AssertionError,OSError,ValueError,StopIteration):time.sleep(2)
    raise RuntimeError('Reload/readiness/rule-health timeout; stop and inspect without restarting services')

def state(directory):return json.loads((directory/'state.json').read_text())
def checked(directory):
    manifest=json.loads((directory/'manifest.json').read_text());s=state(directory)
    proof=json.loads((directory/'backup-verified.json').read_text())
    assert proof['offhost_verified'] and proof['sha256']==s['backup_sha256'],'Verified external backup required'
    expected=dict(manifest['baseline_sha256'])
    for p in s['applied']:expected[p]=manifest['candidate_sha256'][p]
    if s.get('test_sha256'):expected[TEST]=s['test_sha256']
    actual={str(p.relative_to(BASE/'config')):digest(p) for sub in ['rules','targets'] for p in (BASE/'config'/sub).iterdir() if p.is_file() and p.suffix in ['.yml','.yaml','.json']}
    actual['prometheus.yml']=digest(BASE/'config/prometheus.yml')
    assert actual==expected,'Unexpected live configuration drift; do not overwrite'
    assert identity()==s['identity'],'Prometheus/AM identities changed'
    return manifest,s

def replace_file(path,body):
    if path.exists() and path.read_bytes()==body:return False
    src=path if path.exists() else BASE/'config/rules/infra-hosts.yml'
    st=src.stat();temp=path.with_name(path.name+'.incremental-tmp')
    assert not temp.exists(),'Unreviewed temporary file exists'
    fd=os.open(temp,os.O_WRONLY|os.O_CREAT|os.O_EXCL,st.st_mode&0o777)
    with os.fdopen(fd,'wb') as f:f.write(body);f.flush();os.fsync(f.fileno())
    os.chown(temp,st.st_uid,st.st_gid);os.chmod(temp,st.st_mode&0o777)
    os.replace(temp,path);return True

def install(directory,paths):
    manifest,s=checked(directory);changes=[]
    for name in paths:
        src=directory/'candidate'/name;assert digest(src)==manifest['candidate_sha256'][name]
        if replace_file(BASE/'config'/name,src.read_bytes()):changes.append(name)
        if name not in s['applied']:s['applied'].append(name)
        save(directory/'state.json',s)
    if changes and any(p.startswith('rules/') for p in changes):reload()
    print(json.dumps({'changed':changes,'reloaded':bool(changes and any(p.startswith('rules/') for p in changes))}))

def snapshot(directory):
    assert not (directory/'state.json').exists()
    manifest=json.loads((directory/'manifest.json').read_text())
    actual={str(p.relative_to(BASE/'config')):digest(p) for sub in ['rules','targets'] for p in (BASE/'config'/sub).iterdir() if p.is_file() and p.suffix in ['.yml','.yaml','.json']}
    actual['prometheus.yml']=digest(BASE/'config/prometheus.yml');assert actual==manifest['baseline_sha256']
    before=directory/'before';before.mkdir(mode=0o700)
    for name in RULES+TARGETS:
        p=BASE/'config'/name
        if p.exists():
            dst=before/name;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(p.read_bytes())
    backup=directory/'integration-before.tar'
    compose=next((n for n in ['docker-compose.yml','compose.yml','compose'] if (BASE/n).exists()),None)
    assert compose, 'Actual Compose mechanism required before snapshot'
    paths=['config',compose,'.runtime/alertmanager.yml','.runtime/telegram_bot_token']
    assert all((BASE/n).exists() for n in paths), 'Required backup mechanism missing'
    paths += [n for n in ['.env','perm.env'] if (BASE/n).is_file()]
    with tarfile.open(backup,'x') as a:
        for n in paths:a.add(BASE/n,arcname=n,recursive=True)
    backup.chmod(0o600)
    # Restore archive to staging and compare regular files, never live files.
    restored=directory/'restore-check';restored.mkdir(mode=0o700)
    with tarfile.open(backup) as a:
        for member in a:
            assert not Path(member.name).is_absolute() and '..' not in Path(member.name).parts
            assert not member.issym() and not member.islnk(), 'Review linked backup entries before proceeding'
            if member.isfile():
                stream=a.extractfile(member);body=stream.read();assert hashlib.sha256(body).hexdigest()==digest(BASE/member.name)
                target=restored/member.name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(body);target.chmod(0o600)
    s={'identity':identity(),'applied':[],'backup_sha256':digest(backup),'archive_read_and_restore_verified':True}
    save(directory/'state.json',s);print(json.dumps({'sha256':s['backup_sha256'],'bytes':backup.stat().st_size,'identities':s['identity']}))

def validate(directory):
    image=ids()['prometheus']['Image']
    # Same installed image, no network or host writes. No persistent volume.
    run(['docker','run','--rm','--pull=never','--network=none','--read-only','--memory=128m','--cpus=.5','--tmpfs','/prometheus','--tmpfs','/tmp','--mount','type=bind,src='+str(directory/'candidate')+',dst=/etc/prometheus,readonly','--entrypoint','/bin/promtool',image,'check','config','/etc/prometheus/prometheus.yml'])
    for job,count in [('node',17),('cadvisor',17),('blackbox',11)]:
        rows=json.loads(run(['docker','run','--rm','--pull=never','--network=none','--read-only','--memory=128m','--cpus=.5','--tmpfs','/prometheus','--tmpfs','/tmp','--mount','type=bind,src='+str(directory/'candidate')+',dst=/etc/prometheus,readonly','--entrypoint','/bin/promtool',image,'check','service-discovery','--timeout=1s','/etc/prometheus/prometheus.yml',job]))
        assert len(rows)==count,'Unexpected service discovery count: '+job
        keys=[(r['labels']['job'],r['labels']['instance'])+((r['labels'].get('module'),r['labels'].get('probe_type')) if job=='blackbox' else ()) for r in rows]
        assert len(set(keys))==count,'Duplicate service discovery identity: '+job
    print('Pinned installed-image configuration/rules and real service-discovery17/17/11 validation PASS')

def rollback(directory):
    manifest,s=checked(directory);assert not s.get('test_sha256'),'Resolve/remove controlled test before rollback'
    # P0 checkpoint restore; R1 rollback must use the checkpoint including P0.
    for name in TARGETS+RULES:
        original=directory/'before'/name;dst=BASE/'config'/name
        if original.exists():replace_file(dst,original.read_bytes())
        elif dst.exists():
            assert name in s['applied'] and digest(dst)==manifest['candidate_sha256'][name]
            dst.unlink() # Only a newly added integration rule, never data/volumes.
    s['applied']=[];save(directory/'state.json',s);reload();checked(directory)
    print('Checkpoint restored and reloaded; no container/data/volume changed')

def test_rule(directory,remove=False):
    _,s=checked(directory);dst=BASE/'config'/TEST
    if remove:
        assert s.get('test_sha256') and digest(dst)==s['test_sha256'];dst.unlink();s.pop('test_sha256')
    else:
        src=directory/'verification.yml';body=src.read_bytes()
        if dst.exists() and digest(dst)==hashlib.sha256(body).hexdigest():print('Test rule unchanged; no reload');return
        replace_file(dst,body);s['test_sha256']=digest(dst)
    save(directory/'state.json',s);reload();print('Controlled test rule removed' if remove else 'Controlled test rule loaded')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['snapshot','validate','rules','targets','rollback','test','remove-test']);p.add_argument('--directory',type=Path,required=True);p.add_argument('--execute',action='store_true');a=p.parse_args()
    assert a.execute and socket.gethostname()=='infra-prom'
    d=a.directory.resolve();assert d.is_relative_to(BASE/'.runtime') and d.name.startswith('integration-')
    os.umask(0o077)
    if a.action=='snapshot':snapshot(d)
    elif a.action=='validate':validate(d)
    elif a.action=='rules':install(d,RULES)
    elif a.action=='targets':install(d,TARGETS)
    elif a.action=='rollback':rollback(d)
    else:test_rule(d,a.action=='remove-test')
