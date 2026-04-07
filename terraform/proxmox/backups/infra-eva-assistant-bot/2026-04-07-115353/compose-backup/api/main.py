import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy import select, text
from db import engine, SessionLocal
from models import User, Reminder, Message
from parser_service import parse_reminder
from telegram_service import send_message

APP_NAME = os.getenv("APP_NAME", "eva-assistant-bot")

app = FastAPI(title=APP_NAME)


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

        parsed = parse_reminder(text_in)

        if parsed:
            reminder = Reminder(
                user_id=user.id,
                source_text=text_in,
                task_text=parsed["task_text"],
                remind_at=parsed["remind_at"],
                status="pending",
            )
            db.add(reminder)
            db.commit()

            remind_at_local = parsed["remind_at"].strftime("%Y-%m-%d %H:%M")
            reply_text = f'🧠 EVA: Te recordaré "{parsed["task_text"]}" el {remind_at_local}.'
            await send_message(chat_id, reply_text)

            db2 = SessionLocal()
            try:
                user2 = db2.execute(
                    select(User).where(User.telegram_chat_id == chat_id)
                ).scalar_one_or_none()
                if user2:
                    db2.add(Message(
                        user_id=user2.id,
                        direction="outbound",
                        message_text=reply_text,
                        message_type="reminder_confirmation",
                    ))
                    db2.commit()
            finally:
                db2.close()

            return {"status": "ok", "action": "reminder_created"}

        db.commit()

        help_text = (
            "No te entendí del todo. Prueba con:\n"
            "- eva, recuérdame en 2 minutos probar sistema\n"
            "- eva, recuérdame fichar a las 08:00"
        )
        await send_message(chat_id, help_text)

        db2 = SessionLocal()
        try:
            user2 = db2.execute(
                select(User).where(User.telegram_chat_id == chat_id)
            ).scalar_one_or_none()
            if user2:
                db2.add(Message(
                    user_id=user2.id,
                    direction="outbound",
                    message_text=help_text,
                    message_type="help",
                ))
                db2.commit()
        finally:
            db2.close()

        return {"status": "ok", "action": "help_sent"}

    except Exception as exc:
        db.rollback()
        return JSONResponse(
            status_code=500,
            content={"status": "error", "reason": str(exc)}
        )
    finally:
        db.close()
