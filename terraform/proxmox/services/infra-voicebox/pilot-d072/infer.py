"""One isolated generation. Private transcript is never printed by this wrapper."""
import subprocess,json,time,resource,wave,hashlib,os
from pathlib import Path
job=Path('/job');spec=json.loads((job/'request.json').read_text());p=Path('/private')
cmd=['/engine/qwen_tts','-d','/cache/hub/models--Qwen--Qwen3-TTS-12Hz-0.6B-Base/snapshots/5d83992436eae1d760afd27aff78a71d676296fc','--text',spec['text'],'--ref-audio',str(p/'reference.wav'),'--ref-text',(p/'transcript.txt').read_text(),'-l','Spanish','-o',str(job/'output.wav'),'--'+spec['precision'],'--max-duration',str(spec['max_audio_seconds']),'--seed','42','-j','2']
start=time.monotonic()
with (job/'engine-private.log').open('w') as log:
 proc=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT)
r={'exit_code':proc.returncode,'total_seconds':time.monotonic()-start,'rss_hwm_bytes':resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss*1024,'precision':spec['precision'],'seed':42,'threads':2}
if proc.returncode==0 and (job/'output.wav').exists():
 with wave.open(str(job/'output.wav')) as w:r.update(audio_seconds=w.getnframes()/w.getframerate(),sample_rate=w.getframerate(),channels=w.getnchannels(),frames=w.getnframes())
 r['wav_sha256']=hashlib.sha256((job/'output.wav').read_bytes()).hexdigest()
(job/'result.json').write_text(json.dumps(r,indent=2));print(json.dumps(r),flush=True)
raise SystemExit(proc.returncode)
