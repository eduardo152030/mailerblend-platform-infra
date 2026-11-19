#!/usr/bin/env python3
"""Compare the effective Compose credentials without printing their values."""

import argparse
import hmac
import json
import os
import stat
import subprocess
import sys
from pathlib import Path


KEYS = ("COUCHDB_USER", "COUCHDB_PASSWORD")


class PreflightError(Exception):
    """A preflight failure with a message safe to print."""


def private_file(path, label):
    metadata = path.lstat()
    if not stat.S_ISREG(metadata.st_mode):
        raise PreflightError(f"{label}: se requiere un archivo regular sin enlaces")
    if stat.S_IMODE(metadata.st_mode) != 0o600:
        raise PreflightError(f"{label}: se requiere modo 0600")


def compose_environment(compose, service, env_file):
    command = [
        "docker", "compose", "--project-directory", str(compose.parent),
        "--env-file", str(env_file), "-f", str(compose), "config", "--format", "json",
    ]
    result = subprocess.run(
        command, capture_output=True, check=False, timeout=30, cwd=compose.parent,
    )
    if result.returncode:
        raise PreflightError("Compose no pudo renderizar uno de los modelos")
    return json.loads(result.stdout)["services"][service]["environment"]


def run(args):
    private_file(args.env_file, "Entorno CouchDB")
    private_file(args.app_compose, "Compose privado D051")
    if not args.couch_compose.is_file():
        raise PreflightError("Compose CouchDB: archivo ausente")
    with args.env_file.open(encoding="utf-8") as env:
        assignments = [line.partition("=")[0].strip().removeprefix("export ").strip()
                       for line in env if "=" in line]
    if any(assignments.count(key) != 1 for key in KEYS):
        raise PreflightError("Entorno CouchDB: debe haber una asignación por cada clave")
    # Compose reads the legacy env for interpolation. Shell overrides would
    # defeat this comparison, so require callers to unset those keys first.
    if any(key in os.environ for key in KEYS):
        raise PreflightError("El entorno del proceso contiene overrides de CouchDB")
    couch = compose_environment(args.couch_compose, "couchdb", args.env_file)
    app = compose_environment(args.app_compose, "budibase-app", Path("/dev/null"))
    for key in KEYS:
        source, consumer = couch.get(key), app.get(key)
        if not isinstance(source, str) or not isinstance(consumer, str) or not source or not consumer:
            raise PreflightError("Falta una referencia de credencial en los modelos")
        if not hmac.compare_digest(source.encode(), consumer.encode()):
            raise PreflightError("Los modelos CouchDB y D051 no coinciden")
    print("PASS: archivos privados y referencias Compose coincidentes")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env-file", type=Path, required=True)
    parser.add_argument("--couch-compose", type=Path, required=True)
    parser.add_argument("--app-compose", type=Path, required=True)
    args = parser.parse_args()
    for key in vars(args):
        path = getattr(args, key)
        setattr(args, key, path.absolute())
    try:
        run(args)
    except (OSError, KeyError, TypeError, UnicodeError, json.JSONDecodeError, subprocess.TimeoutExpired):
        print("BLOCKED: no se pudo validar la entrada privada o el modelo Compose", file=sys.stderr)
        return 1
    except PreflightError as error:
        print(f"BLOCKED: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
