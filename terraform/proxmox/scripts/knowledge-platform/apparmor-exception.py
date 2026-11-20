#!/usr/bin/env python3
"""Apply or roll back the approved AppArmor exception on an exact platform CT."""
import argparse
import fcntl
from pathlib import Path
import subprocess

TARGETS = {633: "infra-knowledge", 634: "infra-diagrams", 635: "infra-modeling"}
PROFILE = "lxc.apparmor.profile: unconfined"


def pct(*args):
    return subprocess.check_output(["pct", *args], text=True).strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["apply", "rollback"])
    parser.add_argument("ct", choices=TARGETS, type=int)
    args = parser.parse_args()
    ct = str(args.ct)
    path = Path(f"/etc/pve/lxc/{ct}.conf")
    evidence = Path("/var/lib/knowledge-platform-apparmor")
    evidence.mkdir(mode=0o700, exist_ok=True)
    with (evidence / f"{ct}.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        current = path.read_text()
        config = pct("config", ct).splitlines()
        features = next(line.removeprefix("features: ") for line in config if line.startswith("features: "))
        if (
            f"hostname: {TARGETS[args.ct]}" not in config
            or "unprivileged: 1" not in config
            or not {"keyctl=1", "nesting=1"} <= set(features.split(","))
            or any(line.startswith("lock:") for line in config)
        ):
            raise SystemExit("CT identity or isolation guards differ from the approved scope")
        backup = evidence / f"{ct}.before.conf"
        if args.action == "apply":
            if PROFILE in config:
                if not backup.exists():
                    raise SystemExit("Existing exception has no managed backup")
                print(f"CT{ct}: no changes")
                return
            if any(line.startswith("lxc.apparmor.profile:") for line in config):
                raise SystemExit("Existing AppArmor profile differs")
            if not backup.exists():
                with backup.open("x") as stream:
                    stream.write(current)
            changed = current.replace("\n[", f"\n{PROFILE}\n[", 1) if "\n[" in current else current.rstrip("\n") + f"\n{PROFILE}\n"
        else:
            if not backup.exists() or PROFILE not in config:
                raise SystemExit("Managed exception and backup required")
            changed = current.replace(f"{PROFILE}\n", "", 1)
        if pct("status", ct) != "status: running":
            raise SystemExit("Expected running CT")
        pct("shutdown", ct, "--timeout", "60")
        try:
            if path.read_text() != current:
                raise RuntimeError("CT configuration changed concurrently")
            path.write_text(changed)
            pct("start", ct)
            assert pct("status", ct) == "status: running"
            assert (PROFILE in pct("config", ct).splitlines()) == (args.action == "apply")
        except Exception:
            if pct("status", ct) == "status: running":
                pct("shutdown", ct, "--timeout", "60")
            if path.read_text() == changed:
                path.write_text(current)
            pct("start", ct)
            raise
        print(f"CT{ct}: {args.action} PASS, running")


if __name__ == "__main__":
    main()
