#!/usr/bin/env python3
"""Activa soporte cAdvisor N/A en Fleet/Details, conservando todos los demás paneles."""
import importlib.util,json,hashlib,os,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];s=importlib.util.spec_from_file_location('stage',ROOT/'scripts/phase6-stage-a.py');t=importlib.util.module_from_spec(s);s.loader.exec_module(t)
P=Path.home()/'.local/share/mailerblend-recovery/ia-chat/grafana';P.mkdir(parents=True,exist_ok=True,mode=0o700);os.chmod(P,0o700)
base='/opt/infra-grafana/config/provisioning/fleet-assets/'
state=t.g.state();ids={}
for uid in ['proxmox-lxc-fleet','proxmox-lxc-details']:
 file=uid+'.json';body=t.remote(611,['cat',base+file]);desired=(ROOT/'services/infra-grafana/config/provisioning/fleet-assets'/file).read_bytes();old=json.loads(body);new=json.loads(desired)
 differences=[(a,b) for a,b in zip(old['panels'],new['panels']) if a!=b];assert len(old['panels'])==len(new['panels']) and all('salud' in a['title'] or a['title'].startswith('LXC health') for a,b in differences),'Unrelated panel changes'
 assert all(old[k]==new[k] for k in old if k not in ['panels','version']),'Unrelated dashboard properties'
 p=P/(file+'.before')
 if not p.exists():p.write_bytes(body);p.chmod(0o600)
 ids[uid]={'changed':body!=desired,'before_sha256':hashlib.sha256(body).hexdigest(),'desired_sha256':hashlib.sha256(desired).hexdigest()}
# Backup DB online through SQLite backup API; never expose credentials or DB.
if not (P/'grafana-before.db').exists():
 body=t.g.py("import sqlite3,subprocess,json,pathlib,sys; c=json.loads(subprocess.check_output(['docker','inspect','grafana']))[0];v=next(m['Source'] for m in c['Mounts'] if m['Destination']=='/var/lib/grafana');p=pathlib.Path('/opt/infra-grafana/.runtime/ia-chat');p.mkdir(parents=True,exist_ok=True);p.chmod(0o700);src=sqlite3.connect('file:'+v+'/grafana.db?mode=ro',uri=True);dst=sqlite3.connect(str(p/'grafana-before.db'));src.backup(dst);assert dst.execute('pragma integrity_check').fetchone()[0]=='ok';dst.close();(p/'grafana-before.db').chmod(0o600);sys.stdout.buffer.write((p/'grafana-before.db').read_bytes())")
 (P/'grafana-before.db').write_bytes(body);(P/'grafana-before.db').chmod(0o600)
 import sqlite3
 db=sqlite3.connect('file:'+str(P/'grafana-before.db')+'?mode=ro',uri=True);assert db.execute('pragma integrity_check').fetchone()[0]=='ok';db.close()
changed=[]
try:
 for uid,v in ids.items():
  if v['changed']:t.remote(611,['tee',base+uid+'.json'],(ROOT/'services/infra-grafana/config/provisioning/fleet-assets'/str(uid+'.json')).read_bytes());changed.append(uid)
 for attempt in range(25):
  ok=True
  for uid in ids:
   actual=t.g.api('/api/dashboards/uid/'+uid);want=json.loads((ROOT/'services/infra-grafana/config/provisioning/fleet-assets'/str(uid+'.json')).read_text());ok &= actual['meta']['provisioned'] and actual['dashboard']['panels']==want['panels']
  if ok:break
  time.sleep(2)
 assert ok,'Provisioning did not converge'
 assert t.g.state()['identity']==state['identity'],'Grafana restarted'
except Exception:
 for uid in changed:t.remote(611,['tee',base+uid+'.json'],(P/(uid+'.json.before')).read_bytes())
 raise
out={'dashboards':ids,'changed_files':len(changed),'restarts':0,'explicit_reloads':0,'database_backup_integrity':'ok','runtime_api_panels_match':True};(ROOT/'docs/roadmap/evidence/ia-chat-2026-11-13/grafana-integration.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
