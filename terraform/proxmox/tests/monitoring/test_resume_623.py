import copy
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import json
from types import SimpleNamespace

ROOT=Path(__file__).resolve().parents[2]
def load(name):
    spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/name);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

class Resume623Tests(unittest.TestCase):
    def test_post_watch_failure_revokes_only_617_with_complete_observation(self):
        m=load('rollback-post-watch-617.py');state={'ct':617,'result':'PASS'};watch={'result':'FAIL','seconds':901};registry={'prometheus_integrated':[624,626,625,613,621,620,619,623,617]}
        m.rollback_gate(state,watch,registry)
        for change in [{'result':'PASS'},{'seconds':899}]:
            with self.assertRaises(AssertionError):m.rollback_gate(state,watch|change,registry)
        with self.assertRaises(AssertionError):m.rollback_gate(state|{'ct':623},watch,registry)

    def test_blocked_policy_allows_recovery_without_allowing_new_deployment(self):
        import yaml
        m=load('rollout-approved-exporters.py')
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);p=root/'services/common';p.mkdir(parents=True);(p/'phase4-execution-policy.yml').write_text(yaml.safe_dump({'status':'BLOCKED','allowed_mutation_cts':[623,617,615,614,61211],'allowed_recovery_cts':[617],'automatic_rollout':False}))
            with patch.object(m,'ROOT',root):
                m.execution_gate(617,recovery=True)
                with self.assertRaises(RuntimeError):m.execution_gate(617)
                with self.assertRaises(RuntimeError):m.execution_gate(623,recovery=True)

    def test_future_preflight_failure_halts_without_calling_remote_rollback(self):
        m=load('recover-approved-wave.py')
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);here=root/'615';here.mkdir();state={'ct':615,'steps':['preflight_resources'],'result':'BLOCKED'}
            r=SimpleNamespace(ct=615,here=here,root=root,state=state)
            import unittest.mock
            api=SimpleNamespace(execution_gate=unittest.mock.Mock(),save=lambda p,v:p.write_text(json.dumps(v)))
            m.recover(r,api)
            self.assertEqual(state['result'],'BLOCKED_NO_CHANGES');self.assertTrue((root/'HALT.json').exists())

    def test_fixed_cadence_is_scoped_to_new_r4_r5_candidates(self):
        import yaml
        m=load('prepare-approved-exporters.py');rows=json.loads((ROOT/'docs/roadmap/evidence/2026-11-02-rollout-authenticated-preflight.json').read_text())
        for ct in [617,615,614,61211,610]:
            with tempfile.TemporaryDirectory() as d:
                out=Path(d);m.render(ct,out,next(r for r in rows if r['ct']==ct));args=yaml.safe_load((out/'cadvisor.yml').read_text())['services']['cadvisor']['command']
                self.assertEqual('--allow_dynamic_housekeeping=false' in args,ct!=610)

    def test_only_known_reverted_ct_and_incident_can_be_reentered(self):
        m=load('resume-623-cadence.py');state={'ct':623,'result':'BLOCKED_ROLLED_BACK','safe_rollback_verified':True};marker={'ct':623,'reason':'cpu_metric_data_stale','threshold_seconds':90};registry={'prometheus_integrated':[624,626,625,613,621,620,619],'remaining_order':[623,617]}
        m.reentry_gate(state,marker,registry)
        for change in [{'ct':619},{'result':'PASS'},{'safe_rollback_verified':False}]:
            with self.assertRaises(AssertionError):m.reentry_gate(state|change,marker,registry)
        with self.assertRaises(AssertionError):m.reentry_gate(state,marker|{'reason':'new_watcher_anomaly'},registry)
        with self.assertRaises(AssertionError):m.reentry_gate(state,marker,registry|{'prometheus_integrated':registry['prometheus_integrated']+[623]})

    def test_promtool_checks_actual_discovery_and_rejects_duplicate_identities(self):
        m=load('apply-incremental-config.py')
        def discovery(job,count):return json.dumps([{'labels':{'job':job,'instance':'host'+str(n),'module':'http_2xx','probe_type':'public'}} for n in range(count)]).encode()
        with tempfile.TemporaryDirectory() as d,patch.object(m,'ids',return_value={'prometheus':{'Image':'pinned'}}),patch.object(m,'run',side_effect=[b'',discovery('node',17),discovery('cadvisor',17),discovery('blackbox',11)]) as run:
            m.validate(Path(d));self.assertEqual(run.call_count,4);self.assertIn('--pull=never',run.call_args.args[0])
        duplicate=json.dumps([{'labels':{'job':'node','instance':'same'}}]*17).encode()
        with tempfile.TemporaryDirectory() as d,patch.object(m,'ids',return_value={'prometheus':{'Image':'pinned'}}),patch.object(m,'run',side_effect=[b'',duplicate]):
            with self.assertRaisesRegex(AssertionError,'Duplicate'):m.validate(Path(d))
