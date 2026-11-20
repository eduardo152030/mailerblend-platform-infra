"""Stage an authenticated CRMAPI release without replacing the active service."""
import json
import os
from pathlib import Path
import subprocess
import sys
import urllib.error
import urllib.request

SOURCE = Path("/opt/healthcheck-d051/crm-api/compose.private.json")
ROOT = Path("/opt/crm-api-parallel")
CONFIG = ROOT / "compose.private.json"


def main():
    image, = sys.argv[1:]
    data = json.loads(SOURCE.read_text())
    service = data["services"].pop("crm-api")
    if service["environment"].get("CRM_AUTH_ENABLED") != "1":
        raise SystemExit("JWT must be enabled in the source release")
    ports = service["ports"]
    if len(ports) != 1 or ports[0].get("published") != "18088":
        raise SystemExit("Unexpected CRMAPI port configuration")
    ports[0]["published"] = "18091"
    service["container_name"] = "crm-api-parallel"
    service["image"] = image
    service["healthcheck"].update(start_period="15s", start_interval="1s")
    data["services"]["crm-api-parallel"] = service
    ROOT.mkdir(mode=0o700, exist_ok=True)
    fd = os.open(CONFIG, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w") as handle:
        json.dump(data, handle)
    command = ["docker", "compose", "--env-file", "/dev/null", "-p", "crm-api-parallel", "-f", str(CONFIG)]
    try:
        subprocess.run(command + ["up", "-d", "--no-build", "--wait", "--wait-timeout", "45"], check=True)
        base = "http://192.168.1.118:18091"
        with urllib.request.urlopen(base + "/ready", timeout=5) as response:
            if response.status != 200:
                raise RuntimeError("CRMAPI readiness failed")
        try:
            urllib.request.urlopen(base + "/v1/contacts?limit=1", timeout=5)
        except urllib.error.HTTPError as error:
            if error.code != 401:
                raise
        else:
            raise RuntimeError("Candidate allowed anonymous contacts")
    except Exception:
        subprocess.run(command + ["stop"], check=True)
        raise
    print("Candidate API healthy and anonymous access rejected.")


if __name__ == "__main__":
    main()
