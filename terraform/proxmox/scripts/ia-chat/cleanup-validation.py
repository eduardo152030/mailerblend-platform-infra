#!/usr/bin/env python3
"""Retira exclusivamente cuenta/Knowledge/credenciales sintéticas IA-CHAT.
No elimina cuentas reales. Conserva modelos globales y valida JWT revocado.
"""
import importlib.util,json,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];s=importlib.util.spec_from_file_location('stage',ROOT/'scripts/phase6-stage-a.py');t=importlib.util.module_from_spec(s);s.loader.exec_module(t)
print(t.remote(631,['python3','/root/webui-check.py','rag-clean']).decode())
t.py(631,"import pathlib,json,os;p=pathlib.Path('/root/ia-validation-auth.json');d=json.loads(p.read_text());assert d['email']=='ia-chat-validation@example.com';q=pathlib.Path('/opt/ia-chat/data/ia-validation-auth.json');q.write_text(json.dumps({'id':d['id']}));q.chmod(0o600)")
t.remote(631,['sh','-c','cd /opt/ia-chat && docker compose stop open-webui'])
try:
 result=t.remote(631,['sh','-c','cd /opt/ia-chat && docker compose run --rm -T --no-deps --entrypoint python open-webui -'],(ROOT/'scripts/ia-chat/cleanup-test-user.py').read_bytes());assert b'Fixture de usuario eliminada' in result
finally:t.remote(631,['sh','-c','cd /opt/ia-chat && docker compose up -d --no-deps open-webui'])
t.remote(631,['python3','/root/wait-webui.py'])
code="""import pathlib,json,urllib.request,urllib.error,sqlite3
p=pathlib.Path('/root/ia-validation-auth.json');d=json.loads(p.read_text());assert d['email']=='ia-chat-validation@example.com'
req=urllib.request.Request('http://127.0.0.1:3000/api/v1/auths/',headers={'Authorization':'Bearer '+d['token']})
try:urllib.request.urlopen(req);raise AssertionError('JWT still accepted')
except urllib.error.HTTPError as e:assert e.code==401,e.code
c=sqlite3.connect('/opt/ia-chat/data/webui.db');assert c.execute('select count(*) from user').fetchone()[0]==0;assert c.execute('select count(*) from knowledge').fetchone()[0]==0;assert c.execute('pragma quick_check').fetchone()[0]=='ok'
p.unlink();print(json.dumps({'fixture_removed':True,'users':0,'knowledge':0,'old_jwt':401,'sqlite':'ok','owner_first_admin_ready':True}))
"""
result=json.loads(t.py(631,code));(ROOT/'docs/roadmap/evidence/ia-chat-2026-11-13/fixture-cleanup-final.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
