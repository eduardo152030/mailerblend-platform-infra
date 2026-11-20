"""Provision the single production CRM operator through the private GoTrue API."""
import base64
from datetime import datetime, timezone
import hashlib
import hmac
import json
import sys
import time
import urllib.request

issuer = "https://infra-svc01.mailerblend.com/auth/v1"
base = "http://192.168.1.118:18090"


def b64(value):
    return base64.urlsafe_b64encode(value).decode().rstrip("=")


def sign(key, role, duration):
    claims = {"role": role, "iss": issuer, "exp": int(time.time()) + duration}
    prefix = b64(b'{"alg":"HS256","typ":"JWT"}') + "." + b64(json.dumps(claims).encode())
    mac = hmac.new(key.encode(), prefix.encode(), hashlib.sha256).digest()
    return prefix + "." + b64(mac)


def request(path, payload=None, authorization=None):
    headers = {"Content-Type": "application/json"}
    if authorization:
        headers["Authorization"] = f"Bearer {authorization}"
    encoded = json.dumps(payload).encode() if payload is not None else None
    with urllib.request.urlopen(urllib.request.Request(base + path, encoded, headers), timeout=10) as response:
        return json.load(response)


def reconcile(config, *, dry_run=False):
    auth = sign(config["CRM_AUTH_JWT_SECRET"], "service_role", 120)
    users = request("/admin/users?per_page=2", authorization=auth)["users"]
    email = config["email"]
    if users:
        if len(users) != 1 or users[0]["email"] != email:
            raise SystemExit("Unexpected pre-existing GoTrue accounts")
        user = users[0]
        blocked = user.get("banned_until")
        if blocked and datetime.fromisoformat(blocked.replace("Z", "+00:00")) > datetime.now(timezone.utc):
            raise SystemExit("Existing operator is disabled")
        if user.get("app_metadata", {}).get("crm_role") != "admin":
            raise SystemExit("Existing operator lacks the approved role")
    if dry_run:
        print(f"Dry-run: altas={int(not users)}, bajas=0, cambios de rol=0")
        return
    if not users:
        request("/admin/users", {
            "email": email, "password": config["password"], "email_confirm": True,
            "app_metadata": {"crm_role": "admin"},
        }, auth)
    result = request("/token?grant_type=password", {"email": email, "password": config["password"]})
    if result["user"]["app_metadata"].get("crm_role") != "admin":
        raise SystemExit("Missing operator grants")
    claims = json.loads(base64.urlsafe_b64decode(result["access_token"].split(".")[1] + "==="))
    if claims.get("iss") != issuer:
        raise SystemExit("Unexpected GoTrue token issuer")
    print("Single administrator provisioned and login verified.")


def main():
    config = json.load(sys.stdin)
    key = config["CRM_AUTH_JWT_SECRET"]
    if sys.argv[1:] == ["public-key"]:
        print(sign(key, "anon", 365 * 24 * 3600))
        return
    if sys.argv[1:] not in ([], ["--dry-run"]):
        raise SystemExit("Unknown bootstrap mode")
    reconcile(config, dry_run=sys.argv[1:] == ["--dry-run"])


if __name__ == "__main__":
    main()
