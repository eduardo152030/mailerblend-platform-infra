"""Start, sample or roll back the reversible Budibase shutdown on PVE."""
from argparse import ArgumentParser
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import re
import subprocess
from urllib.error import HTTPError
from urllib.request import urlopen
from urllib.parse import unquote, urlsplit
from zoneinfo import ZoneInfo

STATE = Path("/root/crm-legacy-observation-31.json")
NAMES = ("budibase-app", "budibase-couchdb", "budibase-redis")
MADRID = ZoneInfo("Europe/Madrid")
DOMAIN = "https://infra-svc01.mailerblend.com"


def call(*command):
    return subprocess.check_output(command, stderr=subprocess.DEVNULL, text=True)


def docker(*command, ct=618):
    return call("pct", "exec", str(ct), "--", "docker", *command)


def inspect(name):
    return json.loads(docker("inspect", name))[0]


def http(path):
    try:
        with urlopen(DOMAIN + path, timeout=8) as response:
            return response.status
    except HTTPError as error:
        return error.code


def verify_crm():
    if http("/_svc/health") != 200 or http("/_svc/v1/contacts") != 401:
        raise RuntimeError("CRM public services failed")


def save(state):
    temporary = STATE.with_suffix(".tmp")
    temporary.write_text(json.dumps(state, indent=2) + "\n")
    temporary.replace(STATE)


def rollback(state):
    for name in reversed(state["containers"]):
        config = state["containers"][name]
        if inspect(name)["Id"] != config["id"]:
            raise RuntimeError("Container identity changed")
        docker("update", "--restart", config["restart"], name)
        docker("start", name)
    verify_crm()
    state["status"] = "rolled_back"
    save(state)


def redis_exclusive():
    app = inspect("budibase-app")
    redis = inspect("budibase-redis")
    if any(redis["NetworkSettings"].get("Ports", {}).values()):
        return False
    addresses = {network["IPAddress"] for network in app["NetworkSettings"]["Networks"].values()
                 if network.get("IPAddress")}
    values = dict(item.split("=", 1) for item in app["Config"]["Env"])
    url = urlsplit(values["REDIS_URL"])
    args = ["pct", "exec", "618", "--", "docker", "exec"]
    environment = os.environ.copy()
    if url.password:
        # Pass the credential through stdin to a shell inside the Redis container.
        args.extend(["-i", "budibase-redis", "sh", "-c",
                     "IFS= read -r REDISCLI_AUTH; export REDISCLI_AUTH; exec redis-cli CLIENT LIST"])
        listing = subprocess.check_output(args, text=True, input=unquote(url.password)+"\n",
                                          stderr=subprocess.DEVNULL, env=environment)
    else:
        listing = docker("exec", "budibase-redis", "redis-cli", "CLIENT", "LIST")
    clients = []
    for line in listing.splitlines():
        fields = dict(item.split("=", 1) for item in line.split() if "=" in item)
        if fields.get("cmd") == "client|list":
            continue
        clients.append(fields["addr"].rsplit(":", 1)[0])
    return bool(clients) and all(address in addresses for address in clients)


def start(receipt):
    if STATE.exists():
        raise RuntimeError("An observation receipt already exists")
    verified = json.loads(receipt.read_text())
    if verified.get("clone") != 9619 or verified.get("result") != "PASS":
        raise ValueError("Missing verified recovery")
    directory = Path(verified["export"]).resolve()
    if not re.fullmatch(r"/mnt/storage/crm-legacy-final[.][A-Za-z0-9]+", str(directory)):
        raise ValueError("Invalid legacy artifacts directory")
    subprocess.run(["sha256sum", "-c", "SHA256SUMS"], cwd=directory, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    verify_crm()
    config = {}
    names = NAMES if redis_exclusive() else NAMES[:2]
    if names != NAMES:
        print("Redis se conserva activo por uso externo o exclusividad sin verificar")
    for name in names:
        container = inspect(name)
        policy = container["HostConfig"]["RestartPolicy"]
        restart = policy["Name"] or "no"
        if policy["MaximumRetryCount"]:
            restart += ":" + str(policy["MaximumRetryCount"])
        if not container["State"]["Running"]:
            raise RuntimeError("Unexpected legacy state")
        config[name] = {"id": container["Id"], "restart": restart}
    state = {"status": "stopping", "containers": config}
    save(state)
    try:
        for name in names:
            docker("update", "--restart", "no", name)
            docker("stop", name)
        verify_crm()
    except Exception:
        rollback(state)
        raise
    now = datetime.now(timezone.utc)
    end = now + timedelta(hours=24)
    state.update(status="observing", start=now.isoformat(), end=end.isoformat())
    save(state)
    print("Inicio", now.astimezone(MADRID).isoformat(timespec="seconds"))
    print("Fin mínimo", end.astimezone(MADRID).isoformat(timespec="seconds"))


def sample(state):
    if state["status"] != "observing":
        raise RuntimeError("No active observation")
    verify_crm()
    for name in state["containers"]:
        if inspect(name)["State"]["Running"]:
            raise RuntimeError("Legacy container returned unexpectedly")
    with urlopen("http://192.168.1.110:9090/api/v1/alerts", timeout=8) as response:
        alerts = json.load(response)["data"]["alerts"]
    for alert in alerts:
        labels = alert["labels"]
        if alert["state"] != "firing":
            continue
        if labels.get("alertname") == "ApplicationContainerMissing" and labels.get("name") == "budibase-app":
            continue
        if labels.get("service") in {"infra-composable-crm", "infra-pulpo", "infra-mail"}:
            raise RuntimeError("Related monitoring alert")
    consumers = ["crm-api"]
    n8n = [name for name in docker("ps", "--format", "{{.Names}}", ct=619).splitlines() if "n8n" in name.lower()]
    if not n8n:
        raise RuntimeError("Unable to check n8n")
    for ct, names in ((618, consumers), (619, n8n)):
        for name in names:
            result = subprocess.run(["pct", "exec", str(ct), "--", "docker", "logs", "--since",
                                     state["start"], name], capture_output=True, text=True, check=True)
            lines = (result.stdout + result.stderr).splitlines()
            if any(re.search(r"budibase|couchdb|budibase.redis", line, re.I)
                   and re.search(r"error|refused|timeout|failed|unreachable", line, re.I) for line in lines):
                raise RuntimeError("Potential legacy consumer in logs")
    print("PASS: legacy stopped, public CRM and related alerts and logs checked")


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("start", "sample", "rollback"))
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    os.umask(0o077)
    if args.action == "start":
        if not args.receipt:
            parser.error("Need verified recovery receipt")
        start(args.receipt)
    else:
        state = json.loads(STATE.read_text())
        if args.action == "sample":
            sample(state)
        else:
            rollback(state)


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        raise SystemExit("Observation failed: " + type(error).__name__) from None
