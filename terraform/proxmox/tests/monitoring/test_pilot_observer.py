"""Acceptance must reject wrong CPU sources, missing freshness and OOM despite HTTP 200."""
import copy
import importlib.util
import json
from pathlib import Path
import sys
import unittest

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('observer',ROOT/'scripts/observe-exporter-pilot-624.py')
observer=importlib.util.module_from_spec(spec);spec.loader.exec_module(observer)
FIXTURE=ROOT/'docs/roadmap/evidence/2026-11-02-pilot624-metric-samples.json'


class ObserverTests(unittest.TestCase):
    def setUp(self):
        self.first=json.loads(FIXTURE.read_text())['first']

    def test_real_sanitized_pilot_sample_passes(self):
        observer.validate(copy.deepcopy(self.first),self.first)

    def test_shared_host_cpu_counter_is_rejected(self):
        bad=copy.deepcopy(self.first)
        bad['node']['lxc_cpu_usage_seconds_total'][0]['value']=385000
        with self.assertRaises(AssertionError):observer.validate(bad,self.first)

    def test_missing_container_freshness_is_rejected(self):
        bad=copy.deepcopy(self.first);bad['cadvisor']['container_last_seen']=[]
        with self.assertRaises(AssertionError):observer.validate(bad,self.first)

    def test_oom_is_rejected_even_with_web_200(self):
        bad=copy.deepcopy(self.first)
        bad['resources']['memory.events']=bad['resources']['memory.events'].replace('oom_kill 0','oom_kill 1')
        with self.assertRaises(AssertionError):observer.validate(bad,self.first)

    def test_timestamp_misparsed_as_ram_is_rejected(self):
        bad=copy.deepcopy(self.first)
        bad['cadvisor']['container_memory_usage_bytes'][0]['value']=1793633981033
        with self.assertRaises(AssertionError):observer.validate(bad,self.first)


if __name__=='__main__':unittest.main()
