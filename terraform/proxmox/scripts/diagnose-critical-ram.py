#!/usr/bin/env python3
"""Bounded read-only isolation proof for a failed exporter RAM bracket; never converts FAIL to PASS."""
import argparse,importlib.util,json,subprocess,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def diagnose(ct,run):
 assert ct in [617,618,615,614,622,611,616,610] and re.fullmatch(r'integration-[0-9TZ]+',run)
 directory='/opt/exporter-phase4-pilot/'+run+'-'+str(ct)
 code='''from pathlib import Path
import json
p=Path(DIRECTORY);ns={'__name__':'readonly'};exec((p/'memory-alignment.py').read_text().split("\\nif __name__=='__main__':")[0],ns)
records=[json.loads(l) for l in (p/'cpu-probe-failures.jsonl').read_text().splitlines()];record=records[-1];s=record['sample'];mc=ns['mc'];out={'message':record['message'],'scope':s['measurement_scope'],'sample_time':s['time'],'containers':[],'cpu_aligned_count':len(s.get('cpu_alignment',{}))}
cpu={'__name__':'readonly'};exec((p/'cpu-alignment.py').read_text().split("\\nif __name__=='__main__':")[0],cpu);cpu['time']=__import__('types').SimpleNamespace(time=lambda:s['time']);cpu['validate_alignment'](s);out['historical_replay_clock']=s['time']
metric_times=[mc.metric(s,'container_memory_usage_bytes',c)['timestamp'] for c in s['containers'] if c['running']];history=mc.read_history(p/'memory-history.jsonl',min(metric_times)-2,max(metric_times)+2)
for cid,c in mc.active(s).items():
 row=mc.metric(s,'container_memory_usage_bytes',c);assert -2<=s['time']-row['timestamp']<=90
 points=mc.points(history,c,['docker_bytes','cgroup_before','cgroup_after']);pair=ns['bracket'](points,row['timestamp']);failed=[]
 for point in pair:
  for field in ['docker_bytes','cgroup_before','cgroup_after']:
   limit=ns['allowance'](point[field],c['name'])
   if abs(row['value']-point[field])>limit:failed.append({'field':field,'reference':point[field],'difference':abs(row['value']-point[field]),'allowed':limit})
 out['containers'].append({'name':c['name'],'id':cid,'started_at':c['started_at'],'metric_timestamp':row['timestamp'],'age_at_sample':s['time']-row['timestamp'],'cadvisor_bytes':row['value'],'bracket':pair,'failures':failed})
failed=[c for c in out['containers'] if c['failures']]
assert len(failed)==1 and failed[0]['name']=='cadvisor'
c=failed[0];values=[p[f] for p in c['bracket'] for f in ['docker_bytes','cgroup_before','cgroup_after']]
assert min(values)<=c['cadvisor_bytes']<=max(values),'Not a contained volatile gauge bracket'
assert out['message']=='Aligned cAdvisor RAM mismatch or volatile bracket: cadvisor'
out.update(ct=CT,isolated_local_measurement=True,metric_acceptance_passed=False,common_framework_defect_demonstrated=False,active_container_count=len(mc.active(s)))
print(json.dumps(out))
'''.replace('DIRECTORY',repr(directory)).replace('CT',str(ct))
 remote='import subprocess\nr=subprocess.run('+repr(['pct','exec',str(ct),'--','python3','-'])+',input='+repr(code)+',capture_output=True,text=True);print(r.stdout);assert r.returncode==0'
 spec=importlib.util.spec_from_file_location('r',ROOT/'scripts/rollout-approved-exporters.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);r=subprocess.run(m.SSH+['python3','-'],input=remote,text=True,capture_output=True,timeout=45);assert r.returncode==0,'No positive CT-local isolation proof';return json.loads(r.stdout)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--ct',type=int,required=True);p.add_argument('--run',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists();x=diagnose(a.ct,a.run);a.output.write_text(json.dumps(x,indent=2)+'\n');print({'ct':a.ct,'isolated_local_measurement':True,'metric_acceptance_passed':False})
