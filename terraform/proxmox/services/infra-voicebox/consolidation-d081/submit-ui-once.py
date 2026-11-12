"""One literal D081 UI submission; fail closed, no transport or model retries."""
from pathlib import Path
import hashlib,json
from playwright.sync_api import sync_playwright
p=Path.home()/'.local/share/mailerblend-recovery/voicebox-d081'
assert json.loads((p/'preflight-final.json').read_text())['predictive_preflight']['passed']
assert not (p/'submission-started.json').exists(),'Inspect existing attempt; never resubmit'
text=(p/'text.txt').read_text();assert len(text)==1059 and hashlib.sha256(text.encode()).hexdigest()=='a29d9c360200ef3277ea5a6f7ccbeff03cf763deef9df32373fb7ee7b10c413c'
count=0
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True);page=browser.new_page(viewport={'width':1440,'height':1100})
 def gate(route):
  global count
  if route.request.method!='POST':route.continue_();return
  count+=1
  body=route.request.post_data_json
  assert count==1 and body['text']==text and body['profile_id']=='1fd00418-2a79-4178-883f-af6c3f5e07ee'
  assert body['model_size']=='0.6B' and body['engine']=='qwen' and body['language']=='es' and not body.get('personality')
  assert not body.get('instruct') and body.get('seed') in [None,42]
  (p/'request.private.json').write_text(json.dumps(body));(p/'request.private.json').chmod(0o600)
  route.continue_()
 page.route('**/generate',gate)
 page.goto('http://192.168.1.127:17493/',wait_until='networkidle')
 page.locator('select').nth(0).select_option('es');page.locator('select').nth(1).select_option('qwen:0.6B')
 page.get_by_placeholder('Generate speech using Eduardo — Mi Voz…').fill(text)
 assert page.get_by_placeholder('Generate speech using Eduardo — Mi Voz…').input_value()==text
 button=page.get_by_role('button',name='Generate speech',exact=True);assert button.is_enabled()
 page.screenshot(path=str(p/'ui-before-submit.private.png'),full_page=True)
 with (p/'submission-started.json').open('x') as f:json.dump({'ui_click_once':True,'chars':len(text),'sha256':hashlib.sha256(text.encode()).hexdigest()},f)
 with page.expect_response(lambda r:r.url.endswith('/generate') and r.request.method=='POST',timeout=30000) as response:button.click()
 r=response.value;assert r.status==200,r.status;data=r.json();(p/'submission.json').write_text(json.dumps(data));(p/'submission.json').chmod(0o600)
 assert count==1
 (p/'ui-submission.json').write_text(json.dumps({'single_ui_generate_click':True,'post_count':count,'text_exact':True,'chars':len(text),'model_size':'0.6B','language':'es','job_id':data['id'],'seed_request':json.loads((p/'request.private.json').read_text()).get('seed'),'effective_worker_seed':42}))
 page.screenshot(path=str(p/'ui-running.private.png'),full_page=True);browser.close()
 print(json.dumps({'id':data['id'],'status':data['status'],'single_ui_submit':True}))
