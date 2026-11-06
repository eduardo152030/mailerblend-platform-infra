#!/usr/bin/env python3
"""Authorized sequential Journal rollout. No other CT, applications or discovery changes."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tarfile
from datetime import datetime
from zoneinfo import ZoneInfo

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('journal_prepare',ROOT/'scripts/prepare-journal-exporters.py')
prepare=importlib.util.module_from_spec(spec);spec.loader.exec_module(prepare)
SSH=['ssh','-o','BatchMode=yes','-o','ConnectTimeout=10','-o','ServerAliveInterval=30','pve']


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()


def write(path,data):
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_TRUNC,0o600)
    with os.fdopen(fd,'w') as f:json.dump(data,f,indent=2);f.write('\n')


def remote(code,log,timeout=240):
    r=subprocess.run(SSH+['python3','-'],input=code,text=True,capture_output=True,timeout=timeout)
    with log.open('a') as f:f.write(r.stdout+r.stderr)
    assert r.returncode==0,'Remote step failed; private log retained: '+log.name
    return r.stdout


def ct_code(ct,code):
    assert ct in [625,626]
    return 'import subprocess\np=subprocess.run('+repr(['pct','exec',str(ct),'--','python3','-'])+',input='+repr(code)+',text=True,capture_output=True)\nprint(p.stdout,end="");assert p.returncode==0,"CT step failed (private details withheld)"\n'


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--ct',type=int,choices=[626,625],required=True)
    p.add_argument('--run',required=True)
    p.add_argument('--execute',action='store_true')
    a=p.parse_args()
    if not a.execute:p.error('--execute required within an approved deployment')
    import re
    assert re.fullmatch(r'journal-[0-9TZ+-]+',a.run),'Invalid run identifier'
    os.umask(0o077)
    local=Path.home()/'.local/share/mailerblend-recovery/phase4'/a.run
    local.mkdir(parents=True,exist_ok=True,mode=0o700);local.chmod(0o700)
    if a.ct==625:
        previous=json.loads((local/'626/state.json').read_text())
        assert previous['result']=='PASS','CT626 must pass before CT625'
    here=local/str(a.ct);here.mkdir(mode=0o700,exist_ok=True)
    statepath=here/'state.json'
    assert not statepath.exists(),'Existing run: inspect checkpoints; do not repeat blindly'
    bundle=here/'bundle';manifest=prepare.render(a.ct,bundle)
    ctdir='/opt/exporter-phase4-pilot/'+a.run+'-'+str(a.ct)
    pvedir='/mnt/storage/mailerblend-recovery/phase4/'+a.run+'/'+str(a.ct)
    log=here/'execution.private.log';log.touch(mode=0o600)
    state={'ct':a.ct,'run':a.run,'ct_directory':ctdir,'pve_directory':pvedir,'started_at':datetime.now(ZoneInfo('Europe/Madrid')).isoformat(),'result':'IN_PROGRESS','manifest':manifest,'steps':[]}
    def mark(name):
        state['steps'].append(name);write(statepath,state);print('CT',a.ct,name,flush=True)
    mark('preflight_started')
    preflight='''import pathlib,subprocess,json,shutil,re
ct=CT
conf=dict(l.split(': ',1) for l in subprocess.check_output(['pct','config',str(ct)],text=True).splitlines() if ': ' in l)
assert int(conf['cores'])==2 and int(conf['memory'])==2048
root=pathlib.Path('/sys/fs/cgroup/lxc')/str(ct)
assert int((root/'memory.max').read_text())==2048*1024*1024
assert (root/'cpu.max').read_text().split()[0]=='max'
mem=int(re.search(r'MemAvailable:\\s+(\\d+)',pathlib.Path('/proc/meminfo').read_text()).group(1));assert mem>=2*1024*1024
assert shutil.disk_usage('/mnt/storage').free>=2*1024**3
print(json.dumps({'proxmox':{k:conf[k] for k in ['hostname','cores','memory','swap']},'pve_available_kib':mem,'memory_events':(root/'memory.events').read_text(),'memory_pressure':(root/'memory.pressure').read_text(),'cpu_pressure':(root/'cpu.pressure').read_text()}))
'''.replace('CT',str(a.ct))
    state['preflight']=json.loads(remote(preflight,log));assert all(float(x)<=5 for x in re.findall(r'avg(?:10|60)=(\S+)',state['preflight']['memory_pressure']))
    assert __import__('shutil').disk_usage(local).free>=2*1024**3
    mark('preflight_passed')
    payload={n:(bundle/n).read_text() for n in manifest['files']}
    stage='import pathlib,os,hashlib\np=pathlib.Path('+repr(ctdir)+')\nassert not p.exists(),"Run directory exists"\np.mkdir(parents=True,mode=0o700)\n'
    for n,body in payload.items():stage+='f=p/'+repr(n)+'\nf.write_text('+repr(body)+')\nf.chmod('+('0o644' if n=='node-cgroup.sh' else '0o600')+')\nassert hashlib.sha256(f.read_bytes()).hexdigest()=='+repr(manifest['files'][n])+'\n'
    remote(ct_code(a.ct,stage),log)
    stagepve='import pathlib\np=pathlib.Path('+repr(pvedir)+')\np.mkdir(parents=True,mode=0o700,exist_ok=False)\np.chmod(0o700)\n'
    for n in ['observe.py','sample.py']:stagepve+='(p/'+repr(n)+').write_text('+repr(payload[n])+')\n(p/'+repr(n)+').chmod(0o600)\n'
    remote(stagepve,log);mark('staging_hashes_verified')
    def helper(action):
        cmd=['python3',ctdir+'/pilot.py',action,'--execute','--directory',ctdir,'--allow-containerd-socket','--use-lxc-cgroup-cpu']
        code='import subprocess\nr=subprocess.run('+repr(cmd)+',capture_output=True,text=True,timeout=360)\nprint(r.stdout,end="");assert r.returncode==0,"Helper failed; stop and inspect private CT state"\n'
        remote(ct_code(a.ct,code),log,400)
    helper('snapshot');mark('snapshot_image_archive_and_load_verified')
    backup='import subprocess,pathlib,hashlib,json\np=pathlib.Path('+repr(pvedir)+')/"exporters-before.tar"\nwith p.open("xb") as f:\n r=subprocess.run('+repr(['pct','exec',str(a.ct),'--','tar','-C',ctdir,'-cf','-','.'])+',stdout=f,stderr=subprocess.PIPE,timeout=180)\nassert r.returncode==0\np.chmod(0o600)\nh=hashlib.sha256(p.read_bytes()).hexdigest()\nprint(json.dumps({"sha256":h,"bytes":p.stat().st_size}))\n'
    state['backup']=json.loads(remote(backup,log))
    target=here/'exporters-before.tar'
    with target.open('xb') as f:
        r=subprocess.run(SSH+['cat',pvedir+'/exporters-before.tar'],stdout=f,stderr=subprocess.PIPE,timeout=180)
    assert r.returncode==0 and sha(target)==state['backup']['sha256'],'Offhost backup checksum failure'
    with tarfile.open(target) as archive:
        base=json.load(archive.extractfile('./baseline.json'))
        for name,details in base['archives'].items():
            h=hashlib.sha256();stream=archive.extractfile('./'+name)
            for chunk in iter(lambda:stream.read(1024*1024),b''):h.update(chunk)
            assert h.hexdigest()==details['sha256'],'Nested image checksum failed'
    state['original_exporter_ids']={n:c['Id'] if c else None for n,c in base['exporters'].items()}
    proof={'offhost_verified':True,'archives':base['archives'],'bundle_sha256':state['backup']['sha256']}
    remote(ct_code(a.ct,'import pathlib,json\np=pathlib.Path('+repr(ctdir)+')/"external-backup-verified.json"\np.write_text('+repr(json.dumps(proof))+')\np.chmod(0o600)\n'),log)
    mark('backup_pve_offhost_nested_hashes_verified')
    # Only explicit immutable image downloads; no app image operations.
    pull='import subprocess,json\nimages='+repr(['prom/node-exporter@sha256:3ac34ce007accad95afed72149e0d2b927b7e42fd1c866149b945b84737c62c3','ghcr.io/google/cadvisor@sha256:b8e7d1093144fd088f425ff003d75a4aa405de075db78dae3bc563730b1bd07a'])+'\nfor image in images:\n r=subprocess.run(["docker","image","pull",image],capture_output=True,timeout=240)\n assert r.returncode==0,"Pinned pull failed"\n d=json.loads(subprocess.check_output(["docker","image","inspect",image]))[0]\n assert d["Architecture"]=="amd64" and image.split("@",1)[1] in " ".join(d["RepoDigests"])\n print(json.dumps({"reference":image,"id":d["Id"],"digests":d["RepoDigests"]}))\n'
    remote(ct_code(a.ct,pull),log,550);mark('exact_images_verified')
    helper('apply');helper('check');mark('initial_apply_and_readiness_passed')
    identity='import subprocess,json\nprint(json.dumps({n:{k:c[k] for k in ["Id","Image","RestartCount"]}|{"started_at":c["State"]["StartedAt"]} for n in ["node_exporter","cadvisor"] for c in json.loads(subprocess.check_output(["docker","inspect",n]))}))\n'
    first=json.loads(remote(ct_code(a.ct,identity),log))
    helper('rollback')
    verify='''import subprocess,json,urllib.request,time
baseline=json.load(open(DIR+'/baseline.json'))
for name,original in baseline['exporters'].items():
 r=subprocess.run(['docker','inspect',name],capture_output=True,text=True)
 if original:
  c=json.loads(r.stdout)[0];assert c['Id']==original['Id'] and c['State']['Running'] and c['Image']==original['Image']
 else:assert r.returncode!=0
end=time.monotonic()+90
while True:
 try:
  with urllib.request.urlopen(URL,timeout=5) as r:assert r.status==200
  break
 except Exception:
  assert time.monotonic()<end,'Original metrics unavailable after rollback'
  time.sleep(2)
print('Original identities, running state and metrics verified')
'''.replace('DIR',repr(ctdir)).replace('URL',repr('http://'+manifest['ip']+':8085/metrics'))
    remote(ct_code(a.ct,verify),log);mark('rollback_original_metrics_and_apps_passed')
    helper('apply');helper('check')
    resumed=json.loads(remote(ct_code(a.ct,identity),log));assert all(first[n]['Id']==resumed[n]['Id'] for n in first)
    helper('apply');helper('check')
    second=json.loads(remote(ct_code(a.ct,identity),log));assert second==resumed,'Repeated apply changed exporter identity/start/restart'
    state['exporters']=second;mark('resume_same_ids_and_second_apply_idempotent')
    mark('observation_600_seconds_started')
    observe='import subprocess\nr=subprocess.run('+repr(['python3',pvedir+'/observe.py','--probe',pvedir+'/sample.py','--output',pvedir+'/observations.jsonl','--seconds','600','--interval','30'])+',capture_output=True,text=True,timeout=730)\nprint(r.stdout,end="");assert r.returncode==0,"Observation gate failed (stop batch)"\n'
    remote(observe,log,760)
    obs=here/'observations.jsonl'
    with obs.open('xb') as f:r=subprocess.run(SSH+['cat',pvedir+'/observations.jsonl'],stdout=f,stderr=subprocess.PIPE,timeout=60)
    assert r.returncode==0
    samples=[json.loads(l) for l in obs.read_text().splitlines()];assert len(samples)>=21 and samples[-1]['elapsed_seconds']>=600
    before_events=dict(l.split() for l in state['preflight']['memory_events'].splitlines())
    for sample in samples:
        events=dict(l.split() for l in sample['resources']['memory.events'].splitlines())
        assert all(events.get(k,'0')==before_events.get(k,'0') for k in ['oom','oom_kill','oom_group_kill']), 'OOM since preflight'
    helper('check');state['observation']={'samples':len(samples),'seconds':samples[-1]['elapsed_seconds'],'sha256':sha(obs)}
    mark('observation_and_final_check_passed')
    state['result']='PASS';state['completed_at']=datetime.now(ZoneInfo('Europe/Madrid')).isoformat();write(statepath,state)
    print('CT',a.ct,'PASS; evidence:',here,flush=True)


if __name__=='__main__':main()
