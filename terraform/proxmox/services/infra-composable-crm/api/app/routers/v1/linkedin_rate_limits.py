"""
Router: LinkedIn Rate Limits
Configuración de límites globales editables desde UI
"""
from fastapi import APIRouter, Depends, Query, Body, HTTPException
from typing import Optional, Dict, Any
from uuid import UUID
from asyncpg import Connection

from app.db import get_db


router = APIRouter(
    prefix="/v1/linkedin-sourcing/rate-limits",
    tags=["LinkedIn Rate Limits"]
)


@router.get("")
async def list_rate_limits(
    is_active: bool = Query(True),
    conn: Connection = Depends(get_db)
) -> Dict[str, Any]:
    """Listar todos los rate limits."""
    rows = await conn.fetch(
        """
        SELECT *
        FROM linkedin_rate_limits
        WHERE is_active = $1
        ORDER BY limit_type
        """,
        is_active
    )
    
    return {
        "items": [dict(r) for r in rows],
        "count": len(rows)
    }


@router.get("/{limit_type}")
async def get_rate_limit(
    limit_type: str,
    conn: Connection = Depends(get_db)
) -> Dict[str, Any]:
    """Obtener un rate limit específico."""
    row = await conn.fetchrow(
        "SELECT * FROM linkedin_rate_limits WHERE limit_type = $1",
        limit_type
    )
    
    if not row:
        raise HTTPException(404, f"Rate limit '{limit_type}' not found")
    
    return dict(row)


@router.patch("/{limit_type}")
async def update_rate_limit(
    limit_type: str,
    payload: Dict[str, Any] = Body(...),
    conn: Connection = Depends(get_db)
) -> Dict[str, Any]:
    """
    Actualizar valor de un rate limit.
    
    Payload: {"limit_value": 25, "description": "..."}
    """
    exists = await conn.fetchval(
        "SELECT id FROM linkedin_rate_limits WHERE limit_type = $1",
        limit_type
    )
    if not exists:
        raise HTTPException(404, f"Rate limit '{limit_type}' not found")
    
    updates = []
    args = []
    i = 1
    
    if "limit_value" in payload:
        updates.append(f"limit_value = ${i}")
        args.append(int(payload["limit_value"]))
        i += 1
    
    if "description" in payload:
        updates.append(f"description = ${i}")
        args.append(payload["description"])
        i += 1
    
    if "is_active" in payload:
        updates.append(f"is_active = ${i}")
        args.append(payload["is_active"])
        i += 1
    
    if not updates:
        raise HTTPException(400, "No fields to update")
    
    updates.append("updated_at = NOW()")
    args.append(limit_type)
    
    await conn.execute(
        f"UPDATE linkedin_rate_limits SET {', '.join(updates)} WHERE limit_type = ${i}",
        *args
    )
    
    return {"limit_type": limit_type, "updated": True}


@router.get("/current/status")
async def get_current_status(
    conn: Connection = Depends(get_db)
) -> Dict[str, Any]:
    """
    Estado actual del rate limiting HOY.
    
    Retorna:
    - Invites enviadas hoy
    - Mensajes enviados hoy
    - Cap global de invites
    - Cap global de mensajes
    - ¿Puede enviar más?
    """
    # Obtener caps globales
    daily_invites_cap = await conn.fetchval(
        """
        SELECT limit_value FROM linkedin_rate_limits
        WHERE limit_type = 'DAILY_INVITES_GLOBAL' AND is_active = TRUE
        """
    ) or 20
    
    daily_messages_cap = await conn.fetchval(
        """
        SELECT limit_value FROM linkedin_rate_limits
        WHERE limit_type = 'DAILY_MESSAGES_GLOBAL' AND is_active = TRUE
        """
    ) or 50
    
    # Contar actividad hoy
    invites_today = await conn.fetchval(
        """
        SELECT COUNT(*)::int FROM linkedin_activity_log
        WHERE activity_type = 'INVITE'
          AND executed_at >= CURRENT_DATE
          AND executed_at < CURRENT_DATE + INTERVAL '1 day'
        """
    ) or 0
    
    messages_today = await conn.fetchval(
        """
        SELECT COUNT(*)::int FROM linkedin_activity_log
        WHERE activity_type = 'MESSAGE'
          AND executed_at >= CURRENT_DATE
          AND executed_at < CURRENT_DATE + INTERVAL '1 day'
        """
    ) or 0
    
    # ¿Hay cooldown activo?
    cooldown_active = await conn.fetchval(
        """
        SELECT EXISTS(
            SELECT 1 FROM linkedin_cooldowns
            WHERE is_active = TRUE AND cooldown_end > NOW()
        )
        """
    )
    
    return {
        "invites": {
            "sent_today": invites_today,
            "cap": daily_invites_cap,
            "remaining": max(0, daily_invites_cap - invites_today),
            "can_send": invites_today < daily_invites_cap and not cooldown_active
        },
        "messages": {
            "sent_today": messages_today,
            "cap": daily_messages_cap,
            "remaining": max(0, daily_messages_cap - messages_today),
            "can_send": messages_today < daily_messages_cap and not cooldown_active
        },
        "cooldown_active": bool(cooldown_active)
    }