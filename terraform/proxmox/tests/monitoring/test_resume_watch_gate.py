import importlib.util,json,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
s=importlib.util.spec_from_file_location('resume',ROOT/'scripts/resume-rolled-back-exporters.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class ResumeGateTests(unittest.TestCase):
 def test_missing_extended_watch_never_clears_halt(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);(root/'620').mkdir();(root/'620/state.json').write_text(json.dumps({'result':'BLOCKED_ROLLED_BACK','safe_rollback_verified':True}));(root/'HALT.json').write_text('{"ct":621}')
   with self.assertRaises(FileNotFoundError):m.resolution_gate(root)
   self.assertTrue((root/'HALT.json').exists())
 def test_failed_or_short_window_cannot_resume(self):
  for seconds,result,samples in [(599,'PASS',21),(600,'FAIL',21),(600,'PASS',20)]:
   with tempfile.TemporaryDirectory() as d:
    root=Path(d);(root/'620').mkdir();(root/'621').mkdir();(root/'620/state.json').write_text(json.dumps({'result':'BLOCKED_ROLLED_BACK','safe_rollback_verified':True}));(root/'621/post-watch-serialized-check-result.json').write_text(json.dumps({'seconds':seconds,'result':result,'samples':samples}));(root/'HALT.json').write_text('{}')
    with self.assertRaises(AssertionError):m.resolution_gate(root)
    self.assertTrue((root/'HALT.json').exists())
