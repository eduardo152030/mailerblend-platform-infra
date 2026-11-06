import importlib.util,json,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def load(name):
 s=importlib.util.spec_from_file_location(name,ROOT/'scripts'/name);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
class RecoveryTests(unittest.TestCase):
 def setUp(self):
  self.builder=load('prepare-aligned-exporters.py');self.audits=json.loads((ROOT/'docs/roadmap/evidence/2026-11-02-rollout-authenticated-preflight.json').read_text())
 def test_different_reentry_runs_preserve_previous_held_names(self):
  audit=next(x for x in self.audits if x['ct']==617)
  with tempfile.TemporaryDirectory() as d:
   a=self.builder.render(Path(d)/'one',audit|{'deployment_revision':'run-one'});b=self.builder.render(Path(d)/'two',audit|{'deployment_revision':'run-two'});c=self.builder.render(Path(d)/'same',audit|{'deployment_revision':'run-one'})
   self.assertNotEqual(a['framework_revision'],b['framework_revision']);self.assertEqual(a['framework_revision'],c['framework_revision'])
   self.assertIn(a['framework_revision'],(Path(d)/'one/pilot.py').read_text())
 def test_preexisting_503_is_explicit_and_not_reported_as_healthy(self):
  for ct in [615,614]:
   audit=next(x for x in self.audits if x['ct']==ct)
   with tempfile.TemporaryDirectory() as d:
    out=Path(d);m=self.builder.render(out,audit);self.assertEqual(m['initial_seconds'],180)
    body=(out/'pilot.py').read_text();self.assertIn('assert status==503',body);self.assertTrue("'status':status" in body);self.assertTrue('PRE_EXISTING_HTTP_503' in body)
 def test_crm_precision_improves_bracket_without_relaxing_acceptance(self):
  m=load('exporter-memory-alignment.py');self.assertEqual(m.allowance(1,'cadvisor'),4*1024**2);self.assertEqual(m.allowance(20_000_000,'cadvisor'),6_000_000)
  src=(ROOT/'scripts/exporter-memory-alignment.py').read_text();self.assertIn('a.interval-(time.monotonic()-tick)',src);self.assertIn('.05<=a.interval<=.5',src)
if __name__=='__main__':unittest.main()
