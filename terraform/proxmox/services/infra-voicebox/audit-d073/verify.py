"""CT627 non-mutating functional readiness and persisted sample checks. No inference."""
import subprocess,json,hashlib,wave,sqlite3,os
from pathlib import Path
prod=json.loads(subprocess.check_output(['docker','inspect','voicebox']))[0]
r={'production':{'id':prod['Id'],'image':prod['Image'],'started_at':prod['State']['StartedAt'],'restarts':prod['RestartCount'],'health':prod['State'].get('Health',{}).get('Status')},'stable_engines':[]}
for engine in ['kokoro','piper']:
 base=Path('/srv/voicebox/diagnostics-d072-stable');previous=json.loads((base/(engine+'.json')).read_text());audio=base/(engine+'.wav')
 with wave.open(str(audio)) as w: info={'seconds':w.getnframes()/w.getframerate(),'rate':w.getframerate(),'frames':w.getnframes()}
 assert previous['result']=='PASS' and info['frames']>0
 r['stable_engines'].append({'engine':engine,'last_real_inference':'D072','previous_real_inference':previous,'stored_wave_readable':True,'wave':info,'new_inference_d073':False})
code="import importlib.metadata,json;print(json.dumps({k:importlib.metadata.version(k) for k in ['kokoro','piper-tts']}))"
r['installed_versions']=json.loads(subprocess.check_output(['docker','exec','-e','PYTHONDONTWRITEBYTECODE=1','voicebox','python','-c',code]))
for name,path,sha in [('reference','/srv/voicebox/data/profiles/1fd00418-2a79-4178-883f-af6c3f5e07ee/8840f5e1-990b-463e-b94e-e72beef61917.wav','7b388a917fb98bdf6b251454e04e7adc511faec42d21797f103ce539fc167dd4'),('original','/srv/voicebox/private-originals/0d068f05ecc62c9b34e6579482ccf71de15eea0e83a22eadec1f994c19f920fe-original.wav','0d068f05ecc62c9b34e6579482ccf71de15eea0e83a22eadec1f994c19f920fe')]:
 p=Path(path);assert hashlib.sha256(p.read_bytes()).hexdigest()==sha;r[name]={'hash_preserved':True,'mode':oct(p.stat().st_mode&0o777),'uid':p.stat().st_uid}
p=Path('/srv/voicebox/data/models/piper/es_ES-sharvard-medium.onnx');r['piper_model_sha256']=hashlib.sha256(p.read_bytes()).hexdigest();assert r['piper_model_sha256']=='234dc4cf0fdb53ccb76b9b2c4d7ef1330364762674c1b78c1b62d8608c528a54'
r['read_only_verification']=True
print(json.dumps(r))
