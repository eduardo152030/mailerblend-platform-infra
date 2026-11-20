"""Read the recorded conversions for FormEntries."""
from datetime import date
from typing import Annotated, Literal
from uuid import UUID

from asyncpg import Connection
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from app.db import get_db

router = APIRouter(prefix="/v1/conversiones-offline", tags=["conversiones-offline"])


class ConversionFilters(BaseModel):
    sync_status: Literal["PENDING", "SENT", "SYNCED", "FAILED", "SKIPPED"] | None = None
    platform: Literal["GOOGLE", "BING", "LINKEDIN", "FACEBOOK"] | None = None
    event_name: Literal["Lead_Submitted", "Lead_Qualified", "Lead_Won", "Purchase", "Custom"] | None = None
    from_date: date | None = Query(None, alias="from")
    to_date: date | None = Query(None, alias="to")

    def values(self) -> tuple:
        if self.from_date and self.to_date and self.from_date > self.to_date:
            raise HTTPException(422, "Invalid conversion dates")
        status = "SENT" if self.sync_status == "SYNCED" else self.sync_status
        return status, self.platform, self.event_name, self.from_date, self.to_date


class ConversionPage(ConversionFilters):
    limit: int = Query(50, ge=1, le=200)
    offset: int = Query(0, ge=0)


FILTER = """
WHERE ($1::text IS NULL OR sync_status = $1)
  AND ($2::text IS NULL OR platform = $2)
  AND ($3::text IS NULL OR event_name = $3)
  AND ($4::date IS NULL OR conversion_time >= $4)
  AND ($5::date IS NULL OR conversion_time < $5 + 1)
"""


@router.get("")
async def list_conversions(
    filters: Annotated[ConversionPage, Query()],
    conn: Connection = Depends(get_db),
):
    args = filters.values()
    limit, offset = filters.limit, filters.offset
    rows = await conn.fetch(
        "SELECT * FROM conversiones_offline " + FILTER
        + " ORDER BY conversion_time DESC, id DESC LIMIT $6 OFFSET $7",
        *args, limit, offset,
    )
    total = await conn.fetchval("SELECT count(*) FROM conversiones_offline " + FILTER, *args)
    return {"items": [dict(row) for row in rows], "count": len(rows), "total": total,
            "limit": limit, "offset": offset}


@router.get("/stats")
async def conversion_stats(
    filters: Annotated[ConversionFilters, Query()],
    conn: Connection = Depends(get_db),
):
    rows = await conn.fetch(
        """SELECT platform, event_name, sync_status, currency,
           count(*) AS count, COALESCE(sum(conversion_value), 0) AS total_value
           FROM conversiones_offline """
        + FILTER + " GROUP BY platform, event_name, sync_status, currency",
        *filters.values(),
    )
    return {"items": [dict(row) for row in rows]}


@router.get("/{conversion_id}")
async def conversion_detail(conversion_id: UUID, conn: Connection = Depends(get_db)):
    row = await conn.fetchrow("SELECT * FROM conversiones_offline WHERE id = $1", conversion_id)
    if row is None:
        raise HTTPException(404, "Conversion not found")
    return dict(row)
