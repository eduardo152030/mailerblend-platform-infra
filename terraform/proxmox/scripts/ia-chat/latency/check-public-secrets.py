#!/usr/bin/env python3
"""Busca claves vivas y el JWT técnico en los artefactos propios; nunca los imprime."""
import importlib.util,json,yaml
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sp=importlib.util.spec_from_file_location('stage',ROOT/'scripts/phase6-stage-a.py');t=importlib.util.module_from_spec(sp);sp.loader.exec_module(t)
values=[t.remote(630,['cat','/etc/llama/api.key']).strip()]
for line in t.remote(631,['cat','/opt/ia-chat/secrets.env']).decode().splitlines():
 if '=' in line and not line.startswith('#'):
  v=line.split('=',1)[1].strip().strip('\"\'').encode()
  if len(v)>=16:values.append(v)
values.append(yaml.safe_load(t.remote(631,['cat','/opt/ia-chat/searxng/settings.yml']))['server']['secret_key'].encode())
code="import pathlib,json;p=pathlib.Path('/opt/ia-chat/data/.ia-latency-auth.json');print(json.dumps({'token':json.loads(p.read_text())['token'] if p.exists() else None}))"
fixture=json.loads(t.py(631,code))['token']
if fixture:values.append(fixture.encode())
files=[]
for folder in ['scripts/ia-chat','services/infra-llm','services/infra-webui','docs/roadmap/evidence/ia-chat-latency-2026-11-13']:
 files.extend(p for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
files.extend([ROOT/'docs/roadmap/IA-CHAT-LATENCY-2026-11-13.md',ROOT/'services/ia-local/README.md'])
found=[str(p.relative_to(ROOT)) for p in files if any(v and v in p.read_bytes() for v in values)];assert not found,'Live secrets found in '+str(found)
print(json.dumps({'result':'PASS','files_scanned':len(files),'live_secret_matches':0,'technical_jwt_checked':bool(fixture)}))
