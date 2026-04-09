import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from sqlalchemy import select
from models import Reminder, Event, User

TZ = ZoneInfo(os.getenv("TIMEZONE", "Europe/Madrid"))
DAILY_DIGEST_HOUR = int(os.getenv("DAILY_DIGEST_HOUR", "8"))
DAILY_DIGEST_MINUTE = int(os.getenv("DAILY_DIGEST_MINUTE", "0"))


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
    if getattr(reminder, "awaiting_ack", False):
        return f'⏰ EVA: Sigo pendiente de "{reminder.task_text}". Respóndeme "listo" cuando lo hayas hecho.'
    return f'⏰ EVA: Es hora de {reminder.task_text}. Respóndeme "listo" cuando lo hayas hecho.'


def build_expired_text(reminder: Reminder) -> str:
    return f'⌛ EVA: Dejé de insistir con "{reminder.task_text}" porque se alcanzó la hora límite.'

# =========================
# RESUMEN DIARIO
# =========================

def is_digest_time(now: datetime | None = None) -> bool:
    """Devuelve True si es la hora configurada para enviar el resumen diario."""
    now = now or datetime.now(TZ)
    return now.hour == DAILY_DIGEST_HOUR and now.minute == DAILY_DIGEST_MINUTE


def _escape_md(text: str) -> str:
    """Escapa caracteres especiales para Telegram MarkdownV2."""
    special = r"\_*[]()~`>#+-=|{}.!"
    return "".join(f"\\{c}" if c in special else c for c in text)


def build_daily_digest(db, user, now: datetime | None = None) -> str | None:
    """
    Construye el resumen diario para un usuario.
    Devuelve None si no hay nada que mostrar.
    """
    now = now or datetime.now(TZ)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)

    todays = db.execute(
        select(Reminder)
        .where(Reminder.user_id == user.id)
        .where(Reminder.status.in_(["scheduled", "pending", "sent"]))
        .where(Reminder.remind_at >= today_start)
        .where(Reminder.remind_at < today_end)
        .order_by(Reminder.remind_at.asc())
    ).scalars().all()

    overdue = db.execute(
        select(Reminder)
        .where(Reminder.user_id == user.id)
        .where(Reminder.status.in_(["scheduled", "pending", "sent"]))
        .where(Reminder.remind_at < today_start)
        .order_by(Reminder.remind_at.asc())
    ).scalars().all()

    if not todays and not overdue:
        return None

    name = (user.display_name or "").split()[0] if user.display_name else ""
    greeting = f"\u2600\ufe0f Buenos d\u00edas{', ' + name if name else ''}\\.\n\n"
    lines = [greeting]

    if todays:
        lines.append(f"*\U0001f4cb Hoy tienes {len(todays)} recordatorio{'s' if len(todays) != 1 else ''}:*\n")
        for r in todays:
            local_dt = to_local(r.remind_at)
            time_str = local_dt.strftime("%H:%M")
            recurrence = ""
            if r.recurrence_type == "weekly":
                recurrence = " \\(semanal\\)"
            elif r.recurrence_type == "weekdays":
                recurrence = " \\(laborables\\)"
            lines.append(f"  \u2022 `[{r.id}]` {_escape_md(r.task_text)} \u2014 *{time_str}*{recurrence}\n")

    if overdue:
        lines.append(f"\n*\u26a0\ufe0f Pendientes anteriores \\({len(overdue)}\\):*\n")
        for r in overdue:
            local_dt = to_local(r.remind_at)
            date_str = local_dt.strftime("%d/%m %H:%M")
            lines.append(f"  \u2022 `[{r.id}]` {_escape_md(r.task_text)} \u2014 _{date_str}_\n")

    lines.append("\nResponde *listo* al completar cada uno, o *cancela el \\[id\\]* para eliminarlo\\.")
    return "".join(lines)


async def send_daily_digest_to_all(db, send_fn) -> int:
    """
    Envía el resumen diario a todos los usuarios activos.

    send_fn: async callable(chat_id: int, text: str, parse_mode: str)

    Uso en el scheduler loop:
        from scheduler import is_digest_time, send_daily_digest_to_all
        from telegram_service import send_message

        async def _send(chat_id, text, parse_mode="MarkdownV2"):
            await send_message(chat_id, text, parse_mode=parse_mode)

        if is_digest_time():
            await send_daily_digest_to_all(db, _send)
    """
    from models import Message

    now = datetime.now(TZ)
    users = db.execute(select(User)).scalars().all()
    sent = 0

    for user in users:
        if not user.telegram_chat_id:
            continue
        digest = build_daily_digest(db, user, now)
        if not digest:
            continue
        try:
            await send_fn(user.telegram_chat_id, digest, "MarkdownV2")
            db.add(Message(
                user_id=user.id,
                direction="outbound",
                message_text=digest,
                message_type="daily_digest",
            ))
            db.add(Event(
                user_id=user.id,
                event_type="daily_digest_sent",
                event_value=str(now.date()),
                source="scheduler",
                payload={"hour": now.hour, "minute": now.minute},
            ))
            sent += 1
        except Exception as exc:
            print(f"[digest] Error enviando a user {user.id}: {exc}")

    db.commit()
    return sent