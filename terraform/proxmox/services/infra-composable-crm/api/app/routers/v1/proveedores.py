from __future__ import annotations

from typing import Optional, Dict, Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, Query, HTTPException, Body
from asyncpg import Connection

from app.db import get_db

router = APIRouter(prefix="/v1/proveedores", tags=["proveedores"])


def _clamp_limit(limit: int) -> int:
    return max(1, min(200, limit))


@router.get("")
async def list_proveedores(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    q: Optional[str] = Query(None, min_length=1, max_length=200),
    tipo: Optional[str] = Query(None, min_length=1, max_length=50),
    conn: Connection = Depends(get_db),
) -> Dict[str, Any]:
    limit = _clamp_limit(limit)

    where: List[str] = []
    args: List[Any] = []
    i = 1

    if tipo:
        where.append(f"tipo = ${i}")
        args.append(tipo)
        i += 1

    if q:
        q_like = f"%{q}%"
        where.append(f"(nombre ILIKE ${i} OR COALESCE(cif,'') ILIKE ${i})")
        args.append(q_like)
        i += 1

    where_sql = ("WHERE " + " AND ".join(where)) if where else ""

    rows = await conn.fetch(
        f"""
        SELECT *
        FROM proveedores
        {where_sql}
        ORDER BY nombre ASC
        LIMIT ${i} OFFSET ${i+1}
        """,
        *args,
        limit,
        offset,
    )

    total = await conn.fetchval(
        f"SELECT count(*)::int FROM proveedores {where_sql}",
        *args,
    )

    items = [dict(r) for r in rows]
    return {"items": items, "limit": limit, "offset": offset, "count": len(items), "total": int(total or 0)}


@router.get("/{proveedor_id}")
async def get_proveedor(
    proveedor_id: UUID,
    conn: Connection = Depends(get_db),
) -> Dict[str, Any]:
    row = await conn.fetchrow("SELECT * FROM proveedores WHERE id=$1", proveedor_id)
    if not row:
        raise HTTPException(status_code=404, detail="Proveedor not found")
    return dict(row)


@router.post("")
async def create_proveedor(
    payload: Dict[str, Any] = Body(...),
    conn: Connection = Depends(get_db),
) -> Dict[str, Any]:
    nombre = (payload.get("nombre") or "").strip()
    if not nombre:
        raise HTTPException(status_code=400, detail="nombre is required")

    tipo = (payload.get("tipo") or "OTRO").strip()

    row = await conn.fetchrow(
        """
        INSERT INTO proveedores (nombre, cif, tipo, email, telefono, website, notas)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        RETURNING *
        """,
        nombre,
        (payload.get("cif") or None),
        tipo,
        (payload.get("email") or None),
        (payload.get("telefono") or None),
        (payload.get("website") or None),
        (payload.get("notas") or None),
    )
    return dict(row)


@router.patch("/{proveedor_id}")
async def patch_proveedor(
    proveedor_id: UUID,
    payload: Dict[str, Any] = Body(...),
    conn: Connection = Depends(get_db),
) -> Dict[str, Any]:
    before = await conn.fetchrow("SELECT * FROM proveedores WHERE id=$1", proveedor_id)
    if not before:
        raise HTTPException(status_code=404, detail="Proveedor not found")

    editable = {"nombre", "cif", "tipo", "email", "telefono", "website", "notas"}
    updates = {k: payload.get(k) for k in editable if k in payload}
    if not updates:
        return dict(before)

    set_parts: List[str] = []
    args: List[Any] = []
    idx = 1
    for k, v in updates.items():
        set_parts.append(f"{k} = ${idx}")
        args.append(v)
        idx += 1

    args.append(proveedor_id)
    sql = f"UPDATE proveedores SET {', '.join(set_parts)} WHERE id = ${idx} RETURNING *"

    try:
        after = await conn.fetchrow(sql, *args)
    except Exception as e:
        msg = str(e)
        if "violates check constraint" in msg:
            raise HTTPException(status_code=400, detail=f"Invalid value (check constraint): {msg}")
        raise

    return dict(after)
