import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import yaml
ROOT=Path(__file__).resolve().parents[2]
def load(name):
 s=importlib.util.spec_from_file_location(name,ROOT/'scripts'/name);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

class SkipPolicyTests(unittest.TestCase):
 def setUp(self):
  self.m=load('phase4-skip-policy.py');self.policy=yaml.safe_load((ROOT/'services/common/phase4-skip-policy.yml').read_text());self.policy.update(order=[614,61211],deferred=[617,615]);self.safe=dict(completed=False,category='local_exporter_runtime',**{k:True for k in self.m.REQUIRED})
 def test_only_positive_isolation_and_complete_safety_evidence_allow_skip(self):
  self.assertEqual(self.m.decide(self.safe,self.policy)['result'],'BLOCKED / ROLLED BACK')
  for k in self.m.REQUIRED:
   for value in [False,None]:
    self.assertEqual(self.m.decide(self.safe|{k:value},self.policy)['result'],'HALT GLOBAL',k)
 def test_global_and_unknown_errors_never_skip_even_with_other_positive_evidence(self):
  for category in list(self.m.GLOBAL)+['unclassified']:
   self.assertEqual(self.m.decide(self.safe|{'category':category},self.policy)['result'],'HALT GLOBAL')
 def test_inherited_unhealthy_application_without_mutation_still_does_not_satisfy_skip(self):
  evidence=self.safe|dict(category='application_preflight',no_active_changes=True,application_working=False)
  rows=[];calls=[]
  def attempt(ct):calls.append(ct);return evidence
  self.m.sequence(self.policy,attempt,rows.append)
  self.assertEqual(calls,[614]);self.assertEqual(rows[0]['result'],'HALT GLOBAL')
 def test_verified_local_failure_advances_once_to_next_authorized_ct(self):
  calls=[];rows=[]
  def attempt(ct):calls.append(ct);return self.safe
  self.m.sequence(self.policy,attempt,rows.append)
  self.assertEqual(calls,[614,61211]);self.assertEqual(len(rows),2)
 def test_done_requires_full_watch_and_all_acceptance_gates(self):
  good=dict(completed=True,all_acceptance_gates=True,initial_observation_pass=True,watch_pass=True,global_monitoring_healthy=True,application_healthy_before=True,application_healthy_after=True,critical_dependencies_verified=True)
  self.assertEqual(self.m.decide(good,self.policy)['result'],'DONE')
  for key in ['all_acceptance_gates','initial_observation_pass','watch_pass','global_monitoring_healthy','application_healthy_before','application_healthy_after','critical_dependencies_verified']:
   self.assertEqual(self.m.decide(good|{key:False},self.policy)['result'],'HALT GLOBAL')
 def test_unexpected_driver_failure_is_global_and_does_not_start_next_ct(self):
  calls=[];rows=[]
  def attempt(ct):calls.append(ct);raise RuntimeError('unknown')
  self.m.sequence(self.policy,attempt,rows.append);self.assertEqual(calls,[614]);self.assertEqual(rows[0]['result'],'HALT GLOBAL')
 def test_deferred_excluded_and_duplicate_cts_cannot_enter_wave(self):
  for order in [[614,617],[614,618],[614,614]]:
   with self.assertRaises(AssertionError):self.m.sequence(self.policy|{'order':order},lambda ct:self.safe,lambda r:None)
 def test_original_proof_requires_originals_and_app_config_unchanged(self):
  m=load('run-skip-exporter-wave.py');c={'id':'1','image':'img','running':True,'started_at':'old','restarts':0,'oom_killed':False,'config_hash':'hash'};before={n:dict(c,id=n) for n in ['app','cadvisor','node_exporter']};after=copy.deepcopy(before)
  after['node_exporter']['started_at']='controlled rollback';self.assertTrue(m.original_proof(before,after))
  after['app']['started_at']='unexpected';self.assertFalse(m.original_proof(before,after))
 def test_both_authorized_candidates_have_temporal_ram_and_normal_three_minute_window(self):
  builder=load('prepare-617-memory.py');audits=json.loads((ROOT/'docs/roadmap/evidence/2026-11-02-rollout-authenticated-preflight.json').read_text())
  for ct in [614,61211]:
   with tempfile.TemporaryDirectory() as d:
    out=Path(d);manifest=builder.render(out,next(r for r in audits if r['ct']==ct))
    self.assertEqual((manifest['initial_seconds'],manifest['initial_minimum_samples']),(180,7));self.assertIn('memory-alignment.py',manifest['file_sha256']);self.assertIn(f"-phase4-{ct}-{manifest['framework_revision']}-held",(out/'pilot.py').read_text());self.assertNotIn(f"'-phase4-{ct}-held'",(out/'pilot.py').read_text())

 def test_case_b_skips_unchanged_inherited_unhealthy_app_with_verified_independence(self):
  inherited=dict(completed=False,category='pre_existing_application',application_working=False,**{k:True for k in self.m.PREEXISTING})
  row=self.m.decide(inherited,self.policy);self.assertEqual((row['case'],row['result'],row['continue']),('B','BLOCKED / PRE-EXISTING ISSUE',True))
  for key in self.m.PREEXISTING:
   self.assertEqual(self.m.decide(inherited|{key:False},self.policy)['result'],'HALT GLOBAL',key)
  rows=[];calls=[]
  def attempt(ct):calls.append(ct);return inherited if ct==614 else self.safe
  self.m.sequence(self.policy,attempt,rows.append);self.assertEqual(calls,[614,61211])
 def test_case_b_never_overrides_backup_or_critical_dependency_failures(self):
  inherited=dict(completed=False,category='pre_existing_application',**{k:True for k in self.m.PREEXISTING})
  for category in self.m.GLOBAL:
   self.assertEqual(self.m.decide(inherited|{'category':category},self.policy)['result'],'HALT GLOBAL')
 def test_case_c_regression_requires_both_health_restoration_and_containment(self):
  regression=self.safe|dict(category='application_regression',baseline_health_restored=True,regression_contained=True)
  self.assertEqual(self.m.decide(regression,self.policy)['case'],'C')
  for key in ['baseline_health_restored','regression_contained']:
   self.assertEqual(self.m.decide(regression|{key:False},self.policy)['result'],'HALT GLOBAL')

 def test_backend_application_gate_raises_before_promotion_on_unhealthy_result(self):
  from unittest.mock import patch
  m=load('run-skip-exporter-wave.py')
  with patch.object(m,'application_working',return_value=False):
   with self.assertRaises(RuntimeError):m.require_application_working(object())
  with patch.object(m,'application_working',return_value=True):self.assertTrue(m.require_application_working(object()))

if __name__=='__main__':unittest.main()
