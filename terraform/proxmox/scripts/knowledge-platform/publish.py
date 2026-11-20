#!/usr/bin/env python3
"""Render a .puml and update an existing, dedicated Outline document."""
import argparse
import base64
import os
from pathlib import Path
import uuid
import zlib
from urllib.parse import urljoin, urlsplit

import requests

ALPHABET = b"0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_"
MAX_SOURCE = 16 * 1024


def encode(source):
    compressor = zlib.compressobj(wbits=-15)
    compressed = compressor.compress(source) + compressor.flush()
    padded = compressed + b"\0" * (-len(compressed) % 3)
    return base64.b64encode(padded).translate(
        bytes.maketrans(
            b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/",
            ALPHABET,
        )
    ).decode("ascii")


def check(response):
    if not 200 <= response.status_code < 300:
        raise SystemExit(f"Request failed with HTTP {response.status_code}")
    return response


def upload(session, outline, document_id, name, content, mime):
    data = check(session.post(
        outline + "/api/attachments.create",
        json={"documentId": document_id, "name": name, "size": len(content), "contentType": mime},
        timeout=30,
        allow_redirects=False,
    )).json()["data"]
    url = urljoin(outline + "/", data["uploadUrl"])
    if urlsplit(url).netloc != urlsplit(outline).netloc or urlsplit(url).scheme != "https":
        raise SystemExit("Expected same-origin HTTPS local storage upload")
    check(session.post(
        url, data=data["form"], files={"file": (name, content, mime)},
        timeout=60, allow_redirects=False,
    ))
    return data["attachment"]["url"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outline", required=True, help="Outline HTTPS base URL")
    parser.add_argument("--renderer", required=True, help="Private PlantUML base URL")
    parser.add_argument("--document", required=True, type=uuid.UUID)
    parser.add_argument("source", type=Path)
    args = parser.parse_args()

    outline = args.outline.rstrip("/")
    parsed = urlsplit(outline)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.path:
        parser.error("Outline must be an HTTPS origin")
    source = args.source.read_bytes()
    if args.source.suffix != ".puml" or not 0 < len(source) <= MAX_SOURCE:
        parser.error("Expected a .puml source of at most 16 KiB")
    encoded = encode(source)
    rendered = check(requests.get(
        f"{args.renderer.rstrip('/')}/png/{encoded}", timeout=30, allow_redirects=False,
    )).content
    if not rendered.startswith(b"\x89PNG\r\n\x1a\n"):
        raise SystemExit("Renderer returned an invalid PNG")

    with requests.Session() as session:
        session.headers["Authorization"] = "Bearer " + os.environ["OUTLINE_API_TOKEN"]
        document_id = str(args.document)
        source_url = upload(session, outline, document_id, "diagram.puml", source, "text/plain")
        image_url = upload(session, outline, document_id, "diagram.png", rendered, "image/png")
        check(session.post(
            outline + "/api/documents.update",
            json={"id": document_id, "text": f"![Diagrama](<{image_url}>)\n\n[Fuente PlantUML](<{source_url}>)\n"},
            timeout=30,
            allow_redirects=False,
        ))
    print(document_id)


if __name__ == "__main__":
    main()
