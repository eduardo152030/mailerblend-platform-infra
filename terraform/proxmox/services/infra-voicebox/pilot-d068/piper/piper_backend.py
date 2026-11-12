"""CPU-only Piper es_ES-sharvard, pinned local weights; no cloning or implicit download."""
import asyncio,gc,os
from pathlib import Path
import numpy as np
PIPER_VOICE='es_ES-sharvard-medium:F'
class PiperTTSBackend:
 def __init__(self):self.model=None;self.device='cpu';self.model_size='default'
 def is_loaded(self):return self.model is not None
 def _is_model_cached(self):return (Path('/app/data/models/piper')/'es_ES-sharvard-medium.onnx').is_file()
 async def load_model(self,*args):
  if self.model is not None:return
  if not self._is_model_cached():raise ValueError('Pinned Piper model is absent; use reviewed persistent download, no automatic network access')
  from piper import PiperVoice
  def load():
   import onnxruntime as ort
   session=ort.SessionOptions();session.intra_op_num_threads=2;session.inter_op_num_threads=1
   import json
   from piper.config import PiperConfig
   path='/app/data/models/piper/es_ES-sharvard-medium.onnx'
   config=PiperConfig.from_dict(json.loads(Path(path+'.json').read_text()))
   return PiperVoice(config=config,session=ort.InferenceSession(path,sess_options=session,providers=['CPUExecutionProvider']))
  self.model=await asyncio.to_thread(load)
 def unload_model(self):
  self.model=None;gc.collect()
  try:
   import ctypes;ctypes.CDLL(None).malloc_trim(0)
  except Exception:pass
 async def create_voice_prompt(self,*args,**kwargs):raise ValueError('Piper preset does not clone reference recordings')
 async def combine_voice_prompts(self,*args,**kwargs):raise ValueError('Piper preset does not clone reference recordings')
 async def generate(self,text,voice_prompt,language='es',seed=None,instruct=None):
  assert language=='es' and voice_prompt.get('preset_voice_id')==PIPER_VOICE
  await self.load_model()
  def synthesize():
   from piper import SynthesisConfig
   chunks=list(self.model.synthesize(text,syn_config=SynthesisConfig(speaker_id=1,noise_scale=0.0,noise_w_scale=0.0)))
   assert chunks
   return np.concatenate([np.frombuffer(c.audio_int16_bytes,dtype=np.int16).astype(np.float32)/32768.0 for c in chunks]),chunks[0].sample_rate
  return await asyncio.to_thread(synthesize)
