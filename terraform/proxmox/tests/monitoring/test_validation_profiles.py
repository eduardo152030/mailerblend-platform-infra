import importlib.util
from pathlib import Path
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[2]

def load(name):
    spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/name)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

class ProfileTests(unittest.TestCase):
    def setUp(self):
        self.m=load('phase4-validation-profiles.py')
        self.good={k:True for k in ['preflight_pass','backup_verified','node_ready','cadvisor_ready','lxc_cpu_ram_correct','docker_metrics_correct','timestamps_identity_valid','application_baseline_verified','application_no_regression','preexisting_alerts_preserved','critical_dependencies_verified','prometheus_collecting','alertmanager_ready','telegram_errors_unchanged','no_new_oom','no_unexpected_restarts','rollback_available','idempotence_verified','all_observation_samples_passed']}
        self.good.update(telegram_test_required=False,rollback_proof={'result':'PASS','evidence_verified':True,'fingerprint':'a'*64},rollback_fingerprint='a'*64,sample_elapsed_seconds=list(range(0,181,30)))
    def test_pending_are_all_critical_and_no_scope_is_expanded(self):
        import yaml
        known=[yaml.safe_load(p.read_text())['service']['vmid'] for p in (ROOT/'inventory/services').glob('*.yml')]
        # Scenario fixture stays independent of the mutable production migration registry.
        reg={'prometheus_integrated':[624,626,625,613,621,620,619,623,61211]}
        queue={'items':[{'ct':ct} for ct in [617,615,614]]}
        plan=self.m.plan(reg,queue,known)
        self.assertEqual(plan['authorized_standard_order'],[])
        self.assertEqual([r['ct'] for r in plan['pending']],[618,622,611,616,610])
        self.assertEqual(set(plan['blocked']),{617,615,614})
        self.assertEqual(len(plan['accepted']),9)
        self.assertTrue(all(r['profile']=='CRITICAL' for r in plan['pending']))
        with self.assertRaises(ValueError):self.m.profile_for(99999,known)
    def test_standard_accepts_180_seconds_without_watch_or_new_delivery(self):
        self.assertTrue(self.m.assess(self.good,'STANDARD')['accepted'])
        self.assertFalse(self.m.assess(self.good,'STANDARD')['additional_watch_required'])
        self.assertTrue(load('phase4-skip-policy.py').decide(self.good|{'completed':True,'validation_profile':'STANDARD'}, {})['continue'])
    def test_unhealthy_baseline_may_pass_only_without_regression_and_preserved_alerts(self):
        e=self.good|{'application_healthy_before':False,'application_healthy_after':False}
        self.assertTrue(self.m.assess(e,'STANDARD')['accepted'])
        for k in ['application_no_regression','application_baseline_verified','preexisting_alerts_preserved']:
            self.assertFalse(self.m.assess(e|{k:False},'STANDARD')['accepted'])
    def test_missing_invalid_or_failed_samples_cannot_pass(self):
        for k in ['lxc_cpu_ram_correct','docker_metrics_correct','timestamps_identity_valid','backup_verified','alertmanager_ready','telegram_errors_unchanged','no_new_oom','idempotence_verified']:
            e=dict(self.good);e.pop(k);self.assertFalse(self.m.assess(e,'STANDARD')['accepted'],k)
        for times in [[0]*7,[0,30,60,90,120,150,179],[0,30,60,90,120,150,float('nan')],[0,30,60,90,120,150,True],[30,60,90,120,150,180,210]]:
            self.assertFalse(self.m.assess(self.good|{'sample_elapsed_seconds':times},'STANDARD')['accepted'])
        self.assertFalse(self.m.assess(self.good|{'all_observation_samples_passed':False},'STANDARD')['accepted'])
    def test_critical_requires_longer_window_and_continuity_recovery(self):
        self.assertFalse(self.m.assess(self.good,'CRITICAL')['accepted'])
        e=self.good|{'sample_elapsed_seconds':list(range(0,601,30)),'continuity_verified':True,'recovery_verified':True}
        self.assertTrue(self.m.assess(e,'CRITICAL')['accepted'])
        for k in ['continuity_verified','recovery_verified']:
            self.assertFalse(self.m.assess(e|{k:False},'CRITICAL')['accepted'])
    def test_reuse_invalidated_by_code_dependencies_or_unverified_evidence(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/'procedure';f.write_text('v1');fp=self.m.fingerprint([f],{'python':'3.10','docker':'29.1.3'});proof={'result':'PASS','evidence_verified':True,'fingerprint':fp}
            self.assertTrue(self.m.reusable_proof(proof,fp))
            self.assertFalse(self.m.reusable_proof(proof,self.m.fingerprint([f],{'python':'3.11','docker':'29.1.3'})))
            f.write_text('v2');self.assertFalse(self.m.reusable_proof(proof,self.m.fingerprint([f],{'python':'3.10','docker':'29.1.3'})))
            self.assertFalse(self.m.reusable_proof(proof|{'evidence_verified':False},fp))
        self.assertFalse(self.m.assess(self.good|{'rollback_fingerprint':'b'*64},'STANDARD')['accepted'])
        self.assertTrue(self.m.assess(self.good|{'rollback_fingerprint':'b'*64,'rollback_rehearsal_pass':True},'STANDARD')['accepted'])
    def test_delivery_test_is_required_for_changed_config_or_unverified_batch(self):
        for required in [True,None]:
            e=self.good|{'telegram_test_required':required};self.assertFalse(self.m.assess(e,'STANDARD')['accepted'])
            self.assertTrue(self.m.assess(e|{'batch_telegram_delivery_verified':True},'STANDARD')['accepted'])
    def test_observation_policy_selects_profiles_without_changing_historical_windows(self):
        m=load('rollout-observation-policy.py')
        for name,seconds,count in [('STANDARD',180,7),('CRITICAL',600,21)]:
            p=m.policy(name);self.assertEqual((p['seconds'],p['minimum_samples'],p['watch_seconds']),(seconds,count,0))
        self.assertEqual(m.policy('R5')['watch_seconds'],900)

    def test_d040_windows_are_ct_specific_and_shortened_windows_still_require_all_gates(self):
        known=[617,615,614,618,622,611,616,610]
        for ct,seconds,count in [(617,180,7),(615,180,7),(614,180,7),(618,300,11),(622,300,11),(611,180,7),(616,180,7),(610,600,21)]:
            p=self.m.profile_for(ct,known)
            self.assertEqual((p['observation_seconds'],p['minimum_samples']),(seconds,count))
            e=self.good|{'ct':ct,'sample_elapsed_seconds':list(range(0,seconds+1,30)),'continuity_verified':True,'recovery_verified':True}
            self.assertTrue(self.m.assess(e,p['name'])['accepted'])
            for key in ['lxc_cpu_ram_correct','docker_metrics_correct','node_ready','cadvisor_ready','application_no_regression','no_new_oom','no_unexpected_restarts','prometheus_collecting','alertmanager_ready','telegram_errors_unchanged','backup_verified','rollback_available']:
                self.assertFalse(self.m.assess(e|{key:False},p['name'])['accepted'],key)
            self.assertFalse(self.m.assess(e|{'sample_elapsed_seconds':list(range(0,seconds,30))},p['name'])['accepted'])
if __name__=='__main__':unittest.main()
