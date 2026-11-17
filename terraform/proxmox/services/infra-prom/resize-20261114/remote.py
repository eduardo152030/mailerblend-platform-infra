"""Ampliación online exclusiva610: destino absoluto, backup completo, nunca encoger."""
import argparse, datetime, fcntl, hashlib, json, pathlib, subprocess
p=argparse.ArgumentParser();p.add_argument('--target',type=int,required=True);p.add_argument('--execute',action='store_true');a=p.parse_args()
assert a.target==25

def run(*args,timeout=120):
 return subprocess.check_output(args,text=True,timeout=timeout).strip()
def config():
 return json.loads(run('pvesh','get','/nodes/pve/lxc/610/config','--output-format','json'))
def protected():
 return {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in pathlib.Path('/etc/pve/lxc').glob('*.conf') if p.stem!='610'}
def ids():
 return run('pct','exec','610','--','docker','ps','--no-trunc','--format','{{.Names}}|{{.ID}}|{{.Status}}').splitlines()
def identities():
 names=run('pct','exec','610','--','docker','ps','--format','{{.Names}}').splitlines()
 return run('pct','exec','610','--','docker','inspect','--format','{{.Name}}|{{.Id}}|{{.State.StartedAt}}|{{.RestartCount}}|{{.State.Running}}',*sorted(names))
def filesystem():
 return json.loads(run('pct','exec','610','--','python3','-c',"import os,json;s=os.statvfs('/');print(json.dumps({'total':s.f_blocks*s.f_frsize,'available':s.f_bavail*s.f_frsize,'free_percent':100*s.f_bavail/s.f_blocks}))"))
def health():
 for port in [9090,9093]:
  assert run('pct','exec','610','--','curl','-fsS',f'http://127.0.0.1:{port}/-/ready')
def fsbytes():
 fields=dict(line.split(':',1) for line in run('dumpe2fs','-h','/dev/pve/vm-610-disk-0').splitlines() if ':' in line)
 return int(fields['Block count'])*int(fields['Block size'])
with pathlib.Path('/run/lock/ct610-disk-20261114.lock').open('w') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 cfg=config();assert cfg['hostname']=='infra-prom' and 'lock' not in cfg
 assert cfg['rootfs'] in ['local-lvm:vm-610-disk-0,size=10G','local-lvm:vm-610-disk-0,size=25G']
 assert run('pct','status','610')=='status: running'
 assert run('pct','exec','610','--','findmnt','-no','FSTYPE','/')=='ext4'
 assert not json.loads(run('pvenode','task','list','--source','active','--output-format','json'))
 stats=run('dmsetup','status','/dev/mapper/pve-data-tpool').split()
 used,total=map(int,stats[5].split('/'));mu,mt=map(int,stats[4].split('/'))
 assert used/total<.8 and mu/mt<.1 and 'rw' in stats
 assert (total-used)*512*128 > 30*2**30, 'Require at least30GiB pool headroom'
 assert not run('lvs','--noheadings','-o','lv_health_status','pve/data')
 original=protected();identity=identities();pid=run('lxc-info','-n','610','-pH');health()
 before=int(run('blockdev','--getsize64','/dev/pve/vm-610-disk-0'));assert before in [10*2**30,25*2**30]
 assert fsbytes()==before
 pre=filesystem();changed=before!=25*2**30
 backup=None
 if a.execute and changed:
  assert run('findmnt','-no','SOURCE','/mnt/storage')=='/dev/sdb'
  stat=__import__('os').statvfs('/mnt/storage');assert stat.f_bavail*stat.f_frsize>30*2**30
  private=pathlib.Path('/mnt/storage/ct610-disk-20261114');private.mkdir(mode=0o700,exist_ok=True)
  stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
  (private/(stamp+'-config.json')).write_text(json.dumps(cfg));(private/(stamp+'-config.json')).chmod(0o600)
  existing=set(pathlib.Path('/mnt/storage/dump').glob('vzdump-lxc-610-*.tar.zst'))
  with (private/(stamp+'-vzdump.log')).open('w') as log:
   (private/(stamp+'-vzdump.log')).chmod(0o600)
   subprocess.run(['vzdump','610','--mode','snapshot','--storage','storage','--compress','zstd','--bwlimit','30000','--remove','0'],stdout=log,stderr=log,check=True,timeout=1800)
  candidates=set(pathlib.Path('/mnt/storage/dump').glob('vzdump-lxc-610-*.tar.zst'))-existing;assert len(candidates)==1
  archive=candidates.pop();archive.chmod(0o600)
  sha=hashlib.sha256()
  with archive.open('rb') as f:
   for block in iter(lambda:f.read(8*1024**2),b''):sha.update(block)
  subprocess.run(['zstd','-q','-t',str(archive)],check=True,timeout=600)
  with (private/(stamp+'-archive-list.txt')).open('w') as listing:
   subprocess.run(['tar','--zstd','-tf',str(archive)],stdout=listing,check=True,timeout=600)
  listing=(private/(stamp+'-archive-list.txt')).read_text();assert 'etc/vzdump/pct.conf' in listing and ('etc/prometheus' in listing or 'opt/infra-prom' in listing)
  extracted=run('tar','--zstd','-xOf',str(archive),'./etc/vzdump/pct.conf',timeout=600)
  assert 'hostname: infra-prom' in extracted
  backup={'archive':str(archive),'bytes':archive.stat().st_size,'sha256':sha.hexdigest(),'full_zstd_and_tar_read':True,'config_extract_verified':True,'functional_restore_test':False}
  (private/(stamp+'-receipt.json')).write_text(json.dumps(backup));(private/(stamp+'-receipt.json')).chmod(0o600)
  assert config()==cfg and protected()==original and identities()==identity
  subprocess.run(['pct','resize','610','rootfs',str(a.target)+'G'],check=True,stdout=subprocess.DEVNULL,timeout=120)
 after=int(run('blockdev','--getsize64','/dev/pve/vm-610-disk-0'));final=config()
 if a.execute:assert after==25*2**30 and final['rootfs'].endswith('size=25G')
 assert fsbytes()==after, 'Partial resize: STOP; NEVER shrink'
 assert {k:v for k,v in cfg.items() if k not in ['rootfs','digest']}=={k:v for k,v in final.items() if k not in ['rootfs','digest']}
 assert protected()==original and identities()==identity and run('lxc-info','-n','610','-pH')==pid
 health();post=filesystem()
 if a.execute:assert post['free_percent']>15
 print(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'ct':610,'before_bytes':before,'after_bytes':after,'filesystem_bytes':fsbytes(),'before':pre,'after':post,'writes':int(a.execute and changed),'backup':backup,'same_ct_pid_and_container_identities':True,'other_ct_configs_unchanged':True,'prometheus_alertmanager_ready':True}))
