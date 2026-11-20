"""Switch UI and API from Basic Auth to the CRMAPI JWT gate."""
from pathlib import Path
import subprocess
import time
import urllib.request
import urllib.error

VHOST = Path("/etc/nginx/sites-available/infra-svc01.mailerblend.com.conf")
DOMAIN = "infra-svc01.mailerblend.com"
RATE = Path("/etc/nginx/conf.d/crm-auth-rate.conf")
BASIC = '    auth_basic "CRM";\n    auth_basic_user_file /etc/nginx/crm-ui.htpasswd;\n'
LOCATIONS = """  location = /auth/v1/token {
    limit_req zone=crm_auth_login burst=8 nodelay;
    limit_req_status 429;
    limit_except POST { deny all; }
    proxy_pass http://192.168.1.118:18090/token;
  }
  location = /auth/v1/user {
    limit_except GET { deny all; }
    proxy_pass http://192.168.1.118:18090/user;
  }
  location = /auth/v1/logout {
    limit_except POST { deny all; }
    proxy_pass http://192.168.1.118:18090/logout;
  }
  location ^~ /auth/ { return 404; }

"""


def activate(config):
    staged = VHOST.with_suffix(".auth-stage")
    staged.write_text(config)
    staged.replace(VHOST)
    subprocess.run(["nginx", "-t"], check=True)
    subprocess.run(["systemctl", "reload", "nginx"], check=True)


def main():
    current = VHOST.read_text()
    if current.count(BASIC) != 2 or "/auth/v1/token" in current:
        raise SystemExit("Expected existing UI and API Basic Auth")
    for machine in ("intake/webform", "linkedin-sourcing/leads/import/service"):
        if f"location = /_svc/v1/{machine}" not in current:
            raise SystemExit("Expected both machine routes")
    try:
        urllib.request.urlopen("http://192.168.1.118:18088/v1/contacts?limit=1", timeout=5)
    except urllib.error.HTTPError as exc:
        if exc.code != 401:
            raise
    else:
        raise SystemExit("CRMAPI JWT gate not active")
    with urllib.request.urlopen("http://192.168.1.118:18090/health", timeout=5) as res:
        if res.status != 200:
            raise SystemExit("GoTrue unavailable")
    backup = VHOST.with_name(VHOST.name + time.strftime(".before-gotrue-%Y%m%dT%H%M%SZ", time.gmtime()))
    with backup.open("x") as handle:
        handle.write(current)
    if not RATE.exists():
        with RATE.open("x") as handle:
            handle.write("limit_req_zone $binary_remote_addr zone=crm_auth_login:10m rate=5r/s;\n")
    new = current.replace(BASIC, "").replace("  location / {", LOCATIONS + "  location / {", 1)
    try:
        activate(new)
    except subprocess.CalledProcessError:
        activate(current)
        raise
    print(f"GoTrue proxy active. Rollback vhost: {backup}")


if __name__ == "__main__":
    main()
