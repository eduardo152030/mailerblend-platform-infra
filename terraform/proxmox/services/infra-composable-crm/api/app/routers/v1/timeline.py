from __future__ import annotations

from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, Query, HTTPException
from asyncpg import Connection

from app.db import get_db

router = APIRouter(prefix="/v1/timeline", tags=["timeline"])


def _clamp_limit(limit: int) -> int:
    if limit < 1:
        return 1
    if limit > 200:
        return 200
    return limit


@router.get("")
async def list_timeline(
    contacto_id: Optional[UUID] = Query(None),
    oportunidad_id: Optional[UUID] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    type: Optional[str] = Query(None, min_length=1, max_length=50),
    q: Optional[str] = Query(None, min_length=1, max_length=200),
    since: Optional[datetime] = Query(None),
    until: Optional[datetime] = Query(None),
    conn: Connection = Depends(get_db),
) -> Dict[str, Any]:
    """
    Timeline paginable para Budibase.
    Requiere contacto_id o oportunidad_id.
    """
    if not contacto_id and not oportunidad_id:
        raise HTTPException(status_code=400, detail="Provide contacto_id or oportunidad_id")

    limit = _clamp_limit(limit)

    where: List[str] = []
    args: List[Any] = []
    i = 1

    if contacto_id:
        where.append(f"contacto_id = ${i}")
        args.append(contacto_id)
        i += 1

    if oportunidad_id:
        where.append(f"oportunidad_id = ${i}")
        args.append(oportunidad_id)
        i += 1

    if type:
        where.append(f"type = ${i}")
        args.append(type)
        i += 1

    if since:
        where.append(f"created_at >= ${i}")
        args.append(since)
        i += 1

    if until:
        where.append(f"created_at <= ${i}")
        args.append(until)
        i += 1

    if q:
        q_like = f"%{q}%"
        where.append(f"(subject ILIKE ${i} OR notes ILIKE ${i})")
        args.append(q_like)
        i += 1

    where_sql = "WHERE " + " AND ".join(where)

    rows = await conn.fetch(
        f"""
        SELECT *
        FROM historial
        {where_sql}
        ORDER BY COALESCE(activity_date, created_at) DESC NULLS LAST, id DESC
        LIMIT ${i} OFFSET ${i+1}
        """,
        *args,
        limit,
        offset,
    )

    total = await conn.fetchval(
        f"SELECT count(*)::int FROM historial {where_sql}",
        *args,
    )

    items = [dict(r) for r in rows]
    return {"items": items, "limit": limit, "offset": offset, "count": len(items), "total": int(total or 0)}
