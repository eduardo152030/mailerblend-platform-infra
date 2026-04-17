"""
publishing_channels.py — Sistema de recordatorios de publicación por canal

Endpoints REST para gestionar canales de publicación (LinkedIn, YouTube, TikTok).
Se monta en main.py con: app.include_router(publishing_router)

Tabla: publishing_channels
"""

from datetime import datetime, timezone
from typing import Optional
from zoneinfo import ZoneInfo
import os

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from sqlalchemy import select, text

from db import SessionLocal
from models import User

publishing_router = APIRouter(prefix="/publishing", tags=["publishing"])

TZ = ZoneInfo(os.getenv("TIMEZONE", "Europe/Madrid"))


# ── Helpers ───────────────────────────────────────────────────────────────

def _serialize_channel(row) -> dict:
    last_pub = row[4]
    tpw = float(row[7]) if row[7] else None
    tpd = float(row[8]) if row[8] else None
    max_days = row[5]

    # Umbral calculado igual que en check_publishing_reminders
    threshold = _compute_max_days(max_days, tpw, tpd)

    days_since = None
    if last_pub:
        if last_pub.tzinfo is None:
            last_pub = last_pub.replace(tzinfo=TZ)
        delta = (datetime.now(TZ) - last_pub)
        days_since = round(delta.total_seconds() / 86400, 2)

    return {
        "id":                       row[0],
        "user_id":                  row[1],
        "channel":                  row[2],
        "display_name":             row[3],
        "last_published_at":        last_pub.isoformat() if last_pub else None,
        "days_since_last_post":     days_since,
        "max_days_without_posting": max_days,
        "enabled":                  row[6],
        "target_posts_per_week":    tpw,
        "target_posts_per_day":     tpd,
        "threshold_days":           round(threshold, 2),  # umbral calculado visible
        "needs_reminder":           (days_since is not None
                                     and days_since >= threshold
                                     and bool(row[6])),
    }


def _get_default_user_id(db) -> int | None:
    user = db.execute(select(User).limit(1)).scalars().first()
    return user.id if user else None


# ── Endpoints ─────────────────────────────────────────────────────────────

@publishing_router.get("/channels")
async def list_channels():
    """Lista todos los canales de publicación con estado actual."""
    db = SessionLocal()
    try:
        rows = db.execute(text("""
            SELECT id, user_id, channel, display_name, last_published_at,
                   max_days_without_posting, enabled,
                   target_posts_per_week, target_posts_per_day
            FROM publishing_channels
            ORDER BY channel
        """)).fetchall()
        return {"channels": [_serialize_channel(r) for r in rows]}
    finally:
        db.close()


@publishing_router.patch("/channels/{channel_id}")
async def update_channel(channel_id: int, request: Request):
    """
    Actualiza configuración de un canal.
    Acepta: last_published_at, max_days_without_posting, enabled,
            target_posts_per_week, target_posts_per_day
    """
    db = SessionLocal()
    try:
        body = await request.json()
        updates = []
        params = {"id": channel_id}

        if "last_published_at" in body:
            updates.append("last_published_at = :last_pub")
            val = body["last_published_at"]
            params["last_pub"] = datetime.fromisoformat(val) if val else None

        if "max_days_without_posting" in body:
            updates.append("max_days_without_posting = :max_days")
            params["max_days"] = int(body["max_days_without_posting"])

        if "enabled" in body:
            updates.append("enabled = :enabled")
            params["enabled"] = bool(body["enabled"])

        if "target_posts_per_week" in body:
            updates.append("target_posts_per_week = :tpw")
            params["tpw"] = body["target_posts_per_week"]

        if "target_posts_per_day" in body:
            updates.append("target_posts_per_day = :tpd")
            params["tpd"] = body["target_posts_per_day"]

        if not updates:
            return JSONResponse(status_code=400, content={"error": "nothing to update"})

        updates.append("updated_at = now()")
        db.execute(
            text(f"UPDATE publishing_channels SET {', '.join(updates)} WHERE id = :id"),
            params
        )
        db.commit()

        row = db.execute(text("""
            SELECT id, user_id, channel, display_name, last_published_at,
                   max_days_without_posting, enabled,
                   target_posts_per_week, target_posts_per_day
            FROM publishing_channels WHERE id = :id
        """), {"id": channel_id}).fetchone()

        return _serialize_channel(row)
    finally:
        db.close()


@publishing_router.post("/channels/{channel_id}/published-now")
async def mark_published_now(channel_id: int):
    """
    Marca el canal como publicado ahora mismo.
    Shortcut para actualizar last_published_at = now().
    """
    db = SessionLocal()
    try:
        db.execute(
            text("UPDATE publishing_channels SET last_published_at = now(), updated_at = now() WHERE id = :id"),
            {"id": channel_id}
        )
        db.commit()
        row = db.execute(text("""
            SELECT id, user_id, channel, display_name, last_published_at,
                   max_days_without_posting, enabled,
                   target_posts_per_week, target_posts_per_day
            FROM publishing_channels WHERE id = :id
        """), {"id": channel_id}).fetchone()
        return _serialize_channel(row)
    finally:
        db.close()


@publishing_router.post("/channels")
async def create_channel(request: Request):
    """Crea un nuevo canal de publicación."""
    db = SessionLocal()
    try:
        body = await request.json()
        user_id = _get_default_user_id(db)
        if not user_id:
            return JSONResponse(status_code=500, content={"error": "no_user"})

        db.execute(text("""
            INSERT INTO publishing_channels
                (user_id, channel, display_name, max_days_without_posting, enabled)
            VALUES (:uid, :ch, :dn, :max_days, :enabled)
            ON CONFLICT (user_id, channel) DO NOTHING
        """), {
            "uid": user_id,
            "ch": body["channel"].lower(),
            "dn": body.get("display_name", body["channel"].title()),
            "max_days": body.get("max_days_without_posting", 7),
            "enabled": body.get("enabled", True),
        })
        db.commit()
        return {"created": True}
    finally:
        db.close()


# ── Función para el scheduler ─────────────────────────────────────────────

def _compute_max_days(max_days: int, posts_per_week: float | None,
                      posts_per_day: float | None) -> float:
    """
    Calcula el umbral de días sin publicar antes de enviar alerta.

    Jerarquía (más específico gana):
    1. target_posts_per_day  → umbral = 1 / posts_per_day
    2. target_posts_per_week → umbral = 7 / posts_per_week
    3. max_days_without_posting → fallback simple

    Ejemplos:
      posts_per_day=2   → alerta a los 0.5 días (12h)
      posts_per_week=3  → alerta a los 2.3 días
      posts_per_week=1  → alerta a los 7 días
      max_days=14       → alerta a los 14 días
    """
    if posts_per_day and posts_per_day > 0:
        return 1.0 / posts_per_day
    if posts_per_week and posts_per_week > 0:
        return 7.0 / posts_per_week
    return float(max_days)


async def check_publishing_reminders(send_fn) -> int:
    """
    Revisa todos los canales activos y envía alerta si se supera el umbral.

    Lógica escalable:
    - Si target_posts_per_day está definido → umbral en horas/días
    - Si target_posts_per_week está definido → umbral en días
    - Fallback: max_days_without_posting

    Llamar desde run_scheduler.py una vez al día (ej: a las 09:00).
    """
    from datetime import timedelta
    db = SessionLocal()
    sent = 0
    try:
        rows = db.execute(text("""
            SELECT pc.id, pc.channel, pc.display_name,
                   pc.last_published_at, pc.max_days_without_posting,
                   pc.target_posts_per_week, pc.target_posts_per_day,
                   u.telegram_chat_id
            FROM publishing_channels pc
            JOIN users u ON u.id = pc.user_id
            WHERE pc.enabled = TRUE
              AND u.telegram_chat_id IS NOT NULL
        """)).fetchall()

        for row in rows:
            (ch_id, channel, display_name, last_pub,
             max_days, tpw, tpd, chat_id) = row

            # Calcular umbral dinámico
            threshold_days = _compute_max_days(
                max_days,
                float(tpw) if tpw else None,
                float(tpd) if tpd else None
            )

            if not last_pub:
                days_since = 999.0
            else:
                if last_pub.tzinfo is None:
                    last_pub = last_pub.replace(tzinfo=TZ)
                delta = datetime.now(TZ) - last_pub
                days_since = delta.total_seconds() / 86400  # días con decimales

            if days_since < threshold_days:
                continue

            # Formatear mensaje según granularidad
            if days_since < 1:
                time_str = f"{int(days_since * 24)} horas"
            elif days_since == 1:
                time_str = "1 día"
            else:
                time_str = f"{int(days_since)} días"

            # Contexto de frecuencia esperada
            if tpd and tpd > 0:
                freq_str = f"Frecuencia objetivo: {tpd:.1f}x/día."
            elif tpw and tpw > 0:
                freq_str = f"Frecuencia objetivo: {tpw:.1f}x/semana."
            else:
                freq_str = f"Objetivo: publicar cada {max_days} días."

            msg = (f"👋 Hey, llevas {time_str} sin publicar en {display_name}.\n"
                   f"{freq_str}\n"
                   f"¿Qué publicas hoy?")
            try:
                await send_fn(chat_id, msg)
                sent += 1
                print(f"[publishing] reminder sent for {display_name} "
                      f"({days_since:.1f} days, threshold {threshold_days:.1f})")
            except Exception as exc:
                print(f"[publishing] error sending reminder: {exc}")

    except Exception as exc:
        print(f"[publishing] check error: {exc}")
    finally:
        db.close()
    return sent