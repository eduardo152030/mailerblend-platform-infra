#!/usr/bin/env python3
"""Observación D088 de solo lectura600s/21; sin resets de baseline ni secretos."""
import json,time,urllib.request,concurrent.futures
from datetime import datetime,timezone
from pathlib import Path

def fetch(url):
    with urllib.request.urlopen(url,timeout=15) as r:return json.load(r)

def direct(ip):
    t=time.monotonic()
    try:
        with urllib.request.urlopen(f'http://{ip}:8085/metrics',timeout=15) as r:
            body=r.read()
        return dict(ok=True,seconds=time.monotonic()-t,bytes=len(body),cpu=b'container_cpu_usage_seconds_total' in body,ram=b'container_memory_working_set_bytes' in body)
    except Exception as e:return dict(ok=False,error=type(e).__name__,seconds=time.monotonic()-t)

rows=[];start=time.monotonic()
for i in range(21):
    if i:time.sleep(max(0,start+i*30-time.monotonic()))
    row=dict(time_utc=datetime.now(timezone.utc).isoformat(),elapsed=time.monotonic()-start)
    try:
        targets=fetch('http://192.168.1.110:9090/api/v1/targets')['data']['activeTargets']
        row['targets']=[{k:t[k] for k in ['labels','health','lastError','lastScrapeDuration','lastScrape']} for t in targets if t['labels'].get('job')=='cadvisor' and t['labels'].get('instance') in ['192.168.1.123:8085','192.168.1.118:8085']]
        row['alerts']=fetch('http://192.168.1.110:9090/api/v1/alerts')['data']['alerts']
        with concurrent.futures.ThreadPoolExecutor(2) as pool:row['direct']=dict(zip(['623','618'],pool.map(direct,['192.168.1.123','192.168.1.118'])))
    except Exception as e:row['error']=type(e).__name__
    rows.append(row)
    Path('docs/roadmap/evidence/2026-11-13-d088-observation.json').write_text(json.dumps(rows,indent=2))
    print(i,round(row['elapsed'],1),[(t['labels']['instance'],t['health'],round(t['lastScrapeDuration'],3)) for t in row.get('targets',[])],row.get('direct'),flush=True)
