#!/usr/bin/env python3
"""Captura metadatos públicos sin descargar pesos ni usar tokens."""
import json, urllib.request, pathlib, datetime
out={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'repos':{},'releases':{}}
def get(url):
 with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'infra-preflight'}),timeout=60) as r:return json.load(r)
for repo in ['unsloth/Qwen3.6-35B-A3B-GGUF','unsloth/gemma-4-26B-A4B-it-qat-GGUF','google/gemma-4-26B-A4B-it-qat-q4_0-gguf']:
 try:
  info=get('https://huggingface.co/api/models/'+repo)
  files=get('https://huggingface.co/api/models/'+repo+'/tree/main?recursive=true&limit=1000')
  out['repos'][repo]={'revision':info.get('sha'),'files':files}
 except Exception as e:out['repos'][repo]={'error':str(e)}
for repo in ['ggml-org/llama.cpp','open-webui/open-webui','searxng/searxng']:
 try:
  r=get('https://api.github.com/repos/'+repo+'/releases/latest')
  out['releases'][repo]={k:r.get(k) for k in ['tag_name','target_commitish','published_at','html_url']}
 except Exception as e:out['releases'][repo]={'error':str(e)}
p=pathlib.Path('docs/roadmap/evidence/ia-chat-a-2026-11-13/public.json');p.write_text(json.dumps(out,indent=2)+'\n')
for repo,r in out['repos'].items():
 print(repo,r.get('revision',r.get('error')))
 for f in r.get('files',[]):
  if f.get('type')=='file': print(f['path'],f.get('size'),f.get('lfs',{}).get('oid'))
print(json.dumps(out['releases'],indent=2))
