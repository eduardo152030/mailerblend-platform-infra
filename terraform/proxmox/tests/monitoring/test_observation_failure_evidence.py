import importlib.util
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location('rollout',Path(__file__).resolve().parents[2]/'scripts/rollout-approved-exporters.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class FailureEvidenceTests(unittest.TestCase):
    def test_failed_gate_retains_measured_values_and_reason_without_mutating_sample(self):
        sample={'containers':[{'name':'cadvisor'}],'resources':{'memory.current':'100'}}
        try:raise AssertionError('cAdvisor/Docker CPU mismatch: cadvisor')
        except AssertionError as exc:failed=m.failed_observation(sample,exc)
        self.assertEqual(failed['containers'],sample['containers'])
        self.assertEqual(failed['resources'],sample['resources'])
        self.assertFalse(failed['checks_passed'])
        self.assertIn('CPU mismatch',failed['private_failure_message'])
        self.assertIn('AssertionError',failed['private_traceback'])
        self.assertNotIn('checks_passed',sample)
