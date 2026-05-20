"""
api/reminder_routes.py
======================
REST endpoints for reminders and tasks (read + cancel + parse).
To debug reminder list/cancel issues: inspect only this file.
"""
from datetime import datetime
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import select

from db import SessionLocal
from models import Reminder, Event
from core.config import TZ
from utils.time_utils import serialize_reminder
from parser_service import parse_reminder

router = APIRouter()


class ParseCommandRequest(BaseModel):
    text: str


class CancelReminderRequest(BaseModel):
    reason: str | None = None


@router.post("/commands/parse")
async def commands_parse(body: ParseCommandRequest):
    parsed = parse_reminder(body.text)
    if not parsed:
        return {"status": "unrecognized", "parsed": None}
    response = dict(parsed)
    response["remind_at"] = parsed["remind_at"].isoformat()
    if parsed.get("stop_at"):
        response["stop_at"] = parsed["stop_at"].isoformat()
    return {"status": "ok", "parsed": response}


@router.get("/reminders")
async def list_reminders(status: str | None = None):
    db = SessionLocal()
    try:
        stmt = select(Reminder).order_by(Reminder.id.desc())
        if status:
            stmt = stmt.where(Reminder.status == status)
        rows = db.execute(stmt).scalars().all()
        return {"items": [serialize_reminder(r) for r in rows]}
    finally:
        db.close()


@router.get("/tasks")
async def list_tasks(
    board_id: str | None = None,
    limit: int = 500,
):
    """
    Return tasks enriched with smart badge metadata.
    One call → UI can paint all badges (📎 Attachment, 🔁 Recurring,
    ⏰ Overdue, 🏷️ Tags, 🤖 EVA source) without extra fetches.

    Query params:
      ?board_id=...   filter by Focalboard board (tasks vs content)
      ?limit=N        default 500
    """
    from sqlalchemy import text as _text
    from core.config import FOCALBOARD_BOARD_ID, CONTENT_BOARD_ID

    db = SessionLocal()
    try:
        now = datetime.now(TZ)

        # ── Attachment counts — one query for all tasks ───────────────────
        att_rows = db.execute(_text(
            "SELECT reminder_id, COUNT(*) as cnt "
            "FROM task_attachments GROUP BY reminder_id"
        )).fetchall()
        att_map: dict[int, int] = {row[0]: row[1] for row in att_rows}

        # ── Fetch reminders ───────────────────────────────────────────────
        stmt = select(Reminder).order_by(Reminder.remind_at.asc())

        # Filter by board_id via tags heuristic:
        # content board tasks have #contenido in tags
        if board_id:
            if board_id == CONTENT_BOARD_ID:
                stmt = stmt.where(Reminder.tags.ilike("%#contenido%"))
            else:
                # tasks board = everything that is NOT content
                stmt = stmt.where(
                    (Reminder.tags.is_(None)) |
                    (~Reminder.tags.ilike("%#contenido%"))
                )

        stmt = stmt.limit(limit)
        rows = db.execute(stmt).scalars().all()

        def _recurrence_label(r: Reminder) -> str | None:
            if r.recurrence_type == "weekly" and r.recurrence_value:
                return f"weekly ({r.recurrence_value})"
            if r.recurrence_type == "weekdays":
                return "weekdays"
            if r.recurrence_type == "daily":
                return "daily"
            if r.repeat_every_minutes:
                if r.repeat_every_minutes >= 60:
                    return f"every {r.repeat_every_minutes // 60}h"
                return f"every {r.repeat_every_minutes}m"
            return None

        def _is_overdue(r: Reminder) -> bool:
            if r.status in ("completed", "cancelled", "sent", "expired"):
                return False
            if not r.remind_at:
                return False
            local_dt = r.remind_at
            if local_dt.year >= 2099:
                return False
            if local_dt.tzinfo is None:
                local_dt = local_dt.replace(tzinfo=TZ)
            return local_dt < now

        def _board_id(r: Reminder) -> str:
            tags = (r.tags or "").lower()
            return CONTENT_BOARD_ID if "#contenido" in tags else FOCALBOARD_BOARD_ID

        def _serialize(r: Reminder) -> dict:
            att_count    = att_map.get(r.id, 0)
            is_recurring = bool(
                r.recurrence_type or
                (r.repeat_every_minutes and r.is_persistent)
            )
            return {
                "id":                r.id,
                "focalboard_card_id": getattr(r, "focalboard_card_id", None),
                "board_id":          _board_id(r),
                "task_text":         r.task_text,
                "status":            r.status,
                "priority":          getattr(r, "priority", "P3"),
                "tags":              r.tags,
                "remind_at":         r.remind_at.isoformat() if r.remind_at else None,
                "attachments_count": att_count,
                "has_attachments":   att_count > 0,
                "is_recurring":      is_recurring,
                "recurrence_label":  _recurrence_label(r),
                "is_eva_source":     True,  # all tasks in EVA DB are EVA-created
                "is_overdue":        _is_overdue(r),
            }

        return {"items": [_serialize(r) for r in rows], "total": len(rows)}
    finally:
        db.close()


@router.get("/users/{user_id}/reminders")
async def list_user_reminders(user_id: int, status: str | None = None):
    db = SessionLocal()
    try:
        stmt = (
            select(Reminder)
            .where(Reminder.user_id == user_id)
            .order_by(Reminder.id.desc())
        )
        if status:
            stmt = stmt.where(Reminder.status == status)
        rows = db.execute(stmt).scalars().all()
        return {"items": [serialize_reminder(r) for r in rows]}
    finally:
        db.close()


@router.post("/reminders/{reminder_id}/cancel")
async def cancel_reminder(reminder_id: int, body: CancelReminderRequest):
    db = SessionLocal()
    try:
        reminder = db.execute(
            select(Reminder).where(Reminder.id == reminder_id)
        ).scalar_one_or_none()

        if not reminder:
            return JSONResponse(
                status_code=404,
                content={"status": "error", "reason": "reminder_not_found"},
            )

        now = datetime.now(TZ)
        reminder.status      = "cancelled"
        reminder.awaiting_ack = False
        reminder.cancelled_at = now
        reminder.error_message = body.reason

        db.add(
            Event(
                user_id=reminder.user_id,
                event_type="reminder_cancelled",
                event_value=str(reminder.id),
                source="api",
                payload={"reason": body.reason} if body.reason else {},
            )
        )
        db.commit()
        return {"status": "ok", "item": serialize_reminder(reminder)}
    finally:
        db.close()