"""Verify a synthetic GoTrue recovery by following a Mailpit message."""
import base64
import hashlib
import hmac
from html import unescape
from ipaddress import ip_address
import json
import re
import secrets
import sys
import time
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlencode, urlsplit
from urllib.request import build_opener, HTTPRedirectHandler, Request, urlopen


class CaptureRedirect(HTTPRedirectHandler):
    def redirect_request(self, request, response, code, message, headers, url):
        return None


def send(url, method="GET", payload=None, token=None, opener=urlopen):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = "Bearer " + token
    request = Request(url, json.dumps(payload).encode() if payload is not None else None,
                      headers=headers, method=method)
    try:
        with opener(request, timeout=8) as response:
            return response.status, json.load(response), response.headers
    except HTTPError as error:
        return error.code, {}, error.headers


def b64(data):
    return base64.urlsafe_b64encode(data).decode().rstrip("=")


def admin_token(key):
    prefix = b64(b'{"alg":"HS256","typ":"JWT"}') + "." + b64(
        json.dumps({"role": "service_role", "exp": int(time.time()) + 120}).encode()
    )
    return prefix + "." + b64(hmac.digest(key, prefix.encode(), hashlib.sha256))


def main():
    auth, mail = (ip_address(arg) for arg in sys.argv[1:])
    if not (auth.is_private and mail.is_private):
        raise ValueError("Expected isolated rehearsal addresses")
    settings = dict(line.strip().split("=", 1) for line in sys.stdin if "=" in line)
    base = f"http://{auth}:9999"
    mailpit = f"http://{mail}:8025/api/v1"
    email = f"recovery.{secrets.token_hex(8)}@example.com"
    old = secrets.token_urlsafe(28)
    new = secrets.token_urlsafe(28)
    status, _, _ = send(base + "/admin/users", "POST", {
        "email": email, "password": old, "email_confirm": True,
    }, admin_token(settings["CRM_REHEARSAL_JWT_SECRET"].encode()))
    assert status in (200, 201), status

    redirect = "http://auth:9999/restablecer"
    status, _, _ = send(base + "/recover?" + urlencode({"redirect_to": redirect}), "POST", {"email": email})
    assert status == 200, status
    for _ in range(15):
        status, inbox, _ = send(mailpit + "/messages")
        assert status == 200, status
        message = next((msg for msg in inbox["messages"]
                        if any(addr["Address"] == email for addr in msg["To"])), None)
        if message:
            break
        time.sleep(1)
    else:
        raise AssertionError("Recovery message did not arrive in Mailpit")

    status, body, _ = send(mailpit + "/message/" + message["ID"])
    assert status == 200, status
    link = re.search(r'href="(https?://[^"]+)"', body["HTML"])
    assert link, "Missing recovery link"
    verify = urlsplit(unescape(link[1]))
    assert verify.path == "/auth/v1/verify", "Wrong public recovery path"
    status, _, response_headers = send(base + "/verify?" + verify.query, opener=build_opener(CaptureRedirect()).open)
    assert status in (302, 303), status
    location = urlsplit(response_headers["Location"])
    assert location.path == "/restablecer"
    tokens = parse_qs(location.fragment)
    assert tokens.get("type") == ["recovery"]
    status, _, _ = send(base + "/user", "PUT", {"password": new}, tokens["access_token"][0])
    assert status == 200, status
    login = base + "/token?grant_type=password"
    assert send(login, "POST", {"email": email, "password": old})[0] == 400
    assert send(login, "POST", {"email": email, "password": new})[0] == 200
    print("PASS: Mailpit, ruta pública, redirección, cambio de contraseña y nuevo login")


if __name__ == "__main__":
    main()
