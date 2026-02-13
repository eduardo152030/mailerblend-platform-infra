from __future__ import annotations

from typing import Optional, Dict, Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, Query, HTTPException, Body
from asyncpg import Connection

from app.db import get_db

router = APIRouter(prefix="/v1/oportunidades", tags=["oportunidades"])


def _clamp_limit(limit: int) -> int:
    if limit < 1:
        return 1
    if limit > 200:
        return 200
    return limit


@router.get("")
async def list_oportunidades(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),

    # search
    q: Optional[str] = Query(None, min_length=1, max_length=200),

    # filtros exactos
    estado: Optional[str] = Query(None, min_length=1, max_length=50),
    owner: Optional[str] = Query(None, min_length=1, max_length=200),
    next_action: Optional[str] = Query(None, min_length=1, max_length=50),
    lead_tag: Optional[str] = Query(None, min_length=1, max_length=50),
    prioridad: Optional[str] = Query(None, min_length=1, max_length=50),
    pack: Optional[str] = Query(None, min_length=1, max_length=50),

    conn: Connection = Depends(get_db),
) -> Dict[str, Any]:
    """
    Lista oportunidades para grid (Budibase) con filtros y paginación.
    """
    limit = _clamp_limit(limit)

    where: List[str] = []
    args: List[Any] = []
    i = 1

    if estado:
        where.append(f"estado = ${i}")
        args.append(estado)
        i += 1
    if owner:
        where.append(f"owner ILIKE ${i}")
        args.append(f"%{owner}%")
        i += 1
    if next_action:
        where.append(f"next_action = ${i}")
        args.append(next_action)
        i += 1
    if lead_tag:
        where.append(f"lead_tag = ${i}")
        args.append(lead_tag)
        i += 1
    if prioridad:
        where.append(f"prioridad = ${i}")
        args.append(prioridad)
        i += 1
    if pack:
        where.append(f"pack = ${i}")
        args.append(pack)
        i += 1

    if q:
        q_like = f"%{q}%"
        where.append(f"(deal_name ILIKE ${i} OR COALESCE(owner,'') ILIKE ${i} OR COALESCE(contacto_nombre,'') ILIKE ${i})")
        args.append(q_like)
        i += 1

    where_sql = ("WHERE " + " AND ".join(where)) if where else ""

    rows = await conn.fetch(
        f"""
        SELECT
          id,
          contacto_id,
          formulario_id,
          linkedin_lead_id,
          deal_name,
          pack,
          estado,
          prioridad,
          lead_tag,
          deal_value,
          currency,
          probabilidad,
          next_action,
          next_action_date,
          owner,
          team,
          expected_close_date,
          won_at,
          lost_at,
          lost_reason,
          updated_at,
          created_at,
          contacto_nombre
        FROM oportunidades
        {where_sql}
        ORDER BY created_at DESC NULLS LAST, id DESC
        LIMIT ${i} OFFSET ${i+1}
        """,
        *args,
        limit,
        offset,
    )

    total = await conn.fetchval(
        f"SELECT count(*)::int FROM oportunidades {where_sql}",
        *args,
    )

    items = [dict(r) for r in rows]
    return {"items": items, "limit": limit, "offset": offset, "count": len(items), "total": int(total or 0)}


@router.get("/{oportunidad_id}")
async def get_oportunidad(
    oportunidad_id: UUID,
    conn: Connection = Depends(get_db),
) -> Dict[str, Any]:
    row = await conn.fetchrow("SELECT * FROM oportunidades WHERE id = $1", oportunidad_id)
    if not row:
        raise HTTPException(status_code=404, detail="Oportunidad not found")
    return dict(row)


@router.get("/{oportunidad_id}/snapshot")
async def oportunidad_snapshot(
    oportunidad_id: UUID,
    historial_limit: int = Query(200, ge=1, le=200),
    historial_offset: int = Query(0, ge=0),
    conn: Connection = Depends(get_db),
) -> Dict[str, Any]:
    """
    Snapshot por oportunidad (Budibase-friendly):
    - oportunidad
    - contacto (mínimo)
    - historial filtrado por oportunidad_id (paginable)
    - pendientes por oportunidad_id
    - presupuestos por oportunidad_id
    - facturas por oportunidad_id
    """
    historial_limit = _clamp_limit(historial_limit)

    op = await conn.fetchrow("SELECT * FROM oportunidades WHERE id = $1", oportunidad_id)
    if not op:
        raise HTTPException(status_code=404, detail="Oportunidad not found")

    # contacto mínimo
    contacto = None
    if op.get("contacto_id"):
        contacto = await conn.fetchrow(
            """
            SELECT
              id,
              nombre,
              email,
              telefono,
              company_name,
              cargo
            FROM contactos
            WHERE id = $1
            """,
            op["contacto_id"],
        )

    # historial paginable por oportunidad_id
    historial_rows = await conn.fetch(
        """
        SELECT *
        FROM historial
        WHERE oportunidad_id = $1
        ORDER BY COALESCE(activity_date, created_at) DESC NULLS LAST, id DESC
        LIMIT $2 OFFSET $3
        """,
        oportunidad_id,
        historial_limit,
        historial_offset,
    )

    historial_total = await conn.fetchval(
        "SELECT count(*)::int FROM historial WHERE oportunidad_id = $1",
        oportunidad_id,
    )

    # pendientes por oportunidad_id (no DONE primero)
    pendientes_rows = await conn.fetch(
        """
        SELECT
          id,
          contacto_id,
          oportunidad_id,
          linkedin_lead_id,
          title,
          description,
          status,
          priority,
          assigned_to,
          due_date,
          due_time,
          reminder_enabled,
          reminder_datetime,
          completed_at,
          created_at,
          updated_at,
          created_by,
          contacto_nombre
        FROM pendientes
        WHERE oportunidad_id = $1
        ORDER BY
          CASE WHEN status = 'DONE' THEN 1 ELSE 0 END,
          due_date ASC NULLS LAST,
          created_at DESC NULLS LAST,
          id DESC
        LIMIT 200
        """,
        oportunidad_id,
    )

    # presupuestos por oportunidad_id (robusto: ordenar por id)
    presupuestos_rows = await conn.fetch(
        """
        SELECT *
        FROM presupuestos
        WHERE oportunidad_id = $1
        ORDER BY id DESC
        LIMIT 100
        """,
        oportunidad_id,
    )

    # facturas por oportunidad_id (robusto: ordenar por id)
    facturas_rows = await conn.fetch(
        """
        SELECT *
        FROM facturas
        WHERE oportunidad_id = $1
        ORDER BY id DESC
        LIMIT 100
        """,
        oportunidad_id,
    )

    return {
        "oportunidad": dict(op),
        "contacto": dict(contacto) if contacto else None,
        "historial": {
            "items": [dict(r) for r in historial_rows],
            "limit": historial_limit,
            "offset": historial_offset,
            "count": len(historial_rows),
            "total": int(historial_total or 0),
        },
        "pendientes": [dict(r) for r in pendientes_rows],
        "presupuestos": [dict(r) for r in presupuestos_rows],
        "facturas": [dict(r) for r in facturas_rows],
    }


@router.patch("/{oportunidad_id}")
async def patch_oportunidad(
    oportunidad_id: UUID,
    payload: Dict[str, Any] = Body(...),
    conn: Connection = Depends(get_db),
) -> Dict[str, Any]:
    """
    PATCH para Budibase: mover fase/estado + campos operativos.
    Auto-inserta historial: EVENT::STAGE_CHANGED con diff before/after.
    """
    before = await conn.fetchrow("SELECT * FROM oportunidades WHERE id = $1", oportunidad_id)
    if not before:
        raise HTTPException(status_code=404, detail="Oportunidad not found")

    # allowlist alineada a columnas reales en DB (sin expected_value)
    editable = {
        # pipeline
        "estado",
        "lead_tag",
        "prioridad",
        "next_action",
        "next_action_date",
        "probabilidad",

        # negocio
        "deal_value",
        "currency",
        "owner",
        "team",
        "pack",
        "deal_name",

        # cierre / pérdida
        "expected_close_date",
        "won_at",
        "lost_at",
        "lost_reason",
        "lost_reason_notes",

        # notas internas / tags
        "notas_internas",
        "tags",
    }

    updates = {k: v for k, v in payload.items() if k in editable}
    if not updates:
        return dict(before)

    set_parts: List[str] = []
    args: List[Any] = []
    idx = 1
    for k, v in updates.items():
        set_parts.append(f"{k} = ${idx}")
        args.append(v)
        idx += 1

    set_parts.append("updated_at = NOW()")
    sql = f"UPDATE oportunidades SET {', '.join(set_parts)} WHERE id = ${idx} RETURNING *"
    args.append(oportunidad_id)

    after = await conn.fetchrow(sql, *args)

    # diff
    diff: Dict[str, Any] = {}
    for k in updates.keys():
        b = before.get(k)
        a = after.get(k)
        if b != a:
            diff[k] = {"before": b, "after": a}

    if diff:
        contacto_id = after.get("contacto_id")
        await conn.execute(
            """
            INSERT INTO historial (
              contacto_id,
              oportunidad_id,
              type,
              subject,
              notes,
              activity_date,
              created_by
            ) VALUES (
              $1, $2, 'NOTE', 'EVENT::STAGE_CHANGED', $3::text, NOW(), 'api'
            )
            """,
            contacto_id,
            oportunidad_id,
            __import__("json").dumps({"diff": diff}),
        )

    return dict(after)