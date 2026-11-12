"""D079 admission with D080 resource-policy update; no models or production actions."""
from pathlib import Path
import sys,unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'services/infra-voicebox/pilot-d077'))
from guards import predictive_preflight,GIB
class Predictive(unittest.TestCase):
 def test_d077_baseline_passes(self):self.assertTrue(predictive_preflight({'ct_current':int(3.896*GIB)})['passed'])
 def test_d078_baselines_now_pass_with_d080_ram(self):
  for size in [5.299,5.445]:self.assertTrue(predictive_preflight({'ct_current':int(size*GIB)})['passed'])
 def test_boundary_conservative(self):
  self.assertTrue(predictive_preflight({'ct_current':int(9*GIB)})['passed'])
  self.assertFalse(predictive_preflight({'ct_current':int(9*GIB)+1})['passed'])
 def test_cache_is_not_discounted(self):self.assertFalse(predictive_preflight({'ct_current':int(9.3*GIB),'file':int(8.7*GIB)})['passed'])
 def test_projection_and_d080_guard(self):
  p=predictive_preflight({'ct_current':int(4.3*GIB)});self.assertEqual(p['guard_bytes'],int(14*GIB));self.assertEqual(p['projected_with_margin_bytes'],int(4.3*GIB)+5*GIB)
if __name__=='__main__':unittest.main()
