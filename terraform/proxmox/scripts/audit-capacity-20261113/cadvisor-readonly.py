#!/usr/bin/env python3
"""Ejecutar por stdin en PVE. Solo lectura; no arranca CT ni cambia límites."""
import subprocess,json,pathlib,concurrent.futures
from datetime import datetime,timezone

def run(args):return subprocess.check_output(args,text=True,timeout=20).strip()
def audit(ct):
 row={'ct':ct['vmid'],'name':ct['name'],'status':ct['status']}
 if ct['status']!='running':return row
 code='''import subprocess,json,pathlib
cs=json.loads(subprocess.check_output(['docker','inspect','cadvisor'],text=True))[0]
pid=cs['State']['Pid'];cg=pathlib.Path('/sys/fs/cgroup'+pathlib.Path(f'/proc/{pid}/cgroup').read_text().strip().split('::')[1])
stat=dict(line.split() for line in (cg/'memory.stat').read_text().splitlines())
print(json.dumps(dict(id=cs['Id'],started=cs['State']['StartedAt'],restarts=cs['RestartCount'],oom=cs['State']['OOMKilled'],memory_limit=cs['HostConfig']['Memory'],swap_limit=cs['HostConfig']['MemorySwap'],cpu_limit=cs['HostConfig']['NanoCpus'],cgroup={f:(cg/f).read_text().strip() for f in ['memory.current','memory.max','memory.swap.current','memory.events','memory.pressure']},stat={k:int(stat.get(k,0)) for k in ['anon','file','kernel','slab_reclaimable','pgmajfault']})))'''
 try:
  p=subprocess.run(['pct','exec',str(ct['vmid']),'--','python3','-'],input=code,text=True,capture_output=True,timeout=25)
  if p.returncode:row['error']='sin cAdvisor accesible o Python3/Docker disponible'
  else:row.update(json.loads(p.stdout))
 except Exception as e:row['error']=type(e).__name__
 return row
cts=json.loads(run(['pvesh','get','/nodes/pve/lxc','--output-format','json']))
with concurrent.futures.ThreadPoolExecutor(2) as pool:rows=list(pool.map(audit,cts))
print(json.dumps({'time_utc':datetime.now(timezone.utc).isoformat(),'containers':rows}))
