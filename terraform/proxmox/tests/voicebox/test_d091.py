"""Real synthetic WAV contracts; never imports a model or a personal reference."""
import hashlib
import importlib.util
import json
from pathlib import Path
import random
import sys
import tempfile
import unittest
from unittest.mock import patch
import numpy as np
import soundfile as sf

SRC=Path(__file__).resolve().parents[2]/'services/infra-voicebox/validation-d089'
spec=importlib.util.spec_from_file_location('d091_chunks',SRC/'chatterbox_chunks.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
POLICY={'max_chunk_chars':150,'max_chunks':8,'max_tokens':400,'max_chunk_seconds':20,'max_final_seconds':80}

class ChunkContracts(unittest.TestCase):
 def test_split_never_loses_tail_or_exceeds_capacity(self):
  for text, size, count in [('x'*249+'. ' ,300,4), (('x'*249+'. ')*4+'TAIL',300,4),('Hola. '*200,300,4),('Hola. '*200,150,8),('á中🙂. '*240,150,8)]:
   chunks=m.split_text(text,size,count)
   self.assertEqual(''.join(chunks),text);self.assertLessEqual(len(chunks),count)
   self.assertTrue(all(0<len(c)<=size for c in chunks))
 def test_random_boundaries_preserve_exact_input(self):
  rng=random.Random(42)
  for _ in range(250):
   text='a'+''.join(rng.choice('a .!?\ná🙂') for _ in range(rng.randrange(1200)))
   chunks=m.split_text(text)
   self.assertEqual(''.join(chunks),text);self.assertLessEqual(len(chunks),8)
   self.assertTrue(all(len(c)<=150 for c in chunks))
 def test_invalid_capacity_fails_instead_of_unbounded_last_chunk(self):
  for args in [('x'*1201,),(' ',),('x',0,8),('x',150,True)]:
   with self.assertRaises(ValueError):m.split_text(*args)
 def run_job(self,job,fail_at=None,clock=lambda:0):
  metrics={};calls=[]
  def generate(text):
   calls.append(text)
   if len(calls)==fail_at:raise RuntimeError('synthetic failure')
   metrics.update(eos=True,tokens=20)
   return np.full(2400,len(calls)/10,dtype='float32'),24000
  result=m.generate_chunks(job,'a'*301,generate,POLICY,metrics,300,clock)
  return result,calls
 def test_real_concat_order_pause_checksum_and_single_final(self):
  with tempfile.TemporaryDirectory() as d:
   job=Path(d);result,calls=self.run_job(job)
   audio,sr=sf.read(job/'chatterbox.wav')
   self.assertEqual(len(calls),3);self.assertEqual(sr,24000);self.assertEqual(len(audio),9600)
   self.assertAlmostEqual(audio[0],.1,places=4);self.assertEqual(audio[2400],0)
   self.assertAlmostEqual(audio[-1],.3,places=4)
   self.assertEqual(result['wav_sha256'],hashlib.sha256((job/'chatterbox.wav').read_bytes()).hexdigest())
   self.assertTrue(result['eos']);self.assertEqual(result['tokens'],60)
   self.assertEqual(json.loads((job/'chatterbox-chunks/manifest.json').read_text())['state'],'complete')
   with self.assertRaises(FileExistsError):self.run_job(job)
 def test_failure_preserves_completed_chunk_and_never_publishes_partial(self):
  with tempfile.TemporaryDirectory() as d:
   job=Path(d)
   with self.assertRaises(RuntimeError):self.run_job(job,fail_at=2)
   manifest=json.loads((job/'chatterbox-chunks/manifest.json').read_text())
   self.assertEqual(manifest['state'],'failed');self.assertEqual(manifest['chunks'][0]['state'],'complete')
   self.assertTrue((job/'chatterbox-chunks/000.wav').exists());self.assertFalse((job/'chatterbox.wav').exists())
 def test_eos_required_per_chunk_and_no_final_on_invalid_output(self):
  for output in [{},{'eos':False,'tokens':400},{'eos':True,'tokens':401}]:
   with tempfile.TemporaryDirectory() as d:
    metrics={}
    def generate(text):metrics.update(output);return np.zeros(24),24000
    with self.assertRaisesRegex(RuntimeError,'EOS'):
     m.generate_chunks(Path(d),'hola',generate,POLICY,metrics,300,lambda:0)
    self.assertFalse((Path(d)/'chatterbox.wav').exists())
    entry=json.loads((Path(d)/'chatterbox-chunks/manifest.json').read_text())['chunks'][0]
    self.assertEqual(entry['state'],'failed')
    if 'tokens' in output:self.assertEqual(entry['tokens'],output['tokens'])
 def test_tampered_completed_chunk_prevents_final_publication(self):
  with tempfile.TemporaryDirectory() as d:
   job=Path(d);metrics={};calls=[]
   def generate(text):
    calls.append(text);metrics.update(eos=True,tokens=3)
    if len(calls)==2:(job/'chatterbox-chunks/000.wav').write_bytes(b'corrupt')
    return np.zeros(240),24000
   with self.assertRaisesRegex(ValueError,'checksum'):
    m.generate_chunks(job,'a'*151,generate,POLICY,metrics,300,lambda:0)
   self.assertFalse((job/'chatterbox.wav').exists())
 def test_cancellation_and_global_deadline(self):
  for cancel in [True,False]:
   with tempfile.TemporaryDirectory() as d:
    job=Path(d)
    if cancel:(job/'cancel.flag').touch()
    with self.assertRaises((RuntimeError,TimeoutError)):
     self.run_job(job,clock=lambda:301 if not cancel else 0)
    self.assertFalse((job/'chatterbox.wav').exists())
 def test_invalid_wav_and_duration_fail_closed(self):
  for audio,sr in [(np.zeros((24,2)),24000),(np.array([np.nan]),24000),(np.zeros(24),22050),(np.zeros(480001),24000)]:
   with tempfile.TemporaryDirectory() as d:
    metrics={}
    def generate(t):metrics.update(eos=True,tokens=3);return audio,sr
    with self.assertRaises(ValueError):m.generate_chunks(Path(d),'hola',generate,POLICY,metrics,300,lambda:0)
    self.assertFalse((Path(d)/'chatterbox.wav').exists())
 def test_final_duration_remains_bounded(self):
  with tempfile.TemporaryDirectory() as d:
   metrics={}
   def generate(t):metrics.update(eos=True,tokens=3);return np.zeros(2400),24000
   with self.assertRaisesRegex(ValueError,'final'):
    m.generate_chunks(Path(d),'hola',generate,dict(POLICY,max_final_seconds=.05),metrics,300,lambda:0)
 def test_worker_wires_optimized_loader_eos_and_one_reference(self):
  import ast
  tree=ast.parse((SRC/'chatterbox_worker.py').read_text())
  calls=[n for n in ast.walk(tree) if isinstance(n,ast.Call)]
  self.assertEqual(sum(isinstance(n.func,ast.Attribute) and n.func.attr=='prepare_conditionals' for n in calls),1)
  bound=[n for n in calls if isinstance(n.func,ast.Name) and n.func.id=='bounded_inference']
  self.assertEqual(len(bound),1)
  loader=[n for n in calls if isinstance(n.func,ast.Name) and n.func.id=='instrument_loader'][0]
  self.assertTrue(next(k.value.value for k in loader.keywords if k.arg=='assign'))
  generate=[n for n in calls if isinstance(n.func,ast.Attribute) and n.func.attr=='generate'][0]
  self.assertIsNone(next(k.value.value for k in generate.keywords if k.arg=='audio_prompt_path'))
 def test_supervisor_distinguishes_eos_from_oom(self):
  from types import SimpleNamespace
  spec=importlib.util.spec_from_file_location('d091_supervisor',SRC/'supervise_chatterbox.py')
  mod=importlib.util.module_from_spec(spec)
  with patch.dict(sys.modules,{'supervise':SimpleNamespace(),'engine_policy':SimpleNamespace(CB=POLICY,preflight=None,stop_reason=None),'readiness':SimpleNamespace(chatterbox_ready=None)}):
   spec.loader.exec_module(mod)
  with tempfile.TemporaryDirectory() as d:
   job=Path(d)
   (job/'chatterbox-result.json').write_text(json.dumps({'success':False,'error':'No emitió EOS'}))
   self.assertIn('EOS',mod.worker_failure({'ExitCode':1,'OOMKilled':False},job))
   self.assertNotIn('OOM',mod.worker_failure({'ExitCode':1,'OOMKilled':False},job))
   self.assertIn('OOM',mod.worker_failure({'ExitCode':137,'OOMKilled':True},job))
   (job/'chatterbox-result.json').write_text('truncated')
   self.assertIn('pendiente',mod.worker_failure({'ExitCode':1},job))
 def test_target_locks_match_sources_and_keep_rollback(self):
  lock=json.loads((SRC/'deployment-lock.json').read_text())
  for group in ['worker','controller']:
   for name,digest in lock[group].items():self.assertEqual(hashlib.sha256((SRC/name).read_bytes()).hexdigest(),digest,name)
  self.assertIn('chatterbox_chunks.py',lock['worker'])
  self.assertNotIn('chatterbox_chunks.py',lock['original_worker_hashes'])

class WorkerFlow(unittest.TestCase):
 def exercise(self, eos):
  from types import SimpleNamespace, ModuleType
  import contextlib
  spec=importlib.util.spec_from_file_location('d091_fixture_loader',SRC.parents[2]/'tests/voicebox/test_d089.py')
  fixture=importlib.util.module_from_spec(spec);spec.loader.exec_module(fixture)
  worker=fixture.load();calls={'load':0,'reference':0,'generate':0,'decoder':0,'caps':[]}
  class Wave:
   def squeeze(self):return self
   def detach(self):return self
   def cpu(self):return self
   def numpy(self):return np.zeros(2400,dtype='float32')
  class Component:
   def float(self):return self
   def parameters(self):return []
  class Tokenizer:
   def __init__(self,*a):pass
   def text_to_tokens(self,*a,**kw):return SimpleNamespace(numel=lambda:1)
  class Model:
   sr=24000
   def __init__(self):
    self.t3=Component();self.t3.hp=SimpleNamespace(stop_speech_token=9)
    def inference(**kw):calls['caps'].append(kw['max_new_tokens']);return fixture.Tokens(9 if eos else 8)
    self.t3.inference=inference;self.s3gen=Component();self.ve=Component()
    self.watermarker=SimpleNamespace(perth_net=object())
   def prepare_conditionals(self,*a,**kw):calls['reference']+=1
   def generate(self,text,**kw):
    assert kw['audio_prompt_path'] is None
    calls['generate']+=1;self.t3.inference(max_new_tokens=1000)
    calls['decoder']+=1;return Wave()
  model=Model()
  def from_local(*a,**kw):calls['load']+=1;return model
  torch=ModuleType('torch');torch.__version__='2.6.0+cpu';torch.float32='float32'
  torch.cuda=SimpleNamespace(is_available=lambda:False)
  torch.set_num_threads=torch.set_num_interop_threads=torch.manual_seed=lambda *a:None
  torch.inference_mode=contextlib.nullcontext
  mtl=ModuleType('chatterbox.mtl_tts');mtl.MTLTokenizer=Tokenizer
  mtl.ChatterboxMultilingualTTS=SimpleNamespace(from_local=from_local)
  package=ModuleType('chatterbox');package.mtl_tts=mtl
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);job=root/'job';job.mkdir();models=root/'models';models.mkdir()
   reference=root/'synthetic-reference.bin';reference.write_bytes(b'synthetic fixture, not a recording')
   text='a'*301
   request={'engine':'chatterbox','profile_id':'1fd00418-2a79-4178-883f-af6c3f5e07ee','seed':42,'language':'es','text':text}
   (job/'request.json').write_text(json.dumps(request));(job/'text.txt').write_text(text)
   (models/'manifest.json').write_text(json.dumps({'model_revision':'5bb1f6ee58e50c3b8d408bc82a6d3740c2db6e18','files':[]}))
   with patch.dict(sys.modules,{'torch':torch,'chatterbox':package,'chatterbox.mtl_tts':mtl,'d077_contract':SimpleNamespace(REFERENCE_SHA=worker.sha(reference)),Tokenizer.__module__:SimpleNamespace()}), \
        patch.object(worker,'TensorTracker',lambda:SimpleNamespace(modules={},summary=lambda:{})), \
        patch.object(worker,'Events',lambda *a:SimpleNamespace(emit=lambda *a:None)), \
        patch.object(worker,'lazy_chinese',lambda *a:contextlib.nullcontext()), \
        patch.object(worker,'instrument_loader',lambda *a,**kw:contextlib.nullcontext()), \
        patch.object(worker,'install_runtime_events',lambda *a:None):
    if eos:
     result=worker.execute(job,models,reference)
     self.assertTrue(result['success']);self.assertTrue((job/'chatterbox.wav').is_file())
    else:
     with self.assertRaisesRegex(RuntimeError,'EOS'):worker.execute(job,models,reference)
     self.assertFalse((job/'chatterbox.wav').exists())
    self.assertEqual(json.loads((job/'chatterbox-result.json').read_text())['success'],eos)
  return calls
 def test_real_worker_orchestration_one_load_one_reference_and_bounded_chunks(self):
  calls=self.exercise(True)
  self.assertEqual((calls['load'],calls['reference'],calls['generate'],calls['decoder']),(1,1,3,3))
  self.assertEqual(calls['caps'],[400,400,400])
 def test_no_eos_stops_before_decoder_and_keeps_result(self):
  calls=self.exercise(False)
  self.assertEqual(calls['generate'],1);self.assertEqual(calls['decoder'],0)

if __name__=='__main__':unittest.main()
