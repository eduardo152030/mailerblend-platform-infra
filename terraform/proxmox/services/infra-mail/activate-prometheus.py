"""Add the infra-mail target and its rules to Prometheus on CT610."""
from argparse import ArgumentParser
from datetime import datetime, timezone
from ipaddress import IPv4Address, IPv4Network
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path("/opt/infra-prom/config")
TARGETS = ROOT / "targets/node-exporter.json"
RULES = ROOT / "rules/infra-mail.yml"


def merge(current, address):
    desired = {
        "targets": [f"{address}:9100"],
        "labels": {"service": "infra-mail", "vmid": "632", "source": "inventory", "cpu_contract": "lxc_cgroup_v1"},
    }
    owned = [group for group in current if group.get("labels", {}).get("service") == "infra-mail"]
    if any(group.get("labels", {}).get("vmid") != "632" for group in owned):
        raise ValueError("Unexpected existing infra-mail target")
    if owned == [desired]:
        return current
    return [group for group in current if group not in owned] + [desired]


def install(path, content, mode):
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as staged:
        staged.write(content)
        candidate = Path(staged.name)
    candidate.chmod(mode)
    candidate.replace(path)


def command(*args):
    subprocess.run(args, check=True)


def reload_prometheus():
    command("docker", "exec", "prometheus", "promtool", "check", "config", "/etc/prometheus/prometheus.yml")
    command("docker", "kill", "--signal", "HUP", "prometheus")


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--ip", required=True, type=IPv4Address)
    parser.add_argument("--rules", required=True, type=Path)
    args = parser.parse_args()
    if args.ip not in IPv4Network("192.168.1.0/24") or Path("/etc/hostname").read_text().strip() != "infra-prom":
        parser.error("Expected the observed LAN address and the infra-prom host")

    old_targets = TARGETS.read_bytes()
    old_rules = RULES.read_bytes() if RULES.exists() else None
    current = json.loads(old_targets)
    merged = merge(current, args.ip)
    new_targets = old_targets if merged == current else (json.dumps(merged, indent=2) + "\n").encode()
    new_rules = args.rules.read_bytes()
    if new_targets == old_targets and new_rules == old_rules:
        print("Sin cambios")
        return

    directory = Path("/opt/infra-prom/.rollback") / ("infra-mail-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ"))
    directory.mkdir(mode=0o700, parents=True)
    target_mode = TARGETS.stat().st_mode & 0o777
    rules_mode = RULES.stat().st_mode & 0o777 if old_rules is not None else 0o644
    install(directory / "node-exporter.json", old_targets, 0o600)
    if old_rules is not None:
        install(directory / "infra-mail.yml", old_rules, 0o600)
    try:
        install(TARGETS, new_targets, target_mode)
        install(RULES, new_rules, rules_mode)
        reload_prometheus()
    except (OSError, subprocess.CalledProcessError):
        install(TARGETS, old_targets, target_mode)
        if old_rules is None:
            RULES.unlink(missing_ok=True)
        else:
            install(RULES, old_rules, rules_mode)
        reload_prometheus()
        raise
    print(f"Prometheus recargado. Respaldo: {directory}")


if __name__ == "__main__":
    main()
