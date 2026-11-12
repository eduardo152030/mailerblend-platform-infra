#!/usr/bin/env python3
"""D063: integración aditiva exclusiva de CT627, con backup/validación/rollback."""
import argparse,hashlib,importlib.util,json,os,shutil,subprocess,tarfile,io,urllib.request
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[1]
PRIVATE=Path.home()/'.local/share/mailerblend-recovery/new-lxc/voicebox-d063/monitoring-transaction'
spec=importlib.util.spec_from_file_location('stage',ROOT/'scripts/phase6-stage-a.py');t=importlib.util.module_from_spec(spec);spec.loader.exec_module(t)
BASE={610:'/opt/infra-prom',616:'/opt/infra-blackbox'}
FILES={610:['config/targets/node-exporter.json','config/targets/cadvisor.json','config/targets/application-health-stage-a.json','config/rules/voicebox-inventory.yml'],616:['config/blackbox.yml']}
def sha(b):return hashlib.sha256(b).hexdigest()
def get(ct,name):
 code='from pathlib import Path; import sys; p=Path('+repr(BASE[ct]+'/'+name)+');sys.stdout.buffer.write(p.read_bytes() if p.exists() else b"__ABSENT__")'
 return t.py(ct,code)
def candidate(ct,name):return PRIVATE/'candidate'/str(ct)/name
def prepare():
 assert not (PRIVATE/'baseline.json').exists(),'No sobrescribir transacción anterior'
 PRIVATE.mkdir(parents=True,exist_ok=True,mode=0o700);os.chmod(PRIVATE,0o700)
 baseline={}
 for ct in BASE:
  archive=t.remote(ct,['tar','-C',BASE[ct],'-czf','-','config']);(PRIVATE/f'{ct}-config-before.tar.gz').write_bytes(archive)
  with tarfile.open(fileobj=io.BytesIO(archive)) as bundle:
   for member in bundle.getmembers():
    assert not member.issym() and not member.islnk() and not member.name.startswith('/') and '..' not in Path(member.name).parts
   bundle.extractall(PRIVATE/'before'/str(ct),filter='data')
  baseline[str(ct)]={}
  for name in FILES[ct]:
   body=get(ct,name);baseline[str(ct)][name]=sha(body)
   dest=candidate(ct,name);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(body)
 for name,source in [('node-exporter.json','node-exporter.json'),('cadvisor.json','cadvisor.json')]:
  p=candidate(610,'config/targets/'+name);old=json.loads(p.read_text());new=json.loads((PRIVATE.parent/'activation'/source).read_text());assert not any(x['labels'].get('service')=='infra-voicebox' for x in old);p.write_text(json.dumps(old+new,indent=2)+'\n')
 p=candidate(610,'config/targets/application-health-stage-a.json');old=json.loads(p.read_text());old.append({'targets':['http://192.168.1.127:17493/health'],'labels':{'service':'infra-voicebox','vmid':'627','module':'voicebox_api_cpu','probe_id':'voicebox-api-health','probe_type':'internal','scope':'internal','health_signal':'api_liveness','source':'inventory'}});p.write_text(json.dumps(old,indent=2)+'\n')
 candidate(610,'config/rules/voicebox-inventory.yml').write_bytes((PRIVATE.parent/'activation/expected-inventory.yml').read_bytes())
 p=candidate(616,'config/blackbox.yml');data=yaml.safe_load(p.read_text());assert 'voicebox_api_cpu' not in data['modules'];data['modules']['voicebox_api_cpu']={'prober':'http','timeout':'5s','http':{'method':'GET','valid_status_codes':[200],'follow_redirects':False,'fail_if_body_not_matches_regexp':['"status"\\s*:\\s*"healthy"','"backend_variant"\\s*:\\s*"cpu"']}};p.write_text(yaml.safe_dump(data,sort_keys=False))
 (PRIVATE/'baseline.json').write_text(json.dumps(baseline,indent=2)+'\n')
 # Full isolated restore of config plus additive files, never validate partial rules.
 shutil.copytree(PRIVATE/'before/610/config',PRIVATE/'validation/config')
 for name in FILES[610]:
  dest=PRIVATE/'validation'/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(candidate(610,name).read_bytes())
 conf=PRIVATE/'validation/config/prometheus.yml';conf.write_text(conf.read_text().replace('/etc/prometheus/',str(PRIVATE/'validation/config')+'/'))
 pt=Path.home()/'.local/share/mailerblend-recovery/phase5/d050/promtool';p=subprocess.run([str(pt),'check','config',str(conf)],capture_output=True);(PRIVATE/'promtool.log').write_bytes(p.stdout+p.stderr);assert p.returncode==0,'promtool rechazó candidato'
 binary=PRIVATE/'blackbox_exporter';binary.write_bytes(t.remote(616,['docker','exec','infra-blackbox','cat','/bin/blackbox_exporter']));binary.chmod(0o700);p=subprocess.run([str(binary),'--config.file='+str(candidate(616,'config/blackbox.yml')),'--config.check'],capture_output=True);assert p.returncode==0,'Blackbox rechazó candidato'
 (PRIVATE/'validated.json').write_text(json.dumps({str(ct):{name:sha(candidate(ct,name).read_bytes()) for name in FILES[ct]} for ct in BASE},indent=2)+'\n');print('PASS: backup fueraPVE, extracción/restauración aislada, promtool y parserBlackbox')
def backups():
 for ct in BASE:
  folder=BASE[ct]+'/.runtime/d063-voicebox';path=folder+'/config-before.tar.gz';body=(PRIVATE/f'{ct}-config-before.tar.gz').read_bytes()
  code='from pathlib import Path;import sys;p=Path('+repr(path)+');sys.stdout.buffer.write(p.read_bytes() if p.exists() else b"")'
  existing=t.py(ct,code)
  if existing:assert existing==body,'Backup previo distinto; no sobrescribir'
  else:
   t.remote(ct,['mkdir','-p',folder]);t.remote(ct,['chmod','700',folder]);t.remote(ct,['tee',path],body);t.remote(ct,['chmod','600',path])
  assert t.py(ct,code)==body
 print('PASS: backups coordinados enCT yfueraPVE, bytes verificados')
def apply():
 backups()
 baseline=json.loads((PRIVATE/'baseline.json').read_text());desired=json.loads((PRIVATE/'validated.json').read_text());actual={str(ct):{name:sha(get(ct,name)) for name in FILES[ct]} for ct in BASE}
 if actual==desired:print('IDEMPOTENT:0escrituras/0recargas/0reinicios');return
 assert actual==baseline,'Deriva runtime: detener'
 # API liveness must satisfy its contract before discovery publication.
 with urllib.request.urlopen('http://192.168.1.127:17493/health',timeout=10) as r:d=json.load(r)
 assert d['status']=='healthy' and d['backend_variant']=='cpu'
 changed=[]
 try:
  for ct in [616,610]:
   for name in FILES[ct]:
    body=candidate(ct,name).read_bytes();assert sha(body)==desired[str(ct)][name];t.remote(ct,['tee',BASE[ct]+'/'+name],body);changed.append((ct,name))
   t.reload(ct)
 except Exception:
  for ct,name in reversed(changed):
   p=PRIVATE/'before'/str(ct)/name
   if p.exists():t.remote(ct,['tee',BASE[ct]+'/'+name],p.read_bytes())
   else:
    # Remove only this transaction's newly created rule, never a prior artifact.
    assert name=='config/rules/voicebox-inventory.yml';t.py(ct,'from pathlib import Path;Path('+repr(BASE[ct]+'/'+name)+').unlink()')
  for ct in {c for c,n in changed}:t.reload(ct)
  raise
 # Commit local IaC bytes only after successful narrow reloads; no Git commit.
 for ct in BASE:
  for name in FILES[ct]:
   p=ROOT/('services/infra-prom' if ct==610 else 'services/infra-blackbox')/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(candidate(ct,name).read_bytes())
 print('APPLIED: solo targets/regla627 y móduloBlackbox; sin reinicios')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action',choices=['prepare','backups','apply']);a=p.parse_args();globals()[a.action]()
