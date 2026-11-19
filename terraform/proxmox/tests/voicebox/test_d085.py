"""D085: no models or personal audio. Policies, queue, cancellation and recovery."""
import asyncio,hashlib,importlib.util,json,sys,tempfile,time,types,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2];C=ROOT/'services/infra-voicebox/candidate-d085';Q=ROOT/'services/infra-voicebox/candidate-d083'
sys.path[:0]=[str(C),str(Q)]
import engine_policy as policy
import chatterbox_worker as worker
from readiness import chatterbox_ready

def load(name,p):
    spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def request(engine='chatterbox',lang='es'):
    return dict(engine=engine,model_size='default' if engine=='chatterbox' else '0.6B',profile_id=policy.OWNER,seed=42,language=lang,text='Texto de prueba.' if lang=='es' else 'Test text.')

class Policy(unittest.TestCase):
    def test_four_engine_language_routes_and_limits(self):
        for e in ['qwen','chatterbox']:
            for l in ['es','en']:self.assertEqual(policy.validate(request(e,l))['language'],l)
        for e,maxchars in [('qwen',1200),('chatterbox',1200)]:
            self.assertEqual(len(policy.validate(dict(request(e),text='a'*maxchars))['text']),maxchars)
            with self.assertRaises(ValueError):policy.validate(dict(request(e),text='a'*(maxchars+1)))
    def test_identity_parameters_and_checkpoint_boundaries(self):
        for k,v in [('profile_id','other'),('seed',43),('seed',True),('language','fr'),('model_size','0.6B'),('personality',True),('instruct','speak')]:
            with self.subTest(k=k),self.assertRaises(ValueError):policy.validate(dict(request(),**{k:v}))
        with self.assertRaises(ValueError):policy.validate(dict(request('qwen'),engine='chatterbox'))
    def test_mem_guards_are_independent_and_predictive(self):
        s={'ct_current':5*2**30,'host_available':20*2**30,'ct_psi_full_avg10':0,'ct_swap':0,'ct_events':{'oom':0,'oom_kill':0},'host_oom':0}
        self.assertTrue(policy.preflight(s));self.assertFalse(policy.preflight(dict(s,ct_current=7*2**30)))
        self.assertEqual(policy.stop_reason(dict(s,worker_current=7*2**30),s),'CHATTERBOX_WORKER_7_GIB')
        self.assertEqual(policy.stop_reason(dict(s,ct_current=14*2**30),s),'CT_MEMORY_14_GIB')
        self.assertEqual(policy.stop_reason(dict(s,ct_swap=129*2**20),s),'SWAP_GROWTH_128_MIB')
    def test_capabilities_require_matching_protocol_and_freshness(self):
        from qwen_language_policy import WORKER_PROTOCOL,EXPECTED_WORKER_SHA256,policy_fingerprint
        h={'status':'healthy','ct':627,'timestamp':time.time(),'protocol':WORKER_PROTOCOL,'worker_source_sha256':EXPECTED_WORKER_SHA256,'language_policy_sha256':policy_fingerprint(),'languages':['es','en']}
        self.assertTrue(policy.capabilities(h,time.time())['qwen']['ready']);self.assertFalse(policy.capabilities(h,time.time())['chatterbox']['ready'])
        h['chatterbox']={'ready':True};self.assertFalse(policy.capabilities(h,time.time())['chatterbox']['ready'])
        h['chatterbox']['protocol']='d085-cb-v1';self.assertTrue(policy.capabilities(h,time.time())['chatterbox']['ready'])
        self.assertFalse(policy.capabilities(h,time.time()+9)['qwen']['ready'])
    def test_absent_release_never_enables_chatterbox(self):
        with tempfile.TemporaryDirectory() as d:self.assertFalse(chatterbox_ready(Path(d)/'jobs',d)['ready'])
    def test_release_tamper_or_incomplete_bundle_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);jobs=root/'qwen-worker/jobs';jobs.mkdir(parents=True);src=jobs.parent/'src';src.mkdir();code=root/'controller';code.mkdir();env=root/'chatterbox-d085';(env/'models').mkdir(parents=True);(env/'venv/bin').mkdir(parents=True);(env/'venv/bin/python').symlink_to('/usr/local/bin/python3.12');(env/'venv/pyvenv.cfg').write_text('version = 3.12.16')
            (env/'models/manifest.json').write_text(json.dumps({'model_revision':'5bb1f6ee58e50c3b8d408bc82a6d3740c2db6e18','model_repo':'ResembleAI/chatterbox'}));(env/'environment-receipt.json').write_text(json.dumps({'imports':'PASS','weight_loads':0}))
            release={'enabled':True,'model_manifest_sha256':hashlib.sha256((env/'models/manifest.json').read_bytes()).hexdigest(),'environment_receipt_sha256':hashlib.sha256((env/'environment-receipt.json').read_bytes()).hexdigest(),'source_hashes':{},'worker_hashes':{}}
            for name in ['agent.py','engine_policy.py','readiness.py','supervise_chatterbox.py','qwen_language_policy.py']:
                (code/name).write_text(name);release['source_hashes'][name]=hashlib.sha256((code/name).read_bytes()).hexdigest()
            for name in ['worker.py','qwen_language_policy.py','d077_contract.py','chatterbox_worker.py','engine_policy.py']:
                (src/name).write_text(name);release['worker_hashes'][name]=hashlib.sha256((src/name).read_bytes()).hexdigest()
            p=code/'chatterbox-release.json';p.write_text(json.dumps(release));self.assertTrue(chatterbox_ready(jobs,code)['ready'])
            (src/'chatterbox_worker.py').write_text('changed');self.assertFalse(chatterbox_ready(jobs,code)['ready'])
    def test_explicit_loader_limits_and_eos_before_decoder(self):
        class Tokens:
            shape=(1,4)
            def __init__(self,eos):self.eos=eos
            def __getitem__(self,k):return self.eos
        for eos in [99,3]:
            kwargs=[];t3=types.SimpleNamespace(inference=lambda *a,**k:(kwargs.append(k) or Tokens(eos)),hp=types.SimpleNamespace(stop_speech_token=99));m=types.SimpleNamespace(t3=t3);stats={};worker.bounded_inference(m,stats)
            if eos==99:self.assertEqual(m.t3.inference(max_new_tokens=1000).shape,(1,4))
            else:
                with self.assertRaisesRegex(RuntimeError,'EOS'):m.t3.inference(max_new_tokens=1000)
            self.assertEqual(kwargs[0]['max_new_tokens'],400);self.assertEqual(stats['eos'],eos==99)

class Agent(unittest.TestCase):
    def setUp(self):self.m=load('d085_agent',C/'agent.py')
    def test_cancelled_queued_job_is_terminal_without_launch(self):
        with tempfile.TemporaryDirectory() as d:
            job=Path(d)/'a';job.mkdir();(job/'cancel.flag').touch()
            with patch.object(self.m,'write',side_effect=lambda p,v:p.write_text(json.dumps(v))),patch.object(self.m,'request'),patch.object(self.m,'chatterbox_ready',return_value={'ready':True}),patch.object(self.m,'cleanup_owned') as cleanup,patch.object(self.m.subprocess,'Popen') as popen:
                self.m.run_chatterbox(Path(d),job);popen.assert_not_called();cleanup.assert_called_once();self.assertEqual(json.loads((job/'state.json').read_text())['status'],'cancelled')
    def test_cancellation_waits_for_child_and_cleanup_before_terminal(self):
        with tempfile.TemporaryDirectory() as d:
            job=Path(d)/'a';job.mkdir();events=[]
            class Child:
                pid=12345
                alive=True
                def poll(self):return None if self.alive else 0
                def wait(self,**kw):events.append('child-dead');self.alive=False
            child=Child()
            def launch(*args,**kw):
                kw['stdout'].write(json.dumps({'cancelled':True,'processes_released':True,'success':False}).encode());kw['stdout'].flush();(job/'cancel.flag').touch();return child
            def kill(*args):events.append('signal');child.alive=False
            def write(p,v):
                if v.get('status')=='cancelled':events.append('terminal')
                p.write_text(json.dumps(v))
            with patch.object(self.m,'write',side_effect=write),patch.object(self.m,'request'),patch.object(self.m,'heartbeat'),patch.object(self.m,'chatterbox_ready',return_value={'ready':True}),patch.object(self.m,'cleanup_owned',side_effect=lambda:events.append('cleanup')),patch.object(self.m.subprocess,'Popen',side_effect=launch),patch.object(self.m.os,'killpg',side_effect=kill),patch.object(self.m.time,'sleep'):
                self.m.run_chatterbox(Path(d),job)
            self.assertLess(events.index('cleanup'),events.index('terminal'));self.assertIn('child-dead',events)
    def test_dispatch_does_not_send_cb_to_talker_decoder(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'request.json').write_text(json.dumps(request()))
            with patch.object(self.m,'run_chatterbox',return_value='cb') as cb:self.assertEqual(self.m.run(p,p),'cb');cb.assert_called_once()

class Adapter(unittest.IsolatedAsyncioTestCase):
    def module(self):
        pkg=types.ModuleType('d085_candidate');pkg.__path__=[str(C),str(Q)]
        with patch.dict(sys.modules,{'d085_candidate':pkg,'soundfile':types.ModuleType('soundfile')}):
            m=load('d085_candidate.isolated_chatterbox_backend',C/'isolated_chatterbox_backend.py')
        return m
    async def test_queue_language_failure_and_explicit_new_attempt(self):
        import uuid
        m=self.module()
        for lang in ['es','en']:
            with tempfile.TemporaryDirectory() as d,patch.object(m.qwen,'ROOT',Path(d)),patch.object(m,'worker_health',return_value={'ready':True}):
                ident=str(uuid.uuid4());m.qwen.start_context(ident);job=Path(d)/uuid.UUID(ident).hex
                async def fake():
                    while not (job/'state.json').exists():await asyncio.sleep(.001)
                    r=json.loads((job/'request.json').read_text());self.assertEqual(r['language'],lang);self.assertEqual(r['engine'],'chatterbox');self.assertFalse((job/'checkpoint').exists());m.qwen.atomic(job/'state.json',{'status':'failed','error':'synthetic failure'})
                task=asyncio.create_task(fake())
                with self.assertRaisesRegex(RuntimeError,'synthetic'):await m.IsolatedChatterboxBackend().generate(request(lang=lang)['text'],{'profile_id':policy.OWNER},language=lang,seed=42)
                await task
                with self.assertRaisesRegex(ValueError,'nuevo intento'):await m.IsolatedChatterboxBackend().generate('Hola',{'profile_id':policy.OWNER},seed=42)
                self.assertEqual(json.loads((job/'state.json').read_text())['status'],'failed')

if __name__=='__main__':unittest.main()
