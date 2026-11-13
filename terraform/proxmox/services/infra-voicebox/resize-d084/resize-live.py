"""D084: guarded, absolute online growth; run only with --execute after verified backup.
No shrink, reboot, model load, delete, global cache changes or other CT mutations.
"""
import argparse,json,subprocess,fcntl
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--execute',action='store_true');p.add_argument('--backup-receipt',type=Path,required=True);a=p.parse_args()
def call(*args):return subprocess.check_output(args,text=True,timeout=120)
with Path('/run/lock/voicebox-d084.lock').open('w') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 receipt=json.loads(a.backup_receipt.read_text());assert receipt['result']=='PASS' and receipt['full_archive_verified'] and receipt['restore_files_verified']
 archive=Path(receipt['archive']);assert archive.is_file() and str(archive).startswith('/mnt/storage/dump/')
 assert call('findmnt','-no','SOURCE','/mnt/storage').strip()=='/dev/sdb'
 assert call('pct','status','627').strip()=='status: running'
 cfg=dict(x.split(': ',1) for x in call('pct','config','627').splitlines() if ': ' in x)
 assert cfg['cores']=='3' and cfg['memory']=='15360' and cfg['swap']=='2048' and 'lock' not in cfg
 assert cfg['rootfs'] in ['local-lvm:vm-627-disk-0,size=50G','local-lvm:vm-627-disk-0,size=100G']
 assert not call('pvenode','task','list','--source','active').strip(),'Concurrent PVE task'
 stats=call('dmsetup','status','/dev/mapper/pve-data-tpool').split();used,total=map(int,stats[5].split('/'));assert used/total<.8 and 'rw' in stats
 mu,mt=map(int,stats[4].split('/'));assert mu/mt<.1
 assert not call('lvs','--noheadings','-o','lv_health_status','pve/data').strip(),'Thin pool health flag'
 pid=call('lxc-info','-n','627','-pH').strip();root=Path('/proc',pid,'root')
 jobs=root/'srv/voicebox/qwen-worker/jobs'
 assert not any(json.loads(f.read_text()).get('status') in ['running','queued'] for f in jobs.glob('*/state.json'))
 names=call('pct','exec','627','--','docker','ps','--format','{{.Names}}').splitlines()
 assert not any('qwen' in name or 'chatterbox' in name for name in names),'Active isolated worker'
 call('pct','exec','627','--','python3','-c',"import sqlite3;d=sqlite3.connect('file:/srv/voicebox/data/voicebox.db?mode=ro',uri=True);assert d.execute(\"select count(*) from generations where status in ('generating','loading_model','queued','running')\").fetchone()[0]==0")
 c=json.loads(call('pct','exec','627','--','docker','inspect','voicebox'))[0];assert c['State']['Health']['Status']=='healthy'
 assert call('systemctl','is-active','voicebox-qwen-627.service').strip()=='active'
 events=dict(x.split() for x in Path('/sys/fs/cgroup/lxc/627/memory.events').read_text().splitlines());assert events['oom']=='0' and events['oom_kill']=='0'
 sb0=dict(x.split(':',1) for x in call('dumpe2fs','-h','/dev/pve/vm-627-disk-0').splitlines() if ':' in x)
 assert sb0['Filesystem UUID'].strip()=='2c2fab31-95db-4d90-aeaf-b58fd4947d0c'
 before=int(call('blockdev','--getsize64','/dev/pve/vm-627-disk-0'));assert before in [50*2**30,100*2**30]
 assert int(sb0['Block count'])*int(sb0['Block size'])==before,'Existing LV/FS mismatch: stop, NEVER shrink'
 if before==50*2**30:
  assert cfg['rootfs'].endswith('size=50G')
  assert a.execute,'Use --execute only within D084 authorization'
  subprocess.run(['pct','resize','627','rootfs','100G'],check=True,timeout=120)
 after=int(call('blockdev','--getsize64','/dev/pve/vm-627-disk-0'));assert after==100*2**30
 sb=dict(x.split(':',1) for x in call('dumpe2fs','-h','/dev/pve/vm-627-disk-0').splitlines() if ':' in x)
 assert int(sb['Block count'])*int(sb['Block size'])==100*2**30,'Partial resize: keep LV, stop; NEVER shrink'
 assert call('lxc-info','-n','627','-pH').strip()==pid,'Unexpected CT restart'
 final=json.loads(call('pct','exec','627','--','docker','inspect','voicebox'))[0]
 assert final['Id']==c['Id'] and final['State']['StartedAt']==c['State']['StartedAt'] and final['State']['Health']['Status']=='healthy'
 print(json.dumps({'result':'PASS','changed':before!=after,'before_bytes':before,'after_bytes':after,'ct_pid':pid,'filesystem_bytes':int(sb['Block count'])*int(sb['Block size']),'uuid':sb['Filesystem UUID'].strip(),'same_app_id_and_started_at':True}))
