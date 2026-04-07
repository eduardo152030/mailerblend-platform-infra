"""
Router: LinkedIn Knowledge Base
Gestión de servicios, ICP, pain points, objeciones, FAQs

+ Dynamic LinkedIn Query Generator
- Usa pool curado: linkedin_queries_kb
- Evita repetición: linkedin_query_history (exclude_recent_days)
- Si faltan queries, genera dinámicas desde linkedin_query_generator_config
"""

from fastapi import APIRouter, Depends, Query, Body, HTTPException
from typing import Optional, Dict, Any, List, Tuple
from uuid import UUID
from asyncpg import Connection
import json
import random
import hashlib

from app.db import get_db


router = APIRouter(
    prefix="/v1/linkedin-sourcing/knowledge-base",
    tags=["LinkedIn Knowledge Base"]
)


VALID_PACKS = ("GUARDIAN", "MOTOR", "FORTALEZA")


def _clamp_limit(limit: int, max_val: int = 500) -> int:
    return min(max(limit, 1), max_val)


def _assert_pack(pack: str) -> str:
    pack = (pack or "").strip().upper()
    if pack not in VALID_PACKS:
        raise HTTPException(400, "pack must be GUARDIAN, MOTOR, or FORTALEZA")
    return pack


def _md5_lower(s: str) -> str:
    return hashlib.md5(s.strip().lower().encode("utf-8")).hexdigest()


# =====================================================
# Knowledge Base (existing CRUD)
# =====================================================

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
    pack = _assert_pack(pack)

    where = ["is_active = TRUE", "(target_pack = $1 OR target_pack = 'ALL')"]
    args = [pack]

    if categories:
        cat_list = [c.strip() for c in categories.split(",") if c.strip()]
        placeholders = ",".join(f"${i+2}" for i in range(len(cat_list)))
        where.append(f"category IN ({placeholders})")
        args.extend(cat_list)

    where_sql = "WHERE " + " AND ".join(where)

    rows = await conn.fetch(
        f"SELECT category, title, content, priority FROM linkedin_knowledge_base "
        f"{where_sql} ORDER BY priority DESC",
        *args
    )

    context: Dict[str, List[Dict[str, Any]]] = {}
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


# =====================================================
# Dynamic Queries API (NEW)
# =====================================================

async def _fetch_pool_queries(
    conn: Connection,
    pack: str,
    count: int,
    exclude_recent_days: int
) -> List[Dict[str, Any]]:
    """
    Trae queries desde linkedin_queries_kb que NO se hayan usado en los últimos X días.
    Considera pack específico + ALL.
    """
    rows = await conn.fetch(
        """
        SELECT
          q.query,
          q.query_hash,
          q.meta,
          q.priority,
          q.pack AS source_pack
        FROM linkedin_queries_kb q
        LEFT JOIN linkedin_query_history h
          ON q.query_hash = h.query_hash
        WHERE
          (q.pack = $1 OR q.pack = 'ALL')
          AND q.is_active = TRUE
          AND (
            h.used_at IS NULL
            OR h.used_at < NOW() - ($2 * interval '1 day')
          )
        ORDER BY q.priority DESC, random()
        LIMIT $3
        """,
        pack, int(exclude_recent_days), int(count)
    )

    out: List[Dict[str, Any]] = []
    for r in rows:
        out.append({
            "query": r["query"],
            "query_hash": r["query_hash"],
            "meta": r["meta"] if isinstance(r["meta"], dict) else (dict(r["meta"]) if r["meta"] else {}),
            "source": "kb",
            "source_pack": r["source_pack"]
        })
    return out


async def _fetch_generator_config(conn: Connection, pack: str) -> Dict[str, Any]:
    row = await conn.fetchrow(
        """
        SELECT roles, industries, cities, templates, weights, is_active
        FROM linkedin_query_generator_config
        WHERE pack = $1
        """,
        pack
    )
    if not row or not row["is_active"]:
        raise HTTPException(400, f"Generator config not found or inactive for pack={pack}")

    def _ensure_list(v: Any, name: str) -> List[str]:
        if v is None:
            return []
        if isinstance(v, str):
            try:
                v = json.loads(v)
            except Exception:
                pass
        if isinstance(v, list):
            return [str(x) for x in v if str(x).strip()]
        # asyncpg JSONB puede llegar como dict/list ya. Si no, fallback:
        try:
            return [str(x) for x in list(v)]
        except Exception:
            raise HTTPException(500, f"Invalid generator config field: {name}")

    roles = _ensure_list(row["roles"], "roles")
    industries = _ensure_list(row["industries"], "industries")
    cities = _ensure_list(row["cities"], "cities")
    templates = _ensure_list(row["templates"], "templates")

    if not roles or not industries or not cities or not templates:
        raise HTTPException(400, f"Generator config incomplete for pack={pack}")

    weights = row["weights"]
    if isinstance(weights, str):
        try:
            weights = json.loads(weights)
        except Exception:
            weights = {}
    if weights is None:
        weights = {}

    return {
        "roles": roles,
        "industries": industries,
        "cities": cities,
        "templates": templates,
        "weights": weights
    }


async def _is_hash_recent(
    conn: Connection,
    query_hash: str,
    exclude_recent_days: int
) -> bool:
    # True si se usó recientemente
    row = await conn.fetchrow(
        """
        SELECT 1
        FROM linkedin_query_history
        WHERE query_hash = $1
          AND used_at > NOW() - ($2 * interval '1 day')
        LIMIT 1
        """,
        query_hash, int(exclude_recent_days)
    )
    return row is not None


def _weighted_choice(items: List[str], weights_map: Dict[str, Any], key: str) -> str:
    """
    weights_map puede tener:
      {"roles": {"CEO": 3, "Founder": 2}, "cities": {...}, "industries": {...}}
    Si no hay pesos, random normal.
    """
    bucket = weights_map.get(key, {}) if isinstance(weights_map, dict) else {}
    if not isinstance(bucket, dict) or not bucket:
        return random.choice(items)

    w = []
    for it in items:
        try:
            w.append(float(bucket.get(it, 1.0)))
        except Exception:
            w.append(1.0)

    # Si todo es 0, fallback
    if sum(w) <= 0:
        return random.choice(items)

    return random.choices(items, weights=w, k=1)[0]


async def _generate_dynamic_queries(
    conn: Connection,
    pack: str,
    count: int,
    exclude_recent_days: int,
    max_attempts_multiplier: int = 25
) -> List[Dict[str, Any]]:
    """
    Genera queries combinando role/industry/city/template y evita repetición reciente.
    """
    cfg = await _fetch_generator_config(conn, pack)

    roles = cfg["roles"]
    industries = cfg["industries"]
    cities = cfg["cities"]
    templates = cfg["templates"]
    weights = cfg["weights"]

    picked: List[Dict[str, Any]] = []
    seen_hashes = set()

    max_attempts = max(count * max_attempts_multiplier, 50)
    attempts = 0

    while len(picked) < count and attempts < max_attempts:
        attempts += 1

        role = _weighted_choice(roles, weights, "roles")
        industry = _weighted_choice(industries, weights, "industries")
        city = _weighted_choice(cities, weights, "cities")
        template = random.choice(templates)

        q = template.replace("{role}", role).replace("{industry}", industry).replace("{city}", city).strip()
        if not q:
            continue

        h = _md5_lower(f"{pack}::{q}")
        if h in seen_hashes:
            continue

        if await _is_hash_recent(conn, h, exclude_recent_days):
            continue

        meta = {
            "role": role,
            "industry": industry,
            "city": city,
            "template": template,
            "pack": pack,
            "source": "generated"
        }

        picked.append({
            "query": q,
            "query_hash": h,
            "meta": meta,
            "source": "generated",
            "source_pack": pack
        })
        seen_hashes.add(h)

    return picked


async def _reserve_queries(
    conn: Connection,
    pack: str,
    items: List[Dict[str, Any]]
) -> None:
    """
    Marca como usadas (upsert) en linkedin_query_history.
    """
    if not items:
        return

    # Usamos executemany para rendimiento
    values: List[Tuple[str, str, str]] = []
    for it in items:
        q = it["query"]
        h = it["query_hash"]
        values.append((pack, q, h))

    await conn.executemany(
        """
        INSERT INTO linkedin_query_history (pack, query, query_hash, used_at)
        VALUES ($1, $2, $3, NOW())
        ON CONFLICT (query_hash) DO UPDATE
        SET used_at = NOW()
        """,
        values
    )


async def _upsert_generated_into_kb(
    conn: Connection,
    items: List[Dict[str, Any]]
) -> None:
    """
    Inserta queries generadas en linkedin_queries_kb (opcional), para ir creciendo el pool.
    No rompe si ya existe por uq hash.
    OJO: el trigger de tu SQL recalcula hash; igual mandamos query_hash para ON CONFLICT.
    """
    if not items:
        return

    values = []
    for it in items:
        q = it["query"]
        h = it["query_hash"]
        meta = it.get("meta") or {}
        pack = it.get("source_pack") or it.get("pack") or meta.get("pack")
        # Fallback seguro:
        pack = (pack or "").upper().strip()
        if pack not in VALID_PACKS:
            # no insertamos si pack inválido
            continue
        values.append((pack, q, h, json.dumps(meta)))

    if not values:
        return

    await conn.executemany(
        """
        INSERT INTO linkedin_queries_kb (pack, query, query_hash, meta, priority, is_active)
        VALUES ($1, $2, $3, $4::jsonb, 50, TRUE)
        ON CONFLICT (query_hash) DO NOTHING
        """,
        values
    )


@router.get("/queries/{pack}")
async def get_queries_for_pack(
    pack: str,
    count: int = Query(4, ge=1, le=100),
    exclude_recent_days: int = Query(30, ge=0, le=365),
    reserve: bool = Query(True),
    persist_generated: bool = Query(True),
    conn: Connection = Depends(get_db)
) -> Dict[str, Any]:
    """
    Devuelve `count` queries para el pack evitando repetición reciente.

    Orden de obtención:
      1) Pool curado (linkedin_queries_kb) no usado recientemente
      2) Si faltan, generar dinámicamente (linkedin_query_generator_config)

    Params:
      - reserve: si TRUE, marca las queries como usadas (history)
      - persist_generated: si TRUE, inserta las generadas en linkedin_queries_kb (para crecer pool)
    """
    pack = _assert_pack(pack)

    # 1) Pool curado
    items = await _fetch_pool_queries(conn, pack, count, exclude_recent_days)

    # 2) Generación dinámica si faltan
    missing = count - len(items)
    generated: List[Dict[str, Any]] = []
    if missing > 0:
        generated = await _generate_dynamic_queries(conn, pack, missing, exclude_recent_days)
        items.extend(generated)

        if persist_generated and generated:
            await _upsert_generated_into_kb(conn, generated)

    if reserve and items:
        await _reserve_queries(conn, pack, items)

    return {
        "pack": pack,
        "count_requested": int(count),
        "count_returned": len(items),
        "exclude_recent_days": int(exclude_recent_days),
        "reserved": bool(reserve),
        "persist_generated": bool(persist_generated),
        "items": items
    }


@router.post("/queries/{pack}/reserve")
async def reserve_query(
    pack: str,
    payload: Dict[str, Any] = Body(...),
    conn: Connection = Depends(get_db)
) -> Dict[str, Any]:
    """
    Reserva 1 query manualmente.
    Body:
      - query_hash (preferido)
      - query (si no hay hash)
    """
    pack = _assert_pack(pack)
    qh = (payload.get("query_hash") or "").strip()
    q = (payload.get("query") or "").strip()

    if not qh and not q:
        raise HTTPException(400, "Body must include query_hash or query")

    if not qh:
        qh = _md5_lower(f"{pack}::{q}")

    if not q:
        # si solo pasan hash, intentamos recuperar query desde pool
        row = await conn.fetchrow(
            "SELECT query FROM linkedin_queries_kb WHERE query_hash = $1 LIMIT 1",
            qh
        )
        if row:
            q = row["query"]
        else:
            # igual reservamos hash con query vacía? mejor exigir query
            raise HTTPException(400, "query not found for query_hash; please provide query text")

    await conn.execute(
        """
        INSERT INTO linkedin_query_history (pack, query, query_hash, used_at)
        VALUES ($1, $2, $3, NOW())
        ON CONFLICT (query_hash) DO UPDATE
        SET used_at = NOW()
        """,
        pack, q, qh
    )

    return {"pack": pack, "query": q, "query_hash": qh, "reserved": True}


@router.post("/queries/reset")
async def reset_query_history(
    payload: Dict[str, Any] = Body(...),
    conn: Connection = Depends(get_db)
) -> Dict[str, Any]:
    """
    Limpia historial antiguo para permitir reutilización.
    Body:
      - pack: opcional (GUARDIAN|MOTOR|FORTALEZA). Si no viene, aplica a todos.
      - older_than_days: default 30
    """
    older_than_days = int(payload.get("older_than_days", 30))
    if older_than_days < 0 or older_than_days > 3650:
        raise HTTPException(400, "older_than_days must be between 0 and 3650")

    pack = payload.get("pack")
    if pack:
        pack = _assert_pack(pack)
        deleted = await conn.fetchval(
            """
            DELETE FROM linkedin_query_history
            WHERE pack = $1
              AND used_at < NOW() - ($2 * interval '1 day')
            RETURNING 1
            """,
            pack, older_than_days
        )
        # fetchval con DELETE RETURNING 1 devuelve 1 fila; queremos count real:
        deleted_count = await conn.fetchval(
            """
            SELECT COUNT(*)::int
            FROM linkedin_query_history
            WHERE pack = $1
              AND used_at < NOW() - ($2 * interval '1 day')
            """,
            pack, older_than_days
        )
        # Nota: arriba contamos lo que quedaría por borrar; mejor borramos con rowcount:
        # Como asyncpg no expone rowcount fácil aquí, hacemos un approach correcto:
        # re-ejecutamos delete con fetch:
        rows = await conn.fetch(
            """
            DELETE FROM linkedin_query_history
            WHERE pack = $1
              AND used_at < NOW() - ($2 * interval '1 day')
            RETURNING id
            """,
            pack, older_than_days
        )
        deleted_count = len(rows)
        return {"pack": pack, "older_than_days": older_than_days, "deleted": deleted_count}

    rows = await conn.fetch(
        """
        DELETE FROM linkedin_query_history
        WHERE used_at < NOW() - ($1 || ' days')::interval
        RETURNING id
        """,
        older_than_days
    )
    return {"pack": None, "older_than_days": older_than_days, "deleted": len(rows)}