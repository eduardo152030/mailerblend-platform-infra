#!/usr/bin/env python3
"""D035 read-only: prove inherited614 issue unchanged and svc01 critical DB dependency local."""
import argparse
from datetime import datetime,timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import yaml
ROOT=Path(__file__).resolve().parents[1]

def load(name):
 s=importlib.util.spec_from_file_location(name,ROOT/'scripts'/name);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def verify(output):
 assert not output.exists()
 old=json.loads((ROOT/'docs/roadmap/evidence/2026-11-06-d034-wave.json').read_text());r=old['results'][0];assert r['ct']==614 and r['evidence']['no_active_changes'] is True and r['evidence']['originals_verified'] is True
 run=r['evidence']['run'];log=Path.home()/'.local/share/mailerblend-recovery/phase4'/run/'614/private.log';snapshots=[]
 for line in log.read_text().splitlines():
  try:j=json.loads(line)
  except json.JSONDecodeError:continue
  if isinstance(j,dict) and 'infra-nucleoedge-sgtm-1' in j and 'config_hash' in j['infra-nucleoedge-sgtm-1']:snapshots.append(j)
 assert len(snapshots)>=2 and snapshots[0]==snapshots[-1],'D034 original evidence incomplete'
 module=load('run-skip-exporter-wave.py');m=load('rollout-approved-exporters.py')
 code='''import json,subprocess,hashlib,urllib.request,urllib.error
from urllib.parse import urlsplit
out={}
for ct in [614,61211]:
 probe="""import json,subprocess,hashlib
ids=subprocess.check_output(['docker','ps','-aq'],text=True).split();out={}
for c in json.loads(subprocess.check_output(['docker','inspect']+ids)):
 out[c['Name'].lstrip('/') ]={'id':c['Id'],'image':c['Image'],'running':c['State']['Running'],'started_at':c['State']['StartedAt'],'restarts':c['RestartCount'],'oom_killed':c['State']['OOMKilled'],'config_hash':hashlib.sha256(json.dumps(c['Config'],sort_keys=True).encode()).hexdigest()}
print(json.dumps(out))
"""
 p=subprocess.run(['pct','exec',str(ct),'--','python3','-'],input=probe,text=True,capture_output=True);assert p.returncode==0;out[ct]=json.loads(p.stdout)
probe="""import json,subprocess,urllib.request,urllib.error,re
from urllib.parse import urlsplit
app,db=json.loads(subprocess.check_output(['docker','inspect','infra-svc01-nocodb','infra-svc01-nocodb-db']))
env=dict(v.split('=',1) for v in app['Config'].get('Env',[]) if '=' in v)
assert urlsplit(env['NC_DB']).hostname=='db','Unexpected critical DB endpoint'
assert not any(any(x in v.lower() for x in ['192.168.1.114','infra-nucleoedge','sgtm']) for k,v in env.items() if any(x in k.upper() for x in ['URL','HOST','DSN','DB'])),'Referenced614 endpoint requires review'
shared=set(app['NetworkSettings']['Networks']) & set(db['NetworkSettings']['Networks']);assert shared
assert any('db' in (db['NetworkSettings']['Networks'][n].get('Aliases') or []) for n in shared),'DB alias not verified on shared network'
ready=subprocess.run(['docker','exec','infra-svc01-nocodb-db','pg_isready','-h','127.0.0.1','-p','5432'],capture_output=True).returncode==0
assert ready and app['State']['Running'] and db['State']['Running'] and db['State'].get('Health',{}).get('Status')=='healthy'
with urllib.request.urlopen('http://127.0.0.1:18080/api/v1/health',timeout=8) as response:assert response.status==200
print(json.dumps({'critical_dependency':'PostgreSQL local db','database_ready':ready,'database_health':'healthy','shared_networks':sorted(shared),'application_health_status':200,'no_614_endpoint_reference':True}))
"""
p=subprocess.run(['pct','exec','61211','--','python3','-'],input=probe,text=True,capture_output=True);assert p.returncode==0,'Critical dependency not verified';out['dependencies']=json.loads(p.stdout)
status=[]
for port in [8091,8092]:
 try:
  with urllib.request.urlopen('http://192.168.1.114:'+str(port)+'/healthy',timeout=8) as r:s=r.status
 except urllib.error.HTTPError as e:s=e.code
 status.append(s)
assert status==[503,503];out['614_status']=status
print(json.dumps(out))
'''
 result=subprocess.run(m.SSH+['python3','-'],input=code,text=True,capture_output=True,timeout=90);assert result.returncode==0,'Read-only isolation/dependency verification failed; no mutation'
 live=json.loads(result.stdout);assert live['614']==snapshots[0],'CT614 drift from unmodified D034 baseline'
 out={'observed_at_utc':datetime.now(timezone.utc).isoformat(),'decision':'D-035','ct614_case':'B','preexisting_before_mutation':True,'no_active_changes':True,'originals_verified':True,'ct614_current_health':live['614_status'],'critical_dependencies_verified':True,'ct61211_independent_of_614':True,'dependencies':live['dependencies'],'ct614_original_fingerprints':live['614'],'ct61211_initial_fingerprints':live['61211'],'scope':'Read-only; no writes/restarts/application repair; preserves legacy614 alerts; global guard required separately'}
 m.save(output,out);return out

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();result=verify(a.output);print(json.dumps({'ct614_case':result['ct614_case'],'preexisting_unchanged':True,'ct61211_independent':True,'database_ready':True}))
