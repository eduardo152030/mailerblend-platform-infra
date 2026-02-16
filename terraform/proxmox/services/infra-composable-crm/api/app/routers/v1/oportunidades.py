from __future__ import annotations

from typing import Optional, Dict, Any, List, Tuple
from uuid import UUID
from datetime import date, datetime  # 📅 Para convertir strings a fechas

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


# -------------------------
# 📅 Date conversion helper
# -------------------------
def _parse_date_field(value: Any) -> Optional[date]:
    """
    Convierte strings de fecha a objetos date.
    Acepta formatos: 'YYYY-MM-DD' o None.
    """
    if value is None or value == "":
        return None
    if isinstance(value, date):
        return value
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, str):
        try:
            # Intenta parsear formato ISO: YYYY-MM-DD
            return datetime.fromisoformat(value.strip()).date()
        except (ValueError, AttributeError):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid date format: '{value}'. Expected format: YYYY-MM-DD"
            )
    raise HTTPException(
        status_code=400,
        detail=f"Invalid date type: {type(value)}. Expected string in format YYYY-MM-DD"
    )


# -------------------------
# Offline Conversions helpers
# -------------------------
async def _pick_best_parametros_utm_row(conn: Connection, contacto_id: UUID) -> Optional[Dict[str, Any]]:
    """
    Elige el UTM más reciente para el contacto, priorizando que tenga algún click id.
    """
    row = await conn.fetchrow(
        """
        SELECT
          id,
          ads_platform,
          gclid,
          msclkid,
          li_fat_id,
          fbclid,
          utm_campaign,
          utm_source,
          utm_medium,
          device,
          created_at
        FROM parametros_utm
        WHERE contacto_id = $1
        ORDER BY
          (CASE
             WHEN COALESCE(gclid,'')<>'' OR COALESCE(msclkid,'')<>'' OR COALESCE(li_fat_id,'')<>'' OR COALESCE(fbclid,'')<>''
             THEN 0 ELSE 1
           END),
          created_at DESC
        LIMIT 1
        """,
        contacto_id,
    )
    return dict(row) if row else None


def _pick_click_id(utm: Dict[str, Any]) -> Optional[str]:
    """
    Prioridad de click_id por plataforma:
    - GOOGLE: gclid
    - BING: msclkid
    - LINKEDIN: li_fat_id
    - FACEBOOK: fbclid
    Fallback: el primero no vacío.
    """
    gclid = (utm.get("gclid") or "").strip()
    msclkid = (utm.get("msclkid") or "").strip()
    li_fat_id = (utm.get("li_fat_id") or "").strip()
    fbclid = (utm.get("fbclid") or "").strip()

    platform = (utm.get("ads_platform") or "").strip().upper()

    if platform == "GOOGLE" and gclid:
        return gclid
    if platform == "BING" and msclkid:
        return msclkid
    if platform == "LINKEDIN" and li_fat_id:
        return li_fat_id
    if platform == "FACEBOOK" and fbclid:
        return fbclid

    return gclid or msclkid or li_fat_id or fbclid or None


async def _insert_historial_note(
    conn: Connection,
    *,
    contacto_id: Optional[UUID],
    oportunidad_id: UUID,
    subject: str,
    notes_obj: Dict[str, Any],
) -> None:
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


async def _create_offline_conversion_if_possible(
    conn: Connection,
    *,
    contacto_id: UUID,
    oportunidad_id: UUID,
    event_name: str,                 # CHECK: Lead_Submitted|Lead_Qualified|Lead_Won|Purchase|Custom
    conversion_value: Optional[float] = None,
) -> Tuple[bool, str]:
    """
    Inserta en conversiones_offline si hay UTM + click_id + platform válido.
    Requisitos NOT NULL en tabla:
      platform, event_name, click_id, conversion_time
    """
    utm = await _pick_best_parametros_utm_row(conn, contacto_id)
    if not utm:
        return False, "NO_UTM"

    platform = (utm.get("ads_platform") or "").strip().upper()
    if platform not in ("GOOGLE", "BING", "LINKEDIN", "FACEBOOK"):
        return False, f"INVALID_PLATFORM:{platform or '(null)'}"

    click_id = _pick_click_id(utm)
    if not click_id:
        return False, "NO_CLICK_ID"

    # Idempotencia best-effort: evita duplicados por oportunidad+event+click_id
    exists = await conn.fetchval(
        """
        SELECT COUNT(*)::int
        FROM conversiones_offline
        WHERE oportunidad_id = $1 AND event_name = $2 AND click_id = $3
        """,
        oportunidad_id,
        event_name,
        click_id,
    )
    if exists and int(exists) > 0:
        return False, "ALREADY_EXISTS"

    await conn.execute(
        """
        INSERT INTO conversiones_offline (
            oportunidad_id,
            parametros_utm_id,
            platform,
            event_name,
            conversion_value,
            currency,
            click_id,
            conversion_time,
            sync_status,
            retry_count,
            created_at
        ) VALUES (
            $1, $2, $3, $4, $5, 'EUR', $6, NOW(), 'PENDING', 0, NOW()
        )
        """,
        oportunidad_id,
        utm["id"],
        platform,
        event_name,
        conversion_value,
        click_id,
    )

    return True, "CREATED"


@router.get("")
async def list_oportunidades(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    q: Optional[str] = Query(None, min_length=1, max_length=200),
    estado: Optional[str] = Query(None, min_length=1, max_length=50),
    lead_tag: Optional[str] = Query(None, min_length=1, max_length=50),
    prioridad: Optional[str] = Query(None, min_length=1, max_length=50),
    pack: Optional[str] = Query(None, min_length=1, max_length=50),
    urgencia: Optional[str] = Query(None, min_length=1, max_length=80),
    conn: Connection = Depends(get_db),
) -> Dict[str, Any]:
    limit = _clamp_limit(limit)

    where: List[str] = []
    args: List[Any] = []
    i = 1

    if estado:
        where.append(f"estado = ${i}")
        args.append(estado)
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
    if urgencia:
        where.append(f"urgencia = ${i}")
        args.append(urgencia)
        i += 1

    if q:
        q_like = f"%{q}%"
        where.append(f"(COALESCE(deal_name,'') ILIKE ${i} OR COALESCE(owner,'') ILIKE ${i} OR COALESCE(contacto_nombre,'') ILIKE ${i})")
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
            estado,
            lead_tag,
            prioridad,
            urgencia,
            next_action,
            next_action_date,
            probabilidad,
            currency,
            owner,
            pack,
            created_at,
            updated_at,
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
    conn: Connection = Depends(get_db),
) -> Dict[str, Any]:
    op = await conn.fetchrow("SELECT * FROM oportunidades WHERE id = $1", oportunidad_id)
    if not op:
        raise HTTPException(status_code=404, detail="Oportunidad not found")

    contacto = None
    if op.get("contacto_id"):
        contacto = await conn.fetchrow(
            """
            SELECT id, nombre, email, telefono, company_name, cargo, estado, origen, created_at, updated_at
            FROM contactos
            WHERE id = $1
            """,
            op["contacto_id"],
        )

    historial = await conn.fetch(
        """
        SELECT *
        FROM historial
        WHERE oportunidad_id = $1
        ORDER BY COALESCE(activity_date, created_at) DESC NULLS LAST, id DESC
        LIMIT 200
        """,
        oportunidad_id,
    )

    return {
        "oportunidad": dict(op),
        "contacto": dict(contacto) if contacto else None,
        "historial": [dict(r) for r in historial],
    }


@router.patch("/{oportunidad_id}")
async def patch_oportunidad(
    oportunidad_id: UUID,
    payload: Dict[str, Any] = Body(...),
    conn: Connection = Depends(get_db),
) -> Dict[str, Any]:
    before = await conn.fetchrow("SELECT * FROM oportunidades WHERE id = $1", oportunidad_id)
    if not before:
        raise HTTPException(status_code=404, detail="Oportunidad not found")

    editable = {
        "estado",
        "lead_tag",
        "prioridad",
        "urgencia",
        "next_action",
        "next_action_date",
        "probabilidad",
        "deal_value",
        "currency",
        "owner",
        "team",
        "pack",
        "deal_name",
        "expected_close_date",
        "won_at",
        "lost_at",
        "lost_reason",
        "lost_reason_notes",
        "notas_internas",
        "tags",
    }

    updates = {k: v for k, v in payload.items() if k in editable}
    if not updates:
        return dict(before)

    # 📅 Convertir campos de fecha de string a date object
    date_fields = {"next_action_date", "expected_close_date", "won_at", "lost_at"}
    for field in date_fields:
        if field in updates:
            updates[field] = _parse_date_field(updates[field])

    before_estado = (before.get("estado") or "").strip()
    before_lead_tag = (before.get("lead_tag") or "").strip()

    set_parts: List[str] = []
    args: List[Any] = []
    idx = 1
    for k, v in updates.items():
        set_parts.append(f"{k} = ${idx}")
        args.append(v)
        idx += 1

    set_parts.append("updated_at = NOW()")
    args.append(oportunidad_id)

    sql = f"UPDATE oportunidades SET {', '.join(set_parts)} WHERE id = ${idx} RETURNING *"

    try:
        after = await conn.fetchrow(sql, *args)
    except Exception as e:
        # Si hay violación de CHECK (como te pasó con estado=Qualified), devolvemos 400 claro
        msg = str(e)
        if "CheckViolationError" in msg or "violates check constraint" in msg:
            raise HTTPException(status_code=400, detail=f"Invalid value for update (DB check constraint). Error: {msg}")
        raise

    diff: Dict[str, Any] = {}
    for k in updates.keys():
        b = before.get(k)
        a = after.get(k)
        if b != a:
            diff[k] = {"before": b, "after": a}

    contacto_id = after.get("contacto_id")

    # 1) Historial principal (diff)
    if diff:
        await _insert_historial_note(
            conn,
            contacto_id=contacto_id,
            oportunidad_id=oportunidad_id,
            subject="EVENT::STAGE_CHANGED",
            notes_obj={
                "event": "EVENT::STAGE_CHANGED",
                "diff": diff,
                "oportunidad_id": str(oportunidad_id),
                "contacto_id": str(contacto_id) if contacto_id else None,
            },
        )

    # 2) Offline conversions hook
    try:
        after_estado = (after.get("estado") or "").strip()
        after_lead_tag = (after.get("lead_tag") or "").strip()

        # A) Lead qualified => se dispara por lead_tag = Qualified
        if contacto_id and before_lead_tag != after_lead_tag and after_lead_tag == "Qualified":
            created, reason = await _create_offline_conversion_if_possible(
                conn,
                contacto_id=contacto_id,
                oportunidad_id=oportunidad_id,
                event_name="Lead_Qualified",
                conversion_value=300.0,
            )
            await _insert_historial_note(
                conn,
                contacto_id=contacto_id,
                oportunidad_id=oportunidad_id,
                subject="EVENT::OFFLINE_CONVERSION_CREATED" if created else "EVENT::OFFLINE_CONVERSION_SKIPPED",
                notes_obj={
                    "event": "EVENT::OFFLINE_CONVERSION_CREATED" if created else "EVENT::OFFLINE_CONVERSION_SKIPPED",
                    "event_name": "Lead_Qualified",
                    "reason": None if created else reason,
                    "sync_status": "PENDING" if created else None,
                },
            )

        # B) Lead won => se dispara por estado = Ganado
        if contacto_id and before_estado != after_estado and after_estado == "Ganado":
            created, reason = await _create_offline_conversion_if_possible(
                conn,
                contacto_id=contacto_id,
                oportunidad_id=oportunidad_id,
                event_name="Lead_Won",
                conversion_value=900.0,
            )
            await _insert_historial_note(
                conn,
                contacto_id=contacto_id,
                oportunidad_id=oportunidad_id,
                subject="EVENT::OFFLINE_CONVERSION_CREATED" if created else "EVENT::OFFLINE_CONVERSION_SKIPPED",
                notes_obj={
                    "event": "EVENT::OFFLINE_CONVERSION_CREATED" if created else "EVENT::OFFLINE_CONVERSION_SKIPPED",
                    "event_name": "Lead_Won",
                    "reason": None if created else reason,
                    "sync_status": "PENDING" if created else None,
                },
            )
    except Exception:
        # no romper prod por analytics
        pass

    return dict(after)