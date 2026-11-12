"""PVE read-only capacity snapshot. JSON metadata only; no process arguments."""
import json,subprocess,time,re,hashlib,datetime
from pathlib import Path

def text(p):
 try:return Path(p).read_text()
 except (OSError,PermissionError):return ''
def kv(p):
 r={}
 for line in text(p).splitlines():
  a=line.replace(':','').split()
  if len(a)>1:
   try:r[a[0]]=int(a[1])*(1024 if len(a)>2 and a[2]=='kB' else 1)
   except ValueError:pass
 return r
def command(args):
 p=subprocess.run(args,capture_output=True,text=True,timeout=25);return {'returncode':p.returncode,'stdout':p.stdout}
def snapshot():
 lxc=[]
 for p in sorted(Path('/etc/pve/lxc').glob('*.conf'),key=lambda p:int(p.stem)):
  cfg={}
  for line in p.read_text().splitlines():
   k,sep,v=line.partition(': ')
   if sep and k in ['memory','swap','cores','hostname']:cfg[k]=v
  cg=Path('/sys/fs/cgroup/lxc')/p.stem
  lxc.append({'id':p.stem,'config':cfg,'config_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'running_cgroup':cg.exists(),'memory':kv(cg/'memory.stat'),'memory_current':int(text(cg/'memory.current').strip() or 0),'swap_current':int(text(cg/'memory.swap.current').strip() or 0),'events':kv(cg/'memory.events'),'memory_pressure':text(cg/'memory.pressure'),'io_pressure':text(cg/'io.pressure')})
 return {'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'meminfo':kv('/proc/meminfo'),'vmstat':kv('/proc/vmstat'),'memory_pressure':text('/proc/pressure/memory'),'io_pressure':text('/proc/pressure/io'),'cpu_pressure':text('/proc/pressure/cpu'),'lxc':lxc}
r={'before':snapshot(),'cpu':command(['lscpu']),'swap_devices':command(['swapon','--show','--bytes','--output','TYPE,SIZE,USED,PRIO']),'overcommit_memory':text('/proc/sys/vm/overcommit_memory').strip(),'overcommit_ratio':text('/proc/sys/vm/overcommit_ratio').strip(),'zfs_arc':kv('/proc/spl/kstat/zfs/arcstats'),'gpus':command(['sh','-c','lspci | grep -Ei "VGA|3D|Display"'])}
processes=[]
for p in Path('/proc').iterdir():
 if not p.name.isdigit():continue
 try:
  cg=(p/'cgroup').read_text();ct=re.search(r'/lxc/(\d+)(?:/|\n|$)',cg)
  mem=kv(p/'smaps_rollup');status=kv(p/'status')
  if mem:processes.append({'pid':int(p.name),'comm':(p/'comm').read_text().strip(),'ct':ct.group(1) if ct else None,'pss':mem.get('Pss',0),'pss_anon':mem.get('Pss_Anon',0),'pss_file':mem.get('Pss_File',0),'rss':status.get('VmRSS',0),'swap_pss':mem.get('SwapPss',0)})
 except (OSError,ProcessLookupError):pass
r['pss_sum_by_group']={}
for p in processes:
 group=p['ct'] or 'outside_lxc';entry=r['pss_sum_by_group'].setdefault(group,{'pss':0,'pss_anon':0,'pss_file':0,'swap_pss':0,'processes':0})
 for k in ['pss','pss_anon','pss_file','swap_pss']:entry[k]+=p[k]
 entry['processes']+=1
r['top_host_processes']=sorted([p for p in processes if p['ct'] is None],key=lambda p:p['pss'],reverse=True)[:15]
journal=command(['journalctl','-k','--since','2026-11-10 00:00:00 UTC','--no-pager','-g','oom-kill|Out of memory|Killed process|Memory cgroup out of memory']);lines=[x for x in journal['stdout'].splitlines() if x and not x.startswith('--')];r['recent_kernel_oom']={'returncode':journal['returncode'],'matching_lines':len(lines),'since_utc':'2026-11-10T00:00:00Z'}
r['journal_query_scope']='current retained kernel journal, not proof before retention/boot'
time.sleep(10);r['after']=snapshot();print(json.dumps(r))
