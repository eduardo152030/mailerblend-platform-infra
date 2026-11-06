"""Real interprocess lock test, no SSH or production operations."""
import importlib.util,multiprocessing,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def load():
 s=importlib.util.spec_from_file_location('lock',ROOT/'scripts/monitoring-transaction-lock.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def reader(root,entered):
 with load().monitoring_lock(root,exclusive=False):entered.set()

class TransactionLockTests(unittest.TestCase):
 def test_probe_cannot_enter_before_reload_and_readiness_finish(self):
  with tempfile.TemporaryDirectory() as d:
   entered=multiprocessing.Event()
   with load().monitoring_lock(d,exclusive=True):
    p=multiprocessing.Process(target=reader,args=(d,entered));p.start()
    self.assertFalse(entered.wait(.15),'Probe overlapped active transaction')
   self.assertTrue(entered.wait(2));p.join(2);self.assertEqual(p.exitcode,0)
 def test_lock_released_after_failed_transaction(self):
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaises(RuntimeError):
    with load().monitoring_lock(d,exclusive=True):raise RuntimeError('controlled failure')
   with load().monitoring_lock(d,exclusive=False):pass
