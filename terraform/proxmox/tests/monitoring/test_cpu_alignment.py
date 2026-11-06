import copy
import ast
import importlib.util
import json
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import patch

spec=importlib.util.spec_from_file_location('alignment',Path(__file__).resolve().parents[2]/'scripts/exporter-cpu-alignment.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class AlignmentTests(unittest.TestCase):
    def setUp(self):
        self.history=[{'id':'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa','started_at':'generation1','time':float(t),'docker_seconds':10+(t-100)*.5,'cgroup_seconds':10+(t-100)*.5} for t in range(100,201)]
        self.sample={'containers':[{'running':True,'id':'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa','started_at':'generation1','name':'cadvisor'}], 'cadvisor':{'container_cpu_usage_seconds_total':[{'labels':{'name':'cadvisor','id':'/docker-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.scope'},'value':10.5,'timestamp':101.0}]}}

        self.sample['measurement_scope']='fixture-cpu'
        for point in self.history:point['measurement_scope']='fixture-cpu'

    def evidence(self,sample=None,history=None):
        with patch.object(m.time,'time',return_value=110):return m.aligned_evidence(sample or self.sample,history or self.history)

    def test_cached_counter_matches_same_instant_without_larger_tolerance(self):
        # Comparing current Docker (15s at t110) with cached cAdvisor (10.5s at t101)
        # fails the original 1s threshold. Aligned t101 passes without changing it.
        self.assertGreater(abs(15-10.5),m.tolerance(15))
        point=self.evidence()['aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'];self.assertEqual(point['docker_seconds'],10.5)
        self.assertEqual(m.tolerance(point['docker_seconds']),1)

    def test_genuine_wrong_counter_still_fails(self):
        for value in [12.5,5.25,21.0]:
            sample=copy.deepcopy(self.sample);sample['cadvisor']['container_cpu_usage_seconds_total'][0]['value']=value
            with self.subTest(value=value),self.assertRaises(AssertionError):self.evidence(sample)

    def test_missing_timestamps_history_identity_and_resets_fail_closed(self):
        for modify in [lambda s:s['cadvisor']['container_cpu_usage_seconds_total'][0].pop('timestamp'), lambda s:s['containers'][0].update(id='other'),lambda s:s['containers'][0].update(started_at='generation2'),lambda s:s['cadvisor']['container_cpu_usage_seconds_total'][0].update(timestamp=1)]:
            sample=copy.deepcopy(self.sample);modify(sample)
            with self.assertRaises(AssertionError):self.evidence(sample)
        with self.assertRaises(AssertionError):self.evidence(history=[self.history[0],self.history[4]])
        h=copy.deepcopy(self.history);h[1]['docker_seconds']=0
        with self.assertRaises(AssertionError):self.evidence(history=h)

    def test_bounds_must_pass_not_only_interpolated_estimate(self):
        h=copy.deepcopy(self.history);h[0]['docker_seconds']=8.9
        with self.assertRaises(AssertionError):self.evidence(history=h)

    def test_equivalent_window_rates_reject_drift_even_when_cumulative_tolerance_is_large(self):
        old=copy.deepcopy(self.sample);old['cpu_alignment']=self.evidence()
        new=copy.deepcopy(self.sample);new['cpu_alignment']=copy.deepcopy(old['cpu_alignment'])
        p=new['cpu_alignment']['aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'];p.update(time=131,docker_seconds=25.5,cgroup_seconds=25.5,cadvisor_seconds=25.5,bounds={'docker_seconds':[25,26],'cgroup_seconds':[25,26]})
        new['cadvisor']['container_cpu_usage_seconds_total'][0].update(value=25.5,timestamp=131)
        with patch.object(m.time,'time',return_value=135):m.validate_alignment(new,old)
        # Large counters could hide 2s drift under 3% cumulative tolerance; delta gate cannot.
        for sample in [old,new]:
            p=sample['cpu_alignment']['aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa']
            for field in ['docker_seconds','cgroup_seconds','cadvisor_seconds']:p[field]+=1000
            sample['cadvisor']['container_cpu_usage_seconds_total'][0]['value']+=1000
            for field in p['bounds']:p['bounds'][field]=[x+1000 for x in p['bounds'][field]]
        new['cpu_alignment']['aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa']['cadvisor_seconds']+=2
        new['cadvisor']['container_cpu_usage_seconds_total'][0]['value']+=2
        with patch.object(m.time,'time',return_value=135),self.assertRaisesRegex(AssertionError,'window mismatch'):m.validate_alignment(new,old)

    def test_cpu_count_is_not_used_to_scale_cumulative_counters(self):
        self.sample['lxc_proc']={'cpu_count':2};a=self.evidence()
        self.sample['lxc_proc']['cpu_count']=4
        self.assertEqual(self.evidence(),a)

    def test_docker_nanosecond_timestamp_supported_on_python310(self):
        self.assertAlmostEqual(m.timestamp('2026-11-03T08:12:11.5352061Z'),1793693531.535206,places=5)

    def test_partial_append_is_ignored_and_timeline_still_must_bracket_timestamp(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'history';path.write_text(''.join(json.dumps(r)+'\n' for r in self.history)+'{"partial":')
            self.assertEqual(m.history_for_sample(self.sample,path),[r for r in self.history if 99<=r['time']<=103])

    def test_generated_sampler_keeps_explicit_metric_timestamp_and_validator_enforces_alignment(self):
        root=Path(__file__).resolve().parents[2]
        spec=importlib.util.spec_from_file_location('builder',root/'scripts/prepare-approved-exporters.py');builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
        audit=next(r for r in json.loads((root/'docs/roadmap/evidence/2026-11-02-rollout-authenticated-preflight.json').read_text()) if r['ct']==619)
        with tempfile.TemporaryDirectory() as d:
            builder.render(619,Path(d),audit)
            ns={'rows':m.mc.prom_rows}
            row=ns['rows']('container_cpu_usage_seconds_total{id="aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",name="cadvisor"} 10.665283 1793692406977','container_cpu_usage_seconds_total')[0]
            self.assertEqual(row['timestamp'],1793692406.977)
            self.assertEqual(row['value'],10.665283)
            observer=(Path(d)/'observe.py').read_text()
            self.assertIn('validate_alignment(sample,previous)',observer)
            self.assertNotIn("abs(row['value']-api['cpu_total_ns']/1e9)",observer)

    def test_container_stop_between_list_inspect_and_proc_read_does_not_kill_collector(self):
        for c in [None,{'State':{'Running':False,'Pid':0}},{'State':{'Running':True,'Pid':0}}]:
            with patch.object(m.Path,'read_text') as reader:
                self.assertIsNone(m.container_cpu_path(c,'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'));reader.assert_not_called()
        with patch.object(m.Path,'read_text',side_effect=FileNotFoundError):
            self.assertIsNone(m.container_cpu_path({'State':{'Running':True,'Pid':10}},'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'))
        with patch.object(m.Path,'read_text',return_value='0::/docker-other.scope\n'):
            with self.assertRaisesRegex(AssertionError,'identity mismatch'):m.container_cpu_path({'State':{'Running':True,'Pid':10}},'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')

    def test_stale_counter_failure_retains_identity_timestamp_value_and_private_sample(self):
        with tempfile.TemporaryDirectory() as d:
            with patch.object(m.time,'time',return_value=200):
                try:m.aligned_evidence(self.sample,self.history)
                except AssertionError as exc:
                    self.assertIn('cadvisor id=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',str(exc));self.assertIn('age_seconds=99.0',str(exc))
                    m.record_probe_failure(self.sample,Path(d)/'cpu-history.jsonl',exc)
                else:self.fail('Stale metric must fail')
            path=Path(d)/'cpu-probe-failures.jsonl';saved=json.loads(path.read_text())
            self.assertEqual(saved['sample'],self.sample)
            self.assertIn('cpu_seconds=10.5',saved['message'])
            self.assertEqual(path.stat().st_mode & 0o777,0o600)
