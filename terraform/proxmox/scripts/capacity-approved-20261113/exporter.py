#!/usr/bin/env python3
"""Receta autorizada 13nov2026. Stdin en CT619/61211/620; backup antes de apply.
No pull, recreación, restart, apps ni recursosPVE. Rollback restaura inputs y límites.
"""
import subprocess,json,pathlib,hashlib,os,sys,re
from datetime import datetime,timezone

def run(*args):return subprocess.check_output(args,text=True,timeout=30).strip()
def snapshot():
 names=run('docker','ps','--format','{{.Names}}').splitlines()
 cs=json.loads(run('docker','inspect',*names));out={}
 for c in cs:
  out[c['Name'].lstrip('/')]=dict(id=c['Id'],image=c['Image'],started=c['State']['StartedAt'],restarts=c['RestartCount'],oom=c['State']['OOMKilled'],health=c['State'].get('Health',{}).get('Status'),cpu=c['HostConfig']['NanoCpus'],memory=c['HostConfig']['Memory'],swap=c['HostConfig']['MemorySwap'],mounts_sha256=hashlib.sha256(json.dumps(sorted(c['Mounts'],key=lambda x:x['Destination']),sort_keys=True).encode()).hexdigest())
 return out
host=run('hostname');table={'infra-pulpo':(619,384,'192.168.1.119'),'svc01':(61211,384,'192.168.1.112'),'infra-excraper':(620,256,'192.168.1.120')}
# El bind real se obtiene del contenedor, se valida contra el inventario en el driver.
assert host in table,host
ct,mib,ip=table[host];mode=sys.argv[1];base=pathlib.Path('/root/capacity-approved-20261113');before=snapshot();c=json.loads(run('docker','inspect','cadvisor'))[0]
ports=c['HostConfig']['PortBindings'];bound=ports['8080/tcp'][0]['HostIp'];assert bound.startswith('192.168.1.') and ports['8080/tcp'][0]['HostPort']=='8085'
os.environ['EXPORTER_BIND_IP']=bound
files=c['Config']['Labels']['com.docker.compose.project.config_files'].split(',');limit=next(pathlib.Path(f) for f in files if f.endswith('/cadvisor-limits.yml'))
cmd=['docker','compose']
for f in files:cmd+=['-f',f]

def emit():
 state=snapshot();pid=c['State']['Pid'];cg=pathlib.Path('/sys/fs/cgroup'+pathlib.Path(f'/proc/{pid}/cgroup').read_text().strip().split('::')[1])
 print(json.dumps(dict(time_utc=datetime.now(timezone.utc).isoformat(),ct=ct,bind=bound,containers=state,cgroup={f:(cg/f).read_text().strip() for f in ['memory.current','memory.max','memory.events','memory.pressure','memory.swap.current']})))
if mode=='prepare':
 assert c['State']['Running'] and c['State'].get('Health',{}).get('Status')=='healthy'
 base.mkdir(mode=0o700,exist_ok=True)
 if not (base/'baseline.json').exists():
  manifest={}
  for i,f in enumerate(files):
   p=pathlib.Path(f);dst=base/f'input-{i}.before';dst.write_bytes(p.read_bytes());dst.chmod(0o600)
   manifest[f]={'backup':dst.name,'sha256':hashlib.sha256(dst.read_bytes()).hexdigest()}
  (base/'manifest.json').write_text(json.dumps(manifest,indent=2))
  (base/'baseline.json').write_text(json.dumps(before,indent=2))
 for m in json.loads((base/'manifest.json').read_text()).values():assert hashlib.sha256((base/m['backup']).read_bytes()).hexdigest()==m['sha256']
 run(*cmd,'config','--quiet')
elif mode=='apply':
 baseline=json.loads((base/'baseline.json').read_text());assert before['cadvisor']['id']==baseline['cadvisor']['id']
 for m in json.loads((base/'manifest.json').read_text()).values():assert hashlib.sha256((base/m['backup']).read_bytes()).hexdigest()==m['sha256']
 text=limit.read_text();assert len(re.findall(r'mem_limit: \d+m',text))==1
 candidate=re.sub(r'mem_limit: \d+m',f'mem_limit: {mib}m',text)
 total=max(baseline['cadvisor']['swap'],mib*2**20)
 if 'memswap_limit:' in candidate:candidate=re.sub(r'memswap_limit: \d+m',f'memswap_limit: {total//2**20}m',candidate)
 else:candidate=candidate.replace(f'mem_limit: {mib}m',f'mem_limit: {mib}m\n    memswap_limit: {total//2**20}m')
 if candidate!=text:limit.write_text(candidate)
 try:
  run(*cmd,'config','--quiet')
  if before['cadvisor']['memory']!=mib*2**20 or before['cadvisor']['swap']!=total:run('docker','update','--memory',str(mib*2**20),'--memory-swap',str(total),'cadvisor')
 except BaseException:
  limit.write_text(text);raise
 after=snapshot()
 for n,b in before.items():
  a=after[n]
  for k in ['id','image','started','restarts','oom','cpu','mounts_sha256']:assert a[k]==b[k],(n,k)
  if n!='cadvisor':assert a['memory']==b['memory'] and a['swap']==b['swap']
 assert after['cadvisor']['memory']==mib*2**20
elif mode=='rollback':
 baseline=json.loads((base/'baseline.json').read_text());assert before['cadvisor']['id']==baseline['cadvisor']['id']
 for f,m in json.loads((base/'manifest.json').read_text()).items():
  data=(base/m['backup']).read_bytes();assert hashlib.sha256(data).hexdigest()==m['sha256'];pathlib.Path(f).write_bytes(data)
 run(*cmd,'config','--quiet');b=baseline['cadvisor'];run('docker','update','--memory',str(b['memory']),'--memory-swap',str(b['swap']),'cadvisor')
elif mode!='sample':raise ValueError(mode)
emit()
