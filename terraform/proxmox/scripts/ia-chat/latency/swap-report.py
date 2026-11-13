#!/usr/bin/env python3
"""PVE, solo lectura: swap cgroup por CT; no pct exec ni cambios de swap."""
import pathlib,json,datetime,sys,re
label=sys.argv[1];rows=[]
for p in sorted(pathlib.Path('/sys/fs/cgroup/lxc').iterdir(),key=lambda p:p.name):
 if not p.name.isdigit() or not (p/'memory.swap.current').exists():continue
 config=pathlib.Path('/etc/pve/lxc')/(p.name+'.conf');match=re.search(r'^hostname:\s*(.+)$',config.read_text(),re.M) if config.exists() else None
 rows.append({'ct_id':int(p.name),'hostname':match.group(1) if match else None,'swap_bytes':int((p/'memory.swap.current').read_text()),'memory_current':int((p/'memory.current').read_text())})
h={l.split(':')[0]:int(l.split()[1])*1024 for l in pathlib.Path('/proc/meminfo').read_text().splitlines() if l.startswith(('SwapTotal:','SwapFree:','MemAvailable:'))}
d={'label':label,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'host':h,'cts':rows,'ct_swap_sum':sum(r['swap_bytes'] for r in rows),'method':'host cgroup v2 read-only; no guest exec, no swapoff'}
p=pathlib.Path('/root/ia-local/latency')/(label+'-swap.json');p.write_text(json.dumps(d,indent=2)+'\n');print(json.dumps({'label':label,'cts_with_swap':[(r['ct_id'],round(r['swap_bytes']/1024**2,2)) for r in rows if r['swap_bytes']]}))
