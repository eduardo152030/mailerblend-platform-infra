#!/usr/bin/env python3
"""D067: backup, authorized Docker recreation, preserved identities, real Kokoro samples.
Run only after the controlled pilot's supervisor and RAM wrapper have completed.
"""
import array,hashlib,io,json,shlex,subprocess,time,urllib.request,wave
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];PRIVATE=Path.home()/'.local/share/mailerblend-recovery/voicebox-d067';BASE='http://192.168.1.127:17493';SSH=['ssh','-o','UserKnownHostsFile='+str(Path.home()/'.ssh/known_hosts'),'-o','StrictHostKeyChecking=yes','-o','BatchMode=yes','pve']
def api(path,data=None):
 with urllib.request.urlopen(urllib.request.Request(BASE+path,data=None if data is None else json.dumps(data).encode(),headers={'Content-Type':'application/json'}),timeout=20) as r:return json.load(r)
def ct(args,timeout=180):return subprocess.check_output(SSH+[shlex.join(['pct','exec','627','--']+args)],timeout=timeout)
assert (PRIVATE/'ram-result.json').exists(),'Wait for RAM wrapper finalization'
assert not json.loads(ct(['docker','inspect','voicebox-qwen-pilot-d067']))[0]['State']['Running']
profiles=api('/profiles');ids={x['id'] for x in profiles};assert len(ids)==7
fields=['id','name','description','language','voice_type','preset_engine','preset_voice_id','default_engine','created_at','updated_at']
for old in json.loads((PRIVATE/'profiles-before.json').read_text()):
 now=next(x for x in profiles if x['id']==old['id']);assert all(now.get(k)==old.get(k) for k in fields)
# Refuse repeat recreation without reconciling persisted receipt.
assert not (PRIVATE/'recreation-started.json').exists(),'Existing recreation: reconcile instead of repeating'
before=json.loads(ct(['docker','inspect','voicebox']))[0];assert before['Image']=='sha256:7f2e6f7e6a2d09c77ebd35424a7641249e51b8ff0374bc9c4acb1f7393cfcd4c'
r=ct(['python3','/opt/voicebox/backup.py','--output','/opt/voicebox/backups/d067-before-recreate']);(PRIVATE/'backup-before-recreate.json').write_bytes(r)
with (PRIVATE/'before-recreate.tar.gz').open('wb') as f:subprocess.run(SSH+['pct exec 627 -- cat /opt/voicebox/backups/d067-before-recreate.tar.gz'],stdout=f,check=True,timeout=180)
subprocess.run(['python3',str(ROOT/'scripts/check-voicebox-backup.py'),'--archive',str(PRIVATE/'before-recreate.tar.gz'),'--output',str(PRIVATE/'restore-before-recreate')],check=True)
(PRIVATE/'recreation-started.json').write_text(json.dumps({'before_id':before['Id'],'profiles':list(ids)})+'\n')
ct(['docker','compose','-f','/opt/voicebox/compose.yml','up','-d','--no-deps','--no-build','--force-recreate','voicebox'])
for _ in range(60):
 try:
  if api('/health')['status']=='healthy':break
 except Exception:pass
 time.sleep(2)
else:raise RuntimeError('API not recovered after authorized recreation')
new_profiles=api('/profiles');assert {x['id'] for x in new_profiles}==ids
for old in profiles:
 now=next(x for x in new_profiles if x['id']==old['id']);assert all(now.get(k)==old.get(k) for k in fields)
# Compare every backed-up data/model file, except live SQLite and disposable runtime facts.
code="""from pathlib import Path
import json,hashlib,sqlite3
base=Path('/opt/voicebox/backups/d067-before-recreate');manifest=json.loads((base/'manifest.json').read_text());count=0
for rel,h in manifest.items():
 if rel=='data/voicebox.db' or not rel.startswith(('data/','huggingface/','private-originals/')):continue
 p=Path('/srv/voicebox')/rel;assert p.is_file(),rel;assert hashlib.sha256(p.read_bytes()).hexdigest()==h,rel;count+=1
db=sqlite3.connect('file:/srv/voicebox/data/voicebox.db?mode=ro',uri=True);assert db.execute('pragma integrity_check').fetchone()[0]=='ok'
print(json.dumps({'preserved_file_hashes':count,'sqlite_integrity':'ok'}))"""
filecheck=json.loads(ct(['python3','-c',code]));samples=[]
for key,profile in [('alex','250f2938-c396-47e8-8b75-0bf9179d0252'),('male_es','916ce396-1b15-4621-b63c-5eaf49f03b74')]:
 text='Hola, bienvenidos a nuestro canal. Hoy vamos a descubrir cómo funciona esta tecnología y por qué puede cambiar nuestra forma de trabajar. Vamos a comenzar.'
 start=time.monotonic();g=api('/generate',{'profile_id':profile,'engine':'kokoro','language':'es','text':text,'seed':42,'personality':False});ident=g['id'];(PRIVATE/(key+'-request.json')).write_text(json.dumps({'generation_id':ident,'profile_id':profile})+'\n')
 while time.monotonic()-start<180:
  g=api('/history/'+ident)
  if g['status'] in ['completed','failed','cancelled']:break
  time.sleep(2)
 assert g['status']=='completed',g.get('error')
 elapsed=time.monotonic()-start
 with urllib.request.urlopen(BASE+'/audio/'+ident,timeout=20) as r:audio=r.read()
 (PRIVATE/(key+'.wav')).write_bytes(audio)
 with wave.open(io.BytesIO(audio)) as w:
  duration=w.getnframes()/w.getframerate();assert w.getframerate()==24000 and w.getnchannels()==1 and w.getsampwidth()==2;signal=array.array('h',w.readframes(w.getnframes()));assert duration>2 and max(abs(x) for x in signal)>100
 samples.append({'identity':key,'profile_id':profile,'generation_id':ident,'audio_url':BASE+'/audio/'+ident,'audio_seconds':duration,'generation_seconds_observed':elapsed,'sha256':hashlib.sha256(audio).hexdigest()})
after=json.loads(ct(['docker','inspect','voicebox']))[0];assert after['Id']!=before['Id'] and after['Image']==before['Image'] and not after['State']['OOMKilled']
# A second identical Compose application must preserve ID/StartedAt/RestartCount.
ct(['docker','compose','-f','/opt/voicebox/compose.yml','up','-d','--no-deps','--no-build','voicebox'])
second=json.loads(ct(['docker','inspect','voicebox']))[0]
assert [after['Id'],after['State']['StartedAt'],after['RestartCount']]==[second['Id'],second['State']['StartedAt'],second['RestartCount']]
result={'result':'PASS','docker_recreation_preserved_profiles':len(ids),'profile_ids':sorted(ids),'old_profiles_unchanged':5,'samples':samples,'filecheck':filecheck,'image':after['Image'],'new_container':after['Id'],'compose_second_application':'NO_RECREATE_NO_RESTART','original_volumes_preserved':True};(PRIVATE/'recovery.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
