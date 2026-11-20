"""Exercise GoTrue using a synthetic user and the rehearsal services only."""
import base64
import hashlib
import hmac
import ipaddress
import json
import secrets
import sys
import time
import urllib.error
import urllib.request


def b64(value):
    return base64.urlsafe_b64encode(value).decode().rstrip("=")


def request(base, path, data=None, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(base + path, json.dumps(data).encode() if data is not None else None, headers)
    try:
        with urllib.request.urlopen(req, timeout=8) as response:
            return response.status, json.load(response) if response.status != 204 else {}
    except urllib.error.HTTPError as error:
        return error.code, {}


def main():
    host, mail = (ipaddress.ip_address(arg) for arg in sys.argv[1:])
    if not host.is_private or not mail.is_private:
        raise SystemExit("Expected private rehearsal addresses")
    config = dict(line.strip().split("=", 1) for line in sys.stdin if "=" in line)
    key = config["CRM_REHEARSAL_JWT_SECRET"].encode()
    prefix = b64(b'{"alg":"HS256","typ":"JWT"}') + "." + b64(
        json.dumps({"role": "service_role", "exp": int(time.time()) + 120}).encode()
    )
    admin = prefix + "." + b64(hmac.new(key, prefix.encode(), hashlib.sha256).digest())
    url = f"http://{host}:9999"
    assert request(url, "/health")[0] == 200
    mail_url = f"http://{mail}:8025"
    assert request(mail_url, "/api/v1/messages")[0] == 200
    email = f"rehearsal.{secrets.token_hex(8)}@example.com"
    password = secrets.token_urlsafe(32)
    role_map = {"form_entries": "editor"}
    status, _ = request(url, "/admin/users", {
        "email": email, "password": password, "email_confirm": True,
        "app_metadata": {"project_roles": role_map},
    }, admin)
    assert status in (200, 201), status
    status, session = request(url, "/token?grant_type=password", {"email": email, "password": password})
    assert status == 200, status
    assert session["user"]["app_metadata"]["project_roles"] == role_map
    assert session["expires_in"] == 60
    status, renewed = request(url, "/token?grant_type=refresh_token", {"refresh_token": session["refresh_token"]})
    assert status == 200, status
    assert request(url, "/logout", {}, renewed["access_token"])[0] == 204
    status, _ = request(url, "/token?grant_type=refresh_token", {"refresh_token": renewed["refresh_token"]})
    assert status in (400, 401, 403), status
    assert request(url, "/recover", {"email": email})[0] == 200
    for _ in range(10):
        status, inbox = request(mail_url, "/api/v1/messages")
        assert status == 200
        if any(any(addr["Address"] == email for addr in msg["To"]) for msg in inbox["messages"]):
            break
        time.sleep(1)
    else:
        raise AssertionError("Mailpit did not receive the synthetic message")
    print("GoTrue smoke PASS: admin, login, TTL 60 s, refresh, logout y rechazo del refresh revocado y correo en Mailpit")


if __name__ == "__main__":
    main()
