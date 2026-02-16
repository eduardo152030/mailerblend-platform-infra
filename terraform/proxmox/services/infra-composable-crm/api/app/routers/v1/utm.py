from __future__ import annotations

from typing import Optional, Dict, Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, Query, HTTPException
from asyncpg import Connection

from app.db import get_db

router = APIRouter(prefix="/v1/utm", tags=["utm"])


def _clamp_limit(limit: int) -> int:
    if limit < 1:
        return 1
    if limit > 500:
        return 500
    return limit


@router.get("")
async def list_utm(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),

    # búsqueda libre (auditar landing/referrer + utm + ids)
    q: Optional[str] = Query(None, min_length=1, max_length=300),

    # filtros Budibase
    contacto_id: Optional[UUID] = Query(None),
    utm_campaign: Optional[str] = Query(None, max_length=255),
    utm_source: Optional[str] = Query(None, max_length=255),
    utm_medium: Optional[str] = Query(None, max_length=100),
    ads_platform: Optional[str] = Query(None, max_length=50),
    device: Optional[str] = Query(None, max_length=50),
    created_from: Optional[str] = Query(None, description="YYYY-MM-DD"),
    created_to: Optional[str] = Query(None, description="YYYY-MM-DD"),

    conn: Connection = Depends(get_db),
) -> Dict[str, Any]:
    """
    Grid de UTM / tracking.
    Nota: no existe query_string_raw en el schema actual.
    Para auditar el "querystring", usamos landing_url/referrer_url + utm + click ids.
    """
    limit = _clamp_limit(limit)

    where: List[str] = []
    args: List[Any] = []
    i = 1

    def add(clause: str, value: Any):
        nonlocal i
        where.append(clause.replace("$X", f"${i}"))
        args.append(value)
        i += 1

    if contacto_id:
        add("contacto_id = $X", contacto_id)

    if utm_campaign:
        add("utm_campaign = $X", utm_campaign)

    if utm_source:
        add("utm_source = $X", utm_source)

    if utm_medium:
        add("utm_medium = $X", utm_medium)

    if ads_platform:
        add("ads_platform = $X", ads_platform)

    if device:
        add("device = $X", device)

    if created_from:
        add("created_at >= $X::date", created_from)

    if created_to:
        add("created_at < ($X::date + interval '1 day')", created_to)

    if q:
        like = f"%{q}%"
        where.append(
            "("
            f"COALESCE(utm_source,'') ILIKE ${i} OR "
            f"COALESCE(utm_medium,'') ILIKE ${i} OR "
            f"COALESCE(utm_campaign,'') ILIKE ${i} OR "
            f"COALESCE(utm_content,'') ILIKE ${i} OR "
            f"COALESCE(utm_term,'') ILIKE ${i} OR "
            f"COALESCE(adgroup,'') ILIKE ${i} OR "
            f"COALESCE(device,'') ILIKE ${i} OR "
            f"COALESCE(keyword,'') ILIKE ${i} OR "
            f"COALESCE(creative,'') ILIKE ${i} OR "
            f"COALESCE(gclid,'') ILIKE ${i} OR "
            f"COALESCE(msclkid,'') ILIKE ${i} OR "
            f"COALESCE(li_fat_id,'') ILIKE ${i} OR "
            f"COALESCE(fbclid,'') ILIKE ${i} OR "
            f"COALESCE(landing_url,'') ILIKE ${i} OR "
            f"COALESCE(referrer_url,'') ILIKE ${i}"
            ")"
        )
        args.append(like)
        i += 1

    where_sql = ("WHERE " + " AND ".join(where)) if where else ""

    rows = await conn.fetch(
        f"""
        SELECT
            id,
            contacto_id,
            utm_source,
            utm_medium,
            utm_campaign,
            utm_content,
            utm_term,
            adgroup,
            device,
            placement,
            keyword,
            creative,
            gclid,
            msclkid,
            li_fat_id,
            fbclid,
            ads_platform,
            landing_url,
            referrer_url,
            first_visit_at,
            created_at,
            contacto_nombre
        FROM parametros_utm
        {where_sql}
        ORDER BY created_at DESC, id DESC
        LIMIT ${i} OFFSET ${i+1}
        """,
        *args,
        limit,
        offset,
    )

    total = await conn.fetchval(
        f"SELECT count(*)::int FROM parametros_utm {where_sql}",
        *args,
    )

    items = [dict(r) for r in rows]
    return {"items": items, "limit": limit, "offset": offset, "count": len(items), "total": int(total or 0)}


@router.get("/stats")
async def utm_stats(
    group_by: str = Query("campaign", description="campaign|source|medium|device|platform|adgroup|keyword"),
    created_from: Optional[str] = Query(None, description="YYYY-MM-DD"),
    created_to: Optional[str] = Query(None, description="YYYY-MM-DD"),
    ads_platform: Optional[str] = Query(None),
    conn: Connection = Depends(get_db),
) -> Dict[str, Any]:
    """
    Agregados para charts en Budibase.
    """
    mapping = {
        "campaign": "utm_campaign",
        "source": "utm_source",
        "medium": "utm_medium",
        "device": "device",
        "platform": "ads_platform",
        "adgroup": "adgroup",
        "keyword": "keyword",
    }
    if group_by not in mapping:
        raise HTTPException(status_code=400, detail=f"group_by inválido. Usa: {', '.join(mapping.keys())}")

    col = mapping[group_by]

    where: List[str] = ["1=1"]
    args: List[Any] = []
    i = 1

    if created_from:
        where.append(f"created_at >= ${i}::date")
        args.append(created_from)
        i += 1
    if created_to:
        where.append(f"created_at < (${i}::date + interval '1 day')")
        args.append(created_to)
        i += 1
    if ads_platform:
        where.append(f"ads_platform = ${i}")
        args.append(ads_platform)
        i += 1

    rows = await conn.fetch(
        f"""
        SELECT
            COALESCE({col}, '(null)') AS key,
            COUNT(*)::int AS leads,
            SUM((gclid IS NOT NULL AND gclid!='')::int)::int AS with_gclid,
            SUM((msclkid IS NOT NULL AND msclkid!='')::int)::int AS with_msclkid,
            SUM((li_fat_id IS NOT NULL AND li_fat_id!='')::int)::int AS with_li_fat_id,
            SUM((fbclid IS NOT NULL AND fbclid!='')::int)::int AS with_fbclid
        FROM parametros_utm
        WHERE {" AND ".join(where)}
        GROUP BY 1
        ORDER BY leads DESC
        LIMIT 200
        """,
        *args,
    )

    return {"group_by": group_by, "items": [dict(r) for r in rows]}


@router.get("/stats2")
async def utm_stats2(
    group_by: str = Query(
        "campaign_device",
        description="campaign_device|campaign_platform|source_medium|campaign_source|campaign_adgroup|campaign_keyword",
    ),
    created_from: Optional[str] = Query(None, description="YYYY-MM-DD"),
    created_to: Optional[str] = Query(None, description="YYYY-MM-DD"),
    ads_platform: Optional[str] = Query(None),
    conn: Connection = Depends(get_db),
) -> Dict[str, Any]:
    """
    Agregados compuestos (2 dimensiones) para charts/tablas en Budibase.
    Devuelve: items[{key1,key2,leads,with_*ids}]
    """
    mapping = {
        "campaign_device": ("utm_campaign", "device"),
        "campaign_platform": ("utm_campaign", "ads_platform"),
        "source_medium": ("utm_source", "utm_medium"),
        "campaign_source": ("utm_campaign", "utm_source"),
        "campaign_adgroup": ("utm_campaign", "adgroup"),
        "campaign_keyword": ("utm_campaign", "keyword"),
    }
    if group_by not in mapping:
        raise HTTPException(status_code=400, detail=f"group_by inválido. Usa: {', '.join(mapping.keys())}")

    col1, col2 = mapping[group_by]

    where: List[str] = ["1=1"]
    args: List[Any] = []
    i = 1

    if created_from:
        where.append(f"created_at >= ${i}::date")
        args.append(created_from)
        i += 1
    if created_to:
        where.append(f"created_at < (${i}::date + interval '1 day')")
        args.append(created_to)
        i += 1
    if ads_platform:
        where.append(f"ads_platform = ${i}")
        args.append(ads_platform)
        i += 1

    rows = await conn.fetch(
        f"""
        SELECT
            COALESCE({col1}, '(null)') AS key1,
            COALESCE({col2}, '(null)') AS key2,
            COUNT(*)::int AS leads,
            SUM((gclid IS NOT NULL AND gclid!='')::int)::int AS with_gclid,
            SUM((msclkid IS NOT NULL AND msclkid!='')::int)::int AS with_msclkid,
            SUM((li_fat_id IS NOT NULL AND li_fat_id!='')::int)::int AS with_li_fat_id,
            SUM((fbclid IS NOT NULL AND fbclid!='')::int)::int AS with_fbclid
        FROM parametros_utm
        WHERE {" AND ".join(where)}
        GROUP BY 1,2
        ORDER BY leads DESC
        LIMIT 500
        """,
        *args,
    )

    return {"group_by": group_by, "items": [dict(r) for r in rows]}


@router.get("/stats-conversions")
async def utm_stats_conversions(
    group_by: str = Query("campaign", description="campaign|source|medium|device|platform"),
    created_from: Optional[str] = Query(None, description="YYYY-MM-DD"),
    created_to: Optional[str] = Query(None, description="YYYY-MM-DD"),
    conn: Connection = Depends(get_db),
) -> Dict[str, Any]:
    """
    Agregados cruzando conversiones_offline (si hay datos).
    """
    mapping = {
        "campaign": "utm_campaign",
        "source": "utm_source",
        "medium": "utm_medium",
        "device": "device",
        "platform": "ads_platform",
    }
    if group_by not in mapping:
        raise HTTPException(status_code=400, detail=f"group_by inválido. Usa: {', '.join(mapping.keys())}")

    col = mapping[group_by]

    where: List[str] = ["1=1"]
    args: List[Any] = []
    i = 1

    if created_from:
        where.append(f"u.created_at >= ${i}::date")
        args.append(created_from)
        i += 1
    if created_to:
        where.append(f"u.created_at < (${i}::date + interval '1 day')")
        args.append(created_to)
        i += 1

    rows = await conn.fetch(
        f"""
        SELECT
            COALESCE(u.{col}, '(null)') AS key,
            COUNT(DISTINCT u.id)::int AS utm_rows,
            COUNT(c.id)::int AS conversions
        FROM parametros_utm u
        LEFT JOIN conversiones_offline c
          ON c.parametros_utm_id = u.id
        WHERE {" AND ".join(where)}
        GROUP BY 1
        ORDER BY conversions DESC, utm_rows DESC
        LIMIT 200
        """,
        *args,
    )

    return {"group_by": group_by, "items": [dict(r) for r in rows]}


# ⚠️ IMPORTANTE: Este endpoint dinámico SIEMPRE debe ir al FINAL
# FastAPI evalúa las rutas en orden, y /{utm_id} haría match con cualquier path
@router.get("/{utm_id}")
async def get_utm(
    utm_id: UUID,
    conn: Connection = Depends(get_db),
) -> Dict[str, Any]:
    row = await conn.fetchrow("SELECT * FROM parametros_utm WHERE id=$1", utm_id)
    if not row:
        raise HTTPException(status_code=404, detail="UTM record not found")
    return dict(row)