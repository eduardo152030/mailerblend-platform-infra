"""
Router: LinkedIn Activity Log
Registro de toda actividad para rate limiting y análisis
"""
from fastapi import APIRouter, Depends, Query, Body, HTTPException
from typing import Optional, Dict, Any
from uuid import UUID
from asyncpg import Connection
from datetime import datetime, timedelta
import json

from app.db import get_db


router = APIRouter(
    prefix="/v1/linkedin-sourcing/activity-log",
    tags=["LinkedIn Activity Log"]
)


@router.post("")
async def log_activity(
    payload: Dict[str, Any] = Body(...),
    conn: Connection = Depends(get_db)
) -> Dict[str, Any]:
    """
    Registrar actividad.
    
    Payload:
    {
        "activity_type": "INVITE|MESSAGE|PROFILE_VIEW|SEARCH|...",
        "metadata": {...},
        "risk_level": "LOW|MEDIUM|HIGH"
    }
    """
    activity_type = payload.get("activity_type")
    if not activity_type:
        raise HTTPException(400, "activity_type is required")
    
    valid_types = (
        "INVITE", "MESSAGE", "PROFILE_VIEW", "SEARCH",
        "CONNECTION_ACCEPT", "POST_ENGAGEMENT", "LINK_CLICK"
    )
    if activity_type not in valid_types:
        raise HTTPException(
            400,
            f"activity_type must be one of: {', '.join(valid_types)}"
        )
    
    log_id = await conn.fetchval(
        """
        INSERT INTO linkedin_activity_log (
            activity_type,
            metadata,
            risk_level
        ) VALUES ($1, $2::jsonb, $3)
        RETURNING id
        """,
        activity_type,
        json.dumps(payload.get("metadata", {})),
        payload.get("risk_level", "LOW")
    )
    
    return {
        "id": str(log_id),
        "activity_type": activity_type,
        "logged_at": datetime.now().isoformat()
    }


@router.get("")
async def list_activity(
    activity_type: Optional[str] = Query(None),
    hours: int = Query(24, ge=1, le=168),  # Últimas X horas
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    conn: Connection = Depends(get_db)
) -> Dict[str, Any]:
    """
    Listar actividad reciente.
    """
    where = [f"executed_at >= NOW() - INTERVAL '{hours} hours'"]
    args = []
    i = 1
    
    if activity_type:
        where.append(f"activity_type = ${i}")
        args.append(activity_type)
        i += 1
    
    where_sql = "WHERE " + " AND ".join(where)
    
    rows = await conn.fetch(
        f"""
        SELECT * FROM linkedin_activity_log
        {where_sql}
        ORDER BY executed_at DESC
        LIMIT ${i} OFFSET ${i+1}
        """,
        *args,
        limit,
        offset
    )
    
    total = await conn.fetchval(
        f"SELECT COUNT(*)::int FROM linkedin_activity_log {where_sql}",
        *args
    )
    
    return {
        "items": [dict(r) for r in rows],
        "limit": limit,
        "offset": offset,
        "count": len(rows),
        "total": int(total or 0),
        "hours": hours
    }


@router.get("/stats/daily")
async def get_daily_stats(
    days: int = Query(7, ge=1, le=30),
    conn: Connection = Depends(get_db)
) -> Dict[str, Any]:
    """
    Estadísticas diarias de actividad.
    """
    rows = await conn.fetch(
        f"""
        SELECT
            DATE(executed_at) as date,
            activity_type,
            COUNT(*) as count
        FROM linkedin_activity_log
        WHERE executed_at >= CURRENT_DATE - INTERVAL '{days} days'
        GROUP BY DATE(executed_at), activity_type
        ORDER BY date DESC, activity_type
        """
    )
    
    # Agrupar por fecha
    stats_by_date = {}
    for row in rows:
        date_str = row["date"].isoformat()
        if date_str not in stats_by_date:
            stats_by_date[date_str] = {}
        stats_by_date[date_str][row["activity_type"]] = row["count"]
    
    return {
        "stats": stats_by_date,
        "days": days
    }


@router.get("/stats/today")
async def get_today_stats(
    conn: Connection = Depends(get_db)
) -> Dict[str, Any]:
    """
    Estadísticas de HOY (útil para dashboards).
    """
    rows = await conn.fetch(
        """
        SELECT
            activity_type,
            COUNT(*) as count
        FROM linkedin_activity_log
        WHERE executed_at >= CURRENT_DATE
          AND executed_at < CURRENT_DATE + INTERVAL '1 day'
        GROUP BY activity_type
        """
    )
    
    stats = {row["activity_type"]: row["count"] for row in rows}
    
    # Añadir invites y messages explícitamente (aunque sean 0)
    for key in ["INVITE", "MESSAGE", "PROFILE_VIEW"]:
        if key not in stats:
            stats[key] = 0
    
    return {
        "date": datetime.now().date().isoformat(),
        "stats": stats,
        "total": sum(stats.values())
    }


@router.delete("/cleanup")
async def cleanup_old_logs(
    days_to_keep: int = Query(30, ge=7, le=365),
    dry_run: bool = Query(True),
    conn: Connection = Depends(get_db)
) -> Dict[str, Any]:
    """
    Limpiar logs antiguos (por defecto solo cuenta, no elimina).
    """
    count_query = f"""
        SELECT COUNT(*)::int FROM linkedin_activity_log
        WHERE executed_at < CURRENT_DATE - INTERVAL '{days_to_keep} days'
    """
    
    count = await conn.fetchval(count_query) or 0
    
    if not dry_run and count > 0:
        await conn.execute(
            f"""
            DELETE FROM linkedin_activity_log
            WHERE executed_at < CURRENT_DATE - INTERVAL '{days_to_keep} days'
            """
        )
        return {
            "deleted": count,
            "days_to_keep": days_to_keep,
            "dry_run": False
        }
    
    return {
        "would_delete": count,
        "days_to_keep": days_to_keep,
        "dry_run": True
    }