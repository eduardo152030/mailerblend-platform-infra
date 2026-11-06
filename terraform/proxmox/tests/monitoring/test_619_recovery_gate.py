import importlib.util
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location('recovery619',Path(__file__).resolve().parents[2]/'scripts/resume-619-approved-recovery.py')
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class RecoveryGateTests(unittest.TestCase):
    def test_only_resolved_memory_incident_with_safe_rollback_can_resume(self):
        state={'ct':619,'result':'BLOCKED_ROLLED_BACK','safe_rollback_verified':True}
        marker={'ct':619,'reason':'cadvisor_memory_pressure_and_cpu_consistency','extended_seconds_completed':600,'do_not_advance':True}
        m.resolution_gate(state,marker)
        for change in [{'ct':620},{'reason':'post_watch_anomaly'},{'extended_seconds_completed':599},{'do_not_advance':False}]:
            with self.subTest(change=change),self.assertRaises(AssertionError):m.resolution_gate(state,marker|change)
        for change in [{'ct':618},{'result':'PASS'},{'safe_rollback_verified':False}]:
            with self.subTest(change=change),self.assertRaises(AssertionError):m.resolution_gate(state|change,marker)
