#!/usr/bin/env python3
"""Read-only post-deployment watch. Writes a shared HALT marker on any anomaly."""
import argparse,importlib.util,json,os,re,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(path,name):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run',required=True);p.add_argument('--ct',type=int,required=True);p.add_argument('--tag',default='');p.add_argument('--seconds',type=int,default=900);a=p.parse_args();assert re.fullmatch(r'[a-z0-9-]{0,30}',a.tag) and a.seconds>=600;os.umask(0o077)
 m=load(ROOT/'scripts/rollout-approved-exporters.py','approved');m.allowed(a.ct)
 root=Path.home()/'.local/share/mailerblend-recovery/phase4'/a.run;here=root/str(a.ct);state=json.loads((here/'state.json').read_text());assert state['result']=='PASS'
 r=object.__new__(m.Runner);r.watch_mode=True;r.ct=a.ct;r.run=a.run;r.root=root;r.here=here;r.directory='/opt/exporter-phase4-pilot/'+a.run+'-'+str(a.ct);r.log=here/'watch.private.log';r.log.touch(mode=0o600)
 obs=load(here/'bundle/observe.py','observer');initial=json.loads((here/'baseline-sample.json').read_text());before=m.telemetry();start=time.monotonic();end=a.seconds;previous=None;failed=False;n=0
 name='post-watch'+('-'+a.tag if a.tag else '')
 with (here/(name+'.jsonl')).open('x') as out:
  while True:
   tick=time.monotonic();elapsed=tick-start;sample={}
   try:
    sample=r.sample();obs.validate(sample,initial,previous);previous=sample;now=m.telemetry();assert now['alertmanager_notifications_failed_total']==before['alertmanager_notifications_failed_total'];sample['checks_passed']=True
   except Exception as e:
    sample.update(checks_passed=False,failure_type=type(e).__name__,private_traceback=traceback.format_exc())
    if not failed:
     end=max(end,elapsed+600);marker=root/'HALT.json'
     if not marker.exists():m.save(marker,{'ct':a.ct,'reason':'post_watch_anomaly','failure_type':type(e).__name__,'baseline_preserved':True})
     failed=True
   sample['elapsed_seconds']=elapsed;out.write(json.dumps(sample)+'\n');out.flush();n+=1
   if time.monotonic()-start>=end:break
   time.sleep(max(.1,start+min(n*30,end)-time.monotonic()))
 m.save(here/(name+'-result.json'),{'result':'FAIL' if failed else 'PASS','samples':n,'seconds':time.monotonic()-start,'alert_for_proven':False})
 r.stop_cpu_history()
 assert not failed,'Sequence halted; extended observation preserved'
if __name__=='__main__':main()
