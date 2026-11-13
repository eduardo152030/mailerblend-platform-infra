#!/usr/bin/env python3
"""Dentro631: API admin versionada, conserva valores ajenos y no imprime secretos."""
import pathlib,json,urllib.request,sqlite3
cred=json.loads(pathlib.Path('/root/ia-validation-auth.json').read_text());base='http://127.0.0.1:3000/api/v1/audio'
def req(path,data=None):
 r=urllib.request.Request(base+path,data=json.dumps(data).encode() if data is not None else None,headers={'Authorization':'Bearer '+cred['token'],'Content-Type':'application/json'})
 with urllib.request.urlopen(r,timeout=1800) as response:return json.load(response)
config=req('/config');before=config['stt']['WHISPER_MODEL'];config['stt']['WHISPER_MODEL']='base';config['stt']['ENGINE']='';config.pop('realtime',None)
response=req('/config/update',config) if before!='base' else req('/config');assert response['stt']['WHISPER_MODEL']=='base' and response['stt']['ENGINE']==''
actual=json.loads(sqlite3.connect('/opt/ia-chat/data/webui.db').execute("select value from config where key='audio.stt.whisper_model'").fetchone()[0]);assert actual=='base'
print(json.dumps({'previous_actual_model':before,'actual_model':actual,'engine':'local','verified_admin_api':True,'verified_persistent_db':True}))
