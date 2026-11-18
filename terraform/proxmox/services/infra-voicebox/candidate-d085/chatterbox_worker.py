"""Prepared worker. No ML imports at import time. Real execution needs explicit flag."""
from pathlib import Path
import argparse,json,hashlib,time,os
from engine_policy import validate,CB

def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(2**20),b''):h.update(b)
    return h.hexdigest()

def atomic(path,value):
    tmp=path.with_suffix('.partial');tmp.write_text(json.dumps(value));tmp.chmod(0o600)
    with tmp.open('rb') as f:os.fsync(f.fileno())
    os.replace(tmp,path)

def _split_text(text,max_chunk,max_chunks):
    if not text or len(text)<=max_chunk:
        return [text] if text else []
    chunks=[]
    while text and len(chunks)<max_chunks:
        end=min(len(text),max_chunk)
        cut=text.rfind('.',end-max_chunk//2,end)
        if cut>0 and cut>=end-max_chunk//2:
            end=cut+1
        elif (cut2:=text.rfind(' ',end-max_chunk//2,end))>0:
            end=cut2+1
        if len(chunks)==max_chunks-1 and len(text[:end])>=max_chunk:
            chunks.append(text)
            text=''
            break
        chunks.append(text[:end])
        text=text[end:]
    return chunks

def _concat_wav(paths):
    import soundfile as sf
    import numpy as np
    samples=[]
    sr=None
    for p in paths:
        s,sr=sf.read(p,dtype='float32')
        if s.ndim>1:s=s.squeeze()
        samples.append(s)
    combined=np.concatenate(samples)
    return combined,sr

def bounded_inference(model,metrics):
    original=model.t3.inference
    def bounded(*args,**kwargs):
        kwargs['max_new_tokens']=CB['max_tokens'];start=time.monotonic()
        tokens=original(*args,**kwargs)
        count=int(tokens.shape[-1]);eos=int(tokens[0,-1])==model.t3.hp.stop_speech_token
        metrics.update(tokens=count,eos=eos,token_seconds=time.monotonic()-start)
        if not eos:raise RuntimeError('Chatterbox no emiti EOS; no ejecutar decoder ni aceptar audio incompleto')
        return tokens
    model.t3.inference=bounded

def execute(job,models,reference):
    request=validate(json.loads((job/'request.json').read_text()))
    assert request['engine']=='chatterbox' and (job/'text.txt').read_text()==request['text']
    assert not (job/'checkpoint').exists(),'Qwen checkpoints never enter Chatterbox'
    from d077_contract import REFERENCE_SHA
    assert sha(reference)==REFERENCE_SHA
    manifest=json.loads((models/'manifest.json').read_text());assert manifest['model_revision']=='5bb1f6ee58e50c3b8d408bc82a6d3740c2db6e18'
    assert not (models/'conds.pt').exists(),'No default or third-party voice'
    for f in manifest['files']:assert sha(models/f['name'])==f['sha256']
    import torch,soundfile as sf,numpy as np
    from chatterbox.mtl_tts import ChatterboxMultilingualTTS
    torch.set_num_threads(3);torch.set_num_interop_threads(1);torch.manual_seed(42);np.random.seed(42)
    stats={'engine':'chatterbox','variant':'multilingual-v3','language':request['language'],
           'dtype':'float32','seed':42,'chunks':[]}
    start=time.monotonic()
    try:
        t=time.monotonic();model=ChatterboxMultilingualTTS.from_local(models,device='cpu',t3_model='v3')
        for component in [model.t3,model.s3gen,model.ve]:
            component.float();assert all(p.dtype==torch.float32 for p in component.parameters() if p.is_floating_point())
        stats['load_seconds']=time.monotonic()-t
        chunks=_split_text(request['text'],CB['max_chunk'],CB['max_chunks'])
        stats['chunk_count']=len(chunks)
        chunk_wavs=[]
        for i,chunk_text in enumerate(chunks):
            chunk_stats={'chunk_index':i,'chunk_text_length':len(chunk_text),'status':'running'}
            chunk_start=time.monotonic()
            with torch.inference_mode():
                wav=model.generate(chunk_text,language_id=request['language'],
                                   audio_prompt_path=str(reference),exaggeration=.5,cfg_weight=.5)
            audio=wav.squeeze().detach().cpu().numpy()
            assert audio.ndim==1 and len(audio)>0 and np.isfinite(audio).all()
            chunk_duration=len(audio)/model.sr
            assert chunk_duration<=20,f'Chunk {i} duration {chunk_duration:.1f}s exceeds 20s limit'
            chunk_path=job/f'chatterbox-chunk-{i}.wav'
            partial_path=chunk_path.with_suffix('.partial')
            sf.write(partial_path,audio,model.sr,format='WAV',subtype='PCM_16')
            with partial_path.open('rb') as f:os.fsync(f.fileno())
            partial_path.chmod(0o600);os.replace(partial_path,chunk_path)
            chunk_stats.update(status='completed',duration=chunk_duration,
                               wav_sha256=sha(chunk_path),seconds=chunk_duration,
                               token_seconds=time.monotonic()-chunk_start)
            stats['chunks'].append(chunk_stats)
            chunk_wavs.append(chunk_path)
        if len(chunk_wavs)>1:
            combined,sr=_concat_wav(chunk_wavs)
        else:
            combined,sr=sf.read(chunk_wavs[0],dtype='float32')
            combined=combined.squeeze()
        target=job/'chatterbox.wav';assert not target.exists()
        sf.write(target,combined,sr,format='WAV',subtype='PCM_16')
        with target.open('rb') as f:os.fsync(f.fileno())
        target.chmod(0o600)
        stats.update(success=True,seconds=len(combined)/sr,wav_sha256=sha(target),
                     total_duration=sum(c['duration'] for c in stats['chunks']))
    except BaseException as e:
        stats.update(success=False,error=str(e));raise
    finally:
        stats['total_seconds']=time.monotonic()-start;atomic(job/'chatterbox-result.json',stats)
    return stats

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--execute-real',action='store_true');p.add_argument('--job',type=Path,required=True);p.add_argument('--models',type=Path,required=True);p.add_argument('--reference',type=Path,required=True);a=p.parse_args()
    if not a.execute_real:p.error('Preparation does not authorize inference; explicit --execute-real required')
    print(json.dumps(execute(a.job,a.models,a.reference)))
