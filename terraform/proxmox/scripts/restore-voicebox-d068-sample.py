#!/usr/bin/env python3
"""Non-destructive recovery of one original D063 sample, UUID and relational metadata.
Only CT627; never roll back the full DB or overwrite newer records/audio.
"""
import base64,hashlib,json,sqlite3,subprocess
from pathlib import Path
P=Path.home()/'.local/share/mailerblend-recovery/voicebox-d068';IDENT='5385d04b-49fa-4b0f-a001-1cebaf55b854';WANTED='d53665d3932c4b96fe7497587f57215e70b0b2cf8a5c9a290896665961cf2cfe';snapshot=P/'restore-before/snapshot'
assert json.loads((P/'restore-before/restore-check.json').read_text())['result']=='PASS'
db=sqlite3.connect('file:'+str(snapshot/'data/voicebox.db')+'?mode=ro',uri=True);db.row_factory=sqlite3.Row
rows=[];seen=set()
def collect(table,record):
 if record is None:return
 key=(table,json.dumps(dict(record),sort_keys=True,default=str))
 if key in seen:return
 seen.add(key)
 for fk in db.execute('pragma foreign_key_list("'+table+'")'):
  value=record[fk['from']]
  if value is not None:
   parent=db.execute('select * from "'+fk['table']+'" where "'+fk['to']+'"=?',(value,)).fetchone();collect(fk['table'],parent)
 rows.append({'table':table,'row':dict(record)})
record=db.execute('select * from generations where id=?',(IDENT,)).fetchone();assert record and record['status']=='completed';collect('generations',record)
for (table,) in db.execute("select name from sqlite_master where type='table'"):
 for fk in db.execute('pragma foreign_key_list("'+table+'")'):
  if fk['table']=='generations':
   for child in db.execute('select * from "'+table+'" where "'+fk['from']+'"=?',(IDENT,)):collect(table,child)
audio=(snapshot/'data'/record['audio_path']).read_bytes();assert hashlib.sha256(audio).hexdigest()==WANTED
payload={'id':IDENT,'sha256':WANTED,'audio':base64.b64encode(audio).decode(),'audio_path':record['audio_path'],'rows':rows}
ssh=['ssh','-o','UserKnownHostsFile='+str(Path.home()/'.ssh/known_hosts'),'-o','StrictHostKeyChecking=yes','-o','BatchMode=yes','pve']
code=r'''import sys,json,base64,sqlite3,hashlib,os,re
from pathlib import Path
p=json.load(sys.stdin);assert p['id']=='5385d04b-49fa-4b0f-a001-1cebaf55b854'
root=Path('/srv/voicebox/data');db=sqlite3.connect(root/'voicebox.db');db.row_factory=sqlite3.Row
assert db.execute("select count(*) from generations where status in ('generating','pending','queued')").fetchone()[0]==0
backup=Path('/opt/voicebox/backups/d068-before-sample-recovery.sqlite3');assert not backup.exists();copy=sqlite3.connect(backup);db.backup(copy);copy.close();backup.chmod(0o600)
before=set(x[0] for x in db.execute('select id from generations'));inserted=[]
try:
 db.execute('pragma foreign_keys=on');db.execute('begin immediate')
 for item in p['rows']:
  table=item['table'];row=item['row'];assert re.fullmatch('[a-z_]+',table)
  info=list(db.execute('pragma table_info("'+table+'")'));keys=[x['name'] for x in info if x['pk']];assert keys
  assert set(row)<=set(x['name'] for x in info)
  existing=db.execute('select * from "'+table+'" where '+' and '.join('"'+k+'"=?' for k in keys),[row[k] for k in keys]).fetchone()
  if existing:
   if table=='generations' and row['id']==p['id']:assert dict(existing)==row
   continue
  columns=list(row);assert all(re.fullmatch('[a-z_]+',x) for x in columns)
  db.execute('insert into "'+table+'" ('+','.join('"'+x+'"' for x in columns)+') values ('+','.join('?' for _ in columns)+')',[row[x] for x in columns]);inserted.append(table)
 target=(root/p['audio_path']).resolve();assert target.is_relative_to(root/'generations');raw=base64.b64decode(p['audio']);assert hashlib.sha256(raw).hexdigest()==p['sha256']
 if target.exists():assert hashlib.sha256(target.read_bytes()).hexdigest()==p['sha256']
 else:
  with target.open('xb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
  target.chmod(0o600);os.chown(target,999,999)
 assert not db.execute('pragma foreign_key_check').fetchall();assert db.execute('pragma integrity_check').fetchone()[0]=='ok';db.commit()
 assert before<=set(x[0] for x in db.execute('select id from generations'))
 print(json.dumps({'result':'PASS','restored_id':p['id'],'sha256':p['sha256'],'inserted_tables':inserted,'newer_generations_preserved':len(before),'full_db_rollback':False,'cause_of_prior_absence':'UNDETERMINED; no delete issued by this intervention'}))
except BaseException:db.rollback();raise
'''
import shlex
cmd=shlex.join(['pct','exec','627','--','python3','-c',code]);r=subprocess.check_output(ssh+[cmd],input=json.dumps(payload).encode(),timeout=60);(P/'sample-recovery.json').write_bytes(r);print(r.decode())
