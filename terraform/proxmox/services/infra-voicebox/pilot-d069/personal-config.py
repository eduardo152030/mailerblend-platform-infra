#!/usr/bin/env python3
"""Idempotent D069 runtime settings for the actual sole owner; never create a voice."""
import json,urllib.request,socket,time
from pathlib import Path
assert socket.gethostname()=='infra-voicebox'
BASE='http://192.168.1.127:17493';OWNER='1fd00418-2a79-4178-883f-af6c3f5e07ee'
def api(path,value=None,method=None):
 req=urllib.request.Request(BASE+path,data=None if value is None else json.dumps(value).encode(),headers={'Content-Type':'application/json'},method=method)
 with urllib.request.urlopen(req,timeout=15) as r:return json.load(r)
for _ in range(45):
 try:
  if api('/health')['status']=='healthy':break
 except Exception:pass
 time.sleep(1)
else:raise RuntimeError('Voicebox unhealthy; do not change config')
profiles=api('/profiles');assert len(profiles)==1 and profiles[0]['id']==OWNER
refs=api('/profiles/'+OWNER+'/samples');assert refs and all(x['profile_id']==OWNER for x in refs)
changes=[];p=profiles[0]
if p.get('default_engine')!='qwen' or p['language']!='es':
 props=api('/openapi.json')['components']['schemas']['VoiceProfileCreate']['properties'];body={k:v for k,v in p.items() if k in props};body.update({'default_engine':'qwen','language':'es'});api('/profiles/'+OWNER,body,'PUT');changes.append('owner_defaults')
if api('/settings/generation')['max_chunk_chars']!=200:api('/settings/generation',{'max_chunk_chars':200},'PUT');changes.append('chunk_default')
source=Path('/opt/voicebox/voice-identities.yml');target=Path('/srv/voicebox/data/voice-identities.yml')
if not target.exists() or target.read_bytes()!=source.read_bytes():target.write_bytes(source.read_bytes());changes.append('identity_catalog')
target.chmod(0o600)
print(json.dumps({'result':'PASS','changes':changes,'profile_id':OWNER,'profiles':1,'references':len(refs)}))
