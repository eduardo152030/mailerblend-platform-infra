"""PVE read-only180s/7samples after deployment; no inference or remote service changes."""
from pathlib import Path
import datetime
import json
import subprocess
import time
import urllib.request

CG = Path("/sys/fs/cgroup/lxc/627")


def ct(*args):
    return subprocess.check_output(["pct", "exec", "627", "--", *args], text=True, timeout=15)


def nums(path):
    return {k: int(v) for k, v in (x.split() for x in Path(path).read_text().splitlines())}


def sample():
    c = json.loads(ct("docker", "inspect", "voicebox"))[0]
    with urllib.request.urlopen("http://192.168.1.127:17493/health", timeout=5) as f:
        h = json.load(f)
    with urllib.request.urlopen("http://192.168.1.127:17493/qwen-worker/health", timeout=5) as f:
        worker = json.load(f)
    unit = subprocess.check_output(["systemctl", "show", "voicebox-qwen-627.service", "-p", "ActiveState", "-p", "MemoryCurrent", "-p", "NRestarts"], text=True)
    exporters = {str(p): urllib.request.urlopen("http://192.168.1.127:" + str(p) + "/metrics", timeout=8).status for p in [9100, 8085]}
    return {"at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(), "id": c["Id"], "image": c["Image"],
            "restart_count": c["RestartCount"], "healthy": h["status"] == "healthy" and c["State"]["Health"]["Status"] == "healthy",
            "supervisor_healthy": worker["status"] == "healthy", "supervisor": dict(x.split("=", 1) for x in unit.splitlines()),
            "ct_current": int((CG / "memory.current").read_text()), "ct_swap": int((CG / "memory.swap.current").read_text()),
            "ct_stat": nums(CG / "memory.stat"), "ct_events": nums(CG / "memory.events"),
            "ct_psi": (CG / "memory.pressure").read_text(), "host_oom": nums("/proc/vmstat")["oom_kill"], "exporters": exporters}


start = time.monotonic()
result = {"result": "IN PROGRESS", "samples": []}
try:
    for index in range(7):
        if index:
            time.sleep(max(0, start + index * 30 - time.monotonic()))
        row = sample(); result["samples"].append(row)
        baseline = result["samples"][0]
        assert row["id"] == baseline["id"] and row["restart_count"] == baseline["restart_count"]
        assert row["healthy"] and row["supervisor_healthy"] and row["supervisor"]["ActiveState"] == "active"
        assert row["host_oom"] == baseline["host_oom"] and all(row["ct_events"][k] == baseline["ct_events"][k] for k in ["oom", "oom_kill"])
        assert row["ct_current"] < 9.5 * 2**30 and all(s == 200 for s in row["exporters"].values())
    result["result"] = "PASS"
except Exception as exc:
    result.update(result="HALT", error=type(exc).__name__)
finally:
    result["elapsed_seconds"] = time.monotonic() - start
    print(json.dumps(result), flush=True)
raise SystemExit(0 if result["result"] == "PASS" else 1)
