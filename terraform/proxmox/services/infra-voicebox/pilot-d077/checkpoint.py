"""Private, atomic acoustic-code checkpoints. No pickle, model or audio loading."""
import hashlib
import json
import os
import stat
import uuid
from pathlib import Path

import numpy as np

SCHEMA = "qwen-base-06b-checkpoint-v1"
MAX_FILE_BYTES = 16 * 1024 * 1024


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def private_file(path):
    p = Path(path)
    s = p.lstat()
    if not stat.S_ISREG(s.st_mode) or s.st_mode & 0o077 or s.st_uid != os.geteuid():
        raise ValueError("Checkpoint file must be regular, owned and private")
    if s.st_size > MAX_FILE_BYTES:
        raise ValueError("Checkpoint file exceeds size bound")
    return p


def validate_codes(codes, meta):
    if codes.dtype != np.dtype("int64") or codes.ndim != 2:
        raise ValueError("Codes must be int64 [time, quantizers]")
    if not 1 <= codes.shape[0] <= 8192 or codes.shape[1] != 16:
        raise ValueError("Unsupported Base0.6B acoustic-code dimensions")
    if np.any(codes < 0) or np.any(codes >= 2048):
        raise ValueError("Code outside installed decoder codebook")
    ref = meta["reference_frames"]
    if type(ref) is not int or not 0 < ref < codes.shape[0]:
        raise ValueError("Invalid reference/generated split")
    if meta["generated_frames"] != codes.shape[0] - ref:
        raise ValueError("Inconsistent generated-code length")
    if meta["sample_rate"] != 24000 or meta["decode_upsample_rate"] != 1920:
        raise ValueError("Unsupported tokenizer sampling configuration")
    if meta["trim_strategy"] != "official_ratio_floor_after_full_decode":
        raise ValueError("Unknown reference trim semantics")
    if meta["generation"]["eos_emitted"] is not True:
        raise ValueError("Checkpoint must represent a generation completed with EOS")
    if type(meta.get("synthetic")) is not bool:
        raise ValueError("Explicit real/synthetic checkpoint type required")
    if not meta["synthetic"]:
        for key in ["model", "backend", "codec", "reference_sha256", "reference_transcript_sha256", "text_sha256", "threads"]:
            if key not in meta:
                raise ValueError("Real checkpoint missing provenance: " + key)
        for key in ["reference_sha256", "reference_transcript_sha256", "text_sha256"]:
            digest = meta[key]
            if not isinstance(digest, str) or len(digest) != 64 or any(x not in "0123456789abcdef" for x in digest):
                raise ValueError("Invalid provenance digest")


def fsync_dir(path):
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def durable_write(path, data):
    with Path(path).open("xb") as f:
        os.chmod(path, 0o600)
        f.write(data)
        f.flush()
        os.fsync(f.fileno())


def save_checkpoint(target, codes, metadata):
    """Commit an entire directory with same-filesystem rename; never overwrite."""
    target = Path(target)
    if target.exists() or target.is_symlink():
        raise FileExistsError(target)
    codes = np.ascontiguousarray(codes)
    validate_codes(codes, metadata)
    lock = target.with_name(target.name + ".writer-lock")
    lock.mkdir(mode=0o700)  # Exclusive writer; interrupted locks require inspection.
    partial = target.with_name("." + target.name + "." + uuid.uuid4().hex + ".partial")
    try:
        partial.mkdir(mode=0o700)
        with (partial / "codes.npy").open("xb") as f:
            os.chmod(f.name, 0o600)
            np.save(f, codes, allow_pickle=False)
            f.flush()
            os.fsync(f.fileno())
        manifest = dict(metadata, schema=SCHEMA, codes={
            "file": "codes.npy", "dtype": "int64", "shape": list(codes.shape),
            "sha256": sha256(partial / "codes.npy"),
        })
        durable_write(partial / "manifest.json", json.dumps(manifest, sort_keys=True).encode())
        durable_write(partial / "COMMITTED.json", json.dumps({
            "schema": SCHEMA, "manifest_sha256": sha256(partial / "manifest.json")
        }).encode())
        fsync_dir(partial)
        load_checkpoint(partial)  # Validate readback before publication.
        if target.exists() or target.is_symlink():
            raise FileExistsError(target)
        os.rename(partial, target)
        fsync_dir(target.parent)
        return manifest
    finally:
        # Failed partials remain private for diagnosis; readers never accept them as final.
        lock.rmdir()


def load_checkpoint(target):
    p = Path(target)
    s = p.lstat()
    if not stat.S_ISDIR(s.st_mode) or s.st_mode & 0o077 or s.st_uid != os.geteuid():
        raise ValueError("Checkpoint directory must be owned and private")
    commit = json.loads(private_file(p / "COMMITTED.json").read_text())
    if commit["schema"] != SCHEMA or commit["manifest_sha256"] != sha256(private_file(p / "manifest.json")):
        raise ValueError("Manifest integrity failure")
    meta = json.loads((p / "manifest.json").read_text())
    if meta["schema"] != SCHEMA or meta["codes"]["file"] != "codes.npy":
        raise ValueError("Unsupported checkpoint schema/path")
    code_file = private_file(p / "codes.npy")
    if sha256(code_file) != meta["codes"]["sha256"]:
        raise ValueError("Acoustic-code integrity failure")
    with code_file.open("rb") as f:
        if np.lib.format.read_magic(f) != (1, 0):
            raise ValueError("Only NPYv1 checkpoints are supported")
        shape, fortran, dtype = np.lib.format.read_array_header_1_0(f)
        if dtype != np.dtype("int64") or len(shape) != 2 or not 1 <= shape[0] <= 8192 or shape[1] != 16 or fortran:
            raise ValueError("Invalid NPY header; refuse allocation")
        if code_file.stat().st_size != f.tell() + shape[0] * shape[1] * 8:
            raise ValueError("Truncated or trailing checkpoint payload")
    codes = np.load(code_file, allow_pickle=False)
    validate_codes(codes, meta)
    if list(codes.shape) != meta["codes"]["shape"] or str(codes.dtype) != meta["codes"]["dtype"]:
        raise ValueError("Manifest dimensions/dtype differ from payload")
    return codes, meta


def trim_reference(wav, meta):
    total = meta["reference_frames"] + meta["generated_frames"]
    if wav.ndim != 1 or wav.shape[0] != total * meta["decode_upsample_rate"]:
        raise ValueError("Decoder output length does not match acoustic codes")
    # Exact expression from qwen-tts0.1.1, including floating-point floor semantics.
    cut = int(meta["reference_frames"] / max(total, 1) * wav.shape[0])
    return wav[cut:], cut
