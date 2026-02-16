from __future__ import annotations

from typing import Optional, Dict, Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, Query, HTTPException, Body
from asyncpg import Connection

from app.db import get_db

router = APIRouter(prefix="/v1/presupuestos", tags=["presupuestos"])


# -------------------------
# Helpers
# -------------------------
def _clamp_limit(limit: int) -> int:
    if limit < 1:
        return 1
    if limit > 200:
        return 200
    return limit


def _now_ymd() -> str:
    import datetime
    return datetime.datetime.utcnow().strftime("%Y%m%d")


def _make_quote_number() -> str:
    # Q-YYYYMMDD-<6hex>
    import secrets
    return f"Q-{_now_ymd()}-{secrets.token_hex(3).upper()}"


def _as_date_str_or_none(v: Any) -> Optional[str]:
    """
    Acepta 'YYYY-MM-DD' y devuelve str para que el SQL haga ::date.
    Si viene None o '', devuelve None.
    """
    if v is None:
        return None
    if isinstance(v, str):
        s = v.strip()
        return s or None
    try:
        return str(v)
    except Exception:
        return None


def _as_ts_or_none(v: Any) -> Optional[str]:
    """
    Acepta ISO string y devuelve str para que el SQL haga ::timestamptz.
    """
    if v is None:
        return None
    if isinstance(v, str):
        s = v.strip()
        return s or None
    try:
        return str(v)
    except Exception:
        return None


def _event_for_status_transition(before_status: Optional[str], after_status: Optional[str]) -> Optional[str]:
    """
    Mapea transición de estado a evento específico.
    """
    if not after_status:
        return None

    b = (before_status or "").strip()
    a = (after_status or "").strip()

    if b != a:
        if a == "Sent":
            return "EVENT::QUOTE_SENT"
        if a == "Accepted":
            return "EVENT::QUOTE_ACCEPTED"
        if a == "Rejected":
            return "EVENT::QUOTE_REJECTED"
        if a == "Expired":
            return "EVENT::QUOTE_EXPIRED"

    return None


async def _insert_historial(
    conn: Connection,
    *,
    contacto_id: UUID,
    oportunidad_id: UUID,
    subject: str,
    notes_obj: Dict[str, Any],
) -> None:
    """
    Estilo oportunidades.py:
    historial.type='NOTE'
    historial.subject='EVENT::...'
    historial.notes = JSON string
    """
    import json

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
            $1, $2, 'NOTE', $3, $4::text, NOW(), 'api'
        )
        """,
        contacto_id,
        oportunidad_id,
        subject,
        json.dumps(notes_obj, default=str),
    )


async def _get_presupuestos_columns(conn: Connection) -> set[str]:
    rows = await conn.fetch(
        """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema='public' AND table_name='presupuestos'
        """
    )
    return {r["column_name"] for r in rows}


# -------------------------
# Endpoints
# -------------------------
@router.get("")
async def list_presupuestos(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),

    q: Optional[str] = Query(None, min_length=1, max_length=200),

    # filtros Budibase
    status: Optional[str] = Query(None, min_length=1, max_length=50),
    contacto_id: Optional[UUID] = Query(None),
    oportunidad_id: Optional[UUID] = Query(None),
    valid_until_before: Optional[str] = Query(None, description="YYYY-MM-DD"),

    conn: Connection = Depends(get_db),
) -> Dict[str, Any]:
    limit = _clamp_limit(limit)

    where: List[str] = []
    args: List[Any] = []
    i = 1

    if status:
        where.append(f"status = ${i}")
        args.append(status)
        i += 1

    if contacto_id:
        where.append(f"contacto_id = ${i}")
        args.append(contacto_id)
        i += 1

    if oportunidad_id:
        where.append(f"oportunidad_id = ${i}")
        args.append(oportunidad_id)
        i += 1

    if valid_until_before:
        where.append(f"valid_until < ${i}::date")
        args.append(valid_until_before)
        i += 1

    if q:
        q_like = f"%{q}%"
        where.append(
            f"(quote_number ILIKE ${i} OR title ILIKE ${i} OR "
            f"COALESCE(contacto_nombre,'') ILIKE ${i} OR COALESCE(notes,'') ILIKE ${i})"
        )
        args.append(q_like)
        i += 1

    where_sql = ("WHERE " + " AND ".join(where)) if where else ""

    rows = await conn.fetch(
        f"""
        SELECT
            id,
            contacto_id,
            oportunidad_id,
            quote_number,
            title,
            version,
            quote_value,
            currency,
            status,
            created_at,
            updated_at,
            sent_at,
            valid_until,
            accepted_at,
            rejected_at,
            pdf_url,
            notes,
            internal_notes,
            contacto_nombre
        FROM presupuestos
        {where_sql}
        ORDER BY updated_at DESC NULLS LAST, created_at DESC NULLS LAST, id DESC
        LIMIT ${i} OFFSET ${i+1}
        """,
        *args,
        limit,
        offset,
    )

    total = await conn.fetchval(
        f"SELECT count(*)::int FROM presupuestos {where_sql}",
        *args,
    )

    items = [dict(r) for r in rows]
    return {
        "items": items,
        "limit": limit,
        "offset": offset,
        "count": len(items),
        "total": int(total or 0),
    }


@router.get("/{presupuesto_id}")
async def get_presupuesto(
    presupuesto_id: UUID,
    conn: Connection = Depends(get_db),
) -> Dict[str, Any]:
    row = await conn.fetchrow("SELECT * FROM presupuestos WHERE id = $1", presupuesto_id)
    if not row:
        raise HTTPException(status_code=404, detail="Presupuesto not found")
    return dict(row)


@router.post("")
async def create_presupuesto(
    payload: Dict[str, Any] = Body(...),
    conn: Connection = Depends(get_db),
) -> Dict[str, Any]:
    """
    Crea un presupuesto.
    Requiere contacto_id y oportunidad_id (NOT NULL en DB).
    Si no envías quote_number, se autogenera.
    Inserta historial: EVENT::QUOTE_CREATED
    """
    contacto_id = payload.get("contacto_id")
    oportunidad_id = payload.get("oportunidad_id")

    if not contacto_id or not oportunidad_id:
        raise HTTPException(status_code=400, detail="contacto_id y oportunidad_id son requeridos")

    quote_number = payload.get("quote_number") or _make_quote_number()
    title = payload.get("title")
    quote_value = payload.get("quote_value")

    if not title:
        raise HTTPException(status_code=400, detail="title es requerido")
    if quote_value is None:
        raise HTTPException(status_code=400, detail="quote_value es requerido")

    version = payload.get("version", 1)
    currency = payload.get("currency", "EUR")
    line_items = payload.get("line_items")
    status = payload.get("status", "Draft")

    sent_at = _as_ts_or_none(payload.get("sent_at"))
    valid_until = _as_date_str_or_none(payload.get("valid_until"))
    accepted_at = _as_ts_or_none(payload.get("accepted_at"))
    rejected_at = _as_ts_or_none(payload.get("rejected_at"))

    pdf_url = payload.get("pdf_url")
    notes = payload.get("notes")
    internal_notes = payload.get("internal_notes")

    # Convert date strings to proper types for asyncpg
    from datetime import date, datetime
    
    def parse_date(val):
        if val is None:
            return None
        if isinstance(val, date):
            return val
        if isinstance(val, str):
            return datetime.strptime(val.strip(), "%Y-%m-%d").date()
        return None
    
    def parse_timestamp(val):
        if val is None:
            return None
        if isinstance(val, datetime):
            return val
        if isinstance(val, str):
            return datetime.fromisoformat(val.strip().replace('Z', '+00:00'))
        return None

    try:
        row = await conn.fetchrow(
            """
            INSERT INTO presupuestos (
                contacto_id,
                oportunidad_id,
                quote_number,
                title,
                version,
                quote_value,
                currency,
                line_items,
                status,
                sent_at,
                valid_until,
                accepted_at,
                rejected_at,
                pdf_url,
                notes,
                internal_notes,
                created_at,
                updated_at
            ) VALUES (
                $1,$2,$3,$4,$5,$6,$7,$8,$9,
                $10,$11,$12,$13,$14,$15,$16,
                NOW(), NOW()
            )
            RETURNING *
            """,
            UUID(str(contacto_id)),
            UUID(str(oportunidad_id)),
            quote_number,
            title,
            int(version) if version is not None else 1,
            quote_value,
            currency,
            line_items,
            status,
            parse_timestamp(sent_at),
            parse_date(valid_until),
            parse_timestamp(accepted_at),
            parse_timestamp(rejected_at),
            pdf_url,
            notes,
            internal_notes,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating presupuesto: {str(e)}")

    out = dict(row)

    # EVENT::QUOTE_CREATED
    await _insert_historial(
        conn,
        contacto_id=out["contacto_id"],
        oportunidad_id=out["oportunidad_id"],
        subject="EVENT::QUOTE_CREATED",
        notes_obj={
            "event": "EVENT::QUOTE_CREATED",
            "presupuesto_id": str(out["id"]),
            "quote_number": out.get("quote_number"),
            "status": out.get("status"),
            "quote_value": str(out.get("quote_value")),
        },
    )

    # Si lo creas ya como Sent/Accepted/Rejected/Expired, registra evento específico
    evt = _event_for_status_transition(None, out.get("status"))
    if evt and evt != "EVENT::QUOTE_CREATED":
        await _insert_historial(
            conn,
            contacto_id=out["contacto_id"],
            oportunidad_id=out["oportunidad_id"],
            subject=evt,
            notes_obj={
                "event": evt,
                "presupuesto_id": str(out["id"]),
                "before": None,
                "after": out.get("status"),
            },
        )

    return out


@router.patch("/{presupuesto_id}")
async def patch_presupuesto(
    presupuesto_id: UUID,
    payload: Dict[str, Any] = Body(...),
    conn: Connection = Depends(get_db),
) -> Dict[str, Any]:
    """
    PATCH con allowlist + historial:
    - EVENT::QUOTE_UPDATED siempre que haya diff
    - y EVENT::QUOTE_SENT / ACCEPTED / REJECTED / EXPIRED si cambia status
    """
    before = await conn.fetchrow("SELECT * FROM presupuestos WHERE id = $1", presupuesto_id)
    if not before:
        raise HTTPException(status_code=404, detail="Presupuesto not found")

    editable = {
        "title",
        "version",
        "quote_value",
        "currency",
        "line_items",
        "status",
        "sent_at",
        "valid_until",
        "accepted_at",
        "rejected_at",
        "pdf_url",
        "notes",
        "internal_notes",
    }

    updates = {k: v for k, v in payload.items() if k in editable}
    if not updates:
        return dict(before)

    # Convert date/timestamp strings to proper Python types for asyncpg
    from datetime import date, datetime
    
    def parse_date(val):
        if val is None:
            return None
        if isinstance(val, date):
            return val
        if isinstance(val, str):
            s = val.strip()
            if not s:
                return None
            return datetime.strptime(s, "%Y-%m-%d").date()
        return None
    
    def parse_timestamp(val):
        if val is None:
            return None
        if isinstance(val, datetime):
            return val
        if isinstance(val, str):
            s = val.strip()
            if not s:
                return None
            return datetime.fromisoformat(s.replace('Z', '+00:00'))
        return None

    # Parse date/timestamp fields
    if "valid_until" in updates:
        updates["valid_until"] = parse_date(updates["valid_until"])
    for k in ("sent_at", "accepted_at", "rejected_at"):
        if k in updates:
            updates[k] = parse_timestamp(updates[k])

    set_parts: List[str] = []
    args: List[Any] = []
    idx = 1

    for k, v in updates.items():
        set_parts.append(f"{k} = ${idx}")
        args.append(v)
        idx += 1

    set_parts.append("updated_at = NOW()")

    sql = f"UPDATE presupuestos SET {', '.join(set_parts)} WHERE id = ${idx} RETURNING *"
    args.append(presupuesto_id)

    after = await conn.fetchrow(sql, *args)
    out = dict(after)

    # Diff
    diff: Dict[str, Any] = {}
    for k in updates.keys():
        b = before.get(k)
        a = after.get(k)
        if b != a:
            diff[k] = {"before": b, "after": a}

    if diff:
        # Evento general
        await _insert_historial(
            conn,
            contacto_id=out["contacto_id"],
            oportunidad_id=out["oportunidad_id"],
            subject="EVENT::QUOTE_UPDATED",
            notes_obj={
                "event": "EVENT::QUOTE_UPDATED",
                "presupuesto_id": str(out["id"]),
                "diff": diff,
            },
        )

        # Evento específico por cambio status
        before_status = before.get("status")
        after_status = out.get("status")
        evt = _event_for_status_transition(before_status, after_status)
        if evt:
            await _insert_historial(
                conn,
                contacto_id=out["contacto_id"],
                oportunidad_id=out["oportunidad_id"],
                subject=evt,
                notes_obj={
                    "event": evt,
                    "presupuesto_id": str(out["id"]),
                    "before": before_status,
                    "after": after_status,
                },
            )

    return out


@router.delete("/{presupuesto_id}")
async def soft_delete_presupuesto(
    presupuesto_id: UUID,
    conn: Connection = Depends(get_db),
) -> Dict[str, Any]:
    """
    Soft delete opcional.
    Solo funciona si existe columna is_deleted (boolean) o deleted_at (timestamptz).
    Si no existe, devuelve 409.
    """
    colset = await _get_presupuestos_columns(conn)

    if "is_deleted" not in colset and "deleted_at" not in colset:
        raise HTTPException(
            status_code=409,
            detail="Soft delete no habilitado: añade columna is_deleted (bool) o deleted_at (timestamptz)",
        )

    before = await conn.fetchrow("SELECT * FROM presupuestos WHERE id = $1", presupuesto_id)
    if not before:
        raise HTTPException(status_code=404, detail="Presupuesto not found")

    if "is_deleted" in colset:
        after = await conn.fetchrow(
            "UPDATE presupuestos SET is_deleted = true, updated_at = NOW() WHERE id = $1 RETURNING *",
            presupuesto_id,
        )
    else:
        after = await conn.fetchrow(
            "UPDATE presupuestos SET deleted_at = NOW(), updated_at = NOW() WHERE id = $1 RETURNING *",
            presupuesto_id,
        )

    out = dict(after)

    await _insert_historial(
        conn,
        contacto_id=out["contacto_id"],
        oportunidad_id=out["oportunidad_id"],
        subject="EVENT::QUOTE_DELETED",
        notes_obj={
            "event": "EVENT::QUOTE_DELETED",
            "presupuesto_id": str(out["id"]),
        },
    )

    return out