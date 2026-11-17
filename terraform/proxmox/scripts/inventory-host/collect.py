#!/usr/bin/env python3
"""Lecturas PVE; salida filtrada sin entornos, comandos de procesos ni credenciales."""
import subprocess as s,json,pathlib as P,re,shutil,datetime
out={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'missing':[]}
def run(*a):
 if not shutil.which(a[0]):
  out['missing'].append(a[0]);return 'no disponible'
 try:
  p=s.run(a,text=True,capture_output=True,timeout=45)
  return p.stdout.strip() if p.returncode==0 else 'no disponible (comando fallido)'
 except s.TimeoutExpired:return 'no disponible (timeout)'
def read(p):
 try:return P.Path(p).read_text().strip()
 except OSError:return 'no disponible'
def js(*a):
 try:return json.loads(run(*a))
 except ValueError:return []
assert run('id','-u')=='0' and P.Path('/etc/pve').is_dir()
for k,a in {'pve':['pveversion','-v'],'kernel':['uname','-r'],'hostname':['hostname'],'cpu':['lscpu'],'free':['free','-h'],'swap':['swapon','--show'],'pvs':['pvs'],'vgs':['vgs'],'lvs':['lvs','-a','-o','lv_name,vg_name,lv_size,data_percent,metadata_percent,pool_lv'],'df':['df','-hT','-x','tmpfs','-x','devtmpfs'],'storage_status':['pvesm','status'],'gpu':['lspci','-nn'],'network':['ip','-br','a'],'uptime':['uptime'],'processes':['ps','-eo','pid,user,comm,rss,pcpu,pmem','--sort=-rss']}.items():out[k]=run(*a)
out['pve']='\n'.join(out['pve'].splitlines()[:5]);out['gpu']='\n'.join(x for x in out['gpu'].splitlines() if re.search('vga|3d|display',x,re.I));out['processes']='\n'.join(out['processes'].splitlines()[:11])
out['top']='\n'.join(run('top','-bn1').splitlines()[:20]) # solo cabecera: evitar argumentos privados
out['meminfo']=read('/proc/meminfo');out['governor']=read('/sys/devices/system/cpu/cpufreq/policy0/scaling_governor')
out['dmi']=re.sub(r'(?m)^\s*(Serial Number|Asset Tag|Part Number):.*$','',run('dmidecode','-t','memory'))
out['ksm']=read('/sys/kernel/mm/ksm/pages_sharing');out['ksmtuned']=s.run(['systemctl','is-active','ksmtuned'],text=True,capture_output=True,timeout=15).stdout.strip();out['qm_list']=run('qm','list');out['pct_list']=run('pct','list')
out['arcstats']='\n'.join(x for x in read('/proc/spl/kstat/zfs/arcstats').splitlines() if x.split() and x.split()[0] in ['size','c_min','c_max'])
out['zfs_conf']='\n'.join(x for x in read('/etc/modprobe.d/zfs.conf').splitlines() if re.match(r'^\s*options\s+zfs\s',x))
n=out['hostname'];out['guests']=[]
for typ,cli in [('qemu','qm'),('lxc','pct')]:
 for g in js('pvesh','get',f'/nodes/{n}/{typ}','--output-format','json'):
  d={k:g.get(k) for k in ['vmid','name','status','mem','maxmem','cpus']};d['type']=typ
  conf=run(cli,'config',str(g['vmid']));d['config']={}
  for line in conf.splitlines():
   if ':' not in line:continue
   k,v=line.split(':',1)
   if k in ['memory','balloon','swap','cores','sockets','onboot','rootfs'] or re.fullmatch(r'(scsi|sata|virtio|ide|mp|unused)\d+',k):d['config'][k]=v.strip()
  out['guests'].append(d)
status=js('pvesh','get',f'/nodes/{n}/status','--output-format','json');out['node']={k:status.get(k) for k in ['memory','cpu','loadavg','swap']} if isinstance(status,dict) else {}
out['storages']=js('pvesh','get',f'/nodes/{n}/storage','--output-format','json')
out['storage_cfg']='\n'.join(x for x in read('/etc/pve/storage.cfg').splitlines() if re.match(r'^\S+:\s|^\s+(path|vgname|thinpool|pool|content|nodes|disable|shared|is_mountpoint)\s',x))
out['disks']=js('lsblk','-b','-J','-o','NAME,SIZE,TYPE,ROTA,TRAN,MODEL,SERIAL,FSTYPE,MOUNTPOINTS')
def sanitize(ds):
 for d in ds:
  if d.get('serial'):d['serial']='…'+d['serial'][-4:]
  sanitize(d.get('children',[]))
if isinstance(out['disks'],dict):sanitize(out['disks'].get('blockdevices',[]))
out['smart']={}
for d in out.get('disks',{}).get('blockdevices',[]):
 if d['type']!='disk':continue
 dev='/dev/'+d['name'];raw=run('smartctl','-H','-A',dev)
 out['smart'][dev]='\n'.join(x for x in raw.splitlines() if re.search('overall-health|Health Status|Power_On|Reallocat|Percent_Lifetime|Ave_Block|Wear_Level|Percentage|Media_Wear|Available_Reserv|Pending_Sector|Offline_Uncorrect',x)) or raw if raw.startswith('no disponible') else '\n'.join(x for x in raw.splitlines() if re.search('overall-health|Health Status|Power_On|Reallocat|Percent_Lifetime|Ave_Block|Wear_Level|Percentage|Media_Wear|Available_Reserv|Pending_Sector|Offline_Uncorrect',x))
 if d['name'].startswith('nvme'):out['smart'][dev]+='\n'+run('nvme','smart-log',dev)
out['lvm_json']=js('lvs','--units','b','--nosuffix','--reportformat','json','-o','lv_name,vg_name,lv_size,data_percent,metadata_percent,pool_lv')
if P.Path('/proc/spl/kstat/zfs').exists():
 out['zpool']=run('zpool','list','-v');out['zpool_status']=run('zpool','status');out['zfs']=run('zfs','list','-o','name,used,avail,refer,compression,compressratio,mountpoint')
else:out['zfs']='No hay ZFS activo.'
out['directories']={str(p):run('du','-sh','-x',str(p)) for p in [P.Path('/srv'),P.Path('/var/lib/vz'),*P.Path('/mnt').glob('*')] if p.is_dir()}
lines=read('/etc/network/interfaces').splitlines();bridges=[];keep=False
for x in lines:
 if x.startswith('iface '):keep=' vmbr' in x or ' br' in x
 if keep:bridges.append(x)
out['bridges']='\n'.join(bridges);out['links']={p.name:run('ethtool',p.name) for p in P.Path('/sys/class/net').iterdir() if (p/'device').exists()};out['links']={k:'\n'.join(x.strip() for x in v.splitlines() if 'Speed:' in x) for k,v in out['links'].items()}
print(json.dumps(out,ensure_ascii=False,indent=2))
