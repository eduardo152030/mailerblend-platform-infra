#!/usr/bin/env python3
"""Compara secretos vivos con artefactos propios sin imprimirlos."""
import importlib.util,yaml,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];s=importlib.util.spec_from_file_location('stage',ROOT/'scripts/phase6-stage-a.py');t=importlib.util.module_from_spec(s);s.loader.exec_module(t)
secrets=[t.remote(630,['cat','/etc/llama/api.key']).strip()]
env=t.remote(631,['cat','/opt/ia-chat/secrets.env']).decode()
for line in env.splitlines():
 if line and not line.startswith('#') and '=' in line:
  value=line.split('=',1)[1].strip().strip('\"\'').encode()
  if len(value)>=16:secrets.append(value)
settings=yaml.safe_load(t.remote(631,['cat','/opt/ia-chat/searxng/settings.yml']));secrets.append(settings['server']['secret_key'].encode())
findings=[];count=0
for folder in ['scripts/ia-chat','services/ia-local','services/infra-llm','services/infra-webui','docs/roadmap/evidence/ia-chat-2026-11-13']:
 for p in (ROOT/folder).rglob('*'):
  if p.is_file() and '__pycache__' not in p.parts:
   count+=1
   if any(value and value in p.read_bytes() for value in secrets):findings.append(str(p.relative_to(ROOT)))
assert not findings,'Live secret found in files: '+str(findings)
print(json.dumps({'result':'PASS','files_scanned':count,'live_secret_matches':0}))
