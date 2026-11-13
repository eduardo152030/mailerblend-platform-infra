#!/usr/bin/env python3
"""Solo lectura: consultas reales Fleet/Details para630/631; sin inferencia."""
import importlib.util,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];s=importlib.util.spec_from_file_location('stage',ROOT/'scripts/phase6-stage-a.py');t=importlib.util.module_from_spec(s);s.loader.exec_module(t)
checks=[]
for uid in ['proxmox-lxc-fleet','proxmox-lxc-details']:
 response=t.g.api('/api/dashboards/uid/'+uid);assert response['meta']['provisioned'];d=response['dashboard']
 for ct,service in [('630','infra-llm'),('631','infra-webui')]:
  for panel in d['panels']:
   for target in panel.get('targets',[]):
    expr=target.get('expr')
    if not expr:continue
    q=expr.replace('${lxc:regex}',ct).replace('${service:regex}',service);rows=t.query(q)
    assert all(math.isfinite(float(r['value'][1])) for r in rows)
    assert all(r['metric'].get('ct_id',ct)==ct and r['metric'].get('service',service)==service for r in rows),'Cross CT data'
    if panel['title'].startswith(('LXC health','LXC ·')):assert len(rows)==1,(ct,panel['title'],target['refId'],len(rows))
    if panel['title'].startswith('Docker ·') and ct=='630':assert not rows,'Native630 has Docker series'
    checks.append({'uid':uid,'ct_id':ct,'panel':panel['title'],'ref':target['refId'],'series':len(rows),'values':[r['value'][1] for r in rows] if panel['title'].startswith(('LXC health','LXC ·')) else []})
print(json.dumps({'result':'PASS','queries':len(checks),'new_cts':[630,631],'native_docker_series':0}));(ROOT/'docs/roadmap/evidence/ia-chat-2026-11-13/grafana-queries-final.json').write_text(json.dumps(checks,indent=2)+'\n')
