"""D083 local candidate contract + simulated real worker path; NO ML inference."""
import ast
import asyncio
import contextlib
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import types
import unittest
from unittest.mock import patch
import uuid
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
CANDIDATE = ROOT/'services/infra-voicebox/candidate-d083'
STABLE = ROOT/'services/infra-voicebox/pilot-d077'
sys.path.insert(0, str(CANDIDATE)); sys.path.insert(1, str(STABLE))
from qwen_language_policy import validate_request, request_for_worker, checkpoint_language, capabilities
from engine_slot import engine_slot


def load(name, file):
    spec = importlib.util.spec_from_file_location(name, file)
    obj = importlib.util.module_from_spec(spec); spec.loader.exec_module(obj); return obj


def request(language='es'):
    return {'profile_id':'1fd00418-2a79-4178-883f-af6c3f5e07ee','seed':42,'language':language,
            'model_size':'0.6B','text':'This is a test to see if I can speak in English.' if language=='en' else 'Texto español sin traducir.'}


class Policy(unittest.TestCase):
    def test_only_two_languages(self):
        for lang in ['es','en']:self.assertEqual(validate_request(request(lang))['language'],lang)
        for lang in ['fr','auto','English','EN',None,[]]:
            with self.assertRaises(ValueError):validate_request(request(lang))

    def test_other_guards_remain(self):
        for key,value in [('profile_id','other'),('seed',43),('seed',None),('model_size','1.7B'),
                          ('instruct','speak'),('personality',True),('text',''),('text','x'*1201),('engine','chatterbox')]:
            with self.subTest(key=key,value=value),self.assertRaises(ValueError):validate_request(dict(request(),**{key:value}))

    def test_historical_spanish_and_new_english_checkpoints(self):
        model={'id':'Qwen/Qwen3-TTS-12Hz-0.6B-Base'}
        self.assertEqual(checkpoint_language({'model':model,'generation':{'language':'Spanish'}}),'es')
        self.assertEqual(checkpoint_language({'model':model,'generation':{'language':'English','language_code':'en'}}),'en')
        for meta in [{'model':{'id':'chatterbox'},'generation':{'language':'Spanish'}},
                     {'model':model,'generation':{'language':'Spanish','language_code':'en'}}]:
            with self.assertRaises(ValueError):checkpoint_language(meta)

    def test_capability_not_package_presence(self):
        self.assertFalse(capabilities(True)['chatterbox']['ready'])
        self.assertFalse(capabilities(True)['chatterbox_turbo']['ready'])
        self.assertFalse(capabilities(False)['qwen']['ready'])
        self.assertEqual(capabilities(True)['qwen']['languages'],['es','en'])

    def test_shared_lock_and_failed_preflight_release(self):
        with tempfile.TemporaryDirectory() as tmp:
            lock=Path(tmp)/'same-supervisor.lock'
            with engine_slot(lock,lambda:True):
                code="import fcntl,sys;f=open(sys.argv[1],'a');fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)"
                blocked=subprocess.run([sys.executable,'-c',code,str(lock)],capture_output=True)
                self.assertNotEqual(blocked.returncode,0)
            with self.assertRaises(RuntimeError):
                with engine_slot(lock,lambda:False):self.fail('No model may load')
            with engine_slot(lock,lambda:True):pass


class Adapter(unittest.IsolatedAsyncioTestCase):
    async def test_ui_adapter_agent_language_and_terminal_failure(self):
        pkg=types.ModuleType('d083_candidate');pkg.__path__=[str(CANDIDATE)]
        # soundfile is not needed for the terminal-error fixture; any read would fail.
        sf=types.ModuleType('soundfile');sf.read=lambda *a,**k:(_ for _ in ()).throw(AssertionError('No audio read permitted'))
        with patch.dict(sys.modules,{'d083_candidate':pkg,'soundfile':sf}):
            module=load('d083_candidate.isolated_backend',CANDIDATE/'isolated_backend.py')
        agent=load('d083_agent',CANDIDATE/'agent.py')
        for lang in ['es','en']:
            with tempfile.TemporaryDirectory() as tmp:
                module.ROOT=Path(tmp);module.worker_health=lambda:{'status':'healthy'}
                ident=str(uuid.uuid4());module.start_context(ident);job=module.ROOT/uuid.UUID(ident).hex
                async def fake_agent():
                    while not (job/'state.json').exists():await asyncio.sleep(.001)
                    payload=agent.request(job)
                    self.assertEqual(payload['language'],lang);self.assertEqual(payload['seed'],42)
                    req,target=request_for_worker(job);self.assertEqual(target,{'es':'Spanish','en':'English'}[lang])
                    module.atomic(job/'state.json',{'status':'failed','error':'simulated terminal failure; no inference'})
                fixture=asyncio.create_task(fake_agent())
                with self.assertRaisesRegex(RuntimeError,'simulated terminal failure'):
                    await module.IsolatedQwenBackend().generate(request(lang)['text'],{'profile_id':module.OWNER},language=lang,seed=42)
                await fixture
                self.assertEqual(json.loads((job/'state.json').read_text())['status'],'failed')
                with self.assertRaisesRegex(ValueError,'no tiene checkpoint'):
                    await module.IsolatedQwenBackend().generate(request(lang)['text'],{'profile_id':module.OWNER},language=lang,seed=42)
                with self.assertRaises(ValueError):
                    await module.IsolatedQwenBackend().generate('texte',{'profile_id':module.OWNER},language='fr',seed=42)

    async def test_mixed_worker_revision_fails_closed_before_jobs(self):
        import time
        from qwen_language_policy import WORKER_PROTOCOL, EXPECTED_WORKER_SHA256, policy_fingerprint
        pkg=types.ModuleType('d083_handshake');pkg.__path__=[str(CANDIDATE)]
        with patch.dict(sys.modules,{'d083_handshake':pkg,'soundfile':types.ModuleType('soundfile')}):
            module=load('d083_handshake.isolated_backend',CANDIDATE/'isolated_backend.py')
        self.assertEqual(hashlib.sha256((CANDIDATE/'worker.py').read_bytes()).hexdigest(),EXPECTED_WORKER_SHA256)
        with tempfile.TemporaryDirectory() as tmp:
            module.ROOT=Path(tmp)
            value={'timestamp':time.time(),'status':'healthy','ct':627}
            module.atomic(module.ROOT/'agent-heartbeat.json',value)
            with self.assertRaises(RuntimeError):module.worker_health()
            value.update(protocol=WORKER_PROTOCOL,worker_source_sha256=EXPECTED_WORKER_SHA256,
                         language_policy_sha256=policy_fingerprint(),languages=['es','en'])
            module.atomic(module.ROOT/'agent-heartbeat.json',value);self.assertEqual(module.worker_health()['languages'],['es','en'])
            value['worker_source_sha256']='oldSpanishWorker'
            module.atomic(module.ROOT/'agent-heartbeat.json',value)
            with self.assertRaises(RuntimeError):module.worker_health()

    async def test_candidate_cancellation_waits_for_terminal_state(self):
        pkg=types.ModuleType('d083_cancel');pkg.__path__=[str(CANDIDATE)]
        with patch.dict(sys.modules,{'d083_cancel':pkg,'soundfile':types.ModuleType('soundfile')}):
            module=load('d083_cancel.isolated_backend',CANDIDATE/'isolated_backend.py')
        with tempfile.TemporaryDirectory() as tmp:
            module.ROOT=Path(tmp);module.worker_health=lambda:{'status':'healthy'}
            ident=str(uuid.uuid4());module.start_context(ident);job=module.ROOT/uuid.UUID(ident).hex
            task=asyncio.create_task(module.IsolatedQwenBackend().generate(request('en')['text'],{'profile_id':module.OWNER},language='en',seed=42))
            while not (job/'state.json').exists():await asyncio.sleep(.001)
            async def stop_fixture():
                while not (job/'cancel.flag').exists():await asyncio.sleep(.001)
                module.atomic(job/'state.json',{'status':'cancelled'})
            stop=asyncio.create_task(stop_fixture());task.cancel()
            with self.assertRaises(asyncio.CancelledError):await task
            await stop;self.assertEqual(json.loads((job/'state.json').read_text())['status'],'cancelled')
            self.assertTrue(task.done() and stop.done())


class Worker(unittest.TestCase):
    def test_actual_talker_method_with_fake_model_preserves_reference_and_language(self):
        worker=load('d083_worker',CANDIDATE/'worker.py')
        for code,name in [('es','Spanish'),('en','English')]:
            with tempfile.TemporaryDirectory() as tmp:
                base=Path(tmp);job=base/'job';job.mkdir(mode=0o700);private=base/'reference';private.mkdir();modelpath=base/'model';modelpath.mkdir()
                ref=private/'reference.wav';ref.write_bytes(b'synthetic reference bytes, not owner audio')
                transcript=('referencia original sin traducir '*30)[:425];(private/'transcript.txt').write_text(transcript)
                payload=request(code);(job/'request.json').write_text(json.dumps(payload));(job/'text.txt').write_text(payload['text']);(modelpath/'generation_config.json').write_text('{}')
                seen={};ref_codes=np.zeros((3,16),dtype=np.int64)
                class Tensor:
                    def __init__(self,x):self.x=x
                    def detach(self):return self
                    def cpu(self):return self
                    def numpy(self):return self.x
                class Model:
                    @classmethod
                    def from_pretrained(cls,*args,**kwargs):
                        seen['load']=kwargs;return cls()
                    def __init__(self):
                        talker=types.SimpleNamespace(generate=lambda **kwargs:types.SimpleNamespace(sequences=np.array([[7,8,2150]])),generation_config=types.SimpleNamespace(to_dict=lambda:{}))
                        codec=types.SimpleNamespace(parameters=lambda:[])
                        self.model=types.SimpleNamespace(eval=lambda:None,parameters=lambda:[],talker=talker,speech_tokenizer=types.SimpleNamespace(model=codec,decode=lambda x:None))
                    def create_voice_clone_prompt(self,**kwargs):
                        seen['reference']=kwargs;return [types.SimpleNamespace(icl_mode=True,ref_code=Tensor(ref_codes))]
                    def generate_voice_clone(self,**kwargs):
                        seen['generation']=kwargs;self.model.talker.generate(max_new_tokens=1024,eos_token_id=2150)
                        return self.model.speech_tokenizer.decode([{'audio_codes':Tensor(np.zeros((5,16),dtype=np.int64))}])
                torch=types.ModuleType('torch');torch.float32='FP32';torch.manual_seed=lambda seed:seen.update(seed=seed);torch.inference_mode=contextlib.nullcontext
                qwen=types.ModuleType('qwen_tts');qwen.Qwen3TTSModel=Model
                changes={'MODEL_PATH':modelpath,'REFERENCE_SHA':hashlib.sha256(ref.read_bytes()).hexdigest(),'TRANSCRIPT_SHA':hashlib.sha256(transcript.encode()).hexdigest()}
                with patch.dict(sys.modules,{'torch':torch,'qwen_tts':qwen}),patch.multiple(worker,JOB=job,REFERENCE_ROOT=private),patch.multiple(worker.runtime,**changes),patch.object(worker.runtime,'codec_identity',return_value={'synthetic_fixture':True}):
                    result=worker.talker({'synthetic_fixture':True})
                self.assertTrue(result['checkpoint_verified']);self.assertEqual(seen['generation']['language'],name)
                self.assertEqual(seen['generation']['text'],payload['text']);self.assertEqual(seen['reference']['ref_text'],transcript)
                self.assertFalse(seen['reference']['x_vector_only_mode']);self.assertEqual(seen['seed'],42)
                self.assertEqual(seen['load']['dtype'],'FP32');self.assertEqual(seen['load']['attn_implementation'],'sdpa')
                meta=json.loads((job/'checkpoint/manifest.json').read_text());self.assertEqual(meta['generation']['language_code'],code);self.assertEqual(meta['generation']['language'],name)
                self.assertEqual(meta['reference_transcript_sha256'],hashlib.sha256(transcript.encode()).hexdigest())
                self.assertEqual(checkpoint_language(meta),code)


class Routes(unittest.TestCase):
    def test_pinned_api_guards_accept_only_en_es_before_row_creation(self):
        import textwrap
        # Reuse the actual approved overlay's admission fixture, not a rewritten guard.
        tree=ast.parse((ROOT/'services/infra-voicebox/production-d079/patch.py').read_text())
        guard=next(node.args[2].value for node in ast.walk(tree) if isinstance(node,ast.Call)
                   and isinstance(node.func,ast.Name) and node.func.id=='patch'
                   and len(node.args)>2 and isinstance(node.args[2],ast.Constant)
                   and isinstance(node.args[2].value,str) and 'Qwen requiere Eduardo/es/semilla42' in node.args[2].value)
        prefix=textwrap.dedent(guard.split('    try:')[0])
        functions=''
        for name in ['generate','retry']:
            functions+='def '+name+'(data):\n'+textwrap.indent(prefix,'    ')+'    return row_created(data)\n'
        class HTTPException(Exception):
            def __init__(self,status_code,detail):self.status_code=status_code;super().__init__(detail)
        class Router:
            def get(self,*args):return lambda fn:fn
        patcher=load('d083_patcher',CANDIDATE/'patch.py')
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'routes').mkdir();source=root/'routes/generations.py';source.write_text(functions)
            patcher.apply(root)
            rows=[];ns={'router':Router(),'HTTPException':HTTPException,'profile':None,
                       '_resolve_generation_engine':lambda data,profile:data.engine,'row_created':lambda data:rows.append(data)}
            exec(compile(source.read_text(),str(source),'exec'),ns)
            def data(**extra):
                values=dict(request(),engine='qwen',instruct=None,personality=False);values.update(extra);return types.SimpleNamespace(**values)
            for route in ['generate','retry']:
                for language in ['es','en']:
                    payload=data(language=language,seed=None);ns[route](payload);self.assertEqual(payload.seed,42)
                for changes in [{'language':'fr'},{'profile_id':'other'},{'seed':43},{'model_size':'1.7B'},
                                {'instruct':'instruction'},{'personality':True},{'text':'x'*1201},{'engine':'chatterbox'}]:
                    before=len(rows)
                    with self.assertRaises(HTTPException):ns[route](data(**changes))
                    self.assertEqual(len(rows),before,'Rejected input must not allocate history/job rows')


if __name__=='__main__':unittest.main()
