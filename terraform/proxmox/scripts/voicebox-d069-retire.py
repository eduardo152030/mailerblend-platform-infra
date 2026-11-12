#!/usr/bin/env python3
"""D069 explicit retirement; requires verified private restore, exports profiles first."""
from pathlib import Path
import json,urllib.request,zipfile,io,sqlite3,hashlib
P=Path.home()/'.local/share/mailerblend-recovery/voicebox-d069';ROOT=Path(__file__).resolve().parents[1]
OWNER='1fd00418-2a79-4178-883f-af6c3f5e07ee'
IDS={'285b5291-74b8-406d-b7fe-56c31c4e21cd','250f2938-c396-47e8-8b75-0bf9179d0252','7b6c34d0-861a-4001-ba37-aa6cb379b6e9','6be85095-8500-44cb-8f62-bab88f475d95','5850a2d6-7349-4235-9e85-c3d92819281b','916ce396-1b15-4621-b63c-5eaf49f03b74','7e127dfb-8e46-42c4-8b26-c88d0c7c65ae','6ab4fe0a-5a4f-4dc0-9b84-71b5173edfeb'}
def api(path,method='GET'):
 with urllib.request.urlopen(urllib.request.Request('http://192.168.1.127:17493'+path,method=method),timeout=60) as r:return r.read()
def main():
 assert json.loads((P/'restore-before/restore-check.json').read_text())['result']=='PASS'
 db=sqlite3.connect(P/'restore-before/snapshot/data/voicebox.db');db.row_factory=sqlite3.Row
 owner=dict(db.execute('select * from profiles where id=?',(OWNER,)).fetchone());assert owner['voice_type']=='cloned' and not owner['preset_voice_id'] and not owner['preset_engine']
 assert db.execute('select count(*) from profile_samples where profile_id=?',(OWNER,)).fetchone()[0]==1
 # No cross-profile generation-version links or stories/projects to mutate implicitly.
 gens=[r[0] for r in db.execute('select id from generations where profile_id != ?',(OWNER,))]
 assert not list(db.execute('select 1 from story_items')),'Review story references before retirement'
 assert not list(db.execute('select 1 from profile_channel_mappings')),'Review channel links'
 current=json.loads(api('/profiles'));assert {x['id'] for x in current}==IDS|{OWNER}
 exports=[]
 for ident in sorted(IDS):
  profile=dict(db.execute('select * from profiles where id=?',(ident,)).fetchone())
  samples=[dict(r) for r in db.execute('select * from profile_samples where profile_id=?',(ident,))]
  generations=[dict(r) for r in db.execute('select * from generations where profile_id=?',(ident,))]
  versions=[dict(r) for r in db.execute('select v.* from generation_versions v join generations g on g.id=v.generation_id where g.profile_id=?',(ident,))]
  target=P/(ident+'.retired.zip');assert not target.exists()
  snapshot=P/'restore-before/snapshot/data'
  paths=set()
  folder=snapshot/'profiles'/ident
  if folder.exists():paths.update(x for x in folder.rglob('*') if x.is_file())
  for row in generations+versions:
   if row.get('audio_path'):
    rel=Path(row['audio_path'])
    if rel.is_absolute():rel=rel.relative_to('/app/data')
    elif rel.parts[0]=='data':rel=Path(*rel.parts[1:])
    audio=snapshot/rel;assert audio.resolve().is_relative_to(snapshot.resolve()) and audio.is_file();paths.add(audio)
  with zipfile.ZipFile(target,'x',zipfile.ZIP_DEFLATED) as z:
   z.writestr('records.json',json.dumps({'profile':profile,'samples':samples,'generations':generations,'generation_versions':versions},ensure_ascii=False,indent=2))
   for f in paths:z.write(f,'data/'+str(f.relative_to(snapshot)))
  target.chmod(0o600)
  with zipfile.ZipFile(target) as z:assert z.testzip() is None
  raw=target.read_bytes();exports.append({'profile_id':ident,'bytes':len(raw),'files':len(paths),'sha256':hashlib.sha256(raw).hexdigest()})
 (P/'retired-exports.json').write_text(json.dumps(exports,indent=2));(P/'retired-exports.json').chmod(0o600)
 for ident in sorted(IDS):api('/profiles/'+ident,'DELETE')
 final=json.loads(api('/profiles'));assert len(final)==1 and final[0]['id']==OWNER
 refs=json.loads(api('/profiles/'+OWNER+'/samples'));assert len(refs)==1 and refs[0]['id']=='8840f5e1-990b-463e-b94e-e72beef61917'
 result={'result':'PASS','preserved_profile':OWNER,'retired_profiles':sorted(IDS),'standalone_exports':exports,'backup':'d069-before.tar.gz','owner_reference_preserved':True,'engine_uninstalls':0,'integrated_catalog_changes':0}
 (P/'retirement.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
if __name__=='__main__':main()
