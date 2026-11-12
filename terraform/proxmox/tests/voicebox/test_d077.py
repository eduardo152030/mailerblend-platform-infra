"""D077 contracts: integrity, atomic publication, recovery, resource boundaries."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

SOURCE = Path(__file__).resolve().parents[2] / "services/infra-voicebox/pilot-d077"
sys.path.insert(0, str(SOURCE))
import checkpoint as cp
from guards import GIB, MIB, stop_reason


def metadata():
    return {"synthetic": True, "reference_frames": 3, "generated_frames": 9,
            "sample_rate": 24000, "decode_upsample_rate": 1920,
            "trim_strategy": "official_ratio_floor_after_full_decode",
            "generation": {"eos_emitted": True}}


class Checkpoints(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="d077-synthetic-")
        self.root = Path(self.temp.name)
        self.target = self.root / "checkpoint"
        self.codes = np.arange(192, dtype=np.int64).reshape(12, 16)

    def tearDown(self):
        self.temp.cleanup()

    def save(self):
        return cp.save_checkpoint(self.target, self.codes, metadata())

    def test_new_process_recovers_exact_checkpoint_and_trim(self):
        self.save()
        code = "import sys;sys.path.insert(0,sys.argv[1]);from checkpoint import load_checkpoint;import json;c,m=load_checkpoint(sys.argv[2]);print(json.dumps({'sum':int(c.sum()),'ref':m['reference_frames'],'dtype':str(c.dtype)}))"
        result = subprocess.check_output([sys.executable, "-c", code, str(SOURCE), str(self.target)], text=True)
        self.assertEqual(json.loads(result), {"sum": int(self.codes.sum()), "ref": 3, "dtype": "int64"})
        _, meta = cp.load_checkpoint(self.target)
        markers = np.arange(12 * 1920)
        trimmed, cut = cp.trim_reference(markers, meta)
        self.assertEqual(cut, int(3 / 12 * len(markers)))
        self.assertTrue(np.array_equal(trimmed, markers[cut:]))

    def test_payload_corruption_is_rejected(self):
        self.save()
        with (self.target / "codes.npy").open("r+b") as f:
            f.seek(-1, 2); f.write(b"X")
        with self.assertRaisesRegex(ValueError, "integrity"):
            cp.load_checkpoint(self.target)

    def test_manifest_corruption_is_rejected(self):
        self.save()
        (self.target / "manifest.json").write_text("{}")
        with self.assertRaisesRegex(ValueError, "integrity"):
            cp.load_checkpoint(self.target)

    def test_interrupted_write_is_not_published(self):
        with patch.object(cp, "durable_write", side_effect=OSError("simulated disk failure")):
            with self.assertRaises(OSError):
                self.save()
        self.assertFalse(self.target.exists())
        self.assertEqual(len(list(self.root.glob("*.partial"))), 1)
        with self.assertRaises(FileNotFoundError):
            cp.load_checkpoint(self.target)

    def test_completed_checkpoint_is_never_overwritten(self):
        self.save(); digest = cp.sha256(self.target / "codes.npy")
        with self.assertRaises(FileExistsError):
            self.save()
        self.assertEqual(cp.sha256(self.target / "codes.npy"), digest)

    def test_private_permissions_required(self):
        self.save(); os.chmod(self.target / "codes.npy", 0o644)
        with self.assertRaisesRegex(ValueError, "private"):
            cp.load_checkpoint(self.target)

    def test_symlink_payload_is_rejected(self):
        self.save(); original = self.target / "codes.npy"; saved = self.root / "saved.npy"
        original.rename(saved); original.symlink_to(saved)
        with self.assertRaisesRegex(ValueError, "regular"):
            cp.load_checkpoint(self.target)

    def test_dimension_dtype_range_reference_and_eos_contracts(self):
        bad = [self.codes.astype("int32"), self.codes.reshape(24, 8), self.codes * -1, self.codes + 2048]
        for codes in bad:
            with self.subTest(shape=codes.shape, dtype=codes.dtype):
                with self.assertRaises(ValueError):
                    cp.validate_codes(codes, metadata())
        for key, value in [("reference_frames", 12), ("generated_frames", 1), ("sample_rate", 48000), ("decode_upsample_rate", 1)]:
            meta = metadata(); meta[key] = value
            with self.subTest(key=key):
                with self.assertRaises(ValueError):
                    cp.validate_codes(self.codes, meta)
        meta = metadata(); meta["generation"]["eos_emitted"] = False
        with self.assertRaises(ValueError):
            cp.validate_codes(self.codes, meta)

    def test_unknown_writer_lock_preserved(self):
        lock = self.root / "checkpoint.writer-lock"; lock.mkdir()
        with self.assertRaises(FileExistsError):
            self.save()
        self.assertTrue(lock.exists())

    def test_real_checkpoint_requires_provenance(self):
        meta = metadata(); meta["synthetic"] = False
        with self.assertRaisesRegex(ValueError, "missing provenance"):
            cp.validate_codes(self.codes, meta)

    def test_trim_rejects_wrong_decoder_length(self):
        with self.assertRaises(ValueError):
            cp.trim_reference(np.arange(100), metadata())


class Safety(unittest.TestCase):
    def setUp(self):
        self.base = {"ct_current": 4 * GIB, "ct_swap": 0, "host_available": 16 * GIB,
                     "host_oom": 0, "ct_events": {"oom": 0, "oom_kill": 0},
                     "ct_psi_full_avg10": 0, "host_psi_full_avg10": 12}

    def test_all_resource_boundaries_stop(self):
        cases = [("ct_current", 14 * GIB, "CT_MEMORY"), ("worker_current", 8.2 * GIB, "WORKER_MEMORY"),
                 ("rss_bytes", 8.2 * GIB, "WORKER_MEMORY"), ("ct_swap", 128 * MIB, "GROWTH"),
                 ("ct_swap", 1920 * MIB, "1920"), ("host_available", 4 * GIB - 1, "HOST_AVAILABLE"),
                 ("host_oom", 1, "OOM")]
        for key, value, expected in cases:
            row = dict(self.base, **{key: value})
            with self.subTest(key=key, value=value):
                reason, _ = stop_reason(row, self.base, 0, None)
                self.assertIn(expected, reason)

    def test_psi_requires_ten_continuous_seconds_and_resets(self):
        row = dict(self.base, ct_psi_full_avg10=5)
        self.assertEqual(stop_reason(row, self.base, 0, None), (None, 0))
        self.assertIsNone(stop_reason(row, self.base, 9.9, 0)[0])
        self.assertEqual(stop_reason(row, self.base, 10, 0)[0], "PSI_SUSTAINED_10_SECONDS")
        self.assertEqual(stop_reason(self.base, self.base, 9, 0), (None, None))

    def test_no_oom_is_silently_accepted(self):
        for target in ["ct_events", "worker_events"]:
            row = copy.deepcopy(self.base); row[target] = {"oom": 1, "oom_kill": 0}
            self.assertEqual(stop_reason(row, self.base, 0, None)[0], "NEW_OOM")

    def test_global_psi_not_equated_to_physical_exhaustion(self):
        row = dict(self.base, host_psi_full_avg10=25)
        self.assertEqual(stop_reason(row, self.base, 20, 0), (None, None))
        row["host_available"] = 5 * GIB
        self.assertEqual(stop_reason(row, self.base, 10, 0)[0], "PSI_SUSTAINED_10_SECONDS")

    def test_decoder_plan_has_no_talker_or_reference_mount_and_defaults_to300(self):
        raw = subprocess.check_output([sys.executable, str(SOURCE / "supervise.py"), "decoder", "--job", "future01", "--attempt", "01", "--real"], text=True)
        plan = json.loads(raw); self.assertTrue(plan["plan_only"])
        cmd = plan["command"]
        self.assertEqual(cmd[cmd.index("--memory") + 1], "9g")
        self.assertEqual(cmd[cmd.index("--memory-swap") + 1], "9g")
        self.assertEqual(cmd[cmd.index("--chunk") + 1], "300")
        mounts = [cmd[i + 1] for i, item in enumerate(cmd) if item == "-v"]
        self.assertFalse(any(m.endswith(":/cache:ro") or m.endswith(":/private:ro") for m in mounts))
        self.assertTrue(any(m.endswith(":/checkpoint:ro") for m in mounts))
        self.assertTrue(any(m.endswith(":/job/checkpoint:ro") for m in mounts))
        self.assertTrue(any(m.endswith(":/codec/config.json:ro") for m in mounts))
        self.assertTrue(any(m.endswith(":/codec/model.safetensors:ro") for m in mounts))

    def test_trial_defaults_to_plan_and_does_not_start_processes(self):
        plan = json.loads(subprocess.check_output([sys.executable, str(SOURCE / "trial.py"), "--job", "future01"], text=True))
        self.assertTrue(plan["plan_only"])
        self.assertEqual(plan["total_budget_seconds"], 900)
        self.assertEqual(plan["first_decoder_chunk"], 300)
        self.assertFalse(plan["automatic_retry"])
        self.assertFalse(plan["automatic_chunk120"])


if __name__ == "__main__":
    unittest.main()
