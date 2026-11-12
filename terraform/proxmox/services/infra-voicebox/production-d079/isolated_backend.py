"""Voicebox Qwen adapter. File queue only; no model or Docker socket in the app."""
import asyncio
import contextvars
import hashlib
import json
import os
from pathlib import Path
import time
import uuid

import soundfile as sf

OWNER = "1fd00418-2a79-4178-883f-af6c3f5e07ee"
REFERENCE = "8840f5e1-990b-463e-b94e-e72beef61917"
ROOT = Path("/qwen-jobs")
CONTEXT = contextvars.ContextVar("qwen_generation_id", default=None)


def start_context(ident):
    CONTEXT.set(ident)


def atomic(path, data):
    tmp = path.with_name(path.name + ".app-partial")
    with tmp.open("w") as f:
        os.chmod(tmp, 0o600); f.write(json.dumps(data)); f.flush(); os.fsync(f.fileno())
    os.replace(tmp, path)


def worker_health():
    value = json.loads((ROOT / "agent-heartbeat.json").read_text())
    if value["ct"] != 627 or value["status"] != "healthy" or not 0 <= time.time() - value["timestamp"] < 8:
        raise RuntimeError("Supervisor Qwen no disponible; no se inicia inferencia")
    return value


class IsolatedQwenBackend:
    device = "cpu"
    model_size = "0.6B"
    _current_model_size = "0.6B"
    model = None

    def is_loaded(self):
        # Accurate: no ML model is ever resident in Voicebox itself.
        return False

    def unload_model(self):
        return None

    def _get_model_path(self, size="0.6B"):
        if size != "0.6B":
            raise ValueError("Selecciona Qwen Base0.6B; otros tamaños no están habilitados")
        return "Qwen/Qwen3-TTS-12Hz-0.6B-Base"

    def _is_model_cached(self, size="0.6B"):
        if size != "0.6B":
            return False
        try:
            worker_health(); return True
        except Exception:
            return False

    async def load_model_async(self, size="0.6B"):
        self._get_model_path(size); worker_health()

    async def load_model(self, size="0.6B"):
        await self.load_model_async(size)

    async def create_voice_prompt(self, audio_path, reference_text, use_cache=True):
        expected = Path("/app/data/profiles") / OWNER / (REFERENCE + ".wav")
        from .d077_contract import REFERENCE_SHA, TRANSCRIPT_SHA
        if Path(audio_path).resolve() != expected.resolve() or hashlib.sha256(expected.read_bytes()).hexdigest() != REFERENCE_SHA:
            raise ValueError("Se requiere la referencia verificada de Eduardo")
        if hashlib.sha256(reference_text.strip().encode()).hexdigest() != TRANSCRIPT_SHA:
            raise ValueError("La transcripción no coincide con la referencia confirmada")
        return {"profile_id": OWNER}, False

    async def combine_voice_prompts(self, *args):
        raise ValueError("Usar exclusivamente la referencia confirmada de Eduardo")

    async def generate(self, text, voice_prompt, language="es", seed=None, instruct=None):
        if voice_prompt.get("profile_id") != OWNER or language != "es" or instruct or seed not in [None, 42]:
            raise ValueError("Clonación habilitada para Eduardo/es/semilla42, sin instrucciones adicionales")
        if not 1 <= len(text) <= 1200:
            raise ValueError("Qwen admite hasta1200caracteres por trabajo con límite900s")
        worker_health()
        parent = CONTEXT.get()
        if not parent:
            raise ValueError("Se requiere un trabajo persistente de Voicebox")
        ident = uuid.UUID(parent).hex
        path = ROOT / ident
        if path.exists():
            checkpoint = path / "checkpoint"
            if not checkpoint.exists():
                raise ValueError("Este intento ya falló y no tiene checkpoint ni códigos acústicos. "
                                 "Reintentarlo requiere una nueva inferencia explícita con otro intento, "
                                 "después de resolver la causa original; no se repite Talker automáticamente.")
            # No decoder submission occurs here. Integrity must be verified before recovery.
            raise ValueError("Existe una carpeta de checkpoint, pero su integridad no se ha verificado. "
                             "Conservar el intento y verificar códigos, EOS e identidad antes de recuperar Decoder B; "
                             "no se repite Talker automáticamente.")
        path.mkdir(mode=0o700)
        (path / "text.txt").write_text(text); (path / "text.txt").chmod(0o600)
        atomic(path / "request.json", {"profile_id": OWNER, "text": text, "seed": 42, "language": "es", "model_size": "0.6B"})
        atomic(path / "state.json", {"status": "queued", "created_at": time.time()})
        deadline = time.monotonic() + 930
        try:
            while time.monotonic() < deadline:
                state = json.loads((path / "state.json").read_text())
                if state["status"] == "completed":
                    wav = path / "decoded-300.wav"
                    if hashlib.sha256(wav.read_bytes()).hexdigest() != state["wav_sha256"]:
                        raise ValueError("WAV checksum incorrecto")
                    return sf.read(wav, dtype="float32")
                if state["status"] in ["failed", "cancelled"]:
                    raise RuntimeError(state.get("error", state["status"]))
                worker_health()
                await asyncio.sleep(0.4)
            raise TimeoutError("Qwen excedió el plazo; checkpoint conservado")
        except BaseException:
            (path / "cancel.flag").touch(mode=0o600)
            async def reap():
                for _ in range(100):
                    state = json.loads((path / "state.json").read_text())
                    if state["status"] in ["completed", "failed", "cancelled"]:
                        return
                    await asyncio.sleep(0.3)
                raise RuntimeError("Cancelación pendiente: no iniciar otro modelo")
            await asyncio.shield(reap())
            raise
