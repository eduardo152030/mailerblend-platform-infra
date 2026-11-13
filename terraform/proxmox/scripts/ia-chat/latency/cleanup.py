#!/usr/bin/env python3
"""Operador local: limpia fixtures sin parar WebUI y comprueba propietarios originales."""
import importlib.util,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sp=importlib.util.spec_from_file_location('stage',ROOT/'scripts/phase6-stage-a.py');t=importlib.util.module_from_spec(sp);sp.loader.exec_module(t)
# The old credential path was created only by this task; never remove arbitrary auth files.
check=json.loads(t.py(631,"import pathlib,json;p=pathlib.Path('/root/ia-validation-auth.json');print(json.dumps({'exists':p.exists(),'email':json.loads(p.read_text()).get('email') if p.exists() else None}))"))
if check['exists']:
 assert check['email']=='ia-latency-validation@example.com'
 fixture=json.loads(t.py(631,"import pathlib,json;p=pathlib.Path('/root/ia-latency-rag.json');print(json.dumps(json.loads(p.read_text()).get('rag_fixture',{}) if p.exists() else {}))"))
 if fixture and not fixture.get('deleted'):t.remote(631,['env','IA_RESULT_PATH=/root/ia-latency-rag.json','python3','/root/webui-check.py','rag-clean'])
 result=t.remote(631,['docker','exec','-i','ia-chat-open-webui-1','python','-'],(ROOT/'scripts/ia-chat/latency/cleanup-fixture.py').read_bytes());print(result.decode())
 proof=json.loads(result.decode().splitlines()[-1]);(ROOT/'docs/roadmap/evidence/ia-chat-latency-2026-11-13/cleanup-token-proof.json').write_text(json.dumps(proof,indent=2)+'\n')
 t.py(631,"import pathlib,json;p=pathlib.Path('/root/ia-validation-auth.json');assert json.loads(p.read_text())['email']=='ia-latency-validation@example.com';p.unlink()")
code="""import pathlib,sqlite3,json
base=pathlib.Path('/opt/ia-chat');before=sqlite3.connect('file:'+str(base/'.runtime/latency/webui-before.db')+'?mode=ro',uri=True);now=sqlite3.connect(base/'data/webui.db')
old={r[0] for r in before.execute('select id from user')};new={r[0] for r in now.execute('select id from user')};assert old<=new,'Real user removed'
assert now.execute(\"select count(*) from user where email='ia-latency-validation@example.com'\").fetchone()[0]==0
assert now.execute(\"select count(*) from auth where email='ia-latency-validation@example.com'\").fetchone()[0]==0
assert not (base/'data/.ia-latency-auth.json').exists();assert not pathlib.Path('/root/ia-validation-auth.json').exists()
oldowners=dict(before.execute(\"select id,user_id from model where id in ('gemma-4-26b','qwen3.6-35b')\"));newowners=dict(now.execute(\"select id,user_id from model where id in ('gemma-4-26b','qwen3.6-35b')\"));assert oldowners==newowners,'Model owner changed'
f=pathlib.Path('/root/ia-latency-rag.json')
if f.exists():
 kid=json.loads(f.read_text()).get('rag_fixture',{}).get('knowledge_id')
 if kid:assert now.execute('select count(*) from knowledge where id=?',(kid,)).fetchone()[0]==0
assert now.execute('pragma quick_check').fetchone()[0]=='ok'
print(json.dumps({'result':'PASS','fixture_users':0,'fixture_credentials_absent':True,'real_users_preserved':len(old),'users_now':len(new),'model_owners_unchanged':True,'fixture_knowledge_absent':True,'sqlite':'ok'}))
"""
result=json.loads(t.py(631,code));(ROOT/'docs/roadmap/evidence/ia-chat-latency-2026-11-13/cleanup-final.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
