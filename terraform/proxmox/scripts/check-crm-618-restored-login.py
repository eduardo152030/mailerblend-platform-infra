#!/usr/bin/env python3
"""Validate CouchDB and Budibase D051 on the network-isolated CT9618 only."""

import base64
import http.cookiejar
import json
import os
from pathlib import Path
import re
import secrets
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request


BASE = "http://192.168.1.118:8080"
D051 = Path("/opt/healthcheck-d051/budibase-app/compose.private.json")
stage = "isolation"


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


def contains_value(value, expected):
    if isinstance(value, dict):
        return any(contains_value(item, expected) for item in value.values())
    if isinstance(value, list):
        return any(contains_value(item, expected) for item in value)
    return value == expected


def check_synthetic_session(opener, cookies, email, password):
    body = json.dumps({"username": email, "password": password}).encode()
    login = request(opener, BASE + "/api/global/auth/default/login", body, {"Content-Type": "application/json"})
    user = request(opener, BASE + "/api/global/self")
    user_id = login.get("userId") if isinstance(login, dict) else None
    session = any(cookie.name == "budibase:auth" and cookie.value for cookie in cookies)
    email_match = contains_value(user, email)
    id_match = bool(user_id and contains_value(user, user_id))
    print(
        f"fixture_session_cookie={session} profile_email_matches={email_match} profile_id_matches={id_match}",
        flush=True,
    )
    if not session or not (email_match or id_match):
        raise RuntimeError("synthetic authenticated identity not verified")


def verify_login(recheck):
    global stage
    cookies = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(
        urllib.request.ProxyHandler({}),
        urllib.request.HTTPCookieProcessor(cookies),
    )
    verify_isolation()
    stage = "compose_identity"
    budibase = inspect("budibase-app")
    labels = budibase["Config"]["Labels"]
    configs = labels["com.docker.compose.project.config_files"]
    expected_config = str(D051)
    if recheck:
        expected_config = re.escape(expected_config) + r",/tmp/crm-restore-login-[a-z0-9_]+/fixture\.yml"
        valid_config = bool(re.fullmatch(expected_config, configs))
    else:
        valid_config = configs == expected_config
    if (labels["com.docker.compose.project"] != "d051-budibase-app"
            or labels["com.docker.compose.service"] != "budibase-app"
            or not valid_config):
        raise RuntimeError("unexpected restored Compose identity")
    stage = "couch_readiness"
    for attempt in range(30):
        try:
            verify_couch(opener)
            break
        except (KeyError, ValueError, OSError, StopIteration, subprocess.SubprocessError):
            if attempt == 29:
                raise
            time.sleep(4)
    stage = "d051_baseline"
    wait_for_budibase(opener)
    print("PASS: Budibase D051 restaurado, healthy antes de la prueba de login.", flush=True)

    if recheck:
        stage = "fixture_recheck"
        fixture_env = dict(value.split("=", 1) for value in budibase["Config"]["Env"])
        email = fixture_env.get("BB_ADMIN_USER_EMAIL", "")
        password = fixture_env.get("BB_ADMIN_USER_PASSWORD", "")
        if not re.fullmatch(r"crm-restore-[a-f0-9]{16}@example\.invalid", email) or not password:
            raise RuntimeError("synthetic credentials missing")
        check_synthetic_session(opener, cookies, email, password)
        print("PASS: login sintético e identidad de sesión verificados en CT9618.", flush=True)
        return

    email = f"crm-restore-{secrets.token_hex(8)}@example.invalid"
    password = secrets.token_urlsafe(36)
    environment = dict(os.environ, CRM_FIXTURE_EMAIL=email, CRM_FIXTURE_PASSWORD=password)
    started = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="crm-restore-login-") as temp:
        override = Path(temp) / "fixture.yml"
        override.write_text(
            "services:\n  budibase-app:\n    environment:\n"
            "      BB_ADMIN_USER_EMAIL: ${CRM_FIXTURE_EMAIL:?}\n"
            "      BB_ADMIN_USER_PASSWORD: ${CRM_FIXTURE_PASSWORD:?}\n",
            encoding="utf-8",
        )
        stage = "fixture_bootstrap"
        command(
            "docker", "compose", "--project-directory", str(D051.parent), "-p", "d051-budibase-app",
            "--env-file", "/dev/null", "-f", str(D051), "-f", str(override),
            "up", "-d", "--no-deps", "budibase-app", env=environment, timeout=180,
        )
        wait_for_budibase(opener)
        stage = "fixture_login"
        check_synthetic_session(opener, cookies, email, password)
    elapsed = round(time.monotonic() - started)
    print(f"PASS: login sintético e identidad en CT9618; recreación a login={elapsed}s.", flush=True)


if __name__ == "__main__":
    try:
        if sys.argv[1:] not in ([], ["--recheck-fixture"]):
            raise ValueError("unknown fixture check mode")
        verify_login(bool(sys.argv[1:]))
    except Exception as error:
        print(f"BLOCKED: etapa={stage}; tipo={type(error).__name__}; detalle privado omitido.", file=sys.stderr)
        sys.exit(1)
