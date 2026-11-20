#!/usr/bin/env python3
"""Validate CouchDB and Budibase D051 on the network-isolated CT9618 only."""

import base64
import http.cookiejar
import json
import os
from pathlib import Path
import secrets
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request


BASE = "http://192.168.1.118:8080"
D051 = Path("/opt/healthcheck-d051/budibase-app/compose.private.json")


def command(*args, env=None, timeout=30):
    result = subprocess.run(args, capture_output=True, check=True, env=env, timeout=timeout)
    return result.stdout


def inspect(container):
    return json.loads(command("docker", "inspect", container))[0]


def request(opener, url, body=None, headers=None):
    with opener.open(urllib.request.Request(url, body, headers or {}), timeout=8) as response:
        return json.load(response)


def verify_isolation():
    if socket.gethostname() != "crm-rehearsal-9618":
        raise RuntimeError("host is not the rehearsal CT")
    for family in ("-4", "-6"):
        if json.loads(command("ip", family, "-j", "route", "show", "default")):
            raise RuntimeError("default route present")
    link = json.loads(command("ip", "-j", "link", "show", "dev", "eth0"))[0]
    if "LOWER_UP" in link["flags"]:
        raise RuntimeError("external link active")


def verify_couch(opener):
    couch = inspect("budibase-couchdb")
    environment = dict(value.split("=", 1) for value in couch["Config"]["Env"])
    credential = f'{environment["COUCHDB_USER"]}:{environment["COUCHDB_PASSWORD"]}'
    headers = {"Authorization": "Basic " + base64.b64encode(credential.encode()).decode()}
    address = next(
        network["IPAddress"] for network in couch["NetworkSettings"]["Networks"].values()
        if network.get("IPAddress")
    )
    databases = request(opener, f"http://{address}:5984/_all_dbs", headers=headers)
    if "global-db" not in databases:
        raise RuntimeError("Budibase database missing")
    print(f"PASS: CouchDB autenticado; bases enumeradas={len(databases)}.", flush=True)


def wait_for_budibase(opener):
    deadline = time.monotonic() + 300
    while time.monotonic() < deadline:
        try:
            status = request(opener, BASE + "/api/system/status")
            health = inspect("budibase-app")["State"]["Health"]["Status"]
            if status["version"] == "3.27.4" and status["health"]["passing"] and health == "healthy":
                return
        except (KeyError, ValueError, OSError, subprocess.SubprocessError):
            pass
        time.sleep(5)
    raise RuntimeError("Budibase D051 did not become healthy")


def contains_email(value, email):
    if isinstance(value, dict):
        return value.get("email") == email or any(contains_email(item, email) for item in value.values())
    if isinstance(value, list):
        return any(contains_email(item, email) for item in value)
    return False


def verify_login():
    opener = urllib.request.build_opener(
        urllib.request.ProxyHandler({}),
        urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()),
    )
    verify_isolation()
    budibase = inspect("budibase-app")
    labels = budibase["Config"]["Labels"]
    if (labels["com.docker.compose.project"] != "d051-budibase-app"
            or labels["com.docker.compose.service"] != "budibase-app"
            or labels["com.docker.compose.project.config_files"] != str(D051)):
        raise RuntimeError("unexpected restored Compose identity")
    verify_couch(opener)
    wait_for_budibase(opener)
    print("PASS: Budibase D051 restaurado, healthy antes de la prueba de login.", flush=True)

    email = f"crm-restore-{secrets.token_hex(8)}@example.invalid"
    password = secrets.token_urlsafe(36)
    environment = dict(os.environ, CRM_FIXTURE_EMAIL=email, CRM_FIXTURE_PASSWORD=password)
    with tempfile.TemporaryDirectory(prefix="crm-restore-login-") as temp:
        override = Path(temp) / "fixture.yml"
        override.write_text(
            "services:\n  budibase-app:\n    environment:\n"
            "      BB_ADMIN_USER_EMAIL: ${CRM_FIXTURE_EMAIL:?}\n"
            "      BB_ADMIN_USER_PASSWORD: ${CRM_FIXTURE_PASSWORD:?}\n",
            encoding="utf-8",
        )
        command(
            "docker", "compose", "--project-directory", str(D051.parent), "-p", "d051-budibase-app",
            "--env-file", "/dev/null", "-f", str(D051), "-f", str(override),
            "up", "-d", "--no-deps", "budibase-app", env=environment, timeout=180,
        )
        wait_for_budibase(opener)
        body = json.dumps({"username": email, "password": password}).encode()
        login = request(opener, BASE + "/api/global/auth/default/login", body, {"Content-Type": "application/json"})
        user = request(opener, BASE + "/api/global/self")
        if not login.get("userId") or not contains_email(user, email):
            raise RuntimeError("synthetic authenticated identity not verified")
    print("PASS: login sintético e identidad de sesión verificados en CT9618.", flush=True)


if __name__ == "__main__":
    try:
        verify_login()
    except Exception:
        print("BLOCKED: validación aislada fallida; valores y respuestas privadas omitidos.", file=sys.stderr)
        sys.exit(1)
