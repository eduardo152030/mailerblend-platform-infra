import asyncio
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from sqlalchemy import select
from db import SessionLocal
from models import Reminder, User, Message, Event
from telegram_service import send_message
from reminder_service import next_occurrence, should_cancel_due_to_event, build_due_text

POLL_SECONDS = int(os.getenv("SCHEDULER_POLL_SECONDS", "15"))
DEFAULT_RETRY_DELAY_MINUTES = int(os.getenv("DEFAULT_RETRY_DELAY_MINUTES", "5"))
TZ = ZoneInfo(os.getenv("TIMEZONE", "Europe/Madrid"))

async def process_due_reminders():
    now = datetime.now(TZ)

    db = SessionLocal()
    try:
        due_rows = db.execute(
            select(Reminder)
            .where(Reminder.status.in_(["pending", "scheduled"]))
            .where(Reminder.remind_at <= now)
            .order_by(Reminder.remind_at.asc())
        ).scalars().all()

        for reminder in due_rows:
            user = db.execute(
                select(User).where(User.id == reminder.user_id)
            ).scalar_one_or_none()

            if not user:
                reminder.status = "failed"
                reminder.error_message = "user_not_found"
                continue

            if should_cancel_due_to_event(db, reminder):
                reminder.status = "cancelled"
                reminder.error_message = "cancelled_by_event"
                db.add(Event(
                    user_id=reminder.user_id,
                    event_type="reminder_auto_cancelled",
                    event_value=str(reminder.id),
                    source="scheduler",
                    payload={"reason": "cancel_on_event_type_matched"},
                ))
                continue

            try:
                due_text = build_due_text(reminder)
                await send_message(user.telegram_chat_id, due_text)

                reminder.last_sent_at = now

                if reminder.recurrence_type:
                    nxt = next_occurrence(reminder)
                    reminder.remind_at = nxt
                    reminder.status = "scheduled"
                    reminder.sent_at = now
                elif reminder.remind_if_no_response:
                    reminder.status = "scheduled"
                    reminder.sent_at = now
                    reminder.remind_at = now + timedelta(minutes=reminder.retry_delay_minutes or DEFAULT_RETRY_DELAY_MINUTES)
                else:
                    reminder.status = "sent"
                    reminder.sent_at = now

                db.add(Message(
                    user_id=reminder.user_id,
                    direction="outbound",
                    message_text=due_text,
                    message_type="reminder_due",
                ))

                db.add(Event(
                    user_id=reminder.user_id,
                    event_type="reminder_sent",
                    event_value=str(reminder.id),
                    source="scheduler",
                    payload={"task_text": reminder.task_text},
                ))

            except Exception as exc:
                reminder.status = "failed"
                reminder.error_message = str(exc)

        db.commit()
    finally:
        db.close()

async def main():
    while True:
        await process_due_reminders()
        await asyncio.sleep(POLL_SECONDS)

if __name__ == "__main__":
    asyncio.run(main())
