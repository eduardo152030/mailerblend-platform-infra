#!/usr/bin/env python3
"""D063: UI real y selección dinámica627 en dashboards existentes; solo lectura."""
import argparse,base64,importlib.util,json,time
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'docs/roadmap/evidence'
ap=argparse.ArgumentParser();ap.add_argument('--final',action='store_true');ap.add_argument('--prefix');args=ap.parse_args();PREFIX=args.prefix or ('2026-11-10-d063-final-' if args.final else '2026-11-10-d063-')
s=importlib.util.spec_from_file_location('g',ROOT/'scripts/deploy-fleet-dashboard.py');g=importlib.util.module_from_spec(s);s.loader.exec_module(g)
user,password=base64.b64decode(g.credentials()['Authorization'].split(' ',1)[1]).decode().split(':',1)
result={'checks':{},'query_errors':[],'ct_id':627}
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True);page=browser.new_page(viewport={'width':1920,'height':1400})
 page.goto('http://192.168.1.127:17493/',wait_until='domcontentloaded');page.wait_for_function("document.body.innerText.includes('Voicebox')",timeout=15000);page.wait_for_timeout(2000)
 text=page.locator('body').inner_text();assert len(text)>50 and ('Voicebox' in text or 'Voice' in text or 'Generate' in text)
 page.screenshot(path=str(OUT/(PREFIX+'voicebox.png')),full_page=True);result['checks']['voicebox_web_rendered']=True
 page.goto(g.URL+'/login');page.locator('input[name="user"]').fill(user);page.locator('input[name="password"]').fill(password);page.get_by_role('button',name='Log in',exact=True).click();page.wait_for_timeout(1500)
 def response(r):
  if '/api/ds/query' not in r.url:return
  try:
   for ref,v in r.json().get('results',{}).items():
    if v.get('error'):result['query_errors'].append({'ref':ref,'error':v['error']})
  except Exception:pass
 page.on('response',response)
 for uid,slug,label in [('proxmox-lxc-fleet','proxmox-lxc-fleet-overview','fleet'),('proxmox-lxc-details','proxmox-lxc-details','details')]:
  page.goto(g.URL+'/d/'+uid+'/'+slug+'?var-lxc=627&var-service=%24__all&from=now-15m&to=now');page.wait_for_timeout(5000)
  text=page.locator('body').inner_text();assert '627' in text and 'infra-voicebox' in text,(label,text[:200])
  assert 'HEALTHY' in text or label=='details'
  page.screenshot(path=str(OUT/(PREFIX+label+'-627.png')),full_page=True);result['checks'][label+'_627_dynamic_selection']=True
 assert not result['query_errors'];browser.close()
(OUT/(PREFIX+'browser.json')).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
