"""
core/config.py
==============
Single source of truth for all environment variables and constants.

If you need to add a new env var or Focalboard property ID, this is the only
file you need to touch.
"""
import os
from zoneinfo import ZoneInfo

# ── App ───────────────────────────────────────────────────────────────────
APP_NAME         = os.getenv("APP_NAME", "eva-assistant-bot")
DEFAULT_TIMEZONE = os.getenv("TIMEZONE", "Europe/Madrid")
TZ               = ZoneInfo(DEFAULT_TIMEZONE)

# ── Focalboard — Tasks board ──────────────────────────────────────────────
FOCALBOARD_URL      = os.getenv("FOCALBOARD_URL", "")
FOCALBOARD_TOKEN    = os.getenv("FOCALBOARD_TOKEN", "")
FOCALBOARD_BOARD_ID = os.getenv("FOCALBOARD_BOARD_ID", "boshzqexyfjb6zbxhwgg3s8m7hr")

# Task board property IDs
STATUS_PROP_ID   = "aevastatus00000000000000001"
PRIORITY_PROP_ID = "ann9q8kbmc67mb7p4d8xrmma6rr"
DATE_PROP_ID     = "a14y4uzprb1maieayt1ouhca47o"
TEXT_PROP_ID     = "a6bxuk4rgxp7wn6bashiadwaiiy"
URL_PROP_ID      = "asztuket5mjeeongrzooyx5utbo"

STATUS_OPTIONS = {
    "pending":     "aoptpendiente00000000000001",
    "scheduled":   "aoptpendiente00000000000001",
    "sent":        "aoptpendiente00000000000001",
    "in_progress": "atknam74n43b9rezq13w9tz8dsc",
    "completed":   "aoptcompletado0000000000001",
    "cancelled":   "aoptcancelado00000000000001",
    "expired":     "aoptcancelado00000000000001",
}

PRIORITY_OPTIONS = {
    "P0": "akgjwzzkom6j5hnqkw5nxaq4pmo",
    "P1": "a44z9q4cj9jamiqip5gih6okzco",
    "P2": "aqtsqbngmejgxwswgciahqubfoo",
    "P3": "argk36ea34napsf8dq78d4pg8go",
    "P4": "auoqqox58bui398gu1itti85d9a",
}

# ── Focalboard — Content board ────────────────────────────────────────────
CONTENT_BOARD_ID      = os.getenv("FOCALBOARD_CONTENT_BOARD_ID", "bbhzrrkbxubgm8brd7bmoinekbr")
CONTENT_STATUS_PROP   = "content_status_001"
CONTENT_FORMATO_PROP  = "content_formato_001"
CONTENT_PROYECTO_PROP = "content_proyecto_001"
CONTENT_FECHAPUB_PROP = "content_fechapub_001"
CONTENT_LINK_PROP     = "content_link_001"
CONTENT_LOCATION_PROP = "content_location_001"
CONTENT_PRIORITY_PROP = "content_priority_001"

CONTENT_PRIORITY_DEFAULT = "argk36ea34napsf8dq78d4pg8go"  # P3
CONTENT_PRIORITY_MAP = {
    "P0": "akgjwzzkom6j5hnqkw5nxaq4pmo",
    "P1": "a44z9q4cj9jamiqip5gih6okzco",
    "P2": "aqtsqbngmejgxwswgciahqubfoo",
    "P3": "argk36ea34napsf8dq78d4pg8go",
    "P4": "auoqqox58bui398gu1itti85d9a",
}
CONTENT_STATUS_IDEA  = "copt_idea"

# ⚠️  To add a new project tag, add it here only.
CONTENT_PROYECTO_MAP = {
    "#mailerblend": "copt_mailerblend",
    "#nt":          "copt_nt",
    "#personal":    "copt_personal",
    "#tradeintuit": "copt_tradeintuit",
}
CONTENT_FORMATO_MAP = {
    "youtube":  "copt_youtube",
    "short":    "copt_shortreel",
    "reel":     "copt_shortreel",
    "linkedin": "copt_linkedin",
}

# ── Attachments ───────────────────────────────────────────────────────────
UPLOADS_DIR    = os.getenv("UPLOADS_DIR", "/app/uploads")
MAX_FILE_SIZE  = 20 * 1024 * 1024  # 20 MB
ALLOWED_MIME_TYPES = {
    "image/jpeg", "image/png", "image/gif", "image/webp",
    "application/pdf",
    "text/plain",
}

# ── EVA UI ────────────────────────────────────────────────────────────────
# ⚠️  Change here OR set EVA_UI_URL env var when migrating to own subdomain.
EVA_UI_URL   = os.getenv("EVA_UI_URL", "https://eva-flow.lovable.app")
SELF_API_URL = os.getenv("SELF_API_URL", "http://localhost:8000")

# ── Telegram ──────────────────────────────────────────────────────────────
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
