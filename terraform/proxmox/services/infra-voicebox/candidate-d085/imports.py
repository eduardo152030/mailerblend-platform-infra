"""Dependency preflight only: imports/signatures; weight loaders forbidden."""
import json,inspect,resource
from unittest.mock import patch
import torch,torchaudio
assert torch.__version__=='2.6.0+cpu' and torchaudio.__version__=='2.6.0+cpu'
assert not torch.cuda.is_available()
import huggingface_hub,safetensors.torch
with patch.object(torch,'load',side_effect=AssertionError('No weight loading authorized')),patch.object(safetensors.torch,'load_file',side_effect=AssertionError('No weights authorized')),patch.object(huggingface_hub,'hf_hub_download',side_effect=AssertionError('No implicit download authorized')):
 import librosa,perth,diffusers,transformers
 from chatterbox.mtl_tts import ChatterboxMultilingualTTS
 assert callable(perth.PerthImplicitWatermarker)
 assert 't3_model' in inspect.signature(ChatterboxMultilingualTTS.from_local).parameters
 assert 'language_id' in inspect.signature(ChatterboxMultilingualTTS.generate).parameters
 print(json.dumps({'imports':'PASS','torch':torch.__version__,'transformers':transformers.__version__,'diffusers':diffusers.__version__,'languages':['es','en'],'weight_loads':0,'audio_generated':False,'max_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}))
