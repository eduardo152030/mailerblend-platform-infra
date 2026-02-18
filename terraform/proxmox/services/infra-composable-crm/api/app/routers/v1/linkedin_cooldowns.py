"""
Router: LinkedIn Cooldowns
Gestión de pausas automáticas por patrones o señales de riesgo
"""
from fastapi import APIRouter, Depends, Query, Body, HTTPException
from typing import Optional, Dict, Any
from uuid import UUID
from asyncpg import Connection
from datetime import datetime, timedelta
import json

from app.db import get_db


router = APIRouter(
    prefix="/v1/linkedin-sourcing/cooldowns",
    tags=["LinkedIn Cooldowns"]
)


@router.get("/status")
async def get_cooldown_status(
    conn: Connection = Depends(get_db)
) -> Dict[str, Any]:
    """
    Verifica si hay algún cooldown activo AHORA.
    """
    active_cooldown = await conn.fetchrow(
        """
        SELECT *
        FROM linkedin_cooldowns
        WHERE is_active = TRUE
          AND cooldown_end > NOW()
        ORDER BY cooldown_end DESC
        LIMIT 1
        """
    )
    
    if active_cooldown:
        remaining = active_cooldown["cooldown_end"] - datetime.now()
        return {
            "cooldown_active": True,
            "id": str(active_cooldown["id"]),
            "trigger_reason": active_cooldown["trigger_reason"],
            "cooldown_start": active_cooldown["cooldown_start"].isoformat(),
            "cooldown_end": active_cooldown["cooldown_end"].isoformat(),
            "remaining_hours": round(remaining.total_seconds() / 3600, 2),
            "metadata": active_cooldown["metadata"]
        }
    
    return {
        "cooldown_active": False
    }


@router.post("")
async def create_cooldown(
    payload: Dict[str, Any] = Body(...),
    conn: Connection = Depends(get_db)
) -> Dict[str, Any]:
    """
    Crear cooldown manual o automático.
    
    Payload:
    {
        "trigger_reason": "MANUAL|NEGATIVE_RESPONSES_SPIKE|...",
        "duration_hours": 48,
        "metadata": {...}
    }
    """
    trigger_reason = payload.get("trigger_reason")
    duration_hours = payload.get("duration_hours")
    
    if not trigger_reason or not duration_hours:
        raise HTTPException(400, "trigger_reason and duration_hours required")
    
    if duration_hours < 1 or duration_hours > 168:
        raise HTTPException(400, "duration_hours must be 1-168 (1 week max)")
    
    cooldown_end = datetime.now() + timedelta(hours=duration_hours)
    
    cooldown_id = await conn.fetchval(
        """
        INSERT INTO linkedin_cooldowns (
            trigger_reason,
            cooldown_end,
            metadata
        ) VALUES ($1, $2, $3::jsonb)
        RETURNING id
        """,
        trigger_reason,
        cooldown_end,
        json.dumps(payload.get("metadata", {}))
    )
    
    return {
        "id": str(cooldown_id),
        "cooldown_active": True,
        "trigger_reason": trigger_reason,
        "cooldown_end": cooldown_end.isoformat(),
        "duration_hours": duration_hours
    }


@router.get("")
async def list_cooldowns(
    is_active: Optional[bool] = Query(None),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    conn: Connection = Depends(get_db)
) -> Dict[str, Any]:
    """
    Listar cooldowns (histórico).
    """
    where = []
    args = []
    i = 1
    
    if is_active is not None:
        if is_active:
            # Activos ahora
            where.append("is_active = TRUE AND cooldown_end > NOW()")
        else:
            # Ya terminados
            where.append("(is_active = FALSE OR cooldown_end <= NOW())")
    
    where_sql = ("WHERE " + " AND ".join(where)) if where else ""
    
    rows = await conn.fetch(
        f"""
        SELECT * FROM linkedin_cooldowns
        {where_sql}
        ORDER BY cooldown_start DESC
        LIMIT ${i} OFFSET ${i+1}
        """,
        limit,
        offset
    )
    
    total = await conn.fetchval(
        f"SELECT COUNT(*)::int FROM linkedin_cooldowns {where_sql}"
    )
    
    return {
        "items": [dict(r) for r in rows],
        "limit": limit,
        "offset": offset,
        "count": len(rows),
        "total": int(total or 0)
    }


@router.patch("/{cooldown_id}/cancel")
async def cancel_cooldown(
    cooldown_id: UUID,
    reason: str = Body(..., embed=True),
    conn: Connection = Depends(get_db)
) -> Dict[str, Any]:
    """
    Cancelar cooldown manualmente.
    """
    exists = await conn.fetchval(
        "SELECT id FROM linkedin_cooldowns WHERE id = $1",
        cooldown_id
    )
    if not exists:
        raise HTTPException(404, "Cooldown not found")
    
    await conn.execute(
        """
        UPDATE linkedin_cooldowns
        SET 
            is_active = FALSE,
            metadata = jsonb_set(
                COALESCE(metadata, '{}'::jsonb),
                '{cancelled_reason}',
                $2::jsonb
            )
        WHERE id = $1
        """,
        cooldown_id,
        json.dumps(reason)
    )
    
    return {
        "id": str(cooldown_id),
        "cancelled": True,
        "reason": reason
    }


@router.get("/stats")
async def get_cooldown_stats(
    days: int = Query(30, ge=1, le=90),
    conn: Connection = Depends(get_db)
) -> Dict[str, Any]:
    """
    Estadísticas de cooldowns por razón.
    """
    rows = await conn.fetch(
        f"""
        SELECT
            trigger_reason,
            COUNT(*) as count,
            AVG(EXTRACT(EPOCH FROM (cooldown_end - cooldown_start)) / 3600) as avg_duration_hours
        FROM linkedin_cooldowns
        WHERE cooldown_start >= CURRENT_DATE - INTERVAL '{days} days'
        GROUP BY trigger_reason
        ORDER BY count DESC
        """
    )
    
    stats = []
    for row in rows:
        stats.append({
            "trigger_reason": row["trigger_reason"],
            "count": row["count"],
            "avg_duration_hours": round(row["avg_duration_hours"], 2) if row["avg_duration_hours"] else 0
        })
    
    return {
        "stats": stats,
        "days": days,
        "total_cooldowns": sum(s["count"] for s in stats)
    }