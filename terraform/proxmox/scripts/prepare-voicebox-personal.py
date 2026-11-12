#!/usr/bin/env python3
"""Upload owner's real WAV + transcript; never synthesize a fictitious personal voice.
Keeps an exact private original over existing strict PVE SSH, then uploads reference
through the installed API. Does not download/load Base or generate speech.
"""
import array,math
import argparse,base64,hashlib,json,subprocess,uuid,urllib.request,wave
import yaml
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--wav',type=Path,required=True);p.add_argument('--transcript',type=Path,required=True);p.add_argument('--owner-recording',action='store_true',required=True);a=p.parse_args()
raw=a.wav.read_bytes();assert len(raw)<50*1024**2
with wave.open(str(a.wav)) as w:
 assert w.getnchannels()==1 and w.getsampwidth()==2 and w.getframerate() in [24000,44100,48000]
 assert 3<=w.getnframes()/w.getframerate()<=25,'Prepare3–25seconds, leaving margin to installed2–30second validation'
 signal=array.array('h',w.readframes(w.getnframes()));rms=math.sqrt(sum((x/32768)**2 for x in signal)/len(signal));assert rms>=0.01,'Recording too quiet'
 assert sum(abs(x)>=32700 for x in signal)/len(signal)<0.005,'Recording has excessive clipping'
text=a.transcript.read_text().strip();assert 1<=len(text)<=1000
BASE='http://192.168.1.127:17493'
def api(path,data=None):
 with urllib.request.urlopen(urllib.request.Request(BASE+path,data=None if data is None else json.dumps(data).encode(),headers={'Content-Type':'application/json'}),timeout=30) as r:return json.load(r)
# Preserve original bytes privately before API preprocessing.
digest=hashlib.sha256(raw).hexdigest();payload=json.dumps({'sha256':digest,'audio':base64.b64encode(raw).decode(),'transcript':text}).encode()
code="""import sys,json,base64,hashlib,os
from pathlib import Path
os.umask(0o077);d=json.load(sys.stdin);raw=base64.b64decode(d['audio']);assert hashlib.sha256(raw).hexdigest()==d['sha256']
p=Path('/srv/voicebox/private-originals');assert p.is_dir();target=p/(d['sha256']+'.wav')
if target.exists():assert target.read_bytes()==raw
else:target.write_bytes(raw)
transcript=p/(d['sha256']+'.txt')
if transcript.exists():assert transcript.read_text()==d['transcript'],'Original transcript differs; keep prior file'
else:transcript.write_text(d['transcript'])
"""
import shlex
ssh=['ssh','-o','UserKnownHostsFile='+str(Path.home()/'.ssh/known_hosts'),'-o','StrictHostKeyChecking=yes','-o','BatchMode=yes','pve']
subprocess.run(ssh+[shlex.join(['pct','exec','627','--','python3','-c',code])],input=payload,check=True,timeout=60)
name='Eduardo — Mi Voz';matches=[x for x in api('/profiles') if x['name']==name];assert len(matches)<=1
profile=matches[0] if matches else api('/profiles',{'name':name,'description':'Grabación real del propietario; clonación y calidad pendientes de validación Base0.6B.','language':'es','voice_type':'cloned','default_engine':'qwen'})
assert profile['voice_type']=='cloned' and profile.get('default_engine') in (None,'qwen')
# No silent duplicate upload: reconcile receipt after network failures.
private=Path.home()/'.local/share/mailerblend-recovery/voicebox-personal';private.mkdir(parents=True,mode=0o700,exist_ok=True);receipt=private/(digest+'.json')
assert not receipt.exists(),'Receipt exists: reconcile actual sample ID before another upload'
receipt.write_text(json.dumps({'state':'UPLOAD_PENDING','profile_id':profile['id'],'original_sha256':digest})+'\n');receipt.chmod(0o600)
boundary='voicebox'+uuid.uuid4().hex
body=(f'--{boundary}\r\nContent-Disposition: form-data; name="reference_text"\r\n\r\n{text}\r\n--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="reference.wav"\r\nContent-Type: audio/wav\r\n\r\n').encode()+raw+f'\r\n--{boundary}--\r\n'.encode()
req=urllib.request.Request(BASE+'/profiles/'+profile['id']+'/samples',data=body,headers={'Content-Type':'multipart/form-data; boundary='+boundary})
with urllib.request.urlopen(req,timeout=60) as r:sample=json.load(r)
result={'state':'REFERENCE_STORED_BASE_NOT_VALIDATED','profile_id':profile['id'],'sample_id':sample['id'],'original_sha256':digest};receipt.write_text(json.dumps(result,indent=2)+'\n')
# Only update the real ID after the owner's actual reference is persisted. No invented persona.
catalog=Path(__file__).resolve().parents[1]/'services/infra-voicebox/voice-identities.yml'
data=yaml.safe_load(catalog.read_text());entry=data['identities']['personal'];entry.update({'profile_id':profile['id'],'engine':'qwen','model_size':'0.6B','status':'OWNER_REFERENCE_STORED_AWAITING_CONTROLLED_SYNTHESIS','sample_id':sample['id']})
catalog.write_text(yaml.safe_dump(data,sort_keys=False,allow_unicode=True))
import shlex
sync_code="from pathlib import Path;import sys;p=Path('/srv/voicebox/data/voice-identities.yml');p.write_bytes(sys.stdin.buffer.read());p.chmod(0o600)"
subprocess.run(ssh+[shlex.join(['pct','exec','627','--','python3','-c',sync_code])],input=catalog.read_bytes(),check=True,timeout=30)
print(json.dumps(result))
