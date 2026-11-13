"""D087 resource boundaries, without ML imports or inference."""
import importlib.util
from pathlib import Path
import sys
import unittest
import tempfile,hashlib
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'services/infra-voicebox/maintenance-d087'
sys.path.insert(0,str(ROOT/'services/infra-voicebox/candidate-d083'))
def load(name):
 spec=importlib.util.spec_from_file_location('d087_'+name,BASE/(name+'.py'))
 m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
g=load('guards');p=load('engine_policy');G=2**30
class Resources(unittest.TestCase):
 def sample(self,ct=8*G):
  return dict(ct_current=ct,ct_swap=0,host_available=20*G,host_oom=0,ct_events=dict(oom=0,oom_kill=0),ct_psi_full_avg10=0,host_psi_full_avg10=0)
 def test_ct_guard_19_gib_is_exact(self):
  b=self.sample()
  self.assertIsNone(g.stop_reason(self.sample(19*G-1),b,0,None)[0])
  self.assertEqual(g.stop_reason(self.sample(19*G),b,0,None)[0],'CT_MEMORY_19_GIB')
  self.assertIsNone(p.stop_reason(self.sample(19*G-1),b))
  self.assertEqual(p.stop_reason(self.sample(19*G),b),'CT_MEMORY_19_GIB')
 def test_predictive_budgets_and_boundaries(self):
  self.assertTrue(g.predictive_preflight(self.sample(14*G))['passed'])
  self.assertFalse(g.predictive_preflight(self.sample(14*G+1))['passed'])
  self.assertTrue(p.preflight(self.sample(int(11.5*G))))
  self.assertFalse(p.preflight(self.sample(int(11.5*G)+1)))
  self.assertTrue(p.preflight(self.sample(8*G)))
 def test_worker_stops_and_pressure_remain(self):
  b=self.sample()
  self.assertEqual(g.stop_reason(dict(b,worker_current=int(8.2*G)+1),b,0,None)[0],'WORKER_MEMORY_8_2_GIB')
  self.assertEqual(p.stop_reason(dict(b,worker_current=7*G),b),'CHATTERBOX_WORKER_7_GIB')
  self.assertEqual(p.CB['worker_hard_bytes'],8*G)
  self.assertEqual(p.CB['timeout_seconds'],300)
  self.assertFalse(p.preflight(dict(b,ct_psi_full_avg10=5)))
  self.assertEqual(g.stop_reason(dict(b,ct_swap=128*2**20),b,0,None)[0],'CT_SWAP_GROWTH_128_MIB')
 def test_language_identity_and_character_limits(self):
  for engine,size,limit in [('qwen','0.6B',1200),('chatterbox','default',240)]:
   for language in ['es','en']:
    r=dict(engine=engine,profile_id=p.OWNER,seed=42,language=language,model_size=size,text='a'*limit)
    self.assertEqual(p.validate(r)['language'],language)
    with self.assertRaises(ValueError):p.validate(dict(r,text='a'*(limit+1)))
    with self.assertRaises(ValueError):p.validate(dict(r,seed=43))
class LockedCopy(unittest.TestCase):
 def recipe(self):
  spec=importlib.util.spec_from_file_location('transaction_d087',ROOT/'services/infra-voicebox/deploy-d087/transaction.py')
  m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
 def test_cache_and_unlisted_sources_are_not_deployed(self):
  with tempfile.TemporaryDirectory() as d:
   source=Path(d)/'source';target=Path(d)/'target';source.mkdir();target.mkdir()
   (source/'__pycache__').mkdir();(source/'unlisted.py').write_text('not deployed')
   (source/'agent.py').write_text('print("locked")')
   digest=hashlib.sha256((source/'agent.py').read_bytes()).hexdigest()
   self.recipe().copy_locked(source,target,{'agent.py':digest})
   self.assertEqual([p.name for p in target.iterdir()],['agent.py'])
   self.assertEqual((target/'agent.py').read_bytes(),(source/'agent.py').read_bytes())
 def test_bad_hash_stops_before_copying(self):
  with tempfile.TemporaryDirectory() as d:
   source=Path(d)/'source';target=Path(d)/'target';source.mkdir();target.mkdir();(source/'agent.py').write_text('changed')
   with self.assertRaises(AssertionError):self.recipe().copy_locked(source,target,{'agent.py':'0'*64})
   self.assertFalse(list(target.iterdir()))
 def test_symlink_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   source=Path(d)/'source';target=Path(d)/'target';source.mkdir();target.mkdir();(source/'other').write_text('content');(source/'agent.py').symlink_to('other')
   digest=hashlib.sha256(b'content').hexdigest()
   with self.assertRaises(AssertionError):self.recipe().copy_locked(source,target,{'agent.py':digest})
if __name__=='__main__':unittest.main()
