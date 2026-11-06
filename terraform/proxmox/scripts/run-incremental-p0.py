#!/usr/bin/env python3
"""Checkpointed P0 operator; CT610 only. R1 has a separate, conditional gate."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import tarfile
import time
import urllib.parse
import urllib.request
import yaml
from datetime import datetime,timezone

ROOT=Path(__file__).resolve().parents[1]
SSH=['ssh','-o','BatchMode=yes','-o','ConnectTimeout=10','-o','ServerAliveInterval=30','pve']
SERVICES={624:'infra-journal-web',626:'infra-journal-api',625:'infra-journal-db'}

def load(name):
 spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/name);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n');p.chmod(0o600)
def remote(code,timeout=240):
 r=subprocess.run(SSH+['python3','-'],input=code,text=True,capture_output=True,timeout=timeout)
 with (HERE/'private.log').open('a') as f:f.write(r.stdout+r.stderr)
 assert r.returncode==0,'Remote step failed; details retained in private.log'
 return r.stdout

def ct(code):
 return 'import subprocess\nr=subprocess.run(["pct","exec","610","--","python3","-"],input='+repr(code)+',text=True,capture_output=True,timeout=240)\nprint(r.stdout,end="");assert r.returncode==0,"CT610 step failed; stop"\n'

def helper(action):
 return remote(ct('import subprocess\nr=subprocess.run('+repr(['python3',CTDIR+'/apply.py',action,'--directory',CTDIR,'--execute'])+',capture_output=True,text=True,timeout=220)\nprint(r.stdout,end="");assert r.returncode==0,"Integration helper failed"\n'))

def get(base,path):
 with urllib.request.urlopen(base+path,timeout=15) as r:return json.load(r)
def query(expr):return get('http://192.168.1.110:9090','/api/v1/query?'+urllib.parse.urlencode({'query':expr}))['data']['result']
def telemetry():
 return {n:query(n+'{integration="telegram"}') for n in ['alertmanager_notifications_total','alertmanager_notifications_failed_total']}
def checks():
 c=load('check-incremental-chain.py');out={}
 for ident,service in SERVICES.items():
  data=c.collect('http://192.168.1.110:9090',ident,service);assert not c.assess(data),str(ident)+': '+','.join(c.assess(data))
  def val(expr):
   rows=query(expr);assert len(rows)==1;return float(rows[0]['value'][1])
  assert val('lxc_cpu_capacity_cores{job="node_exporter",ct_id="'+str(ident)+'"}')==(1 if ident==624 else 2)
  assert val('node_memory_MemTotal_bytes{job="node_exporter",service="'+service+'"}')==(512 if ident==624 else 2048)*1024**2
  for metric in ['container_memory_usage_bytes','container_cpu_usage_seconds_total']:
   rows=query(metric+'{job="cadvisor",service="'+service+'",name!=""}')
   for item in STATE['expected_containers'][str(ident)]:
    found=[v for v in rows if item['id'] in v['metric'].get('id','') and v['metric'].get('name','').lstrip('/')==item['name']]
    assert len(found)==1,'Missing/duplicate Docker identity'
  out[str(ident)]={'cpu_percent':float(data['cpu_percent'][0]['value'][1]),'contract_valid':True,'docker_identities_verified':len(STATE['expected_containers'][str(ident)])}
 targets=get('http://192.168.1.110:9090','/api/v1/targets')['data']['activeTargets'];counts={}
 for t in targets:counts[t['labels']['job']]=counts.get(t['labels']['job'],0)+1
 assert counts['node_exporter']==17 and counts['cadvisor']==17 and counts['blackbox']==11 and 'grafana' not in counts
 return out

def wait_checks():
 end=time.monotonic()+180
 while True:
  try:return checks()
  except (AssertionError,OSError,ValueError):
   assert time.monotonic()<end,'P0 API checks timeout; do not start R1'
   time.sleep(3)

def resources():
 code='import pathlib,json\nr={}\nfor ct in [610,624,626,625]:\n p=pathlib.Path("/sys/fs/cgroup/lxc")/str(ct)\n r[str(ct)]={n:(p/n).read_text() for n in ["memory.events","memory.pressure","memory.current","cpu.stat"]}\nprint(json.dumps(r))'
 return json.loads(remote(code,30))

def prepare():
 assert not (HERE/'state.json').exists(),'Run already exists'
 subprocess.run(['python3',str(ROOT/'scripts/snapshot-incremental-monitoring.py'),'--output',str(HERE/'baseline.json')],check=True)
 prep=load('prepare-incremental-monitoring.py');files,manifest=prep.build(json.loads((HERE/'baseline.json').read_text()),yaml.safe_load((ROOT/'services/common/exporter-migration.yml').read_text()),prep.generator.load_services())
 save(HERE/'manifest.json',manifest)
 code='import pathlib,os,hashlib\nd=pathlib.Path('+repr(CTDIR)+')\nassert not d.exists()\nd.mkdir(parents=True,mode=0o700)\n'
 payload={'apply.py':(ROOT/'scripts/apply-incremental-config.py').read_text(),'manifest.json':json.dumps(manifest),**{'candidate/'+k:v for k,v in files.items()}}
 for name,body in payload.items():
  code+='p=d/'+repr(name)+'\np.parent.mkdir(parents=True,exist_ok=True)\np.write_text('+repr(body)+')\np.chmod('+('0o644' if name.startswith('candidate/') else '0o600')+')\n'
 code+='\nfor p in (d/"candidate").rglob("*"):\n if p.is_dir():p.chmod(0o755)\n(d/"candidate").chmod(0o755)\n'
 remote(ct(code));snapshot=json.loads(helper('snapshot'));STATE.update(snapshot);STATE['resources_before']=resources()
 baseline_containers={}
 code='import subprocess,json\nr={}\nfor n in [624,626,625]:\n p=subprocess.run(["pct","exec",str(n),"--","python3","-c",'+repr('import subprocess,json;ids=subprocess.check_output(["docker","ps","-q"],text=True).split();print(json.dumps([{ "id":c["Id"],"name":c["Name"].lstrip("/"),"image":c["Image"],"started_at":c["State"]["StartedAt"]} for c in json.loads(subprocess.check_output(["docker","inspect"]+ids,text=True))]))')+'],text=True,capture_output=True,timeout=20)\n assert p.returncode==0\n r[str(n)]=json.loads(p.stdout)\nprint(json.dumps(r))'
 STATE['expected_containers']=json.loads(remote(code));assert all(len(x)==4 for x in STATE['expected_containers'].values())
 pvedir='/mnt/storage/mailerblend-recovery/phase4/'+RUN+'/P0';STATE['pve_directory']=pvedir
 code='import pathlib,subprocess,hashlib,json\np=pathlib.Path('+repr(pvedir)+');p.mkdir(parents=True,mode=0o700,exist_ok=False)\nf=p/"integration-before.tar"\nr=subprocess.run(["pct","pull","610",'+repr(CTDIR+'/integration-before.tar')+',str(f)],capture_output=True);assert r.returncode==0\nf.chmod(0o600)\nprint(hashlib.sha256(f.read_bytes()).hexdigest())'
 assert remote(code).strip()==snapshot['sha256']
 backup=HERE/'integration-before.tar'
 with backup.open('xb') as f:r=subprocess.run(SSH+['cat',pvedir+'/integration-before.tar'],stdout=f,stderr=subprocess.PIPE,timeout=120)
 assert r.returncode==0 and sha(backup)==snapshot['sha256']
 with tarfile.open(backup) as a:
  for item in a:
   if item.isfile():assert a.extractfile(item).read() is not None
 remote(ct('import pathlib,json\np=pathlib.Path('+repr(CTDIR)+')/"backup-verified.json"\np.write_text('+repr(json.dumps({'offhost_verified':True,'sha256':snapshot['sha256']}))+')\np.chmod(0o600)'))
 helper('validate');STATE['prepared']=True;STATE['offhost_verified']=True
 print('P0 backup restored/verified, external copy verified, installed-image validation PASS',flush=True)

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run',required=True);p.add_argument('phase',choices=['prepare','apply','rollback-test','firing','resolved','remove-test','observe','check']);a=p.parse_args()
 RUN=a.run;assert re.fullmatch(r'integration-[0-9TZ]+',RUN);os.umask(0o077)
 HERE=Path.home()/'.local/share/mailerblend-recovery/phase4'/RUN/'P0';HERE.mkdir(parents=True,exist_ok=True,mode=0o700)
 CTDIR='/opt/infra-prom/.runtime/'+RUN;STATE=json.loads((HERE/'state.json').read_text()) if (HERE/'state.json').exists() else {'run':RUN,'ct_directory':CTDIR}
 if a.phase=='prepare':prepare()
 elif a.phase=='apply':
  assert STATE['prepared'];helper('rules');helper('targets');STATE['api_checks']=wait_checks();STATE['applied']=True;print('P0 applied; 3 corrected +14 legacy, unique targets and source/memory/Docker verified')
 elif a.phase=='rollback-test':
  assert STATE['applied'];helper('rollback')
  end=time.monotonic()+120
  while True:
   t=get('http://192.168.1.110:9090','/api/v1/targets')['data']['activeTargets']
   if sum(x['labels'].get('job')=='node_exporter' for x in t)==14 and sum(x['labels'].get('job')=='cadvisor' for x in t)==14:break
   assert time.monotonic()<end;time.sleep(2)
  helper('rules');helper('targets');wait_checks();STATE['rollback_test_passed']=True;print('P0 actual rollback to baseline and reapplication PASS')
 elif a.phase in ['firing','resolved']:
  assert STATE['rollback_test_passed'];chain=load('check-incremental-chain.py');rule=chain.verification_rule(624,RUN.replace('-','_'),a.phase=='firing')
  r=rule['groups'][0]['rules'][0];r['expr']='lxc:cpu_usage:percent{ct_id=~"624|626|625"} '+('>= 0' if a.phase=='firing' else '< 0');r['annotations']['description']+=' Run '+RUN
  if a.phase=='firing':STATE['telegram_before']=telemetry()
  remote(ct('import pathlib\np=pathlib.Path('+repr(CTDIR+'/verification.yml')+');p.write_text('+repr(yaml.safe_dump(rule,sort_keys=False,allow_unicode=True))+');p.chmod(0o600)'))
  helper('test');STATE[a.phase+'_rule_loaded_at']=datetime.now(timezone.utc).isoformat();print('Controlled '+a.phase+' rule loaded for 3 Journal; no CPU load induced')
 elif a.phase=='remove-test':helper('remove-test');STATE['test_removed']=True
 elif a.phase=='check':print(json.dumps(checks()))
 elif a.phase=='observe':
  assert STATE['applied'];initial=STATE['resources_before'];rows=[];start=time.monotonic()
  with (HERE/'observations.jsonl').open('x') as out:
   while True:
    row={'at':datetime.now(timezone.utc).isoformat(),'checks':checks(),'resources':resources()}
    for n,r in row['resources'].items():
     events=lambda text:dict(l.split() for l in text.splitlines())
     assert all(events(r['memory.events'])[k]==events(initial[n]['memory.events'])[k] for k in ['oom','oom_kill','oom_group_kill'])
     assert all(float(v)<=5 for v in re.findall(r'avg(?:10|60)=(\S+)',r['memory.pressure']))
    row['elapsed_seconds']=time.monotonic()-start;rows.append(row);out.write(json.dumps(row)+'\n');out.flush()
    print('P0 integrated sample',len(rows),'elapsed',round(row['elapsed_seconds'],1),flush=True)
    if row['elapsed_seconds']>=600:break
    time.sleep(min(30,max(.1,600-row['elapsed_seconds'])))
  assert len(rows)>=21;STATE['observation']={'samples':len(rows),'seconds':rows[-1]['elapsed_seconds'],'sha256':sha(HERE/'observations.jsonl')}
 if a.phase=='observe':
  latest=json.loads((HERE/'state.json').read_text());latest['observation']=STATE['observation'];STATE=latest
 save(HERE/'state.json',STATE)
