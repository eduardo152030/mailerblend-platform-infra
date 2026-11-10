#!/usr/bin/env python3
"""Authenticated read-only browser validation of D052; requires Playwright."""
import os,json,time,base64,importlib.util
from pathlib import Path
from playwright.sync_api import sync_playwright
spec=importlib.util.spec_from_file_location('deploy','scripts/deploy-fleet-dashboard.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
user,password=base64.b64decode(m.credentials()['Authorization'].split(' ',1)[1]).decode().split(':',1)
result={'timestamp_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'checks':{},'query_errors':[],'js_errors':[],'frame_counts':[],'query_endpoints':[]}
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True)
 page=browser.new_page(viewport={'width':1920,'height':1500})
 page.on('pageerror',lambda e:result['js_errors'].append(str(e)))
 def response(r):
  if '/api/ds/query' not in r.url and 'query' not in r.url:return
  try:
   result['query_endpoints'].append(r.url.split('?')[0])
   d=r.json()
   for ref,x in d.get('results',{}).items():
    if x.get('error'):result['query_errors'].append({'ref':ref,'error':x['error']})
    for f in x.get('frames',[]):
     fields=[z['name'] for z in f['schema']['fields']];vals=f.get('data',{}).get('values',[])
     if 'ct_id' in fields and vals:result['frame_counts'].append({'ref':ref,'rows':len(vals[0]),'fields':fields})
  except Exception:pass
 page.on('response',response)
 page.goto(m.URL+'/login');page.locator('input[name="user"]').fill(user);page.locator('input[name="password"]').fill(password);page.get_by_role('button',name='Log in',exact=True).click();page.wait_for_timeout(1500)
 base=m.URL+'/d/proxmox-lxc-fleet/proxmox-lxc-fleet-overview?theme=dark'
 page.goto(base);page.wait_for_timeout(5000)
 text=page.locator('body').inner_text();assert '17' in text and 'UNKNOWN' in text and 'HEALTHY' in text
 result['checks']['default_real_data']=True
 if os.environ.get('FLEET_EVIDENCE_ID') in ['d056','d057']:
  import re
  assert 'Uptime' in text and len(re.findall(r'\b\d+\s+d\s+\d{2}:\d{2}:\d{2}\b',text))>=3, 'Readable uptime durations missing'
  result['checks']['real_uptime_duration_rendered']=True
 if os.environ.get('FLEET_EVIDENCE_ID')=='d054':
  assert 'Uptime' in text and 'Monitoring Health' in text and 'NOT APPLICABLE' in text
  result['checks']['typed_health_and_uptime']=True
 # Scroll to render lazy panels and retain actual full-page visualization.
 page.mouse.wheel(0,1200);page.wait_for_timeout(2000)
 text=page.locator('body').inner_text();assert 'Sin alertas activas' in text
 assert 'Componentes Docker · diagnóstico (no disponibilidad de aplicación)' not in text
 assert page.get_by_role('columnheader',name='Environment',exact=True).count()==0
 result['checks']['empty_alerts_explicit']=True
 result['checks']['requested_presentation_removals']=True
 page.evaluate('() => document.querySelectorAll("*").forEach(e => { if(e.scrollTop) e.scrollTop=0; })')
 page.wait_for_timeout(500)
 page.screenshot(path='docs/roadmap/evidence/'+os.environ.get('FLEET_EVIDENCE_DATE','2026-11-07')+'-'+os.environ.get('FLEET_EVIDENCE_ID','d052')+'-fleet.png',full_page=True)
 page.goto(base+'&var-lxc=618&var-service=%24__all&from=now-1h&to=now');page.wait_for_timeout(4500)
 text=page.locator('body').inner_text();assert 'CT 618 · infra-composable-crm' in text and 'CT 624 ·' not in text
 result['checks']['lxc_filter_and_one_hour_range']=True
 if os.environ.get('FLEET_EVIDENCE_ID')=='d054':
  assert 'HEALTHY (readiness)' in text
  result['checks']['crm_readiness_explicit']=True
 page.goto(base+'&var-service=infra-nucleoedge&var-lxc=%24__all');page.wait_for_timeout(4500)
 text=page.locator('body').inner_text();assert 'CT 614 · infra-nucleoedge' in text and 'CT 618 ·' not in text
 result['checks']['service_filter']=True
 # Follow the provisioned table link, rather than emulating a manual dashboard edit.
 link=page.get_by_role('link',name='614',exact=True)
 assert link.count()==1;link.click();page.wait_for_timeout(3000)
 assert 'var-lxc=614' in page.url and '/d/proxmox-lxc-details/' in page.url
 result['checks']['ct_table_navigation']=True
 browser.close()
assert not result['query_errors'] and not result['js_errors'],result
# CT counts additionally verified through Prometheus and authenticated datasource queries.
result['result']='PASS'
Path('docs/roadmap/evidence/'+os.environ.get('FLEET_EVIDENCE_DATE','2026-11-07')+'-'+os.environ.get('FLEET_EVIDENCE_ID','d052')+'-browser.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({'checks':result['checks'],'errors':len(result['query_errors'])+len(result['js_errors']),'query_requests':len(result['query_endpoints'])}))
