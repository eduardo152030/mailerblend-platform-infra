#!/usr/bin/env python3
"""Prepare a new private CT633 bootstrap directory. Existing material is preserved."""
import argparse
import json
import os
from pathlib import Path
import re
import secrets
import subprocess
from uuid import uuid4

import bcrypt

ORIGIN = "https://knowledge.test:18443"


def run(directory, *args):
    subprocess.run(["openssl", *args], cwd=directory, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--admin-email", required=True)
    parser.add_argument("--agent-email", required=True)
    args = parser.parse_args()
    emails = [args.admin_email.lower(), args.agent_email.lower()]
    if len(set(emails)) != 2 or any(not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email) for email in emails):
        parser.error("Two distinct valid email addresses are required")

    os.umask(0o077)
    args.directory.mkdir()
    runtime = args.directory / "private"
    runtime.mkdir()
    run(args.directory, "req", "-x509", "-newkey", "rsa:3072", "-nodes", "-days", "30",
        "-subj", "/CN=Knowledge Platform Private CA", "-keyout", "ca.key", "-out", "private/ca.pem",
        "-addext", "basicConstraints=critical,CA:TRUE")
    run(args.directory, "req", "-new", "-newkey", "rsa:3072", "-nodes",
        "-subj", "/CN=knowledge.test", "-keyout", "private/server.key", "-out", "server.csr")
    (args.directory / "server-ext.cnf").write_text("subjectAltName=DNS:knowledge.test\nextendedKeyUsage=serverAuth\n")
    run(args.directory, "x509", "-req", "-in", "server.csr", "-CA", "private/ca.pem",
        "-CAkey", "ca.key", "-CAcreateserial", "-out", "private/server.pem",
        "-days", "30", "-extfile", "server-ext.cnf")
    client_secret = secrets.token_hex(32)
    users = []
    passwords = {}
    for username, email in zip(("operator", "outline-agent"), emails):
        password = secrets.token_urlsafe(30)
        passwords[email] = password
        users.append({
            "email": email, "username": username, "userID": str(uuid4()),
            "hash": bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode(),
        })
    config = {
        "issuer": ORIGIN + "/dex",
        "storage": {"type": "sqlite3", "config": {"file": "/var/dex/knowledge.db"}},
        "web": {"http": "0.0.0.0:5556"},
        "oauth2": {"responseTypes": ["code"], "skipApprovalScreen": True},
        "enablePasswordDB": True,
        "staticClients": [{
            "id": "outline-knowledge", "name": "Outline", "secret": client_secret,
            "redirectURIs": [ORIGIN + "/auth/oidc.callback"],
        }],
        "staticPasswords": users,
    }
    (runtime / "dex.json").write_text(json.dumps(config, indent=2) + "\n")
    (args.directory / "login.json").write_text(json.dumps(passwords, indent=2) + "\n")
    values = {
        "SERVICE_BIND_IP": "127.0.0.1", "OUTLINE_URL": ORIGIN,
        "OUTLINE_SECRET_KEY": secrets.token_hex(32), "OUTLINE_UTILS_SECRET": secrets.token_hex(32),
        "POSTGRES_PASSWORD": secrets.token_hex(32), "OIDC_ISSUER_URL": ORIGIN + "/dex",
        "OIDC_CLIENT_ID": "outline-knowledge", "OIDC_CLIENT_SECRET": client_secret,
    }
    (args.directory / "outline.env").write_text("".join(f"{key}={value}\n" for key, value in values.items()))


if __name__ == "__main__":
    main()
