"""PVE: verify full HDD backup and isolated directory restore, never start a CT."""
from pathlib import Path
import argparse,subprocess,json,hashlib,sqlite3,wave,datetime,os
p=argparse.ArgumentParser();p.add_argument('archive',type=Path);p.add_argument('baseline',type=Path);a=p.parse_args()
assert a.archive.parent==Path('/mnt/storage/dump') and a.archive.name.startswith('vzdump-lxc-627-')
base=Path('/mnt/storage/d084-627');out=base/'restore-rootfs';assert not out.exists()
assert subprocess.check_output(['findmnt','-no','SOURCE','/mnt/storage'],text=True).strip()=='/dev/sdb'
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return h.hexdigest()
# One sequential read: SHA256, zstd frame integrity and full tar extraction.
# --ignore-zeros consumes through stream EOF; no decompressed bytes go to logs.
out.mkdir(mode=0o700)
h=hashlib.sha256()
decoder=subprocess.Popen(['nice','-n','10','zstd','--decompress','--stdout'],stdin=subprocess.PIPE,stdout=subprocess.PIPE)
extractor=subprocess.Popen(['nice','-n','10','tar','--extract','--ignore-zeros','--file','-','--directory',str(out),'--numeric-owner','--same-owner','--acls','--xattrs','--sparse'],stdin=decoder.stdout)
decoder.stdout.close()
try:
 with a.archive.open('rb') as f:
  for chunk in iter(lambda:f.read(4*1024*1024),b''):
   h.update(chunk);decoder.stdin.write(chunk)
 decoder.stdin.close()
 assert decoder.wait()==0,'zstd frame integrity/decompression failure'
 assert extractor.wait()==0,'full directory extraction failed'
finally:
 for process in [decoder,extractor]:
  if process.poll() is None:process.kill();process.wait()
sha=h.hexdigest()
b=json.loads(a.baseline.read_text());verified=0
for name,expected in b['files'].items():
 f=out/name;assert f.is_file(),name
 assert digest(f)==expected,name
 verified+=1
assert (out/'etc/vzdump/pct.conf').is_file()
db=sqlite3.connect('file:'+str(out/'srv/voicebox/data/voicebox.db')+'?mode=ro',uri=True)
assert db.execute('pragma integrity_check').fetchone()[0]=='ok'
assert db.execute("select count(*) from profiles where id='1fd00418-2a79-4178-883f-af6c3f5e07ee'").fetchone()[0]==1
rows=db.execute("select audio_path from generations where status='completed'").fetchall();refs=db.execute('select audio_path from profile_samples').fetchall()
for (name,) in rows+refs:
 path=Path(name)
 if path.is_absolute():path=path.relative_to('/app/data')
 elif path.parts[0]=='data':path=Path(*path.parts[1:])
 f=out/'srv/voicebox/data'/path;assert f.is_file()
 with wave.open(str(f)) as w:assert w.getnframes()>0
# Hash both large Qwen files and require snapshot symlink resolves within restored HF.
pid=subprocess.check_output(['lxc-info','-n','627','-pH'],text=True).strip();live=Path('/proc',pid,'root')
model=Path('srv/voicebox/huggingface/hub/models--Qwen--Qwen3-TTS-12Hz-0.6B-Base/snapshots/5d83992436eae1d760afd27aff78a71d676296fc')
model_hashes={}
for name in ['model.safetensors','speech_tokenizer/model.safetensors','config.json']:
 f=out/model/name;assert f.resolve().is_relative_to(out)
 model_hashes[name]=digest(f);assert model_hashes[name]==digest(live/model/name)
for rel in ['srv/voicebox/private-originals','srv/voicebox/qwen-worker/jobs']:
 assert (out/rel).stat().st_mode&0o777==0o700
r={'result':'PASS','at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'archive':str(a.archive),'archive_bytes':a.archive.stat().st_size,'archive_sha256':sha,'full_archive_verified':True,'full_directory_extraction':True,'restore_files_verified':verified,'sqlite_integrity':'ok','eduardo_profile':True,'completed_wavs':len(rows),'reference_wavs':len(refs),'model_hashes_verified':model_hashes,'restore_root':str(out),'boot_restore_executed':False,'production_untouched':True}
(base/'verified.json').write_text(json.dumps(r,indent=2)+'\n');(base/'verified.json').chmod(0o600)
print(json.dumps(r))
