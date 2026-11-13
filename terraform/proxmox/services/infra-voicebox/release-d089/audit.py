"""PVE read-only acceptance audit. No inference, DSP or mutations."""
from pathlib import Path
import datetime,hashlib,json,re,subprocess,sys,urllib.request
sys.dont_write_bytecode=True;sys.path.insert(0,'/opt/voicebox-qwen-627')
import engine_policy
BASE='http://192.168.1.127:17493'
def get(p):return json.load(urllib.request.urlopen(BASE+p,timeout=20))
def ct(*a):return subprocess.check_output(['pct','exec','627','--',*a],text=True,timeout=30)
caps=get('/tts-capabilities');health=get('/health');presets=get('/effects/presets');wanted=['Robotic','Radio','Echo Chamber','Deep Voice'];chosen=[p for p in presets if p['name'] in wanted];assert len(chosen)==4
for engine in ['qwen','chatterbox']:assert caps[engine]['ready'] and caps[engine]['languages']==['es','en']
checks={}
for n in [240,241,1200]:
 request={'engine':'chatterbox','profile_id':engine_policy.OWNER,'seed':42,'language':'es','model_size':'default','text':'a'*n}
 try:engine_policy.validate(request);checks[str(n)]='accepted_by_pure_validation'
 except ValueError:checks[str(n)]='rejected_before_ML'
assert checks['240'].startswith('accepted') and checks['241'].startswith('rejected') and checks['1200'].startswith('rejected')
pid=subprocess.check_output(['lxc-info','-n','627','-pH'],text=True).strip();root=Path('/proc',pid,'root');src=root/'srv/voicebox/qwen-worker/src';worker=(src/'chatterbox_worker.py').read_text();assert "CB['max_tokens']" in worker and "<=20" in worker
model=root/'srv/voicebox/chatterbox-d085/venv/lib/python3.12/site-packages/chatterbox';mtl=(model/'mtl_tts.py').read_text();config=(model/'models/t3/modules/t3_config.py').read_text();assert 'max_new_tokens=1000' in mtl and 'max_text_tokens = 2048' in config and 'max_speech_tokens = 4096' in config
# Read actual image files without importing any backend or DSP.
code='''from pathlib import Path
import hashlib,json,re,sqlite3
root=Path('/app/backend');api=(root/'routes/generations.py').read_text();policy=(root/'backends/engine_policy.py').read_text();service=(root/'services/generation.py').read_text();models=(root/'models.py').read_text()
assert 'admission(data)' in api and "'max_chars':240" in policy
assert 'effects_chain=effects_chain_config' in api and 'apply_effects(audio, sample_rate, effects_chain)' in service
assert 'default=None' in models[models.index('class GenerationRequest'):models.index('class GenerationRequest')+6500]
assets=Path('/app/frontend/assets');index=Path('/app/frontend/index.html').read_text();names=re.findall(r'(?:/|\\./)assets/([^" ]+\\.js)',index);assert names
bundles=[(n,(assets/n).read_text()) for n in names]
assert any('"chatterbox"?240' in s and '"qwen"?1200' in s for _,s in bundles)
assert any('Audio effects' in s and 'value:p||"none"' in s for _,s in bundles)
db=sqlite3.connect('file:/app/data/voicebox.db?mode=ro',uri=True);val=db.execute("select effects_chain from profiles where id=?",('1fd00418-2a79-4178-883f-af6c3f5e07ee',)).fetchone()[0]
print(json.dumps({'api_admission_240':True,'api_effects_shared_postprocessing':True,'api_effects_default_none':True,'eduardo_profile_effects_none':val in [None,'','[]','null'],'served_bundles':[{'name':n,'sha256':hashlib.sha256(s.encode()).hexdigest(),'effects_selector':('Audio effects' in s),'requested_effect_labels':all(t in s for t in ['Robotic','Radio','Echo Chamber','Deep Voice'])} for n,s in bundles]}))
'''
ui=json.loads(subprocess.check_output(['pct','exec','627','--','docker','exec','-i','voicebox','python','-c',code],text=True))
for asset in ui['served_bundles']:
 raw=urllib.request.urlopen(BASE+'/assets/'+asset['name'],timeout=20).read();assert hashlib.sha256(raw).hexdigest()==asset['sha256']
assert ui['eduardo_profile_effects_none']
print(json.dumps({'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'healthy':health['status']=='healthy','capabilities':caps,'chatterbox_policy':engine_policy.CB,'pure_validation_no_requests':checks,'worker_audio_cap_seconds':20,'upstream':{'source_commit':'ab55923c27757c90cfcc407baa57dc25a7d25217','generate_max_new_tokens':1000,'max_text_tokens':2048,'max_speech_tokens':4096,'mtl_sha256':hashlib.sha256(mtl.encode()).hexdigest()},'ui_api':ui,'effects_presets':chosen,'effects_selection_both_engines':True,'effects_default':'none; Eduardo profile has no effects chain','audio_generated_or_processed':False}))
