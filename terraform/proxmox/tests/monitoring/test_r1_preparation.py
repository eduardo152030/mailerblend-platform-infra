import importlib.util
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('r1',ROOT/'scripts/prepare-r1-exporters.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class R1Tests(unittest.TestCase):
 def test_preparation_is_deterministic_and_cannot_overwrite_snapshot(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);a=m.render(p);self.assertEqual(a,m.render(p));(p/'baseline.json').write_text('{}')
   with self.assertRaises(AssertionError):m.render(p)
 def test_no_application_claim_is_a_real_guard(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);m.render(p);spec=importlib.util.spec_from_file_location('r1helper',p/'pilot.py');h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
   with patch.object(h,'identities',return_value=[{'name':'unexpected'}]):
    with self.assertRaises(AssertionError):h.web()
   with patch.object(h,'identities',return_value=[]),patch.object(h,'run',return_value=b'node_exporter cadvisor cadvisor_business'):
    with self.assertRaises(AssertionError):h.web()
   with patch.object(h,'identities',return_value=[]),patch.object(h,'run',return_value=b'node_exporter cadvisor'):
    self.assertTrue(h.web()['no_application_baseline'])
   with patch.object(h,'ALLOW_CONTAINERD_SOCKET',False):
    with self.assertRaises(AssertionError):h.apply(p)
 def test_one_core_cgroup_collector_has_correct_identity(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);bundle=p/'bundle';m.render(bundle);host=p/'host'
   for n in ['etc','proc','sys/fs/cgroup']:(host/n).mkdir(parents=True,exist_ok=True)
   (host/'etc/hostname').write_text('infra-hola\n');(host/'proc/stat').write_text('cpu 1\ncpu2 1\n');(host/'sys/fs/cgroup/cpu.stat').write_text('usage_usec 1000000\nuser_usec 600000\nsystem_usec 400000\n')
   r=subprocess.run(['sh',str(bundle/'node-cgroup.sh'),'--once'],env=dict(os.environ,PILOT_HOST_ROOT=str(host),PILOT_METRIC_DIR=str(p/'out')),capture_output=True)
   self.assertEqual(r.returncode,0);text=(p/'out/lxc-cpu.prom').read_text();self.assertIn('ct_id="613"',text);self.assertRegex(text,r'lxc_cpu_capacity_cores\{[^}]*\} 1\n');self.assertNotIn('node_cpu_seconds_total',text)
if __name__=='__main__':unittest.main()
