"""
integrations/anthropic_client.py
==================================
Single point of contact for all Anthropic API communication.

Rules enforced here:
  - Auth headers built here, nowhere else.
  - API URL built here, nowhere else.
  - Timeout defined here, nowhere else.
  - Model selection here, nowhere else.
  - Response parsing (extract text block) here.
  - Error normalization and logging here.
  - Callers receive plain dicts or None — no httpx objects leak out.

To debug Anthropic integration:
  - 401 errors          → check ANTHROPIC_API_KEY env var
  - Timeout errors      → adjust TIMEOUT constant here
  - Model errors        → check MODEL constant here
  - Unexpected None     → check [anthropic] logs below

Do NOT import httpx for Anthropic calls anywhere outside this file.
"""
import os
from typing import Any

import httpx

# ── Config ─────────────────────────────────────────────────────────────────
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
MODEL             = "claude-haiku-4-5-20251001"
API_URL           = "https://api.anthropic.com/v1/messages"
TIMEOUT           = 10   # seconds — standard calls
TIMEOUT_SHORT     = 5    # seconds — humanize (fire-and-forget feel)


def _headers() -> dict:
    return {
        "x-api-key":         ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type":      "application/json",
    }


def is_configured() -> bool:
    """Return True if API key is set."""
    return bool(ANTHROPIC_API_KEY)


# ── Core call ──────────────────────────────────────────────────────────────

async def complete(
    system: str,
    messages: list[dict],
    max_tokens: int = 512,
    tools: list[dict] | None = None,
    tool_choice: dict | None = None,
    timeout: float = TIMEOUT,
) -> dict | None:
    """
    Send a request to the Anthropic Messages API.

    Returns the full API response dict on success, None on any failure.
    Callers extract content themselves so business logic stays in the caller.

    Args:
        system:     System prompt string.
        messages:   List of {"role": "user"|"assistant", "content": str} dicts.
        max_tokens: Maximum tokens to generate.
        tools:      Optional tool definitions for tool_use calls.
        tool_choice: Optional tool_choice dict.
        timeout:    HTTP timeout in seconds (override for slow calls).
    """
    if not is_configured():
        return None

    payload: dict[str, Any] = {
        "model":      MODEL,
        "max_tokens": max_tokens,
        "system":     system,
        "messages":   messages,
    }
    if tools:
        payload["tools"] = tools
    if tool_choice:
        payload["tool_choice"] = tool_choice

    try:
        async with httpx.AsyncClient(timeout=timeout) as c:
            r = await c.post(API_URL, headers=_headers(), json=payload)
            if r.status_code != 200:
                print(f"[anthropic] API error {r.status_code}: {r.text[:200]}")
                return None
            return r.json()
    except httpx.TimeoutException:
        print(f"[anthropic] timeout after {timeout}s")
        return None
    except Exception as exc:
        print(f"[anthropic] exception: {exc}")
        return None


# ── Convenience helpers ────────────────────────────────────────────────────

def extract_text(response: dict | None) -> str | None:
    """Extract the first text block from an API response. Returns None if not found."""
    if not response:
        return None
    try:
        return response["content"][0]["text"].strip()
    except (KeyError, IndexError, TypeError):
        return None


def extract_tool_input(response: dict | None, tool_name: str) -> dict | None:
    """Extract input dict from a tool_use block. Returns None if not found."""
    if not response:
        return None
    for block in response.get("content", []):
        if block.get("type") == "tool_use" and block.get("name") == tool_name:
            return block.get("input", {})
    return None