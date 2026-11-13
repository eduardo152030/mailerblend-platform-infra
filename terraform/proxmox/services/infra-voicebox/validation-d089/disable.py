"""Fail closed after a validation failure; preserve code, jobs and all data."""
from pathlib import Path
import json,os,urllib.request,time
p=Path('/opt/voicebox-qwen-627/chatterbox-release.json');back=Path('/mnt/storage/d089/release-before-disable.json');assert not back.exists();back.write_bytes(p.read_bytes());back.chmod(0o600)
r=json.loads(p.read_text());r.update(enabled=False,reason='D089 validation stopped: observer network route failed; no English trial; evidence preserved')
tmp=p.with_suffix('.d089-disable');tmp.write_text(json.dumps(r,indent=2));tmp.chmod(0o600);os.replace(tmp,p)
for _ in range(30):
 caps=json.load(urllib.request.urlopen('http://192.168.1.127:17493/tts-capabilities',timeout=10))
 if caps['qwen']['ready'] and not caps['chatterbox']['ready']:break
 time.sleep(.5)
else:raise RuntimeError('Failed to confirm disabled CB/Qwen ready')
health=json.load(urllib.request.urlopen('http://192.168.1.127:17493/health',timeout=10));assert health['status']=='healthy'
print(json.dumps({'chatterbox_disabled':True,'qwen_es_en_ready':caps['qwen']['ready'] and caps['qwen']['languages']==['es','en'],'voicebox_healthy':True,'no_service_restart':True}))
