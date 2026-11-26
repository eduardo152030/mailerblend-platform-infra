#!/usr/bin/env python3
"""Stage the EVA web API on CT622 without recreating the bot services."""

import argparse
import json
from pathlib import Path
import socket
import subprocess
from uuid import UUID


def docker(*args, capture=False):
    return subprocess.run(
        ["docker", *args], check=True, text=True, capture_output=capture,
    ).stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("release", type=Path)
    parser.add_argument("--tls", action="store_true")
    args = parser.parse_args()
    if socket.gethostname().split(".")[0] != "infra-eva-assistant-bot":
        raise SystemExit("Expected CT622")
    release = args.release.resolve(strict=True)
    subject = UUID((release / "owner-subject").read_text().strip())
    existing = json.loads(docker("inspect", "eva-api", capture=True))[0]
    if not existing["State"]["Running"] or "eva-network" not in existing["NetworkSettings"]["Networks"]:
        raise SystemExit("Expected running EVA API on eva-network")

    environment = dict(item.split("=", 1) for item in existing["Config"]["Env"])
    environment["EVA_UI_OWNER_SUBJECT"] = str(subject)
    if not environment.get("FOCALBOARD_TOKEN"):
        raise SystemExit("EVA service token is missing")
    mounts = [
        f"{m['Source']}:{m['Destination']}:{'rw' if m['RW'] else 'ro'}"
        for m in existing["Mounts"]
        if m["Type"] == "bind" and m["Destination"] in (
            "/app/uploads", "/app/persona", "/etc/timezone", "/etc/localtime",
        )
    ]
    paths = (
        "eva_ui_entrypoint.py",
        "api/ui_session_routes.py",
        "api/ui_board_routes.py",
        "integrations/focalboard_client.py",
    )
    for relative in paths:
        path = release / relative
        if not path.is_file() or path.is_symlink():
            raise SystemExit(f"Missing release file: {relative}")
        mounts.append(f"{path}:/app/{relative}:ro")

    command = ["uvicorn", "eva_ui_entrypoint:app", "--host", "0.0.0.0", "--port", "8000"]
    port = "127.0.0.1:18001:8000"
    if args.tls:
        for filename in ("server.crt", "server.key"):
            path = release / filename
            if not path.is_file() or path.is_symlink():
                raise SystemExit(f"Missing TLS input: {filename}")
            mounts.append(f"{path}:/run/eva-tls/{filename}:ro")
        command.extend(["--ssl-certfile", "/run/eva-tls/server.crt",
                        "--ssl-keyfile", "/run/eva-tls/server.key"])
        port = "192.168.1.122:18443:8000"

    config = {
        "services": {
            "web-api": {
                "image": existing["Image"],
                "command": command,
                "environment": {key: value.replace("$", "$$") for key, value in environment.items()},
                "volumes": mounts,
                "networks": ["existing"],
                "ports": [port],
                "restart": "unless-stopped",
                "logging": {"driver": "json-file", "options": {"max-size": "10m", "max-file": "3"}},
            },
        },
        "networks": {"existing": {"external": True, "name": "eva-network"}},
    }
    compose = release / "compose.private.json"
    compose.touch(mode=0o600)
    compose.write_text(json.dumps(config))
    docker("compose", "-p", "eva-web", "-f", str(compose), "config", "--quiet")
    docker("compose", "-p", "eva-web", "-f", str(compose), "up", "-d", "--pull", "never")


if __name__ == "__main__":
    main()
