"""
telegram_service.py
====================
Backward-compatible wrapper. All existing imports continue to work:

    from telegram_service import send_message

Internally delegates to integrations/telegram_client.py.
Do NOT add new Telegram HTTP calls here — add them to telegram_client.py.
"""
from integrations.telegram_client import send_message  # noqa: F401 — re-exported

# Legacy helper kept for any code that still imports it directly
import os
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

def telegram_api_url(method: str) -> str:
    """Kept for backward compatibility. Prefer telegram_client internals."""
    return f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/{method}"
