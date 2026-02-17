from __future__ import annotations

import json
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, Query, HTTPException, Body
from asyncpg import Connection

from app.db import get_db

router = APIRouter(prefix="/v1/linkedin-sourcing/leads", tags=["linkedin-sourcing-leads"])


def _clamp_limit(limit: int) -> int:
    if limit < 1:
        return 1
    if limit > 200:
        return 200
    return limit


# ==================== HELPERS ====================

def _calculate_lead_score(lead_data: Dict[str, Any], pack_candidate: str) -> Dict[str, Any]:
    """
    Calcula el lead score según el pack.
    TODO: Implementar lógica específica por pack según documentación
    """
    score = 0
    breakdown = {}
    
    if pack_candidate == "GUARDIAN":
        # Pack 1: Fit ICP + Places signals + Web signals
        score = 50  # Placeholder
        breakdown = {"fit_icp": 20, "places_signals": 20, "web_signals": 10}
    elif pack_candidate == "MOTOR":
        score = 60  # Placeholder
        breakdown = {"fit_icp": 25, "web_signals": 20, "places_signals": 15}
    elif pack_candidate == "FORTALEZA":
        score = 70  # Placeholder
        breakdown = {"fit_structural": 30, "places_signals": 20, "tech_signals": 20}
    else:
        score = 0
        breakdown = {"reason": "No pack assigned"}
    
    return {"score": score, "breakdown": breakdown}


def _auto_classify_pack(lead_data: Dict[str, Any]) -> str:
    """
    Auto-clasifica el pack basado en señales.
    TODO: Implementar lógica real de clasificación
    """
    # Placeholder - clasificación básica
    reviews = lead_data.get("places_user_ratings_total", 0)
    
    if reviews < 50:
        return "GUARDIAN"
    elif 50 <= reviews <= 200:
        return "MOTOR"
    elif reviews > 200:
        return "FORTALEZA"
    
    return "NONE"


# ==================== ENDPOINTS ====================

@router.post("/import")
async def import_leads(
    payload: Dict[str, Any] = Body(...),
    conn: Connection = Depends(get_db),
) -> Dict[str, Any]:
    """
    Importar leads en batch.
    
    Payload esperado:
    {
        "leads": [
            {
                "linkedin_url": "https://linkedin.com/in/user",
                "full_name": "Juan Pérez",
                "title": "CTO",
                "company": "Acme Corp",
                "location": "Madrid, Spain",
                "pack_candidate": "MOTOR",  # Opcional
                "segment": "Pack2_Services_MAD"  # Opcional
            }
        ],
        "auto_classify": true  # Si true, clasifica automáticamente si no viene pack_candidate
    }
    """
    leads = payload.get("leads", [])
    auto_classify = payload.get("auto_classify", True)
    
    if not leads:
        raise HTTPException(status_code=400, detail="No leads provided")
    
    if len(leads) > 100:
        raise HTTPException(status_code=400, detail="Maximum 100 leads per import")
    
    results = {
        "total_imported": len(leads),
        "successful": 0,
        "failed": 0,
        "duplicates": 0,
        "errors": [],
        "imported_ids": []
    }
    
    for idx, lead_item in enumerate(leads):
        try:
            linkedin_url = lead_item.get("linkedin_url")
            full_name = lead_item.get("full_name")
            
            if not linkedin_url or not full_name:
                results["failed"] += 1
                results["errors"].append({
                    "index": idx,
                    "error": "linkedin_url and full_name are required"
                })
                continue
            
            # Check duplicado
            exists = await conn.fetchval(
                "SELECT id FROM linkedin_leads WHERE linkedin_url = $1",
                linkedin_url
            )
            
            if exists:
                results["duplicates"] += 1
                results["errors"].append({
                    "index": idx,
                    "linkedin_url": linkedin_url,
                    "error": "Duplicate - lead already exists",
                    "existing_id": str(exists)
                })
                continue
            
            # Auto-clasificar pack si es necesario
            pack_candidate = lead_item.get("pack_candidate")
            if auto_classify and not pack_candidate:
                pack_candidate = _auto_classify_pack(lead_item)
            
            # Calcular score
            score_result = _calculate_lead_score(lead_item, pack_candidate or "NONE")
            
            # Insertar lead
            new_id = await conn.fetchval(
                """
                INSERT INTO linkedin_leads (
                    linkedin_url,
                    full_name,
                    title,
                    company,
                    location,
                    pack_candidate,
                    segment,
                    status,
                    lead_score,
                    score_breakdown,
                    created_at,
                    updated_at
                ) VALUES (
                    $1, $2, $3, $4, $5, $6, $7, 'NEW', $8, $9::jsonb, NOW(), NOW()
                ) RETURNING id
                """,
                linkedin_url,
                full_name,
                lead_item.get("title"),
                lead_item.get("company"),
                lead_item.get("location"),
                pack_candidate,
                lead_item.get("segment"),
                score_result["score"],
                json.dumps(score_result["breakdown"])
            )
            
            # Registrar attempt
            await conn.execute(
                """
                INSERT INTO linkedin_attempts (
                    linkedin_lead_id,
                    attempt_type,
                    result,
                    metadata,
                    attempted_at
                ) VALUES (
                    $1, 'INVITE', 'COMPLETED', $2::jsonb, NOW()
                )
                """,
                new_id,
                json.dumps({
                    "imported_by": "api",
                    "auto_classified": auto_classify,
                    "initial_score": score_result["score"]
                })
            )
            
            results["successful"] += 1
            results["imported_ids"].append(str(new_id))
            
        except Exception as e:
            results["failed"] += 1
            results["errors"].append({
                "index": idx,
                "linkedin_url": lead_item.get("linkedin_url"),
                "error": str(e)
            })
    
    return results


@router.get("")
async def list_leads(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    q: Optional[str] = Query(None, min_length=1, max_length=200),
    status: Optional[str] = Query(None),
    pack_candidate: Optional[str] = Query(None),
    segment: Optional[str] = Query(None),
    min_score: Optional[int] = Query(None, ge=0, le=100),
    max_score: Optional[int] = Query(None, ge=0, le=100),
    conn: Connection = Depends(get_db),
) -> Dict[str, Any]:
    """
    Listar leads con filtros y paginación.
    
    Filtros:
    - q: Búsqueda por nombre o empresa
    - status: Filtrar por status
    - pack_candidate: Filtrar por pack
    - segment: Filtrar por segmento
    - min_score / max_score: Rango de score
    """
    limit = _clamp_limit(limit)
    
    where: List[str] = []
    args: List[Any] = []
    i = 1
    
    if status:
        where.append(f"status = ${i}")
        args.append(status)
        i += 1
    
    if pack_candidate:
        where.append(f"pack_candidate = ${i}")
        args.append(pack_candidate)
        i += 1
    
    if segment:
        where.append(f"segment = ${i}")
        args.append(segment)
        i += 1
    
    if min_score is not None:
        where.append(f"lead_score >= ${i}")
        args.append(min_score)
        i += 1
    
    if max_score is not None:
        where.append(f"lead_score <= ${i}")
        args.append(max_score)
        i += 1
    
    if q:
        q_like = f"%{q}%"
        where.append(f"(COALESCE(full_name,'') ILIKE ${i} OR COALESCE(company,'') ILIKE ${i})")
        args.append(q_like)
        i += 1
    
    where_sql = ("WHERE " + " AND ".join(where)) if where else ""
    
    rows = await conn.fetch(
        f"""
        SELECT
            id,
            contacto_id,
            linkedin_url,
            full_name,
            title,
            company,
            location,
            pack_candidate,
            segment,
            status,
            lead_score,
            score_breakdown,
            invite_sent_at,
            accepted_at,
            wait_window_days,
            next_action_at,
            places_place_id,
            places_rating,
            places_user_ratings_total,
            research_depth,
            total_attempts,
            last_attempt_at,
            created_at,
            updated_at
        FROM linkedin_leads
        {where_sql}
        ORDER BY created_at DESC NULLS LAST, id DESC
        LIMIT ${i} OFFSET ${i+1}
        """,
        *args,
        limit,
        offset,
    )
    
    total = await conn.fetchval(
        f"SELECT count(*)::int FROM linkedin_leads {where_sql}",
        *args,
    )
    
    items = [dict(r) for r in rows]
    return {
        "items": items,
        "limit": limit,
        "offset": offset,
        "count": len(items),
        "total": int(total or 0)
    }


@router.get("/{lead_id}")
async def get_lead(
    lead_id: UUID,
    conn: Connection = Depends(get_db),
) -> Dict[str, Any]:
    """Obtener detalle completo de un lead"""
    row = await conn.fetchrow(
        "SELECT * FROM linkedin_leads WHERE id = $1",
        lead_id
    )
    if not row:
        raise HTTPException(status_code=404, detail="Lead not found")
    return dict(row)


@router.get("/{lead_id}/snapshot")
async def lead_snapshot(
    lead_id: UUID,
    conn: Connection = Depends(get_db),
) -> Dict[str, Any]:
    """
    Snapshot completo del lead incluyendo:
    - Datos del lead
    - Contacto vinculado (si existe)
    - Historial de attempts
    - Conversaciones
    - Approvals
    """
    lead = await conn.fetchrow(
        "SELECT * FROM linkedin_leads WHERE id = $1",
        lead_id
    )
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Contacto vinculado
    contacto = None
    if lead.get("contacto_id"):
        contacto = await conn.fetchrow(
            """
            SELECT id, nombre, email, telefono, company_name, cargo, estado
            FROM contactos
            WHERE id = $1
            """,
            lead["contacto_id"]
        )
    
    # Attempts
    attempts = await conn.fetch(
        """
        SELECT *
        FROM linkedin_attempts
        WHERE linkedin_lead_id = $1
        ORDER BY attempted_at DESC
        LIMIT 100
        """,
        lead_id
    )
    
    # Conversaciones
    conversations = await conn.fetch(
        """
        SELECT *
        FROM linkedin_conversations
        WHERE linkedin_lead_id = $1
        ORDER BY sent_at ASC
        LIMIT 200
        """,
        lead_id
    )
    
    # Approvals
    approvals = await conn.fetch(
        """
        SELECT *
        FROM linkedin_approvals
        WHERE linkedin_lead_id = $1
        ORDER BY created_at DESC
        LIMIT 50
        """,
        lead_id
    )
    
    return {
        "lead": dict(lead),
        "contacto": dict(contacto) if contacto else None,
        "attempts": [dict(r) for r in attempts],
        "conversations": [dict(r) for r in conversations],
        "approvals": [dict(r) for r in approvals]
    }


@router.patch("/{lead_id}")
async def patch_lead(
    lead_id: UUID,
    payload: Dict[str, Any] = Body(...),
    conn: Connection = Depends(get_db),
) -> Dict[str, Any]:
    """
    Actualizar un lead.
    
    Campos editables:
    - full_name, title, company, location
    - pack_candidate, segment
    - status, lead_score, score_breakdown
    - wait_window_days
    - research_depth, research_data
    """
    before = await conn.fetchrow(
        "SELECT * FROM linkedin_leads WHERE id = $1",
        lead_id
    )
    if not before:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    editable = {
        "full_name",
        "title",
        "company",
        "location",
        "pack_candidate",
        "segment",
        "status",
        "lead_score",
        "score_breakdown",
        "wait_window_days",
        "research_depth",
        "research_data",
        "next_action_at"
    }
    
    updates = {k: v for k, v in payload.items() if k in editable}
    if not updates:
        return dict(before)
    
    # Si cambió el pack, recalcular score
    if "pack_candidate" in updates and updates["pack_candidate"] != before.get("pack_candidate"):
        score_result = _calculate_lead_score(
            dict(before),
            updates["pack_candidate"]
        )
        updates["lead_score"] = score_result["score"]
        updates["score_breakdown"] = score_result["breakdown"]
    
    # Convertir JSONB fields a JSON strings
    jsonb_fields = {"score_breakdown", "research_data"}
    for field in jsonb_fields:
        if field in updates and updates[field] is not None:
            if isinstance(updates[field], (dict, list)):
                updates[field] = json.dumps(updates[field])
    
    set_parts: List[str] = []
    args: List[Any] = []
    idx = 1
    for k, v in updates.items():
        if k in jsonb_fields:
            set_parts.append(f"{k} = ${idx}::jsonb")
        else:
            set_parts.append(f"{k} = ${idx}")
        args.append(v)
        idx += 1
    
    set_parts.append("updated_at = NOW()")
    args.append(lead_id)
    
    sql = f"UPDATE linkedin_leads SET {', '.join(set_parts)} WHERE id = ${idx} RETURNING *"
    
    try:
        after = await conn.fetchrow(sql, *args)
    except Exception as e:
        msg = str(e)
        if "CheckViolationError" in msg or "violates check constraint" in msg:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid value for update (DB check constraint). Error: {msg}"
            )
        raise
    
    # Registrar attempt de UPDATE
    diff = {}
    for k in updates.keys():
        if before.get(k) != after.get(k):
            diff[k] = {"before": before.get(k), "after": after.get(k)}
    
    if diff:
        await conn.execute(
            """
            INSERT INTO linkedin_attempts (
                linkedin_lead_id,
                attempt_type,
                result,
                metadata,
                attempted_at
            ) VALUES (
                $1, 'SCORE_UPDATE', 'COMPLETED', $2::jsonb, NOW()
            )
            """,
            lead_id,
            json.dumps({"fields_updated": list(diff.keys()), "diff": diff})
        )
    
    return dict(after)


@router.get("/{lead_id}/attempts")
async def get_lead_attempts(
    lead_id: UUID,
    limit: int = Query(100, ge=1, le=500),
    conn: Connection = Depends(get_db),
) -> Dict[str, Any]:
    """Obtener historial de attempts de un lead"""
    # Verificar que el lead existe
    exists = await conn.fetchval(
        "SELECT id FROM linkedin_leads WHERE id = $1",
        lead_id
    )
    if not exists:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    limit = _clamp_limit(limit)
    
    rows = await conn.fetch(
        """
        SELECT *
        FROM linkedin_attempts
        WHERE linkedin_lead_id = $1
        ORDER BY attempted_at DESC
        LIMIT $2
        """,
        lead_id,
        limit
    )
    
    return {"items": [dict(r) for r in rows]}


@router.delete("/{lead_id}")
async def delete_lead(
    lead_id: UUID,
    conn: Connection = Depends(get_db),
) -> Dict[str, Any]:
    """
    Eliminar un lead.
    ADVERTENCIA: Esto eliminará en cascada attempts, approvals, conversations, outcomes.
    Considera usar status=ARCHIVED en su lugar.
    """
    deleted = await conn.fetchval(
        "DELETE FROM linkedin_leads WHERE id = $1 RETURNING id",
        lead_id
    )
    if not deleted:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    return {"deleted": True, "id": str(deleted)}