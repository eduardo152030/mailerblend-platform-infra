"""
utils/url_utils.py
==================
URL parsing, title extraction, and social media domain detection.

Rules:
  - Pure functions — no DB, no HTTP, no side effects.
  - Uses only stdlib (re, urllib.parse).
  - Telegram message dict is passed in — never fetched here.

IMPORTANT — Telegram preview metadata:
  The Telegram Bot API webhook does NOT include page preview title in
  incoming message payloads. link_preview_options only exists on outgoing
  sendMessage requests — not on incoming messages.

  Title priority used here:
    1. text    — text alongside the URL, cleaned of hashtags/site suffixes
    2. social  — platform label + path slug for known social domains
    3. domain  — platform label + domain for known platforms with no useful path
    4. fallback — "Revisar domain.com"

To debug title source:
  Look for [capture:url] log lines — they always state the title source.
"""
import os
import re
import urllib.parse
from typing import Optional


# ── Social / content platform domains ────────────────────────────────────
SOCIAL_DOMAINS = {
    "x.com":           "X (Twitter)",
    "twitter.com":     "X (Twitter)",
    "t.co":            "X (Twitter)",
    "linkedin.com":    "LinkedIn",
    "youtube.com":     "YouTube",
    "youtu.be":        "YouTube",
    "tiktok.com":      "TikTok",
    "instagram.com":   "Instagram",
    "threads.net":     "Threads",
    "github.com":      "GitHub",
    "reddit.com":      "Reddit",
    "medium.com":      "Medium",
    "substack.com":    "Substack",
    "stockstotrade.com": "StocksToTrade",
    "university.stockstotrade.com": "STT University",
}

_GENERIC_PATHS = {
    "watch", "posts", "feed", "status", "stories", "reel",
    "p", "c", "shorts", "live", "channel", "user", "in",
}


def extract_url(text: str) -> Optional[str]:
    m = re.search(r'https?://\S+', text)
    return m.group(0) if m else None


def clean_domain(url: str) -> str:
    try:
        return urllib.parse.urlparse(url).netloc.replace("www.", "")
    except Exception:
        return url


def is_social_url(url: str) -> bool:
    domain = clean_domain(url)
    return any(domain == d or domain.endswith("." + d) for d in SOCIAL_DOMAINS)


def platform_label(url: str) -> Optional[str]:
    domain = clean_domain(url)
    for d, label in SOCIAL_DOMAINS.items():
        if domain == d or domain.endswith("." + d):
            return label
    return None


def extract_title_from_message(message: dict, url: str) -> str:
    """
    Extract best available title for a URL from a Telegram message.

    NOTE: Telegram webhook payloads do NOT include page preview titles.
    Only text present in the message itself is available.
    """
    domain = clean_domain(url)

    # ── Source 1: text alongside the URL ─────────────────────────────────
    text         = message.get("text") or message.get("caption") or ""
    text_no_url  = text.replace(url, "").strip()
    text_no_tags = re.sub(r'\s*#[a-zA-Z]\w*', '', text_no_url).strip()

    if text_no_tags and 4 <= len(text_no_tags) <= 120:
        candidate = text_no_tags.split("\n")[0].strip()
        candidate = re.sub(r'\s*\|[^|]{1,40}$', '', candidate).strip()
        candidate = re.sub(r'\s*[-\u2013\u2014][^-\u2013\u2014]{1,40}$', '', candidate).strip()
        if len(candidate) >= 4:
            print(f"[capture:url] title source=text title='{candidate}' url={url}")
            return candidate
        print(f"[capture:url] text too short after cleanup ('{candidate}'), trying next source")

    # ── Source 2: platform label + path slug ─────────────────────────────
    label = platform_label(url)
    if label:
        try:
            path_parts = [p for p in urllib.parse.urlparse(url).path.strip("/").split("/")
                          if p and "?" not in p]
            for slug in path_parts:
                if slug.lower() not in _GENERIC_PATHS and len(slug) >= 2:
                    title = f"{label} — {slug}"
                    print(f"[capture:url] title source=social url={url} title='{title}'")
                    return title
        except Exception:
            pass
        # ── Source 3: platform label + domain ────────────────────────────
        title = f"{label} — {domain}"
        print(f"[capture:url] title source=domain url={url} title='{title}'")
        return title

    # ── Source 4: generic fallback ────────────────────────────────────────
    title = f"Revisar {domain}"
    print(f"[capture:url] title source=fallback (no preview in webhook) url={url} title='{title}'")
    return title


def filename_to_title(filename: str) -> str:
    """
    Convert a filename to a clean card title.
    'my_document.pdf' -> 'my document'
    'Q3 Report 2024.pdf' -> 'Q3 Report 2024'
    """
    name = os.path.splitext(filename)[0]
    name = name.replace("_", " ").replace("-", " ")
    name = re.sub(r'\s+', ' ', name).strip()
    return name if name else filename


def split_text_and_tags(text: str) -> tuple[str, list[str]]:
    tags  = re.findall(r'#[a-zA-Z]\w*', text)
    clean = re.sub(r'\s*#[a-zA-Z]\w*', '', text).strip()
    return clean, tags