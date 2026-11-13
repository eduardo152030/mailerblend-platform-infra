"""Run inside CT627: read-only logical DB fingerprint and existing HTTP audio."""
import sqlite3,json,hashlib,urllib.request
from pathlib import Path
d=sqlite3.connect('file:/srv/voicebox/data/voicebox.db?mode=ro',uri=True);r={}
for table in ['profiles','profile_samples','generations']:
 rows=d.execute('select * from '+table+' order by id').fetchall();r[table]={'rows':len(rows),'sha256':hashlib.sha256(json.dumps(rows,default=str,ensure_ascii=False).encode()).hexdigest()}
assert d.execute('pragma integrity_check').fetchone()[0]=='ok'
http={}
for name,url in [('health','http://192.168.1.127:17493/health'),('agent','http://192.168.1.127:17493/qwen-worker/health'),('wav','http://192.168.1.127:17493/audio/baa61a95-c7b4-4524-8229-aa697b941710'),('node','http://192.168.1.127:9100/metrics'),('cadvisor','http://192.168.1.127:8085/healthz')]:
 with urllib.request.urlopen(url,timeout=20) as response:
  b=response.read();assert response.status==200
  if name=='wav':assert b[:4]==b'RIFF' and b[8:12]==b'WAVE'
  http[name]={'status':200,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()} if name=='wav' else {'status':200}
print(json.dumps({'database':r,'sqlite_integrity':'ok','http':http}))
