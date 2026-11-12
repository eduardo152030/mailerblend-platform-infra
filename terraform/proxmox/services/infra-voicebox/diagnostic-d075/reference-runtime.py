"""CT627 reference/runtime metadata only: no audio/transcript disclosure or model loading."""
from pathlib import Path
import json,wave,hashlib,urllib.request,subprocess,os
owner='1fd00418-2a79-4178-883f-af6c3f5e07ee';sample='8840f5e1-990b-463e-b94e-e72beef61917'
samples=json.load(urllib.request.urlopen('http://192.168.1.127:17493/profiles/'+owner+'/samples',timeout=8));s=next(x for x in samples if x['id']==sample)
transcript=next(Path('/srv/voicebox/private-originals').glob('*-transcript.txt')).read_text().strip();assert s['reference_text'].strip()==transcript
r={'transcript_characters':len(transcript),'transcript_matches_owner_confirmed_private_original':True,'samples_count':len(samples),'reference':{}}
paths={'normalized':Path('/srv/voicebox/data/profiles')/owner/(sample+'.wav'),'original':next(Path('/srv/voicebox/private-originals').glob('*-original.wav'))}
for name,p in paths.items():
 with wave.open(str(p)) as w:info={'rate':w.getframerate(),'channels':w.getnchannels(),'sample_width':w.getsampwidth(),'duration_seconds':w.getnframes()/w.getframerate()}
 info.update(sha256=hashlib.sha256(p.read_bytes()).hexdigest(),mode=oct(p.stat().st_mode&0o777),uid=p.stat().st_uid);r['reference'][name]=info
model=Path('/srv/voicebox/huggingface/hub/models--Qwen--Qwen3-TTS-12Hz-0.6B-Base/snapshots/5d83992436eae1d760afd27aff78a71d676296fc');r['model_generation_config']=json.loads((model/'generation_config.json').read_text());cfg=json.loads((model/'config.json').read_text());r['talker_shape']=cfg.get('talker_config',{});r['model_type']=cfg.get('tts_model_type')
c=json.loads(subprocess.check_output(['docker','inspect','voicebox']))[0];r['voicebox']={'id':c['Id'],'image':c['Image'],'started_at':c['State']['StartedAt'],'health':c['State']['Health']['Status'],'limits':{k:c['HostConfig'][k] for k in ['NanoCpus','CpusetCpus','Memory','MemorySwap']}}
r['qwen_c_image']=json.loads(subprocess.check_output(['docker','image','inspect','local/qwen-c:d072']))[0]['Id'];print(json.dumps(r))
