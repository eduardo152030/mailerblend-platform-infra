import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from supabase import create_client, Client

APP_NAME = os.getenv("APP_NAME", "eva-assistant-bot")
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

app = FastAPI(title=APP_NAME)

def get_supabase() -> Client | None:
    if not SUPABASE_URL or not SUPABASE_KEY:
        return None
    return create_client(SUPABASE_URL, SUPABASE_KEY)

@app.get("/health")
async def health():
    return {"status": "ok", "service": APP_NAME}

@app.get("/ready")
async def ready():
    sb = get_supabase()
    if sb is None:
        return JSONResponse(
            status_code=503,
            content={"status": "not_ready", "reason": "missing_supabase_env"}
        )

    try:
        sb.table("reminders").select("id").limit(1).execute()
        return {"status": "ready", "service": APP_NAME}
    except Exception as exc:
        return JSONResponse(
            status_code=503,
            content={"status": "not_ready", "reason": str(exc)}
        )

@app.post("/telegram/webhook")
async def telegram_webhook(request: Request):
    payload = await request.json()
    return {"status": "accepted", "payload_type": list(payload.keys())}
