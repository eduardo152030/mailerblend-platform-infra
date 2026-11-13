"""Metadata/read-only probe through real entrypoint against actual production binds.
Not a server startup test: real Uvicorn startup is separately tested on safe clones.
"""
import os,json
from pathlib import Path
assert os.geteuid()==999 and os.getegid()==999
paths={}
for name in ['/app/backend','/app/backend/config.py','/app/backend/models.py','/app/backend/backends/isolated_backend.py','/app/data','/app/data/voicebox.db','/app/data/cache','/app/data/cache/numba','/app/data/profiles','/app/data/generations','/qwen-jobs','/home/voicebox/.cache','/home/voicebox/.cache/huggingface']:
 p=Path(name);s=p.stat();paths[name]={'uid':s.st_uid,'gid':s.st_gid,'mode':oct(s.st_mode&0o777),'read':os.access(p,os.R_OK),'write':os.access(p,os.W_OK)}
 if p.is_dir():assert os.access(p,os.R_OK|os.X_OK)
 else:
  fd=os.open(p,os.O_RDONLY);os.close(fd)
for name in ['/app/data','/app/data/voicebox.db','/app/data/cache','/app/data/profiles','/app/data/generations','/qwen-jobs','/home/voicebox/.cache','/home/voicebox/.cache/huggingface']:assert paths[name]['write']
print(json.dumps({'result':'PASS','uid':os.geteuid(),'gid':os.getegid(),'paths':paths,'writes_performed':0,'modules_and_config_readable':True,'db_readable_and_writable_by_dac':True}))
