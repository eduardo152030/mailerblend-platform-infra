"""No Torch/model required: durable telemetry and namespace-safe residual checks."""
import importlib.util,json,sys,tempfile,types,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'services/infra-voicebox/memory-d088'
def load(name):
 spec=importlib.util.spec_from_file_location('d088_'+name,BASE/(name+'.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
class Diagnostics(unittest.TestCase):
 def test_complete_event_persists_and_is_numeric_only(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'events.jsonl';e=load('telemetry').Events(p);e.emit('load.before',component_bytes=16)
   row=json.loads(p.read_text());self.assertEqual(row['phase'],'load.before');self.assertIn('VmRSS_bytes',row['memory']);self.assertNotIn('tensor_values',row);self.assertEqual(p.stat().st_mode&0o777,0o600)
 def test_file_mapped_is_not_added_to_current(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);(p/'memory.current').write_text('100');(p/'memory.stat').write_text('anon 40\nfile 50\nkernel 10\nfile_mapped 30\nfile_dirty 0\n')
   row=load('telemetry').snapshot(p);self.assertEqual(row['memory.current'],100);self.assertEqual(row['memory.stat']['file_mapped'],30)
 def test_host_pid_is_checked_by_cmdline_not_ct_pid(self):
  with patch.dict(sys.modules,{'supervise':types.SimpleNamespace(),'engine_policy':types.SimpleNamespace(preflight=None,stop_reason=None)}):m=load('supervise_load')
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);cg=p/'cg';proc=p/'proc';cg.mkdir();proc.mkdir();(proc/'99999').mkdir();(proc/'99999/cmdline').write_bytes(b'/cb/venv/bin/python\x00/src/driver.py\x00');(cg/'cgroup.procs').write_text('99999\n')
   self.assertTrue(m.driver_only(cg,proc));(cg/'cgroup.procs').write_text('99999\n123\n');self.assertFalse(m.driver_only(cg,proc))
if __name__=='__main__':unittest.main()
