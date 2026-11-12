#!/usr/bin/env python3
"""D068 bounded diagnostic: actual token progress, talker/predictor/codec, no personal voice."""
import argparse,collections,faulthandler,functools,json,os,time,traceback
from pathlib import Path
import torch,soundfile as sf
from qwen_tts import Qwen3TTSModel
p=argparse.ArgumentParser();p.add_argument('--dtype',choices=['bfloat16','float32','float16'],required=True);p.add_argument('--codec-dtype',choices=['bfloat16','float32'],default='bfloat16');p.add_argument('--attention',choices=['sdpa','eager'],default='sdpa');p.add_argument('--tokens',type=int,default=128);p.add_argument('--speaker',default='Ryan');p.add_argument('--text',default='Hola, soy una voz generada mediante inteligencia artificial.');p.add_argument('--output',default='/diag');a=p.parse_args();out=Path(a.output);out.mkdir(exist_ok=True,parents=True)
log=out/'events.jsonl';assert not log.exists(),'Preserve prior diagnostics';start=time.monotonic();counts=collections.Counter();last=time.monotonic();recent=[]
def event(stage,**kwargs):
 row={'elapsed':round(time.monotonic()-start,6),'unix':time.time(),'stage':stage,**kwargs}
 with log.open('a') as f:f.write(json.dumps(row)+'\n')
 (out/'progress.json').write_text(json.dumps(row));print(json.dumps(row),flush=True)
stack=(out/'stacks.private.txt').open('w');faulthandler.dump_traceback_later(30,repeat=True,file=stack)
torch.set_num_threads(2);torch.set_num_interop_threads(1)
event('runtime',dtype=a.dtype,attention=a.attention,threads=torch.get_num_threads(),interop=torch.get_num_interop_threads(),torch=torch.__version__)
def wrap(obj,name,label):
 original=getattr(obj,name)
 @functools.wraps(original)
 def wrapped(*args,**kw):
  event(label+'_start');t=time.monotonic();result=original(*args,**kw);extra={}
  if label=='codes':extra['code_frames']=[int(x.shape[0]) for x in result[0]]
  if label=='codec':extra['audio_samples']=[len(x) for x in result[0]];extra['sample_rate']=result[1]
  event(label+'_end',seconds=time.monotonic()-t,**extra);return result
 setattr(obj,name,wrapped)
try:
 event('load_start');t=time.monotonic();model=Qwen3TTSModel.from_pretrained('/models/hub/models--Qwen--Qwen3-TTS-12Hz-0.6B-CustomVoice/snapshots/85e237c12c027371202489a0ec509ded67b5e4b5',torch_dtype=getattr(torch,a.dtype),attn_implementation=a.attention)
 if a.codec_dtype!=a.dtype:
  event('codec_cast_start',target=a.codec_dtype);cast=time.monotonic();model.model.speech_tokenizer.model.to(dtype=getattr(torch,a.codec_dtype));event('codec_cast_end',seconds=time.monotonic()-cast)
 event('load_end',seconds=time.monotonic()-t,main_dtype=str(next(model.model.parameters()).dtype),codec_dtype=str(next(model.model.speech_tokenizer.model.parameters()).dtype))
 talker=model.model.talker;predictor=talker.code_predictor;times={};eos=model.model.config.talker_config.codec_eos_token_id
 def pre(label,module,args,kwargs):
  times[label]=time.monotonic()
  if label=='talker':
   ids=kwargs.get('input_ids')
   if ids is not None:recent.extend(ids.detach().reshape(-1).tolist());del recent[:-64]
 def post(label,module,args,kwargs,result):
  counts[label]+=1
  if label=='talker' or counts[label]%15==0:
   facts={'calls':dict(counts),'call_seconds':time.monotonic()-times[label],'recent_unique':len(set(recent)),'recent_count':len(recent)}
   if label=='talker':
    scores=result.logits[0,-1].detach().float();facts['finite_logits']=bool(torch.isfinite(scores).all());facts['eos_rank']=int((scores>scores[eos]).sum())+1
   event(label+'_forward',**facts)
 for label,module in [('talker',talker),('predictor',predictor)]:
  module.register_forward_pre_hook(functools.partial(pre,label),with_kwargs=True);module.register_forward_hook(functools.partial(post,label),with_kwargs=True)
 wrap(model.model,'generate','codes');wrap(model.model.speech_tokenizer,'decode','codec')
 torch.manual_seed(42);event('inference_start',max_new_tokens=a.tokens,speaker=a.speaker,text_words=len(a.text.split()));t=time.monotonic()
 with torch.inference_mode():wavs,sr=model.generate_custom_voice(text=a.text,language='Spanish',speaker=a.speaker,max_new_tokens=a.tokens)
 seconds=time.monotonic()-t;frames=len(wavs[0]);sf.write(str(out/'audio.wav'),wavs[0],sr,subtype='PCM_16')
 result={'result':'PASS' if counts['talker']<a.tokens else 'TOKEN_CAP_REACHED_NOT_ACCEPTED','dtype':a.dtype,'codec_dtype':a.codec_dtype,'attention':a.attention,'inference_seconds':seconds,'audio_seconds':frames/sr,'sample_rate':sr,'calls':dict(counts),'tokens_limit':a.tokens,'speaker':a.speaker}
 event('finished',**result);(out/'result.json').write_text(json.dumps(result,indent=2)+'\n')
except BaseException as e:
 event('error',error=type(e).__name__+': '+str(e));(out/'exception.private.txt').write_text(traceback.format_exc());raise
finally:faulthandler.cancel_dump_traceback_later()
