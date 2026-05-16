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
async def list_tasks():
    db = SessionLocal()
    try:
        rows = db.execute(
            select(Reminder)
            .where(Reminder.status.in_(["pending", "scheduled", "sent"]))
            .order_by(Reminder.remind_at.asc())
        ).scalars().all()
        return {"items": [serialize_reminder(r) for r in rows]}
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
