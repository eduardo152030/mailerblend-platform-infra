import ast,importlib.util,json,tempfile,unittest
from pathlib import Path
from unittest.mock import Mock,patch
ROOT=Path(__file__).resolve().parents[2]
def load(name):
 s=importlib.util.spec_from_file_location(name,ROOT/'scripts'/name);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
class CriticalTests(unittest.TestCase):
 def test_critical_renderer_preserves_stopped_application_identity_scope(self):
  audits=json.loads((ROOT/'tests/monitoring/fixtures/critical-rollout-inventory.json').read_text())
  m=load('prepare-aligned-exporters.py')
  for audit in audits:
   with tempfile.TemporaryDirectory() as d:
    out=Path(d);manifest=m.render(out,audit)
    self.assertEqual((manifest['initial_seconds'],manifest['initial_minimum_samples']),({618:300,622:300,611:180,616:180,610:600}[audit['ct']],{618:11,622:11,611:7,616:7,610:21}[audit['ct']]))
    self.assertEqual(set(manifest['apps']),{c['name'] for c in audit['containers'] if c['running'] and not c['name'].startswith(('node_exporter','cadvisor'))})
    self.assertIn('memory_alignment',manifest)
    for c in audit['containers']:
     if not c['running']:self.assertIn(repr(c['name']),(out/'pilot.py').read_text())
    if audit['ct'] in [618,622]:self.assertIn("if c['running'] and not c['name'].startswith",(out/'observe.py').read_text())
    for p in out.glob('*.py'):ast.parse(p.read_text())
 def test_no_rollback_is_executed_by_critical_mutate(self):
  m=load('run-critical-exporter-wave.py');r=object.__new__(m.CriticalRunner)
  for method in ['namespace','helper','mark','point']:setattr(r,method,Mock())
  r.monitor=Mock();r.identities=Mock(return_value={'node_exporter':{'id':'stable'}});r.state={}
  with patch.object(m,'verify_recovery_procedure'):r.mutate()
  r.monitor.rollback.assert_not_called();self.assertNotIn(('rollback',),[c.args for c in r.helper.call_args_list]);r.monitor.idempotence.assert_called_once()
 def test_recovery_applies_to_five_critical_targets_without_extending_blocked_scope(self):
  m=load('run-critical-exporter-wave.py');self.assertEqual(m.ORDER,[618,622,611,616,610]);self.assertFalse(set(m.ORDER)&{617,615,614})
 def test_external_observer_has_no_prometheus_api_dependency(self):
  m=load('run-critical-exporter-wave.py');source=__import__('inspect').getsource(m.ExternalWatch.sample)
  self.assertNotIn('/api/v1',source);self.assertIn('pct',source);self.assertIn('/metrics',source);self.assertIn('/-/ready',source)
 def test_resume_requires_positive_isolation_before_creating_run_or_mutating(self):
  import argparse
  m=load('run-critical-exporter-wave.py')
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'isolation.json';p.write_text(json.dumps({'isolated_local_measurement':False}))
   args=argparse.Namespace(start_ct=622,isolation_evidence=p,run='integration-00000000T000000Z',output=Path(d)/'out.json')
   policy={'decision':'D-039','status':'AUTHORIZED','allowed_mutation_cts':[622,611,616,610]}
   with patch.object(m.yaml,'safe_load',return_value=policy):
    with self.assertRaises(AssertionError):m.run(args)
   self.assertFalse(args.output.exists())
 def test_window_is_frozen_at_observation_entry_even_when_policy_changes(self):
  m=load('run-critical-exporter-wave.py');r=object.__new__(m.CriticalRunner);r.ct=622;r.manifest={};r.state={}
  with tempfile.TemporaryDirectory() as d:
   r.here=Path(d);window={'observation_seconds':300,'minimum_samples':11}
   profiles=Mock();profiles.profile_for.return_value=window
   def during_observation():
    window.update(observation_seconds=180,minimum_samples=7)
    self.assertEqual((r.manifest['initial_seconds'],r.manifest['initial_minimum_samples']),(300,11))
   r.observe_and_telegram=during_observation
   with patch.object(m,'load',return_value=profiles):r.observe(batch_end=True)
   self.assertEqual(r.state['observation_policy']['seconds'],300)
   self.assertTrue(r.state['observation_policy']['frozen_at_observation_start'])
if __name__=='__main__':unittest.main()
