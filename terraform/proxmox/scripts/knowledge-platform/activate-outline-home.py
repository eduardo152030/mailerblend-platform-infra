#!/usr/bin/env python3
"""Replace the legacy /home redirect in the existing Outline edge vhost."""
import argparse
import os
from pathlib import Path
import socket
import subprocess
import tempfile

VHOST = Path("/etc/nginx/sites-available/doc.mailerblend.com.conf")
ANCHOR = """    allow 192.168.1.0/24;
    allow 127.0.0.1;
    deny all;
    access_log off;
    location = /home {
        return 302 /;
    }
    location / {
        proxy_pass https://192.168.1.72:18444;
        proxy_ssl_server_name on;
        proxy_ssl_name knowledge.test;
        proxy_ssl_trusted_certificate /etc/nginx/knowledge-platform/ct633-ca.pem;
        proxy_ssl_verify on;
"""


def replace(contents, mode):
    with tempfile.NamedTemporaryFile(dir=VHOST.parent, delete=False) as stream:
        stream.write(contents)
        candidate = Path(stream.name)
    candidate.chmod(mode)
    candidate.replace(VHOST)


def reload():
    subprocess.run(["nginx", "-t"], check=True, timeout=12)
    subprocess.run(["systemctl", "reload", "nginx"], check=True, timeout=12)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("snippet", type=Path)
    parser.add_argument("backup_directory", type=Path)
    parser.add_argument("--rollback", action="store_true")
    args = parser.parse_args()
    if socket.gethostname() != "edge-router":
        raise SystemExit("Expected CT109 edge-router")
    os.umask(0o077)
    current = VHOST.read_bytes()
    mode = VHOST.stat().st_mode & 0o777
    snippet = args.snippet.read_bytes()
    backup = args.backup_directory / "vhost.before"
    prepared = args.backup_directory / "vhost.after"
    if args.rollback:
        if current != prepared.read_bytes():
            raise SystemExit("Unexpected vhost drift")
        desired = backup.read_bytes()
    else:
        if snippet in current:
            print("Sin cambios")
            return
        if current.count(ANCHOR.encode()) != 1:
            raise SystemExit("Expected exactly one matching legacy stanza")
        desired = current.replace(ANCHOR.encode(), snippet)
        with backup.open("xb") as stream:
            stream.write(current)
        with prepared.open("xb") as stream:
            stream.write(desired)
    replace(desired, mode)
    try:
        reload()
    except (OSError, subprocess.SubprocessError):
        replace(current, mode)
        reload()
        raise
    print("Vhost validado y recargado")


if __name__ == "__main__":
    main()
