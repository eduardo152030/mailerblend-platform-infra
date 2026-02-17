from __future__ import annotations

from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, Query, HTTPException, Body
from asyncpg import Connection

from app.db import get_db

router = APIRouter(prefix="/v1/linkedin-sourcing", tags=["linkedin-sourcing"])


def _clamp_limit(limit: int) -> int:
    if limit < 1:
        return 1
    if limit > 200:
        return 200
    return limit


# ==================== CONVERSATIONS ====================

@router.post("/conversations")
async def create_message(
    payload: Dict[str, Any] = Body(...),
    conn: Connection = Depends(get_db),
) -> Dict[str, Any]:
    """
    Crear un mensaje en una conversación.
    
    Payload:
    {
        "linkedin_lead_id": "uuid",
        "message_text": "Contenido del mensaje",
        "direction": "SENT|RECEIVED",
        "sent_by": "usuario o SYSTEM",
        "sentiment": "POSITIVE|NEUTRAL|NEGATIVE (opcional)",
        "intent": "INTERESTED|NOT_INTERESTED|QUESTION (opcional)"
    }
    """
    linkedin_lead_id = payload.get("linkedin_lead_id")
    message_text = payload.get("message_text")
    direction = payload.get("direction")
    
    if not all([linkedin_lead_id, message_text, direction]):
        raise HTTPException(
            status_code=400,
            detail="linkedin_lead_id, message_text, and direction are required"
        )
    
    if direction not in ("SENT", "RECEIVED"):
        raise HTTPException(
            status_code=400,
            detail="direction must be SENT or RECEIVED"
        )
    
    # Verificar que el lead existe
    lead = await conn.fetchrow(
        "SELECT id, status FROM linkedin_leads WHERE id = $1",
        UUID(linkedin_lead_id)
    )
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Crear mensaje
    new_id = await conn.fetchval(
        """
        INSERT INTO linkedin_conversations (
            linkedin_lead_id,
            message_text,
            direction,
            sent_by,
            sentiment,
            intent,
            sent_at
        ) VALUES (
            $1, $2, $3, $4, $5, $6, NOW()
        ) RETURNING id
        """,
        UUID(linkedin_lead_id),
        message_text,
        direction,
        payload.get("sent_by", "api"),
        payload.get("sentiment"),
        payload.get("intent")
    )
    
    # Actualizar lead stats
    if direction == "SENT":
        await conn.execute(
            """
            UPDATE linkedin_leads
            SET
                last_attempt_at = NOW(),
                total_attempts = total_attempts + 1,
                updated_at = NOW()
            WHERE id = $1
            """,
            UUID(linkedin_lead_id)
        )
    elif direction == "RECEIVED":
        # Marcar último mensaje SENT como respondido
        # PostgreSQL no permite ORDER BY + LIMIT en UPDATE directo → usar subquery
        await conn.execute(
            """
            UPDATE linkedin_conversations
            SET replied_at = NOW()
            WHERE id = (
                SELECT id FROM linkedin_conversations
                WHERE linkedin_lead_id = $1
                  AND direction = 'SENT'
                  AND replied_at IS NULL
                ORDER BY sent_at DESC
                LIMIT 1
            )
            """,
            UUID(linkedin_lead_id)
        )
    
    row = await conn.fetchrow(
        "SELECT * FROM linkedin_conversations WHERE id = $1",
        new_id
    )
    return dict(row)


@router.get("/leads/{lead_id}/conversations")
async def get_lead_conversations(
    lead_id: UUID,
    limit: int = Query(200, ge=1, le=500),
    conn: Connection = Depends(get_db),
) -> Dict[str, Any]:
    """
    Obtener historial de conversación de un lead.
    Orden cronológico (más antiguos primero).
    """
    # Verificar que el lead existe
    exists = await conn.fetchval(
        "SELECT id FROM linkedin_leads WHERE id = $1",
        lead_id
    )
    if not exists:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    limit = min(limit, 500)
    
    rows = await conn.fetch(
        """
        SELECT *
        FROM linkedin_conversations
        WHERE linkedin_lead_id = $1
        ORDER BY sent_at ASC
        LIMIT $2
        """,
        lead_id,
        limit
    )
    
    return {"items": [dict(r) for r in rows]}


# ==================== OUTCOMES ====================

@router.post("/outcomes")
async def create_outcome(
    payload: Dict[str, Any] = Body(...),
    conn: Connection = Depends(get_db),
) -> Dict[str, Any]:
    """
    Registrar outcome final de un lead.
    
    Payload:
    {
        "linkedin_lead_id": "uuid",
        "outcome": "BOOKED|INTERESTED_LATER|NOT_FIT|GHOSTED|CONVERTED",
        "outcome_notes": "Notas sobre el resultado",
        "calendar_event_id": "ID de Cal.com (si BOOKED)",
        "calendar_event_url": "URL del evento",
        "scheduled_at": "2026-02-20T11:00:00Z (si BOOKED)"
    }
    
    Side effects:
    - Actualiza status del lead según el outcome
    """
    linkedin_lead_id = payload.get("linkedin_lead_id")
    outcome = payload.get("outcome")
    
    if not all([linkedin_lead_id, outcome]):
        raise HTTPException(
            status_code=400,
            detail="linkedin_lead_id and outcome are required"
        )
    
    valid_outcomes = ("BOOKED", "INTERESTED_LATER", "NOT_FIT", "GHOSTED", "CONVERTED")
    if outcome not in valid_outcomes:
        raise HTTPException(
            status_code=400,
            detail=f"outcome must be one of: {', '.join(valid_outcomes)}"
        )
    
    # Verificar que el lead existe
    lead = await conn.fetchrow(
        "SELECT id, contacto_id FROM linkedin_leads WHERE id = $1",
        UUID(linkedin_lead_id)
    )
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Convertir scheduled_at de string ISO a datetime (asyncpg lo requiere)
    scheduled_at_raw = payload.get("scheduled_at")
    scheduled_at = None
    if scheduled_at_raw:
        if isinstance(scheduled_at_raw, str):
            try:
                scheduled_at = datetime.fromisoformat(
                    scheduled_at_raw.replace("Z", "+00:00")
                )
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid scheduled_at format: '{scheduled_at_raw}'. Use ISO 8601 e.g. '2026-02-25T10:00:00Z'"
                )
        else:
            scheduled_at = scheduled_at_raw

    # Crear outcome
    new_id = await conn.fetchval(
        """
        INSERT INTO linkedin_outcomes (
            linkedin_lead_id,
            outcome,
            outcome_notes,
            calendar_event_id,
            calendar_event_url,
            scheduled_at,
            recorded_by,
            outcome_at
        ) VALUES (
            $1, $2, $3, $4, $5, $6, $7, NOW()
        ) RETURNING id
        """,
        UUID(linkedin_lead_id),
        outcome,
        payload.get("outcome_notes"),
        payload.get("calendar_event_id"),
        payload.get("calendar_event_url"),
        scheduled_at,
        payload.get("recorded_by", "api")
    )
    
    # Mapear outcome a status del lead
    status_mapping = {
        "BOOKED": "CONVERTED",        # BOOKED no existe, usar CONVERTED
        "CONVERTED": "CONVERTED",
        "NOT_FIT": "ARCHIVED",        # NOT_FIT no existe, usar ARCHIVED
        "GHOSTED": "ARCHIVED",        # GHOSTED no existe, usar ARCHIVED
        "INTERESTED_LATER": "ENGAGE_LATER"
    }
    new_status = status_mapping.get(outcome)
    
    if new_status:
        await conn.execute(
            "UPDATE linkedin_leads SET status = $1, updated_at = NOW() WHERE id = $2",
            new_status,
            UUID(linkedin_lead_id)
        )
    
    row = await conn.fetchrow(
        "SELECT * FROM linkedin_outcomes WHERE id = $1",
        new_id
    )
    return dict(row)


@router.get("/outcomes")
async def list_outcomes(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    outcome: Optional[str] = Query(None),
    lead_id: Optional[str] = Query(None),
    days: int = Query(30, ge=1, le=365),
    conn: Connection = Depends(get_db),
) -> Dict[str, Any]:
    """
    Listar outcomes con filtros.
    """
    limit = _clamp_limit(limit)
    
    where: List[str] = [f"outcome_at >= NOW() - INTERVAL '{days} days'"]
    args: List[Any] = []
    i = 1
    
    if outcome:
        where.append(f"outcome = ${i}")
        args.append(outcome)
        i += 1
    
    if lead_id:
        where.append(f"linkedin_lead_id = ${i}")
        args.append(UUID(lead_id))
        i += 1
    
    where_sql = "WHERE " + " AND ".join(where)
    
    rows = await conn.fetch(
        f"""
        SELECT
            o.id,
            o.linkedin_lead_id,
            o.oportunidad_id,
            o.outcome,
            o.outcome_notes,
            o.calendar_event_id,
            o.calendar_event_url,
            o.scheduled_at,
            o.outcome_at,
            o.recorded_by,
            l.full_name      AS lead_full_name,
            l.title          AS lead_title,
            l.company        AS lead_company,
            l.location       AS lead_location,
            l.pack_candidate AS lead_pack_candidate,
            l.lead_score     AS lead_score,
            l.linkedin_url   AS lead_linkedin_url,
            l.status         AS lead_status
        FROM linkedin_outcomes o
        LEFT JOIN linkedin_leads l ON l.id = o.linkedin_lead_id
        {where_sql}
        ORDER BY o.outcome_at DESC
        LIMIT ${i} OFFSET ${i+1}
        """,
        *args,
        limit,
        offset
    )
    
    total = await conn.fetchval(
        f"SELECT count(*)::int FROM linkedin_outcomes o {where_sql}",
        *args
    )
    
    items = [dict(r) for r in rows]
    return {
        "items": items,
        "limit": limit,
        "offset": offset,
        "count": len(items),
        "total": int(total or 0)
    }


# ==================== DASHBOARD ====================

@router.get("/dashboard")
async def get_dashboard(
    days: int = Query(30, ge=1, le=365),
    conn: Connection = Depends(get_db),
) -> Dict[str, Any]:
    """
    Dashboard principal con KPIs del sistema LinkedIn Sourcing.
    """
    cutoff = f"NOW() - INTERVAL '{days} days'"
    last_7_days = "NOW() - INTERVAL '7 days'"
    
    # Total leads
    total_leads = await conn.fetchval(
        "SELECT count(*)::int FROM linkedin_leads"
    )
    
    # By status
    status_rows = await conn.fetch(
        """
        SELECT status, count(*)::int as count
        FROM linkedin_leads
        GROUP BY status
        """
    )
    by_status = {row["status"]: row["count"] for row in status_rows}
    
    # By pack
    pack_rows = await conn.fetch(
        """
        SELECT pack_candidate, count(*)::int as count
        FROM linkedin_leads
        GROUP BY pack_candidate
        """
    )
    by_pack = {row["pack_candidate"]: row["count"] for row in pack_rows}
    
    # Invites sent
    invites_sent = await conn.fetchval(
        f"""
        SELECT count(*)::int FROM linkedin_leads
        WHERE invite_sent_at IS NOT NULL AND invite_sent_at >= {cutoff}
        """
    )
    
    # Acceptances
    acceptances = await conn.fetchval(
        f"""
        SELECT count(*)::int FROM linkedin_leads
        WHERE accepted_at IS NOT NULL AND accepted_at >= {cutoff}
        """
    )
    
    # Acceptance rate
    acceptance_rate = (acceptances / invites_sent * 100) if invites_sent > 0 else 0.0
    
    # Avg time to accept (en horas)
    avg_time_hours = await conn.fetchval(
        f"""
        SELECT AVG(EXTRACT(EPOCH FROM (accepted_at - invite_sent_at)) / 3600)
        FROM linkedin_leads
        WHERE accepted_at IS NOT NULL
          AND invite_sent_at IS NOT NULL
          AND accepted_at >= {cutoff}
        """
    )
    
    # ── Conversaciones activas: leads con mensajes en últimos 7 días ──
    # FIX: no filtramos por status=IN_CONVERSATION (no existe en schema)
    # Usamos leads que tienen al menos 1 mensaje en linkedin_conversations
    active_conversations_rows = await conn.fetch(
        """
        SELECT DISTINCT
            l.id            AS lead_id,
            l.full_name,
            l.title,
            l.company,
            l.pack_candidate,
            l.lead_score,
            l.status,
            MAX(c.sent_at)  AS last_message_at
        FROM linkedin_leads l
        INNER JOIN linkedin_conversations c ON c.linkedin_lead_id = l.id
        GROUP BY l.id, l.full_name, l.title, l.company, l.pack_candidate, l.lead_score, l.status
        ORDER BY last_message_at DESC
        """
    )
    active_conversations = len(active_conversations_rows)
    active_conversations_list = [dict(r) for r in active_conversations_rows]

    # ── Pending approvals: drafts sin aprobar ni rechazar ──
    pending_approvals_rows = await conn.fetch(
        """
        SELECT
            a.id            AS approval_id,
            a.linkedin_lead_id,
            a.draft_message,
            a.ai_rationale,
            a.created_at,
            l.full_name     AS lead_full_name,
            l.title         AS lead_title,
            l.company       AS lead_company,
            l.pack_candidate AS lead_pack_candidate,
            l.lead_score    AS lead_score
        FROM linkedin_approvals a
        LEFT JOIN linkedin_leads l ON l.id = a.linkedin_lead_id
        WHERE a.approved IS NULL
        ORDER BY a.created_at ASC
        """
    )
    pending_approvals = len(pending_approvals_rows)
    pending_approvals_list = [dict(r) for r in pending_approvals_rows]

    # ── Booked calls ──
    booked_calls = await conn.fetchval(
        f"""
        SELECT count(*)::int FROM linkedin_outcomes
        WHERE outcome = 'BOOKED' AND outcome_at >= {cutoff}
        """
    )

    # ── Converted opportunities ──
    converted_opportunities = await conn.fetchval(
        f"""
        SELECT count(*)::int FROM linkedin_outcomes
        WHERE outcome = 'CONVERTED' AND outcome_at >= {cutoff}
        """
    )

    # ── Last 7 days ──
    new_leads_7d = await conn.fetchval(
        f"SELECT count(*)::int FROM linkedin_leads WHERE created_at >= {last_7_days}"
    )
    accepted_7d = await conn.fetchval(
        f"SELECT count(*)::int FROM linkedin_leads WHERE accepted_at >= {last_7_days}"
    )
    booked_7d = await conn.fetchval(
        f"""
        SELECT count(*)::int FROM linkedin_outcomes
        WHERE outcome = 'BOOKED' AND outcome_at >= {last_7_days}
        """
    )

    # ── A/B Testing ──
    segment_rows = await conn.fetch(
        f"""
        SELECT
            segment,
            count(*) FILTER (WHERE invite_sent_at IS NOT NULL AND invite_sent_at >= {cutoff}) as invites,
            count(*) FILTER (WHERE accepted_at IS NOT NULL AND accepted_at >= {cutoff}) as accepts
        FROM linkedin_leads
        WHERE segment IS NOT NULL
        GROUP BY segment
        """
    )
    segments_performance = {}
    for row in segment_rows:
        segment = row["segment"]
        invites = row["invites"]
        accepts = row["accepts"]
        rate = (accepts / invites * 100) if invites > 0 else 0.0
        segments_performance[segment] = {
            "invites": invites,
            "accepts": accepts,
            "acceptance_rate": round(rate, 2)
        }

    return {
        "total_leads": int(total_leads or 0),
        "by_status": by_status,
        "by_pack": by_pack,
        "invites_sent": int(invites_sent or 0),
        "acceptances": int(acceptances or 0),
        "acceptance_rate": round(acceptance_rate, 2),
        "avg_time_to_accept_hours": round(float(avg_time_hours), 2) if avg_time_hours else None,
        # FIX: ahora cuenta leads con mensajes reales, no por status
        "active_conversations": active_conversations,
        "active_conversations_list": active_conversations_list,
        # NUEVO: pending approvals
        "pending_approvals": pending_approvals,
        "pending_approvals_list": pending_approvals_list,
        "booked_calls": int(booked_calls or 0),
        "converted_opportunities": int(converted_opportunities or 0),
        "new_leads_7d": int(new_leads_7d or 0),
        "accepted_7d": int(accepted_7d or 0),
        "booked_7d": int(booked_7d or 0),
        "pending_approvals_7d": pending_approvals,
        "segments_performance": segments_performance if segments_performance else None
    }