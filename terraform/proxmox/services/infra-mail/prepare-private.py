"""Prepare the private relay files locally. Never prints credentials."""
import argparse
from email.utils import parseaddr
from ipaddress import IPv4Address
import os
from pathlib import Path
import re
import secrets
import subprocess

from dotenv import dotenv_values

IDENTITIES = ("crm", "gotrue", "proxmox", "grafana", "alertmanager", "n8n")


def private_file(path, content):
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_NOFOLLOW | os.O_TRUNC, 0o600)
    with os.fdopen(descriptor, "w") as stream:
        os.fchmod(stream.fileno(), 0o600)
        stream.write(content)


def openssl(*args, input=None):
    return subprocess.run(
        ["openssl", *args], input=input, text=True, check=True, capture_output=True,
    ).stdout


def prepare(source, directory, ip):
    values = dotenv_values(source, interpolate=False)
    host, port, user, password = [values.get("NC_SMTP_" + name) or "" for name in ("HOST", "PORT", "USERNAME", "PASSWORD")]
    sender = parseaddr(values.get("NC_SMTP_FROM") or user)[1]
    if not re.fullmatch(r"[a-zA-Z0-9.-]+", host) or port not in ("465", "587"):
        raise ValueError("Invalid SMTP endpoint")
    if not user or not password or re.search(r"\s", user) or re.search(r"[\r\n]", password):
        raise ValueError("Invalid SMTP login format")
    if not re.fullmatch(r"[^\s@]+@[^\s@]+", sender):
        raise ValueError("Invalid sender")
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    if directory.is_symlink() or directory.stat().st_mode & 0o077:
        raise ValueError("Output directory must be private")
    ca = directory / "ca.crt"
    ca_key = directory / "ca.key"
    if not ca.is_file() and not ca_key.is_file():
        openssl("req", "-x509", "-newkey", "rsa:3072", "-nodes", "-days", "1825",
                "-subj", "/CN=Homelab infra-mail CA", "-keyout", str(ca_key), "-out", str(ca))
    host_key = directory / "tls.key"
    request = directory / "tls.csr"
    certificate = directory / "tls.crt"
    extensions = directory / "tls.ext"
    private_file(extensions, f"subjectAltName=DNS:infra-mail,DNS:infra-mail.lan,IP:{ip}\nextendedKeyUsage=serverAuth\n")
    openssl("req", "-new", "-newkey", "rsa:3072", "-nodes", "-subj", "/CN=infra-mail",
            "-keyout", str(host_key), "-out", str(request))
    openssl("x509", "-req", "-in", str(request), "-CA", str(ca), "-CAkey", str(ca_key),
            "-set_serial", str(secrets.randbits(127) + 1), "-days", "365",
            "-extfile", str(extensions), "-out", str(certificate))

    private_file(directory / "relay-host", f"[{host}]:{port}\n")
    private_file(directory / "relay-password", f"[{host}]:{port} {user}:{password}\n")
    private_file(directory / "sender-login", f"{sender} {','.join(IDENTITIES)}\n")
    hashed = []
    for identity in IDENTITIES:
        path = directory / (identity + ".password")
        if not path.exists():
            private_file(path, secrets.token_urlsafe(36) + "\n")
        stored = path.read_text().strip()
        digest = openssl("passwd", "-6", "-stdin", input=stored + "\n").strip()
        hashed.append(f"{identity}:{{SHA512-CRYPT}}{digest}")
    private_file(directory / "service-users", "\n".join(hashed) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--ip", required=True, type=IPv4Address)
    args = parser.parse_args()
    os.umask(0o077)
    try:
        prepare(args.source, args.output, args.ip)
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        raise SystemExit(f"Private provisioning failed: {type(error).__name__}") from None
