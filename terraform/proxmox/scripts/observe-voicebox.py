#!/usr/bin/env python3
"""Observación continua D063:600s/21 muestras, sin ocultar anomalías ni reiniciar baseline."""
import argparse,datetime,json,time,urllib.parse,urllib.request
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=Path.home()/'.local/share/mailerblend-recovery/new-lxc/voicebox-d063');ap.add_argument('--duration',type=int,default=600);args=ap.parse_args();assert args.duration>=180 and args.duration%30==0;ROOT=args.output;ROOT.mkdir(parents=True,exist_ok=True)
def query(q):
 with urllib.request.urlopen('http://192.168.1.110:9090/api/v1/query?'+urllib.parse.urlencode({'query':q}),timeout=15) as r:d=json.load(r)
 assert d['status']=='success';return d['data']['result']
result={'started_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'result':'IN PROGRESS','duration_required_seconds':args.duration,'samples':[]};start=time.monotonic()
try:
 for index in range(args.duration//30+1):
  if index:time.sleep(max(0,start+index*30-time.monotonic()))
  counts={r['metric']['job']:int(float(r['value'][1])) for r in query('count by(job)(up == 1)')};assert counts['node_exporter']==18 and counts['cadvisor']==18 and counts['blackbox']==19
  assert not query('up == 0'),'Target DOWN'
  probes=query('probe_success{job="blackbox"}');assert len(probes)==19 and all(float(x['value'][1])==1 for x in probes)
  cpu=query('lxc:cpu_usage:percent');assert len(cpu)==18 and all(0<=float(x['value'][1])<=100 for x in cpu)
  alerts=query('ALERTS{alertstate=~"firing|pending"}');assert not alerts,'Alerta FIRING/PENDING'
  available=query('100*node_memory_MemAvailable_bytes{service="infra-voicebox"}/node_memory_MemTotal_bytes{service="infra-voicebox"}');assert len(available)==1 and float(available[0]['value'][1])>=20,'Memoria sin margen20%'
  with urllib.request.urlopen('http://192.168.1.127:17493/health',timeout=10) as r:health=json.load(r)
  assert health['status']=='healthy' and health['backend_variant']=='cpu'
  sample={'index':index,'elapsed_seconds':round(time.monotonic()-start,2),'counts_up':counts,'memory_available_percent':float(available[0]['value'][1]),'alerts':0,'probes_success':19,'cpu_sources':18};result['samples'].append(sample);(ROOT/'observation.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS sample',index,'elapsed',sample['elapsed_seconds'],flush=True)
 result['result']='PASS';result['elapsed_seconds']=round(time.monotonic()-start,2)
except Exception as error:
 result['result']='HALT';result['error']=str(error);raise
finally:(ROOT/'observation.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'result':result['result'],'samples':len(result['samples']),'elapsed_seconds':result.get('elapsed_seconds')}))
