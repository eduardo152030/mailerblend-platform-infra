"""
integrations/focalboard_client.py
==================================
Single point of contact for all Focalboard HTTP communication.

Rules enforced here:
  - All auth headers built here, nowhere else.
  - All endpoint URLs built here, nowhere else.
  - All timeouts defined here, nowhere else.
  - All response parsing / error normalization here.
  - Callers receive plain Python dicts or booleans — no httpx objects leak out.

To debug Focalboard integration:
  - Connection errors          → check FB_URL / FB_TOKEN env vars
  - Card not created           → inspect create_card() logs
  - Card not updated           → inspect update_card_properties() logs
  - Polling not returning cards → inspect get_cards_since() logs
  - Wrong property values      → inspect the props dict built in each method

Do NOT import httpx anywhere outside this file for Focalboard calls.
"""
import json
import os
import time
import uuid
from datetime import datetime
from typing import Any

import httpx

# ── Config ─────────────────────────────────────────────────────────────────
_FB_URL   = os.getenv("FOCALBOARD_URL",      "http://focalboard:8000")
_FB_TOKEN = os.getenv("FOCALBOARD_TOKEN",    "")
_FB_BOARD = os.getenv("FOCALBOARD_BOARD_ID", "")

_TIMEOUT_DEFAULT = 10   # seconds — standard reads/writes
_TIMEOUT_POLL    = 15   # seconds — card listing (larger response)
_TIMEOUT_PATCH   = 8    # seconds — property updates


def _headers() -> dict:
    """Auth + CSRF headers required by Focalboard API."""
    return {
        "Authorization": f"Bearer {_FB_TOKEN}",
        "Content-Type":  "application/json",
        "X-Requested-With": "XMLHttpRequest",
    }


def _board_url(path: str = "") -> str:
    """Build a boards/{board_id}/... URL."""
    return f"{_FB_URL}/api/v2/boards/{_FB_BOARD}{path}"


# ── Card operations ────────────────────────────────────────────────────────

async def create_card(
    title: str,
    properties: dict,
    board_id: str | None = None,
) -> str | None:
    """
    Create a card on the board. Returns the card ID on success, None on failure.

    Args:
        title:      Card title.
        properties: Dict of {prop_id: value} — caller is responsible for
                    building correct property IDs and values.
        board_id:   Override board (e.g. content board). Defaults to tasks board.
    """
    bid     = board_id or _FB_BOARD
    card_id = uuid.uuid4().hex[:26]
    now_ms  = int(time.time() * 1000)

    block = {
        "id":       card_id,
        "type":     "card",
        "schema":   1,
        "boardId":  bid,
        "parentId": bid,
        "title":    title,
        "createAt": now_ms,
        "updateAt": now_ms,
        "deleteAt": 0,
        "fields": {
            "isTemplate":   False,
            "contentOrder": [],
            "properties":   properties,
        },
    }

    url = f"{_FB_URL}/api/v2/boards/{bid}/blocks"
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT_DEFAULT) as c:
            r = await c.post(url, headers=_headers(), json=[block])
            if r.status_code in (200, 201):
                data = r.json()
                cid  = data[0]["id"] if isinstance(data, list) else data.get("id", card_id)
                print(f"[fb_client] ✅ card created: {cid} — '{title[:60]}'")
                return cid
            print(f"[fb_client] ❌ create_card failed {r.status_code}: {r.text[:200]}")
            return None
    except Exception as exc:
        print(f"[fb_client] ❌ create_card exception: {exc}")
        return None


async def update_card_properties(
    card_id: str,
    properties: dict,
    board_id: str | None = None,
) -> bool:
    """
    Patch a card's properties. Returns True on success.

    Note: Focalboard replaces the entire properties object, it does NOT merge.
    Always pass all known properties to avoid losing existing values.
    """
    bid = board_id or _FB_BOARD
    url = f"{_FB_URL}/api/v2/boards/{bid}/blocks/{card_id}"
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT_PATCH) as c:
            r = await c.patch(
                url,
                headers=_headers(),
                json={"updatedFields": {"properties": properties}},
            )
            ok = r.status_code in (200, 204)
            if ok:
                print(f"[fb_client] ✅ card updated: {card_id}")
            else:
                print(f"[fb_client] ❌ update_card_properties failed {r.status_code}: {r.text[:100]}")
            return ok
    except Exception as exc:
        print(f"[fb_client] ❌ update_card_properties exception card={card_id}: {exc}")
        return False


async def delete_card(card_id: str, board_id: str | None = None) -> bool:
    """Delete a card. Returns True on success."""
    bid = board_id or _FB_BOARD
    url = f"{_FB_URL}/api/v2/boards/{bid}/blocks/{card_id}"
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT_PATCH) as c:
            r = await c.delete(url, headers=_headers())
            ok = r.status_code in (200, 204)
            if not ok:
                print(f"[fb_client] ❌ delete_card failed {r.status_code}: card={card_id}")
            return ok
    except Exception as exc:
        print(f"[fb_client] ❌ delete_card exception card={card_id}: {exc}")
        return False


async def get_cards_since(since: datetime, board_id: str | None = None) -> list[dict]:
    """
    Return all cards updated after `since`.
    Returns empty list on any failure (caller handles gracefully).
    """
    bid      = board_id or _FB_BOARD
    url      = f"{_FB_URL}/api/v2/boards/{bid}/blocks?type=card"
    since_ms = since.timestamp() * 1000
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT_POLL) as c:
            r = await c.get(url, headers=_headers())
            if r.status_code != 200:
                print(f"[fb_client] ❌ get_cards_since failed {r.status_code}")
                return []
            cards = r.json()
            return [card for card in cards if card.get("updateAt", 0) > since_ms]
    except Exception as exc:
        print(f"[fb_client] ❌ get_cards_since exception: {exc}")
        return []


async def get_all_cards(board_id: str | None = None) -> list[dict]:
    """Return all cards on the board (no time filter)."""
    bid = board_id or _FB_BOARD
    url = f"{_FB_URL}/api/v2/boards/{bid}/blocks?type=card"
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT_POLL) as c:
            r = await c.get(url, headers=_headers())
            if r.status_code != 200:
                print(f"[fb_client] ❌ get_all_cards failed {r.status_code}")
                return []
            return r.json()
    except Exception as exc:
        print(f"[fb_client] ❌ get_all_cards exception: {exc}")
        return []


# ── Availability check ─────────────────────────────────────────────────────

def is_configured() -> bool:
    """Return True if Focalboard credentials are set."""
    return bool(_FB_TOKEN and _FB_BOARD)
