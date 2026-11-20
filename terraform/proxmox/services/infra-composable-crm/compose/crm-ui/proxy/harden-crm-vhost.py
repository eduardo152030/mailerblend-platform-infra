"""Apply security headers and a rate limit to the CRM user API."""
from pathlib import Path
import subprocess
import time

VHOST = Path("/etc/nginx/sites-available/infra-svc01.mailerblend.com.conf")
RATE = Path("/etc/nginx/conf.d/crm-api-rate.conf")
RATE_DEFINITION = "limit_req_zone $binary_remote_addr zone=crm_api_user:10m rate=30r/s;\n"
HEADERS = """  add_header Strict-Transport-Security "max-age=31536000" always;
  add_header Content-Security-Policy "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; font-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'" always;
  add_header X-Frame-Options DENY always;
  add_header Referrer-Policy strict-origin-when-cross-origin always;
  add_header X-Content-Type-Options nosniff always;
"""


def render(config):
    server = "  server_name infra-svc01.mailerblend.com;\n"
    api_block = "   location /_svc/ {\n"
    ui_block = "  location / {\n"
    if config.count(server) != 2 or any(config.count(mark) != 1 for mark in (api_block, ui_block)):
        raise ValueError("Unexpected CRM vhost layout")
    if any(mark in config for mark in ("zone=crm_api_user", "add_header Strict-Transport-Security")):
        raise ValueError("CRM hardening already configured")
    return (
        config.replace(server, server + HEADERS, 1)
        .replace(api_block, api_block + "    limit_req zone=crm_api_user burst=90 nodelay;\n    limit_req_status 429;\n")
        .replace(ui_block, ui_block + "    proxy_hide_header Content-Security-Policy;\n")
    )


def install(config):
    stage = VHOST.with_suffix(".hardening-stage")
    stage.write_text(config)
    stage.replace(VHOST)
    subprocess.run(["nginx", "-t"], check=True)
    subprocess.run(["systemctl", "reload", "nginx"], check=True)


def main():
    original = VHOST.read_text()
    candidate = render(original)
    backup = VHOST.with_name(VHOST.name + time.strftime(".before-hardening-%Y%m%dT%H%M%SZ", time.gmtime()))
    with backup.open("x") as handle:
        handle.write(original)
    if RATE.exists():
        if RATE.read_text() != RATE_DEFINITION:
            raise SystemExit("Unexpected CRM rate limit definition")
    else:
        with RATE.open("x") as handle:
            handle.write(RATE_DEFINITION)
    try:
        install(candidate)
    except subprocess.CalledProcessError:
        install(original)
        raise
    print(f"CRM proxy hardened. Rollback vhost: {backup}")


if __name__ == "__main__":
    main()
