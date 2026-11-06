import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]
SCRIPT=ROOT/'services/common/pilot-624/node-cgroup.sh'


class TextfileTests(unittest.TestCase):
    def fixture(self,path,hostname='infra-journal-web',stat='usage_usec 9391013523\nuser_usec 6331973931\nsystem_usec 3059039592\n'):
        for name in ['etc','proc','sys/fs/cgroup']:(path/name).mkdir(parents=True,exist_ok=True)
        (path/'etc/hostname').write_text(hostname+'\n')
        (path/'proc/stat').write_text('cpu 1 2 3 4\ncpu2 1 2 3 4\n')
        (path/'sys/fs/cgroup/cpu.stat').write_text(stat)

    def test_exact_cgroup_counters_are_exported_without_host_cpu_fabrication(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);self.fixture(root)
            output=root/'metrics'
            p=subprocess.run(['sh',str(SCRIPT),'--once'],env=dict(os.environ,PILOT_HOST_ROOT=str(root),PILOT_METRIC_DIR=str(output)),capture_output=True,text=True)
            self.assertEqual(p.returncode,0,p.stderr)
            text=(output/'lxc-cpu.prom').read_text()
            self.assertIn('9391.013523',text)
            self.assertIn('6331.973931',text)
            self.assertIn('3059.039592',text)
            self.assertIn('cpu_source="cgroup_v2"',text)
            self.assertNotIn('node_cpu_seconds_total',text)
            self.assertNotIn('idle',text)
            self.assertFalse((output/'lxc-cpu.prom.tmp').exists())

    def test_wrong_ct_fails_without_writing_metrics(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);self.fixture(root,hostname='infra-composable-crm')
            out=root/'metrics'
            p=subprocess.run(['sh',str(SCRIPT),'--once'],env=dict(os.environ,PILOT_HOST_ROOT=str(root),PILOT_METRIC_DIR=str(out)),capture_output=True)
            self.assertNotEqual(p.returncode,0)
            self.assertFalse(out.exists())

    def test_missing_cgroup_counter_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);self.fixture(root,stat='user_usec 12\n')
            out=root/'metrics'
            p=subprocess.run(['sh',str(SCRIPT),'--once'],env=dict(os.environ,PILOT_HOST_ROOT=str(root),PILOT_METRIC_DIR=str(out)),capture_output=True)
            self.assertNotEqual(p.returncode,0)
            text=(out/'lxc-cpu.prom').read_text()
            self.assertIn('} 0',text)
            self.assertNotIn('lxc_cpu_usage_seconds_total',text)


if __name__=='__main__':unittest.main()
