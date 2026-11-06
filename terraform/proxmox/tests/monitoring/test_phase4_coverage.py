"""Offline regression checks for inventory generation and false-green monitoring evidence."""
import copy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
import yaml

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


generator = load('targets', 'gen-prom-targets.py')
validator = load('phase4', 'validate-phase4-evidence.py')
blackbox = load('blackbox', 'validate-blackbox-targets.py')


class Phase4Tests(unittest.TestCase):
    def setUp(self):
        self.runtime = json.loads((ROOT / 'docs/roadmap/evidence/2026-11-02-runtime-audit.json').read_text())
        self.expected = [s['name'] for s in generator.load_services()]

    def good_evidence(self):
        runtime = copy.deepcopy(self.runtime)
        targets = []
        for service in runtime['services']:
            rt = service['runtime']
            rt['node_endpoint'] = {'http': 200, 'cpu_count': int(service['proxmox']['cores']),
                                   'memory_total': int(service['proxmox']['memory']) * 1024 * 1024,
                                   'cpu_source':'cgroup_v2_textfile','cpu_ct_id':str(service['ct']),
                                   'native_cpu_time_series_count':0,'cpu_collector_success':1,'cpu_collector_age_seconds':2,
                                   'textfile_scrape_error':0,'cpu_capacity_cores':int(service['proxmox']['cores']),
                                   'cpu_usage_seconds':10,'cpu_user_seconds':6,'cpu_system_seconds':4}
            names = [c['name'] for c in rt['containers'] if c['running']]
            rt['cadvisor_endpoint'] = {'http': 200, 'memory_container_names': names, 'cpu_container_names': names}
            targets += [{'service': service['service'], 'job': job, 'health': 'up'} for job in ['node_exporter', 'cadvisor']]
        targets.append({'service': 'infra-grafana', 'job': 'grafana', 'health': 'up'})
        probes = [{'metric': {'service': name}, 'value': [0, '1']} for name in self.expected if name.startswith('infra-journal-')]
        return runtime, {'targets': targets, 'journal_probe_success': probes}

    def test_generation_covers_17_and_preserves_base_blackbox(self):
        base = blackbox.CATALOG.read_bytes()
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)
            counts = generator.generate(ROOT / 'inventory/services', output)
            first = {p.name: p.read_bytes() for p in output.iterdir()}
            generator.generate(ROOT / 'inventory/services', output)
            self.assertEqual(first, {p.name: p.read_bytes() for p in output.iterdir()})
            self.assertEqual(counts, {'node-exporter.json': 17, 'cadvisor.json': 17, 'grafana.json': 1, 'blackbox-journal.json': 3})
            journal = json.loads(first['blackbox-journal.json'])
            self.assertEqual(blackbox.validate(json.loads(base) + journal), 14)
        self.assertEqual(blackbox.CATALOG.read_bytes(), base)

    def test_duplicate_inventory_fails_before_writing(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            inventory = directory / 'inventory'; inventory.mkdir()
            row = {'service': {'name': 'duplicate', 'ip': '192.0.2.1/24', 'vmid': 1}}
            for name in ['a.yml', 'b.yml']:
                (inventory / name).write_text(yaml.safe_dump(row))
            out = directory / 'out'
            with self.assertRaises(ValueError):
                generator.generate(inventory, out)
            self.assertFalse(out.exists())

    def test_current_evidence_is_not_falsely_accepted(self):
        monitoring = json.loads((ROOT / 'docs/roadmap/evidence/2026-11-02-monitoring-audit.json').read_text())
        issues = validator.assess(self.runtime, monitoring, self.expected)
        self.assertTrue(any('Node RAM differs' in issue for issue in issues))
        self.assertTrue(any('individual Docker' in issue for issue in issues))
        self.assertTrue(any('Grafana' in issue for issue in issues))
        self.assertTrue(any('journal' in issue for issue in issues))

    def test_complete_synthetic_core_evidence_passes(self):
        runtime, monitoring = self.good_evidence()
        self.assertEqual(validator.assess(runtime, monitoring, self.expected), [])

    def test_http_200_root_series_does_not_prove_docker_visibility(self):
        runtime, monitoring = self.good_evidence()
        runtime['services'][0]['runtime']['cadvisor_endpoint'] = {'http': 200, 'memory_series': 1, 'named_memory_series': 0}
        self.assertTrue(any('individual Docker' in x for x in validator.assess(runtime, monitoring, self.expected)))

    def test_memory_capacity_mismatch_is_rejected(self):
        runtime, monitoring = self.good_evidence()
        runtime['services'][0]['runtime']['node_endpoint']['memory_total'] = 16646774784
        self.assertTrue(any('Node RAM differs' in x for x in validator.assess(runtime, monitoring, self.expected)))

    def test_cgroup_cpu_collector_requires_fresh_correct_ct_identity(self):
        runtime, monitoring = self.good_evidence()
        service = runtime['services'][0]
        node = service['runtime']['node_endpoint']
        node.update(cpu_source='cgroup_v2_textfile', native_cpu_time_series_count=0, cpu_collector_success=1, cpu_ct_id=str(service['ct']), cpu_collector_age_seconds=2)
        self.assertEqual(validator.assess(runtime,monitoring,self.expected),[])
        node['cpu_collector_age_seconds']=60
        self.assertTrue(any('stale' in x for x in validator.assess(runtime,monitoring,self.expected)))
        node['cpu_ct_id']='999'
        self.assertTrue(any('another CT' in x for x in validator.assess(runtime,monitoring,self.expected)))

    def test_cpu_unknown_missing_nonfinite_negative_and_wrong_capacity_fail_closed(self):
        for field,value in [('cpu_source','procfs_unverified'),('cpu_capacity_cores',0),('cpu_capacity_cores',99),('cpu_usage_seconds',None),('cpu_usage_seconds',float('nan')),('cpu_user_seconds',float('inf')),('cpu_system_seconds',-1),('textfile_scrape_error',1),('cpu_collector_age_seconds',float('nan'))]:
            with self.subTest(field=field,value=value):
                runtime,monitoring=self.good_evidence()
                runtime['services'][0]['runtime']['node_endpoint'][field]=value
                self.assertTrue(validator.assess(runtime,monitoring,self.expected))

    def test_duplicate_healthy_scrapes_are_rejected(self):
        runtime, monitoring = self.good_evidence()
        monitoring['targets'].append(copy.deepcopy(monitoring['targets'][0]))
        self.assertTrue(any('exactly one healthy' in x for x in validator.assess(runtime, monitoring, self.expected)))

    def test_ram_without_per_container_cpu_is_rejected(self):
        runtime, monitoring = self.good_evidence()
        runtime['services'][0]['runtime']['cadvisor_endpoint']['cpu_container_names'] = []
        self.assertTrue(any('Docker CPU' in x for x in validator.assess(runtime, monitoring, self.expected)))

    def test_tcp_probe_identity_and_duplicates_are_checked(self):
        tcp = next(r for r in generator.journal_groups(generator.load_services()) if r['labels']['module'] == 'tcp_connect')
        self.assertEqual(tcp['targets'], ['192.168.1.125:5432'])
        self.assertEqual(blackbox.validate([tcp]), 1)
        broken = copy.deepcopy(tcp); broken['labels']['alert_target'] = 'http://192.168.1.125/'
        with self.assertRaises(ValueError):blackbox.validate([broken])
        duplicate = copy.deepcopy(tcp); duplicate['labels']['probe_id'] = 'another-id'
        with self.assertRaises(ValueError):blackbox.validate([tcp, duplicate])

    def test_node_image_lock_preserves_all_installed_versions(self):
        lock = json.loads((ROOT / 'services/common/phase4-images.json').read_text())
        for service in self.runtime['services']:
            installed = next((c for c in service['runtime']['containers'] if c['name'] == 'node_exporter'), None)
            item = lock['node'][service['service']]
            if installed:
                self.assertEqual(item['image'], 'prom/node-exporter@' + installed['image_id'])
            else:
                self.assertTrue(item['new_install_requires_approved_download'])

    def test_grafana_and_explicit_probe_catalogs_are_wired(self):
        config = yaml.safe_load((ROOT / 'services/infra-prom/config/prometheus.yml').read_text())
        grafana = [j for j in config['scrape_configs'] if j['job_name'] == 'grafana']
        self.assertEqual(len(grafana), 1)
        self.assertEqual(grafana[0]['file_sd_configs'][0]['files'], ['/etc/prometheus/targets/grafana.json'])
        job = next(j for j in config['scrape_configs'] if j['job_name'] == 'blackbox')
        self.assertEqual(job['file_sd_configs'][0]['files'], ['/etc/prometheus/targets/blackbox.json', '/etc/prometheus/targets/blackbox-journal.json'])


if __name__ == '__main__':
    unittest.main()
