"""Execute on PVE. One stage/container, CT627 only. Default is plan, not execution."""
import argparse
import datetime
import fcntl
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import time
import urllib.request
import uuid

from guards import stop_reason, predictive_preflight

CG = Path("/sys/fs/cgroup/lxc/627")
ROOT = "/srv/voicebox/pilot-d077"
CODEC = "/srv/voicebox/huggingface/hub/models--Qwen--Qwen3-TTS-12Hz-0.6B-Base/snapshots/5d83992436eae1d760afd27aff78a71d676296fc/speech_tokenizer"
IMAGE = "sha256:bcc5c14f88064ffa76f813d788d183918b208deba45075d8118a2b07c60c248b"


def ct(*args, timeout=15):
    return subprocess.check_output(["pct", "exec", "627", "--", *args], text=True, timeout=timeout)


def ct_python(code):
    return ct("python3", "-c", code)


def nums(path):
    return {k: int(v) for k, v in (line.split() for line in Path(path).read_text().splitlines())}


def psi(path):
    return float(Path(path).read_text().splitlines()[-1].split()[1].split("=")[1])


def health():
    return json.load(urllib.request.urlopen("http://192.168.1.127:17493/health", timeout=5))


def sample(worker=None):
    vmstat = nums("/proc/vmstat")
    value = {"at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
             "ct_current": int((CG / "memory.current").read_text()),
             "ct_swap": int((CG / "memory.swap.current").read_text()),
             "ct_stat": nums(CG / "memory.stat"), "ct_cpu": nums(CG / "cpu.stat"),
             "ct_events": nums(CG / "memory.events"), "host_oom": vmstat["oom_kill"],
             "host_pswpin": vmstat["pswpin"], "host_pswpout": vmstat["pswpout"],
             "ct_psi_full_avg10": psi(CG / "memory.pressure"),
             "host_psi_full_avg10": psi("/proc/pressure/memory"),
             "host_available": int(next(line.split()[1] for line in Path("/proc/meminfo").read_text().splitlines() if line.startswith("MemAvailable:"))) * 1024}
    if worker and worker.exists():
        try:
            value.update(worker_current=int((worker / "memory.current").read_text()),
                         worker_swap=int((worker / "memory.swap.current").read_text()),
                         worker_stat=nums(worker / "memory.stat"), worker_cpu=nums(worker / "cpu.stat"),
                         worker_events=nums(worker / "memory.events"))
            rss = 0
            pids = (worker / "cgroup.procs").read_text().split()
            value["worker_process_count"] = len(pids)
            for pid in pids:
                try:
                    data = Path("/proc", pid, "status").read_text()
                    rss += int(data.split("VmRSS:")[1].split()[0]) * 1024 if "VmRSS:" in data else 0
                except OSError:
                    pass
            value["rss_bytes"] = rss
        except FileNotFoundError:
            pass  # Cgroup removed when stage finishes; process state is verified separately.
    return value


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["talker", "decoder", "verify", "imports", "synthetic-write", "synthetic-read", "hold"])
    ap.add_argument("--job", required=True)
    ap.add_argument("--attempt", required=True)
    ap.add_argument("--chunk", type=int, choices=[300, 120], default=300)
    ap.add_argument("--timeout", type=int, default=180)
    ap.add_argument("--cancel-after", type=float)
    ap.add_argument("--execute", action="store_true")
    ap.add_argument("--real", action="store_true")
    args = ap.parse_args()
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,35}", args.job) or not re.fullmatch(r"[a-z0-9-]{1,12}", args.attempt):
        raise ValueError("Unsafe job/attempt identifier")
    if not 10 <= args.timeout <= 900:
        raise ValueError("Timeout must be10..900seconds")
    if args.cancel_after is not None and (args.stage != "hold" or not 1 <= args.cancel_after <= 5):
        raise ValueError("Synthetic cancellation is only for hold stage")
    real = args.stage in ["talker", "decoder"]
    if real and not args.real:
        raise ValueError("Real stages require explicit --real; preparation does not authorize them")
    job = ROOT + "/jobs/" + args.job
    name = "qwen-d077-" + args.job + "-" + args.stage + "-" + args.attempt
    owner = uuid.uuid4().hex
    cmd = ["docker", "run", "-d", "--name", name, "--network", "none", "--no-healthcheck",
           "--label", "d077.owner=" + owner,
           "--cpus", "3", "--memory", "9g", "--memory-swap", "9g", "--pids-limit", "96",
           "--user", "999:999", "--read-only", "--cap-drop", "ALL", "--security-opt", "no-new-privileges",
           "--tmpfs", "/tmp:rw,size=128m", "-e", "NUMBA_CACHE_DIR=/tmp/numba", "-e", "HF_HUB_OFFLINE=1",
           "-e", "OMP_NUM_THREADS=3", "-e", "MKL_NUM_THREADS=3", "-e", "TORCH_NUM_THREADS=3",
           "-e", "TOKENIZERS_PARALLELISM=false", "-e", "PYTHONDONTWRITEBYTECODE=1",
           "-e", "PILOT_TIMEOUT_SECONDS=" + str(args.timeout - 5), "-e", "RESULT_NAME=" + args.stage + "-" + args.attempt,
           "-v", ROOT + "/src:/src:ro", "-v", job + ":/job:rw"]
    if args.stage == "talker":
        cmd += ["-e", "HF_HOME=/cache", "-v", "/srv/voicebox/huggingface:/cache:ro",
                "-v", "/srv/voicebox/pilot-d072/private:/private:ro"]
    if args.stage in ["decoder", "verify", "synthetic-read"]:
        # Also mask the alias under writable /job, so B cannot alter A's checkpoint.
        cmd += ["-v", job + "/checkpoint:/checkpoint:ro",
                "-v", job + "/checkpoint:/job/checkpoint:ro"]
    if args.stage in ["decoder", "imports"]:
        # HF snapshot files are relative symlinks into blobs outside speech_tokenizer/.
        # Bind individual files so Docker resolves each source; no broken isolated symlinks.
        cmd += ["-v", CODEC + "/config.json:/codec/config.json:ro",
                "-v", CODEC + "/model.safetensors:/codec/model.safetensors:ro"]
    cmd += ["--workdir", "/job", "--entrypoint", "python", IMAGE, "/src/worker.py", args.stage, "--chunk", str(args.chunk)]
    if real:
        cmd += ["--real"]
    if not args.execute:
        return {"plan_only": True, "command": cmd, "no_container_created": True}
    lock = open("/run/lock/qwen-d077-627.lock", "a")
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    start = time.monotonic()
    baseline = sample()
    result = {"stage": args.stage, "name": name, "baseline": baseline, "measurements": [], "chunk_steps": args.chunk}
    created = False
    launch_attempted = False
    worker = None
    cid = None
    since = None
    try:
        if args.stage == 'talker':
            result['predictive_preflight'] = predictive_preflight(baseline)
            if not result['predictive_preflight']['passed']:
                p = result['predictive_preflight']
                raise RuntimeError('Memoria inicial insuficiente para preparar la voz: '
                                   f"{p['initial_ct_bytes']/2**30:.2f}GiB +4.50GiB de arranque +0.50GiB de margen "
                                   '> guarda14.00GiB. Qwen no se ha cargado; recuperar margen antes de reintentar.')
        if baseline["host_available"] < 12 * 2**30 or baseline["ct_swap"] >= 1792 * 2**20 or baseline["ct_psi_full_avg10"] >= 5:
            raise RuntimeError("Preflight headroom/pressure failed")
        initial_stop, _ = stop_reason(baseline, baseline, 0, None)
        if initial_stop:
            raise RuntimeError("Preflight:" + initial_stop)
        if int((CG / "memory.max").read_text()) != 15 * 2**30 or int((CG / "memory.swap.max").read_text()) != 2 * 2**30:
            raise RuntimeError("CT resources differ from authorized limits")
        config = subprocess.check_output(["pct", "config", "627"], text=True)
        if "cores: 3" not in config.splitlines():
            raise RuntimeError("CTCPU must remain3")
        if ct("docker", "ps", "--format", "{{.Names}}").strip().count("qwen-"):
            raise RuntimeError("Another Qwen worker is active")
        if name in ct("docker", "ps", "-a", "--format", "{{.Names}}").splitlines():
            raise RuntimeError("Attempt exists; never stop or replace it")
        h = health()
        if h["status"] != "healthy" or h["model_loaded"]:
            raise RuntimeError("Voicebox unhealthy or productive model active")
        # Fail closed if Docker would silently create an absent checkpoint/source bind.
        code = f"from pathlib import Path;import os; p=Path({job!r});assert p.is_dir() and p.stat().st_uid==999 and not p.stat().st_mode&0o077;assert (Path({ROOT!r})/'src/worker.py').is_file();assert os.statvfs(p).f_bavail*os.statvfs(p).f_frsize>10*2**30"
        if args.stage in ["decoder", "verify", "synthetic-read"]:
            code += ";assert (p/'checkpoint/COMMITTED.json').is_file()"
        if args.stage == "decoder":
            code += ";import json,hashlib;r=json.loads((p/'talker-release.json').read_text());assert r['pid']==0 and not r['running'] and r['cgroup_empty'];assert r['manifest_sha256']==hashlib.sha256((p/'checkpoint/manifest.json').read_bytes()).hexdigest()"
        if args.stage in ["decoder", "imports"]:
            code += f";assert (Path({CODEC!r})/'config.json').is_file() and (Path({CODEC!r})/'model.safetensors').is_file()"
        ct_python(code)
        launch_attempted = True
        cid = ct(*cmd).strip()
        if not re.fullmatch(r"[a-f0-9]{64}", cid):
            raise RuntimeError("Invalid created container ID")
        created = True
        created_at = time.monotonic()
        worker = next(CG.rglob("docker-" + cid + ".scope"), None)
        next_health = 0
        while True:
            now = time.monotonic() - start
            m = sample(worker)
            m["elapsed"] = now
            result["measurements"].append(m)
            reason, since = stop_reason(m, baseline, now, since)
            if reason:
                raise RuntimeError(reason)
            if now >= args.timeout - 2:
                raise TimeoutError("External stage deadline")
            if args.cancel_after and time.monotonic() - created_at >= args.cancel_after:
                result["expected_synthetic_cancellation"] = True
                raise InterruptedError("Synthetic cancellation requested")
            state = json.loads(ct("docker", "inspect", "-f", "{{json .State}}", cid))
            if not state["Running"]:
                result["worker_result"] = json.loads(ct("cat", job + "/" + args.stage + "-" + args.attempt + ".json"))
                result["success"] = state["ExitCode"] == 0 and result["worker_result"].get("success") is True
                break
            if now >= next_health:
                h = health()
                if h["status"] != "healthy" or h["model_loaded"]:
                    raise RuntimeError("Productive service changed during pilot")
                next_health = now + 5
            time.sleep(0.4)
    except BaseException as exc:
        result.update(success=False, error_type=type(exc).__name__, error=str(exc))
    finally:
        # Ensure a second disconnect/interrupt cannot interrupt cancellation midway.
        for s in [signal.SIGINT, signal.SIGTERM, signal.SIGHUP]:
            signal.signal(s, signal.SIG_IGN)
        if launch_attempted and not created:
            # docker run may time out after creating the container. Adopt only our UUID label.
            found = ct("docker", "ps", "-aq", "--no-trunc", "--filter", "label=d077.owner=" + owner).split()
            if len(found) > 1:
                raise RuntimeError("Ambiguous owned container")
            if found:
                cid = found[0]
                created = True
                worker = next(CG.rglob("docker-" + cid + ".scope"), None)
        if created:
            state = json.loads(ct("docker", "inspect", "-f", "{{json .State}}", cid))
            if state["Running"]:
                if worker and worker.exists():
                    if not worker.is_relative_to(CG) or worker.name != "docker-" + cid + ".scope":
                        raise RuntimeError("Refuse cancellation of unowned cgroup")
                    try:
                        (worker / "cgroup.kill").write_text("1")
                        result["cgroup_kill"] = True
                    except OSError:
                        ct("docker", "kill", cid)
                else:
                    ct("docker", "kill", cid)
            ct("docker", "stop", "--time", "1", cid)
            state = json.loads(ct("docker", "inspect", "-f", "{{json .State}}", cid))
            if state["Running"] or state["Pid"] != 0:
                raise RuntimeError("Process still alive; do not start next stage")
            result["container_state"] = state
            result["worker_cgroup_empty"] = worker is None or not worker.exists() or not (worker / "cgroup.procs").read_text().strip()
            if not result["worker_cgroup_empty"]:
                raise RuntimeError("Residual processes; next stage forbidden")
            # Only our freshly-created ephemeral container; persistent bind data stays.
            ct("docker", "rm", cid)
            result["owned_container_removed"] = True
            if args.stage in ["talker", "verify"] and result.get("success"):
                release = json.dumps({"container_id": cid, "pid": 0, "running": False, "cgroup_empty": True,
                                      "checkpoint_verified": True})
                ct_python(f"""from pathlib import Path
import os,json,hashlib
p=Path({job!r});r=json.loads({release!r});r['manifest_sha256']=hashlib.sha256((p/'checkpoint/manifest.json').read_bytes()).hexdigest()
target=p/'talker-release.json'
if target.exists():
 old=json.loads(target.read_text());assert old['manifest_sha256']==r['manifest_sha256'] and old['pid']==0 and old['cgroup_empty'] and not old['running']
else:
 temp=p/'talker-release.partial'
 with temp.open('x') as f:
  os.chmod(temp,0o600);os.chown(temp,999,999);f.write(json.dumps(r));f.flush();os.fsync(f.fileno())
 os.rename(temp,target)
 fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd)
""")
        result["after"] = sample()
        result["elapsed_total"] = time.monotonic() - start
        lock.close()
    return result


if __name__ == "__main__":
    def interrupt(signum, frame):
        raise InterruptedError("Supervisor interrupted")
    for s in [signal.SIGINT, signal.SIGTERM, signal.SIGHUP]:
        signal.signal(s, interrupt)
    result = main()
    print(json.dumps(result), flush=True)
    raise SystemExit(0 if result.get("plan_only") or result.get("success") or result.get("expected_synthetic_cancellation") else 1)
