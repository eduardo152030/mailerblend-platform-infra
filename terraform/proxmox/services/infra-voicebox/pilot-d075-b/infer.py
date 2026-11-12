"""Exactly one direct official Qwen Base FP32 generation. Private reference is never logged."""
import os,time,json,resource,signal,hashlib,wave,collections,functools,sys,inspect
from pathlib import Path
os.umask(0o077)
def wall_timeout(signum,frame):raise TimeoutError('worker_wall_timeout')
signal.signal(signal.SIGALRM,wall_timeout);signal.alarm(295)
ROOT=Path('/job');start=time.monotonic();events=[];stats={'stages':{},'generation_end':None,'model_dtype':'float32','text':'Hola, soy Eduardo.','max_new_tokens':64,'seed':42,'thread_budget':{'intraop':2,'interop':1}}
def event(stage,kind,**extra):
 value={'elapsed':time.monotonic()-start,'stage':stage,'event':kind,**extra};events.append(value)
 with (ROOT/'events.jsonl').open('a') as f:f.write(json.dumps(value)+'\n')
 (ROOT/'progress.json').write_text(json.dumps(value))
def timed(stage,fn):
 @functools.wraps(fn)
 def wrapped(*args,**kwargs):
  event(stage,'start');t=time.monotonic()
  try:return fn(*args,**kwargs)
  finally:stats['stages'][stage]=stats['stages'].get(stage,0)+time.monotonic()-t;event(stage,'end',seconds=time.monotonic()-t)
 return wrapped
try:
 import torch,soundfile as sf,importlib.metadata
 from qwen_tts import Qwen3TTSModel
 torch.set_num_threads(2);torch.set_num_interop_threads(1);torch.manual_seed(42)
 stats['versions']={k:importlib.metadata.version(k) for k in ['qwen-tts','torch','transformers','accelerate']}
 model_path='/cache/hub/models--Qwen--Qwen3-TTS-12Hz-0.6B-Base/snapshots/5d83992436eae1d760afd27aff78a71d676296fc'
 event('load','start');t=time.monotonic()
 model=Qwen3TTSModel.from_pretrained(model_path,device_map='cpu',dtype=torch.float32,attn_implementation='sdpa',local_files_only=True)
 stats['stages']['load']=time.monotonic()-t;event('load','end',seconds=stats['stages']['load'])
 model.model.eval();model.model.speech_tokenizer.model.eval()
 stats['parameter_dtypes']={name:dict(collections.Counter(str(p.dtype) for p in obj.parameters() if p.is_floating_point())) for name,obj in [('main',model.model),('codec',model.model.speech_tokenizer.model)]}
 assert all(set(v)=={'torch.float32'} for v in stats['parameter_dtypes'].values()),'Non-FP32 parameter found'
 stats['attention']=model.model.config._attn_implementation
 ref=Path('/private/reference.wav');assert hashlib.sha256(ref.read_bytes()).hexdigest()=='7b388a917fb98bdf6b251454e04e7adc511faec42d21797f103ce539fc167dd4'
 reftext=(Path('/private')/'transcript.txt').read_text().strip();assert len(reftext)==425
 model.model.speech_tokenizer.encode=timed('reference_encode',model.model.speech_tokenizer.encode)
 model.model.speech_tokenizer.decode=timed('decode',model.model.speech_tokenizer.decode)
 event('reference_prompt','start');t=time.monotonic()
 with torch.inference_mode():prompt=model.create_voice_clone_prompt(ref_audio=str(ref),ref_text=reftext,x_vector_only_mode=False)
 stats['stages']['reference_prompt']=time.monotonic()-t;event('reference_prompt','end',seconds=stats['stages']['reference_prompt'])
 talker=model.model.talker;oldforward=talker.forward;forward_calls=0
 @functools.wraps(oldforward)
 def forward(*args,**kwargs):
  global forward_calls
  forward_calls+=1;t=time.monotonic()
  if forward_calls==1:event('prefill_forward','start',positions=int(kwargs['inputs_embeds'].shape[-2]) if kwargs.get('inputs_embeds') is not None else None)
  output=oldforward(*args,**kwargs)
  if forward_calls==1:stats['stages']['prefill_forward']=time.monotonic()-t;event('prefill_forward','end',seconds=time.monotonic()-t)
  if forward_calls%8==0:event('talker_forward','progress',calls=forward_calls)
  return output
 talker.forward=forward;oldgen=talker.generate
 @functools.wraps(oldgen)
 def generate(*args,**kwargs):
  assert kwargs['max_new_tokens']==64
  event('talker_generation','start',max_new_tokens=kwargs['max_new_tokens'],eos_token_id=kwargs['eos_token_id']);t=time.monotonic()
  result=oldgen(*args,**kwargs);duration=time.monotonic()-t
  seq=result.sequences;tokens=int(seq.shape[-1]);eos=kwargs['eos_token_id'];hit=bool((seq==eos).any().item())
  stats.update(generated_sequence_tokens=tokens,generation_hidden_state_steps=len(result.hidden_states),talker_forward_calls=forward_calls,eos_emitted=hit,eos_token_id=int(eos),tokens_per_second=tokens/duration,generation_end='EOS' if hit else ('TOKEN_LIMIT' if tokens>=64 else 'OTHER_STOP'))
  stats['stages']['talker_generation']=duration;event('talker_generation','end',seconds=duration,tokens=tokens,eos=hit,reason=stats['generation_end']);return result
 talker.generate=generate;oldcore=model.model.generate
 def core(*args,**kwargs):
  t=time.monotonic();result=oldcore(*args,**kwargs);stats['stages']['core_generation']=time.monotonic()-t;stats['audio_code_shapes']=[list(x.shape) for x in result[0]];event('audio_codes','ready',shapes=stats['audio_code_shapes']);return result
 model.model.generate=core
 event('clone','start',signature_max_new_tokens='kwargs forwarded via _merge_generate_kwargs -> model.generate -> talker.generate')
 t=time.monotonic()
 with torch.inference_mode():wavs,sr=model.generate_voice_clone(text='Hola, soy Eduardo.',language='Spanish',voice_clone_prompt=prompt,max_new_tokens=64)
 stats['stages']['clone']=time.monotonic()-t;event('clone','end',seconds=stats['stages']['clone'])
 assert len(wavs)==1 and len(wavs[0])>0
 event('write','start');t=time.monotonic();sf.write(ROOT/'output.wav',wavs[0],sr,subtype='PCM_16');stats['stages']['write']=time.monotonic()-t
 with wave.open(str(ROOT/'output.wav')) as w:stats['audio']={'seconds':w.getnframes()/w.getframerate(),'rate':w.getframerate(),'channels':w.getnchannels(),'frames':w.getnframes(),'sample_width':w.getsampwidth()}
 stats['audio']['sha256']=hashlib.sha256((ROOT/'output.wav').read_bytes()).hexdigest();event('write','end',**stats['audio'])
 stats['classification']='A' if stats.get('eos_emitted') else ('C' if stats.get('generation_end')=='TOKEN_LIMIT' else 'F')
except BaseException as e:
 stats.update(classification='F',error_type=type(e).__name__,error=str(e)[:500]);event('failure','error',error_type=type(e).__name__)
finally:
 stats['total_seconds']=time.monotonic()-start;stats['rss_hwm_bytes']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024;(ROOT/'result.json').write_text(json.dumps(stats,indent=2));signal.alarm(0)
print(json.dumps({k:v for k,v in stats.items() if k not in ['text']}),flush=True)
raise SystemExit(0 if stats.get('audio') else 1)
