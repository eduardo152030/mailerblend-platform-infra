"""Read-only FormEntries lists for web submissions, invoices and activity."""
from typing import Annotated

from asyncpg import Connection
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from app.db import get_db

router = APIRouter(tags=["form-entries"])


class Page(BaseModel):
    limit: int = Query(50, ge=1, le=200)
    offset: int = Query(0, ge=0)


def page_result(rows, total, page):
    return {"items": [dict(row) for row in rows], "count": len(rows), "total": total,
            "limit": page.limit, "offset": page.offset}


@router.get("/v1/formulario-web")
async def list_submissions(page: Annotated[Page, Query()], conn: Connection = Depends(get_db)):
    rows = await conn.fetch(
        """SELECT id, contacto_id, contacto_nombre, servicio_relacionado, mensaje, origen, submitted_at
           FROM formulario_web ORDER BY submitted_at DESC NULLS LAST, id DESC LIMIT $1 OFFSET $2""",
        page.limit, page.offset,
    )
    return page_result(rows, await conn.fetchval("SELECT count(*) FROM formulario_web"), page)


@router.get("/v1/facturas")
async def list_invoices(page: Annotated[Page, Query()], conn: Connection = Depends(get_db)):
    rows = await conn.fetch(
        """SELECT id, contacto_id, invoice_number, invoice_value, currency, status, issue_date, due_date
           FROM facturas ORDER BY issue_date DESC NULLS LAST, id DESC LIMIT $1 OFFSET $2""",
        page.limit, page.offset,
    )
    return page_result(rows, await conn.fetchval("SELECT count(*) FROM facturas"), page)


@router.get("/v1/historial")
async def list_activity(page: Annotated[Page, Query()], conn: Connection = Depends(get_db)):
    scope = "WHERE linkedin_lead_id IS NULL AND (contacto_id IS NOT NULL OR oportunidad_id IS NOT NULL)"
    rows = await conn.fetch(
        """SELECT id, contacto_id, oportunidad_id, type, subject, COALESCE(activity_date, created_at) AS occurred_at
           FROM historial """
        + scope + " ORDER BY COALESCE(activity_date, created_at) DESC NULLS LAST, id DESC LIMIT $1 OFFSET $2",
        page.limit, page.offset,
    )
    return page_result(rows, await conn.fetchval("SELECT count(*) FROM historial " + scope), page)
