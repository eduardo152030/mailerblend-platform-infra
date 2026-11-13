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

# Optional recovery baseline: compare protected original rows and each original audio.
import argparse
parser=argparse.ArgumentParser();parser.add_argument('--baseline',type=Path);args=parser.parse_args()
if args.baseline:
    base=args.baseline;assert base.parent==Path('/opt/voicebox/backups') and base.name=='input1200-before-deploy'
    prior=sqlite3.connect('file:'+str(base/'data/voicebox.db')+'?mode=ro',uri=True)
    for table in ['profiles','profile_samples']:
        assert prior.execute('select * from '+table+' order by id').fetchall()==d.execute('select * from '+table+' order by id').fetchall(),'Protected profile/reference changed'
    columns=[r[1] for r in d.execute('pragma table_info(generations)')];index=columns.index('id')
    live={row[index]:row for row in d.execute('select * from generations')}
    for row in prior.execute('select * from generations'):assert live.get(row[index])==row,'Historical generation changed'
    count=0
    assert prior.execute("select count(*) from generations where status='completed' and coalesce(trim(audio_path),'')=''").fetchone()[0]==0
    for table in ['generations','profile_samples']:
        for (name,) in prior.execute("select audio_path from "+table+" where audio_path is not null and trim(audio_path)!=''"):
            rel=Path(name)
            if rel.is_absolute():rel=rel.relative_to('/app/data')
            elif rel.parts[0]=='data':rel=Path(*rel.parts[1:])
            assert '..' not in rel.parts
            a=base/'data'/rel;b=Path('/srv/voicebox/data')/rel
            assert hashlib.sha256(a.read_bytes()).digest()==hashlib.sha256(b.read_bytes()).digest(),'Original audio changed';count+=1
    print(json.dumps({'baseline_profile_reference_and_history_unchanged':True,'original_audio_hashes_checked':count}))
