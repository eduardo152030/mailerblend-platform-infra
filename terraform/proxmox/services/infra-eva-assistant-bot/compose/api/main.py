import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy import select, text
from db import engine, SessionLocal
from models import User, Reminder, Message, Event
from parser_service import parse_reminder
from telegram_service import send_message
from reminder_service import build_confirmation_text
from schemas import ParseCommandRequest, CancelReminderRequest, EventCreateRequest

APP_NAME = os.getenv("APP_NAME", "eva-assistant-bot")

app = FastAPI(title=APP_NAME)


def serialize_reminder(r: Reminder) -> dict:
    return {
        "id": r.id,
        "user_id": r.user_id,
        "task_text": r.task_text,
        "source_text": r.source_text,
        "status": r.status,
        "remind_at": r.remind_at.isoformat() if r.remind_at else None,
        "recurrence_type": r.recurrence_type,
        "recurrence_value": r.recurrence_value,
        "weekdays_only": r.weekdays_only,
        "remind_if_no_response": r.remind_if_no_response,
        "retry_delay_minutes": r.retry_delay_minutes,
        "cancel_on_event_type": r.cancel_on_event_type,
        "created_at": r.created_at.isoformat() if r.created_at else None,
        "sent_at": r.sent_at.isoformat() if r.sent_at else None,
        "last_sent_at": r.last_sent_at.isoformat() if r.last_sent_at else None,
        "acked_at": r.acked_at.isoformat() if r.acked_at else None,
        "error_message": r.error_message,
    }

def serialize_event(e: Event) -> dict:
    return {
        "id": e.id,
        "user_id": e.user_id,
        "event_type": e.event_type,
        "event_value": e.event_value,
        "source": e.source,
        "payload": e.payload,
        "created_at": e.created_at.isoformat() if e.created_at else None,
    }


@app.get("/")
async def root():
    return {"service": APP_NAME, "message": "EVA API running"}


@app.get("/health")
async def health():
    return {"status": "ok", "service": APP_NAME}


@app.get("/ready")
async def ready():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ready", "service": APP_NAME}
    except Exception as exc:
        return JSONResponse(
            status_code=503,
            content={"status": "not_ready", "reason": str(exc)}
        )


@app.post("/commands/parse")
async def commands_parse(body: ParseCommandRequest):
    parsed = parse_reminder(body.text)
    if not parsed:
        return {"status": "unrecognized", "parsed": None}
    return {
        "status": "ok",
        "parsed": {
            **parsed,
            "remind_at": parsed["remind_at"].isoformat(),
        },
    }


@app.get("/reminders")
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


@app.get("/tasks")
async def list_tasks():
    db = SessionLocal()
    try:
        rows = db.execute(
            select(Reminder)
            .where(Reminder.status.in_(["pending", "scheduled"]))
            .order_by(Reminder.remind_at.asc())
        ).scalars().all()
        return {"items": [serialize_reminder(r) for r in rows]}
    finally:
        db.close()


@app.get("/users/{user_id}/reminders")
async def list_user_reminders(user_id: int, status: str | None = None):
    db = SessionLocal()
    try:
        stmt = select(Reminder).where(Reminder.user_id == user_id).order_by(Reminder.id.desc())
        if status:
            stmt = stmt.where(Reminder.status == status)
        rows = db.execute(stmt).scalars().all()
        return {"items": [serialize_reminder(r) for r in rows]}
    finally:
        db.close()


@app.post("/reminders/{reminder_id}/cancel")
async def cancel_reminder(reminder_id: int, body: CancelReminderRequest):
    db = SessionLocal()
    try:
        reminder = db.execute(
            select(Reminder).where(Reminder.id == reminder_id)
        ).scalar_one_or_none()

        if not reminder:
            return JSONResponse(status_code=404, content={"status": "error", "reason": "reminder_not_found"})

        reminder.status = "cancelled"
        reminder.error_message = body.reason

        db.add(Event(
            user_id=reminder.user_id,
            event_type="reminder_cancelled",
            event_value=str(reminder.id),
            source="api",
            payload={"reason": body.reason} if body.reason else {},
        ))
        db.commit()

        return {"status": "ok", "item": serialize_reminder(reminder)}
    finally:
        db.close()


@app.post("/events")
async def create_event(body: EventCreateRequest):
    db = SessionLocal()
    try:
        event = Event(
            user_id=body.user_id,
            event_type=body.event_type,
            event_value=body.event_value,
            source=body.source,
            payload=body.payload,
        )
        db.add(event)
        db.commit()
        db.refresh(event)
        return {"status": "ok", "item": serialize_event(event)}
    finally:
        db.close()


@app.get("/events")
async def list_events(user_id: int | None = None, event_type: str | None = None):
    db = SessionLocal()
    try:
        stmt = select(Event).order_by(Event.id.desc())
        if user_id is not None:
            stmt = stmt.where(Event.user_id == user_id)
        if event_type:
            stmt = stmt.where(Event.event_type == event_type)
        rows = db.execute(stmt).scalars().all()
        return {"items": [serialize_event(e) for e in rows]}
    finally:
        db.close()


@app.post("/telegram/webhook")
async def telegram_webhook(request: Request):
    payload = await request.json()
    message = payload.get("message") or {}
    text_in = message.get("text")

    if not text_in:
        return {"status": "ignored", "reason": "no_text_message"}

    chat = message.get("chat") or {}
    from_user = message.get("from") or {}

    chat_id = chat.get("id")
    telegram_username = from_user.get("username")
    display_name = " ".join(
        x for x in [from_user.get("first_name"), from_user.get("last_name")] if x
    ) or telegram_username or "Unknown"

    db = SessionLocal()
    try:
        user = db.execute(
            select(User).where(User.telegram_chat_id == chat_id)
        ).scalar_one_or_none()

        if user is None:
            user = User(
                telegram_chat_id=chat_id,
                telegram_username=telegram_username,
                display_name=display_name,
                timezone="Europe/Madrid",
            )
            db.add(user)
            db.flush()
        else:
            user.telegram_username = telegram_username
            user.display_name = display_name

        db.add(Message(
            user_id=user.id,
            direction="inbound",
            message_text=text_in,
            message_type="chat",
        ))

        lowered = text_in.lower().strip()
        if lowered in ["/reminders", "eva, /reminders", "eva reminders", "eva, reminders"]:
            rows = db.execute(
                select(Reminder)
                .where(Reminder.user_id == user.id)
                .where(Reminder.status.in_(["pending", "scheduled"]))
                .order_by(Reminder.remind_at.asc())
            ).scalars().all()

            if rows:
                reply = "📋 Recordatorios activos:\n" + "\n".join(
                    f'- [{r.id}] {r.task_text} @ {r.remind_at.strftime("%Y-%m-%d %H:%M")}'
                    for r in rows
                )
            else:
                reply = "📋 No tienes recordatorios activos."

            db.commit()
            await send_message(chat_id, reply)
            return {"status": "ok", "action": "reminders_list_sent"}

        parsed = parse_reminder(text_in)

        if parsed:
            reminder = Reminder(
                user_id=user.id,
                source_text=text_in,
                task_text=parsed["task_text"],
                remind_at=parsed["remind_at"],
                status=parsed["status"],
                recurrence_type=parsed["recurrence_type"],
                recurrence_value=parsed["recurrence_value"],
                weekdays_only=parsed["weekdays_only"],
                remind_if_no_response=parsed["remind_if_no_response"],
                retry_delay_minutes=parsed["retry_delay_minutes"],
                cancel_on_event_type=parsed["cancel_on_event_type"],
            )
            db.add(reminder)
            db.commit()
            db.refresh(reminder)

            reply_text = build_confirmation_text(reminder)
            await send_message(chat_id, reply_text)

            db.add(Message(
                user_id=user.id,
                direction="outbound",
                message_text=reply_text,
                message_type="reminder_confirmation",
            ))
            db.commit()

            return {"status": "ok", "action": "reminder_created", "reminder_id": reminder.id}

        db.commit()

        help_text = (
            "No te entendí del todo. Prueba con:\n"
            "- eva, recuérdame en 2 minutos probar sistema\n"
            "- mañana recuérdame fichar a las 08:00\n"
            "- cada lunes recuérdame revisión semanal a las 09:00\n"
            "- eva, recuérdame fichar a las 08:00, solo días laborables\n"
            "- eva, recuérdame fichar a las 08:00, si ya fiché, cancela el recordatorio"
        )
        await send_message(chat_id, help_text)

        db.add(Message(
            user_id=user.id,
            direction="outbound",
            message_text=help_text,
            message_type="help",
        ))
        db.commit()

        return {"status": "ok", "action": "help_sent"}

    except Exception as exc:
        db.rollback()
        return JSONResponse(
            status_code=500,
            content={"status": "error", "reason": str(exc)}
        )
    finally:
        db.close()
