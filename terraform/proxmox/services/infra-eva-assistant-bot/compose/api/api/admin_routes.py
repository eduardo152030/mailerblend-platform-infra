"""
api/admin_routes.py
====================
Admin utility endpoints.
To debug backfill issues: inspect only this file.
"""
import json
from fastapi import APIRouter
from sqlalchemy import select

from db import SessionLocal
from models import Reminder
from utils.time_utils import to_local

router = APIRouter()


@router.post("/admin/backfill-dates")
async def backfill_focalboard_dates():
    """
    Write the Date property to Focalboard for all reminders that have
    remind_at set but the property is empty. Run once after deploy.
    """
    import httpx as _hx
    from sync_service import (STATUS_OPTIONS, STATUS_PROP_ID, DATE_PROP_ID,
                               TEXT_PROP_ID, URL_PROP_ID, PRIORITY_PROP_ID,
                               PRIORITY_OPTIONS, FOCALBOARD_URL as _FB_URL,
                               FOCALBOARD_TOKEN as _FB_TOK,
                               FOCALBOARD_BOARD_ID as _FB_BID, _h)
    db = SessionLocal()
    updated = skipped = errors = 0
    try:
        rows = db.execute(
            select(Reminder)
            .where(Reminder.focalboard_card_id.isnot(None))
            .where(Reminder.remind_at.isnot(None))
        ).scalars().all()

        for r in rows:
            local_dt = to_local(r.remind_at)
            if not local_dt or local_dt.year >= 2099:
                skipped += 1
                continue
            try:
                date_val = json.dumps({"from": int(local_dt.timestamp() * 1000)})
                props = {
                    STATUS_PROP_ID: STATUS_OPTIONS.get(r.status, "aoptpendiente00000000000001"),
                    DATE_PROP_ID:   date_val,
                }
                if getattr(r, "notes",    None): props[TEXT_PROP_ID]     = r.notes
                if getattr(r, "url",      None): props[URL_PROP_ID]      = r.url
                if getattr(r, "priority", None) and r.priority in PRIORITY_OPTIONS:
                    props[PRIORITY_PROP_ID] = PRIORITY_OPTIONS[r.priority]

                async with _hx.AsyncClient(timeout=8) as client:
                    resp = await client.patch(
                        f"{_FB_URL}/api/v2/boards/{_FB_BID}/blocks/{r.focalboard_card_id}",
                        headers=_h(),
                        json={"updatedFields": {"properties": props}},
                    )
                    if resp.status_code in (200, 204):
                        updated += 1
                    else:
                        errors += 1
            except Exception as exc:
                print(f"[backfill] error {r.id}: {exc}")
                errors += 1

        return {"updated": updated, "skipped": skipped, "errors": errors, "total": len(rows)}
    finally:
        db.close()
