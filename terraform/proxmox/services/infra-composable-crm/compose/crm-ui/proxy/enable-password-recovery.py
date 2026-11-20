"""Enable the CRM GoTrue recovery routes on the existing vhost."""
from pathlib import Path
import subprocess
import tempfile

VHOST = Path("/etc/nginx/sites-available/infra-svc01.mailerblend.com.conf")
AUTH_BLOCK = """  location = /auth/v1/user {
    limit_except GET { deny all; }
    proxy_pass http://192.168.1.118:18090/user;
  }
"""
RECOVERY_BLOCK = """  location = /auth/v1/recover {
    limit_req zone=crm_auth_login burst=8 nodelay;
    limit_req_status 429;
    limit_except POST { deny all; }
    proxy_pass http://192.168.1.118:18090/recover;
  }
  location = /auth/v1/verify {
    access_log off;
    limit_except GET { deny all; }
    proxy_pass http://192.168.1.118:18090/verify;
  }
""" + AUTH_BLOCK.replace("except GET ", "except GET PUT ")


def update(current: str) -> str:
    if RECOVERY_BLOCK in current:
        return current
    if current.count(AUTH_BLOCK) != 1 or any(
        f"location = /auth/v1/{route} " in current for route in ("recover", "verify")
    ):
        raise ValueError("Unexpected CRM authentication route configuration")
    return current.replace(AUTH_BLOCK, RECOVERY_BLOCK)


def main():
    current = VHOST.read_text()
    updated = update(current)
    if current == updated:
        return
    with tempfile.NamedTemporaryFile(mode="w", prefix=VHOST.name + ".before-recovery-",
                                     dir=VHOST.parent, delete=False) as backup:
        backup.write(current)
    try:
        VHOST.write_text(updated)
        subprocess.run(["nginx", "-t"], check=True)
        subprocess.run(["systemctl", "reload", "nginx"], check=True)
    except (OSError, subprocess.CalledProcessError):
        VHOST.write_text(current)
        subprocess.run(["nginx", "-t"], check=True)
        subprocess.run(["systemctl", "reload", "nginx"], check=True)
        raise


if __name__ == "__main__":
    main()
