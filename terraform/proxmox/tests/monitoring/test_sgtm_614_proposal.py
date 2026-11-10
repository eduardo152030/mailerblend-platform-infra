import json,unittest
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'services/infra-nucleoedge/proposals/d043'
class SgtmProposalTests(unittest.TestCase):
 def test_application_overlay_changes_only_healthchecks_without_shell_or_curl(self):
  c=yaml.safe_load((P/'healthcheck.native.yml').read_text());self.assertEqual(set(c['services']),{'sgtm','sgtm_preview'})
  for service in c['services'].values():
   self.assertEqual(set(service),{'healthcheck'});self.assertEqual(service['healthcheck']['test'],['CMD','/nodejs/bin/node','/app/health_checker_bin.js'])
 def test_deferred_probe_never_sends_ga4_payload_or_accepts_error_status(self):
  original=json.loads((ROOT/'services/infra-prom/config/targets/blackbox.json').read_text());candidate=json.loads((P/'targets.candidate.json').read_text());self.assertEqual(len(candidate),len(original)+2)
  untouched=original
  self.assertTrue(all(r in candidate for r in untouched))
  probes=[r for r in candidate if r['labels'].get('probe_type')=='sgtm_health'];self.assertEqual({r['targets'][0] for r in probes},{'https://edge.nucleotecnologico.es/healthz','https://edge.nucleotecnologico.es/preview/healthz'})
  module=yaml.safe_load((P/'blackbox.candidate.yml').read_text())['modules']['http_sgtm_health']['http'];self.assertEqual(module['method'],'GET');self.assertEqual(module['valid_status_codes'],[200]);self.assertFalse(module['tls_config']['insecure_skip_verify']);self.assertNotIn('headers',module)
 def test_deferred_alert_is_runtime_health_and_not_a_collection_delivery_claim(self):
  c=yaml.safe_load((P/'sgtm-health.rules.yml').read_text());r=c['groups'][0]['rules'][0]
  self.assertEqual(r['alert'],'SgtmRuntimeUnhealthy');self.assertIn('sgtm_health',r['expr']);self.assertIn('No equivale',r['annotations']['description'])
if __name__=='__main__':unittest.main()
