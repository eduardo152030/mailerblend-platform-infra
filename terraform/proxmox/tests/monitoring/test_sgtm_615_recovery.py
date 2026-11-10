"""Run the D044 regression contract against the CT615 profile without remote access."""
import importlib.util,unittest,tempfile,json
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
base=load('sgtm614_contract',ROOT/'tests/monitoring/test_sgtm_614_recovery.py')
class CT615Contract(base.RecoveryTests):
 def setUp(self):
  original=base.m
  base.m=load('sgtm615_recovery',ROOT/'scripts/recover-sgtm-614.py');base.m.configure_target(615)
  self.addCleanup(setattr,base,'m',original)
 def test_exact_scoped_profile(self):
  m=base.m
  self.assertEqual(m.CT,615);self.assertEqual(str(m.BASE),'/opt/infra-mailerblend-edge/docker-compose.yml')
  self.assertEqual(m.NAMES,{'sgtm_preview':'mailerblend-sgtm-preview','sgtm':'mailerblend-sgtm-serving'})
  self.assertEqual(m.PORTS,{'sgtm_preview':18092,'sgtm':18091});self.assertEqual(m.EXPECTED_PROBES,1)
  self.assertEqual(m.PUBLIC_BASE,'https://edge.mailerblend.com');self.assertEqual(m.PREVIEW_HEALTH_PATH,'/gtm/healthz');self.assertEqual(m.PREVIEW_ROUTING_HEADERS,{'X-Gtm-Server-Preview':'1'})
 def test_compose_recreates_only_requested_service_without_pull(self):
  m=base.m
  with tempfile.TemporaryDirectory() as d,patch.object(m,'cmd',return_value='') as call:
   m.compose(Path(d),['sgtm_preview'],force=True)
   args=call.call_args.args[0]
   self.assertEqual(args[-1],'sgtm_preview');self.assertIn('--no-deps',args);self.assertIn('--force-recreate',args)
   self.assertEqual(args[args.index('--pull')+1],'never');self.assertEqual(args[args.index('--project-name')+1],'infra-mailerblend-edge')
 def test_unapproved_target_rejected(self):
  with self.assertRaises(AssertionError):base.m.configure_target(616)
if __name__=='__main__':unittest.main()
