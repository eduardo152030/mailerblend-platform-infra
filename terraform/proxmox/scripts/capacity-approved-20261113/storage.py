#!/usr/bin/env python3
"""PVE: limpieza autorizada13nov2026. Validar fuentes antes de destroy/unlink.
Clones exclusivos9618/9622, backup100 trasladado con SHA256 y VMAverify.
No toca respaldos618/622, datosproductivos ni imágenes de rollback.
"""
import subprocess,pathlib,hashlib,json,os,tarfile,time,re
from datetime import datetime,timezone
BASE=pathlib.Path('/mnt/storage/capacity-approved-20261113');BASE.mkdir(mode=0o700,exist_ok=True)
LOG=BASE/'execution.json';result={'status':'IN PROGRESS','stages':[]}
def save(stage,**kw):
 result.update(time_utc=datetime.now(timezone.utc).isoformat());result['stages'].append({'stage':stage,**kw});LOG.write_text(json.dumps(result,indent=2));LOG.chmod(0o600);print(json.dumps(result['stages'][-1]),flush=True)
def run(*args):return subprocess.check_output(args,text=True,timeout=60).strip()
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while b:=f.read(8*1024**2):h.update(b)
 return h.hexdigest()
def capacity():return {'df':run('df','-B1','/','/mnt/storage'),'pool':json.loads(run('lvs','pve/data','--units','b','--nosuffix','--reportformat','json','-o','lv_size,data_percent,metadata_percent'))}
def production():
 out={}
 for ct in [618,622]:
  p=run('pct','exec',str(ct),'--','docker','ps','--format','{{.ID}} {{.Names}} {{.Status}}');out[str(ct)]=p
 return out
assert run('mountpoint','-q','/mnt/storage')==''
assert os.stat('/mnt/storage').st_dev!=os.stat('/').st_dev
before=capacity();prod=production();save('preflight',capacity=before)
# Las configuraciones privadas y su checksum quedan enHDD antes de destrucción.
configs={}
for ct,name in [(9618,'crm-recovery-9618'),(9622,'eva-recovery-9622')]:
 conf=run('pct','config',str(ct));assert 'status: stopped'==run('pct','status',str(ct))
 assert f'hostname: {name}' in conf and 'onboot: 0' in conf and 'ip=manual' in conf and 'link_down=1' in conf
 assert not re.search(r'^(mp\d+|unused\d+|lock):',conf,re.M)
 assert f'rootfs: local-lvm:vm-{ct}-disk-0,' in conf
 snapshots=json.loads(run('pvesh','get',f'/nodes/pve/lxc/{ct}/snapshot','--output-format','json'));assert all(s['name']=='current' for s in snapshots)
 p=BASE/f'{ct}.conf';assert not p.exists();p.write_text(conf+'\n');p.chmod(0o600);configs[ct]=conf;assert p.read_text()==conf+'\n'
 save('clone_config_saved',ct=ct,sha256=digest(p))
for svc,ct,filename in [('crm',618,'vzdump-lxc-618-2026_11_02-11_09_28.tar.zst'),('eva',622,'vzdump-lxc-622-2026_11_02-11_41_01.tar.zst')]:
 p=pathlib.Path('/mnt/storage/mailerblend-recovery/20261102T100708Z')/svc/filename
 expected=pathlib.Path(str(p)+'.sha256').read_text().split()[0];assert re.fullmatch('[0-9a-f]{64}',expected)
 sha=digest(p);assert sha==expected
 save('source_checksum_PASS',production_ct=ct,sha256=sha,bytes=p.stat().st_size)
 proc=subprocess.Popen(['zstd','-q','-d','-c',str(p)],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
 found=False;count=0
 try:
  with tarfile.open(fileobj=proc.stdout,mode='r|') as tar:
   for m in tar:
    count+=1
    if m.name.lstrip('./')=='etc/vzdump/pct.conf':found=True
  # Consumir posiblepadding, comprobandoCRC/EOF delzstd entero.
  while proc.stdout.read(8*1024**2):pass
 finally:proc.stdout.close()
 assert proc.wait()==0 and found and count>100
 save('source_archive_readable_PASS',production_ct=ct,entries=count)
# La autorización retira clones obsoletos usados enensayos; no se restauran ni arrancan.
for ct in [9618,9622]:
 assert run('pct','config',str(ct))==configs[ct]
 assert run('pct','status',str(ct))=='status: stopped'
 # No referenciar volumen declone desde otroCT.
 vol=f'local-lvm:vm-{ct}-disk-0'
 for f in pathlib.Path('/etc/pve/lxc').glob('*.conf'):
  if f.stem!=str(ct):assert vol not in f.read_text()
 run('pct','destroy',str(ct))
 assert not pathlib.Path(f'/etc/pve/lxc/{ct}.conf').exists()
 assert vol not in run('pvesm','list','local-lvm','--vmid',str(ct))
 save('clone_removed',ct=ct)
# Verificar aplicacionesoriginales poridentidad y estado, sin comparar duraciónhumanizada.
afterprod=production()
for ct in prod:
 old={tuple(l.split()[:2]) for l in prod[ct].splitlines()};new={tuple(l.split()[:2]) for l in afterprod[ct].splitlines()};assert old==new
save('clones_complete',capacity=capacity(),production_ids_unchanged=True)
source=pathlib.Path('/var/lib/vz/dump/vzdump-qemu-100-2025_03_23-23_03_29.vma.zst')
dest=pathlib.Path('/mnt/storage/dump')/source.name;temp=pathlib.Path(str(dest)+'.copying-20261113')
assert source.is_file() and not dest.exists() and not temp.exists()
stat=source.stat();assert os.statvfs(dest.parent).f_bavail*os.statvfs(dest.parent).f_frsize>stat.st_size+10*1024**3
h=hashlib.sha256();copied=0;last=time.monotonic()
with source.open('rb') as src,temp.open('xb') as dst:
 os.chmod(temp,0o600)
 while block:=src.read(8*1024**2):
  dst.write(block);h.update(block);copied+=len(block)
  if time.monotonic()-last>=45:save('copy_progress',bytes=copied,total=stat.st_size);last=time.monotonic()
 dst.flush();os.fsync(dst.fileno())
assert temp.stat().st_size==stat.st_size
sha=h.hexdigest();assert digest(temp)==sha
save('vm100_copy_checksum_PASS',bytes=stat.st_size,sha256=sha)
# VMA verificaCRC deimagen completa. Salida privada nunca seimprime.
with (BASE/'vma-verify.private.log').open('wb') as log:
 os.chmod(BASE/'vma-verify.private.log',0o600)
 dec=subprocess.Popen(['zstd','-q','-d','-c',str(temp)],stdout=subprocess.PIPE,stderr=log)
 verify=subprocess.Popen(['vma','verify','-'],stdin=dec.stdout,stdout=log,stderr=log)
 dec.stdout.close();vrc=verify.wait();drc=dec.wait()
assert vrc==0 and drc==0,'VMAverify falló: conservarorigen ycopiatemporal'
assert source.stat().st_size==stat.st_size and source.stat().st_mtime_ns==stat.st_mtime_ns and source.stat().st_ino==stat.st_ino
# Publicación connombre exacto noexistente; todo está en mismoFSdestino.
os.link(temp,dest);temp.unlink();assert dest.stat().st_size==stat.st_size
(pathlib.Path(str(dest)+'.sha256')).write_text(sha+'  '+dest.name+'\n')
save('vm100_archive_readable_PASS',destination=str(dest),sha256=sha)
source.unlink()
assert not source.exists() and dest.exists()
result['status']='DONE';save('complete',capacity=capacity(),vm100_preserved=str(dest),source_removed=True)
