"""Full resource-aware release/heartbeat, synthetic metadata and no ML loading."""
import hashlib,importlib.util,json,shutil,sys,tempfile,time,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2];S=ROOT/'services/infra-voicebox'
sys.path[:0]=[str(S/'maintenance-d087'),str(S/'candidate-d085'),str(S/'candidate-d083')]
# Import the release under test by file identity, never an order-dependent module cache.
spec=importlib.util.spec_from_file_location('d087_release_readiness',S/'maintenance-d087/readiness.py')
readiness_module=importlib.util.module_from_spec(spec);spec.loader.exec_module(readiness_module)
chatterbox_ready=readiness_module.chatterbox_ready

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
class Release(unittest.TestCase):
 def fixture(self,root):
  jobs=root/'qwen-worker/jobs';jobs.mkdir(parents=True);src=jobs.parent/'src';src.mkdir();code=root/'controller';code.mkdir()
  release=json.loads((S/'maintenance-d087/release.proposed.json').read_text());release['enabled']=True
  for folder,key in [(code,'source_hashes'),(src,'worker_hashes')]:
   for name,digest in release[key].items():
    candidates=[S/'maintenance-d087'/name,S/'candidate-d085'/name,S/'candidate-d083'/name]
    source=next(p for p in candidates if p.exists() and sha(p)==digest)
    shutil.copy2(source,folder/name)
  env=root/'chatterbox-d085';(env/'models').mkdir(parents=True);(env/'venv/bin').mkdir(parents=True)
  (env/'venv/bin/python').symlink_to('/usr/local/bin/python');(env/'venv/pyvenv.cfg').write_text('version = 3.12.16')
  for rel,key,value in [('models/manifest.json','model_manifest_sha256',dict(model_repo='ResembleAI/chatterbox',model_revision='5bb1f6ee58e50c3b8d408bc82a6d3740c2db6e18')),('environment-receipt.json','environment_receipt_sha256',dict(imports='PASS',weight_loads=0))]:
   p=env/rel;p.write_text(json.dumps(value));release[key]=sha(p)
  (code/'chatterbox-release.json').write_text(json.dumps(release));return jobs,code,src
 def test_complete_resource_release_and_real_agent_heartbeat(self):
  with tempfile.TemporaryDirectory() as d:
   jobs,code,src=self.fixture(Path(d));self.assertTrue(chatterbox_ready(jobs,code)['ready'])
   (code/'__pycache__').mkdir();(src/'__pycache__').mkdir()
   spec=importlib.util.spec_from_file_location('d087_fixture_agent',code/'agent.py');agent=importlib.util.module_from_spec(spec);
   with patch.dict(sys.modules,{'readiness':readiness_module}):spec.loader.exec_module(agent)
   agent.CODE=code
   agent.heartbeat(jobs);h=json.loads((jobs/'agent-heartbeat.json').read_text())
   self.assertEqual(h['status'],'healthy');self.assertEqual(h['languages'],['es','en']);self.assertTrue(h['chatterbox']['ready']);self.assertLess(time.time()-h['timestamp'],8)
 def test_modified_guard_or_missing_required_source_fails_closed(self):
  with tempfile.TemporaryDirectory() as d:
   jobs,code,src=self.fixture(Path(d));(src/'guards.py').write_text('tampered');self.assertFalse(chatterbox_ready(jobs,code)['ready'])
  with tempfile.TemporaryDirectory() as d:
   jobs,code,src=self.fixture(Path(d));p=code/'chatterbox-release.json';r=json.loads(p.read_text());del r['source_hashes']['supervise.py'];p.write_text(json.dumps(r));self.assertFalse(chatterbox_ready(jobs,code)['ready'])
 def test_fixture_cannot_use_legacy_readiness_from_module_cache(self):
  legacy_spec=importlib.util.spec_from_file_location('legacy_readiness',S/'candidate-d085/readiness.py')
  legacy=importlib.util.module_from_spec(legacy_spec);legacy_spec.loader.exec_module(legacy)
  with tempfile.TemporaryDirectory() as d:
   jobs,code,src=self.fixture(Path(d))
   # The full stable receipt includes guards.py/supervise.py. Legacy D085 rejects it.
   self.assertFalse(legacy.chatterbox_ready(jobs,code)['ready'])
   with patch.dict(sys.modules,{'readiness':legacy}):
    self.assertTrue(chatterbox_ready(jobs,code)['ready'])
if __name__=='__main__':unittest.main()
