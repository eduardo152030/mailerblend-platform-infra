"""Private short preset smoke only; never clone/alter the owner profile."""
import asyncio,json,time,resource,sys
from pathlib import Path
import numpy as np,soundfile as sf
async def main():
 engine=sys.argv[1];assert engine in ['kokoro','piper']
 if engine=='kokoro':
  from backend.backends.kokoro_backend import KokoroTTSBackend
  backend=KokoroTTSBackend();voice='em_alex'
 else:
  from backend.backends.piper_backend import PiperTTSBackend,PIPER_VOICE
  backend=PiperTTSBackend();voice=PIPER_VOICE
 t=time.monotonic();audio,rate=await backend.generate('Prueba breve del motor de voz en español.',{'preset_voice_id':voice},language='es',seed=42)
 assert len(audio)>rate and float(np.max(np.abs(audio)))>.01
 path=Path('/diagnostic-output')/(engine+'.wav');sf.write(path,audio,rate,subtype='PCM_16');path.chmod(0o600)
 result={'result':'PASS','engine':engine,'sample_rate':rate,'audio_seconds':len(audio)/rate,'generation_seconds':time.monotonic()-t,'process_peak_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,'owner_profile_used':False,'preset_profile_created':False}
 Path('/diagnostic-output/'+engine+'.json').write_text(json.dumps(result,indent=2));backend.unload_model();print(json.dumps(result))
asyncio.run(main())
