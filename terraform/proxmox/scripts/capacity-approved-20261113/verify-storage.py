#!/usr/bin/env python3
"""PVE: segunda revisión de sololectura; no repite destroy, copy ni unlink."""
import pathlib,json,subprocess
from datetime import datetime,timezone
base=pathlib.Path('/mnt/storage/capacity-approved-20261113');receipt=json.loads((base/'execution.json').read_text());assert receipt['status']=='DONE'
for ct in [9618,9622]:
 assert not pathlib.Path(f'/etc/pve/lxc/{ct}.conf').exists()
 volumes=subprocess.check_output(['pvesm','list','local-lvm','--vmid',str(ct)],text=True)
 assert f'local-lvm:vm-{ct}-disk-0' not in volumes
 assert (base/f'{ct}.conf').is_file()
source=pathlib.Path('/var/lib/vz/dump/vzdump-qemu-100-2025_03_23-23_03_29.vma.zst');assert not source.exists()
dest=pathlib.Path('/mnt/storage/dump')/source.name
verified=next(s for s in receipt['stages'] if s['stage']=='vm100_copy_checksum_PASS')
assert dest.stat().st_size==verified['bytes']
assert pathlib.Path(str(dest)+'.sha256').read_text().split()[0]==verified['sha256']
for s in receipt['stages']:
 if s['stage']=='source_checksum_PASS':
  ct=s['production_ct'];svc='crm' if ct==618 else 'eva'
  files=list((pathlib.Path('/mnt/storage/mailerblend-recovery/20261102T100708Z')/svc).glob('*.tar.zst'))
  assert len(files)==1 and files[0].stat().st_size==s['bytes']
print(json.dumps({'time_utc':datetime.now(timezone.utc).isoformat(),'status':'PASS','mode':'read-only second review','clones_absent':[9618,9622],'source_backups_preserved':[618,622],'vm100_destination_present':True,'vm100_source_absent':True,'new_changes':False}))
