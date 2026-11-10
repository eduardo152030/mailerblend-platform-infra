#!/usr/bin/env python3
"""D060 authenticated visual/navigation validation of both provisioned dashboards."""
import base64,importlib.util,json,re,time
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('g',ROOT/'scripts/deploy-fleet-dashboard.py');g=importlib.util.module_from_spec(s);s.loader.exec_module(g)
user,password=base64.b64decode(g.credentials()['Authorization'].split(' ',1)[1]).decode().split(':',1)
result={'timestamp_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'checks':{},'query_errors':[],'js_errors':[],'table_frames':[],'query_endpoints':[]}
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True);page=browser.new_page(viewport={'width':1920,'height':1500});page.on('pageerror',lambda e:result['js_errors'].append(str(e)))
 selected={'ct':None}
 def response(r):
  if '/api/ds/query' not in r.url and '/api/v1/query' not in r.url:return
  result['query_endpoints'].append(r.url.split('?')[0])
  try:
   d=r.json()
   if d.get('status')=='error':result['query_errors'].append({'ct':selected['ct'],'error':d.get('error')})
   if isinstance(d.get('data'),dict) and isinstance(d['data'].get('result'),list):
    ids={str(row['metric']['ct_id']) for row in d['data']['result'] if row.get('metric',{}).get('ct_id')}
    if ids:
     result['table_frames'].append({'ct':selected['ct'],'ct_ids':sorted(ids),'source':'Grafana Prometheus proxy'})
     if selected['ct'] and ids!={selected['ct']}:result['query_errors'].append({'cross_ct':sorted(ids),'selected':selected['ct']})
   for ref,v in d.get('results',{}).items():
    if v.get('error'):result['query_errors'].append({'ct':selected['ct'],'ref':ref,'error':v['error']})
    for frame in v.get('frames',[]):
     fields=frame['schema']['fields'];values=frame.get('data',{}).get('values',[])
     for field in fields:
      labels=field.get('labels',{})
      if labels.get('ct_id'):
       ids={str(labels['ct_id'])};result['table_frames'].append({'ct':selected['ct'],'ref':ref,'ct_ids':sorted(ids),'source':'field labels'})
       if selected['ct'] and ids!={selected['ct']}:result['query_errors'].append({'cross_ct':sorted(ids),'selected':selected['ct']})
     for i,field in enumerate(fields):
      if field['name']=='ct_id' and values:
       ids=set(str(x) for x in values[i]);result['table_frames'].append({'ct':selected['ct'],'ref':ref,'ct_ids':sorted(ids)})
       if selected['ct'] and ids and ids!={selected['ct']}:result['query_errors'].append({'cross_ct':sorted(ids),'selected':selected['ct']})
  except Exception:pass
 page.on('response',response)
 page.goto(g.URL+'/login');page.locator('input[name="user"]').fill(user);page.locator('input[name="password"]').fill(password);page.get_by_role('button',name='Log in',exact=True).click();page.wait_for_timeout(1200)
 fleet=g.URL+'/d/proxmox-lxc-fleet/proxmox-lxc-fleet-overview?theme=dark'
 details=g.URL+'/d/proxmox-lxc-details/proxmox-lxc-details?theme=dark'
 selected['ct']=None;page.goto(fleet);page.wait_for_timeout(4500)
 text=page.locator('body').inner_text();assert '17' in text and 'Uptime' in text and 'HEALTHY' in text
 assert page.get_by_role('columnheader',name='Environment',exact=True).count()==0
 assert 'Componentes Docker · diagnóstico (no disponibilidad de aplicación)' not in text
 result['checks']['fleet_17_health_real_uptime_and_removals']=True
 page.screenshot(path=str(ROOT/'docs/roadmap/evidence/2026-11-09-d060-fleet.png'),full_page=True)
 # Take the actual table data link and check the selected CT survives navigation.
 page.goto(fleet+'&var-lxc=614&var-service=%24__all&from=now-1h&to=now');page.wait_for_timeout(3500)
 selected['ct']='614';page.get_by_role('link',name='614',exact=True).click();page.wait_for_timeout(4500)
 assert '/d/proxmox-lxc-details/' in page.url and 'var-lxc=614' in page.url and 'from=' in page.url
 result['checks']['fleet_to_details_ct_and_time']=True
 for ct,service,other in [('614','infra-nucleoedge','infra-mailerblend-edge'),('615','infra-mailerblend-edge','infra-nucleoedge'),('618','infra-composable-crm','infra-nucleoedge'),('613','infra-hola','infra-nucleoedge')]:
  selected['ct']=ct;page.goto(details+'&var-lxc='+ct+'&from=now-1h&to=now');page.wait_for_timeout(4000)
  body=page.locator('body').inner_text();assert service in body and other not in body,(ct,'service isolation')
  assert 'CPU asignada' in body and 'RAM asignada' in body and 'Disco raíz' in body
  assert 'Uptime' in body and 'HEALTHY' in body
  if ct=='613':assert 'NOT APPLICABLE' in body
  if ct=='618':assert 'HEALTHY (readiness)' in body
  # Render lazy panels by moving through each semantic section.
  for title in ['Red del LXC · recepción / transmisión','Docker · contenedores activos del LXC','Monitoring · targets y frescura','Alertas activas · CT '+ct,'Documentación · ficha local existente']:
   loc=page.get_by_text(title,exact=True)
   for _ in range(12):
    if loc.count():break
    page.mouse.wheel(0,850);page.wait_for_timeout(350)
   loc.scroll_into_view_if_needed(timeout=5000);page.wait_for_timeout(1000)
   if title.startswith('Docker'):
    assert page.get_by_role('columnheader',name='Healthcheck',exact=True).count()==1
    assert page.get_by_role('columnheader',name='RAM working set',exact=True).count()==1
   if title.startswith('Monitoring'):
    assert page.get_by_role('columnheader',name='Edad fuente (s)',exact=True).count()==1
   if ct=='614' and title in ['Docker · contenedores activos del LXC','Monitoring · targets y frescura']:
    page.screenshot(path=str(ROOT/('docs/roadmap/evidence/2026-11-09-d060-section-'+('docker' if title.startswith('Docker') else 'monitoring')+'.png')))
  text=page.locator('body').inner_text()
  result['checks']['details_'+ct+'_scoped_panels']=True
  if ct in ['614','618']:
   page.evaluate('() => document.querySelectorAll("*").forEach(e => { if(e.scrollTop) e.scrollTop=0; })');page.wait_for_timeout(300)
   page.screenshot(path=str(ROOT/('docs/roadmap/evidence/2026-11-09-d060-details-'+ct+'.png')),full_page=True)
 # The reverse link is the real provisioned dashboard link.
 selected['ct']='614';page.goto(details+'&var-lxc=614');page.wait_for_timeout(2500)
 link=page.get_by_role('link',name='← Fleet Overview',exact=False);assert link.count()==1
 link.click();page.wait_for_timeout(3000)
 assert '/d/proxmox-lxc-fleet/' in page.url and 'var-lxc=614' in page.url
 result['checks']['details_to_fleet_preserves_ct']=True
 browser.close()
assert not result['query_errors'] and not result['js_errors'],result
assert result['table_frames'],('No real datasource frames observed',sorted(set(result['query_endpoints'])))
result['result']='PASS';(ROOT/'docs/roadmap/evidence/2026-11-09-d060-browser.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n');print(json.dumps({'checks':result['checks'],'errors':0,'frames':len(result['table_frames'])}))
