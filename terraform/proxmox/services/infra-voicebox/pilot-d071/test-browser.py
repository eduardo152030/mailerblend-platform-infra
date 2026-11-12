#!/usr/bin/env python3
"""Actual UI submit/play/export/history for trading fixture; no personal references published."""
from pathlib import Path
import json,time,urllib.request,hashlib,re
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[3];PRIVATE=Path.home()/'.local/share/mailerblend-recovery/voicebox-d071';text=json.loads((Path(__file__).parent/'test-texts.json').read_text())['trading'];BASE='http://192.168.1.127:17493'
def history(ident):
 with urllib.request.urlopen(BASE+'/history/'+ident,timeout=10) as r:return json.load(r)
result={'status':'IN_PROGRESS'}
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True);page=browser.new_page(viewport={'width':1600,'height':1200},accept_downloads=True);errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto(BASE,wait_until='domcontentloaded');page.wait_for_timeout(1500)
  assert 'OpenVoice' in ' '.join(page.get_by_role('combobox').all_text_contents())
  page.get_by_placeholder('Generate speech using Eduardo — Mi Voz…').fill(text);t=time.monotonic()
  with page.expect_response(lambda r:r.request.method=='POST' and r.url.endswith('/generate'),timeout=15000) as response:page.get_by_role('button',name='Generate speech',exact=True).click()
  r=response.value;assert r.status==200;g=r.json();ident=g['id'];result['generation_id']=ident;(PRIVATE/'browser-trading-request.json').write_text(json.dumps({'id':ident,'start_utc_seconds':time.time()})+'\n')
  while time.monotonic()-t<220:
   g=history(ident)
   if g['status'] in ['completed','failed']:break
   page.wait_for_timeout(1000)
  assert g['status']=='completed',g.get('error','UI generation timeout')
  result['generation_seconds']=time.monotonic()-t;result['audio_seconds']=g['duration'];page.wait_for_timeout(1200)
  page.evaluate("text=>{let e=[...document.querySelectorAll('textarea')].find(e=>e.readOnly&&e.value===text);if(!e)throw Error('History row missing');e.closest('div.border.rounded-md.bg-card').setAttribute('data-d071-row','true')}",text)
  row=page.locator('[data-d071-row=true]');row.scroll_into_view_if_needed();row.get_by_role('button',name='Actions',exact=True).click();print('MENU',page.get_by_role('menuitem').all_text_contents(),flush=True)
  page.get_by_role('menuitem',name=re.compile('^Play',re.I)).click();page.wait_for_timeout(1500)
  result['playback_ui_playing']=row.get_by_role('button',name=re.compile('Playing')).count()>0
  assert result['playback_ui_playing'],'Audio did not enter playing state'
  row.get_by_role('button',name='Actions',exact=True).click()
  menu=page.get_by_role('menuitem').filter(has_text=re.compile('Export Audio|Export audio|Download',re.I)).filter(has_not_text=re.compile('MP3',re.I)).first
  with page.expect_download(timeout=15000) as download:menu.click()
  file=PRIVATE/'ui-trading.wav';download.value.save_as(str(file));file.chmod(0o600)
  with urllib.request.urlopen(BASE+'/audio/'+ident) as r:raw=r.read()
  assert file.read_bytes()==raw;assert not errors
  result.update(status='PASS',profile_visible=True,engine_visible='openvoice',submitted_from_ui=True,history_visible=True,download_bytes_identical=True,page_errors=errors,audio_url=BASE+'/audio/'+ident,sha256=hashlib.sha256(raw).hexdigest());browser.close()
except BaseException as e:result.update(status='FAIL',reason=str(e));raise
finally:(PRIVATE/'browser-trading.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
