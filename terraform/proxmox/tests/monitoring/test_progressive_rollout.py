"""No network: validate inventory coverage, execution gates and safe ordering."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import subprocess

ROOT=Path(__file__).resolve().parents[2]

def load(filename):
 spec=importlib.util.spec_from_file_location(filename,ROOT/'scripts'/filename)
 m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m


class ProgressiveTests(unittest.TestCase):
 def test_plan_covers_every_ct_once_and_keeps_recovered_apps_last(self):
  m=load('plan-exporter-rollout.py')
  with patch.object(subprocess,'run') as run:
   plan=m.build();self.assertEqual(plan,m.build());run.assert_not_called()
  batches=plan['remaining_batches'];ids=[r['ct'] for b in batches for r in b['ct_order']]
  self.assertEqual(len(set(ids+[624,625,626])),17)
  self.assertEqual([r['ct'] for r in batches[-2]['ct_order']],[618,622])
  self.assertEqual(ids[-1],610)
  self.assertTrue(all(b['execution']=='NOT_AUTHORIZED' for b in batches))
  self.assertEqual(plan['concurrency'],1)
  self.assertTrue(plan['incremental_integration']['complete_chain_required_per_ct'])
  for batch in batches:
   self.assertIn('integrate_source_verified_ct_into_prometheus_and_rules',batch['steps_per_ct'])
   self.assertIn('verify_exporter_backed_rule_alertmanager_telegram_chain',batch['steps_per_ct'])

 def test_executor_cannot_target_any_other_lxc(self):
  m=load('rollout-journal-exporters.py')
  for ct in [624,618,622,610]:
   with self.assertRaises(AssertionError):m.ct_code(ct,'print("no")')

 def test_db_requires_successful_api_gate_before_staging(self):
  m=load('rollout-journal-exporters.py')
  with tempfile.TemporaryDirectory() as d,patch.object(m.Path,'home',return_value=Path(d)),patch.object(m,'remote') as remote,patch('sys.argv',['runner','--ct','625','--run','journal-20261102T000000Z','--execute']):
   with self.assertRaises(FileNotFoundError):m.main()
   remote.assert_not_called()


 def test_after_archive_cannot_run_before_successful_observation(self):
  m=load('archive-journal-exporters.py')
  with tempfile.TemporaryDirectory() as d,patch.object(m.Path,'home',return_value=Path(d)),patch.object(m.m,'remote') as remote:
   here=Path(d)/'.local/share/mailerblend-recovery/phase4/journal-20261102T000000Z/626'
   here.mkdir(parents=True);(here/'state.json').write_text('{"ct":626,"result":"IN_PROGRESS"}')
   with self.assertRaises(AssertionError):m.archive('journal-20261102T000000Z',626)
   remote.assert_not_called()


if __name__=='__main__':unittest.main()
