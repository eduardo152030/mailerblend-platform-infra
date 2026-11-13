"""Prepared worker. No ML imports at import time. Real execution needs explicit flag."""
from pathlib import Path
import argparse,json,hashlib,time,os,contextlib,importlib
from telemetry import Events
from load_probe import TensorTracker,instrument_loader,lazy_chinese,install_runtime_events
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

def bounded_inference(model,metrics):
    original=model.t3.inference
    def bounded(*args,**kwargs):
        kwargs['max_new_tokens']=CB['max_tokens'];start=time.monotonic()
        tokens=original(*args,**kwargs)
        count=int(tokens.shape[-1]);eos=int(tokens[0,-1])==model.t3.hp.stop_speech_token
        metrics.update(tokens=count,eos=eos,token_seconds=time.monotonic()-start)
        if not eos:raise RuntimeError('Chatterbox no emitió EOS; no ejecutar decoder ni aceptar audio incompleto')
        return tokens
    model.t3.inference=bounded

def execute(job,models,reference):
    os.umask(0o077);Path('/tmp/numba').mkdir(mode=0o700,exist_ok=True)
    tracker=TensorTracker();events=Events(job/'events.jsonl',tracker.summary);events.emit('worker.start')
    request=validate(json.loads((job/'request.json').read_text()))
    assert request['engine']=='chatterbox' and (job/'text.txt').read_text()==request['text']
    assert not (job/'checkpoint').exists(),'Qwen checkpoints never enter Chatterbox'
    from d077_contract import REFERENCE_SHA
    assert sha(reference)==REFERENCE_SHA
    manifest=json.loads((models/'manifest.json').read_text());assert manifest['model_revision']=='5bb1f6ee58e50c3b8d408bc82a6d3740c2db6e18'
    assert not (models/'conds.pt').exists(),'No default or third-party voice'
    for f in manifest['files']:assert sha(models/f['name'])==f['sha256']
    import torch,soundfile as sf,numpy as np
    import chatterbox.mtl_tts as mtl
    assert torch.__version__=='2.6.0+cpu' and not torch.cuda.is_available()
    tokenmod=importlib.import_module(mtl.MTLTokenizer.__module__)
    torch.set_num_threads(3);torch.set_num_interop_threads(1);torch.manual_seed(42);np.random.seed(42)
    stats={'engine':'chatterbox','variant':'multilingual-v3','language':request['language'],'dtype':'float32','seed':42}
    start=time.monotonic()
    try:
        events.emit('inputs.verified')
        # Verify selected-language tokenizer before loading weights; no Chinese download.
        with lazy_chinese(tokenmod,events):
            tok=mtl.MTLTokenizer(str(models/'grapheme_mtl_merged_expanded_v1.json'))
            ids=tok.text_to_tokens(request['text'],language_id=request['language'])
            assert ids.numel()>0
        events.emit('tokenizer.preflight.pass')
        t=time.monotonic();events.emit('load.before')
        with lazy_chinese(tokenmod,events),instrument_loader(mtl,torch,tracker,events,assign=True):
            model=mtl.ChatterboxMultilingualTTS.from_local(models,device='cpu',t3_model='v3')
        tracker.modules['Watermark']=model.watermarker.perth_net
        events.emit('load.after')
        for component in [model.t3,model.s3gen,model.ve]:
            component.float();assert all(p.dtype==torch.float32 for p in component.parameters() if p.is_floating_point())
        stats['load_seconds']=time.monotonic()-t;bounded_inference(model,stats)
        install_runtime_events(model,events)
        with torch.inference_mode():
            wav=model.generate(request['text'],language_id=request['language'],audio_prompt_path=str(reference),exaggeration=.5,cfg_weight=.5)
        audio=wav.squeeze().detach().cpu().numpy();assert audio.ndim==1 and len(audio)>0 and np.isfinite(audio).all()
        assert model.sr==24000 and len(audio)/model.sr<=20,'Short-pilot duration limit'
        events.emit('write.before')
        target=job/'chatterbox.wav';assert not target.exists()
        part=job/'chatterbox.partial';sf.write(part,audio,model.sr,format='WAV',subtype='PCM_16')
        with part.open('rb') as f:os.fsync(f.fileno())
        part.chmod(0o600);os.replace(part,target)
        info=sf.info(target);assert info.frames==len(audio) and info.samplerate==24000 and info.channels==1
        events.emit('write.after')
        stats.update(success=True,seconds=len(audio)/model.sr,wav_sha256=sha(target))
    except BaseException as e:
        stats.update(success=False,error=str(e));raise
    finally:
        stats['total_seconds']=time.monotonic()-start;events.emit('worker.end');atomic(job/'chatterbox-result.json',stats)
    return stats

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--execute-real',action='store_true');p.add_argument('--job',type=Path,required=True);p.add_argument('--models',type=Path,required=True);p.add_argument('--reference',type=Path,required=True);a=p.parse_args()
    if not a.execute_real:p.error('Preparation does not authorize inference; explicit --execute-real required')
    print(json.dumps(execute(a.job,a.models,a.reference)))
