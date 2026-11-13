"""Two explicit load-only variants. Same upstream from_local; candidate changes assign only."""
from pathlib import Path
import argparse,contextlib,hashlib,json,os,time,weakref
from telemetry import Events

class TensorTracker:
    def __init__(self):self.modules={};self.states={}
    def add_state(self,label,state):
        self.states[label]=[weakref.ref(t) for t in state.values() if hasattr(t,'untyped_storage')]
    @staticmethod
    def storages(tensors):
        found={}
        for t in tensors:
            if t is None or t.device.type=='meta':continue
            s=t.untyped_storage();found[(str(t.device),s.data_ptr(),s.nbytes())]=s.nbytes()
        return found
    def summary(self):
        modules=self.storages(t for m in self.modules.values() for t in list(m.parameters())+list(m.buffers()))
        states=self.storages(ref() for refs in self.states.values() for ref in refs)
        return {'module_storage_bytes':sum(modules.values()),'live_state_storage_bytes':sum(states.values()),'shared_storage_bytes':sum(modules[k] for k in modules.keys()&states.keys()),'union_storage_bytes':sum({**modules,**states}.values()),'live_state_tensor_objects':sum(r() is not None for refs in self.states.values() for r in refs)}

def compare_and_touch(module,state,torch):
    """Compare all loaded checkpoint tensors; read every byte without an extra weight copy."""
    live=module.state_dict();count=0;seen=set();digests=[]
    for key,t in state.items():
        if not torch.is_tensor(t):continue
        v=live[key];assert v.shape==t.shape and v.dtype==t.dtype and torch.equal(v,t),'Loaded checkpoint mismatch'
        for item in [t,v]:
            storage=item.untyped_storage();ident=(storage.data_ptr(),storage.nbytes())
            if ident in seen:continue
            seen.add(ident)
            raw=torch.empty(0,dtype=torch.uint8).set_(storage,0,(storage.nbytes(),),(1,))
            # numpy and memoryview are views, not tobytes()/contiguous() weight copies.
            digests.append(hashlib.sha256(memoryview(raw.numpy())).digest())
        count+=1
    return {'tensor_values_verified':count,'storages_read_fully':len(seen),'storage_content_aggregate_sha256':hashlib.sha256(b''.join(digests)).hexdigest()}

@contextlib.contextmanager
def lazy_chinese(tokenizer_module,events=None):
    """Defer the official Chinese-only converter; es/en encode never uses it."""
    original=tokenizer_module.ChineseCangjieConverter
    class Lazy:
        def __init__(self,model_dir=None):self._directory=model_dir;self._delegate=None
        def _get(self):
            if self._delegate is None:
                if events:events.emit('chinese_aux.initialize.before')
                self._delegate=original(self._directory)
                if events:events.emit('chinese_aux.initialize.after')
            return self._delegate
        def __call__(self,*args,**kwargs):return self._get()(*args,**kwargs)
        def __getattr__(self,name):return getattr(self._get(),name)
    tokenizer_module.ChineseCangjieConverter=Lazy
    try:yield
    finally:tokenizer_module.ChineseCangjieConverter=original

@contextlib.contextmanager
def instrument_loader(mtl,torch,tracker,events,assign):
    originals={n:getattr(mtl,n) for n in ['VoiceEncoder','T3','S3Gen','load_safetensors','MTLTokenizer']};old_torch_load=torch.load
    labels={'VoiceEncoder':'VE','T3':'T3','S3Gen':'S3Gen'}
    def factory(name):
        original=originals[name];label=labels[name]
        def create(*args,**kwargs):
            events.emit(label+'.construct.before');module=original(*args,**kwargs);tracker.modules[label]=module;events.emit(label+'.construct.after')
            old=module.load_state_dict
            def load(state,*args,**kwargs):
                tracker.add_state(label,state)
                assert all(not t.is_floating_point() or t.dtype==torch.float32 for t in state.values() if torch.is_tensor(t)),'Weights must remain FP32'
                events.emit(label+'.load_state.before',assign=assign)
                if assign:kwargs['assign']=True
                result=old(state,*args,**kwargs)
                events.emit(label+'.load_state.after',assign=assign)
                verification=compare_and_touch(module,state,torch)
                events.emit(label+'.verified_and_read',assign=assign,**verification)
                return result
            module.load_state_dict=load
            return module
        return create
    def load_pt(path,*args,**kwargs):
        label={'ve.pt':'VE','s3gen.pt':'S3Gen'}.get(Path(path).name,'nested')
        events.emit(label+'.checkpoint.before');state=old_torch_load(path,*args,**kwargs)
        if isinstance(state,dict):tracker.add_state(label,state)
        events.emit(label+'.checkpoint.after');return state
    def load_safe(*args,**kwargs):
        events.emit('T3.checkpoint.before');state=originals['load_safetensors'](*args,**kwargs);tracker.add_state('T3',state);events.emit('T3.checkpoint.after');return state
    def tokenizer(*args,**kwargs):
        events.emit('tokenizer.construct.before');value=originals['MTLTokenizer'](*args,**kwargs);events.emit('tokenizer.construct.after');return value
    mtl.MTLTokenizer=tokenizer
    for name in labels:setattr(mtl,name,factory(name))
    mtl.load_safetensors=load_safe;torch.load=load_pt
    try:yield
    finally:
        for name,value in originals.items():setattr(mtl,name,value)
        torch.load=old_torch_load

def install_runtime_events(model,events):
    """Prepared for a later authorized TTS job; wrappers never log arguments/results."""
    for obj,method,label in [(model,'prepare_conditionals','reference'),(model.t3,'inference','tokens'),(model.s3gen,'inference','decoder')]:
        original=getattr(obj,method)
        def wrapped(*args,_original=original,_label=label,**kwargs):
            events.emit(_label+'.before')
            try:return _original(*args,**kwargs)
            finally:events.emit(_label+'.after')
        setattr(obj,method,wrapped)

def main():
    p=argparse.ArgumentParser();p.add_argument('--variant',choices=['original','candidate'],required=True);p.add_argument('--models',type=Path,required=True);p.add_argument('--job',type=Path,required=True);p.add_argument('--execute-load',action='store_true');a=p.parse_args();assert a.execute_load
    os.umask(0o077);Path('/tmp/numba').mkdir(mode=0o700,exist_ok=True);tracker=TensorTracker();events=Events(a.job/'events.jsonl',tracker.summary);events.emit('worker.start')
    manifest=json.loads((a.models/'manifest.json').read_text())
    assert manifest['model_revision']=='5bb1f6ee58e50c3b8d408bc82a6d3740c2db6e18' and manifest['model_repo']=='ResembleAI/chatterbox'
    for entry in manifest['files']:
        assert Path(entry['name']).name==entry['name']
        digest=hashlib.sha256()
        with (a.models/entry['name']).open('rb') as stream:
            for chunk in iter(lambda:stream.read(4*1024*1024),b''):digest.update(chunk)
        assert digest.hexdigest()==entry['sha256']
    events.emit('inputs.verified',model_files=len(manifest['files']))
    import torch
    assert torch.__version__=='2.6.0+cpu' and not torch.cuda.is_available();torch.set_num_threads(3);torch.set_num_interop_threads(1);torch.manual_seed(42)
    import chatterbox.mtl_tts as mtl
    original_tokenizer_module=mtl.MTLTokenizer.__module__
    from importlib.metadata import version
    events.emit('imports.ready',torch_version=torch.__version__,chatterbox_version=version('chatterbox-tts'))
    # No network, personal binds, built-in conditioning or synthesis are allowed here.
    assert not (a.models/'conds.pt').exists()
    def forbidden(*args,**kwargs):raise RuntimeError('Voice/reference/TTS forbidden in D088 load-only test')
    mtl.ChatterboxMultilingualTTS.generate=forbidden;mtl.ChatterboxMultilingualTTS.prepare_conditionals=forbidden
    import huggingface_hub
    huggingface_hub.snapshot_download=forbidden
    result={'variant':a.variant,'success':False,'torch':torch.__version__,'fp32':True,'audio_generated':False,'personal_reference_used':False}
    try:
        events.emit('from_local.before')
        import importlib
        tokenmod=importlib.import_module(original_tokenizer_module)
        with contextlib.ExitStack() as contexts:
            if a.variant=='candidate':contexts.enter_context(lazy_chinese(tokenmod,events))
            contexts.enter_context(instrument_loader(mtl,torch,tracker,events,assign=a.variant=='candidate'))
            model=mtl.ChatterboxMultilingualTTS.from_local(a.models,device='cpu',t3_model='v3')
        tracker.modules['Watermark']=model.watermarker.perth_net
        for component in [model.t3,model.s3gen,model.ve,model.watermarker.perth_net]:
            assert all(p.device.type=='cpu' and p.dtype==torch.float32 for p in component.parameters() if p.is_floating_point())
            assert all(b.device.type!='meta' for b in component.buffers())
        assert model.conds is None and model.sr==24000
        events.emit('from_local.after')
        # Required constructor-generated, nonpersistent buffer must remain initialized.
        fade=model.s3gen.trim_fade;expected=torch.zeros(960);expected[480:]=(torch.cos(torch.linspace(torch.pi,0,480))+1)/2;assert fade.device.type=='cpu' and torch.equal(fade,expected)
        events.emit('model.ready',nonpersistent_trim_fade_materialized=True)
        time.sleep(2);events.emit('model.steady')
        result.update(success=True,model_parameters_match_checkpoint=True,nonpersistent_buffers_materialized=True,chinese_aux_deferred=a.variant=='candidate',full_model_ready_without_reference=True)
    except BaseException as exc:
        result.update(error_type=type(exc).__name__);events.emit('worker.failed',error_type=type(exc).__name__);raise
    finally:
        events.emit('worker.end');tmp=a.job/'result.partial';tmp.write_text(json.dumps(result));tmp.chmod(0o600)
        with tmp.open('rb') as f:os.fsync(f.fileno())
        os.replace(tmp,a.job/'result.json')
if __name__=='__main__':main()
