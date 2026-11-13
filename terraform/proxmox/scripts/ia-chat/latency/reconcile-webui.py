#!/usr/bin/env python3
"""Dentro de WebUI: cambios graduales por API oficial, preservando configuración ajena.
Etapas a/b/c/g. Sin credenciales stdout. Usa fixture privada únicamente.
"""
import json,pathlib,urllib.request,sys,os
AUTH=json.loads(pathlib.Path('/app/backend/data/.ia-latency-auth.json').read_text());BASE='http://127.0.0.1:8080'
def call(path,data=None):
 req=urllib.request.Request(BASE+path,data=json.dumps(data).encode() if data is not None else None,headers={'Authorization':'Bearer '+AUTH['token'],'Content-Type':'application/json'})
 with urllib.request.urlopen(req,timeout=120) as r:return json.load(r)
PROFILE=json.loads(os.environ['IA_CHAT_PROFILE']);SYSTEM=PROFILE['system']
stage=sys.argv[1];before=call('/api/v1/configs/export');updates={};model_writes=0
if stage=='a':
 for model in ['gemma-4-26b','qwen3.6-35b']:
  old=call('/api/v1/models/model?id='+model);form=json.loads(json.dumps({k:old[k] for k in ['id','base_model_id','name','meta','params'] if k in old}));form['meta'].setdefault('capabilities',{})['builtin_tools']=PROFILE['builtin_tools'];form['params']['function_calling']=PROFILE['function_calling']
  if form!= {k:old[k] for k in form}:call('/api/v1/models/model/update',form);model_writes+=1
 defaults=json.loads(json.dumps(before.get('models.default_params') or {}));defaults['function_calling']=PROFILE['function_calling'];updates['models.default_params']=defaults
elif stage=='b':updates={'task.title.enable':False,'task.tags.enable':False,'task.follow_up.enable':False,'task.autocomplete.enable':False,'task.query.retrieval.enable':False}
elif stage=='c':updates={'task.query.search.enable':False}
elif stage=='e':
 defaults=json.loads(json.dumps(before.get('models.default_params') or {}));defaults.setdefault('custom_params',{})['cache_prompt']=PROFILE['cache_prompt'];updates['models.default_params']=defaults
 for model in ['gemma-4-26b','qwen3.6-35b']:
  old=call('/api/v1/models/model?id='+model);form=json.loads(json.dumps({k:old[k] for k in ['id','base_model_id','name','meta','params'] if k in old}));form['params'].setdefault('custom_params',{})['cache_prompt']=PROFILE['cache_prompt']
  if form!={k:old[k] for k in form}:call('/api/v1/models/model/update',form);model_writes+=1
elif stage=='g':
 defaults=json.loads(json.dumps(before.get('models.default_params') or {}));defaults['system']=SYSTEM;updates['models.default_params']=defaults
 for model in ['gemma-4-26b','qwen3.6-35b']:
  old=call('/api/v1/models/model?id='+model);form=json.loads(json.dumps({k:old[k] for k in ['id','base_model_id','name','meta','params'] if k in old}));form['params']['system']=SYSTEM
  if form!={k:old[k] for k in form}:call('/api/v1/models/model/update',form);model_writes+=1
else:raise SystemExit('Unknown stage')
changes={k:v for k,v in updates.items() if before.get(k)!=v};after=call('/api/v1/configs/import',{'config':{**before,**updates}}) if changes else before;assert all(after.get(k)==v for k,v in before.items() if k not in updates)
print(json.dumps({'stage':stage,'keys':list(updates),'changed_config_keys':list(changes),'model_writes':model_writes,'unrelated_config_preserved':True}))
