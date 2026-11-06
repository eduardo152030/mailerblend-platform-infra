#!/usr/bin/env python3
"""D036: memory-only collectors over strict SSH/stdin. Reads eight accepted CTs; never writes remote files."""
import argparse
from concurrent.futures import ThreadPoolExecutor,as_completed
from datetime import datetime,timezone
import importlib.util
import json
from pathlib import Path
import subprocess
import yaml
ROOT=Path(__file__).resolve().parents[1]
ACCEPTED=[624,626,625,613,621,620,619,623]
def load(name):
 s=importlib.util.spec_from_file_location(name,ROOT/'scripts'/name);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def check(ct,seconds):
 contract=load('exporter_metric_contract.py');source_cpu=contract.render_alignment_source('cpu').split("\nif __name__=='__main__':")[0];source_mem=contract.render_alignment_source('memory').split("\nif __name__=='__main__':")[0]
 service=next(yaml.safe_load(p.read_text()) for p in (ROOT/'inventory/services').glob('*.yml') if int(yaml.safe_load(p.read_text())['service']['vmid'])==ct);ip=service['service']['ip'].split('/')[0];cores=service['resources']['cpu'];memory=service['resources']['memory']*1024**2
 inside="cpu={'__name__':'cpu'};exec("+repr(source_cpu)+",cpu)\nmem={'__name__':'memory'};exec("+repr(source_mem)+",mem)\n"+'''
import urllib.request,json,time,pathlib,hashlib,re
api=cpu['docker_get'];mc=cpu['mc']
def fetch(port):
 with urllib.request.urlopen('http://IP:'+str(port)+'/metrics',timeout=8) as r:assert r.status==200;return r.read().decode()
def inventory():
 out={}
 for item in api('/containers/json?all=true'):
  c=api('/containers/'+item['Id']+'/json')
  out[c['Name'].lstrip('/') ]={'id':c['Id'],'image':c['Image'],'started_at':c['State']['StartedAt'],'running':c['State']['Running'],'restarts':c['RestartCount']}
 return out
def node_check():
 text=fetch(9100)
 def val(key):
  rows=mc.prom_rows(text,key);assert len(rows)==1;return rows[0]['value']
 assert val('node_memory_MemTotal_bytes')==MEMORY and val('lxc_cpu_capacity_cores')==CORES
 assert mc.prom_rows(text,'lxc_cpu_usage_seconds_total')[0]['labels'].get('ct_id')==str(CT)
 assert not mc.prom_rows(text,'node_cpu_seconds_total') and val('lxc_cpu_collector_success')==1 and val('node_textfile_scrape_error')==0
 age=time.time()-val('lxc_cpu_collector_timestamp_seconds');assert -2<=age<=15
 direct=int(dict(l.split() for l in pathlib.Path('/sys/fs/cgroup/cpu.stat').read_text().splitlines())['usage_usec'])/1e6
 assert abs(val('lxc_cpu_usage_seconds_total')-direct)<=max(1,CORES*(age+2))
 return {'total_memory_bytes':MEMORY,'capacity_cores':CORES,'cpu_collector_age_seconds':age,'native_cpu_series':0}
before=inventory();active=[];inputs={}
for name,info in before.items():
 if not info['running']:continue
 c=api('/containers/'+info['id']+'/json');cg=cpu['container_cpu_path'](c,c['Id']);assert cg
 active.append((name,c,cg.parent))
 if name in ['node_exporter','cadvisor']:
  files=(c['Config'].get('Labels') or {}).get('com.docker.compose.project.config_files','').split(',')+[m['Source'] for m in c['Mounts'] if m['Source'].endswith('node-cgroup.sh')]
  for name in files:
   if name and pathlib.Path(name).is_file():inputs[name]=hashlib.sha256(pathlib.Path(name).read_bytes()).hexdigest()
node_before=node_check();history_cpu=[];history_mem=[];pending=None;first=None;previous=None;last=None;valid=0;widths={};end=time.monotonic()+SECONDS;next_scrape=0;errors=[]
while time.monotonic()<end:
 tick=time.monotonic()
 for name,c,cg in active:
  def read_stats():
   s=api('/containers/'+c['Id']+'/stats?stream=false&one-shot=true');match=re.search(r'\\.(\\d+)',s['read']);width=len(match.group(1)) if match else 0;widths[str(width)]=widths.get(str(width),0)+1;return s
  point=mc.capture(cg,read_stats,c['Id'],name,c['State']['StartedAt']);history_cpu.append(point['cpu']);history_mem.append(point['memory'])
 if pending:
  # A source sample older than this collector is warm-up, never an invented historical value.
  ready=all(min(p['time'] for p in history_cpu if p['id']==c['id'])<mc.metric(pending,'container_cpu_usage_seconds_total',c)['timestamp']<max(p['time'] for p in history_cpu if p['id']==c['id']) and min(p['time'] for p in history_mem if p['id']==c['id'])<mc.metric(pending,'container_memory_usage_bytes',c)['timestamp']<max(p['time'] for p in history_mem if p['id']==c['id']) for c in pending['containers'])
  if ready and not pending.get('invalid_freshness'):
   pending['cpu_alignment']=cpu['aligned_evidence'](pending,history_cpu);pending['memory_alignment']=mem['aligned_evidence'](pending,history_mem)
   cpu['validate_alignment'](pending,previous);mem['validate_alignment'](pending,previous)
   if first is None:first=pending
   previous=pending;last=pending;valid+=1;pending=None
 if tick>=next_scrape:
  text=fetch(8085);pending={'time':time.time(),'measurement_contract_schema':mc.SCHEMA,'measurement_scope':mc.scope(),'containers':[dict(info,name=name) for name,info in before.items() if info['running']],'cadvisor':{key:mc.prom_rows(text,key) for key in ['container_cpu_usage_seconds_total','container_memory_usage_bytes']}}
  for c in pending['containers']:
   for key in pending['cadvisor']:
    row=mc.metric(pending,key,c);observed=time.time()
    try:mc.fresh(row['timestamp'],observed)
    except AssertionError:
     pending['invalid_freshness']=True
     item={'kind':'source_freshness','id':c['id'],'name':c['name'],'metric':key,'metric_time':row['timestamp'],'observed_time':observed,'age_seconds':observed-row['timestamp']}
     if not any(e['id']==item['id'] and e['metric']==key and e['metric_time']==item['metric_time'] for e in errors):errors.append(item)
  next_scrape=tick+5
 time.sleep(max(.01,.5-(time.monotonic()-tick)))
assert valid and last,'No temporally bracketed compatibility sample within bounded window'
after=inventory();assert before==after,'Container identity/image/StartedAt/restart drift during read-only audit'
node_after=node_check();windows={cid:last['cpu_alignment'][cid]['time']-first['cpu_alignment'][cid]['time'] for cid in last['cpu_alignment']}
print(json.dumps({'result':'PASS' if not errors else 'FAIL','ct':CT,'source_freshness_errors':errors,'measurement_scope':mc.scope(),'alignment_compatibility_passed':True,'observed_at':time.time(),'seconds':SECONDS,'valid_samples':valid,'container_count':len(active),'containers_unchanged':True,'node_before':node_before,'node_after':node_after,'input_sha256':inputs,'cpu_window_seconds':windows,'timestamp_fractional_widths_observed':widths,'last_cpu_alignment':last['cpu_alignment'],'last_memory_alignment':last['memory_alignment'],'runtime':after,'remote_files_written':False,'deployment_or_restart_performed':False}))
'''.replace('IP',ip).replace('MEMORY',str(memory)).replace('CORES',str(cores)).replace('SECONDS',str(seconds)).replace('CT',str(ct))
 remote="import subprocess,json\nr=subprocess.run(['pct','exec',"+repr(str(ct))+",'--','python3','-'],input="+repr(inside)+",text=True,capture_output=True,timeout="+str(seconds+30)+")\nif r.returncode:print(json.dumps({'ct':"+str(ct)+",'result':'FAIL','error':r.stderr.splitlines()[-1:] } ))\nelse:print(r.stdout)"
 m=load('rollout-approved-exporters.py');r=subprocess.run(m.SSH+['python3','-'],input=remote,text=True,capture_output=True,timeout=seconds+60);assert r.returncode==0,'Strict SSH compatibility audit failed'
 return json.loads(r.stdout)

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--seconds',type=int,default=130);p.add_argument('--workers',type=int,default=4);p.add_argument('--cts',type=int,nargs='+',choices=ACCEPTED,default=ACCEPTED);a=p.parse_args();assert 90<=a.seconds<=180 and 1<=a.workers<=4 and not a.output.exists()
 registry=yaml.safe_load((ROOT/'services/common/exporter-migration.yml').read_text());assert set(registry['prometheus_integrated'])==set(ACCEPTED)
 results=[]
 with ThreadPoolExecutor(max_workers=a.workers) as pool:
  jobs={pool.submit(check,ct,a.seconds):ct for ct in a.cts}
  for future in as_completed(jobs):
   ct=jobs[future]
   try:result=future.result()
   except Exception as exc:result={'ct':ct,'result':'FAIL','error_type':type(exc).__name__}
   results.append(result);print('CT',ct,result['result'],flush=True)
   a.output.write_text(json.dumps({'mode':'read-only','accepted_cts':ACCEPTED,'checked_cts':a.cts,'observed_at_utc':datetime.now(timezone.utc).isoformat(),'results':results},indent=2)+'\n')
 assert len(results)==len(a.cts) and all(r['result']=='PASS' for r in results),'Compatibility did not pass every accepted source; preserve evidence'

if __name__=='__main__':main()
