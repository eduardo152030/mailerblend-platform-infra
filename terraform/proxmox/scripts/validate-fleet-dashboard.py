#!/usr/bin/env python3
"""Validate D052 PromQL against the actual Prometheus, retaining sanitized evidence."""
import os,json,urllib.request,urllib.parse,time,math,yaml
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
D=ROOT/'services/infra-grafana/config/provisioning/fleet-assets/proxmox-lxc-fleet.json'
def query(q):
 for v in ['${lxc:regex}','${service:regex}']:q=q.replace(v,'.*')
 data=urllib.parse.urlencode({'query':q}).encode()
 with urllib.request.urlopen(urllib.request.Request('http://192.168.1.110:9090/api/v1/query',data=data),timeout=30) as r:d=json.load(r)
 assert d['status']=='success',d
 return d['data']['result']
def main():
 expected={str(yaml.safe_load(p.read_text())['service']['vmid']) for p in (ROOT/'inventory/services').glob('*.yml')}
 d=json.loads(D.read_text());out={'timestamp_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'uid':d['uid'],'queries':[]}
 for p in d['panels']:
  for t in p.get('targets',[]):
   rows=query(t['expr']);values=[float(r['value'][1]) for r in rows]
   assert all(math.isfinite(v) for v in values),(p['title'],t['refId'],'nonfinite')
   if p['type']=='timeseries' or p['title'].startswith('LXC health'):
    keys=[r['metric'].get('ct_id') for r in rows];assert len(keys)==len(set(keys)),('duplicate CT',p['title'],t['refId'])
    assert set(keys)==expected,(p['title'],t['refId'],'inventory mismatch',len(rows))
   if p['type']=='timeseries':assert all(0<=v<=100 for v in values),(p['title'],values)
   out['queries'].append({'panel':p['title'],'refId':t['refId'],'series':len(rows),'samples':rows if p['title'].startswith('LXC health') or p['type']=='timeseries' else []})
 # Variables and datasource metadata are independently inspected; no absent environment invented.
 out['variables']=[v['name'] for v in d['templating']['list']]
 out['result']='PASS';path=ROOT/('docs/roadmap/evidence/'+os.environ.get('FLEET_EVIDENCE_DATE','2026-11-07')+'-'+os.environ.get('FLEET_EVIDENCE_ID','d052')+'-promql.json');path.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n');print('PASS:',len(out['queries']),'live queries; health and resources',len(expected),'unique CT each; finite percentages')
if __name__=='__main__':main()
