from __future__ import annotations

from typing import Optional, Dict, Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, Query, HTTPException, Body
from asyncpg import Connection

from app.db import get_db

router = APIRouter(prefix="/v1/linkedin-sourcing/approvals", tags=["linkedin-sourcing-approvals"])


def _clamp_limit(limit: int) -> int:
    if limit < 1:
        return 1
    if limit > 200:
        return 200
    return limit


@router.post("")
async def create_approval(
    payload: Dict[str, Any] = Body(...),
    conn: Connection = Depends(get_db),
) -> Dict[str, Any]:
    """
    Crear una approval para mensaje generado por IA.
    
    Payload:
    {
        "linkedin_lead_id": "uuid",
        "draft_message": "Mensaje generado por IA",
        "ai_rationale": "Explicación de por qué este mensaje"
    }
    """
    linkedin_lead_id = payload.get("linkedin_lead_id")
    draft_message = payload.get("draft_message")
    
    if not linkedin_lead_id or not draft_message:
        raise HTTPException(
            status_code=400,
            detail="linkedin_lead_id and draft_message are required"
        )
    
    # Verificar que el lead existe y está en estado apropiado
    lead = await conn.fetchrow(
        "SELECT id, status FROM linkedin_leads WHERE id = $1",
        UUID(linkedin_lead_id)
    )
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    if lead["status"] != "ACCEPTED":
        raise HTTPException(
            status_code=400,
            detail=f"Lead must be ACCEPTED. Current: {lead['status']}"
        )
    
    # Crear approval
    new_id = await conn.fetchval(
        """
        INSERT INTO linkedin_approvals (
            linkedin_lead_id,
            draft_message,
            ai_rationale,
            created_at
        ) VALUES (
            $1, $2, $3, NOW()
        ) RETURNING id
        """,
        UUID(linkedin_lead_id),
        draft_message,
        payload.get("ai_rationale")
    )
    
    row = await conn.fetchrow(
        "SELECT * FROM linkedin_approvals WHERE id = $1",
        new_id
    )
    
    return dict(row)


@router.get("")
async def list_approvals(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    pending_only: bool = Query(True),
    lead_id: Optional[str] = Query(None),
    conn: Connection = Depends(get_db),
) -> Dict[str, Any]:
    """
    Listar approvals.
    
    Filtros:
    - pending_only: Solo mostrar pendientes (approved IS NULL)
    - lead_id: Filtrar por lead específico
    """
    limit = _clamp_limit(limit)
    
    where: List[str] = []
    args: List[Any] = []
    i = 1
    
    if pending_only:
        where.append("approved IS NULL")
    
    if lead_id:
        where.append(f"linkedin_lead_id = ${i}")
        args.append(UUID(lead_id))
        i += 1
    
    where_sql = ("WHERE " + " AND ".join(where)) if where else ""
    
    rows = await conn.fetch(
        f"""
        SELECT *
        FROM linkedin_approvals
        {where_sql}
        ORDER BY created_at DESC
        LIMIT ${i} OFFSET ${i+1}
        """,
        *args,
        limit,
        offset
    )
    
    total = await conn.fetchval(
        f"SELECT count(*)::int FROM linkedin_approvals {where_sql}",
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


@router.get("/{approval_id}")
async def get_approval(
    approval_id: UUID,
    conn: Connection = Depends(get_db),
) -> Dict[str, Any]:
    """Obtener detalle de una approval"""
    row = await conn.fetchrow(
        "SELECT * FROM linkedin_approvals WHERE id = $1",
        approval_id
    )
    if not row:
        raise HTTPException(status_code=404, detail="Approval not found")
    return dict(row)


@router.post("/{approval_id}/approve")
async def approve_draft(
    approval_id: UUID,
    payload: Dict[str, Any] = Body(...),
    conn: Connection = Depends(get_db),
) -> Dict[str, Any]:
    """
    Aprobar un draft.
    
    Payload:
    {
        "final_message": "Mensaje aprobado/editado (opcional)",
        "angle": "Bueno|Regular|Incorrecto",
        "pain_assessment": "Real|Superficial|Inventado",
        "human_note": "Nota del humano"
    }
    
    Side effects:
    - Marca approved=TRUE
    - Cambia status del lead a IN_CONVERSATION
    - Crea mensaje en linkedin_conversations
    """
    approval = await conn.fetchrow(
        "SELECT * FROM linkedin_approvals WHERE id = $1",
        approval_id
    )
    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found")
    
    if approval["approved"] is not None:
        raise HTTPException(
            status_code=400,
            detail="Approval already processed"
        )
    
    final_message = payload.get("final_message") or approval["draft_message"]
    
    # Actualizar approval
    await conn.execute(
        """
        UPDATE linkedin_approvals
        SET
            approved = TRUE,
            final_message = $1,
            angle = $2,
            pain_assessment = $3,
            human_note = $4,
            approved_at = NOW(),
            approved_by = $5
        WHERE id = $6
        """,
        final_message,
        payload.get("angle"),
        payload.get("pain_assessment"),
        payload.get("human_note"),
        payload.get("approved_by", "api"),
        approval_id
    )
    
    # Actualizar status del lead (mantener en ACCEPTED, no cambiar a IN_CONVERSATION)
    await conn.execute(
        """
        UPDATE linkedin_leads
        SET updated_at = NOW()
        WHERE id = $1
        """,
        approval["linkedin_lead_id"]
    )
    
    # Crear mensaje en conversations
    await conn.execute(
        """
        INSERT INTO linkedin_conversations (
            linkedin_lead_id,
            message_text,
            direction,
            sent_by,
            sent_at
        ) VALUES (
            $1, $2, 'SENT', $3, NOW()
        )
        """,
        approval["linkedin_lead_id"],
        final_message,
        payload.get("approved_by", "api")
    )
    
    # Retornar approval actualizada
    updated = await conn.fetchrow(
        "SELECT * FROM linkedin_approvals WHERE id = $1",
        approval_id
    )
    return dict(updated)


@router.post("/{approval_id}/reject")
async def reject_draft(
    approval_id: UUID,
    payload: Dict[str, Any] = Body(...),
    conn: Connection = Depends(get_db),
) -> Dict[str, Any]:
    """
    Rechazar un draft.
    
    Payload:
    {
        "angle": "Bueno|Regular|Incorrecto",
        "pain_assessment": "Real|Superficial|Inventado",
        "human_note": "Nota del humano (por qué se rechazó)"
    }
    
    NO cambia el status del lead.
    """
    approval = await conn.fetchrow(
        "SELECT * FROM linkedin_approvals WHERE id = $1",
        approval_id
    )
    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found")
    
    if approval["approved"] is not None:
        raise HTTPException(
            status_code=400,
            detail="Approval already processed"
        )
    
    # Actualizar approval
    await conn.execute(
        """
        UPDATE linkedin_approvals
        SET
            approved = FALSE,
            angle = $1,
            pain_assessment = $2,
            human_note = $3,
            approved_at = NOW(),
            approved_by = $4
        WHERE id = $5
        """,
        payload.get("angle"),
        payload.get("pain_assessment"),
        payload.get("human_note"),
        payload.get("approved_by", "api"),
        approval_id
    )
    
    updated = await conn.fetchrow(
        "SELECT * FROM linkedin_approvals WHERE id = $1",
        approval_id
    )
    return dict(updated)


@router.get("/stats/feedback")
async def get_approval_feedback_stats(
    days: int = Query(30, ge=1, le=365),
    conn: Connection = Depends(get_db),
) -> Dict[str, Any]:
    """
    Estadísticas de feedback de approvals.
    Útil para mejorar la generación de drafts de la IA.
    """
    from datetime import timedelta
    
    cutoff = f"NOW() - INTERVAL '{days} days'"
    
    # Total approvals
    total = await conn.fetchval(
        f"SELECT count(*)::int FROM linkedin_approvals WHERE created_at >= {cutoff}"
    )
    
    # Approved vs rejected
    approved = await conn.fetchval(
        f"SELECT count(*)::int FROM linkedin_approvals WHERE approved = TRUE AND created_at >= {cutoff}"
    )
    rejected = await conn.fetchval(
        f"SELECT count(*)::int FROM linkedin_approvals WHERE approved = FALSE AND created_at >= {cutoff}"
    )
    
    # By angle
    angle_stats = await conn.fetch(
        f"""
        SELECT angle, count(*)::int as count
        FROM linkedin_approvals
        WHERE created_at >= {cutoff} AND angle IS NOT NULL
        GROUP BY angle
        """
    )
    
    # By pain_assessment
    pain_stats = await conn.fetch(
        f"""
        SELECT pain_assessment, count(*)::int as count
        FROM linkedin_approvals
        WHERE created_at >= {cutoff} AND pain_assessment IS NOT NULL
        GROUP BY pain_assessment
        """
    )
    
    by_angle = {row["angle"]: row["count"] for row in angle_stats}
    by_pain = {row["pain_assessment"]: row["count"] for row in pain_stats}
    
    approval_rate = (approved / total * 100) if total > 0 else 0.0
    
    return {
        "total_approvals": int(total or 0),
        "approved": int(approved or 0),
        "rejected": int(rejected or 0),
        "approval_rate": round(approval_rate, 2),
        "by_angle": by_angle,
        "by_pain": by_pain
    }