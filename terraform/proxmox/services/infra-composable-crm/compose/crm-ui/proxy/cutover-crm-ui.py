"""Switch the CRM vhost UI location, preserving CRMAPI and TLS."""
import pathlib
import subprocess
import sys
import time

VHOST = pathlib.Path("/etc/nginx/sites-available/infra-svc01.mailerblend.com.conf")
LEGACY = "    proxy_pass http://192.168.1.118:8080;"
RELEASE = """    auth_basic "CRM";
    auth_basic_user_file /etc/nginx/crm-ui.htpasswd;
    proxy_set_header Authorization "";
    proxy_pass http://192.168.1.118:18089;"""

def activate(config):
    staged = VHOST.with_name(VHOST.name + ".ui-stage")
    staged.write_text(config)
    staged.replace(VHOST)
    subprocess.run(["nginx", "-t"], check=True)
    subprocess.run(["systemctl", "reload", "nginx"], check=True)

def main():
    action, = sys.argv[1:]
    old, new = {"apply": (LEGACY, RELEASE), "rollback": (RELEASE, LEGACY)}[action]
    original = VHOST.read_text()
    if original.count(old) != 1 or not pathlib.Path("/etc/nginx/crm-ui.htpasswd").is_file():
        raise SystemExit("Expected CRM UI upstream and credentials")
    if original.count('auth_basic "CRM";') != (1 if action == "apply" else 2):
        raise SystemExit("Expected active API containment")
    backup = VHOST.with_name(VHOST.name + time.strftime(".before-ui-%Y%m%dT%H%M%SZ", time.gmtime()))
    with backup.open("x") as handle:
        handle.write(original)
    try:
        activate(original.replace(old, new))
    except subprocess.CalledProcessError:
        activate(original)
        raise
    print(f"{action}: vhost backup at {backup}")

if __name__ == "__main__":
    main()
