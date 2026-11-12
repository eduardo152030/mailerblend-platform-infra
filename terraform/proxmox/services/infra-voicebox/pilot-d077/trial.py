"""Future two-stage pilot, plan by default. No retry and900s combined budget."""
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys
import time

ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument("--job", required=True)
ap.add_argument("--execute", action="store_true", help="Requires separate owner approval of real inference")
args = ap.parse_args()
if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,35}", args.job):
    ap.error("Unsafe job identifier")
if not args.execute:
    print(json.dumps({"plan_only": True, "total_budget_seconds": 900, "first_decoder_chunk": 300,
                      "stages": ["Talker->atomic checkpoint->PID0/cgroup empty", "decoder-only with remaining budget"],
                      "automatic_retry": False, "automatic_chunk120": False}))
    raise SystemExit(0)

start = time.monotonic()
results = {}
for stage in ["talker", "decoder"]:
    # Reserve time for SSH/startup/complete cancellation; never silently extend deadline.
    remaining = int(900 - (time.monotonic() - start) - 15)
    if remaining < 30:
        results[stage] = {"not_started": True, "reason": "Insufficient remaining total budget; keep checkpoint"}
        break
    cmd = [sys.executable, str(Path(__file__).with_name("run.py")), stage, "--job", args.job,
           "--attempt", "01", "--real", "--execute", "--timeout", str(min(remaining, 885)), "--chunk", "300"]
    r = subprocess.run(cmd, text=True, capture_output=True)
    try:
        results[stage] = json.loads(r.stdout)
    except json.JSONDecodeError:
        results[stage] = {"success": False, "reason": "Supervisor output unavailable; inspect owned stage before any resume"}
    if r.returncode or not results[stage].get("success"):
        break
results["elapsed_seconds"] = time.monotonic() - start
print(json.dumps(results), flush=True)
raise SystemExit(0 if results.get("decoder", {}).get("success") else 1)
