"""PVE read-only SSD/thin-pool audit. No resize, trim, repair or state changes."""
import json,subprocess,datetime
from pathlib import Path

def run(args):
    r=subprocess.run(args,capture_output=True,text=True,timeout=30)
    return {'code':r.returncode,'output':r.stdout,'error':r.stderr[:300]}
commands={
'pvesm':['pvesm','status'],
'vgs':['vgs','--reportformat','json','--units','b','--nosuffix','-o','vg_name,vg_size,vg_free,vg_extent_size,vg_extent_count,vg_free_count'],
'lvs':['lvs','-a','--reportformat','json','--units','b','--nosuffix','-o','lv_name,vg_name,lv_attr,lv_size,pool_lv,origin,data_percent,metadata_percent,lv_health_status,segtype'],
'pvs':['pvs','--reportformat','json','--units','b','--nosuffix','-o','pv_name,vg_name,pv_size,pv_free'],
'pool_status':['dmsetup','status','/dev/mapper/pve-data-tpool'],
'pool_table':['dmsetup','table','/dev/mapper/pve-data-tpool'],
'lvm_policy':['lvmconfig','--type','full','activation/thin_pool_autoextend_threshold','activation/thin_pool_autoextend_percent','activation/monitoring'],
'pool_monitor':['lvs','--noheadings','-o','lv_name,seg_monitor','pve/data'],
'ct_snapshots':['pct','listsnapshot','627']}
result={'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),**{k:run(v) for k,v in commands.items()}}
r=run(['dumpe2fs','-h','/dev/pve/vm-627-disk-0']);result['ext4']={}
for line in r['output'].splitlines():
 if ':' in line:
  k,v=line.split(':',1)
  if k in ['Filesystem features','Filesystem state','Errors behavior','Block count','Reserved block count','Free blocks','Block size','Reserved GDT blocks']:result['ext4'][k]=v.strip()
result['block_device_bytes']=int(subprocess.check_output(['blockdev','--getsize64','/dev/pve/vm-627-disk-0'],text=True))
print(json.dumps(result))
