"""Switch all four CRMAPI upstream locations to the verified candidate."""
from pathlib import Path
import subprocess
import time
import urllib.error
import urllib.request

VHOST = Path("/etc/nginx/sites-available/infra-svc01.mailerblend.com.conf")
OLD = "proxy_pass http://192.168.1.118:18088/"
NEW = "proxy_pass http://192.168.1.118:18091/"


def activate(text):
    stage = VHOST.with_suffix(".parallel-stage")
    stage.write_text(text)
    stage.replace(VHOST)
    subprocess.run(["nginx", "-t"], check=True)
    subprocess.run(["systemctl", "reload", "nginx"], check=True)


def main():
    original = VHOST.read_text()
    if original.count(OLD) != 4 or NEW in original:
        raise SystemExit("Unexpected CRM vhost upstream layout")
    try:
        urllib.request.urlopen("http://192.168.1.118:18091/v1/contacts?limit=1", timeout=4)
    except urllib.error.HTTPError as error:
        if error.code != 401:
            raise
    else:
        raise SystemExit("JWT protection is not active")
    backup = VHOST.with_name(VHOST.name + time.strftime(".before-parallel-%Y%m%dT%H%M%SZ", time.gmtime()))
    with backup.open("x") as handle:
        handle.write(original)
    try:
        activate(original.replace(OLD, NEW))
    except subprocess.CalledProcessError:
        activate(original)
        raise
    print(f"CRMAPI proxy switched. Rollback vhost: {backup}")


if __name__ == "__main__":
    main()
