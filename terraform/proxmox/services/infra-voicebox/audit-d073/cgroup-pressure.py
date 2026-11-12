"""Read-only nested cgroup limits/pressure; no container exec or configuration change."""
from pathlib import Path
import json,time,datetime
root=Path('/sys/fs/cgroup/lxc')
def val(p):
 try:return p.read_text().strip()
 except OSError:return ''
def stat(p):
 d={}
 for line in val(p).splitlines():
  x=line.split()
  if len(x)==2:
   try:d[x[0]]=int(x[1])
   except ValueError:pass
 return d
def snap():
 r=[]
 for p in root.rglob('memory.pressure'):
  cg=p.parent; pressure=val(p);full=pressure.splitlines()[-1].split() if pressure else []
  if not full:continue
  psi={k:float(v) for k,v in [x.split('=') for x in full[1:]]}
  events=stat(cg/'memory.events.local');current=val(cg/'memory.current')
  if int(current or 0)<1024*1024 and not any(events.get(k,0) for k in ['oom','oom_kill','high','max']) and psi['avg10']==0:continue
  r.append({'path':str(cg.relative_to(root)),'memory_current':int(current or 0),'memory_max':val(cg/'memory.max'),'memory_high':val(cg/'memory.high'),'memory_low':val(cg/'memory.low'),'swap_current':int(val(cg/'memory.swap.current') or 0),'swap_max':val(cg/'memory.swap.max'),'memory_events_local':events,'swap_events':stat(cg/'memory.swap.events'),'full':psi,'io_pressure':val(cg/'io.pressure'),'memory_stat':{k:v for k,v in stat(cg/'memory.stat').items() if k in ['anon','file','kernel','pgmajfault','pgscan','pgsteal','workingset_refault_anon','workingset_refault_file']}})
 return {'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'groups':r}
a=snap();time.sleep(10);print(json.dumps({'before':a,'after':snap()}))
