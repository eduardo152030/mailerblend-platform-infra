#!/usr/bin/env python3
"""Driver secuencial autorizado 619→61211→620;600s/21, HALT y rollback ante fallo."""
import subprocess,os,json,pathlib,time,urllib.request,urllib.parse,tarfile,tempfile,hashlib
from datetime import datetime,timezone
ROOT=pathlib.Path(__file__).resolve().parent;E=pathlib.Path('docs/roadmap/evidence');PRIVATE=pathlib.Path.home()/'.local/state/mailerblend/capacity-approved-20261113';PRIVATE.mkdir(parents=True,exist_ok=True,mode=0o700)
SSH=['ssh','-o','UserKnownHostsFile='+os.environ['HOME']+'/.ssh/known_hosts','-o','StrictHostKeyChecking=yes','-o','BatchMode=yes','pve'];CODE=(ROOT/'exporter.py').read_text()
def remote(ct,mode):
 p=subprocess.run(SSH+['pct','exec',str(ct),'--','python3','-',mode],input=CODE,text=True,capture_output=True,timeout=60)
 if p.returncode:raise RuntimeError(f'CT{ct} {mode} falló: '+p.stderr[-600:])
 return json.loads(p.stdout)
def get(path):
 with urllib.request.urlopen('http://192.168.1.110:9090'+path,timeout=15) as r:return json.load(r)
def metrics(ip):
 with urllib.request.urlopen('http://'+ip+':8085/metrics',timeout=15) as r:b=r.read()
 assert b'container_cpu_usage_seconds_total' in b and b'container_memory_working_set_bytes' in b
 return len(b)
def events(s):return dict((k,int(v)) for k,v in (line.split() for line in s.splitlines()))
def save(ct,data): (E/f'2026-11-13-capacity-execute-{ct}.json').write_text(json.dumps(data,indent=2))
for ct in [619,61211,620]:
 result={'ct':ct,'status':'IN PROGRESS','samples':[]};changed=False
 try:
  baseline=remote(ct,'prepare');result['baseline']=baseline;save(ct,result)
  p=subprocess.run(SSH+['pct','exec',str(ct),'--','tar','-C','/root','-czf','-','capacity-approved-20261113'],capture_output=True,check=True)
  archive=PRIVATE/f'{ct}-before.tar.gz';archive.write_bytes(p.stdout);archive.chmod(0o600)
  with tempfile.TemporaryDirectory(dir=PRIVATE) as tmp:
   with tarfile.open(archive) as tar:tar.extractall(tmp,filter='data')
   base=pathlib.Path(tmp)/'capacity-approved-20261113'
   for m in json.loads((base/'manifest.json').read_text()).values():assert hashlib.sha256((base/m['backup']).read_bytes()).hexdigest()==m['sha256']
  result['external_config_restore']='PASS';changed=True;applied=remote(ct,'apply');result['applied']=applied;save(ct,result)
  print(ct,'APPLIED; backup externo restaurado; empieza600s/21',flush=True)
  start=time.monotonic()
  for i in range(21):
   if i:time.sleep(max(0,start+i*30-time.monotonic()))
   s=remote(ct,'sample');s['elapsed']=time.monotonic()-start
   for name,b in baseline['containers'].items():
    a=s['containers'][name]
    for k in ['id','image','started','restarts','oom','cpu','mounts_sha256']:assert a[k]==b[k],(ct,name,k)
    if b['health']=='healthy':assert a['health']=='healthy',(name,'health')
   ev=events(s['cgroup']['memory.events']);old=events(baseline['cgroup']['memory.events'])
   assert ev['oom']==old['oom'] and ev['oom_kill']==old['oom_kill']
   targets=get('/api/v1/targets')['data']['activeTargets'];cad=[t for t in targets if t['labels'].get('job')=='cadvisor']
   assert len(cad)==18 and all(t['health']=='up' and not t['lastError'] for t in cad),'fleet targets'
   target=next(t for t in cad if t['labels']['instance']==s['bind']+':8085')
   s['scrape_duration']=target['lastScrapeDuration'];s['metrics_bytes']=metrics(s['bind'])
   q='lxc:cpu_usage:percent{ct_id="'+str(ct)+'"}'
   cpu=get('/api/v1/query?'+urllib.parse.urlencode({'query':q}))['data']['result'];assert len(cpu)==1 and 0<=float(cpu[0]['value'][1])<=100
   s['lxc_cpu']=cpu[0]
   alerts=get('/api/v1/alerts')['data']['alerts'];assert not any(a['labels'].get('ct_id')==str(ct) or a['labels'].get('service')==target['labels']['service'] for a in alerts),'target alert'
   s['psi_avg10']=float(s['cgroup']['memory.pressure'].splitlines()[0].split('avg10=')[1].split()[0])
   result['samples'].append(s);save(ct,result)
   print(ct,i,round(s['elapsed'],1),'scrape',round(s['scrape_duration'],3),'PSI',s['psi_avg10'],flush=True)
  assert result['samples'][-1]['elapsed']>=600
  assert all(s['psi_avg10']<=0.1 for s in result['samples'][-3:]),'PSI final persistente'
  reapply=remote(ct,'apply');last=result['samples'][-1]
  assert reapply['containers']==last['containers'],'idempotencia'
  result.update(status='DONE',idempotence='PASS',finished_utc=datetime.now(timezone.utc).isoformat());save(ct,result)
  print(ct,'DONE; siguiente CT permitido',flush=True)
 except BaseException as exc:
  result.update(status='HALT',error=str(exc))
  if changed:
   try:result['rollback']=remote(ct,'rollback')
   except BaseException as rb:result['rollback_error']=str(rb)
  save(ct,result);print(ct,'HALT',str(exc),flush=True);raise
