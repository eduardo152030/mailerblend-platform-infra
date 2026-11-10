#!/usr/bin/env python3
"""D060 read-only PromQL checks across every monitored CT; never publish missing data as zero."""
import concurrent.futures,json,math,time,urllib.parse,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];BASE='http://192.168.1.110:9090'
def api(path,data=None):
 with urllib.request.urlopen(urllib.request.Request(BASE+path,data=urllib.parse.urlencode(data).encode() if data else None),timeout=45) as r:
  d=json.load(r);assert d['status']=='success';return d['data']
def query(q):return api('/api/v1/query',{'query':q})['result']
def substitute(expr,ct,service):
 return expr.replace('${lxc:regex}',ct).replace('${service:regex}',service)
def main():
 model=json.loads((ROOT/'services/infra-grafana/config/provisioning/fleet-assets/proxmox-lxc-details.json').read_text())
 inv=query('lxc:cpu_inventory:expected');assert len(inv)==17;checks=[]
 def one(row):
  ct=row['metric']['ct_id'];service=row['metric']['service'];out=[]
  for p in model['panels']:
   for t in p.get('targets',[]):
    q=substitute(t['expr'],ct,service);rows=query(q)
    for r in rows:
     labels=r['metric'];value=float(r['value'][1]);assert math.isfinite(value),(ct,p['title'],'nonfinite')
     assert labels.get('ct_id',ct)==ct,(ct,p['title'],t['refId'],labels)
     if 'service' in labels:assert labels['service']==service,(ct,'cross-service',labels['service'])
    if p['title'].startswith('LXC ·') or p['title'] in ['CPU asignada','RAM asignada','Disco raíz · capacidad','Identidad e IP del LXC']:assert len(rows)==1,(ct,p['title'],t['refId'],len(rows))
    if p['title'].startswith('Docker ·'):
     keys=[r['metric']['container_key'] for r in rows];assert len(keys)==len(set(keys));assert all(k.startswith(service+'|') for k in keys)
    out.append({'ct_id':ct,'panel':p['title'],'ref':t['refId'],'series':len(rows),'samples':rows if p['title'].startswith('LXC ·') else []})
  return out
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
  for out in pool.map(one,inv):checks.extend(out)
 # Range-query parser and history checks on representative CTs, including separate clones of Docker IDs.
 history=[]
 for ct in ['614','615','618','613']:
  service=next(x['metric']['service'] for x in inv if x['metric']['ct_id']==ct)
  for p in model['panels']:
   for t in p.get('targets',[]):
    if not t.get('range'):continue
    rows=api('/api/v1/query_range',{'query':substitute(t['expr'],ct,service),'start':time.time()-3600,'end':time.time(),'step':60})['result']
    assert all(r['metric'].get('ct_id')==ct and r['metric'].get('service',service)==service for r in rows)
    history.append({'ct_id':ct,'panel':p['title'],'series':len(rows)})
 result={'timestamp_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'result':'PASS','ct_count':len(inv),'query_count':len(checks),'checks':checks,'history':history,'cross_lxc_data':False}
 (ROOT/'docs/roadmap/evidence/2026-11-09-d060-promql.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS',len(checks),'instant queries across17CT;',len(history),'range queries; no cross-CT/service data')
if __name__=='__main__':main()
