import copy
import importlib.util
import json
from pathlib import Path
import unittest
import sys

sys.dont_write_bytecode = True
from urllib.parse import parse_qs, urlsplit

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('catalog', ROOT/'scripts/validate-blackbox-targets.py')
catalog = importlib.util.module_from_spec(spec)
spec.loader.exec_module(catalog)


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.rows = json.loads(catalog.CATALOG.read_text())

    def test_catalog_has_no_duplicate_requests(self):
        self.assertEqual(catalog.validate(self.rows), 11)

    def test_duplicate_request_under_different_labels_is_rejected(self):
        self.rows.append(copy.deepcopy(self.rows[0]))
        self.rows[-1]['labels']['probe_id'] = 'duplicate-with-different-name'
        with self.assertRaisesRegex(ValueError, 'Duplicate request'):
            catalog.validate(self.rows)

    def test_nucleo_variants_preserved_and_share_incident_identity(self):
        rows = [r for r in self.rows if r['labels']['service'] == 'edge-nucleotecnologico-collect']
        self.assertEqual(len(rows), 2)
        params = [parse_qs(urlsplit(r['targets'][0]).query) for r in rows]
        self.assertNotEqual(params[0]['cid'], params[1]['cid'])
        self.assertEqual({k:v for k,v in params[0].items() if k != 'cid'},
                         {k:v for k,v in params[1].items() if k != 'cid'})
        for key in ['service', 'alert_target', 'probe_type']:
            self.assertEqual(rows[0]['labels'][key], rows[1]['labels'][key])

    def test_internet_redirect_contracts_preserved(self):
        modules = {r['labels']['module'] for r in self.rows if r['labels']['service'] == 'internet'}
        self.assertEqual(modules, {'http_2xx', 'http_2xx_strict'})

    def test_svc01_has_one_root_get(self):
        rows = [r for r in self.rows if r['labels']['service'] == 'svc01']
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['targets'], ['https://infra-svc01.mailerblend.com/'])
        self.assertEqual(rows[0]['labels']['module'], 'http_2xx')

    def test_exact_discovery_file_excludes_remote_legacy_files(self):
        import yaml  # Existing inventory tooling already uses PyYAML.
        config = yaml.safe_load((ROOT/'services/infra-prom/config/prometheus.yml').read_text())
        job = next(j for j in config['scrape_configs'] if j['job_name'] == 'blackbox')
        self.assertEqual(job['file_sd_configs'], [{'files':['/etc/prometheus/targets/blackbox.json', '/etc/prometheus/targets/blackbox-journal.json']}])

    def test_previous_endpoint_and_module_coverage_is_preserved(self):
        expected = {
            ('infra-svc01.mailerblend.com', 'http_2xx'),
            ('infra-doc.mailerblend.com', 'http_2xx'),
            ('infra-pulpo.mailerblend.com', 'http_2xx'),
            ('infra-eva.mailerblend.com', 'http_2xx'),
            ('edge.mailerblend.com', 'http_collect_200'),
            ('edge.nucleotecnologico.es', 'http_collect_200'),
            ('www.google.com', 'http_2xx'), ('www.google.com', 'http_2xx_strict'),
            ('192.168.1.110:9090', 'http_2xx_strict'), ('192.168.1.110:9093', 'http_2xx_strict'),
        }
        actual = {(urlsplit(r['targets'][0]).netloc,r['labels']['module']) for r in self.rows}
        self.assertEqual(actual, expected)


if __name__ == '__main__':
    unittest.main()
