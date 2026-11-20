#!/usr/bin/env python3
"""Publish only the verified CT632–635 targets and rules on CT610."""
import argparse
from datetime import datetime, timezone
import fcntl
import json
from pathlib import Path
import subprocess
import tempfile
import time
import urllib.request

ROOT = Path("/opt/infra-prom/config")
SERVICES = {
    "infra-mail": "632",
    "infra-knowledge": "633",
    "infra-diagrams": "634",
    "infra-modeling": "635",
}


def install(path, data, mode):
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
        staged = Path(stream.name)
        stream.write(data)
    staged.chmod(mode)
    staged.replace(path)


def promtool():
    subprocess.run(
        ["docker", "exec", "prometheus", "promtool", "check", "config", "/etc/prometheus/prometheus.yml"],
        check=True,
    )


def reload():
    subprocess.run(["docker", "kill", "--signal", "HUP", "prometheus"], check=True, stdout=subprocess.DEVNULL)


def health():
    with urllib.request.urlopen("http://127.0.0.1:9090/api/v1/targets", timeout=5) as response:
        return {
            (row["labels"].get("job"), row["labels"].get("service"), row["labels"].get("instance")): row["health"]
            for row in json.load(response)["data"]["activeTargets"]
        }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", type=Path)
    args = parser.parse_args()
    assert Path("/etc/hostname").read_text().strip() == "infra-prom"
    rollback_root = ROOT.parent / ".rollback"
    rollback_root.mkdir(mode=0o700, exist_ok=True)
    with (rollback_root / "ct632-635.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        baseline = health()
        changes = {}
        desired = set()
        expected_relabels = set()
        for name, job in (("node-exporter.json", "node_exporter"), ("cadvisor.json", "cadvisor")):
            path = ROOT / "targets" / name
            old = json.loads(path.read_bytes())
            new = json.loads((args.bundle / name).read_bytes())
            services = set(SERVICES) - ({"infra-mail"} if job == "cadvisor" else set())
            assert len(new) == len(services)
            assert {row["labels"]["service"] for row in new} == services
            merged = list(old)
            for row in new:
                label = row["labels"]
                assert label["job"] == job and label["vmid"] == SERVICES[label["service"]]
                assert len(row["targets"]) == 1
                target = row["targets"][0]
                if job == "node_exporter":
                    assert label["cpu_contract"] == "lxc_cgroup_v1" and target.endswith(":9100")
                else:
                    assert target.endswith(":8085")
                collisions = [
                    item for item in old
                    if item.get("labels", {}).get("service") == label["service"]
                    or target in item.get("targets", [])
                ]
                if collisions and collisions != [row]:
                    if label["service"] != "infra-mail" or len(collisions) != 1:
                        raise ValueError(f"Target conflict for {job}/{label['service']}")
                    legacy = collisions[0]
                    if {**legacy, "labels": {**legacy["labels"], "job": job}} != row:
                        raise ValueError("Unexpected infra-mail target drift")
                    merged[merged.index(legacy)] = row
                    expected_relabels.add(("node", "infra-mail", target))
                elif not collisions:
                    merged.append(row)
                desired.add((job, label["service"], target))
            if merged != old:
                changes[path] = (json.dumps(merged, indent=2) + "\n").encode()
        for name in ("ct632-635-inventory.yml", "infra-mail.yml"):
            path = ROOT / "rules" / name
            candidate = (args.bundle / name).read_bytes()
            if not path.exists() or path.read_bytes() != candidate:
                if path.exists():
                    raise ValueError(f"Conflicting existing rules: {name}")
                changes[path] = candidate
        if not changes:
            assert all(baseline.get(key) == "up" for key in desired)
            print("Sin cambios. Los siete targets están UP.")
            return
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        backup = rollback_root / f"ct632-635-{stamp}"
        backup.mkdir(mode=0o700)
        originals = {
            path: (path.read_bytes(), path.stat().st_mode & 0o777) if path.exists() else (None, 0o644)
            for path in changes
        }
        for path, (data, _) in originals.items():
            if data is not None:
                install(backup / path.name, data, 0o600)
        try:
            for path, candidate in changes.items():
                install(path, candidate, originals[path][1])
            promtool()
            reload()
            deadline = time.monotonic() + 100
            while time.monotonic() < deadline:
                current = health()
                if all(current.get(key) == "up" for key in desired):
                    stable = {key: state for key, state in baseline.items() if key not in expected_relabels}
                    assert all(key in current for key in stable)
                    assert all(current[key] == "up" for key, state in stable.items() if state == "up")
                    print(f"Siete targets UP. Respaldo: {backup}")
                    return
                time.sleep(5)
            raise TimeoutError("New target coverage did not converge")
        except Exception:
            for path, (data, mode) in originals.items():
                if data is None:
                    path.unlink(missing_ok=True)
                else:
                    install(path, data, mode)
            promtool()
            reload()
            raise


if __name__ == "__main__":
    main()
