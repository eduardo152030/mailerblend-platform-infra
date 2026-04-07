import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from sqlalchemy import select
from models import Reminder, Event

TZ = ZoneInfo(os.getenv("TIMEZONE", "Europe/Madrid"))

def to_local(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=TZ)
    return dt.astimezone(TZ)

def next_occurrence(reminder: Reminder) -> datetime | None:
    current = to_local(reminder.remind_at)

    if reminder.recurrence_type == "weekly" and reminder.recurrence_value:
        return current + timedelta(days=7)

    if reminder.recurrence_type == "weekdays":
        nxt = current + timedelta(days=1)
        while nxt.weekday() >= 5:
            nxt = nxt + timedelta(days=1)
        return nxt

    return None

def should_cancel_due_to_event(db, reminder: Reminder) -> bool:
    if not reminder.cancel_on_event_type:
        return False

    event = db.execute(
        select(Event)
        .where(Event.user_id == reminder.user_id)
        .where(Event.event_type == reminder.cancel_on_event_type)
        .where(Event.created_at >= reminder.created_at)
        .order_by(Event.created_at.desc())
        .limit(1)
    ).scalar_one_or_none()

    return event is not None

def build_confirmation_text(reminder: Reminder) -> str:
    local_dt = to_local(reminder.remind_at)
    return f'🧠 EVA: Te recordaré "{reminder.task_text}" el {local_dt.strftime("%Y-%m-%d %H:%M")}.'

def build_due_text(reminder: Reminder) -> str:
    return f'⏰ EVA: Es hora de {reminder.task_text}.'
