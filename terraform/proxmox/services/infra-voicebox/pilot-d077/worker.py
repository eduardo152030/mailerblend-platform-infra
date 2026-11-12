"""One isolated stage per invocation. Real stages require explicit --real flag."""
import argparse
import hashlib
import json
import os
import resource
import signal
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

from checkpoint import durable_write, fsync_dir, load_checkpoint, save_checkpoint, sha256, trim_reference
import runtime

os.umask(0o077)
START = time.monotonic()
JOB = Path("/job")


def event(stage, **fields):
    line = dict(elapsed=time.monotonic() - START, stage=stage, **fields)
    with (JOB / "events.jsonl").open("a") as f:
        f.write(json.dumps(line) + "\n")
        f.flush()


def persistent_job():
    lines = Path("/proc/self/mountinfo").read_text().splitlines()
    mount = next(line for line in lines if line.split()[4] == "/job")
    if mount.split(" - ")[1].split()[0] in ["tmpfs", "ramfs", "overlay"]:
        raise ValueError("Job must be a persistent bind mount, not temporary/rootfs storage")
    if JOB.stat().st_uid != os.geteuid() or JOB.stat().st_mode & 0o077:
        raise ValueError("Job must be private and owned by worker")


def synthetic_metadata():
    return {"synthetic": True, "reference_frames": 3, "generated_frames": 9,
            "sample_rate": 24000, "decode_upsample_rate": 1920,
            "trim_strategy": "official_ratio_floor_after_full_decode",
            "generation": {"eos_emitted": True, "seed": 42}}


class CheckpointComplete(BaseException):
    """Intentionally stop official clone API at the decoder boundary."""


def talker(backend):
    import torch
    from qwen_tts import Qwen3TTSModel
    torch.manual_seed(42)
    ref = Path("/private/reference.wav")
    transcript = Path("/private/transcript.txt").read_text().strip()
    if sha256(ref) != runtime.REFERENCE_SHA or len(transcript) != 425 or hashlib.sha256(transcript.encode()).hexdigest() != runtime.TRANSCRIPT_SHA:
        raise ValueError("Reference/transcript differ from owner-confirmed data")
    text = (JOB / "text.txt").read_text().strip()
    if not text:
        raise ValueError("Missing generation text")
    checkpoint = JOB / "checkpoint"
    if checkpoint.exists():
        raise FileExistsError("Completed checkpoint exists: use decoder only")
    codec = runtime.MODEL_PATH / "speech_tokenizer"
    identity = runtime.codec_identity(codec)
    event("load_talker_start")
    model = Qwen3TTSModel.from_pretrained(str(runtime.MODEL_PATH), device_map="cpu",
                                        dtype=torch.float32, attn_implementation="sdpa", local_files_only=True)
    model.model.eval()
    if any(p.dtype != torch.float32 for obj in [model.model, model.model.speech_tokenizer.model]
           for p in obj.parameters() if p.is_floating_point()):
        raise ValueError("Talker/codec precision differs from FP32")
    event("load_talker_end")
    with torch.inference_mode():
        prompt = model.create_voice_clone_prompt(ref_audio=str(ref), ref_text=transcript, x_vector_only_mode=False)
    if len(prompt) != 1 or not prompt[0].icl_mode or prompt[0].ref_code is None:
        raise ValueError("Full audio-and-text ICL reference required")
    ref_codes = prompt[0].ref_code.detach().cpu().numpy()
    event("reference_ready", frames=int(ref_codes.shape[0]))
    gen = {}
    old_generate = model.model.talker.generate

    def generate(*args, **kwargs):
        if kwargs["max_new_tokens"] != 1024:
            raise ValueError("Unexpected token cap")
        effective = {}
        for key, value in kwargs.items():
            try:
                json.dumps(value)
                effective[key] = value
            except (TypeError, ValueError):
                pass  # Embeddings/reference tensors are represented by the saved acoustic codes.
        t = time.monotonic()
        result = old_generate(*args, **kwargs)
        seq = result.sequences
        gen.update(eos_emitted=int(seq[0, -1]) == int(kwargs["eos_token_id"]),
                   sequence_tokens=int(seq.shape[-1]), eos_token_id=int(kwargs["eos_token_id"]),
                   seconds=time.monotonic() - t, seed=42, max_new_tokens=1024, language="Spanish",
                   effective_generate_kwargs=effective,
                   generation_config=model.model.talker.generation_config.to_dict(),
                   snapshot_generation_config=json.loads((runtime.MODEL_PATH / "generation_config.json").read_text()))
        event("talker_end", **gen)
        return result

    model.model.talker.generate = generate

    def persist_instead_of_decode(encoded):
        if not gen.get("eos_emitted") or not isinstance(encoded, list) or len(encoded) != 1:
            raise ValueError("No complete single-sample EOS generation")
        codes = encoded[0]["audio_codes"].detach().cpu().numpy()
        nref = int(ref_codes.shape[0])
        if not np.array_equal(codes[:nref], ref_codes):
            raise ValueError("Official reference concatenation changed")
        meta = {"synthetic": False, "reference_frames": nref,
                "generated_frames": int(codes.shape[0]) - nref, "sample_rate": 24000,
                "decode_upsample_rate": 1920, "trim_strategy": "official_ratio_floor_after_full_decode",
                "model": {"id": runtime.MODEL_ID, "snapshot": runtime.SNAPSHOT, "precision": "float32", "attention": "sdpa"},
                "backend": backend, "codec": identity, "generation": gen,
                "reference_sha256": runtime.REFERENCE_SHA,
                "reference_transcript_sha256": hashlib.sha256(transcript.encode()).hexdigest(),
                "reference_transcript_characters": len(transcript),
                "text_sha256": hashlib.sha256(text.encode()).hexdigest(), "threads": {"intraop": 3, "interop": 1}}
        save_checkpoint(checkpoint, codes, meta)
        load_checkpoint(checkpoint)
        event("checkpoint_committed", manifest_sha256=sha256(checkpoint / "manifest.json"), shape=list(codes.shape))
        raise CheckpointComplete()

    # Preserve official prompt/token/cat logic; the actual decoder is never called in A.
    model.model.speech_tokenizer.decode = persist_instead_of_decode
    try:
        with torch.inference_mode():
            model.generate_voice_clone(text=text, language="Spanish", voice_clone_prompt=prompt, max_new_tokens=1024)
    except CheckpointComplete:
        return {"checkpoint_verified": True, "decoder_called": False, "eos_emitted": True}
    raise RuntimeError("Official API unexpectedly returned without checkpoint boundary")


def decode(backend, chunk):
    import torch
    import soundfile as sf
    # No /cache, reference audio or Talker weights are mounted in B.
    codes, meta = load_checkpoint("/checkpoint")
    if meta.get("synthetic") is not False:
        raise ValueError("Synthetic checkpoint cannot be used for real decoding")
    expected_model = {"id": runtime.MODEL_ID, "snapshot": runtime.SNAPSHOT, "precision": "float32", "attention": "sdpa"}
    if meta["model"] != expected_model or meta["backend"] != backend or meta["codec"] != runtime.codec_identity("/codec"):
        raise ValueError("Checkpoint/model/backend identity mismatch")
    output = JOB / ("decoded-" + str(chunk) + ".wav")
    if output.exists():
        raise FileExistsError(output)
    event("load_decoder_only_start", chunk_steps=chunk, left_context_steps=25)
    decoder = runtime.load_decoder_only("/codec")
    if hasattr(decoder, "talker") or hasattr(decoder, "encoder"):
        raise ValueError("Decoder stage must not contain Talker/encoder")
    event("load_decoder_only_end")
    with torch.inference_mode():
        tensor = torch.from_numpy(codes).unsqueeze(0).transpose(1, 2)
        wav = decoder.chunked_decode(tensor, chunk_size=chunk, left_context_size=25).squeeze(0).squeeze(0)
        wav = wav[:codes.shape[0] * meta["decode_upsample_rate"]].to(torch.float32).cpu().numpy()
    event("decode_end", complete_samples=int(wav.shape[0]))
    wav, cut = trim_reference(wav, meta)
    if not wav.size or not np.isfinite(wav).all() or float(np.max(np.abs(wav))) == 0:
        raise ValueError("Empty, non-finite or silent output")
    temp = output.with_suffix(".partial.wav")
    if temp.exists():
        raise FileExistsError(temp)
    sf.write(temp, wav, meta["sample_rate"], subtype="PCM_16")
    info = sf.info(temp)
    if info.channels != 1 or info.samplerate != 24000 or info.frames != len(wav) or info.subtype != "PCM_16":
        raise ValueError("WAV validation failed")
    with temp.open("rb") as f:
        os.fsync(f.fileno())
    os.rename(temp, output); fsync_dir(JOB)
    return {"wav_sha256": sha256(output), "sample_rate": info.samplerate, "seconds": info.duration,
            "frames": info.frames, "reference_cut_samples": cut, "chunk_steps": chunk,
            "left_context_steps": 25, "talker_loaded": False, "encoder_loaded": False}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["talker", "decoder", "verify", "imports", "synthetic-write", "synthetic-read", "hold"])
    ap.add_argument("--real", action="store_true")
    ap.add_argument("--chunk", type=int, choices=[300, 120], default=300)
    args = ap.parse_args()
    persistent_job()
    if args.stage in ["talker", "decoder"] and not args.real:
        raise ValueError("Real inference requires explicit --real")
    if args.stage == "synthetic-write":
        save_checkpoint(JOB / "checkpoint", np.arange(12 * 16, dtype=np.int64).reshape(12, 16), synthetic_metadata())
        return {"synthetic_checkpoint_written": True, "model_loaded": False, "audio_generated": False}
    if args.stage == "synthetic-read":
        codes, meta = load_checkpoint("/checkpoint")
        if not meta["synthetic"] or not np.array_equal(codes, np.arange(192, dtype=np.int64).reshape(12, 16)):
            raise ValueError("Synthetic recovery mismatch")
        return {"synthetic_recovered_in_new_process": True, "model_loaded": False, "audio_generated": False}
    if args.stage == "verify":
        codes, meta = load_checkpoint("/checkpoint")
        if meta.get("synthetic") is not False:
            raise ValueError("Recovery verification requires a real completed checkpoint")
        if meta["model"]["id"] != runtime.MODEL_ID or meta["model"]["snapshot"] != runtime.SNAPSHOT:
            raise ValueError("Unexpected model identity")
        return {"checkpoint_verified": True, "manifest_sha256": sha256(Path("/checkpoint/manifest.json")),
                "shape": list(codes.shape), "model_loaded": False, "audio_generated": False}
    if args.stage == "hold":
        subprocess.Popen([sys.executable, "-c", "import time; time.sleep(120)"])
        event("synthetic_parent_and_child_waiting")
        time.sleep(120)
        raise RuntimeError("Cancellation test failed to stop process")
    backend = runtime.preflight()
    if args.stage == "imports":
        from validation import chunk_contract, decoder_loader_contract
        return {"imports": backend, "codec": runtime.codec_identity("/codec"),
                "layout": runtime.validate_decoder_layout("/codec"), "chunks": chunk_contract(),
                "loader_synthetic": decoder_loader_contract(), "audio_generated": False}
    if args.stage == "talker":
        return talker(backend)
    return decode(backend, args.chunk)


if __name__ == "__main__":
    def timeout(signum, frame):
        raise TimeoutError("Worker wall timeout")
    signal.signal(signal.SIGALRM, timeout)
    signal.alarm(int(os.environ.get("PILOT_TIMEOUT_SECONDS", "60")))
    result = {}
    try:
        result = main()
        result["success"] = True
    except BaseException as exc:
        result = {"success": False, "error_type": type(exc).__name__, "error": str(exc)[:400]}
    finally:
        result.update(elapsed_seconds=time.monotonic() - START,
                      rss_hwm_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024)
        # Separate result file for each container/stage; checkpoint is never changed here.
        destination = JOB / (os.environ.get("RESULT_NAME", "result") + ".json")
        durable_write(destination, json.dumps(result, sort_keys=True).encode())
        signal.alarm(0)
    print(json.dumps(result), flush=True)
    raise SystemExit(0 if result["success"] else 1)
