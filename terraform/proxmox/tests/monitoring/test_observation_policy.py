import importlib.util,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('policy',ROOT/'scripts/rollout-observation-policy.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class ObservationTests(unittest.TestCase):
 def good(self):return {k:True for k in m.REQUIRED}
 def test_conventional_batches_are_three_minutes_not_p0_or_r1(self):
  for b in ['R2','R3','R4','R5']:self.assertEqual(m.policy(b)['seconds'],180)
  for b in ['P0','R1','R6','R7']:self.assertEqual(m.policy(b)['seconds'],600)
 def test_seven_samples_and_180_seconds_both_required(self):
  self.assertFalse(m.assess([self.good()]*6,'R2',180)['initial_window_passed'])
  self.assertFalse(m.assess([self.good()]*7,'R2',179)['initial_window_passed'])
  r=m.assess([self.good()]*7,'R2',180);self.assertTrue(r['initial_window_passed']);self.assertFalse(r['alert_for_runtime_firing_validated']);self.assertTrue(r['continuous_watch_still_required'])
 def test_any_anomaly_halts_and_requires_extended_observation(self):
  samples=[self.good() for _ in range(7)];samples[3]['no_new_oom']=False;r=m.assess(samples,'R2',180)
  self.assertTrue(r['halt_advance']);self.assertFalse(r['initial_window_passed']);self.assertEqual(r['extended_observation_min_seconds'],600)
 def test_ten_minute_batch_cannot_pass_at_three_minutes(self):
  self.assertFalse(m.assess([self.good()]*7,'R6',180)['initial_window_passed'])
if __name__=='__main__':unittest.main()
