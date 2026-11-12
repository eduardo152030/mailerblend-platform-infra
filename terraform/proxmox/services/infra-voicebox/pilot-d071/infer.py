"""One job per process. No imports of ML libraries in the API controller."""
import json,sys,time,resource,re,os
from pathlib import Path
p=Path(sys.argv[1]);request=json.loads((p/'request.json').read_text());start=time.monotonic();events=[]
def event(stage,**fields):
 events.append({'stage':stage,'elapsed_seconds':time.monotonic()-start,**fields});(p/'progress.json').write_text(json.dumps(events));print(json.dumps(events[-1]),flush=True)
import torch,numpy as np,soundfile as sf
os.umask(0o077);torch.set_num_threads(2);torch.set_num_interop_threads(1);torch.manual_seed(42)
from melo.api import TTS
from openvoice.api import ToneColorConverter
models=Path('/models');ref=Path('/references/8840f5e1-990b-463e-b94e-e72beef61917.wav');assert ref.is_file()
text=request['text'];spoken=re.sub(r'\btrader\b',lambda m:'Tréider' if m[0][0].isupper() else 'tréider',text,flags=re.I)
(p/'pronunciation.json').write_text(json.dumps({'original':text,'spoken':spoken,'rule':'trader→tréider only'},ensure_ascii=False))
t=time.monotonic();melo=TTS(language='ES',device='cpu',config_path=str(models/'melo/config.json'),ckpt_path=str(models/'melo/checkpoint.pth'));event('melo_loaded',seconds=time.monotonic()-t)
t=time.monotonic();melo.tts_to_file(spoken,melo.hps.data.spk2id['ES'],str(p/'source.wav'),quiet=True);event('source_synthesized',seconds=time.monotonic()-t)
del melo
import gc,ctypes;gc.collect();ctypes.CDLL(None).malloc_trim(0)
t=time.monotonic();converter=ToneColorConverter(str(models/'converter/config.json'),device='cpu',enable_watermark=False);converter.load_ckpt(str(models/'converter/checkpoint.pth'));event('converter_loaded',seconds=time.monotonic()-t)
t=time.monotonic();target=converter.extract_se(str(ref));source=torch.load(models/'source-es.pth',map_location='cpu');event('owner_embedding_extracted',seconds=time.monotonic()-t)
t=time.monotonic();converter.convert(str(p/'source.wav'),source,target,str(p/'output.wav'));event('converted',seconds=time.monotonic()-t)
audio,rate=sf.read(str(p/'output.wav'));assert rate==22050 and len(audio)>rate and np.max(np.abs(audio))>.01
sf.write(p/'output.wav',audio,rate,subtype='PCM_16');result={'audio_seconds':len(audio)/rate,'sample_rate':rate,'elapsed_seconds':time.monotonic()-start,'process_peak_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,'stages':events};(p/'result.json').write_text(json.dumps(result,indent=2));event('completed')
