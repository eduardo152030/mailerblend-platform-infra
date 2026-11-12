"""Production adapter tests with a file-queue fixture; never loads models or emits audio."""
import asyncio
import importlib.util
import json
from pathlib import Path
import tempfile
import time
import unittest
import uuid

SOURCE = Path(__file__).resolve().parents[2] / "services/infra-voicebox/production-d077"


def module(name):
    spec = importlib.util.spec_from_file_location("d077_test_" + name, SOURCE / (name + ".py"))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


class Adapter(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="d077-adapter-")
        self.root = Path(self.temp.name)
        self.mod = module("isolated_backend"); self.mod.ROOT = self.root
        self.ident = uuid.uuid4(); self.mod.start_context(str(self.ident))
        self.mod.atomic(self.root / "agent-heartbeat.json", {"timestamp": time.time(), "ct": 627, "status": "healthy"})
        self.backend = self.mod.IsolatedQwenBackend()

    def tearDown(self):
        self.temp.cleanup()

    async def test_no_resident_model_or_unsupported_size(self):
        self.assertFalse(self.backend.is_loaded())
        self.assertIsNone(self.backend.model)
        await self.backend.load_model_async("0.6B")
        with self.assertRaises(ValueError):
            await self.backend.load_model_async("1.7B")

    async def test_stale_agent_fails_before_queueing(self):
        self.mod.atomic(self.root / "agent-heartbeat.json", {"timestamp": time.time() - 20, "ct": 627, "status": "healthy"})
        with self.assertRaises(RuntimeError):
            await self.backend.generate("hola", {"profile_id": self.mod.OWNER})
        self.assertFalse((self.root / self.ident.hex).exists())

    async def test_failure_preserves_checkpoint_and_does_not_retry(self):
        path = self.root / self.ident.hex
        async def fixture():
            while not (path / "state.json").exists():
                await asyncio.sleep(.01)
            (path / "checkpoint").mkdir()
            self.mod.atomic(path / "state.json", {"status": "failed", "error": "decoder fixture failure"})
        fake = asyncio.create_task(fixture())
        with self.assertRaisesRegex(RuntimeError, "decoder fixture failure"):
            await self.backend.generate("Texto intacto, sin dividir.", {"profile_id": self.mod.OWNER})
        await fake
        request = json.loads((path / "request.json").read_text())
        self.assertEqual(request["text"], "Texto intacto, sin dividir.")
        self.assertEqual(request["seed"], 42)
        self.assertTrue((path / "checkpoint").is_dir())
        with self.assertRaisesRegex(ValueError, "no se repite"):
            await self.backend.generate(request["text"], {"profile_id": self.mod.OWNER})

    async def test_cancellation_waits_for_terminal_state(self):
        path = self.root / self.ident.hex
        task = asyncio.create_task(self.backend.generate("hola", {"profile_id": self.mod.OWNER}))
        while not (path / "state.json").exists():
            await asyncio.sleep(.01)
        async def fixture():
            while not (path / "cancel.flag").exists():
                await asyncio.sleep(.01)
            self.mod.atomic(path / "state.json", {"status": "cancelled"})
        fake = asyncio.create_task(fixture()); task.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await task
        await fake
        self.assertEqual(json.loads((path / "state.json").read_text())["status"], "cancelled")

    async def test_wrong_owner_or_parameters_rejected(self):
        for kwargs in [{"voice_prompt": {"profile_id": "other"}}, {"seed": 1}, {"language": "en"}, {"instruct": "voice"}]:
            args = dict(text="hola", voice_prompt={"profile_id": self.mod.OWNER}); args.update(kwargs)
            with self.assertRaises(ValueError):
                await self.backend.generate(**args)


class Agent(unittest.TestCase):
    def test_invalid_job_does_not_execute_commands(self):
        agent = module("agent")
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory) / uuid.uuid4().hex; p.mkdir()
            r = {"profile_id": "wrong", "seed": 42, "language": "es", "model_size": "0.6B", "text": "hola"}
            (p / "request.json").write_text(json.dumps(r)); (p / "text.txt").write_text("hola")
            with self.assertRaises(ValueError):
                agent.request(p)


if __name__ == "__main__":
    unittest.main()
