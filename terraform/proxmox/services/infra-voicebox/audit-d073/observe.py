"""Read-only 60-second host/CT627/known-pressure group observation."""
from pathlib import Path
import json,time,datetime
root=Path('/sys/fs/cgroup/lxc');paths={'627':root/'627','618_cadvisor':root/'618/ns/system.slice/docker-7a110a7339fe9762643a954d11511e0002fb5708773ad06baa9f59d8f8aec4dc.scope'}
def rd(p):
 try:return p.read_text()
 except OSError:return ''
def nums(p):return {x.split()[0].rstrip(':'):int(x.split()[1]) for x in rd(p).splitlines() if len(x.split())>1 and x.split()[1].isdigit()}
def sample():
 return {'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'time':time.monotonic(),'meminfo_kib':nums(Path('/proc/meminfo')),'vmstat':{k:v for k,v in nums(Path('/proc/vmstat')).items() if k in ['pswpin','pswpout','pgscan_kswapd','pgscan_direct','allocstall_normal','pgmajfault','oom_kill']},'host_memory_pressure':rd(Path('/proc/pressure/memory')),'host_io_pressure':rd(Path('/proc/pressure/io')),'groups':{name:{'memory':int(rd(p/'memory.current') or 0),'swap':int(rd(p/'memory.swap.current') or 0),'pressure':rd(p/'memory.pressure'),'events':nums(p/'memory.events.local')} for name,p in paths.items()}}
r=[]
for n in range(31):
 r.append(sample())
 if n<30:time.sleep(2)
print(json.dumps(r))
