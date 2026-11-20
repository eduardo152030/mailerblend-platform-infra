"""Apply the CRM-only authentication gate in CT109. Read an htpasswd entry on stdin."""
import os
import pathlib
import shutil
import subprocess
import sys
import time

VHOST = pathlib.Path("/etc/nginx/sites-available/infra-svc01.mailerblend.com.conf")
USERS = pathlib.Path("/etc/nginx/crm-ui.htpasswd")
MARKER = "   location /_svc/ {"

def main():
    entry = sys.stdin.read().strip()
    if not entry.startswith("crm-operator:$6$") or len(entry.splitlines()) != 1:
        raise SystemExit("Expected one SHA-512 htpasswd entry for crm-operator")
    original = VHOST.read_text()
    if original.count(MARKER) != 1:
        raise SystemExit("Unexpected CRM vhost layout")
    location = """   location = /_svc/health {
    proxy_pass http://192.168.1.118:18088/health;
  }

   location = /_svc/v1/intake/webform {
    limit_except POST { deny all; }
    proxy_pass http://192.168.1.118:18088/v1/intake/webform;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
  }

"""
    gate = '\n    auth_basic "CRM";\n    auth_basic_user_file /etc/nginx/crm-ui.htpasswd;'
    candidate = original.replace(MARKER, location + MARKER + gate)
    if USERS.exists() and USERS.read_text() != entry + "\n":
        raise SystemExit("Existing CRM credential file differs")
    if candidate.count('auth_basic "CRM";') > 1:
        raise SystemExit("Containment already present")
    nginx = ["nginx"]
    subprocess.run(nginx + ["-t"], check=True)
    backup = VHOST.with_name(VHOST.name + time.strftime(".before-containment-%Y%m%dT%H%M%SZ", time.gmtime()))
    with backup.open("x") as handle:
        handle.write(original)
    if not USERS.exists():
        with USERS.open("x") as handle:
            os.fchmod(handle.fileno(), 0o640)
            shutil.chown(USERS, user="root", group="www-data")
            handle.write(entry + "\n")
    staged = VHOST.with_name(VHOST.name + ".containment-stage")
    staged.write_text(candidate)
    staged.replace(VHOST)
    try:
        subprocess.run(nginx + ["-t"], check=True)
        subprocess.run(["systemctl", "reload", "nginx"], check=True)
    except subprocess.CalledProcessError:
        staged.write_text(original)
        staged.replace(VHOST)
        subprocess.run(nginx + ["-t"], check=True)
        subprocess.run(["systemctl", "reload", "nginx"], check=True)
        raise
    print(f"Vhost backup: {backup}")

if __name__ == "__main__":
    main()
