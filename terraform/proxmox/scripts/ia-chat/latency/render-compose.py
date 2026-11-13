#!/usr/bin/env python3
"""Renderiza solo parámetros de rendimiento de Compose desde perfil canónico público."""
import json,yaml
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];p=ROOT/'services/infra-webui/config/chat-performance.json';profile=json.loads(p.read_text());dest=ROOT/'services/infra-webui/compose/docker-compose.yml';old=dest.read_text();d=yaml.safe_load(old);env=d['services']['open-webui']['environment']
params=json.loads(env['DEFAULT_MODEL_PARAMS']);params.update({'system':profile['system'],'function_calling':profile['function_calling']});params.setdefault('custom_params',{})['cache_prompt']=profile['cache_prompt'];env['DEFAULT_MODEL_PARAMS']=json.dumps(params,ensure_ascii=False)
meta=json.loads(env['DEFAULT_MODEL_METADATA']);meta.setdefault('capabilities',{})['builtin_tools']=profile['builtin_tools'];env['DEFAULT_MODEL_METADATA']=json.dumps(meta)
for key,value in {'ENABLE_TITLE_GENERATION':profile['title_generation'],'ENABLE_SEARCH_QUERY_GENERATION':profile['search_query_generation'],'ENABLE_TAGS_GENERATION':False,'ENABLE_FOLLOW_UP_GENERATION':False,'ENABLE_AUTOCOMPLETE_GENERATION':False,'ENABLE_RETRIEVAL_QUERY_GENERATION':False}.items():env[key]=str(value).lower()
body=yaml.safe_dump(d,sort_keys=False,allow_unicode=True)
if body!=old:dest.write_text(body)
print(json.dumps({'compose_changed':body!=old,'profile':str(p.relative_to(ROOT))}))
