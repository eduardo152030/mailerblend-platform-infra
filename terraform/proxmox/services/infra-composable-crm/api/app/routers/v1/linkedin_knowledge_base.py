"""
Router: LinkedIn Knowledge Base
Gestión de servicios, ICP, pain points, objeciones, FAQs
"""
from fastapi import APIRouter, Depends, Query, Body, HTTPException
from typing import Optional, Dict, Any, List
from uuid import UUID
from asyncpg import Connection
import json

from app.db import get_db


router = APIRouter(
    prefix="/v1/linkedin-sourcing/knowledge-base",
    tags=["LinkedIn Knowledge Base"]
)


def _clamp_limit(limit: int, max_val: int = 500) -> int:
    return min(max(limit, 1), max_val)


@router.post("")
async def create_knowledge_entry(
    payload: Dict[str, Any] = Body(...),
    conn: Connection = Depends(get_db)
) -> Dict[str, Any]:
    """Crear entrada en knowledge base."""
    required = ["category", "title", "content"]
    if not all(k in payload for k in required):
        raise HTTPException(400, f"Required: {', '.join(required)}")
    
    entry_id = await conn.fetchval(
        """
        INSERT INTO linkedin_knowledge_base (
            category, subcategory, title, content, target_pack, priority
        ) VALUES ($1, $2, $3, $4::jsonb, $5, $6)
        RETURNING id
        """,
        payload["category"],
        payload.get("subcategory"),
        payload["title"],
        json.dumps(payload["content"]),
        payload.get("target_pack"),
        payload.get("priority", 50)
    )
    
    return {"id": str(entry_id), "category": payload["category"], "created": True}


@router.get("")
async def list_knowledge_entries(
    category: Optional[str] = Query(None),
    target_pack: Optional[str] = Query(None),
    is_active: bool = Query(True),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    conn: Connection = Depends(get_db)
) -> Dict[str, Any]:
    """Listar knowledge entries con filtros."""
    limit = _clamp_limit(limit)
    where = ["is_active = $1"]
    args = [is_active]
    i = 2
    
    if category:
        where.append(f"category = ${i}")
        args.append(category)
        i += 1
    
    if target_pack:
        where.append(f"(target_pack = ${i} OR target_pack = 'ALL')")
        args.append(target_pack)
        i += 1
    
    where_sql = "WHERE " + " AND ".join(where)
    
    rows = await conn.fetch(
        f"SELECT * FROM linkedin_knowledge_base {where_sql} "
        f"ORDER BY priority DESC, created_at DESC LIMIT ${i} OFFSET ${i+1}",
        *args, limit, offset
    )
    
    total = await conn.fetchval(
        f"SELECT COUNT(*)::int FROM linkedin_knowledge_base {where_sql}",
        *args
    )
    
    return {
        "items": [dict(r) for r in rows],
        "limit": limit,
        "offset": offset,
        "count": len(rows),
        "total": int(total or 0)
    }


@router.get("/context/{pack}")
async def get_context_for_pack(
    pack: str,
    categories: Optional[str] = Query(None),
    conn: Connection = Depends(get_db)
) -> Dict[str, Any]:
    """Contexto completo para IA - por pack."""
    if pack not in ("GUARDIAN", "MOTOR", "FORTALEZA"):
        raise HTTPException(400, "pack must be GUARDIAN, MOTOR, or FORTALEZA")
    
    where = ["is_active = TRUE", "(target_pack = $1 OR target_pack = 'ALL')"]
    args = [pack]
    
    if categories:
        cat_list = categories.split(',')
        placeholders = ','.join(f"${i+2}" for i in range(len(cat_list)))
        where.append(f"category IN ({placeholders})")
        args.extend(cat_list)
    
    where_sql = "WHERE " + " AND ".join(where)
    
    rows = await conn.fetch(
        f"SELECT category, title, content, priority FROM linkedin_knowledge_base "
        f"{where_sql} ORDER BY priority DESC",
        *args
    )
    
    context = {}
    for row in rows:
        cat = row["category"]
        if cat not in context:
            context[cat] = []
        context[cat].append({
            "title": row["title"],
            "content": row["content"],
            "priority": row["priority"]
        })
    
    return {"pack": pack, "context": context, "total_entries": len(rows)}


@router.get("/{entry_id}")
async def get_knowledge_entry(
    entry_id: UUID,
    conn: Connection = Depends(get_db)
) -> Dict[str, Any]:
    """Obtener entrada específica."""
    row = await conn.fetchrow(
        "SELECT * FROM linkedin_knowledge_base WHERE id = $1", entry_id
    )
    if not row:
        raise HTTPException(404, "Knowledge entry not found")
    return dict(row)


@router.patch("/{entry_id}")
async def update_knowledge_entry(
    entry_id: UUID,
    payload: Dict[str, Any] = Body(...),
    conn: Connection = Depends(get_db)
) -> Dict[str, Any]:
    """Actualizar entrada."""
    exists = await conn.fetchval(
        "SELECT id FROM linkedin_knowledge_base WHERE id = $1", entry_id
    )
    if not exists:
        raise HTTPException(404, "Not found")
    
    updates = []
    args = []
    i = 1
    
    for field in ["title", "subcategory", "category", "target_pack", "priority", "is_active"]:
        if field in payload:
            updates.append(f"{field} = ${i}")
            args.append(payload[field])
            i += 1
    
    if "content" in payload:
        updates.append(f"content = ${i}::jsonb")
        args.append(json.dumps(payload["content"]))
        i += 1
    
    if not updates:
        raise HTTPException(400, "No fields to update")
    
    updates.append("updated_at = NOW()")
    args.append(entry_id)
    
    await conn.execute(
        f"UPDATE linkedin_knowledge_base SET {', '.join(updates)} WHERE id = ${i}",
        *args
    )
    
    return {"id": str(entry_id), "updated": True}


@router.delete("/{entry_id}")
async def delete_knowledge_entry(
    entry_id: UUID,
    hard_delete: bool = Query(False),
    conn: Connection = Depends(get_db)
) -> Dict[str, Any]:
    """Soft delete por defecto."""
    exists = await conn.fetchval(
        "SELECT id FROM linkedin_knowledge_base WHERE id = $1", entry_id
    )
    if not exists:
        raise HTTPException(404, "Not found")
    
    if hard_delete:
        await conn.execute(
            "DELETE FROM linkedin_knowledge_base WHERE id = $1", entry_id
        )
    else:
        await conn.execute(
            "UPDATE linkedin_knowledge_base SET is_active = FALSE WHERE id = $1",
            entry_id
        )
    
    return {"id": str(entry_id), "deleted": True}