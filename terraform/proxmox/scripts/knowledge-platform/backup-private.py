#!/usr/bin/env python3
"""Capture and verify encrypted application backups through trusted PVE SSH."""
import argparse
from datetime import datetime, timedelta, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess

MODULE = Path(__file__).resolve().parents[2]
DEX_SNAPSHOT = """
import pathlib, sqlite3, subprocess, sys, tempfile
root = subprocess.check_output(
    ['docker', 'volume', 'inspect', '--format', '{{.Mountpoint}}', 'infra-knowledge_dex-data'],
    text=True,
).strip()
with tempfile.TemporaryDirectory() as directory:
    target = pathlib.Path(directory) / 'dex.db'
    with sqlite3.connect(f'file:{root}/knowledge.db?mode=ro', uri=True) as source:
        with sqlite3.connect(target) as copy:
            source.backup(copy)
            assert copy.execute('PRAGMA integrity_check').fetchone() == ('ok',)
    with target.open('rb') as snapshot:
        while chunk := snapshot.read(1024 * 1024):
            sys.stdout.buffer.write(chunk)
"""
EXPORTS = (
    ("633-postgres.dump", 633, ["docker", "exec", "infra-knowledge-postgres-1", "pg_dump", "-U", "outline", "-d", "outline", "-Fc"]),
    ("633-attachments.tar", 633, ["sh", "-ec", 'path=$(docker volume inspect --format "{{.Mountpoint}}" infra-knowledge_attachments); test -d "$path"; tar -C "$path" -cf - .']),
    ("633-dex.sqlite", 633, ["python3", "-c", DEX_SNAPSHOT]),
    ("633-redis.rdb", 633, ["docker", "exec", "infra-knowledge-redis-1", "sh", "-ec",
                          'file=$(mktemp); trap \'unlink "$file"\' EXIT; redis-cli --rdb "$file" >&2; cat "$file"']),
    ("633-config.tar", 633, ["tar", "-C", "/opt/infra-knowledge", "-cf", "-", ".env", "docker-compose.yml", "private"]),
    ("634-config.tar", 634, ["tar", "-C", "/opt/infra-diagrams", "-cf", "-", ".env", "docker-compose.yml"]),
    ("635-config.tar", 635, ["tar", "-C", "/opt/infra-modeling", "-cf", "-", ".env", "docker-compose.yml"]),
)


def digest(stream, output=None):
    result = sha256()
    size = 0
    while chunk := stream.read(1024 * 1024):
        result.update(chunk)
        size += len(chunk)
        if output is not None:
            output.write(chunk)
    return result.hexdigest(), size


def encrypted_capture(producer, target, key):
    gpg = [
        "gpg", "--no-options", "--batch", "--pinentry-mode", "loopback",
        "--passphrase-file", str(key),
    ]
    pending = target.with_suffix(".gpg.pending")
    with subprocess.Popen(producer, stdout=subprocess.PIPE) as source:
        with subprocess.Popen(gpg + [
            "--cipher-algo", "AES256", "--symmetric", "--output", str(pending),
        ], stdin=subprocess.PIPE, stderr=subprocess.DEVNULL) as encrypt:
            expected, size = digest(source.stdout, encrypt.stdin)
            encrypt.stdin.close()
            if encrypt.wait() or source.wait() or not size:
                raise RuntimeError(f"Backup capture failed for {target.name}")
    with subprocess.Popen(gpg + ["--decrypt", str(pending)], stdout=subprocess.PIPE,
                          stderr=subprocess.DEVNULL) as verify:
        actual, restored_size = digest(verify.stdout)
        if verify.wait() or (actual, restored_size) != (expected, size):
            raise RuntimeError(f"Encrypted backup verification failed for {target.name}")
    pending.rename(target)
    return {"file": target.name, "bytes": size, "sha256": expected}


def prune(root, current, days):
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    removed = 0
    for candidate in root.iterdir():
        if candidate == current or candidate.is_symlink() or not candidate.is_dir():
            continue
        match = re.fullmatch(r"backup-([0-9]{8}T[0-9]{6}Z)", candidate.name)
        if not match:
            continue
        try:
            stamp = datetime.strptime(match[1], "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
            receipt = json.loads((candidate / "receipt.json").read_text())
        except (OSError, ValueError):
            continue
        expected = {name + ".gpg" for name, _, _ in EXPORTS} | {"operator-material.tar.gpg"}
        if stamp < cutoff and receipt.get("decryption_verified") is True and {
            row.get("file") for row in receipt.get("files", [])
        } == expected and {child.name for child in candidate.iterdir()} == expected | {"receipt.json"}:
            shutil.rmtree(candidate)
            removed += 1
    print(f"Expired verified generations removed: {removed}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--key-file", required=True, type=Path)
    parser.add_argument("--operator-material", required=True, type=Path,
                        help="Private Outline bootstrap directory, including the offline CA key")
    parser.add_argument("--retention-days", type=int)
    args = parser.parse_args()
    out = args.output.resolve()
    key = args.key_file.resolve()
    operator = args.operator_material.resolve()
    if (MODULE / "inventory.tf").is_file() and any(
        path.is_relative_to(MODULE.parents[1]) for path in (out, key, operator)
    ):
        parser.error("Keep backups and private material outside the module")
    if out.exists() or args.key_file.is_symlink() or key.stat().st_mode & 0o077:
        parser.error("Use a new output directory and mode 0600 for the key")
    if args.retention_days is not None and (
        args.retention_days < 7
        or not re.fullmatch(r"backup-[0-9]{8}T[0-9]{6}Z", out.name)
        or out.parent.stat().st_mode & 0o077
    ):
        parser.error("Retention requires a private scheduled backup directory and at least seven days")
    if operator.stat().st_mode & 0o077:
        parser.error("Operator material must be private")
    os.umask(0o077)
    out.mkdir()
    ssh = [
        "ssh", "-o", f"UserKnownHostsFile={Path.home() / '.ssh/known_hosts'}",
        "-o", "StrictHostKeyChecking=yes", "-o", "BatchMode=yes", "pve",
    ]
    exports = [
        (name, ssh + [shlex.join(["pct", "exec", str(ct), "--", *command])])
        for name, ct, command in EXPORTS
    ]
    exports.append(("operator-material.tar", [
        "tar", "-C", str(operator), "-cf", "-", "ca.key", "private/ca.pem",
        "login.json", "outline.env",
    ]))
    receipt = []
    for name, producer in exports:
        receipt.append(encrypted_capture(producer, out / (name + ".gpg"), key))
    (out / "receipt.json").write_text(json.dumps({
        "observed_at_utc": datetime.now(timezone.utc).isoformat(),
        "decryption_verified": True, "files": receipt,
    }, indent=2) + "\n")
    print(f"Verified encrypted archives: {len(receipt)}")
    if args.retention_days is not None:
        prune(out.parent, out, args.retention_days)


if __name__ == "__main__":
    main()
