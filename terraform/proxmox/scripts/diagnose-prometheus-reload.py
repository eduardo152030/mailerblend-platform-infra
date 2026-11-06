#!/usr/bin/env python3
"""D025 diagnostic only: revalidate/reload unchanged backed-up config and record API health."""
import argparse,hashlib,importlib.util,json,os,subprocess,threading,time,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(n):
 s=importlib.util.spec_from_file_location(n,ROOT/'scripts'/n);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run',required=True);p.add_argument('--execute',action='store_true');a=p.parse_args();assert a.execute;os.umask(0o077)
 root=Path.home()/'.local/share/mailerblend-recovery/phase4'/a.run;state=json.loads((root/'620/state.json').read_text());assert state['result']=='BLOCKED_ROLLED_BACK' and state['safe_rollback_verified'] and (root/'HALT.json').exists()
 trace=root/'diagnostic-reload-health.jsonl';assert not trace.exists();stop=threading.Event();rows=[]
 def poll():
  with trace.open('x') as out:
   while not stop.is_set():
    try:
     with urllib.request.urlopen('http://192.168.1.110:9090/api/v1/rules',timeout=5) as response:rules=json.load(response)['data']['groups']
     counts={}
     for group in rules:
      for rule in group['rules']:counts[rule['health']]=counts.get(rule['health'],0)+1
     row={'time':time.time(),'health_counts':counts};rows.append(row);out.write(json.dumps(row)+'\n');out.flush()
    except Exception as exc:rows.append({'time':time.time(),'error_type':type(exc).__name__})
    stop.wait(.5)
 thread=threading.Thread(target=poll);thread.start()
 directory='/opt/infra-prom/.runtime/'+a.run+'-620'
 probe='import importlib.util,pathlib,hashlib,json\nd=pathlib.Path('+repr(directory)+')\ns=importlib.util.spec_from_file_location("apply",d/"apply.py");m=importlib.util.module_from_spec(s);s.loader.exec_module(m)\nm.checked(d)\nbefore=m.identity();m.reload();m.checked(d);assert m.identity()==before;print("Unchanged backed-up configuration reloaded; identity and readiness preserved")'
 code='import subprocess\nr=subprocess.run(["pct","exec","610","--","python3","-"],input='+repr(probe)+',capture_output=True,text=True,timeout=180)\nprint(r.stdout+r.stderr);assert r.returncode==0'
 try:
  with load('monitoring-transaction-lock.py').monitoring_lock(root,exclusive=True):r=subprocess.run(load('rollout-approved-exporters.py').SSH+['python3','-'],input=code,capture_output=True,text=True,timeout=210)
  (root/'diagnostic-reload.private.log').write_text(r.stdout+r.stderr);(root/'diagnostic-reload.private.log').chmod(0o600);assert r.returncode==0,'Diagnostic reload failed; retain HALT'
 finally:stop.set();thread.join(10)
 report={'same_configuration':True,'no_container_restart':True,'unknown_health_observed':any('unknown' in x.get('health_counts',{}) for x in rows),'polls':len(rows),'bad_health_observed':any(any(k not in ['ok','unknown'] for k in x.get('health_counts',{})) for x in rows),'api_errors':[x for x in rows if 'error_type' in x]}
 (ROOT/'docs/roadmap/evidence/2026-11-02-reload-race-diagnosis.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
if __name__=='__main__':main()
