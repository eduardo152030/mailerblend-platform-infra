#!/usr/bin/env python3
"""Apply the reviewed CouchDB rotation inside CT618, with coordinated rollback."""

import argparse
import base64
import fcntl
import json
import os
from pathlib import Path
import re
import signal
import stat
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from urllib.parse import unquote, urlsplit


LEGACY = Path("/opt/infra-composable-crm/budibase")
D051 = Path("/opt/healthcheck-d051/budibase-app")
FIXED = ("budibase-redis", "crm-api", "supabase-db")
HELD = ("budibase-worker", "budibase-app-d051-original", "budibase-app-pre-recovery")
TARGETS = ("budibase-couchdb", "budibase-app")
PUBLIC = "https://infra-svc01.mailerblend.com"
LOCAL = "http://192.168.1.118:8080"
KEYS = ("COUCHDB_USER", "COUCHDB_PASSWORD")


class RotationError(Exception):
    """An invariant failure with a safe, fixed message."""


def require(condition, message):
    if not condition:
        raise RotationError(message)


def command(*args, timeout=120):
    process = subprocess.run(args, capture_output=True, timeout=timeout)
    require(process.returncode == 0, "Falló un comando de Docker, Compose o preflight")
    return process.stdout


def inspect(name):
    return json.loads(command("docker", "inspect", name))[0]


def identity(item):
    return item["Id"], item["State"]["Running"], item["State"]["StartedAt"]


def topology(item):
    mounts = sorted((m["Type"], m["Source"], m["Destination"], m["RW"]) for m in item["Mounts"])
    ports = item["HostConfig"].get("PortBindings")
    return item["Image"], mounts, sorted(item["NetworkSettings"]["Networks"]), ports


def environment(item):
    return dict(value.split("=", 1) for value in item["Config"]["Env"])


def compose(prefix, *args):
    return command(*prefix, *args)


def url_status(url, auth=None):
    headers = {}
    if auth:
        pair = ":".join(auth).encode()
        headers["Authorization"] = "Basic " + base64.b64encode(pair).decode()
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=8) as response:
            return response.status
    except urllib.error.HTTPError as error:
        return error.code
    except OSError:
        return 0


def public_health():
    return all(url_status(PUBLIC + path) == 200 for path in ("/builder/auth/login", "/_svc/health"))


def couch_auth(pair):
    ip = inspect(TARGETS[0])["NetworkSettings"]["Networks"]["nucleo_network"]["IPAddress"]
    return url_status(f"http://{ip}:5984/_all_dbs", pair) if ip else 0


def wait_until(check, seconds, message):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if check():
            return
        time.sleep(3)
    raise RotationError(message)


def app_ready():
    current = inspect(TARGETS[1])
    if current["State"].get("Health", {}).get("Status") != "healthy":
        return False
    try:
        with urllib.request.urlopen(LOCAL + "/api/system/status", timeout=8) as response:
            report = json.load(response)
        return report["version"] == "3.27.4" and report["health"]["passing"] and public_health()
    except (KeyError, ValueError, OSError):
        return False


def private_copy(source, destination):
    with destination.open("xb") as output:
        os.fchmod(output.fileno(), 0o600)
        output.write(source.read_bytes())


def install_atomic(source, destination, metadata, mode):
    with tempfile.NamedTemporaryFile(dir=destination.parent, prefix=".crm-rotation-", delete=False) as output:
        temporary = Path(output.name)
        try:
            output.write(source.read_bytes())
            output.flush()
            os.fchown(output.fileno(), metadata.st_uid, metadata.st_gid)
            os.fchmod(output.fileno(), mode)
            os.fsync(output.fileno())
            os.replace(temporary, destination)
            directory = os.open(destination.parent, os.O_DIRECTORY)
            try:
                os.fsync(directory)
            finally:
                os.close(directory)
        finally:
            temporary.unlink(missing_ok=True)


def app_data(item):
    matches = [Path(m["Source"]) for m in item["Mounts"] if m["Destination"] == "/data" and m["Type"] == "volume"]
    require(len(matches) == 1, "Montaje /data de Budibase inesperado")
    source = matches[0].resolve(strict=True)
    require(source.parent.parent == Path("/var/lib/docker/volumes") and source.name == "_data",
            "Volumen persistido fuera de Docker")
    return source / ".env"


def labels_match(item, project, service, file):
    labels = item["Config"]["Labels"]
    return (
        labels.get("com.docker.compose.project") == project
        and labels.get("com.docker.compose.service") == service
        and labels.get("com.docker.compose.project.config_files") == str(file)
    )


def rotate(stage, prepare_only):
    couch_file, d051_file = LEGACY / "docker-compose.yml", D051 / "compose.private.json"
    couch = ("docker", "compose", "--project-directory", str(LEGACY), "-p", "budibase",
             "--env-file", str(LEGACY / ".env"), "-f", str(couch_file))
    app = ("docker", "compose", "--project-directory", str(D051), "-p", "d051-budibase-app",
           "--env-file", "/dev/null", "-f", str(d051_file))
    before = {name: inspect(name) for name in TARGETS + FIXED + HELD}
    require(all(before[name]["State"]["Running"] for name in TARGETS + FIXED)
            and not any(before[name]["State"]["Running"] for name in HELD),
            "Servicios activos u originales detenidos no coinciden con el runbook")
    require(labels_match(before[TARGETS[0]], "budibase", "couchdb", couch_file)
            and labels_match(before[TARGETS[1]], "d051-budibase-app", "budibase-app", d051_file),
            "Etiquetas Compose no coinciden con el runbook")
    require(before[TARGETS[1]]["Config"]["User"] in ("", "0", "root"), "Runner D051 no es root")
    for prefix, service, container in ((couch, "couchdb", TARGETS[0]), (app, "budibase-app", TARGETS[1])):
        model = json.loads(compose(prefix, "config", "--format", "json"))
        image = model["services"][service]["image"]
        resolved = json.loads(command("docker", "image", "inspect", image))[0]["Id"]
        require(resolved == before[container]["Image"], "La referencia Compose cambió de imagen")
    require(all("nucleo_network" in before[name]["NetworkSettings"]["Networks"] for name in TARGETS),
            "No se encuentra la red esperada")
    active = environment(before[TARGETS[0]])
    old = tuple(active[key] for key in KEYS)
    require(tuple(environment(before[TARGETS[1]])[key] for key in KEYS) == old,
            "La configuración activa de los consumidores no coincide")
    require(couch_auth(old) == 200 and app_ready(), "Baseline CouchDB, D051 o HTTPS no disponible")
    print("PASS: baseline productiva, topología y autenticación actual.", flush=True)

    names = (".env", "compose.private.json", "budibase-data.env")
    files = (LEGACY / ".env", d051_file, app_data(before[TARGETS[1]]))
    metadata = [path.lstat() for path in files]
    require(all(stat.S_ISREG(info.st_mode) for info in metadata), "Fuente no regular")
    for name, path in zip(names, files):
        private_copy(path, stage / name)
    private_copy(couch_file, stage / "docker-compose.yml")
    command(sys.executable, str(stage / "check-crm-couchdb-rotation.py"),
            "--env-file", str(stage / names[0]), "--couch-compose", str(stage / "docker-compose.yml"),
            "--app-compose", str(stage / names[1]), "--app-persisted-env", str(stage / names[2]),
            "--prepare-candidate", str(stage), "--normalize-legacy-env")
    candidates = list(stage.glob("crm-rotation-candidate-*"))
    require(len(candidates) == 1, "Se esperaba un candidato privado")
    candidate = candidates[0]
    parsed = urlsplit((candidate / names[2]).read_text().strip().partition("=")[2])
    new = unquote(parsed.username or ""), unquote(parsed.password or "")
    require(new[0] == old[0] and new[1] and new[1] != old[1], "Cambio de identidad CouchDB inesperado")
    require(all(path.read_bytes() == (stage / name).read_bytes() for name, path in zip(names, files)),
            "Las fuentes cambiaron durante la preparación")
    print("PASS: originales privados y tres candidatos coherentes.", flush=True)
    if prepare_only:
        return

    def verify_unchanged():
        require(all(identity(inspect(name)) == identity(before[name]) for name in FIXED + HELD),
                "Cambió un servicio protegido")
        require(all(topology(inspect(name)) == topology(before[name]) for name in TARGETS),
                "Cambió la imagen, red o montaje de un objetivo")

    def recreate(prefix, service):
        compose(prefix, "up", "-d", "--pull", "never", "--no-deps", "--force-recreate", service)

    started = time.monotonic()
    try:
        compose(app, "stop", "budibase-app")
        for name, path, info in zip(names, files, metadata):
            install_atomic(candidate / name, path, info, 0o600)
        recreate(couch, "couchdb")
        wait_until(lambda: couch_auth(new) == 200, 100, "CouchDB no acepta la credencial candidata")
        require(couch_auth(old) == 401, "CouchDB no rechazó la credencial anterior")
        print("PASS: CouchDB candidato 200 y credencial anterior 401.", flush=True)
        recreate(app, "budibase-app")
        wait_until(app_ready, 300, "D051 o HTTPS no recuperó readiness")
        verify_unchanged()
        applied = {name: identity(inspect(name)) for name in TARGETS}
        compose(couch, "up", "-d", "--pull", "never", "--no-deps", "couchdb")
        compose(app, "up", "-d", "--pull", "never", "--no-deps", "budibase-app")
        require(all(identity(inspect(name)) == applied[name] for name in TARGETS),
                "La segunda aplicación recreó un servicio")
        require(app_ready() and couch_auth(new) == 200 and couch_auth(old) == 401,
                "Falló la verificación posterior a la segunda aplicación")
        verify_unchanged()
    except BaseException:
        print("ROLLBACK: restauración coordinada de configuración y servicios.", file=sys.stderr, flush=True)
        try:
            compose(app, "stop", "budibase-app")
        except (RotationError, subprocess.SubprocessError):
            pass
        for name, path, info in zip(names, files, metadata):
            install_atomic(stage / name, path, info, stat.S_IMODE(info.st_mode))
        recreate(couch, "couchdb")
        wait_until(lambda: couch_auth(old) == 200, 100, "Rollback: CouchDB no acepta el valor original")
        recreate(app, "budibase-app")
        wait_until(app_ready, 300, "Rollback: D051 no recuperó readiness")
        verify_unchanged()
        print("ROLLBACK PASS: CouchDB, D051 y HTTPS recuperados.", file=sys.stderr, flush=True)
        raise
    print(f"PASS: D051 healthy, HTTPS 200, idempotencia y servicios protegidos; intervención={round(time.monotonic()-started)}s.",
          flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("prepare", "execute"))
    parser.add_argument("stage", type=Path)
    args = parser.parse_args()
    require(Path("/etc/hostname").read_text().strip() == "infra-composable-crm", "Host inesperado")
    require(os.geteuid() == 0, "La receta requiere root en CT618")
    require(bool(re.fullmatch(r"/root/crm-couchdb-rotation\.[A-Za-z0-9]+", str(args.stage))),
            "Ruta privada inesperada")
    require(args.stage.is_dir() and stat.S_IMODE(args.stage.stat().st_mode) == 0o700,
            "Staging no privado")
    os.umask(0o077)
    with open("/run/lock/crm-618-couchdb-rotation.lock", "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        rotate(args.stage, args.mode == "prepare")


def interrupted(_signal, _frame):
    raise RotationError("Interrupción de la operación")


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, interrupted)
    signal.signal(signal.SIGHUP, interrupted)
    try:
        main()
    except RotationError as error:
        print(f"BLOCKED: {error}", file=sys.stderr)
        sys.exit(1)
    except Exception:
        print("BLOCKED: error de ejecución; salida privada omitida.", file=sys.stderr)
        sys.exit(1)
