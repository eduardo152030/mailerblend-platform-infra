"""Pinned-environment synthetic tests only: no Chatterbox weight load or audio."""
from pathlib import Path
import hashlib,json,os,tempfile
Path('/tmp/numba').mkdir(mode=0o700,exist_ok=True)
import torch
assert torch.__version__=='2.6.0+cpu'
from load_probe import TensorTracker,compare_and_touch,install_runtime_events,lazy_chinese
from telemetry import Events
checks=0
torch.manual_seed(42);state=torch.nn.Linear(4,3).state_dict()
copy=torch.nn.Linear(4,3);copy.load_state_dict(state)
assigned=torch.nn.Linear(4,3);assigned.load_state_dict(state,assign=True)
assert copy.weight.data_ptr()!=state['weight'].data_ptr() and assigned.weight.data_ptr()==state['weight'].data_ptr();checks+=1
tracker=TensorTracker();tracker.modules={'model':copy};tracker.add_state('weights',state);assert tracker.summary()['shared_storage_bytes']==0
tracker.modules={'model':assigned};assert tracker.summary()['union_storage_bytes']==tracker.summary()['module_storage_bytes'];checks+=1
v=compare_and_touch(assigned,state,torch);assert v['tensor_values_verified']==2;checks+=1
from torch.nn.utils.parametrizations import weight_norm
c1=weight_norm(torch.nn.Conv1d(2,2,3));c2=weight_norm(torch.nn.Conv1d(2,2,3));c2.load_state_dict(c1.state_dict(),assign=True);x=torch.ones(1,2,5);assert torch.equal(c1(x),c2(x));checks+=1
l1=torch.nn.LSTM(3,4,batch_first=True);l2=torch.nn.LSTM(3,4,batch_first=True);l2.load_state_dict(l1.state_dict(),assign=True);x=torch.ones(1,2,3);assert torch.equal(l1(x)[0],l2(x)[0]);checks+=1
class Buffers(torch.nn.Module):
    def __init__(self):
        super().__init__();self.weight=torch.nn.Parameter(torch.ones(2));self.register_buffer('fade',torch.linspace(0,1,8),persistent=False)
b=Buffers();b.load_state_dict(Buffers().state_dict(),assign=True);assert b.fade.device.type=='cpu' and b.fade[-1]==1;checks+=1
with torch.device('meta'):meta=Buffers()
meta.load_state_dict(b.state_dict(),assign=True);assert meta.fade.device.type=='meta';checks+=1
# Phase hooks must preserve return values without serializing private arguments/results.
class Box:pass
m=Box();m.t3=Box();m.s3gen=Box();m.prepare_conditionals=lambda *a,**kw:'PRIVATE_RESULT';m.t3.inference=lambda *a,**kw:'PRIVATE_RESULT';m.s3gen.inference=lambda *a,**kw:'PRIVATE_RESULT'
with tempfile.TemporaryDirectory() as d:
    path=Path(d)/'events.jsonl';ev=Events(path);install_runtime_events(m,ev)
    assert m.prepare_conditionals('PRIVATE_REFERENCE')=='PRIVATE_RESULT';assert m.t3.inference('PRIVATE_TEXT')=='PRIVATE_RESULT';assert m.s3gen.inference('PRIVATE_TENSOR')=='PRIVATE_RESULT'
    raw=path.read_text();assert 'PRIVATE' not in raw;rows=[json.loads(l) for l in raw.splitlines()];assert len(rows)==6;checks+=1
# Import real packages with their loaders forbidden: still no real model weights.
from unittest.mock import patch
import huggingface_hub,safetensors.torch
with patch.object(torch,'load',side_effect=AssertionError('Real weights forbidden in contracts')),patch.object(safetensors.torch,'load_file',side_effect=AssertionError('Real weights forbidden in contracts')),patch.object(huggingface_hub,'hf_hub_download',side_effect=AssertionError('Download forbidden')):
    import chatterbox.mtl_tts as mtl
import inspect
assert 'assign' in inspect.signature(torch.nn.Module.load_state_dict).parameters;checks+=1
if Path('/models/grapheme_mtl_merged_expanded_v1.json').exists():
    import importlib
    tokenmod=importlib.import_module(mtl.MTLTokenizer.__module__)
    class UnusedChinese:
        def __init__(self,*a,**kw):pass
        def __call__(self,*a,**kw):raise AssertionError('Chinese must not be used for es/en')
    with patch.object(tokenmod,'ChineseCangjieConverter',UnusedChinese):reference=mtl.MTLTokenizer('/models/grapheme_mtl_merged_expanded_v1.json')
    with lazy_chinese(tokenmod):candidate=mtl.MTLTokenizer('/models/grapheme_mtl_merged_expanded_v1.json')
    for lang,text in [('es','Mañana tomaremos café.'),('en','Hello, this is a test.')]:assert reference.encode(text,language_id=lang)==candidate.encode(text,language_id=lang);checks+=1
    assert candidate.cangjie_converter._delegate is None;checks+=1
print(json.dumps({'contracts_passed':checks,'torch':torch.__version__,'assign_shares_storage':True,'copy_duplicates_storage':True,'lstm_and_parametrization_equal':True,'meta_nonpersistent_buffer_not_materialized':True,'personal_data_logged':False,'weight_loads':0,'tts_inferences':0,'mtl_source_sha256':hashlib.sha256(Path(mtl.__file__).read_bytes()).hexdigest()}))
