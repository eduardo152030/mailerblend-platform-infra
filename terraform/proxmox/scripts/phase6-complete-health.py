#!/usr/bin/env python3
"""D057 fixed read-only app checks and complete fleet health transaction."""
import argparse,fcntl,importlib.util,inspect,json,os,time
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('stage',ROOT/'scripts/phase6-stage-a.py');t=importlib.util.module_from_spec(s);s.loader.exec_module(t)
t.PRIVATE=Path.home()/'.local/share/mailerblend-recovery/phase6/d057-20261109'
t.SPEC=ROOT/'services/infra-prom/config/phase6/complete-health.yml'
t.PATHS={610:['config/prometheus.yml','config/targets/application-health-complete.json'],611:['config/provisioning/fleet-assets/proxmox-lxc-fleet.json'],616:['config/blackbox.yml']}
COMMON=ROOT/'services/common/functional-health'
# Reuse the verified transaction with a fresh backup namespace; never overwrite D054.
exec(inspect.getsource(t.baseline).replace('.runtime/d054','.runtime/d057-20261109'),t.__dict__)
exec(inspect.getsource(t.prepare).replace('application-health-stage-a.json','application-health-complete.json').replace('apps-before.json','apps-before-v2.json'),t.__dict__)

def identities():
 out={}
 for ct in [613,621,623,625]:
  out[str(ct)]=json.loads(t.py(ct,"import subprocess,json,hashlib;ids=subprocess.check_output(['docker','ps','-q'],text=True).split();cs=json.loads(subprocess.check_output(['docker','inspect']+ids));print(json.dumps({c['Name']:[c['Id'],c['State']['StartedAt'],c['RestartCount'],hashlib.sha256(json.dumps([c['Config'],c['HostConfig'],sorted(c['Mounts'],key=lambda m:json.dumps(m,sort_keys=True))],sort_keys=True).encode()).hexdigest()] for c in cs}))"))
 return out
t.app_identities=identities

def collectors():
 contracts=yaml.safe_load((COMMON/'checks.yml').read_text());inventory={}
 for path in (ROOT/'inventory/services').glob('*.yml'):
  service=yaml.safe_load(path.read_text())['service'];inventory[service['name']]=service['vmid']
 if not (t.PRIVATE/'apps-before-v2.json').exists():t.save('apps-before-v2.json',identities())
 for name,contract in contracts.items():
  ct=int(inventory[name]);spec={'ct_id':ct,'service':name,**contract};base='/opt/monitoring-functional'
  files={base+'/check.py':(COMMON/'check.py').read_bytes(),base+'/config.json':(json.dumps(spec,indent=2)+'\n').encode(),'/etc/systemd/system/functional-health.service':(COMMON/'functional-health.service').read_bytes(),'/etc/systemd/system/functional-health.timer':(COMMON/'functional-health.timer').read_bytes()}
  state=json.loads(t.py(ct,'import pathlib,hashlib,json;paths='+repr(list(files))+';print(json.dumps({f:hashlib.sha256(pathlib.Path(f).read_bytes()).hexdigest() if pathlib.Path(f).exists() else None for f in paths}))'))
  marker=t.PRIVATE/f'collector-{ct}.json'
  desired={f:t.digest(b) for f,b in files.items()}
  if marker.exists():assert state==desired,'Collector config drift';print('IDEMPOTENT collector CT'+str(ct));continue
  if state==desired:
   active=t.remote(ct,['systemctl','is-active','functional-health.timer']).decode().strip();assert active=='active'
   t.save(marker.name,desired);print('ADOPT verified existing collector CT'+str(ct));continue
  assert all(v is None for v in state.values()),'Collector paths already exist; do not overwrite'
  t.save(f'collector-{ct}-before.json',state)
  for f,body in files.items():
   t.remote(ct,['mkdir','-p',str(Path(f).parent)]);t.remote(ct,['tee',f],body);t.remote(ct,['chmod','644',f])
  t.remote(ct,['systemd-analyze','verify','/etc/systemd/system/functional-health.service','/etc/systemd/system/functional-health.timer'])
  t.remote(ct,['systemctl','daemon-reload']);t.remote(ct,['systemctl','start','functional-health.service'])
  t.remote(ct,['systemctl','enable','--now','functional-health.timer'])
  t.save(marker.name,desired);print('PASS functional collector CT'+str(ct)+'; application containers untouched')
 assert identities()==json.loads((t.PRIVATE/'apps-before-v2.json').read_text()),'App config drift'

def verify():
 b=json.loads((t.PRIVATE/'baseline.json').read_text());expected=t.expected()
 for ct in t.BASES:
  state=t.state(ct);assert state['identity']==b['states'][str(ct)]['identity'],'Container drift';assert state['hashes']==expected[str(ct)],'Config drift'
 assert identities()==json.loads((t.PRIVATE/'apps-before-v2.json').read_text()),'App drift'
 targets=t.api('/api/v1/targets')['activeTargets'];old={(json.dumps(x['labels'],sort_keys=True),x['scrapeUrl']) for x in b['targets']};now={(json.dumps(x['labels'],sort_keys=True),x['scrapeUrl']) for x in targets};assert old<=now and len(now-old)==1,'Old targets lost'
 assert all(x['health']=='up' for x in targets),'Target not UP'
 probes=t.query('probe_success{job="blackbox"}');assert len(probes)==18 and all(float(x['value'][1])==1 for x in probes),'Probe failed'
 for job in ['node_exporter','cadvisor']:assert int(float(t.query('count(up{job="'+job+'"} == 1)')[0]['value'][1]))==17
 checks=t.query('lxc_app_check_success');assert len(checks)==3 and all(float(x['value'][1])==1 for x in checks),'Functional check failed'
 assert not t.query('ALERTS{alertstate="firing"}')
 rules=t.api('/api/v1/rules')
 def defs(data):return [(r['name'],r['query'],r.get('duration'),r.get('labels'),r.get('annotations')) for x in data['groups'] for r in x['rules']]
 assert defs(rules)==defs(b['rules']) and all(r['health']=='ok' for x in rules['groups'] for r in x['rules'])
 dashboards=t.g.dashboards();assert set(dashboards)==set(b['dashboards'])
 for uid,model in b['dashboards'].items():
  if uid!='proxmox-lxc-fleet':assert model==dashboards[uid],'Other dashboard changed'
 model=json.loads((t.PRIVATE/'candidate/611'/t.PATHS[611][0]).read_text());live=t.g.api('/api/dashboards/uid/proxmox-lxc-fleet');assert live['meta']['provisioned']
 for k in ['panels','templating']:assert live['dashboard'][k]==model[k],'Waiting for Grafana'
 assert t.g.api('/api/datasources')==b['datasources']
 table=next(p for p in model['panels'] if p['title'].startswith('LXC health'));values={}
 for target in table['targets']:
  rows=t.query(target['expr'].replace('${lxc:regex}','.*').replace('${service:regex}','.*'));assert len(rows)==17 and len({x['metric']['ct_id'] for x in rows})==17,(target['refId'],len(rows));values[target['refId']]=rows
 assert all(float(x['value'][1])>=0 or float(x['value'][1])==-2 for x in values['D']),'Application UNKNOWN'
 assert all(float(x['value'][1])==1 for x in values['K']),'Monitoring not healthy'
 assert all(float(x['value'][1])==0 for x in values['M']),'Infrastructure not healthy'
 assert all(float(x['value'][1])==0 for x in values['I']),'Overall not healthy'
 assert all(float(x['value'][1])>0 for x in values['J']),'Uptime missing'
 result={'timestamp_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'table':values,'applications_config_unchanged':True,'old_monitoring_preserved':True,'blackbox_success':18,'node_up':17,'cadvisor_up':17,'f5_rules_unchanged':True,'firing':[]}
 (ROOT/'docs/roadmap/evidence/2026-11-09-d057-deployment.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS complete fleet:17 infrastructure/monitoring/overall healthy, real uptime, no Application UNKNOWN')
t.verify=verify
if __name__=='__main__':
 t.PRIVATE.mkdir(parents=True,exist_ok=True,mode=0o700);os.chmod(t.PRIVATE,0o700);lock=(t.PRIVATE/'transaction.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 p=argparse.ArgumentParser();p.add_argument('action',choices=['baseline','collectors','prepare','validate','apply','verify']);a=p.parse_args();(collectors if a.action=='collectors' else getattr(t,a.action))()
