#!/usr/bin/env python3
"""21 muestras/600s: salud, frescura, CPU/RAM, Docker y disponibilidad en Grafana.
No carga modelos ni interviene otros CT. Cualquier anomalía veta aceptación.
"""
import importlib.util,json,time,datetime,urllib.request,urllib.parse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sp=importlib.util.spec_from_file_location('stage',ROOT/'scripts/phase6-stage-a.py');t=importlib.util.module_from_spec(sp);sp.loader.exec_module(t)
P=ROOT/'docs/roadmap/evidence/ia-chat-2026-11-13/monitoring-observation.json';samples=[];start=time.monotonic()
queries={'node':'up{job="node_exporter",service=~"infra-llm|infra-webui"}','cadvisor':'up{job="cadvisor",service="infra-webui"}','probes':'probe_success{job="blackbox",service=~"infra-llm|infra-webui"}','cpu':'lxc:cpu_usage:percent{ct_id=~"630|631"}','contract':'lxc:cpu_contract:valid{ct_id=~"630|631"}','ram':'node_memory_MemTotal_bytes{job="node_exporter",service=~"infra-llm|infra-webui"}','pve':'pve_up{ct_id=~"630|631"}','alerts':'ALERTS{service=~"infra-llm|infra-webui",alertstate="firing"}','freshness':'time()-lxc_cpu_collector_timestamp_seconds{job="node_exporter",ct_id=~"630|631"}'}
for i in range(21):
 while time.monotonic()<start+i*30:time.sleep(min(1,start+i*30-time.monotonic()))
 q={k:t.query(v) for k,v in queries.items()};errors=[]
 for key,count in [('node',2),('cadvisor',1),('probes',2),('cpu',2),('contract',2),('ram',2),('pve',2),('freshness',2)]:
  if len(q[key])!=count:errors.append(key+' cardinality '+str(len(q[key])))
 for key in ['node','cadvisor','probes','pve']:
  if any(float(r['value'][1])!=1 for r in q[key]):errors.append(key+' not healthy')
 if any(not 0<=float(r['value'][1])<=100 for r in q['cpu']):errors.append('CPU outside allocation')
 if any(not -2<=float(r['value'][1])<=45 for r in q['freshness']):errors.append('staleCPU')
 if q['alerts']:errors.append('firing alert')
 sample={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'elapsed_seconds':time.monotonic()-start,'queries':q,'errors':errors};samples.append(sample)
 P.write_text(json.dumps({'status':'IN PROGRESS','samples':samples},indent=2)+'\n');print(i,errors,flush=True)
 # Initial discovery/rate convergence is explicit warmup; acceptance requires a fresh full observation.
 if errors:raise SystemExit('HALT: monitoring not ready; no acceptance')
out={'status':'PASS','samples':samples,'duration_seconds':time.monotonic()-start,'sample_count':len(samples)};P.write_text(json.dumps(out,indent=2)+'\n');print('PASS 600s/21')
