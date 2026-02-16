from __future__ import annotations

import csv
import io
from typing import Optional, Dict, Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, Query, HTTPException, Body
from fastapi.responses import StreamingResponse
from asyncpg import Connection

from app.db import get_db

router = APIRouter(prefix="/v1/gastos", tags=["gastos"])


def _clamp_limit(limit: int) -> int:
    return max(1, min(200, limit))


@router.get("")
async def list_gastos(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    q: Optional[str] = Query(None, min_length=1, max_length=200),

    # filtros Budibase
    categoria: Optional[str] = Query(None, min_length=1, max_length=50),
    estado: Optional[str] = Query(None, min_length=1, max_length=20),
    proveedor_id: Optional[UUID] = Query(None),
    project_key: Optional[str] = Query(None, min_length=1, max_length=20),

    # rango fechas
    from_date: Optional[str] = Query(None, alias="from"),
    to_date: Optional[str] = Query(None, alias="to"),

    conn: Connection = Depends(get_db),
) -> Dict[str, Any]:
    limit = _clamp_limit(limit)

    where: List[str] = []
    args: List[Any] = []
    i = 1

    if categoria:
        where.append(f"categoria = ${i}")
        args.append(categoria)
        i += 1

    if estado:
        where.append(f"estado = ${i}")
        args.append(estado)
        i += 1

    if proveedor_id:
        where.append(f"proveedor_id = ${i}")
        args.append(proveedor_id)
        i += 1

    if project_key:
        where.append(f"project_key = ${i}")
        args.append(project_key)
        i += 1

    # fechas: parse en SQL (safe)
    if from_date:
        where.append(f"fecha_gasto >= ${i}::date")
        args.append(from_date)
        i += 1
    if to_date:
        where.append(f"fecha_gasto <= ${i}::date")
        args.append(to_date)
        i += 1

    if q:
        q_like = f"%{q}%"
        where.append(
            f"(concepto ILIKE ${i} OR COALESCE(proveedor_nombre,'') ILIKE ${i} OR COALESCE(numero_factura,'') ILIKE ${i})"
        )
        args.append(q_like)
        i += 1

    where_sql = ("WHERE " + " AND ".join(where)) if where else ""

    rows = await conn.fetch(
        f"""
        SELECT
          id,
          fecha_gasto,
          fecha_vencimiento,
          proveedor_id,
          proveedor_nombre,
          concepto,
          categoria,
          project_key,
          base_imponible,
          iva_porcentaje,
          iva_importe,
          total,
          currency,
          estado,
          metodo_pago,
          numero_factura,
          adjunto_url,
          notas,
          internal_notes,
          created_at,
          updated_at
        FROM gastos
        {where_sql}
        ORDER BY fecha_gasto DESC, created_at DESC
        LIMIT ${i} OFFSET ${i+1}
        """,
        *args,
        limit,
        offset,
    )

    total = await conn.fetchval(
        f"SELECT count(*)::int FROM gastos {where_sql}",
        *args,
    )

    items = [dict(r) for r in rows]
    return {"items": items, "limit": limit, "offset": offset, "count": len(items), "total": int(total or 0)}


@router.get("/stats")
async def gastos_stats(
    group_by: str = Query("categoria", pattern="^(categoria|estado|metodo_pago|proveedor)$"),
    from_date: Optional[str] = Query(None, alias="from"),
    to_date: Optional[str] = Query(None, alias="to"),
    project_key: Optional[str] = Query(None, min_length=1, max_length=20),
    conn: Connection = Depends(get_db),
) -> Dict[str, Any]:
    """
    Budibase friendly: agrupa gastos y suma base/iva/total.
    group_by: categoria | estado | metodo_pago | proveedor
    """
    from datetime import datetime
    
    def parse_date(val):
        if val is None:
            return None
        if isinstance(val, str):
            return datetime.strptime(val.strip(), "%Y-%m-%d").date()
        return val
    
    where: List[str] = []
    args: List[Any] = []
    i = 1

    if from_date:
        where.append(f"g.fecha_gasto >= ${i}")
        args.append(parse_date(from_date))
        i += 1
    if to_date:
        where.append(f"g.fecha_gasto <= ${i}")
        args.append(parse_date(to_date))
        i += 1
    if project_key:
        where.append(f"g.project_key = ${i}")
        args.append(project_key)
        i += 1

    where_sql = ("WHERE " + " AND ".join(where)) if where else ""

    if group_by == "proveedor":
        key_expr = "COALESCE(g.proveedor_nombre, '(sin proveedor)')"
    elif group_by == "metodo_pago":
        key_expr = "COALESCE(g.metodo_pago, '(null)')"
    else:
        key_expr = f"COALESCE(g.{group_by}, '(null)')"

    rows = await conn.fetch(
        f"""
        SELECT
          {key_expr} AS key,
          COUNT(*)::int AS count,
          COALESCE(SUM(g.base_imponible),0)::numeric(12,2) AS sum_base,
          COALESCE(SUM(g.iva_importe),0)::numeric(12,2) AS sum_iva,
          COALESCE(SUM(g.total),0)::numeric(12,2) AS sum_total
        FROM gastos g
        {where_sql}
        GROUP BY 1
        ORDER BY sum_total DESC, count DESC
        LIMIT 200
        """,
        *args,
    )

    return {"group_by": group_by, "items": [dict(r) for r in rows]}


@router.get("/stats-timeseries")
async def gastos_stats_timeseries(
    bucket: str = Query("month", pattern="^(month|week|day)$"),
    from_date: Optional[str] = Query(None, alias="from"),
    to_date: Optional[str] = Query(None, alias="to"),
    project_key: Optional[str] = Query(None, min_length=1, max_length=20),
    conn: Connection = Depends(get_db),
) -> Dict[str, Any]:
    """
    Serie temporal para dashboards: month|week|day
    """
    from datetime import datetime
    
    def parse_date(val):
        if val is None:
            return None
        if isinstance(val, str):
            return datetime.strptime(val.strip(), "%Y-%m-%d").date()
        return val
    
    where: List[str] = []
    args: List[Any] = []
    i = 1

    if from_date:
        where.append(f"fecha_gasto >= ${i}")
        args.append(parse_date(from_date))
        i += 1
    if to_date:
        where.append(f"fecha_gasto <= ${i}")
        args.append(parse_date(to_date))
        i += 1
    if project_key:
        where.append(f"project_key = ${i}")
        args.append(project_key)
        i += 1

    where_sql = ("WHERE " + " AND ".join(where)) if where else ""
    bucket_expr = f"date_trunc('{bucket}', fecha_gasto::timestamptz)"

    rows = await conn.fetch(
        f"""
        SELECT
          {bucket_expr} AS bucket,
          COUNT(*)::int AS count,
          COALESCE(SUM(base_imponible),0)::numeric(12,2) AS sum_base,
          COALESCE(SUM(iva_importe),0)::numeric(12,2) AS sum_iva,
          COALESCE(SUM(total),0)::numeric(12,2) AS sum_total
        FROM gastos
        {where_sql}
        GROUP BY 1
        ORDER BY bucket ASC
        """,
        *args,
    )

    # bucket sale como timestamp -> iso
    items = []
    for r in rows:
        d = dict(r)
        if d.get("bucket"):
            d["bucket"] = d["bucket"].isoformat()
        items.append(d)

    return {"bucket": bucket, "items": items}


@router.get("/tax-summary")
async def gastos_tax_summary(
    from_date: str = Query(..., alias="from"),
    to_date: str = Query(..., alias="to"),
    conn: Connection = Depends(get_db),
) -> Dict[str, Any]:
    """
    Resumen básico para gestoría:
    - total base imponible
    - IVA soportado
    - total gasto
    """
    from datetime import datetime
    
    def parse_date(val):
        if isinstance(val, str):
            return datetime.strptime(val.strip(), "%Y-%m-%d").date()
        return val
    
    row = await conn.fetchrow(
        """
        SELECT
          COALESCE(SUM(base_imponible),0)::numeric(12,2) AS base_total,
          COALESCE(SUM(iva_importe),0)::numeric(12,2) AS iva_total,
          COALESCE(SUM(total),0)::numeric(12,2) AS total
        FROM gastos
        WHERE fecha_gasto >= $1 AND fecha_gasto <= $2
        """,
        parse_date(from_date),
        parse_date(to_date),
    )
    return {"from": from_date, "to": to_date, **dict(row)}


@router.get("/export.csv")
async def export_gastos_csv(
    from_date: Optional[str] = Query(None, alias="from"),
    to_date: Optional[str] = Query(None, alias="to"),
    categoria: Optional[str] = Query(None),
    estado: Optional[str] = Query(None),
    proveedor_id: Optional[UUID] = Query(None),
    project_key: Optional[str] = Query(None, min_length=1, max_length=20),
    q: Optional[str] = Query(None, min_length=1, max_length=200),
    conn: Connection = Depends(get_db),
):
    """
    Export CSV para gestoría o Excel.
    Filtros:
      - from / to (fecha_gasto)
      - categoria, estado, proveedor_id, project_key
      - q (concepto / proveedor_nombre / numero_factura)
    """
    from datetime import datetime
    
    def parse_date(val):
        if val is None:
            return None
        if isinstance(val, str):
            return datetime.strptime(val.strip(), "%Y-%m-%d").date()
        return val
    
    where: List[str] = []
    args: List[Any] = []
    i = 1

    if from_date:
        where.append(f"g.fecha_gasto >= ${i}")
        args.append(parse_date(from_date))
        i += 1
    if to_date:
        where.append(f"g.fecha_gasto <= ${i}")
        args.append(parse_date(to_date))
        i += 1
    if categoria:
        where.append(f"g.categoria = ${i}")
        args.append(categoria)
        i += 1
    if estado:
        where.append(f"g.estado = ${i}")
        args.append(estado)
        i += 1
    if proveedor_id:
        where.append(f"g.proveedor_id = ${i}")
        args.append(proveedor_id)
        i += 1
    if project_key:
        where.append(f"g.project_key = ${i}")
        args.append(project_key)
        i += 1
    if q:
        q_like = f"%{q}%"
        where.append(f"(g.concepto ILIKE ${i} OR COALESCE(g.proveedor_nombre,'') ILIKE ${i} OR COALESCE(g.numero_factura,'') ILIKE ${i})")
        args.append(q_like)
        i += 1

    where_sql = ("WHERE " + " AND ".join(where)) if where else ""

    rows = await conn.fetch(
        f"""
        SELECT
          g.fecha_gasto,
          g.fecha_vencimiento,
          COALESCE(g.proveedor_nombre, '') AS proveedor,
          g.categoria,
          g.project_key,
          g.estado,
          COALESCE(g.metodo_pago,'') AS metodo_pago,
          g.concepto,
          COALESCE(g.numero_factura,'') AS numero_factura,
          g.base_imponible,
          g.iva_porcentaje,
          g.iva_importe,
          g.total,
          g.currency,
          COALESCE(g.adjunto_url,'') AS adjunto_url,
          COALESCE(g.notas,'') AS notas,
          g.created_at,
          g.updated_at,
          g.id
        FROM gastos g
        {where_sql}
        ORDER BY g.fecha_gasto DESC, g.created_at DESC
        """,
        *args,
    )

    output = io.StringIO()
    writer = csv.writer(output, delimiter=';')

    # Cabecera (Excel friendly)
    writer.writerow([
        "fecha_gasto",
        "fecha_vencimiento",
        "proveedor",
        "categoria",
        "project_key",
        "estado",
        "metodo_pago",
        "concepto",
        "numero_factura",
        "base_imponible",
        "iva_porcentaje",
        "iva_importe",
        "total",
        "currency",
        "adjunto_url",
        "notas",
        "created_at",
        "updated_at",
        "id",
    ])

    for r in rows:
        d = dict(r)
        writer.writerow([
            d.get("fecha_gasto"),
            d.get("fecha_vencimiento"),
            d.get("proveedor"),
            d.get("categoria"),
            d.get("project_key"),
            d.get("estado"),
            d.get("metodo_pago"),
            d.get("concepto"),
            d.get("numero_factura"),
            d.get("base_imponible"),
            d.get("iva_porcentaje"),
            d.get("iva_importe"),
            d.get("total"),
            d.get("currency"),
            d.get("adjunto_url"),
            d.get("notas"),
            d.get("created_at").isoformat() if d.get("created_at") else "",
            d.get("updated_at").isoformat() if d.get("updated_at") else "",
            d.get("id"),
        ])

    output.seek(0)

    # filename con rango si existe
    fname_parts = ["gastos"]
    if from_date:
        fname_parts.append(f"from_{from_date}")
    if to_date:
        fname_parts.append(f"to_{to_date}")
    filename = "_".join(fname_parts) + ".csv"

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/stats2")
async def gastos_stats2(
    group_by: str = Query("project_categoria", pattern="^(project_categoria|project_month)$"),
    from_date: Optional[str] = Query(None, alias="from"),
    to_date: Optional[str] = Query(None, alias="to"),
    project_key: Optional[str] = Query(None, min_length=1, max_length=20),
    conn: Connection = Depends(get_db),
) -> Dict[str, Any]:
    """
    stats2:
      - project_categoria: pivot (project_key, categoria)
      - project_month: pivot (project_key, month)
    """
    from datetime import datetime
    
    def parse_date(val):
        if val is None:
            return None
        if isinstance(val, str):
            return datetime.strptime(val.strip(), "%Y-%m-%d").date()
        return val
    
    where: List[str] = []
    args: List[Any] = []
    i = 1

    if from_date:
        where.append(f"g.fecha_gasto >= ${i}")
        args.append(parse_date(from_date))
        i += 1
    if to_date:
        where.append(f"g.fecha_gasto <= ${i}")
        args.append(parse_date(to_date))
        i += 1
    if project_key:
        where.append(f"g.project_key = ${i}")
        args.append(project_key)
        i += 1

    where_sql = ("WHERE " + " AND ".join(where)) if where else ""

    if group_by == "project_categoria":
        rows = await conn.fetch(
            f"""
            SELECT
              g.project_key AS project_key,
              COALESCE(g.categoria, '(null)') AS categoria,
              COUNT(*)::int AS count,
              COALESCE(SUM(g.base_imponible),0)::numeric(12,2) AS sum_base,
              COALESCE(SUM(g.iva_importe),0)::numeric(12,2) AS sum_iva,
              COALESCE(SUM(g.total),0)::numeric(12,2) AS sum_total
            FROM gastos g
            {where_sql}
            GROUP BY 1, 2
            ORDER BY g.project_key ASC, sum_total DESC, count DESC
            LIMIT 500
            """,
            *args,
        )
        return {"group_by": group_by, "items": [dict(r) for r in rows]}

    # group_by == "project_month"
    rows = await conn.fetch(
        f"""
        SELECT
          g.project_key AS project_key,
          date_trunc('month', g.fecha_gasto::timestamptz) AS bucket,
          COUNT(*)::int AS count,
          COALESCE(SUM(g.base_imponible),0)::numeric(12,2) AS sum_base,
          COALESCE(SUM(g.iva_importe),0)::numeric(12,2) AS sum_iva,
          COALESCE(SUM(g.total),0)::numeric(12,2) AS sum_total
        FROM gastos g
        {where_sql}
        GROUP BY 1, 2
        ORDER BY bucket ASC, project_key ASC
        LIMIT 1000
        """,
        *args,
    )

    items = []
    for r in rows:
        d = dict(r)
        if d.get("bucket"):
            d["bucket"] = d["bucket"].isoformat()
        items.append(d)

    return {"group_by": group_by, "items": items}


@router.get("/pnl-monthly")
async def gastos_pnl_monthly(
    from_date: Optional[str] = Query(None, alias="from"),
    to_date: Optional[str] = Query(None, alias="to"),
    conn: Connection = Depends(get_db),
) -> Dict[str, Any]:
    """
    P&L mensual (solo gastos):
    Devuelve por mes columnas:
      - nucleo_total / mailerblend_total / shared_total
      - nucleo_base / mailerblend_base / shared_base
      - nucleo_iva / mailerblend_iva / shared_iva
      - grand_total
    Ideal para Budibase charts apilados.
    """
    from datetime import datetime
    
    def parse_date(val):
        if val is None:
            return None
        if isinstance(val, str):
            return datetime.strptime(val.strip(), "%Y-%m-%d").date()
        return val
    
    where: List[str] = []
    args: List[Any] = []
    i = 1

    if from_date:
        where.append(f"fecha_gasto >= ${i}")
        args.append(parse_date(from_date))
        i += 1
    if to_date:
        where.append(f"fecha_gasto <= ${i}")
        args.append(parse_date(to_date))
        i += 1

    where_sql = ("WHERE " + " AND ".join(where)) if where else ""

    rows = await conn.fetch(
        f"""
        WITH m AS (
          SELECT
            date_trunc('month', fecha_gasto::timestamptz) AS month,
            project_key,
            COALESCE(SUM(base_imponible),0)::numeric(12,2) AS sum_base,
            COALESCE(SUM(iva_importe),0)::numeric(12,2) AS sum_iva,
            COALESCE(SUM(total),0)::numeric(12,2) AS sum_total
          FROM gastos
          {where_sql}
          GROUP BY 1, 2
        )
        SELECT
          m.month AS month,

          COALESCE(SUM(CASE WHEN m.project_key='Nucleo_tecnologico' THEN m.sum_base END),0)::numeric(12,2) AS nucleo_base,
          COALESCE(SUM(CASE WHEN m.project_key='Nucleo_tecnologico' THEN m.sum_iva END),0)::numeric(12,2) AS nucleo_iva,
          COALESCE(SUM(CASE WHEN m.project_key='Nucleo_tecnologico' THEN m.sum_total END),0)::numeric(12,2) AS nucleo_total,

          COALESCE(SUM(CASE WHEN m.project_key='Mailerblend' THEN m.sum_base END),0)::numeric(12,2) AS mailerblend_base,
          COALESCE(SUM(CASE WHEN m.project_key='Mailerblend' THEN m.sum_iva END),0)::numeric(12,2) AS mailerblend_iva,
          COALESCE(SUM(CASE WHEN m.project_key='Mailerblend' THEN m.sum_total END),0)::numeric(12,2) AS mailerblend_total,

          COALESCE(SUM(CASE WHEN m.project_key='SHARED' THEN m.sum_base END),0)::numeric(12,2) AS shared_base,
          COALESCE(SUM(CASE WHEN m.project_key='SHARED' THEN m.sum_iva END),0)::numeric(12,2) AS shared_iva,
          COALESCE(SUM(CASE WHEN m.project_key='SHARED' THEN m.sum_total END),0)::numeric(12,2) AS shared_total,

          COALESCE(SUM(m.sum_total),0)::numeric(12,2) AS grand_total
        FROM m
        GROUP BY 1
        ORDER BY month ASC
        """,
        *args,
    )

    items = []
    for r in rows:
        d = dict(r)
        if d.get("month"):
            d["month"] = d["month"].isoformat()
        items.append(d)

    return {"items": items}


@router.get("/pnl-summary")
async def gastos_pnl_summary(
    from_date: Optional[str] = Query(None, alias="from"),
    to_date: Optional[str] = Query(None, alias="to"),
    conn: Connection = Depends(get_db),
) -> Dict[str, Any]:
    """
    Resumen P&L (solo gastos):
    - MTD / QTD / YTD por proyecto y total
    - Si pasas from/to, también devuelve CUSTOM
    """
    from datetime import datetime
    
    def parse_date(val):
        if val is None:
            return None
        if isinstance(val, str):
            return datetime.strptime(val.strip(), "%Y-%m-%d").date()
        return val
    
    row = await conn.fetchrow(
        """
        WITH bounds AS (
          SELECT
            now()::date AS today,
            date_trunc('month', now())::date AS month_start,
            date_trunc('quarter', now())::date AS quarter_start,
            date_trunc('year', now())::date AS year_start
        ),
        sums AS (
          SELECT
            'MTD' AS bucket,
            g.project_key,
            COALESCE(SUM(g.base_imponible),0)::numeric(12,2) AS sum_base,
            COALESCE(SUM(g.iva_importe),0)::numeric(12,2) AS sum_iva,
            COALESCE(SUM(g.total),0)::numeric(12,2) AS sum_total
          FROM gastos g, bounds b
          WHERE g.fecha_gasto >= b.month_start AND g.fecha_gasto <= b.today
          GROUP BY 1,2

          UNION ALL

          SELECT
            'QTD' AS bucket,
            g.project_key,
            COALESCE(SUM(g.base_imponible),0)::numeric(12,2) AS sum_base,
            COALESCE(SUM(g.iva_importe),0)::numeric(12,2) AS sum_iva,
            COALESCE(SUM(g.total),0)::numeric(12,2) AS sum_total
          FROM gastos g, bounds b
          WHERE g.fecha_gasto >= b.quarter_start AND g.fecha_gasto <= b.today
          GROUP BY 1,2

          UNION ALL

          SELECT
            'YTD' AS bucket,
            g.project_key,
            COALESCE(SUM(g.base_imponible),0)::numeric(12,2) AS sum_base,
            COALESCE(SUM(g.iva_importe),0)::numeric(12,2) AS sum_iva,
            COALESCE(SUM(g.total),0)::numeric(12,2) AS sum_total
          FROM gastos g, bounds b
          WHERE g.fecha_gasto >= b.year_start AND g.fecha_gasto <= b.today
          GROUP BY 1,2
        ),
        pivot AS (
          SELECT
            bucket,

            COALESCE(SUM(CASE WHEN project_key='Nucleo_tecnologico' THEN sum_base END),0)::numeric(12,2) AS nucleo_base,
            COALESCE(SUM(CASE WHEN project_key='Nucleo_tecnologico' THEN sum_iva END),0)::numeric(12,2) AS nucleo_iva,
            COALESCE(SUM(CASE WHEN project_key='Nucleo_tecnologico' THEN sum_total END),0)::numeric(12,2) AS nucleo_total,

            COALESCE(SUM(CASE WHEN project_key='Mailerblend' THEN sum_base END),0)::numeric(12,2) AS mailerblend_base,
            COALESCE(SUM(CASE WHEN project_key='Mailerblend' THEN sum_iva END),0)::numeric(12,2) AS mailerblend_iva,
            COALESCE(SUM(CASE WHEN project_key='Mailerblend' THEN sum_total END),0)::numeric(12,2) AS mailerblend_total,

            COALESCE(SUM(CASE WHEN project_key='SHARED' THEN sum_base END),0)::numeric(12,2) AS shared_base,
            COALESCE(SUM(CASE WHEN project_key='SHARED' THEN sum_iva END),0)::numeric(12,2) AS shared_iva,
            COALESCE(SUM(CASE WHEN project_key='SHARED' THEN sum_total END),0)::numeric(12,2) AS shared_total,

            COALESCE(SUM(sum_total),0)::numeric(12,2) AS grand_total
          FROM sums
          GROUP BY 1
        )
        SELECT jsonb_build_object(
          'MTD', (SELECT to_jsonb(p) FROM pivot p WHERE p.bucket='MTD'),
          'QTD', (SELECT to_jsonb(p) FROM pivot p WHERE p.bucket='QTD'),
          'YTD', (SELECT to_jsonb(p) FROM pivot p WHERE p.bucket='YTD')
        ) AS result;
        """
    )

    # JSONB comes as a string, need to deserialize it
    import json
    result = json.loads(row["result"]) if row and row["result"] else {}

    # CUSTOM (si pasan from/to)
    if from_date and to_date:
        custom = await conn.fetchrow(
            """
            WITH s AS (
              SELECT
                project_key,
                COALESCE(SUM(base_imponible),0)::numeric(12,2) AS sum_base,
                COALESCE(SUM(iva_importe),0)::numeric(12,2) AS sum_iva,
                COALESCE(SUM(total),0)::numeric(12,2) AS sum_total
              FROM gastos
              WHERE fecha_gasto >= $1 AND fecha_gasto <= $2
              GROUP BY 1
            )
            SELECT jsonb_build_object(
              'bucket','CUSTOM',
              'from',$1::text,
              'to',$2::text,

              'nucleo_base', COALESCE((SELECT sum_base FROM s WHERE project_key='Nucleo_tecnologico'),0)::numeric(12,2),
              'nucleo_iva', COALESCE((SELECT sum_iva FROM s WHERE project_key='Nucleo_tecnologico'),0)::numeric(12,2),
              'nucleo_total', COALESCE((SELECT sum_total FROM s WHERE project_key='Nucleo_tecnologico'),0)::numeric(12,2),

              'mailerblend_base', COALESCE((SELECT sum_base FROM s WHERE project_key='Mailerblend'),0)::numeric(12,2),
              'mailerblend_iva', COALESCE((SELECT sum_iva FROM s WHERE project_key='Mailerblend'),0)::numeric(12,2),
              'mailerblend_total', COALESCE((SELECT sum_total FROM s WHERE project_key='Mailerblend'),0)::numeric(12,2),

              'shared_base', COALESCE((SELECT sum_base FROM s WHERE project_key='SHARED'),0)::numeric(12,2),
              'shared_iva', COALESCE((SELECT sum_iva FROM s WHERE project_key='SHARED'),0)::numeric(12,2),
              'shared_total', COALESCE((SELECT sum_total FROM s WHERE project_key='SHARED'),0)::numeric(12,2),

              'grand_total', COALESCE((SELECT SUM(sum_total) FROM s),0)::numeric(12,2)
            ) AS result
            """,
            parse_date(from_date),
            parse_date(to_date),
        )
        if custom and custom["result"]:
            result["CUSTOM"] = json.loads(custom["result"])

    return result


@router.get("/pnl-summary-fiscal")
async def gastos_pnl_summary_fiscal(
    from_date: Optional[str] = Query(None, alias="from"),
    to_date: Optional[str] = Query(None, alias="to"),
    conn: Connection = Depends(get_db),
) -> Dict[str, Any]:
    """
    Resumen fiscal (IVA soportado) desde gastos:
    - MTD / QTD / YTD por proyecto y total
    - Si pasas from/to, también devuelve CUSTOM
    Nota: esto es "IVA soportado" (sum(iva_importe)), útil para gestoría.
    Excluye estado='ANULADO'
    """
    from datetime import datetime
    
    def parse_date(val):
        if val is None:
            return None
        if isinstance(val, str):
            return datetime.strptime(val.strip(), "%Y-%m-%d").date()
        return val
    
    row = await conn.fetchrow(
        """
        WITH bounds AS (
          SELECT
            now()::date AS today,
            date_trunc('month', now())::date AS month_start,
            date_trunc('quarter', now())::date AS quarter_start,
            date_trunc('year', now())::date AS year_start
        ),
        sums AS (
          SELECT
            'MTD' AS bucket,
            g.project_key,
            COALESCE(SUM(g.base_imponible),0)::numeric(12,2) AS sum_base,
            COALESCE(SUM(g.iva_importe),0)::numeric(12,2) AS sum_iva,
            COALESCE(SUM(g.total),0)::numeric(12,2) AS sum_total
          FROM gastos g, bounds b
          WHERE g.fecha_gasto >= b.month_start AND g.fecha_gasto <= b.today
            AND g.estado <> 'ANULADO'
          GROUP BY 1,2

          UNION ALL

          SELECT
            'QTD' AS bucket,
            g.project_key,
            COALESCE(SUM(g.base_imponible),0)::numeric(12,2) AS sum_base,
            COALESCE(SUM(g.iva_importe),0)::numeric(12,2) AS sum_iva,
            COALESCE(SUM(g.total),0)::numeric(12,2) AS sum_total
          FROM gastos g, bounds b
          WHERE g.fecha_gasto >= b.quarter_start AND g.fecha_gasto <= b.today
            AND g.estado <> 'ANULADO'
          GROUP BY 1,2

          UNION ALL

          SELECT
            'YTD' AS bucket,
            g.project_key,
            COALESCE(SUM(g.base_imponible),0)::numeric(12,2) AS sum_base,
            COALESCE(SUM(g.iva_importe),0)::numeric(12,2) AS sum_iva,
            COALESCE(SUM(g.total),0)::numeric(12,2) AS sum_total
          FROM gastos g, bounds b
          WHERE g.fecha_gasto >= b.year_start AND g.fecha_gasto <= b.today
            AND g.estado <> 'ANULADO'
          GROUP BY 1,2
        ),
        pivot AS (
          SELECT
            bucket,

            COALESCE(SUM(CASE WHEN project_key='Nucleo_tecnologico' THEN sum_base END),0)::numeric(12,2) AS nucleo_base,
            COALESCE(SUM(CASE WHEN project_key='Nucleo_tecnologico' THEN sum_iva END),0)::numeric(12,2) AS nucleo_iva,
            COALESCE(SUM(CASE WHEN project_key='Nucleo_tecnologico' THEN sum_total END),0)::numeric(12,2) AS nucleo_total,

            COALESCE(SUM(CASE WHEN project_key='Mailerblend' THEN sum_base END),0)::numeric(12,2) AS mailerblend_base,
            COALESCE(SUM(CASE WHEN project_key='Mailerblend' THEN sum_iva END),0)::numeric(12,2) AS mailerblend_iva,
            COALESCE(SUM(CASE WHEN project_key='Mailerblend' THEN sum_total END),0)::numeric(12,2) AS mailerblend_total,

            COALESCE(SUM(CASE WHEN project_key='SHARED' THEN sum_base END),0)::numeric(12,2) AS shared_base,
            COALESCE(SUM(CASE WHEN project_key='SHARED' THEN sum_iva END),0)::numeric(12,2) AS shared_iva,
            COALESCE(SUM(CASE WHEN project_key='SHARED' THEN sum_total END),0)::numeric(12,2) AS shared_total,

            COALESCE(SUM(sum_base),0)::numeric(12,2) AS base_total,
            COALESCE(SUM(sum_iva),0)::numeric(12,2) AS iva_total,
            COALESCE(SUM(sum_total),0)::numeric(12,2) AS total
          FROM sums
          GROUP BY 1
        )
        SELECT jsonb_build_object(
          'MTD', (SELECT to_jsonb(p) FROM pivot p WHERE p.bucket='MTD'),
          'QTD', (SELECT to_jsonb(p) FROM pivot p WHERE p.bucket='QTD'),
          'YTD', (SELECT to_jsonb(p) FROM pivot p WHERE p.bucket='YTD')
        ) AS result;
        """
    )

    # JSONB comes as a string, need to deserialize it
    import json
    result = json.loads(row["result"]) if row and row["result"] else {}

    # CUSTOM (si pasan from/to)
    if from_date and to_date:
        custom = await conn.fetchrow(
            """
            WITH s AS (
              SELECT
                project_key,
                COALESCE(SUM(base_imponible),0)::numeric(12,2) AS sum_base,
                COALESCE(SUM(iva_importe),0)::numeric(12,2) AS sum_iva,
                COALESCE(SUM(total),0)::numeric(12,2) AS sum_total
              FROM gastos
              WHERE fecha_gasto >= $1 AND fecha_gasto <= $2
                AND estado <> 'ANULADO'
              GROUP BY 1
            )
            SELECT jsonb_build_object(
              'bucket','CUSTOM',
              'from',$1::text,
              'to',$2::text,

              'nucleo_base', COALESCE((SELECT sum_base FROM s WHERE project_key='Nucleo_tecnologico'),0)::numeric(12,2),
              'nucleo_iva', COALESCE((SELECT sum_iva FROM s WHERE project_key='Nucleo_tecnologico'),0)::numeric(12,2),
              'nucleo_total', COALESCE((SELECT sum_total FROM s WHERE project_key='Nucleo_tecnologico'),0)::numeric(12,2),

              'mailerblend_base', COALESCE((SELECT sum_base FROM s WHERE project_key='Mailerblend'),0)::numeric(12,2),
              'mailerblend_iva', COALESCE((SELECT sum_iva FROM s WHERE project_key='Mailerblend'),0)::numeric(12,2),
              'mailerblend_total', COALESCE((SELECT sum_total FROM s WHERE project_key='Mailerblend'),0)::numeric(12,2),

              'shared_base', COALESCE((SELECT sum_base FROM s WHERE project_key='SHARED'),0)::numeric(12,2),
              'shared_iva', COALESCE((SELECT sum_iva FROM s WHERE project_key='SHARED'),0)::numeric(12,2),
              'shared_total', COALESCE((SELECT sum_total FROM s WHERE project_key='SHARED'),0)::numeric(12,2),

              'base_total', COALESCE((SELECT SUM(sum_base) FROM s),0)::numeric(12,2),
              'iva_total', COALESCE((SELECT SUM(sum_iva) FROM s),0)::numeric(12,2),
              'total', COALESCE((SELECT SUM(sum_total) FROM s),0)::numeric(12,2)
            ) AS result
            """,
            parse_date(from_date),
            parse_date(to_date),
        )
        if custom and custom["result"]:
            result["CUSTOM"] = json.loads(custom["result"])

    return result
@router.get("/{gasto_id}")
async def get_gasto(
    gasto_id: UUID,
    conn: Connection = Depends(get_db),
) -> Dict[str, Any]:
    row = await conn.fetchrow("SELECT * FROM gastos WHERE id=$1", gasto_id)
    if not row:
        raise HTTPException(status_code=404, detail="Gasto not found")
    return dict(row)


@router.post("")
async def create_gasto(
    payload: Dict[str, Any] = Body(...),
    conn: Connection = Depends(get_db),
) -> Dict[str, Any]:
    from datetime import datetime
    
    def parse_date(val):
        """Convert date string to Python date object for asyncpg"""
        if val is None:
            return None
        if isinstance(val, str):
            return datetime.strptime(val.strip(), "%Y-%m-%d").date()
        return val
    
    # mínimos
    fecha_gasto = payload.get("fecha_gasto")
    concepto = (payload.get("concepto") or "").strip()
    if not fecha_gasto:
        raise HTTPException(status_code=400, detail="fecha_gasto is required (YYYY-MM-DD)")
    if not concepto:
        raise HTTPException(status_code=400, detail="concepto is required")

    # proveedor snapshot automático si nos pasan proveedor_id
    proveedor_id = payload.get("proveedor_id")
    proveedor_nombre = (payload.get("proveedor_nombre") or None)

    if proveedor_id and not proveedor_nombre:
        p = await conn.fetchrow("SELECT nombre FROM proveedores WHERE id=$1", UUID(str(proveedor_id)))
        if p:
            proveedor_nombre = p["nombre"]

    row = await conn.fetchrow(
        """
        INSERT INTO gastos (
          fecha_gasto, fecha_vencimiento,
          proveedor_id, proveedor_nombre,
          concepto, categoria, project_key,
          base_imponible, iva_porcentaje,
          currency, estado, metodo_pago,
          numero_factura, adjunto_url,
          notas, internal_notes
        ) VALUES (
          $1, $2,
          $3, $4,
          $5, $6, $7,
          $8, $9,
          $10, $11, $12,
          $13, $14,
          $15, $16
        )
        RETURNING *
        """,
        parse_date(fecha_gasto),
        parse_date(payload.get("fecha_vencimiento")),
        UUID(str(proveedor_id)) if proveedor_id else None,
        proveedor_nombre,
        concepto,
        (payload.get("categoria") or "OTRO"),
        (payload.get("project_key") or "Nucleo_tecnologico"),
        payload.get("base_imponible", 0),
        payload.get("iva_porcentaje", 21),
        (payload.get("currency") or "EUR"),
        (payload.get("estado") or "PAGADO"),
        payload.get("metodo_pago", "Transferencia"),
        payload.get("numero_factura"),
        payload.get("adjunto_url"),
        payload.get("notas"),
        payload.get("internal_notes"),
    )

    return dict(row)


@router.patch("/{gasto_id}")
async def patch_gasto(
    gasto_id: UUID,
    payload: Dict[str, Any] = Body(...),
    conn: Connection = Depends(get_db),
) -> Dict[str, Any]:
    from datetime import datetime
    
    def parse_date(val):
        """Convert date string to Python date object for asyncpg"""
        if val is None:
            return None
        if isinstance(val, str):
            s = val.strip()
            if not s:
                return None
            return datetime.strptime(s, "%Y-%m-%d").date()
        return val
    
    before = await conn.fetchrow("SELECT * FROM gastos WHERE id=$1", gasto_id)
    if not before:
        raise HTTPException(status_code=404, detail="Gasto not found")

    editable = {
        "fecha_gasto",
        "fecha_vencimiento",
        "proveedor_id",
        "proveedor_nombre",
        "concepto",
        "categoria",
        "project_key",
        "base_imponible",
        "iva_porcentaje",
        "currency",
        "estado",
        "metodo_pago",
        "numero_factura",
        "adjunto_url",
        "notas",
        "internal_notes",
    }

    updates = {k: payload.get(k) for k in editable if k in payload}
    if not updates:
        return dict(before)

    # si cambian proveedor_id y no mandan proveedor_nombre, intentamos resolver
    if "proveedor_id" in updates and "proveedor_nombre" not in updates:
        pid = updates.get("proveedor_id")
        if pid:
            p = await conn.fetchrow("SELECT nombre FROM proveedores WHERE id=$1", UUID(str(pid)))
            if p:
                updates["proveedor_nombre"] = p["nombre"]

    # Parse dates to Python date objects
    if "fecha_gasto" in updates:
        updates["fecha_gasto"] = parse_date(updates["fecha_gasto"])
    if "fecha_vencimiento" in updates:
        updates["fecha_vencimiento"] = parse_date(updates["fecha_vencimiento"])

    set_parts: List[str] = []
    args: List[Any] = []
    idx = 1

    for k, v in updates.items():
        if k == "proveedor_id":
            set_parts.append(f"{k} = ${idx}")
            args.append(UUID(str(v)) if v else None)
        else:
            set_parts.append(f"{k} = ${idx}")
            args.append(v)
        idx += 1

    args.append(gasto_id)
    sql = f"UPDATE gastos SET {', '.join(set_parts)} WHERE id = ${idx} RETURNING *"

    try:
        after = await conn.fetchrow(sql, *args)
    except Exception as e:
        msg = str(e)
        if "violates check constraint" in msg:
            raise HTTPException(status_code=400, detail=f"Invalid value (check constraint): {msg}")
        raise

    return dict(after)