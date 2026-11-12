"""Pinned installed-backend contract; imports do not load model weights."""
import hashlib
import importlib.metadata
import json
import os
import struct
from pathlib import Path

from checkpoint import sha256

MODEL_ID = "Qwen/Qwen3-TTS-12Hz-0.6B-Base"
SNAPSHOT = "5d83992436eae1d760afd27aff78a71d676296fc"
MODEL_PATH = Path("/cache/hub/models--Qwen--Qwen3-TTS-12Hz-0.6B-Base/snapshots") / SNAPSHOT
IMAGE = "sha256:bcc5c14f88064ffa76f813d788d183918b208deba45075d8118a2b07c60c248b"
REFERENCE_SHA = "7b388a917fb98bdf6b251454e04e7adc511faec42d21797f103ce539fc167dd4"
TRANSCRIPT_SHA = 'b959d04503d357bf2d5876bd541f3a4d81e730c8617fe4b1712167173ce141e9'
PINNED_SOURCES = {
    "inference/qwen3_tts_model.py": "e1da450732857c1f5fe3e36ebab85db2f6dc6a48caaff6973f463384e30275e4",
    "inference/qwen3_tts_tokenizer.py": "ac2d855022a1bd21d33ab7b267ec952eef71f81d3f8d969a306139ff1a929515",
    "core/tokenizer_12hz/modeling_qwen3_tts_tokenizer_v2.py": "844e8dd8c0182ef9c6463c874631c22ef3c5a4fd1899dd657016164cc5379628",
    "core/tokenizer_12hz/configuration_qwen3_tts_tokenizer_v2.py": "9e30c24394b00cb0366d7da3482b7436468acc1cd3da1a6fe614a1d34653a5e3",
}


def tensor_header(path):
    """Only safetensors header bytes, never tensor storage."""
    with Path(path).open("rb") as f:
        length = struct.unpack("<Q", f.read(8))[0]
        if not 0 < length < 1024 * 1024:
            raise ValueError("Invalid safetensors header size")
        raw = f.read(length)
    return json.loads(raw), hashlib.sha256(raw).hexdigest()


def codec_identity(path):
    path = Path(path)
    cfg = json.loads((path / "config.json").read_text())
    if (cfg["model_type"], cfg["output_sample_rate"], cfg["decode_upsample_rate"], cfg["decoder_config"]["num_quantizers"]) != (
        "qwen3_tts_tokenizer_12hz", 24000, 1920, 16
    ):
        raise ValueError("Unsupported codec configuration")
    header, digest = tensor_header(path / "model.safetensors")
    decoder = {k: v for k, v in header.items() if k.startswith("decoder.")}
    if len(decoder) != 271 or any(v["dtype"] != "F32" for v in decoder.values()):
        raise ValueError("Installed decoder tensor contract changed")
    return {"config_sha256": sha256(path / "config.json"),
            "weights_header_sha256": digest, "weights_size": (path / "model.safetensors").stat().st_size,
            "decoder_tensor_count": len(decoder),
            "decoder_weight_bytes": sum(v["data_offsets"][1] - v["data_offsets"][0] for v in decoder.values())}


def preflight():
    cache = Path(os.environ["NUMBA_CACHE_DIR"])
    if str(cache) != "/tmp/numba" or os.geteuid() != 999:
        raise ValueError("Unexpected cache/worker user")
    cache.mkdir(mode=0o700, parents=True, exist_ok=True)
    mount = next(line for line in Path("/proc/self/mountinfo").read_text().splitlines() if line.split()[4] == "/tmp")
    if mount.split(" - ")[1].split()[0] != "tmpfs":
        raise ValueError("Numba cache must use isolated tmpfs")
    marker = cache / "write-check"
    marker.write_bytes(b"d077"); marker.unlink()
    if os.statvfs(cache).f_bavail * os.statvfs(cache).f_frsize < 64 * 2**20:
        raise ValueError("Insufficient cache space")
    import numba, librosa, torch, soundfile, qwen_tts  # noqa: F401
    torch.set_num_threads(3)
    torch.set_num_interop_threads(1)
    if torch.get_default_dtype() != torch.float32:
        raise ValueError("FP32 required")
    root = Path(qwen_tts.__file__).parent
    sources = {name: sha256(root / name) for name in PINNED_SOURCES}
    if sources != PINNED_SOURCES:
        raise ValueError("Backend source differs from reviewed revision")
    versions = {name: importlib.metadata.version(name) for name in ["qwen-tts", "torch", "transformers", "accelerate", "safetensors", "numpy"]}
    if versions["qwen-tts"] != "0.1.1" or versions["torch"] != "2.8.0+cpu" or versions["transformers"] != "4.57.3":
        raise ValueError("Backend version changed")
    return {"versions": versions, "sources": sources, "image": IMAGE}


def decoder_classes():
    from qwen_tts.core.tokenizer_12hz.configuration_qwen3_tts_tokenizer_v2 import Qwen3TTSTokenizerV2DecoderConfig
    from qwen_tts.core.tokenizer_12hz.modeling_qwen3_tts_tokenizer_v2 import Qwen3TTSTokenizerV2Decoder
    return Qwen3TTSTokenizerV2DecoderConfig, Qwen3TTSTokenizerV2Decoder


def decoder_config(path):
    config_cls, _ = decoder_classes()
    cfg = config_cls(**json.loads((Path(path) / "config.json").read_text())["decoder_config"])
    cfg._attn_implementation = "sdpa"
    return cfg


def validate_decoder_layout(path):
    """Meta-device skeleton only: no real parameters, weights, forward or audio."""
    import torch
    _, decoder_cls = decoder_classes()
    with torch.device("meta"):
        decoder = decoder_cls(decoder_config(path))
    state = decoder.state_dict()
    header, _ = tensor_header(Path(path) / "model.safetensors")
    expected = {k.removeprefix("decoder."): v for k, v in header.items() if k.startswith("decoder.")}
    if set(state) != set(expected) or not all(list(state[k].shape) == v["shape"] for k, v in expected.items()):
        raise ValueError("Decoder state keys/shapes differ from reviewed checkpoint")
    if not all(t.is_meta for t in state.values()):
        raise ValueError("Static validation allocated actual model storage")
    return {"decoder_tensors": len(state), "all_tensors_meta": True, "weights_loaded": False, "forward_called": False}


def load_decoder_only(path):
    """Future real B: load only decoder.*; never construct Talker or encoder."""
    import torch
    from accelerate import init_empty_weights
    from safetensors import safe_open
    _, decoder_cls = decoder_classes()
    # Non-persistent rotary buffers stay on CPU; parameters start on meta.
    with init_empty_weights(include_buffers=False):
        decoder = decoder_cls(decoder_config(path))
    with safe_open(str(Path(path) / "model.safetensors"), framework="pt", device="cpu") as f:
        state = {k.removeprefix("decoder."): f.get_tensor(k) for k in f.keys() if k.startswith("decoder.")}
    decoder.load_state_dict(state, strict=True, assign=True)
    if any(t.is_meta or t.device.type != "cpu" or (t.is_floating_point() and t.dtype != torch.float32)
           for t in list(decoder.parameters()) + list(decoder.buffers())):
        raise ValueError("Decoder must be complete CPU FP32, including non-persistent buffers")
    decoder.eval()
    return decoder
