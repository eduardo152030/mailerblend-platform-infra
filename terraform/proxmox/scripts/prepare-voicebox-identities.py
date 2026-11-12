#!/usr/bin/env python3
"""D067 additive real profile records; no personal impersonation, no deletion or model load."""
import json,urllib.request
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[1];PRIVATE=Path.home()/'.local/share/mailerblend-recovery/voicebox-d067';BASE='http://192.168.1.127:17493'
def api(path,data=None):
 with urllib.request.urlopen(urllib.request.Request(BASE+path,data=None if data is None else json.dumps(data).encode(),headers={'Content-Type':'application/json'}),timeout=15) as r:return json.load(r)
assert json.loads((PRIVATE/'restore-before/restore-check.json').read_text())['result']=='PASS'
before=api('/profiles');catalog=yaml.safe_load((ROOT/'services/infra-voicebox/voice-identities.yml').read_text());created=[]
assert catalog.get('policy') != 'PERSONAL_ONLY_D069; additional identities require a future scope','D069 personal-only policy: do not recreate historical profiles'
for key,name,engine,voice,description in [
 ('male_es','ES Male — Narrator','kokoro','em_alex','Candidato D067 basado en Alex, aceptable previamente para el propietario. Edad25–45, acento peninsular y rol narrador pendientes de escucha; no certificación automática.'),
 ('female_es','ES Female — Narrator','qwen_custom_voice','Serena','Candidata experimental D067: preset Serena nativo chino, síntesis solicitada en español; acento de España, edad25–45 y estilo NO validados. Motor condicionado al piloto BF16/SDPA; no usar backend FP32 original.')]:
 available={x['voice_id'] for x in api('/profiles/presets/'+engine)['voices']};assert voice in available
 desired={'name':name,'description':description,'language':'es','voice_type':'preset','preset_engine':engine,'preset_voice_id':voice,'default_engine':engine}
 matches=[x for x in before if x['name']==name];assert len(matches)<=1
 if matches:p=matches[0];assert all(p.get(k)==v for k,v in desired.items())
 else:p=api('/profiles',desired);created.append(p['id'])
 catalog['identities'][key].update({'profile_id':p['id'],'engine':engine,'preset_voice_id':voice,'status':'CANDIDATE_METADATA_ONLY_AWAITING_AUDIO','auditory_acceptance':'PENDING'})
 if key=='female_es':catalog['identities'][key]['model_size']='0.6B'
profiles=api('/profiles');fields=['id','name','description','language','voice_type','preset_engine','preset_voice_id','default_engine','created_at','updated_at']
for b in json.loads((PRIVATE/'profiles-before.json').read_text()):
 p=next(x for x in profiles if x['id']==b['id']);assert all(b.get(k)==p.get(k) for k in fields),'Preexisting profile changed'
assert not any(x['name']=='Eduardo — Personal Voice' for x in profiles),'Do not create fictitious personal voice'
(ROOT/'services/infra-voicebox/voice-identities.yml').write_text(yaml.safe_dump(catalog,sort_keys=False,allow_unicode=True))
r={'result':'PASS_METADATA_ONLY','created_ids':created,'identities':catalog['identities'],'preexisting_profiles_preserved':len(before),'profiles_total':len(profiles),'personal_profile_created':False};(PRIVATE/'identities.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(json.dumps(r,ensure_ascii=False))
