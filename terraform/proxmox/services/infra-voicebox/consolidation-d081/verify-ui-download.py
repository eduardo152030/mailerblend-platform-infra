"""Read history and export the completed D081 WAV through UI; never regenerate."""
from pathlib import Path
import json,hashlib,re
from playwright.sync_api import sync_playwright
p=Path.home()/'.local/share/mailerblend-recovery/voicebox-d081';wav=json.loads((p/'wav.json').read_text())
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True);page=browser.new_page()
 page.goto('http://192.168.1.127:17493/',wait_until='networkidle')
 latest=page.get_by_role('button',name=re.compile(r'^Sample from Eduardo — Mi Voz, 0:57,')).first;assert latest.is_visible()
 page.get_by_role('button',name='Actions',exact=True).first.click()
 with page.expect_download(timeout=30000) as pending:page.get_by_role('menuitem',name='Export Audio',exact=True).click()
 download=pending.value;target=p/'UI-export-D081.wav';download.save_as(target);target.chmod(0o600)
 sha=hashlib.sha256(target.read_bytes()).hexdigest();assert sha==wav['sha256']
 result={'history_new_sample_visible':True,'ui_export_downloaded':True,'suggested_filename':download.suggested_filename,'same_sha256_as_api':True,'sha256':sha,'generate_posts':0}
 (p/'ui-final.json').write_text(json.dumps(result));browser.close();print(json.dumps(result))
