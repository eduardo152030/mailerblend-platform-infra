#!/usr/bin/env python3
"""Apply only the reviewed CRM monitoring files on CT610 or CT611."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import socket
import subprocess
import tempfile

SCOPES = {
    "infra-prom": ("/opt/infra-prom", (
        "config/rules/container-availability.yml",
        "config/rules/crm-618-health.yml",
        "config/targets/blackbox.json",
    )),
    "infra-grafana": ("/opt/infra-grafana", (
        "config/provisioning/fleet-assets/proxmox-lxc-fleet.json",
        "config/provisioning/fleet-assets/proxmox-lxc-details.json",
    )),
}


def digest(contents):
    return sha256(contents).hexdigest() if contents is not None else None


def read(path):
    return path.read_bytes() if path.is_file() else None


def write(path, contents, mode):
    if contents is None:
        path.unlink(missing_ok=True)
        return
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
        stream.write(contents)
        staged = Path(stream.name)
    staged.chmod(mode)
    staged.replace(path)


def reload_prometheus(host):
    if host == "infra-prom":
        subprocess.run(
            ["docker", "exec", "prometheus", "promtool", "check", "config", "/etc/prometheus/prometheus.yml"],
            check=True,
        )
        subprocess.run(["docker", "kill", "--signal", "HUP", "prometheus"], check=True, stdout=subprocess.DEVNULL)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", type=Path)
    parser.add_argument("--rollback", action="store_true")
    args = parser.parse_args()
    host = socket.gethostname()
    root, names = SCOPES[host]
    expected = json.loads((args.bundle / "baseline.json").read_text())
    originals = args.bundle / "before"
    originals.mkdir(mode=0o700, exist_ok=True)
    changes = []
    for name in names:
        path = Path(root) / name
        current = read(path)
        candidate = (args.bundle / "candidate" / name).read_bytes()
        backup = originals / path.name
        mode = path.stat().st_mode & 0o777 if current is not None else 0o644
        if args.rollback:
            if current != candidate:
                raise SystemExit(f"Post-deploy configuration drift: {name}")
            desired = read(backup)
            if digest(desired) != expected[name]:
                raise SystemExit(f"Rollback backup does not match baseline: {name}")
        else:
            desired = candidate
            if current == desired:
                continue
            if digest(current) != expected[name]:
                raise SystemExit(f"Live configuration differs from baseline: {name}")
            if current is not None:
                if not backup.exists():
                    with backup.open("xb") as stream:
                        stream.write(current)
                if read(backup) != current:
                    raise SystemExit(f"Rollback backup differs from baseline: {name}")
        changes.append((path, current, desired, mode))
    if not changes:
        print("Sin cambios")
        return
    try:
        for path, _, desired, mode in changes:
            write(path, desired, mode)
        reload_prometheus(host)
    except Exception:
        for path, previous, _, mode in changes:
            write(path, previous, mode)
        reload_prometheus(host)
        raise
    print(f"{host}: {len(changes)} archivos acotados; respaldo {originals}")


if __name__ == "__main__":
    main()
