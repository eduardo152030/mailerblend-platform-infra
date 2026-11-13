"""CT627-only private clone of binds for startup; no source writes or model loads."""
from pathlib import Path
import os,json,shutil,sqlite3,socket
assert socket.gethostname()=='infra-voicebox'
base=Path('/srv/voicebox/chatterbox-d085/startup-validation');assert not base.exists()
st=os.statvfs('/');assert st.f_bavail*st.f_frsize>25*2**30
base.mkdir(mode=0o700)
db=sqlite3.connect('file:/srv/voicebox/data/voicebox.db?mode=ro',uri=True)
assert db.execute("select count(*) from generations where status in ('generating','loading_model')").fetchone()[0]==0
sources={
 'data':Path('/srv/voicebox/data'),
 'huggingface':Path('/srv/voicebox/huggingface'),
 'jobs':Path('/srv/voicebox/qwen-worker/jobs')}
counts={}
for name,source in sources.items():
 target=base/name
 ignore=shutil.ignore_patterns('voicebox.db','voicebox.db-wal','voicebox.db-shm') if name=='data' else None
 shutil.copytree(source,target,symlinks=True,ignore=ignore)
 # copy2 preserves modes/times, ownership must be reproduced explicitly.
 for path in [target,*target.rglob('*')]:
  original=source/path.relative_to(target);s=original.lstat();os.chown(path,s.st_uid,s.st_gid,follow_symlinks=False)
  if not path.is_symlink():assert path.stat().st_mode&0o7777==s.st_mode&0o7777
 counts[name]=sum(p.is_file() for p in target.rglob('*'))
# Reject links that could escape the private clone before starting any test app.
for path in base.rglob('*'):
 if path.is_symlink():assert path.resolve().is_relative_to(base),str(path)
dest=base/'data/voicebox.db';out=sqlite3.connect(dest);db.backup(out);assert out.execute('pragma integrity_check').fetchone()[0]=='ok';out.close();db.close()
s=Path('/srv/voicebox/data/voicebox.db').stat();os.chown(dest,s.st_uid,s.st_gid);dest.chmod(s.st_mode&0o7777)
print(json.dumps({'fixture_root':str(base),'files':counts,'sqlite_integrity':'ok','source_writes':0,'model_loads':0,'personal_audio_copies_private':True,'owners_modes_preserved':True}))
