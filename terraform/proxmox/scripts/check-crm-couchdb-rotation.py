#!/usr/bin/env python3
"""Compare the effective Compose credentials without printing their values."""

import argparse
import hmac
import json
import os
import re
import secrets
import stat
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit


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


def persisted_couch_url(path, couch):
    private_file(path, "Entorno persistido de Budibase")
    text = path.read_text(encoding="utf-8")
    match = re.fullmatch(r"COUCH_DB_URL=(http://[A-Za-z0-9._~%:@/-]+)\n?", text)
    if not match:
        raise PreflightError("Entorno persistido: formato de URL no reconocido")
    url = urlsplit(match.group(1))
    if (url.username is None or url.password is None or url.port != 5984
            or not url.hostname or url.path not in ("", "/")):
        raise PreflightError("Entorno persistido: endpoint de CouchDB no reconocido")
    for key, value in zip(KEYS, (url.username, url.password)):
        if not hmac.compare_digest(couch[key].encode(), unquote(value).encode()):
            raise PreflightError("La URL persistida y los modelos Compose no coinciden")
    return url


def prepare_candidate(args, persisted):
    parent = args.prepare_candidate
    metadata = parent.lstat()
    if (not stat.S_ISDIR(metadata.st_mode) or metadata.st_uid != os.geteuid()
            or stat.S_IMODE(metadata.st_mode) != 0o700):
        raise PreflightError("El directorio de candidatos debe ser propio y de modo 0700")
    password = secrets.token_urlsafe(36)
    legacy_env = args.env_file.read_text(encoding="utf-8")
    candidate_env, changed = re.subn(
        r"(?m)^[ \t]*(?:export[ \t]+)?COUCHDB_PASSWORD[ \t]*=[^\n]*$",
        lambda _: f"COUCHDB_PASSWORD={password}", legacy_env,
    )
    if changed != 1:
        raise PreflightError("No se pudo reemplazar la asignación de CouchDB")
    app_model = json.loads(args.app_compose.read_text(encoding="utf-8"))
    app_model["services"]["budibase-app"]["environment"]["COUCHDB_PASSWORD"] = password

    with tempfile.TemporaryDirectory(prefix="crm-rotation-check-", dir=parent) as tmp:
        candidate = Path(tmp)
        endpoint = persisted.netloc.rsplit("@", 1)[-1]
        username = quote(unquote(persisted.username), safe="")
        candidate_url = persisted._replace(netloc=f"{username}:{password}@{endpoint}")
        files = {
            ".env": candidate_env,
            "compose.private.json": json.dumps(app_model, indent=2) + "\n",
            "budibase-data.env": f"COUCH_DB_URL={candidate_url.geturl()}\n",
        }
        for name, content in files.items():
            fd = os.open(candidate / name, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(fd, "w", encoding="utf-8") as output:
                output.write(content)
        couch = compose_environment(args.couch_compose, "couchdb", candidate / ".env")
        app = compose_environment(candidate / "compose.private.json", "budibase-app", Path("/dev/null"))
        if any(model.get("COUCHDB_PASSWORD") != password for model in (couch, app)):
            raise PreflightError("Compose no conserva el valor candidato")
        if couch.get("COUCHDB_USER") != app.get("COUCHDB_USER"):
            raise PreflightError("Los usuarios candidatos no coinciden")

        destination = Path(tempfile.mkdtemp(prefix="crm-rotation-candidate-", dir=parent))
        for name in files:
            (candidate / name).rename(destination / name)
    print(f"PASS: archivos candidatos privados generados en {destination}")


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
    if args.prepare_candidate and not args.app_persisted_env:
        raise PreflightError("Se requiere --app-persisted-env para preparar los tres candidatos")
    if args.app_persisted_env:
        persisted = persisted_couch_url(args.app_persisted_env, couch)
    if args.prepare_candidate:
        prepare_candidate(args, persisted)
    else:
        print("PASS: archivos privados y referencias Compose coincidentes")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env-file", type=Path, required=True)
    parser.add_argument("--couch-compose", type=Path, required=True)
    parser.add_argument("--app-compose", type=Path, required=True)
    parser.add_argument("--app-persisted-env", type=Path)
    parser.add_argument("--prepare-candidate", type=Path, metavar="DIRECTORIO_PRIVADO")
    args = parser.parse_args()
    for key in vars(args):
        path = getattr(args, key)
        if path is not None:
            setattr(args, key, path.absolute())
    try:
        run(args)
    except (OSError, KeyError, TypeError, ValueError, subprocess.TimeoutExpired):
        print("BLOCKED: no se pudo validar la entrada privada o el modelo Compose", file=sys.stderr)
        return 1
    except PreflightError as error:
        print(f"BLOCKED: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
