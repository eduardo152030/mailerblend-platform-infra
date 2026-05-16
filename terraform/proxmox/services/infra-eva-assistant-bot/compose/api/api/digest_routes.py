"""
api/digest_routes.py
====================
Daily briefing endpoints.
To debug digest issues: inspect only this file.
"""
from datetime import datetime, timedelta

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import select

from db import SessionLocal
from models import User, Reminder, Event, Message
from core.config import TZ
from utils.time_utils import to_local
from telegram_service import send_message
from scheduler import build_daily_digest

router = APIRouter()


@router.post("/digest/send")
async def trigger_daily_digest(user_id: int | None = None):
    """
    Trigger the daily briefing with AI.
    - No params: send to all users.
    - user_id param: send only to that user.
    """
    from ai_parser import build_briefing_ai
    from memory_service import get_user_facts
    from persona_service import load_persona

    db = SessionLocal()
    try:
        async def _send(chat_id: int, text_out: str, parse_mode: str = "Markdown"):
            await send_message(chat_id, text_out, parse_mode=parse_mode)

        async def _send_briefing_to_user(user: User) -> bool:
            now         = datetime.now(TZ)
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            today_end   = now.replace(hour=23, minute=59, second=59, microsecond=0)

            today_reminders = db.execute(
                select(Reminder)
                .where(Reminder.user_id == user.id)
                .where(Reminder.status.in_(["scheduled", "pending"]))
                .where(Reminder.remind_at >= today_start)
                .where(Reminder.remind_at <= today_end)
                .order_by(Reminder.remind_at.asc())
            ).scalars().all()

            reminders_data = [
                {
                    "id": r.id,
                    "task_text": r.task_text,
                    "remind_at": to_local(r.remind_at).strftime("%H:%M") if to_local(r.remind_at) else "?",
                    "status": r.status,
                }
                for r in today_reminders
            ]

            yesterday_start = (now - timedelta(days=1)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            recent_events_raw = db.execute(
                select(Event)
                .where(Event.user_id == user.id)
                .where(Event.event_type.in_([
                    "reminder_rescheduled", "reminder_cancelled",
                    "reminder_corrected", "reminder_created",
                ]))
                .where(Event.created_at >= yesterday_start)
                .order_by(Event.created_at.desc())
                .limit(10)
            ).scalars().all()

            events_data = [
                {"type": e.event_type, "value": e.event_value or "", "payload": e.payload}
                for e in recent_events_raw
            ]
            for ev in events_data:
                if "task_text" in (ev["payload"] or {}):
                    ev["value"] = ev["payload"]["task_text"]

            user_facts = get_user_facts(db, user.id)
            persona    = load_persona(user.telegram_username)

            briefing = await build_briefing_ai(
                reminders_today=reminders_data,
                recent_events=events_data,
                user_facts=user_facts,
                persona=persona,
            )
            if not briefing:
                briefing = build_daily_digest(db, user)
            if not briefing:
                return False

            await _send(user.telegram_chat_id, briefing, parse_mode="Markdown")
            db.add(Message(user_id=user.id, direction="outbound",
                           message_text=briefing, message_type="daily_digest"))
            db.add(Event(user_id=user.id, event_type="daily_digest_sent",
                         event_value=str(now.date()), source="api",
                         payload={"triggered_by": "manual", "ai": True}))
            db.commit()
            return True

        if user_id is not None:
            user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
            if not user:
                return JSONResponse(
                    status_code=404,
                    content={"status": "error", "reason": "user_not_found"},
                )
            sent = await _send_briefing_to_user(user)
            return {"status": "ok", "sent": 1 if sent else 0}

        users = db.execute(select(User)).scalars().all()
        count = 0
        for u in users:
            try:
                if await _send_briefing_to_user(u):
                    count += 1
            except Exception as exc:
                print(f"[digest] error user {u.id}: {exc}")
        return {"status": "ok", "sent": count}

    finally:
        db.close()


@router.get("/digest/preview/{user_id}")
async def preview_daily_digest(user_id: int):
    """Return digest text without sending it. Useful for debugging."""
    db = SessionLocal()
    try:
        user = db.execute(
            select(User).where(User.id == user_id)
        ).scalar_one_or_none()
        if not user:
            return JSONResponse(
                status_code=404,
                content={"status": "error", "reason": "user_not_found"},
            )
        digest = build_daily_digest(db, user)
        return {"status": "ok", "digest": digest or "", "has_content": digest is not None}
    finally:
        db.close()
