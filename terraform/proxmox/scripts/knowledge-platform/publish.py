#!/usr/bin/env python3
"""Render a .puml and patch an explicitly managed block in Outline."""
import argparse
import base64
from hashlib import sha256
import os
from pathlib import Path
import re
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


def api(session, outline, method, body):
    return check(session.post(
        f"{outline}/api/{method}", json=body, timeout=30, allow_redirects=False,
    )).json()["data"]


def managed_block(text, key):
    begin = f"PlantUML begin: {key}"
    end = f"PlantUML end: {key}"
    if text.splitlines().count(begin) != 1 or text.splitlines().count(end) != 1:
        raise SystemExit("Expected exactly one pair of managed block markers")
    start, remaining = re.split(r"(?m)^" + re.escape(begin) + r"$", text, maxsplit=1)
    if not re.search(r"(?m)^" + re.escape(end) + r"$", remaining):
        raise SystemExit("Managed block markers are out of order")
    inner, tail = re.split(r"(?m)^" + re.escape(end) + r"$", remaining, maxsplit=1)
    return start, begin + inner + end, tail


def same_origin(outline, value):
    url = urljoin(outline + "/", value)
    parts = urlsplit(url)
    if parts.netloc != urlsplit(outline).netloc or parts.scheme != "https":
        raise SystemExit("Expected a same-origin HTTPS attachment URL")
    return url


def public_session(session):
    client = requests.Session()
    client.trust_env = session.trust_env
    client.verify = session.verify
    return client


def attachment_bytes(session, outline, url):
    response = session.get(same_origin(outline, url), timeout=30, allow_redirects=False)
    if response.is_redirect:
        with public_session(session) as client:
            response = client.get(
                same_origin(outline, response.headers["Location"]), timeout=30, allow_redirects=False,
            )
    return check(response).content


def upload(session, outline, document_id, key, extension, content, mime):
    digest = sha256(content).hexdigest()
    identity = f"plantuml:{document_id}:{key}:{extension}:{digest}".encode()
    # Outline v1.13.0 validates supplied attachment identifiers as UUIDv4.
    attachment_id = str(uuid.UUID(bytes=sha256(identity).digest()[:16], version=4))
    name = f"{key}-{digest[:16]}.{extension}"
    redirect = f"/api/attachments.redirect?id={attachment_id}"
    existing = session.get(same_origin(outline, redirect), timeout=30, allow_redirects=False)
    if existing.status_code != 404:
        if not 200 <= existing.status_code < 400 or attachment_bytes(session, outline, redirect) != content:
            raise SystemExit("Existing attachment cannot be verified; inspect before retrying")
        return redirect

    data = api(session, outline, "attachments.create", {
        "id": attachment_id, "documentId": document_id, "name": name, "size": len(content), "contentType": mime,
    })
    url = same_origin(outline, data["uploadUrl"])
    form = data["form"]
    if not form.get("sig") or data["attachment"]["id"] != attachment_id:
        raise SystemExit("Expected a signed local storage upload for the requested ID")
    with public_session(session) as client:
        check(client.post(url, data=form, files={"file": (name, content, mime)}, timeout=60, allow_redirects=False))
    if attachment_bytes(session, outline, redirect) != content:
        raise SystemExit("Uploaded attachment did not pass read-back verification")
    return redirect


def managed_assets(block):
    lines = [line.strip() for line in block.splitlines() if line.strip()]
    if len(lines) == 2:
        return None
    if len(lines) == 5 and re.fullmatch(r"PlantUML SHA256: [0-9a-f]{64}", lines[1]):
        image = re.fullmatch(r"!\[PlantUML diagram\]\(<?([^>\s)]+)>?\)", lines[2])
        source = re.fullmatch(r"\[PlantUML source\]\(<?([^>\s)]+)>?\)", lines[3])
        if image and source:
            return lines[1], image[1], source[1]
    raise SystemExit("Managed block contains unrecognized edits; inspect before publishing")



def publish(session, outline, renderer, document_id, key, source):
    original = api(session, outline, "documents.info", {"id": document_id})
    if type(original.get("revision")) is not int:
        raise SystemExit("Outline did not return a document revision")
    before, block, after = managed_block(original["text"], key)
    marker = f"PlantUML SHA256: {sha256(source).hexdigest()}"
    assets = managed_assets(block)
    if assets and assets[0] == marker:
        _, image_url, source_url = assets
        if attachment_bytes(session, outline, source_url) != source or not attachment_bytes(
            session, outline, image_url,
        ).startswith(b"\x89PNG\r\n\x1a\n"):
            raise SystemExit("Existing managed attachments failed verification")
        print(f"{document_id}: unchanged")
        return
    rendered = check(requests.get(
        f"{renderer.rstrip('/')}/png/{encode(source)}", timeout=30, allow_redirects=False,
    )).content
    if not rendered.startswith(b"\x89PNG\r\n\x1a\n"):
        raise SystemExit("Renderer returned an invalid PNG")
    source_url = upload(session, outline, document_id, key, "puml", source, "text/plain")
    image_url = upload(session, outline, document_id, key, "png", rendered, "image/png")
    replacement = (
        f"PlantUML begin: {key}\n\n{marker}\n\n"
        f"![PlantUML diagram](<{image_url}>)\n\n[PlantUML source](<{source_url}>)\n\n"
        f"PlantUML end: {key}"
    )
    api(session, outline, "documents.update", {
        "id": document_id, "lastRevision": original["revision"],
        "editMode": "patch", "findText": block, "text": replacement,
    })
    verified = api(session, outline, "documents.info", {"id": document_id})
    prefix, content, suffix = managed_block(verified["text"], key)
    if (prefix, suffix) != (before, after) or marker not in content.splitlines() or any(
        url not in content for url in (image_url, source_url)
    ):
        raise SystemExit("Document read-back differs from the intended managed patch")
    print(f"{document_id}: updated")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outline", required=True, help="Outline HTTPS base URL")
    parser.add_argument("--renderer", required=True, help="Private PlantUML base URL")
    parser.add_argument("--document", required=True, type=uuid.UUID)
    parser.add_argument("--diagram-key", required=True)
    parser.add_argument("source", type=Path)
    args = parser.parse_args()

    outline = args.outline.rstrip("/")
    parsed = urlsplit(outline)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.path:
        parser.error("Outline must be an HTTPS origin")
    source = args.source.read_bytes()
    if args.source.suffix != ".puml" or not 0 < len(source) <= MAX_SOURCE:
        parser.error("Expected a .puml source of at most 16 KiB")
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,47}", args.diagram_key):
        parser.error("Diagram key must contain only lowercase letters, digits and hyphens")

    with requests.Session() as session:
        session.headers["Authorization"] = "Bearer " + os.environ["OUTLINE_API_TOKEN"]
        publish(session, outline, args.renderer, str(args.document), args.diagram_key, source)


if __name__ == "__main__":
    main()
