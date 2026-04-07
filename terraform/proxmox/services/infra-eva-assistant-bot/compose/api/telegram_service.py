import os
import httpx

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

def telegram_api_url(method: str) -> str:
    return f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/{method}"

async def send_message(chat_id: int, text: str) -> dict:
    async with httpx.AsyncClient(timeout=20.0) as client:
        resp = await client.post(
            telegram_api_url("sendMessage"),
            json={
                "chat_id": chat_id,
                "text": text,
            },
        )
        resp.raise_for_status()
        return resp.json()
