#!/usr/bin/env python3
"""631: corrige claves persistidas por API oficial, conserva el resto sin imprimir secretos."""
import json,pathlib,urllib.request,sys
cred=json.loads(pathlib.Path('/root/ia-validation-auth.json').read_text());base='http://127.0.0.1:3000/api/v1/configs'
def call(path,data=None):
 r=urllib.request.Request(base+path,data=json.dumps(data).encode() if data is not None else None,headers={'Authorization':'Bearer '+cred['token'],'Content-Type':'application/json'})
 with urllib.request.urlopen(r,timeout=60) as response:return json.load(response)
before=call('/export');updates={'audio.stt.whisper_model':sys.argv[1],'ui.default_interface_settings':{'webSearch':False,'responseAutoPlayback':False},'ui.visibility':{'settings.text_to_speech_engine':False}}
desired={**before,**updates};after=call('/import',{'config':desired});assert after==desired
print(json.dumps({'updated_keys':list(updates),'whisper_effective':after['audio.stt.whisper_model'],'unrelated_config_unchanged':all(after.get(k)==v for k,v in before.items() if k not in updates)}))
