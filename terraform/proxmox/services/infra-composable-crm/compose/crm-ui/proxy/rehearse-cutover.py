"""Exercise the historical proxy cutover on ephemeral loopback Nginx."""
from argparse import ArgumentParser
from base64 import b64encode
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import importlib.util
from pathlib import Path
import socketserver
import subprocess
import tempfile
import threading
import time
from urllib.error import HTTPError
from urllib.request import Request, urlopen


def load_cutover():
    path = Path(__file__).with_name("cutover-crm-ui.py")
    spec = importlib.util.spec_from_file_location("cutover", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def backend(label):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(label)

        def log_message(self, *_):
            pass

    service = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=service.serve_forever, daemon=True).start()
    return service


def request(port, path, authenticated):
    headers = {"Authorization": "Basic " + b64encode(b"fixture:synthetic").decode()} if authenticated else {}
    try:
        with urlopen(Request(f"http://127.0.0.1:{port}{path}", headers=headers), timeout=3) as response:
            return response.status, response.read()
    except HTTPError as error:
        return error.code, b""


def rehearse(nginx, directory):
    cutover = load_cutover()
    services = [backend(label) for label in (b"budibase-fixture", b"crmapi-fixture", b"ui-fixture")]
    legacy, api, release = [host.server_port for host in services]
    with socketserver.TCPServer(("127.0.0.1", 0), None) as reserved:
        port = reserved.server_address[1]
    cutover.VHOST = directory / "crm.conf"
    cutover.AUTH_FILE = directory / "users"
    digest = subprocess.check_output(["openssl", "passwd", "-apr1", "synthetic"], text=True).strip()
    cutover.AUTH_FILE.write_text(f"fixture:{digest}\n")
    cutover.LEGACY = cutover.LEGACY.replace("192.168.1.118:8080", f"127.0.0.1:{legacy}")
    cutover.RELEASE = cutover.RELEASE.replace("192.168.1.118:18089", f"127.0.0.1:{release}")
    cutover.RELEASE = cutover.RELEASE.replace("/etc/nginx/crm-ui.htpasswd", str(cutover.AUTH_FILE))
    original = f"""server {{
  listen 127.0.0.1:{port};
  location /_svc/ {{
    auth_basic "CRM";
    auth_basic_user_file {cutover.AUTH_FILE};
    proxy_pass http://127.0.0.1:{api};
  }}
  location / {{
{cutover.LEGACY}
  }}
}}
"""
    cutover.VHOST.write_text(original)
    cutover.VHOST.chmod(0o640)
    config = directory / "nginx.conf"
    config.write_text(f"pid {directory}/nginx.pid; error_log {directory}/error.log;\n"
                      f"events {{}} http {{ access_log off; "
                      f"client_body_temp_path {directory}/body; proxy_temp_path {directory}/proxy; "
                      f"fastcgi_temp_path {directory}/fastcgi; uwsgi_temp_path {directory}/uwsgi; "
                      f"scgi_temp_path {directory}/scgi; include {cutover.VHOST}; }}\n")
    command = [nginx, "-p", str(directory), "-c", str(config)]
    run = subprocess.run
    calls = []

    def real_nginx(args, **kwargs):
        calls.append(args)
        return run(command + (["-t"] if args[-1] == "-t" else ["-s", "reload"]),
                   capture_output=True, **kwargs)

    run(command + ["-t"], check=True)
    nginx_process = subprocess.Popen(command + ["-g", "daemon off;"],
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(25):
            try:
                if request(port, "/", False)[0] == 200:
                    break
            except OSError:
                time.sleep(0.1)
        cutover.subprocess.run = real_nginx
        valid = cutover.RELEASE
        cutover.RELEASE = valid + "\n    invalid_for_rehearsal on;"
        try:
            cutover.transition("apply")
        except subprocess.CalledProcessError:
            pass
        else:
            raise AssertionError("Invalid candidate was applied")
        assert cutover.VHOST.read_text() == original
        assert cutover.VHOST.stat().st_mode & 0o777 == 0o640
        assert request(port, "/", False) == (200, b"budibase-fixture")
        assert request(port, "/_svc/health", False)[0] == 401
        assert request(port, "/_svc/health", True) == (200, b"crmapi-fixture")
        cutover.RELEASE = valid
        backup = cutover.transition("apply")
        assert backup.with_suffix(backup.suffix + ".sha256").is_file()
        count = len(calls)
        assert cutover.transition("apply") is None and len(calls) == count
        cutover.transition("rollback")
        count = len(calls)
        assert cutover.transition("rollback") is None and len(calls) == count
        assert cutover.VHOST.read_text() == original
    finally:
        cutover.subprocess.run = run
        nginx_process.terminate()
        nginx_process.wait(timeout=10)
        for service in services:
            service.shutdown()
    print("PASS: nginx rechazó candidato, rollback recuperó Budibase y API 401/200, repetición sin reload")


if __name__ == "__main__":
    cli = ArgumentParser(description=__doc__)
    cli.add_argument("--nginx", default="nginx")
    with tempfile.TemporaryDirectory() as path:
        rehearse(cli.parse_args().nginx, Path(path))
