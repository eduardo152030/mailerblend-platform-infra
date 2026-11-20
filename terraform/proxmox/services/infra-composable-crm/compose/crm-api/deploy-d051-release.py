"""Roll out a built CRMAPI image with private input settings and rollback."""
import json
import os
import pathlib
import subprocess
import sys
import time
import urllib.request

ROOT = pathlib.Path("/opt/healthcheck-d051/crm-api")
CONFIG = ROOT / "compose.private.json"
PROJECT = "d051-crm-api"


def write_private(path, value):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w") as handle:
        json.dump(value, handle)


def run(path):
    command = ["docker", "compose", "--env-file", "/dev/null", "-p", PROJECT, "-f", str(path)]
    subprocess.run(command + ["config", "--quiet"], check=True)
    subprocess.run(command + ["up", "-d", "--no-build", "--wait", "--wait-timeout", "75"], check=True)
    with urllib.request.urlopen("http://192.168.1.118:18088/ready", timeout=8) as response:
        if response.status != 200:
            raise RuntimeError("CRMAPI readiness failed")


def main():
    if len(sys.argv) not in (2, 3) or (len(sys.argv) == 3 and sys.argv[2] != "--fast-start"):
        raise SystemExit("Usage: deploy-d051-release.py IMAGE [--fast-start]")
    image = sys.argv[1]
    settings = json.load(sys.stdin)
    if not settings or settings.keys() - {
        "CRM_LINKEDIN_IMPORT_TOKEN", "CRM_AUTH_ENABLED", "CRM_AUTH_ISSUER", "CRM_AUTH_JWT_SECRET", "CRM_UI_ORIGIN"
    }:
        raise SystemExit("Unexpected release settings")
    config = json.loads(CONFIG.read_text())
    service = config["services"]["crm-api"]
    previous = subprocess.check_output(
        ["docker", "inspect", "--format", "{{.Image}}", "crm-api"], text=True
    ).strip()
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    rollback_image = f"infra-composable-crm/crm-api:rollback-{stamp.lower()}"
    subprocess.run(["docker", "tag", previous, rollback_image], check=True)
    backup = ROOT / f"compose.before-{stamp}.json"
    service["image"] = rollback_image
    service.pop("build", None)
    write_private(backup, config)
    service["image"] = image
    service["environment"].update(settings)
    if len(sys.argv) == 3:
        service["healthcheck"].update(start_period="15s", start_interval="1s")
    stage = ROOT / f"compose.release-{stamp}.json"
    write_private(stage, config)
    stage.replace(CONFIG)
    try:
        run(CONFIG)
    except Exception:
        write_private(stage, json.loads(backup.read_text()))
        stage.replace(CONFIG)
        run(CONFIG)
        raise
    print(f"CRMAPI ready. Rollback compose: {backup}")


if __name__ == "__main__":
    main()
