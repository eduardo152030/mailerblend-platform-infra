#!/usr/bin/env python3
"""Minimal scoped Outline REST examples for authorized workspaces."""
import argparse
import json
import os
from pathlib import Path

import requests


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("collections")
    commands.add_parser("search").add_argument("query")
    commands.add_parser("read").add_argument("id")
    create = commands.add_parser("create")
    create.add_argument("collection")
    create.add_argument("title")
    create.add_argument("markdown", type=Path)
    patch = commands.add_parser("patch")
    patch.add_argument("id")
    patch.add_argument("revision", type=int)
    patch.add_argument("old", type=Path)
    patch.add_argument("new", type=Path)
    args = parser.parse_args()

    origin = os.environ["OUTLINE_URL"].rstrip("/")
    if not origin.startswith("https://"):
        parser.error("An HTTPS Outline origin is required")

    def call(method, body):
        response = requests.post(
            f"{origin}/api/{method}", json=body, timeout=20, allow_redirects=False,
            headers={"Authorization": f"Bearer {os.environ['OUTLINE_API_TOKEN']}"},
        )
        if response.status_code == 409:
            raise SystemExit("Revision conflict. Read the document and recompute the patch.")
        if not 200 <= response.status_code < 300:
            raise SystemExit(f"{method} failed with HTTP {response.status_code}")
        return response.json()["data"]

    if args.command == "collections":
        result = call("collections.list", {})
    elif args.command == "search":
        result = call("documents.search", {"query": args.query})
    elif args.command == "read":
        result = call("documents.info", {"id": args.id})
    elif args.command == "create":
        created = call("documents.create", {
            "collectionId": args.collection, "title": args.title,
            "text": args.markdown.read_text(encoding="utf-8"), "publish": True,
        })
        result = call("documents.info", {"id": created["id"]})
    else:
        old = args.old.read_text(encoding="utf-8")
        new = args.new.read_text(encoding="utf-8")
        current = call("documents.info", {"id": args.id})
        if current["revision"] != args.revision or not old or current["text"].count(old) != 1:
            raise SystemExit("Stale revision or non-unique patch. Read the document again.")
        updated = call("documents.update", {
            "id": args.id, "lastRevision": args.revision,
            "editMode": "patch", "findText": old, "text": new,
        })
        result = call("documents.info", {"id": args.id})
        if updated["revision"] != result["revision"] or new.strip() not in result["text"]:
            raise SystemExit("Read-back differs. Inspect the document before further writes.")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
