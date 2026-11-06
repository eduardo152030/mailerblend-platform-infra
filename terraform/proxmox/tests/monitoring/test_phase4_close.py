import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import yaml

ROOT=Path(__file__).resolve().parents[2]
def load(name):
    s=importlib.util.spec_from_file_location(name,ROOT/'scripts'/name);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

class CloseTests(unittest.TestCase):
    def test_suspension_blocks_single_target_and_all_rollout_before_remote_work(self):
        m=load('rollout-approved-exporters.py')
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);p=root/'services/common';p.mkdir(parents=True)
            (p/'phase4-execution-policy.yml').write_text(yaml.safe_dump({'status':'SUSPENDED','allowed_mutation_cts':[],'automatic_rollout':False}))
            with patch.object(m,'ROOT',root):
                for ct in m.ORDER:
                    for all_mode in [False,True]:
                        with self.assertRaisesRegex(RuntimeError,'suspended'):m.execution_gate(ct,all_mode)

    def test_future_single_ct_authorization_does_not_imply_other_ct_or_all(self):
        m=load('rollout-approved-exporters.py')
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);p=root/'services/common';p.mkdir(parents=True)
            (p/'phase4-execution-policy.yml').write_text(yaml.safe_dump({'status':'AUTHORIZED','allowed_mutation_cts':[623],'automatic_rollout':False}))
            with patch.object(m,'ROOT',root):
                m.execution_gate(623)
                with self.assertRaises(RuntimeError):m.execution_gate(623,True)
                with self.assertRaises(RuntimeError):m.execution_gate(617)

    def test_cadence_proposal_only_changes_cadvisor_model_not_resources_or_thresholds(self):
        a=next(x for x in json.loads((ROOT/'docs/roadmap/evidence/2026-11-02-rollout-authenticated-preflight.json').read_text()) if x['ct']==623)
        with tempfile.TemporaryDirectory() as d:
            old=Path(d)/'old';new=Path(d)/'new'
            before=load('prepare-approved-exporters.py').render(623,old,a)
            after=load('prepare-623-cadence.py').render(new,a)
            changed={n for n in before['file_sha256'] if (old/n).read_bytes()!=(new/n).read_bytes()}
            self.assertEqual(changed,{'cadvisor.yml','pilot.py'})
            self.assertTrue(after['approval_required']);self.assertFalse(after['automatic_continuation'])
            self.assertEqual(before['cadvisor_image'],after['cadvisor_image'])
            args=yaml.safe_load((new/'cadvisor.yml').read_text())['services']['cadvisor']['command']
            self.assertIn('--allow_dynamic_housekeeping=false',args);self.assertIn('--jitter_factor=0',args)
            self.assertEqual((new/'observe.py').read_bytes(),(old/'observe.py').read_bytes())
            self.assertEqual((new/'cadvisor-limits.yml').read_bytes(),(old/'cadvisor-limits.yml').read_bytes())
            self.assertGreater(60*(1+1),90);self.assertLess(30*(1+0),90)
