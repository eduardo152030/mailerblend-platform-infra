"""Historical Basic Auth cutover transaction. Do not apply to the current JWT vhost."""
import hashlib
import os
import pathlib
import stat
import tempfile
import subprocess
import sys

VHOST = pathlib.Path("/etc/nginx/sites-available/infra-svc01.mailerblend.com.conf")
AUTH_FILE = pathlib.Path("/etc/nginx/crm-ui.htpasswd")
LEGACY = "    proxy_pass http://192.168.1.118:8080;"
RELEASE = """    auth_basic "CRM";
    auth_basic_user_file /etc/nginx/crm-ui.htpasswd;
    proxy_set_header Authorization "";
    proxy_pass http://192.168.1.118:18089;"""

def activate(config):
    original = VHOST.stat()
    with tempfile.NamedTemporaryFile(mode="w", dir=VHOST.parent, prefix=VHOST.name + ".ui-stage-",
                                     delete=False) as handle:
        staged = pathlib.Path(handle.name)
        handle.write(config)
        os.fchmod(handle.fileno(), stat.S_IMODE(original.st_mode))
        if os.geteuid() == 0:
            os.fchown(handle.fileno(), original.st_uid, original.st_gid)
    staged.replace(VHOST)
    subprocess.run(["nginx", "-t"], check=True)
    subprocess.run(["systemctl", "reload", "nginx"], check=True)


def transition(action):
    old, new = {"apply": (LEGACY, RELEASE), "rollback": (RELEASE, LEGACY)}[action]
    original = VHOST.read_text()
    expected = 1 if action == "apply" else 2
    count = original.count('auth_basic "CRM";')
    destination_count = 3 - expected
    if not AUTH_FILE.is_file():
        raise ValueError("Expected cutover credentials")
    if original.count(new) == 1 and original.count(old) == 0 and count == destination_count:
        return None
    if original.count(old) != 1 or count != expected:
        raise ValueError("Unexpected cutover vhost")
    with tempfile.NamedTemporaryFile(mode="w", dir=VHOST.parent, prefix=VHOST.name + ".before-ui-",
                                     delete=False) as handle:
        backup = pathlib.Path(handle.name)
        handle.write(original)
    digest = hashlib.sha256(backup.read_bytes()).hexdigest()
    with open(backup.with_suffix(backup.suffix + ".sha256"), "x", opener=private_opener) as handle:
        handle.write(f"{digest}  {backup.name}\n")
    try:
        activate(original.replace(old, new))
    except (OSError, subprocess.CalledProcessError):
        activate(original)
        raise
    return backup


def private_opener(path, flags):
    return os.open(path, flags, 0o600)


def main():
    action, = sys.argv[1:]
    backup = transition(action)
    print(f"{action}: vhost backup at {backup}" if backup else f"{action}: no changes")


if __name__ == "__main__":
    main()
