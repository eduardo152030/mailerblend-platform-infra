#!/usr/bin/env python3
"""Set the native Draw.io origin through an Outline administrator session."""
import os

import requests

OUTLINE = "https://infra-doc.mailerblend.com"
SETTINGS = {"diagrams": {"url": "https://infra-diagrams.mailerblend.com/"}}


def main():
    with requests.Session() as session:
        session.headers["Authorization"] = "Bearer " + os.environ["OUTLINE_ADMIN_SESSION_TOKEN"]

        def call(method, body):
            response = session.post(f"{OUTLINE}/api/{method}", json=body, timeout=20, allow_redirects=False)
            if not 200 <= response.status_code < 300:
                raise SystemExit(f"{method} failed with HTTP {response.status_code}")
            return response.json()["data"]

        existing = call("integrations.list", {"service": "diagrams", "type": "embed"})
        if len(existing) > 1 or (existing and existing[0]["settings"] != SETTINGS):
            raise SystemExit("Existing Draw.io integration differs; review before replacing it")
        integration = existing[0] if existing else call(
            "integrations.create", {"service": "diagrams", "type": "embed", "settings": SETTINGS},
        )
        if call("integrations.info", {"id": integration["id"]})["settings"] != SETTINGS:
            raise SystemExit("Draw.io integration could not be verified")
        print("Native Draw.io origin verified")


if __name__ == "__main__":
    main()
