#!/usr/bin/env python3
"""CT613 monitoring transaction; preserves the accepted P0 contracts and container IDs."""
import argparse,copy,hashlib,importlib.util,json,os,re,subprocess,time
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[1]
def load(n):
 s=importlib.util.spec_from_file_location(n,ROOT/'scripts'/n);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n');p.chmod(0o600)
def gate(run):
 p=Path.home()/'.local/share/mailerblend-recovery/phase4'/run/'P0/state.json';s=json.loads(p.read_text())
 assert s.get('result')=='PASS' and s['recipient_confirmation']['confirmed'] and s['observation']['seconds']>=600,'P0 must fully pass first'

def stage(files,manifest,initial=False):
 code='import pathlib\nd=pathlib.Path('+repr(P.CTDIR)+')\n'
 if initial:code+='assert not d.exists()\nd.mkdir(parents=True,mode=0o700)\n'
 payload={'manifest.json':json.dumps(manifest),**{'candidate/'+k:v for k,v in files.items()}}
 if initial:payload['apply.py']=(ROOT/'scripts/apply-incremental-config.py').read_text()
 for name,body in payload.items():code+='p=d/'+repr(name)+'\np.parent.mkdir(parents=True,exist_ok=True)\np.write_text('+repr(body)+')\np.chmod('+('0o644' if name.startswith('candidate/') else '0o600')+')\n'
 code+='for p in (d/"candidate").rglob("*"):\n if p.is_dir():p.chmod(0o755)\n(d/"candidate").chmod(0o755)\n'
 P.remote(P.ct(code))

def prepare():
 assert not (HERE/'state.json').exists()
 subprocess.run(['python3',str(ROOT/'scripts/snapshot-incremental-monitoring.py'),'--output',str(HERE/'baseline.json')],check=True)
 b=json.loads((HERE/'baseline.json').read_text());s=yaml.safe_load((ROOT/'services/common/exporter-migration.yml').read_text())
 files,manifest=PREP.build(b,s,PREP.generator.load_services());stage(files,manifest,True)
 snap=json.loads(P.helper('snapshot'));STATE.update(snap);STATE['manifest']=manifest
 pvedir='/mnt/storage/mailerblend-recovery/phase4/'+RUN+'/R1-monitoring';STATE['pve_directory']=pvedir
 code='import pathlib,subprocess,hashlib\np=pathlib.Path('+repr(pvedir)+');p.mkdir(parents=True,mode=0o700,exist_ok=False)\nf=p/"integration-before.tar"\nr=subprocess.run(["pct","pull","610",'+repr(P.CTDIR+'/integration-before.tar')+',str(f)],capture_output=True);assert r.returncode==0\nf.chmod(0o600)\nprint(hashlib.sha256(f.read_bytes()).hexdigest())'
 assert P.remote(code).strip()==snap['sha256']
 target=HERE/'integration-before.tar'
 with target.open('xb') as f:r=subprocess.run(P.SSH+['cat',pvedir+'/integration-before.tar'],stdout=f,stderr=subprocess.PIPE,timeout=120)
 assert r.returncode==0 and hashlib.sha256(target.read_bytes()).hexdigest()==snap['sha256']
 P.remote(P.ct('import pathlib\np=pathlib.Path('+repr(P.CTDIR+'/backup-verified.json')+');p.write_text('+repr(json.dumps({'offhost_verified':True,'sha256':snap['sha256']}))+');p.chmod(0o600)'))
 STATE['offhost_verified']=True;STATE['prepared']=True


def point():
 code='''import pathlib,subprocess,json,time
host=str(pathlib.Path('/proc/1/ns/cgroup').readlink())
probe=PROBE
r=subprocess.run(['pct','exec','613','--','python3','-'],input=probe,text=True,capture_output=True,timeout=40);assert r.returncode==0
out=json.loads(r.stdout);assert out['cadvisor_namespace']==out['ct_namespace'] and out['ct_namespace']!=host
parent=dict(l.split() for l in pathlib.Path('/sys/fs/cgroup/lxc/613/cpu.stat').read_text().splitlines());assert abs(out['cpu_usage_seconds']-int(parent['usage_usec'])/1e6)<20
out['parent_cpu_seconds']=int(parent['usage_usec'])/1e6;out['pve_namespace']=host
print(json.dumps(out))
'''
 probe='''import pathlib,subprocess,json,re,urllib.request,time
with urllib.request.urlopen('http://192.168.1.113:9100/metrics',timeout=8) as r:text=r.read().decode()
def value(name):return float(re.search(r'^'+name+r'(?:\\{[^}]*\\})? (\\S+)',text,re.M).group(1))
assert value('lxc_cpu_capacity_cores')==1 and value('node_memory_MemTotal_bytes')==536870912
assert value('lxc_cpu_collector_success')==1 and -2<=time.time()-value('lxc_cpu_collector_timestamp_seconds')<=15
assert not re.search('^node_cpu_seconds_total',text,re.M)
ids=subprocess.check_output(['docker','ps','-q'],text=True).split();containers=json.loads(subprocess.check_output(['docker','inspect']+ids,text=True));assert {c['Name'].lstrip('/') for c in containers}=={'node_exporter','cadvisor'}
cad=next(c for c in containers if c['Name']=='/cadvisor')
print(json.dumps({'ct':613,'result':'PASS','cpu_source':'cgroup_v2_textfile','cpu_usage_seconds':value('lxc_cpu_usage_seconds_total'),'memory_total_bytes':536870912,'allocated_cores':1,'ct_namespace':str(pathlib.Path('/proc/1/ns/cgroup').readlink()),'cadvisor_namespace':str((pathlib.Path('/proc')/str(cad['State']['Pid'])/'ns/cgroup').readlink()),'containers':[{'name':c['Name'].lstrip('/'),'id':c['Id'],'started_at':c['State']['StartedAt'],'image':c['Image']} for c in containers],'observation_complete':False}))
'''
 out=json.loads(P.remote(code.replace('PROBE',repr(probe))))
 save(HERE/'cpu-point.json',out);return out

def api_check():
 chain=load('check-incremental-chain.py');data=chain.collect('http://192.168.1.110:9090',613,'infra-hola');assert not chain.assess(data),','.join(chain.assess(data))
 return float(data['cpu_percent'][0]['value'][1])
def integrate(resume=False):
 out=point()
 if not resume:
  s=yaml.safe_load((ROOT/'services/common/exporter-migration.yml').read_text());s['cpu_contract_verified']['613']=str(HERE/'cpu-point.json');s['remaining_order'].remove(613)
  files,manifest=PREP.build(json.loads((HERE/'baseline.json').read_text()),s,PREP.generator.load_services());stage(files,manifest);STATE['manifest']=manifest
 P.helper('validate');P.helper('rules');P.helper('targets')
 end=time.monotonic()+180
 while True:
  try:STATE['cpu_percent']=api_check();break
  except (AssertionError,OSError,ValueError):
   assert time.monotonic()<end,'R1 integration timeout';time.sleep(3)
 # Previously accepted P0 sources must remain healthy.
 c=load('check-incremental-chain.py')
 for ct,name in [(624,'infra-journal-web'),(626,'infra-journal-api'),(625,'infra-journal-db')]:assert not c.assess(c.collect('http://192.168.1.110:9090',ct,name))
 STATE['integrated']=True;STATE['namespace_verified']=True

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run',required=True);p.add_argument('phase',choices=['prepare','integrate','rollback','resume','firing','resolved','remove-test','check']);a=p.parse_args()
 RUN=a.run;assert re.fullmatch(r'integration-[0-9TZ]+',RUN);gate(RUN);os.umask(0o077)
 HERE=Path.home()/'.local/share/mailerblend-recovery/phase4'/RUN/'613/monitoring';HERE.mkdir(parents=True,exist_ok=True,mode=0o700)
 P=load('run-incremental-p0.py');P.HERE=HERE;P.CTDIR='/opt/infra-prom/.runtime/'+RUN+'-r1';PREP=load('prepare-incremental-monitoring.py')
 STATE=json.loads((HERE/'state.json').read_text()) if (HERE/'state.json').exists() else {'run':RUN}
 if a.phase=='prepare':prepare()
 elif a.phase=='integrate':integrate()
 elif a.phase=='resume':integrate(True)
 elif a.phase=='rollback':P.helper('rollback');STATE['rollback_verified']=True
 elif a.phase=='check':print(api_check())
 elif a.phase in ['firing','resolved']:
  c=load('check-incremental-chain.py');rule=c.verification_rule(613,RUN.replace('-','_')+'_R1',a.phase=='firing');rule['groups'][0]['rules'][0]['annotations']['description']+=' Run '+RUN+' R1'
  if a.phase=='firing':STATE['telegram_before']=P.telemetry()
  P.remote(P.ct('import pathlib\np=pathlib.Path('+repr(P.CTDIR+'/verification.yml')+');p.write_text('+repr(yaml.safe_dump(rule,sort_keys=False,allow_unicode=True))+');p.chmod(0o600)'))
  P.helper('test');STATE[a.phase+'_loaded']=True
 else:P.helper('remove-test');STATE['test_removed']=True
 save(HERE/'state.json',STATE);print('R1 monitoring',a.phase,'PASS',flush=True)
