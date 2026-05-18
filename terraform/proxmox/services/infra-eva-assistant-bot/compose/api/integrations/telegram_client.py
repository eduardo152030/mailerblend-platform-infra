"""
integrations/telegram_client.py
=================================
Single point of contact for all Telegram Bot API HTTP communication.

Rules enforced here:
  - All Telegram URLs built here, nowhere else.
  - All auth tokens read here, nowhere else.
  - All timeouts defined here, nowhere else.
  - Callers receive plain dicts or bytes — no httpx objects leak out.

Backward compatibility:
  - telegram_service.py still exists and still exports send_message().
  - It now delegates to this client internally.
  - All existing imports of telegram_service.send_message() continue to work.

To debug Telegram integration:
  - Messages not delivered   → check TELEGRAM_BOT_TOKEN env var
  - Photos not downloading   → inspect get_file() / download_file() logs
  - sendMessage 4xx errors   → inspect the payload in send_message()
"""
import os
from typing import Any

import httpx

# ── Config ──────────────────────────────────────────────────────────────────
_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

_BASE_URL      = "https://api.telegram.org"
_TIMEOUT_SEND  = 20    # seconds — outbound messages
_TIMEOUT_FILE  = 15    # seconds — getFile metadata
_TIMEOUT_DL    = 60    # seconds — file download (can be large)


def _api_url(method: str) -> str:
    """Build a Bot API endpoint URL."""
    return f"{_BASE_URL}/bot{_TOKEN}/{method}"


# ── Message operations ────────────────────────────────────────────────────

async def send_message(chat_id: int, text: str, parse_mode: str | None = None) -> dict:
    """
    Send a text message to a chat.
    Returns the Telegram API response dict on success.
    Returns {"ok": False, "error": "..."} on failure — does NOT raise.
    Callers should check the return value if they need to know if it succeeded.
    """
    payload: dict[str, Any] = {"chat_id": chat_id, "text": text}
    if parse_mode:
        payload["parse_mode"] = parse_mode

    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT_SEND) as client:
            resp = await client.post(_api_url("sendMessage"), json=payload)
            if resp.status_code == 200:
                return resp.json()
            print(f"[tg_client] ❌ sendMessage failed {resp.status_code} chat_id={chat_id}: {resp.text[:100]}")
            return {"ok": False, "error": f"HTTP {resp.status_code}", "chat_id": chat_id}
    except Exception as exc:
        print(f"[tg_client] ❌ sendMessage exception chat_id={chat_id}: {exc}")
        return {"ok": False, "error": str(exc), "chat_id": chat_id}


# ── File operations ───────────────────────────────────────────────────────

async def get_file(file_id: str) -> str | None:
    """
    Resolve a file_id to a file_path on Telegram servers.
    Returns the file_path string or None on failure.
    """
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT_FILE) as client:
            r = await client.get(_api_url("getFile"), params={"file_id": file_id})
            if r.status_code == 200:
                return r.json().get("result", {}).get("file_path")
            print(f"[tg_client] ❌ getFile failed {r.status_code}: file_id={file_id}")
            return None
    except Exception as exc:
        print(f"[tg_client] ❌ get_file exception: {exc}")
        return None


async def download_file(file_path: str) -> bytes | None:
    """
    Download raw bytes for a file_path returned by get_file().
    Returns bytes or None on failure.
    """
    url = f"{_BASE_URL}/file/bot{_TOKEN}/{file_path}"
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT_DL) as client:
            r = await client.get(url)
            if r.status_code == 200:
                return r.content
            print(f"[tg_client] ❌ download_file failed {r.status_code}: {file_path}")
            return None
    except Exception as exc:
        print(f"[tg_client] ❌ download_file exception: {exc}")
        return None


async def get_webhook_info() -> dict:
    """Return current webhook configuration (useful for smoke tests)."""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(_api_url("getWebhookInfo"))
            return r.json() if r.status_code == 200 else {}
    except Exception as exc:
        print(f"[tg_client] ❌ get_webhook_info exception: {exc}")
        return {}


# ── Availability check ────────────────────────────────────────────────────

def is_configured() -> bool:
    """Return True if bot token is set."""
    return bool(_TOKEN)