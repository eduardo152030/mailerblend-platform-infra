"""PVE-only file queue supervisor. Fixed CT627, no network listener or model loading."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import time

from qwen_language_policy import (validate_request, WORKER_PROTOCOL, EXPECTED_WORKER_SHA256,
                                  policy_fingerprint)

CT_ROOT = "/srv/voicebox/qwen-worker"
CODE = Path("/opt/voicebox-qwen-627")
OWNER = "1fd00418-2a79-4178-883f-af6c3f5e07ee"
STOP = False
CHILD = None


def ct(*args):
    return subprocess.check_output(["pct", "exec", "627", "--", *args], text=True, timeout=20)


def root():
    pid = subprocess.check_output(["lxc-info", "-n", "627", "-pH"], text=True, timeout=5).strip()
    if not pid.isdigit():
        raise RuntimeError("CT627 not running")
    base = Path("/proc", pid, "root")
    if (base / "etc/hostname").read_text().strip() != "infra-voicebox":
        raise RuntimeError("Wrong CT identity")
    return base / CT_ROOT.lstrip("/") / "jobs"


def read(path, max_bytes=1024 * 1024):
    path = Path(path)
    if path.is_symlink() or not path.is_file() or path.stat().st_size > max_bytes:
        raise ValueError("Invalid queue file")
    return json.loads(path.read_text())


def write(path, data):
    """Use mapped CT UID/GID from directory, not unmapped host UID999."""
    path = Path(path)
    owner = path.parent.stat()
    tmp = path.with_name(path.name + ".agent-partial")
    with tmp.open("w") as f:
        os.chmod(tmp, 0o600); os.chown(tmp, owner.st_uid, owner.st_gid)
        f.write(json.dumps(data)); f.flush(); os.fsync(f.fileno())
    os.replace(tmp, path)


def cleanup_owned():
    ids = ct("docker", "ps", "-aq", "--no-trunc", "--filter", "label=d077.root=" + CT_ROOT).split()
    for ident in ids:
        if not re.fullmatch(r"[a-f0-9]{64}", ident):
            raise RuntimeError("Invalid owned container ID")
        state = json.loads(ct("docker", "inspect", "-f", "{{json .State}}", ident))
        if state["Running"]:
            ct("docker", "kill", ident)
        ct("docker", "stop", "--time", "1", ident)
        state = json.loads(ct("docker", "inspect", "-f", "{{json .State}}", ident))
        if state["Running"] or state["Pid"]:
            raise RuntimeError("Owned inference remains active")
        ct("docker", "rm", ident)


def heartbeat(jobs):
    try:
        worker_sha = hashlib.sha256((jobs.parent/'src/worker.py').read_bytes()).hexdigest()
        policy_sha = hashlib.sha256((jobs.parent/'src/qwen_language_policy.py').read_bytes()).hexdigest()
    except OSError:
        worker_sha = policy_sha = None
    ready = worker_sha == EXPECTED_WORKER_SHA256 and policy_sha == policy_fingerprint()
    write(jobs / "agent-heartbeat.json", {"timestamp": time.time(), "status": "healthy" if ready else "unavailable", "ct": 627,
                                         "dtype": "float32", "chunk": 300, "context": 25,
                                         "protocol": WORKER_PROTOCOL, "languages": ['es', 'en'],
                                         "worker_source_sha256": worker_sha, "language_policy_sha256": policy_sha})


def request(path):
    r = read(path / "request.json")
    if not re.fullmatch(r"[a-f0-9]{32}", path.name) or path.is_symlink():
        raise ValueError("Invalid job identifier")
    validate_request(r)
    if not isinstance(r["text"], str) or not 1 <= len(r["text"]) <= 1200:
        raise ValueError("Text must contain1..1200characters")
    if (path / "checkpoint").exists():
        raise ValueError("Checkpoint exists; do not repeat Talker. Decoder recovery requires review")
    if (path / "text.txt").read_text() != r["text"]:
        raise ValueError("Request/text integrity mismatch")
    return r


def run(jobs, path):
    global CHILD
    state = {"status": "running", "phase": "preflight", "started_at": time.time(), "job": path.name}
    write(path / "state.json", state)
    start = time.monotonic()
    try:
        request(path)
        for stage in ["talker", "decoder"]:
            if STOP or (path / "cancel.flag").exists():
                state.update(status="cancelled"); break
            remaining = int(900 - (time.monotonic() - start) - 15)
            if remaining < 30:
                raise TimeoutError("Total budget exhausted; checkpoint preserved")
            state["phase"] = stage; write(path / "state.json", state)
            log = path / (stage + "-supervisor.json")
            with log.open("wb") as stream:
                owner = path.stat(); os.chmod(log, 0o600); os.chown(log, owner.st_uid, owner.st_gid)
                CHILD = subprocess.Popen(["/usr/bin/python3", str(CODE / "supervise.py"), stage,
                                          "--job", path.name, "--attempt", "01", "--timeout", str(remaining),
                                          "--chunk", "300", "--real", "--execute"], stdout=stream,
                                         stderr=subprocess.DEVNULL, start_new_session=True)
                cancelling = False
                while CHILD.poll() is None:
                    heartbeat(jobs)
                    if (STOP or (path / "cancel.flag").exists()) and not cancelling:
                        os.killpg(CHILD.pid, signal.SIGTERM); cancelling = True
                    time.sleep(0.3)
                CHILD.wait(); CHILD = None
            if STOP or (path / "cancel.flag").exists():
                cleanup_owned(); state.update(status="cancelled"); break
            result = read(log, 32 * 1024 * 1024)
            if not result.get("success"):
                raise RuntimeError(stage + ": " + result.get("error", "worker failed; inspect private metrics"))
            state[stage] = result["worker_result"]
            state["checkpoint_preserved"] = (path / "checkpoint/COMMITTED.json").exists()
            write(path / "state.json", state)
        else:
            if not (path / "decoded-300.wav").is_file():
                raise RuntimeError("Decoder returned without WAV")
            state.update(status="completed", duration=state["decoder"]["seconds"],
                         wav_sha256=state["decoder"]["wav_sha256"])
    except Exception as exc:
        state.update(status="failed", error=str(exc)[:400])
    finally:
        if CHILD and CHILD.poll() is None:
            os.killpg(CHILD.pid, signal.SIGTERM)
            try:
                CHILD.wait(timeout=25)
            except subprocess.TimeoutExpired:
                os.killpg(CHILD.pid, signal.SIGKILL); CHILD.wait()
        CHILD = None
        cleanup_owned()
        state.update(finished_at=time.time(), checkpoint_preserved=(path / "checkpoint/COMMITTED.json").exists())
        write(path / "state.json", state)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--cleanup-owned", action="store_true"); args = ap.parse_args()
    if args.cleanup_owned:
        cleanup_owned(); return
    jobs = root()
    cleanup_owned()
    # A service restart never retries an interrupted inference, even if a checkpoint exists.
    for path in jobs.iterdir():
        if path.is_dir() and not path.is_symlink() and (path / "state.json").is_file():
            s = read(path / "state.json")
            if s.get("status") in ["running", "queued"]:
                s.update(status="failed", error="Agent restarted; inspect retained checkpoint before recovery")
                write(path / "state.json", s)
    while not STOP:
        heartbeat(jobs)
        for path in sorted(jobs.iterdir()):
            if path.is_symlink() or not path.is_dir() or not re.fullmatch(r"[a-f0-9]{32}", path.name):
                continue
            if (path / "request.json").is_file() and (path / "state.json").is_file():
                if read(path / "state.json").get("status") == "queued":
                    run(jobs, path); break
        time.sleep(0.5)


if __name__ == "__main__":
    def stop(signum, frame):
        global STOP
        STOP = True
    signal.signal(signal.SIGTERM, stop); signal.signal(signal.SIGINT, stop)
    main()
