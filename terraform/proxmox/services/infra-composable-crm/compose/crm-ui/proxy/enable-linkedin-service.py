"""Expose the token-authenticated machine importer at one exact path."""
from pathlib import Path
import subprocess
import time
import urllib.request

VHOST = Path("/etc/nginx/sites-available/infra-svc01.mailerblend.com.conf")
PATH = "/_svc/v1/linkedin-sourcing/leads/import/service"


def activate(config):
    stage = VHOST.with_suffix(".linkedin-stage")
    stage.write_text(config)
    stage.replace(VHOST)
    subprocess.run(["nginx", "-t"], check=True)
    subprocess.run(["systemctl", "reload", "nginx"], check=True)


original = VHOST.read_text()
marker = "   location /_svc/ {"
if original.count(marker) != 1 or PATH in original:
    raise SystemExit("Unexpected CRM vhost layout")
exception = f"""   location = {PATH} {{
    limit_except POST {{ deny all; }}
    proxy_pass http://192.168.1.118:18088/v1/linkedin-sourcing/leads/import/service;
  }}

"""
req = urllib.request.Request(
    "http://192.168.1.118:18088/v1/linkedin-sourcing/leads/import/service",
    data=b'{"leads":[]}', headers={"Content-Type": "application/json"}
)
try:
    urllib.request.urlopen(req, timeout=5)
except urllib.error.HTTPError as exc:
    if exc.code != 401:
        raise
else:
    raise SystemExit("Importer allowed a request without its token")

backup = VHOST.with_name(VHOST.name + time.strftime(".before-linkedin-%Y%m%dT%H%M%SZ", time.gmtime()))
with backup.open("x") as handle:
    handle.write(original)
try:
    activate(original.replace(marker, exception + marker))
except subprocess.CalledProcessError:
    activate(original)
    raise
print(f"LinkedIn proxy active. Rollback vhost: {backup}")
