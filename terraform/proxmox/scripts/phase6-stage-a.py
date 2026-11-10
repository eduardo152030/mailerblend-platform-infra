#!/usr/bin/env python3
"""D054 coordinated additive Prometheus/Blackbox/Grafana config transaction."""
import argparse,fcntl,hashlib,importlib.util,io,json,os,shlex,subprocess,tarfile,time,urllib.request,urllib.parse
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[1]
PRIVATE=Path.home()/'.local/share/mailerblend-recovery/phase6/d054'
SPEC=ROOT/'services/infra-prom/config/phase6/application-health.yml'
BASES={610:'/opt/infra-prom',611:'/opt/infra-grafana',616:'/opt/infra-blackbox'}
PATHS={610:['config/prometheus.yml','config/targets/application-health-stage-a.json'],611:['config/provisioning/fleet-assets/proxmox-lxc-fleet.json'],616:['config/blackbox.yml']}
def digest(b):return hashlib.sha256(b).hexdigest()
def remote(ct,args,body=None):
 r=subprocess.run(['ssh','-o','UserKnownHostsFile='+str(Path.home()/'.ssh/known_hosts'),'-o','StrictHostKeyChecking=yes','-o','BatchMode=yes','pve',shlex.join(['pct','exec',str(ct),'--']+args)],input=body,capture_output=True,timeout=120)
 assert r.returncode==0,f'CT{ct} failed; output withheld'
 return r.stdout
def py(ct,code):return remote(ct,['python3','-c',code])
def module(name,path):
 s=importlib.util.spec_from_file_location(name,ROOT/path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
g=module('grafana','scripts/deploy-fleet-dashboard.py')
def query(q):
 with urllib.request.urlopen(urllib.request.Request('http://192.168.1.110:9090/api/v1/query',data=urllib.parse.urlencode({'query':q}).encode()),timeout=30) as r:return json.load(r)['data']['result']
def api(path):return json.load(urllib.request.urlopen('http://192.168.1.110:9090'+path,timeout=20))['data']
def save(name,d):
 p=PRIVATE/name;p.parent.mkdir(parents=True,exist_ok=True,mode=0o700);p.write_text(json.dumps(d,indent=2)+'\n');os.chmod(p,0o600)
def state(ct):
 return json.loads(py(ct,f'''import pathlib,hashlib,json,subprocess
p=pathlib.Path({BASES[ct]!r});ids=subprocess.check_output(['docker','ps','-q'],text=True).split();cs=json.loads(subprocess.check_output(['docker','inspect']+ids))
print(json.dumps({{'hashes':{{str(f.relative_to(p)):hashlib.sha256(f.read_bytes()).hexdigest() for f in p.glob('config/**/*') if f.is_file()}},'identity':{{c['Name']:[c['Id'],c['State']['StartedAt'],c['RestartCount']] for c in cs}}}}))'''))
def baseline():
 assert not (PRIVATE/'baseline.json').exists(),'Baseline exists; do not overwrite'
 PRIVATE.mkdir(parents=True,exist_ok=True,mode=0o700);os.chmod(PRIVATE,0o700)
 b={'started':time.time(),'states':{},'targets':api('/api/v1/targets')['activeTargets'],'dashboards':g.dashboards(),'datasources':g.api('/api/datasources'),'rules':api('/api/v1/rules'),'backups':{},'unknown_initial':11}
 for ct in BASES:
  b['states'][str(ct)]=state(ct)
  archive=py(ct,f'''import io,tarfile,pathlib,sys,hashlib,os
base=pathlib.Path({BASES[ct]!r});p=base/'.runtime/d054';p.mkdir(parents=True,exist_ok=False);os.chmod(p,0o700);b=io.BytesIO()
with tarfile.open(fileobj=b,mode='w:gz') as a:a.add(base/'config',arcname='config')
body=b.getvalue();(p/'before.tar.gz').write_bytes(body);os.chmod(p/'before.tar.gz',0o600);sys.stdout.buffer.write(body)''')
  (PRIVATE/f'{ct}-before.tar.gz').write_bytes(archive);os.chmod(PRIVATE/f'{ct}-before.tar.gz',0o600)
  assert py(ct,f'import hashlib;print(hashlib.sha256(open({BASES[ct]+"/.runtime/d054/before.tar.gz"!r},"rb").read()).hexdigest())').decode().strip()==digest(archive)
  dest=PRIVATE/'before'/str(ct);dest.mkdir(parents=True,mode=0o700)
  with tarfile.open(fileobj=io.BytesIO(archive)) as a:a.extractall(dest,filter='data')
  assert all(digest((dest/f).read_bytes())==h for f,h in b['states'][str(ct)]['hashes'].items())
  b['backups'][str(ct)]=digest(archive)
 save('baseline.json',b);print('PASS baseline, three CT/offhost backups and restore-check hashes')
def app_identities():
 out={}
 for ct in [617,618,620,624,626]:
  out[str(ct)]=json.loads(py(ct,"import subprocess,json;ids=subprocess.check_output(['docker','ps','-q'],text=True).split();cs=json.loads(subprocess.check_output(['docker','inspect']+ids));print(json.dumps({c['Name']:[c['Id'],c['State']['StartedAt'],c['RestartCount']] for c in cs}))"))
 return out
def prepare():
 b=json.loads((PRIVATE/'baseline.json').read_text());spec=yaml.safe_load(SPEC.read_text())
 apps=app_identities()
 if (PRIVATE/'apps-before.json').exists():assert apps==json.loads((PRIVATE/'apps-before.json').read_text())
 else:save('apps-before.json',apps)
 for ct in BASES:
  assert state(ct)==b['states'][str(ct)],'Drift before prepare'
  for name in PATHS[ct]:
   old=PRIVATE/'before'/str(ct)/name;out=PRIVATE/'candidate'/str(ct)/name;out.parent.mkdir(parents=True,exist_ok=True)
   if old.exists():out.write_bytes(old.read_bytes())
 conf=PRIVATE/'candidate/610/config/prometheus.yml';prom=yaml.safe_load(conf.read_text())
 job=next(j for j in prom['scrape_configs'] if j['job_name']==spec['scrape_job'])
 assert not any(spec['file_sd_path'] in x['files'] for x in job['file_sd_configs'])
 job['file_sd_configs'].append({'files':[spec['file_sd_path']]});conf.write_text(yaml.safe_dump(prom,sort_keys=False))
 targets=[];oldurls={t['labels'].get('instance') for t in b['targets'] if t['labels'].get('job')=='blackbox'}
 for t in spec['targets']:
  assert t['url'] not in oldurls,'Duplicate probe'
  targets.append({'targets':[t['url']],'labels':{'service':t['service'],'vmid':t['vmid'],'module':t['module'],'probe_id':t['probe_id'],'probe_type':'internal' if t['signal'] not in ['public_liveness'] else 'public_url','scope':'external' if t['signal']=='public_liveness' else 'internal','health_signal':t['signal'],'source':'phase6_iac'}})
 (PRIVATE/'candidate/610/config/targets/application-health-stage-a.json').write_text(json.dumps(targets,indent=2)+'\n')
 black=PRIVATE/'candidate/616/config/blackbox.yml';bb=yaml.safe_load(black.read_text());assert not (set(bb['modules'])&set(spec['modules']));bb['modules'].update(spec['modules']);black.write_text(yaml.safe_dump(bb,sort_keys=False))
 (PRIVATE/'candidate/611'/PATHS[611][0]).write_bytes((ROOT/'services/infra-grafana'/PATHS[611][0]).read_bytes())
 save('candidate.json',{str(ct):{f:digest((PRIVATE/'candidate'/str(ct)/f).read_bytes()) for f in PATHS[ct]} for ct in BASES})
 print('Prepared additive candidate; original targets/modules/jobs preserved')
def validate():
 # promtool from already verified D050 installation; validate against complete baseline config.
 staging=PRIVATE/'validation';staging.mkdir(exist_ok=True)
 import shutil
 shutil.copytree(PRIVATE/'before/610/config',staging/'config',dirs_exist_ok=True)
 for f in PATHS[610]:
  dest=staging/f;dest.parent.mkdir(exist_ok=True,parents=True);dest.write_bytes((PRIVATE/'candidate/610'/f).read_bytes())
 conf=staging/'config/prometheus.yml';conf.write_text(conf.read_text().replace('/etc/prometheus/',str(staging/'config')+'/'))
 pt=Path.home()/'.local/share/mailerblend-recovery/phase5/d050/promtool'
 r=subprocess.run([str(pt),'check','config',str(conf)],capture_output=True);assert r.returncode==0,'promtool failed (output withheld)'
 # Real Blackbox binary parser in config-check mode, no server or app restarts.
 binary=PRIVATE/'blackbox_exporter';binary.write_bytes(remote(616,['docker','exec','infra-blackbox','cat','/bin/blackbox_exporter']));os.chmod(binary,0o700)
 r=subprocess.run([str(binary),'--config.file='+str(PRIVATE/'candidate/616/config/blackbox.yml'),'--config.check'],capture_output=True);assert r.returncode==0,'Blackbox config-check failed'
 json.loads((PRIVATE/'candidate/611'/PATHS[611][0]).read_text());save('validated.json',json.loads((PRIVATE/'candidate.json').read_text()));print('PASS promtool + actual Blackbox config parser + JSON')
def reload(ct):
 container={610:'prometheus',616:'infra-blackbox'}[ct];remote(ct,['docker','kill','--signal=SIGHUP',container])
def expected():
 b=json.loads((PRIVATE/'baseline.json').read_text());cand=json.loads((PRIVATE/'candidate.json').read_text());out={}
 for ct in BASES:out[str(ct)]=dict(b['states'][str(ct)]['hashes']);out[str(ct)].update(cand[str(ct)])
 return out
def verify():
 b=json.loads((PRIVATE/'baseline.json').read_text());exp=expected()
 for ct in BASES:
  s=state(ct);assert s['identity']==b['states'][str(ct)]['identity'],'Container identity drift';assert s['hashes']==exp[str(ct)],'Config mismatch'
 old={(json.dumps(t['labels'],sort_keys=True),t['scrapeUrl']) for t in b['targets']};targets=api('/api/v1/targets')['activeTargets'];now={(json.dumps(t['labels'],sort_keys=True),t['scrapeUrl']) for t in targets};assert old<=now,'Old targets lost'
 assert len(now-old)==6,'Expected six new probes';assert all(t['health']=='up' for t in targets),'Target not UP'
 assert len(query('probe_success{job="blackbox"}'))==17
 assert all(float(r['value'][1])==1 for r in query('probe_success{job="blackbox"}')),'Existing probe regression'
 assert app_identities()==json.loads((PRIVATE/'apps-before.json').read_text()),'Application container drift'
 assert not query('ALERTS{alertstate="firing"}'),'Unexpected FIRING alerts'
 assert all(float(r['value'][1])==1 for r in query('probe_success{source="phase6_iac"}')),'New functional probe failed'
 assert len(query('probe_success{source="phase6_iac"}'))==6
 rules=api('/api/v1/rules');assert all(r['health']=='ok' for x in rules['groups'] for r in x['rules'])
 # Alert rules and recording rules must be identical, ignoring runtime evaluation data.
 def ruledefs(groups):return [(r['name'],r['query'],r.get('duration'),r.get('labels'),r.get('annotations')) for x in groups for r in x['rules']]
 assert ruledefs(rules['groups'])==ruledefs(b['rules']['groups']),'Rule definitions changed'
 dashboards=g.dashboards();assert set(dashboards)==set(b['dashboards'])
 for uid,oldmodel in b['dashboards'].items():
  if uid!='proxmox-lxc-fleet':assert dashboards[uid]==oldmodel,'Unrelated dashboard changed'
 model=json.loads((PRIVATE/'candidate/611'/PATHS[611][0]).read_text());live=g.api('/api/dashboards/uid/proxmox-lxc-fleet');assert live['meta']['provisioned']
 for k in ['panels','templating']:assert live['dashboard'][k]==model[k],'Dashboard not yet provisioned'
 assert g.api('/api/datasources')==b['datasources']
 table=next(p for p in model['panels'] if p['title'].startswith('LXC health'))
 values={}
 for t in table['targets']:
  rows=query(t['expr'].replace('${lxc:regex}','.*').replace('${service:regex}','.*'));assert len(rows)==17 and len({r['metric']['ct_id'] for r in rows})==17,(t['refId'],len(rows));values[t['refId']]=rows
 result={'timestamp_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'new_targets':6,'old_blackbox_preserved':11,'all_blackbox_up':17,'new_functional_probes_pass':6,'old_dashboards_preserved':7,'application_identities_unchanged':True,'container_identity_unchanged':True,'rules_unchanged':True,'table':values,'firing':query('ALERTS{alertstate="firing"}'),'pending':query('ALERTS{alertstate="pending"}')}
 (ROOT/'docs/roadmap/evidence/2026-11-07-d054-deployment.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS verification: 17 CT, 17 Blackbox, 6 new functional probes; original targets/rules/dashboards/identities preserved')
def apply():
 b=json.loads((PRIVATE/'baseline.json').read_text());cand=json.loads((PRIVATE/'candidate.json').read_text());assert cand==json.loads((PRIVATE/'validated.json').read_text());exp=expected()
 for ct in BASES:
  for f in PATHS[ct]:assert digest((PRIVATE/'candidate'/str(ct)/f).read_bytes())==cand[str(ct)][f]
 states={str(ct):state(ct) for ct in BASES}
 if all(states[str(ct)]['hashes']==exp[str(ct)] for ct in BASES):
  verify();save('idempotence.json',{'writes':0,'reloads':0,'restarts':0,'result':'PASS'});print('IDEMPOTENT zero writes/reloads/restarts');return
 assert states==b['states'],'Drift before apply'
 try:
  for ct in [616,610,611]:
   for f in PATHS[ct]:
    remote(ct,['mkdir','-p',str(Path(BASES[ct]+'/'+f).parent)]);remote(ct,['tee',BASES[ct]+'/'+f],(PRIVATE/'candidate'/str(ct)/f).read_bytes())
   if ct in [610,616]:reload(ct)
  deadline=time.monotonic()+100
  while True:
   try:verify();break
   except AssertionError as e:
    if time.monotonic()>deadline:raise
    time.sleep(3)
  save('applied.json',{'time':time.time()})
 except Exception:
  rollback();raise
def rollback():
 b=json.loads((PRIVATE/'baseline.json').read_text())
 for ct in [611,610,616]:
  for f in PATHS[ct]:
   p=PRIVATE/'before'/str(ct)/f
   if p.exists():remote(ct,['tee',BASES[ct]+'/'+f],p.read_bytes())
   else:py(ct,f'from pathlib import Path;Path({BASES[ct]+"/"+f!r}).unlink(missing_ok=True)')
  if ct in [610,616]:reload(ct)
 for ct in BASES:assert state(ct)==b['states'][str(ct)]
 print('Safety rollback: baseline files and identities restored; backups retained')
if __name__=='__main__':
 PRIVATE.mkdir(parents=True,exist_ok=True,mode=0o700);lock=(PRIVATE/'transaction.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 p=argparse.ArgumentParser();p.add_argument('action',choices=['baseline','prepare','validate','apply','verify','rollback']);args=p.parse_args();globals()[args.action]()
