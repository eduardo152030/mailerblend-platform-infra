"""No models, network, audio, production writes or cache manipulation."""
import importlib.util
from pathlib import Path
import sys
import unittest

path=Path(__file__).resolve().parents[2]/'services/infra-voicebox/proposals/d078/recovery_policy.py'
spec=importlib.util.spec_from_file_location('d078_recovery',path)
m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)

class RecoveryPolicy(unittest.TestCase):
    def classify(self,**kw):
        args=dict(terminal=True,processes_stopped=True,checkpoint='absent',same_identity=True,eos=False);args.update(kw)
        r=m.classify(**args);self.assertFalse(r.allow_talker_automatically);self.assertTrue(r.preserve_original);return r
    def test_absent_is_explicit_new_attempt_not_decoder(self):
        self.assertEqual(self.classify().action,'offer_new_attempt_explicitly')
    def test_valid_matching_EOS_can_offer_decoder(self):
        self.assertEqual(self.classify(checkpoint='valid',eos=True).action,'offer_decoder_only')
    def test_no_EOS_or_wrong_identity_cannot_resume(self):
        self.assertEqual(self.classify(checkpoint='valid',eos=False).action,'review_identity_or_EOS')
        self.assertEqual(self.classify(checkpoint='valid',eos=True,same_identity=False).action,'review_identity_or_EOS')
    def test_partial_or_invalid_retained(self):
        for state in ['partial','invalid']:
            self.assertEqual(self.classify(checkpoint=state).action,'preserve_and_review')
    def test_active_process_blocks_all_recovery(self):
        self.assertEqual(self.classify(processes_stopped=False).action,'wait_or_cancel')
        self.assertEqual(self.classify(terminal=False).action,'wait_or_cancel')
    def test_unknown_checkpoint_status_fails_closed(self):
        with self.assertRaises(ValueError):self.classify(checkpoint='exists_unverified')
