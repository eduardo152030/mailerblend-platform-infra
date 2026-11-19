#!/usr/bin/env python3
"""Inventario PVE de solo lectura; excluye seriales, entornos y configuración privada."""
import subprocess,json,pathlib,re
from datetime import datetime,timezone

def run(*args):return subprocess.check_output(args,text=True,timeout=30).strip()
def selected_memory():
 text=run('dmidecode','-t','17');devices=[]
 for block in text.split('Memory Device')[1:]:
  d={}
  for line in block.splitlines():
   if ':' in line:
    k,v=line.strip().split(':',1)
    if k in ['Size','Type','Speed','Configured Memory Speed','Locator','Form Factor']:d[k]=v.strip()
  devices.append(d)
 return devices
out={'time_utc':datetime.now(timezone.utc).isoformat(),'pve':run('pveversion'),'os':dict(line.split('=',1) for line in pathlib.Path('/etc/os-release').read_text().splitlines() if '=' in line),'architecture':run('uname','-m'),'kernel':run('uname','-r')}
cpu=json.loads(run('lscpu','-J'))['lscpu'];out['cpu']={r['field']:r['data'] for r in cpu if r['field'] in ['Model name:','CPU(s):','Thread(s) per core:','Core(s) per socket:','Socket(s):','CPU max MHz:','Flags:']}
out['memory_devices']=selected_memory();out['meminfo']={k:v.strip() for k,v in (line.split(':',1) for line in pathlib.Path('/proc/meminfo').read_text().splitlines()) if k in ['MemTotal','MemAvailable','SwapTotal','SwapFree']}
out['gpu_pci']=[line for line in run('lspci','-nn').splitlines() if re.search('VGA|3D controller|Display controller',line,re.I)]
out['disks']=json.loads(run('lsblk','-b','-J','-o','NAME,MODEL,SIZE,ROTA,TRAN,TYPE,MOUNTPOINT'))
out['filesystems']=run('df','-B1','-T','/','/mnt/storage');out['storage']=json.loads(run('pvesh','get','/nodes/pve/storage','--output-format','json'))
out['lvm']=json.loads(run('lvs','--units','b','--nosuffix','--reportformat','json','-o','lv_name,lv_size,pool_lv,data_percent,metadata_percent,origin'))
out['clones']={}
for ct in ['9618','9622']:
 conf=run('pct','config',ct);allowed=['hostname','onboot','rootfs','memory','cores','lock','protection']
 out['clones'][ct]={'status':run('pct','status',ct),'config':{line.split(':',1)[0]:line.split(':',1)[1].strip() for line in conf.splitlines() if line.split(':',1)[0] in allowed},'network_isolated':'ip=manual' in conf and 'link_down=1' in conf,'snapshots':run('pct','listsnapshot',ct)}
paths=list(pathlib.Path('/var/lib/vz/dump').glob('*'))
for svc in ['crm','eva']:paths+=list((pathlib.Path('/mnt/storage/mailerblend-recovery/20261102T100708Z')/svc).glob('*tar.zst*'))
out['backup_files']=[{'path':str(p),'bytes':p.stat().st_size,'mtime_utc':datetime.fromtimestamp(p.stat().st_mtime,timezone.utc).isoformat()} for p in paths if p.is_file()]
out['backup_jobs']=json.loads(run('pvesh','get','/cluster/backup','--output-format','json'))
print(json.dumps(out))
