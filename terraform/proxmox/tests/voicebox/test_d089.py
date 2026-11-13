"""Offline contracts for the exact instrumented candidate; never loads weights."""
import importlib.util,sys,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2];SRC=ROOT/'services/infra-voicebox/validation-d089'
def load():
 with patch.dict(sys.modules):
  old=sys.path[:];sys.path.insert(0,str(SRC))
  try:
   spec=importlib.util.spec_from_file_location('d089_worker_contract',SRC/'chatterbox_worker.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
  finally:sys.path[:]=old
class Tokens:
 shape=(1,3)
 def __init__(self,eos):self.eos=eos
 def __getitem__(self,k):return self.eos
class Candidate(unittest.TestCase):
 def test_explicit_token_cap_and_eos_required_before_decoder(self):
  m=load();calls=[]
  def inference(**kwargs):calls.append(kwargs);return Tokens(9)
  model=SimpleNamespace(t3=SimpleNamespace(inference=inference,hp=SimpleNamespace(stop_speech_token=9)))
  stats={};m.bounded_inference(model,stats);model.t3.inference(max_new_tokens=1000)
  self.assertEqual(calls[0]['max_new_tokens'],400);self.assertTrue(stats['eos'])
  model=SimpleNamespace(t3=SimpleNamespace(inference=lambda **kw:Tokens(8),hp=SimpleNamespace(stop_speech_token=9)))
  m.bounded_inference(model,{})
  with self.assertRaisesRegex(RuntimeError,'EOS'):model.t3.inference()
 def test_runtime_phase_events_survive_failure_without_logging_inputs(self):
  m=load();rows=[];events=SimpleNamespace(emit=lambda phase:rows.append(phase))
  def fail(*args,**kw):raise ValueError('synthetic')
  model=SimpleNamespace(prepare_conditionals=fail,t3=SimpleNamespace(inference=fail),s3gen=SimpleNamespace(inference=fail))
  m.install_runtime_events(model,events)
  with self.assertRaises(ValueError):model.prepare_conditionals('private-sentinel')
  self.assertEqual(rows,['reference.before','reference.after']);self.assertNotIn('private-sentinel',str(rows))
 def test_stable_and_candidate_readiness_require_complete_matching_bundles(self):
  import tempfile,json,hashlib
  spec=importlib.util.spec_from_file_location('d089_fixture_factory',ROOT/'tests/voicebox/test_d087_readiness.py')
  fixture=importlib.util.module_from_spec(spec);spec.loader.exec_module(fixture)
  spec=importlib.util.spec_from_file_location('d089_ready',SRC/'readiness.py')
  candidate=importlib.util.module_from_spec(spec);spec.loader.exec_module(candidate)
  with tempfile.TemporaryDirectory() as d:
   jobs,code,src=fixture.Release().fixture(Path(d))
   self.assertTrue(fixture.chatterbox_ready(jobs,code)['ready'])
   self.assertFalse(candidate.chatterbox_ready(jobs,code)['ready'])
   p=code/'chatterbox-release.json';release=json.loads(p.read_text())
   for n in ['load_probe.py','telemetry.py']:
    (src/n).write_bytes((SRC/n).read_bytes());release['worker_hashes'][n]=hashlib.sha256((src/n).read_bytes()).hexdigest()
   (code/'readiness.py').write_bytes((SRC/'readiness.py').read_bytes());release['source_hashes']['readiness.py']=hashlib.sha256((code/'readiness.py').read_bytes()).hexdigest();p.write_text(json.dumps(release))
   self.assertTrue(candidate.chatterbox_ready(jobs,code)['ready'])
   (src/'telemetry.py').write_text('tampered')
   self.assertFalse(candidate.chatterbox_ready(jobs,code)['ready'])
if __name__=='__main__':unittest.main()
