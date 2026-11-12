"""CT627: verifica referencia y copia privada; no cambia Voicebox."""
from pathlib import Path
import json,hashlib,wave,sqlite3,os,struct,collections,subprocess
root=Path('/srv/voicebox/pilot-d072'); private=root/'private';private.mkdir(mode=0o700,exist_ok=True)
ref=Path('/srv/voicebox/data/profiles/1fd00418-2a79-4178-883f-af6c3f5e07ee/8840f5e1-990b-463e-b94e-e72beef61917.wav')
assert hashlib.sha256(ref.read_bytes()).hexdigest()=='7b388a917fb98bdf6b251454e04e7adc511faec42d21797f103ce539fc167dd4'
with wave.open(str(ref)) as w: audio={'rate':w.getframerate(),'channels':w.getnchannels(),'width':w.getsampwidth(),'seconds':w.getnframes()/w.getframerate()}
assert audio['rate']==24000 and audio['channels']==1 and audio['width']==2
originals=Path('/srv/voicebox/private-originals'); transcripts=list(originals.glob('*-transcript.txt')); assert len(transcripts)==1
transcript=transcripts[0].read_text().strip();assert len(transcript)==425
(private/'reference.wav').write_bytes(ref.read_bytes());(private/'transcript.txt').write_text(transcript)
for p in private.iterdir():p.chmod(0o600);os.chown(p,999,999)
os.chown(private,999,999)
model=Path('/srv/voicebox/huggingface/hub/models--Qwen--Qwen3-TTS-12Hz-0.6B-Base/snapshots/5d83992436eae1d760afd27aff78a71d676296fc')
r={'audio':audio,'reference_sha256':hashlib.sha256(ref.read_bytes()).hexdigest(),'transcript_characters':len(transcript),'private_permissions':'0700/0600','weights':[]}
for p in model.rglob('*.safetensors'):
 with p.open('rb') as f:n=struct.unpack('<Q',f.read(8))[0];h=json.loads(f.read(n))
 r['weights'].append({'name':str(p.relative_to(model)),'bytes':p.stat().st_size,'dtype_counts':dict(collections.Counter(v['dtype'] for k,v in h.items() if k!='__metadata__'))})
(root/'reference-check.json').write_text(json.dumps(r,indent=2));print(json.dumps(r))
