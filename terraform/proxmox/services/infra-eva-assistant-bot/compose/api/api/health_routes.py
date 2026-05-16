"""
api/health_routes.py
====================
Health and readiness endpoints.
To debug: if /health fails, the container is down. If /ready fails, DB is down.
"""
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import text

from db import engine
from core.config import APP_NAME

router = APIRouter()


@router.get("/")
async def root():
    return {"service": APP_NAME, "message": "EVA API running"}


@router.get("/health")
async def health():
    return {"status": "ok", "service": APP_NAME}


@router.get("/ready")
async def ready():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ready", "service": APP_NAME}
    except Exception as exc:
        return JSONResponse(
            status_code=503,
            content={"status": "not_ready", "reason": str(exc)},
        )
