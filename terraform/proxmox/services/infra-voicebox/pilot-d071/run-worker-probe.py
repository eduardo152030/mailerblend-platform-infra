#!/usr/bin/env python3
"""PVE-side bounded initial probe, production Voicebox remains unchanged."""
import subprocess,json,time,uuid,argparse
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--label',required=True);a=p.parse_args();out=Path('/root/voicebox-d071')/a.label;out.mkdir(mode=0o700,parents=True,exist_ok=False)
def rpc(path,value=None):
 code="import json,sys,urllib.request;d=json.load(sys.stdin);q=urllib.request.Request('http://127.0.0.1:8080'+d['path'],data=None if d['value'] is None else json.dumps(d['value']).encode(),headers={'Content-Type':'application/json'});print(urllib.request.urlopen(q,timeout=8).read().decode())"
 return json.loads(subprocess.check_output(['pct','exec','627','--','docker','exec','-i','voicebox-openvoice','python','-c',code],input=json.dumps({'path':path,'value':value}).encode(),timeout=12))
CG=Path('/sys/fs/cgroup/lxc/627')
def measure():
 return {'elapsed':time.monotonic()-start,'memory_current':int((CG/'memory.current').read_text()),'swap':int((CG/'memory.swap.current').read_text()),'events':dict(x.split() for x in (CG/'memory.events').read_text().splitlines()),'cpu':(CG/'cpu.stat').read_text(),'host_available':int(next(x.split()[1] for x in Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')))*1024,'host_pressure':Path('/proc/pressure/memory').read_text()}
start=time.monotonic();baseline=measure();result={'status':'IN_PROGRESS','measurements':[]};ident=str(uuid.uuid4())
try:
 assert baseline['host_available']>1.5*2**30 and float(baseline['host_pressure'].splitlines()[1].split()[1].split('=')[1])<2
 assert rpc('/health')['status']=='healthy'
 rpc('/jobs',{'request_id':ident,'profile_id':'1fd00418-2a79-4178-883f-af6c3f5e07ee','text':'Hola, soy Eduardo Velázquez. Esta es una prueba de mi voz generada mediante inteligencia artificial.','timeout_seconds':180});result['worker_job_id']=ident
 while time.monotonic()-start<190:
  m=measure();result['measurements'].append(m);(out/'result.json').write_text(json.dumps(result,indent=2))
  assert m['memory_current']<6.5*2**30 and m['swap']-baseline['swap']<64*2**20,'Memory/swap stop'
  assert m['host_available']>1.5*2**30 and float(m['host_pressure'].splitlines()[1].split()[1].split('=')[1])<2,'Host safety stop'
  assert all(int(m['events'][k])==int(baseline['events'][k]) for k in ['oom','oom_kill','oom_group_kill']),'OOM stop'
  job=rpc('/jobs/'+ident)
  if job['status'] in ['completed','failed','cancelled']:break
  time.sleep(1)
 assert job['status']=='completed',job.get('error','Probe timeout')
 result.update({'status':'TECHNICAL_PASS','job':job})
except BaseException as e:
 result.update({'status':'FAIL','reason':str(e)})
 try:result['cancel']=rpc('/jobs/'+ident+'/cancel',{})
 except Exception:pass
 subprocess.run(['pct','exec','627','--','docker','stop','--timeout','10','voicebox-openvoice'],check=True,timeout=20)
finally:(out/'result.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='measurements'}),flush=True)
