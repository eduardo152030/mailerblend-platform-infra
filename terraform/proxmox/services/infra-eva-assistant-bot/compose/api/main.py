import os
import re
import traceback
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy import select, text

from db import engine, SessionLocal
from models import User, Reminder, Message, Event
from parser_service import parse_reminder
from telegram_service import send_message
from scheduler import build_daily_digest, send_daily_digest_to_all
from schemas import ParseCommandRequest, CancelReminderRequest, EventCreateRequest

APP_NAME = os.getenv("APP_NAME", "eva-assistant-bot")
DEFAULT_TIMEZONE = os.getenv("TIMEZONE", "Europe/Madrid")
TZ = ZoneInfo(DEFAULT_TIMEZONE)

app = FastAPI(title=APP_NAME)


def to_local(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=TZ)
    return dt.astimezone(TZ)


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
        "is_persistent": getattr(r, "is_persistent", False),
        "repeat_every_minutes": getattr(r, "repeat_every_minutes", None),
        "stop_at": r.stop_at.isoformat() if getattr(r, "stop_at", None) else None,
        "awaiting_ack": getattr(r, "awaiting_ack", False),
        "retry_count": getattr(r, "retry_count", 0),
        "max_retries": getattr(r, "max_retries", 0),
        "created_at": r.created_at.isoformat() if r.created_at else None,
        "sent_at": r.sent_at.isoformat() if r.sent_at else None,
        "last_sent_at": r.last_sent_at.isoformat() if r.last_sent_at else None,
        "acked_at": r.acked_at.isoformat() if r.acked_at else None,
        "completed_at": r.completed_at.isoformat() if getattr(r, "completed_at", None) else None,
        "expired_at": r.expired_at.isoformat() if getattr(r, "expired_at", None) else None,
        "cancelled_at": r.cancelled_at.isoformat() if getattr(r, "cancelled_at", None) else None,
        "ack_text": getattr(r, "ack_text", None),
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


def normalize_text(text_in: str) -> str:
    txt = text_in.lower().strip()
    txt = re.sub(r"\s+", " ", txt)
    return txt


def is_list_command(lowered: str) -> bool:
    candidates = {
        "/reminders",
        "eva, /reminders",
        "eva reminders",
        "eva, reminders",
        "eva, lista mis recordatorios",
        "eva lista mis recordatorios",
        "lista mis recordatorios",
        "mis recordatorios",
        "recordatorios",
        "lista recordatorios",
        "eva, lista recordatorios",
        "eva lista recordatorios",
        "qué tengo pendiente",
        "que tengo pendiente",
        "eva, qué tengo pendiente",
        "eva, que tengo pendiente",
        "eva qué tengo pendiente",
        "eva que tengo pendiente",
    }
    return lowered in candidates


def extract_pending_task(lowered: str) -> str | None:
    """
    Detecta tareas sin fecha — intención de hacer algo sin especificar cuándo.
    Devuelve el texto de la tarea o None si no aplica.

    Ejemplos:
      "tengo que revisar el router"
      "hay que actualizar el certificado"
      "pendiente: revisar route53"
      "quiero hacer X"
      "no olvidar llamar al médico"
      "eva, apunta: revisar backups"
      "tarea: migrar la BD"
    """
    # Primero descartar si tiene hora — eso es un recordatorio normal
    if re.search(r'\ba las\s+\d{1,2}[:\s]', lowered):
        return None
    if re.search(r'\ben\s+\d+\s+minutos?\b', lowered):
        return None
    if re.search(r'\bmañana\b', lowered):
        return None

    patterns = [
        r'^(?:eva[,\s]+)?tengo que\s+(.+)$',
        r'^(?:eva[,\s]+)?hay que\s+(.+)$',
        r'^(?:eva[,\s]+)?tengo pendiente[:\s]+(.+)$',
        r'^(?:eva[,\s]+)?pendiente[:\s]+(.+)$',
        r'^(?:eva[,\s]+)?quiero hacer\s+(.+)$',
        r'^(?:eva[,\s]+)?no olvidar[:\s]+(.+)$',
        r'^(?:eva[,\s]+)?no olvidarme de\s+(.+)$',
        r'^(?:eva[,\s]+)?apunta[:\s]+(.+)$',
        r'^(?:eva[,\s]+)?apúntame[:\s]+(.+)$',
        r'^(?:eva[,\s]+)?tarea[:\s]+(.+)$',
        r'^(?:eva[,\s]+)?necesito\s+(.+)$',
        r'^(?:eva[,\s]+)?recuerda que tengo que\s+(.+)$',
        r'^(?:eva[,\s]+)?debo\s+(.+)$',
    ]

    for pattern in patterns:
        m = re.match(pattern, lowered, re.IGNORECASE)
        if m:
            task = m.group(1).strip()
            # Descartar si es muy corto o parece un comando
            if len(task) >= 4:
                return task
    return None


def is_ack_text(lowered: str) -> bool:
    ack_values = {
        "ok", "okay", "vale", "listo", "gracias", "hecho",
        "ya está", "ya esta", "si", "sí", "ya", "perfecto",
    }
    if lowered in ack_values:
        return True
    # También captura frases de snooze para que pasen por handle_ack_command
    if _parse_snooze(lowered) is not None:
        return True
    return False


def _parse_snooze(lowered: str) -> timedelta | None:
    """
    Detecta intención de posponer. Devuelve timedelta o None.
    Ejemplos: "en 10 minutos", "en 1 hora", "mañana", "luego", "después"
    """
    m = re.match(r'^(?:en\s+)?(\d+)\s+minutos?$', lowered)
    if m:
        return timedelta(minutes=int(m.group(1)))

    m = re.match(r'^(?:en\s+)?(\d+)\s+hora?s?$', lowered)
    if m:
        return timedelta(hours=int(m.group(1)))

    m = re.match(r'^(?:en\s+)?media\s+hora$', lowered)
    if m:
        return timedelta(minutes=30)

    m = re.match(r'^en\s+un\s+rato$', lowered)
    if m:
        return timedelta(minutes=15)

    if lowered in ("mañana", "manana"):
        return timedelta(hours=24)

    if lowered in ("luego", "después", "despues", "ahora no", "más tarde", "mas tarde"):
        return timedelta(hours=1)

    return None


def extract_cancel_task(lowered: str) -> str | None:
    patterns = [
        r"^eva,\s*cancela el recordatorio$",
        r"^eva\s+cancela el recordatorio$",
        r"^cancela el recordatorio$",
        r"^eva,\s*cancela el de\s+(.+)$",
        r"^eva\s+cancela el de\s+(.+)$",
        r"^cancela el de\s+(.+)$",
        r"^eva,\s*cancela\s+(.+)$",
        r"^eva\s+cancela\s+(.+)$",
        r"^cancela\s+(.+)$",
    ]

    for pattern in patterns:
        m = re.match(pattern, lowered, re.IGNORECASE)
        if m:
            if m.lastindex:
                captured = m.group(1).strip()
                # Si lo capturado es solo un número o "el N" → es cancelación por ID,
                # dejar que handle_cancel_by_id lo gestione
                if re.match(r'^(?:el\s+)?\d+$', captured):
                    return None
                return captured
            return ""
    return None


def extract_edit_command(lowered: str) -> tuple[int, dict] | None:
    """
    Detecta comandos de edición por ID. Devuelve (reminder_id, updates) o None.
    Ejemplos:
      "cambia el 28 a las 11:00"
      "eva, mueve el 5 a mañana a las 9:30"
      "edita el 12, nueva tarea: llamar al médico"
      "renombra el 7 a revisar correos"
    """
    edit_keywords = ("cambia", "cambiar", "mueve", "mover", "edita", "editar", "actualiza", "actualizar", "renombra", "renombrar", "modifica", "modificar")
    if not any(w in lowered for w in edit_keywords):
        return None

    id_match = re.search(r'\b(\d{1,6})\b', lowered)
    if not id_match:
        return None

    reminder_id = int(id_match.group(1))
    updates: dict = {}

    time_match = re.search(r'a\s+las?\s+(\d{1,2}):(\d{2})', lowered)
    if time_match:
        updates["hour"] = int(time_match.group(1))
        updates["minute"] = int(time_match.group(2))

    if "mañana" in lowered or "manana" in lowered:
        updates["tomorrow"] = True

    task_match = re.search(r'(?:nueva\s+tarea|tarea|texto|nombre)\s*[:]\s*(.+)', lowered)
    if task_match:
        updates["task_text"] = task_match.group(1).strip()

    rename_match = re.match(r'.*(?:renombra|renombrar)\s+el\s+\d+\s+a\s+(.+)', lowered)
    if rename_match:
        updates["task_text"] = rename_match.group(1).strip()

    if not updates:
        return None

    return reminder_id, updates


def build_list_reply(active: list[Reminder], awaiting: list[Reminder]) -> str:
    if not active and not awaiting:
        return "📋 No tienes recordatorios activos."

    lines = []

    if active:
        lines.append(f"📋 *Próximos recordatorios ({len(active)}):*")
        for r in active:
            local_dt = to_local(r.remind_at)
            dt_str = local_dt.strftime("%d/%m %H:%M") if local_dt else "sin hora"
            recurrence = ""
            if r.recurrence_type == "weekly":
                recurrence = " ↻ semanal"
            elif r.recurrence_type == "weekdays":
                recurrence = " ↻ lab."
            elif r.is_persistent and r.repeat_every_minutes:
                recurrence = f" ↻ cada {r.repeat_every_minutes}min"
            lines.append(f"  • [{r.id}] {r.task_text} — {dt_str}{recurrence}")

    if awaiting:
        if active:
            lines.append("")
        lines.append(f"⏳ *Pendientes de confirmación ({len(awaiting)}):*")
        for r in awaiting:
            local_dt = to_local(r.last_sent_at or r.remind_at)
            dt_str = local_dt.strftime("%d/%m %H:%M") if local_dt else "sin hora"
            lines.append(f"  • [{r.id}] {r.task_text} — enviado {dt_str}")
        lines.append("  Responde *listo* para confirmar el más reciente.")

    return "\n".join(lines)


def build_help_text() -> str:
    return (
        "No te entendí del todo. Prueba con:\n"
        "- eva, recuérdame en 2 minutos probar sistema\n"
        "- eva, cada 5 minutos recuérdame tomar agua\n"
        "- eva, recuérdame cada 10 minutos revisar el horno hasta las 22:00\n"
        "- eva, recuérdame 2 minutos antes de las 22:00\n"
        "- eva, recuérdame 2 minutos antes de que sean las 22:00\n"
        "- mañana recuérdame fichar a las 08:00\n"
        "- cada lunes recuérdame revisión semanal a las 09:00\n"
        "- eva, recuérdame fichar a las 08:00, solo días laborables\n"
        "- eva, recuérdame fichar a las 08:00, si ya fiché, cancela el recordatorio\n"
        "- eva, recuérdame fichar a las 22:40 y sigue avisándome hasta las 22:50\n"
        "- eva, lista mis recordatorios\n"
        "- eva, cancela el 28\n"
        "- eva, cambia el 28 a las 11:00\n"
        "- listo / ok / ya está / en 10 minutos / luego"
    )


def build_confirmation_text_from_parsed(source_text: str, parsed: dict, reminder_id: int | None = None) -> str:
    remind_at_local = to_local(parsed["remind_at"])
    # Formato más humano: "mañana a las 10:00" en lugar de "2026-04-10 10:00"
    now_local = datetime.now(TZ)
    if remind_at_local.date() == now_local.date():
        date_str = f"hoy a las {remind_at_local.strftime('%H:%M')}"
    elif remind_at_local.date() == (now_local + timedelta(days=1)).date():
        date_str = f"mañana a las {remind_at_local.strftime('%H:%M')}"
    else:
        DIAS = ["lunes","martes","miércoles","jueves","viernes","sábado","domingo"]
        date_str = f"el {DIAS[remind_at_local.weekday()]} {remind_at_local.strftime('%d/%m')} a las {remind_at_local.strftime('%H:%M')}"

    remind_time_str = remind_at_local.strftime("%H:%M")
    task_text = parsed["task_text"]
    id_hint = f" [{reminder_id}]" if reminder_id else ""

    if parsed.get("mode") == "before_time":
        minutes_before = parsed.get("minutes_before")
        target_time_text = parsed.get("target_time_text")
        if minutes_before is not None and target_time_text:
            base = f"✅ Anotado{id_hint}: te aviso a las {remind_time_str} ({minutes_before} min antes de las {target_time_text})."
        else:
            base = f'✅ "{task_text}" — {date_str}.{id_hint}'
    elif parsed.get("mode") == "interval_minutes":
        interval = parsed.get("repeat_every_minutes", 0)
        stop_at = parsed.get("stop_at")
        if stop_at:
            stop_at_local = to_local(stop_at)
            return (
                f'✅ Anotado{id_hint}: "{task_text}" cada {interval} min '
                f'hasta las {stop_at_local.strftime("%H:%M")}.\n'
                f'Responde "listo" para parar.'
            )
        return (
            f'✅ Anotado{id_hint}: "{task_text}" cada {interval} min '
            f'hasta que respondas "listo".'
        )
    elif parsed.get("mode") == "tomorrow_at_time":
        base = f'✅ Anotado{id_hint}: "{task_text}" — mañana a las {remind_time_str}.'
    elif parsed.get("mode") == "next_weekday":
        DIAS = ["lunes","martes","miércoles","jueves","viernes","sábado","domingo"]
        dia = DIAS[remind_at_local.weekday()]
        base = f'✅ Anotado{id_hint}: "{task_text}" — el próximo {dia} a las {remind_time_str}.'
    elif parsed.get("mode") == "absolute_date":
        base = f'✅ Anotado{id_hint}: "{task_text}" — el {remind_at_local.strftime("%d/%m/%Y")} a las {remind_time_str}.'
    elif parsed.get("mode") == "weekly_day":
        recurrence_value = parsed.get("recurrence_value") or "ese día"
        base = f'✅ Anotado{id_hint}: "{task_text}" — cada {recurrence_value} a las {remind_time_str}.'
    elif parsed.get("mode") == "weekdays":
        base = f'✅ Anotado{id_hint}: "{task_text}" — días laborables a las {remind_time_str}.'
    else:
        base = f'✅ "{task_text}" — {date_str}.{id_hint}'

    correction_hint = f'\n_Si la hora es incorrecta responde "no, a las HH:MM"_'

    if parsed.get("is_persistent"):
        repeat_every_minutes = parsed.get("repeat_every_minutes") or 2
        stop_at = parsed.get("stop_at")
        if stop_at:
            stop_at_local = to_local(stop_at)
            return (
                f"{base}\n"
                f"🔁 Repetiré cada {repeat_every_minutes} min "
                f"hasta las {stop_at_local.strftime('%H:%M')} o hasta \"listo\"."
            )
        return (
            f"{base}\n"
            f"🔁 Repetiré cada {repeat_every_minutes} min hasta \"listo\"."
        )

    return f"{base}{correction_hint}"



def _get_recent_context(db, user_id: int, limit: int = 5) -> list[dict]:
    """Devuelve los últimos N mensajes del usuario para contexto conversacional."""
    rows = db.execute(
        select(Message)
        .where(Message.user_id == user_id)
        .order_by(Message.id.desc())
        .limit(limit)
    ).scalars().all()
    return [
        {"direction": m.direction, "text": m.message_text}
        for m in reversed(rows)
    ]


async def send_and_log(db, user_id: int, chat_id: int, text_out: str, message_type: str) -> None:
    await send_message(chat_id, text_out)
    db.add(
        Message(
            user_id=user_id,
            direction="outbound",
            message_text=text_out,
            message_type=message_type,
        )
    )
    db.commit()


async def handle_list_command(db, user: User, chat_id: int):
    # Próximos: scheduled/pending — aún no disparados
    active = db.execute(
        select(Reminder)
        .where(Reminder.user_id == user.id)
        .where(Reminder.status.in_(["pending", "scheduled"]))
        .order_by(Reminder.remind_at.asc())
    ).scalars().all()

    # Pendientes de confirmación: sent + awaiting_ack
    awaiting = db.execute(
        select(Reminder)
        .where(Reminder.user_id == user.id)
        .where(Reminder.status == "sent")
        .where(Reminder.awaiting_ack.is_(True))
        .order_by(Reminder.last_sent_at.desc().nullslast())
    ).scalars().all()

    reply = build_list_reply(active, awaiting)
    await send_and_log(db, user.id, chat_id, reply, "reminders_list")
    return {"status": "ok", "action": "reminders_list_sent"}


async def handle_ack_command(db, user: User, chat_id: int, lowered: str):
    reminder = db.execute(
        select(Reminder)
        .where(Reminder.user_id == user.id)
        .where(
            (Reminder.awaiting_ack.is_(True)) |
            (Reminder.status == "sent")
        )
        .order_by(Reminder.last_sent_at.desc().nullslast(), Reminder.id.desc())
        .limit(1)
    ).scalars().first()

    if not reminder:
        reply = "👌 No tengo ningún recordatorio pendiente de confirmación ahora mismo."
        await send_and_log(db, user.id, chat_id, reply, "ack_no_pending")
        return {"status": "ok", "action": "ack_no_pending"}

    # =========================
    # SNOOZE (antes del ACK)
    # =========================
    snooze_delta = _parse_snooze(lowered)
    if snooze_delta is not None:
        now = datetime.now(TZ)
        new_remind_at = now + snooze_delta
        reminder.remind_at = new_remind_at
        reminder.status = "scheduled"
        reminder.awaiting_ack = False

        db.add(Event(
            user_id=user.id,
            event_type="reminder_snoozed",
            event_value=str(reminder.id),
            source="telegram",
            payload={"snooze_text": lowered, "new_remind_at": new_remind_at.isoformat()},
        ))
        db.commit()

        dt_str = to_local(new_remind_at).strftime("%H:%M")
        reply = f'⏱️ Vale, te recuerdo "{reminder.task_text}" a las {dt_str}.'
        await send_and_log(db, user.id, chat_id, reply, "snooze_confirmation")
        return {"status": "ok", "action": "reminder_snoozed", "reminder_id": reminder.id}

    now = datetime.now(TZ)
    reminder.acked_at = now
    reminder.completed_at = now
    reminder.awaiting_ack = False
    reminder.ack_text = lowered
    reminder.status = "completed"

    db.add(
        Event(
            user_id=user.id,
            event_type="reminder_completed",
            event_value=str(reminder.id),
            source="telegram",
            payload={"text": lowered},
        )
    )
    db.commit()

    reply = f'✅ Entendido. Marco como completado: "{reminder.task_text}".'
    await send_and_log(db, user.id, chat_id, reply, "ack_confirmation")
    return {"status": "ok", "action": "reminder_acknowledged", "reminder_id": reminder.id}


async def handle_cancel_command(db, user: User, chat_id: int, cancel_task: str):
    stmt = (
        select(Reminder)
        .where(Reminder.user_id == user.id)
        .where(Reminder.status.in_(["pending", "scheduled", "sent"]))
    )

    rows = db.execute(stmt.order_by(Reminder.remind_at.asc(), Reminder.id.desc())).scalars().all()

    if not rows:
        reply = "📋 No tienes recordatorios activos para cancelar."
        await send_and_log(db, user.id, chat_id, reply, "cancel_none")
        return {"status": "ok", "action": "cancel_no_active"}

    target = None

    if cancel_task == "":
        target = rows[0]
    else:
        cancel_task_norm = cancel_task.strip().lower()
        for row in rows:
            if cancel_task_norm in (row.task_text or "").lower():
                target = row
                break

    if not target:
        reply = "No encontré un recordatorio activo que coincida con ese texto."
        await send_and_log(db, user.id, chat_id, reply, "cancel_not_found")
        return {"status": "ok", "action": "cancel_not_found"}

    now = datetime.now(TZ)
    target.status = "cancelled"
    target.awaiting_ack = False
    target.cancelled_at = now
    target.error_message = "cancelled_by_user"

    db.add(
        Event(
            user_id=user.id,
            event_type="reminder_cancelled",
            event_value=str(target.id),
            source="telegram",
            payload={"task_match": cancel_task},
        )
    )
    db.commit()

    reply = f'🛑 He cancelado el recordatorio: "{target.task_text}".'
    await send_and_log(db, user.id, chat_id, reply, "cancel_confirmation")
    return {"status": "ok", "action": "reminder_cancelled", "reminder_id": target.id}


async def handle_cancel_by_id(db, user: User, chat_id: int, reminder_id: int):
    reminder = db.execute(
        select(Reminder).where(Reminder.id == reminder_id)
    ).scalar_one_or_none()

    if not reminder:
        reply = f"❌ No encontré ningún recordatorio con id {reminder_id}."
        await send_and_log(db, user.id, chat_id, reply, "cancel_by_id_not_found")
        return {"status": "ok", "action": "cancel_by_id_not_found"}

    if reminder.status in ("cancelled", "completed"):
        reply = f"ℹ️ El recordatorio [{reminder_id}] ya estaba {reminder.status}."
        await send_and_log(db, user.id, chat_id, reply, "cancel_by_id_already_done")
        return {"status": "ok", "action": "cancel_by_id_already_done"}

    now = datetime.now(TZ)
    reminder.status = "cancelled"
    reminder.awaiting_ack = False
    reminder.cancelled_at = now
    reminder.error_message = "cancelled_by_user_command"

    db.add(Event(
        user_id=user.id,
        event_type="reminder_cancelled",
        event_value=str(reminder.id),
        source="telegram",
        payload={"cancel_method": "by_id", "reminder_id": reminder_id},
    ))
    db.commit()

    reply = f'🛑 He cancelado [{reminder_id}]: "{reminder.task_text}".'
    await send_and_log(db, user.id, chat_id, reply, "cancel_by_id_confirmation")
    return {"status": "ok", "action": "reminder_cancelled", "reminder_id": reminder_id}


async def handle_pending_task(db, user: User, chat_id: int, task_text: str):
    """
    Crea una tarea sin fecha directamente en Focalboard (columna Pendiente).
    No crea un Reminder — es una tarjeta libre para gestionar desde la UI.
    """
    import time
    import uuid
    import httpx

    FOCALBOARD_URL   = os.getenv("FOCALBOARD_URL", "")
    FOCALBOARD_TOKEN = os.getenv("FOCALBOARD_TOKEN", "")
    FOCALBOARD_BOARD_ID = os.getenv("FOCALBOARD_BOARD_ID", "")

    if not FOCALBOARD_TOKEN or not FOCALBOARD_BOARD_ID:
        reply = f'📌 Apuntado: "{task_text}"\n⚠️ Focalboard no configurado — guárdalo manualmente.'
        await send_and_log(db, user.id, chat_id, reply, "pending_task_no_fb")
        return {"status": "ok", "action": "pending_task_no_focalboard"}

    now_ms  = int(time.time() * 1000)
    card_id = uuid.uuid4().hex[:26]

    block = {
        "id": card_id,
        "type": "card",
        "schema": 1,
        "boardId": FOCALBOARD_BOARD_ID,
        "parentId": FOCALBOARD_BOARD_ID,
        "title": task_text,
        "createAt": now_ms,
        "updateAt": now_ms,
        "deleteAt": 0,
        "fields": {
            "isTemplate": False,
            "contentOrder": [],
            "properties": {
                "aevastatus00000000000000001": "aoptpendiente00000000000001",
            },
        },
    }

    headers = {
        "Authorization": f"Bearer {FOCALBOARD_TOKEN}",
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest",
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.post(
                f"{FOCALBOARD_URL}/api/v2/boards/{FOCALBOARD_BOARD_ID}/blocks",
                headers=headers,
                json=[block],
            )
            if r.status_code in (200, 201):
                data = r.json()
                fb_id = data[0]["id"] if isinstance(data, list) else data.get("id", card_id)
                db.add(Event(
                    user_id=user.id,
                    event_type="pending_task_created",
                    event_value=fb_id,
                    source="telegram",
                    payload={"task_text": task_text, "card_id": fb_id},
                ))
                db.commit()
                reply = (
                    f'📌 Apuntado en Focalboard: "{task_text}"\n'
                    f'Cuando tengas un momento, asígnale fecha desde la UI.'
                )
                await send_and_log(db, user.id, chat_id, reply, "pending_task_created")
                return {"status": "ok", "action": "pending_task_created", "card_id": fb_id}
            else:
                raise Exception(f"Focalboard {r.status_code}: {r.text[:200]}")
    except Exception as exc:
        print(f"[pending_task] error: {exc}")
        reply = f'📌 Apuntado: "{task_text}"\n⚠️ No pude crear la tarjeta en Focalboard ahora mismo.'
        await send_and_log(db, user.id, chat_id, reply, "pending_task_fb_error")
        return {"status": "ok", "action": "pending_task_fb_error"}


async def handle_edit_reminder(db, user: User, chat_id: int, reminder_id: int, updates: dict):
    reminder = db.execute(
        select(Reminder).where(Reminder.id == reminder_id)
    ).scalar_one_or_none()

    if not reminder:
        reply = f"❌ No encontré ningún recordatorio con id {reminder_id}."
        await send_and_log(db, user.id, chat_id, reply, "edit_not_found")
        return {"status": "ok", "action": "edit_not_found"}

    if reminder.status in ("cancelled", "completed"):
        reply = f"ℹ️ El recordatorio {reminder_id} ya está {reminder.status}, no se puede editar."
        await send_and_log(db, user.id, chat_id, reply, "edit_invalid_status")
        return {"status": "ok", "action": "edit_invalid_status"}

    now = datetime.now(TZ)
    base_dt = to_local(reminder.remind_at) or now

    if updates.get("tomorrow"):
        base_dt = base_dt + timedelta(days=1)

    if "hour" in updates:
        base_dt = base_dt.replace(hour=updates["hour"], minute=updates.get("minute", 0), second=0, microsecond=0)
        if base_dt <= now and not updates.get("tomorrow"):
            base_dt = base_dt + timedelta(days=1)
        reminder.remind_at = base_dt
        reminder.status = "scheduled"

    if "task_text" in updates:
        reminder.task_text = updates["task_text"]

    db.add(Event(
        user_id=user.id,
        event_type="reminder_edited",
        event_value=str(reminder.id),
        source="telegram",
        payload={"updates": {k: str(v) for k, v in updates.items()}},
    ))
    db.commit()

    local_dt = to_local(reminder.remind_at)
    dt_str = local_dt.strftime("%Y-%m-%d %H:%M") if local_dt else "—"
    reply = f'✏️ Recordatorio [{reminder_id}] actualizado: "{reminder.task_text}" → {dt_str}.'
    await send_and_log(db, user.id, chat_id, reply, "edit_confirmation")
    return {"status": "ok", "action": "reminder_edited", "reminder_id": reminder_id}


def _extract_telegram_message(payload: dict) -> dict | None:
    return (
        payload.get("message")
        or payload.get("edited_message")
        or payload.get("channel_post")
        or payload.get("edited_channel_post")
    )


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

    response = dict(parsed)
    response["remind_at"] = parsed["remind_at"].isoformat()
    if parsed.get("stop_at"):
        response["stop_at"] = parsed["stop_at"].isoformat()

    return {"status": "ok", "parsed": response}


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
            .where(Reminder.status.in_(["pending", "scheduled", "sent"]))
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

        now = datetime.now(TZ)
        reminder.status = "cancelled"
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
    message = _extract_telegram_message(payload)

    if not message:
        return {"status": "ignored", "reason": "unsupported_update_type"}

    text_in = message.get("text")
    if not text_in:
        return {"status": "ignored", "reason": "no_text_message"}

    chat = message.get("chat") or {}
    from_user = message.get("from") or {}

    chat_id = chat.get("id")
    if chat_id is None:
        return {"status": "ignored", "reason": "missing_chat_id"}

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
                timezone=DEFAULT_TIMEZONE,
            )
            db.add(user)
            db.flush()
        else:
            user.telegram_username = telegram_username
            user.display_name = display_name

        db.add(
            Message(
                user_id=user.id,
                direction="inbound",
                message_text=text_in,
                message_type="chat",
            )
        )
        db.commit()

        lowered = normalize_text(text_in)

        if is_list_command(lowered):
            return await handle_list_command(db, user, chat_id)

        # Cancelación por ID — va ANTES que extract_cancel_task para que
        # "cancela el 28" no se interprete como búsqueda de texto "el 28"
        _cancel_keywords = ("cancela", "cancelar", "elimina", "eliminar", "borra", "borrar")
        _id_match = re.search(r'\b(\d{1,6})\b', lowered)
        if any(w in lowered for w in _cancel_keywords) and _id_match:
            return await handle_cancel_by_id(db, user, chat_id, int(_id_match.group(1)))

        cancel_task = extract_cancel_task(lowered)
        if cancel_task is not None:
            return await handle_cancel_command(db, user, chat_id, cancel_task)

        edit_result = extract_edit_command(lowered)
        if edit_result is not None:
            reminder_id, updates = edit_result
            return await handle_edit_reminder(db, user, chat_id, reminder_id, updates)

        if is_ack_text(lowered):
            return await handle_ack_command(db, user, chat_id, lowered)

        # C) Corrección rápida: "no, a las 11" / "no, era a las 11:00"
        # Corrige la hora del último recordatorio creado
        _correction = re.match(
            r'^no[,.]?\s+(?:era\s+)?a las?\s+(\d{1,2})(?::(\d{2}))?$',
            lowered, re.IGNORECASE
        )
        if _correction:
            new_hour   = int(_correction.group(1))
            new_minute = int(_correction.group(2)) if _correction.group(2) else 0
            # Buscar el último reminder creado por este usuario
            last_r = db.execute(
                select(Reminder)
                .where(Reminder.user_id == user.id)
                .where(Reminder.status.in_(["scheduled", "pending"]))
                .order_by(Reminder.id.desc())
                .limit(1)
            ).scalars().first()
            if last_r:
                now_tz = datetime.now(TZ)
                new_dt = to_local(last_r.remind_at).replace(
                    hour=new_hour, minute=new_minute, second=0, microsecond=0
                )
                if new_dt <= now_tz:
                    new_dt = new_dt + timedelta(days=1)
                last_r.remind_at = new_dt
                last_r.status = "scheduled"
                db.add(Event(
                    user_id=user.id,
                    event_type="reminder_corrected",
                    event_value=str(last_r.id),
                    source="telegram",
                    payload={"new_time": f"{new_hour:02d}:{new_minute:02d}"},
                ))
                db.commit()
                reply = (
                    f'✅ Corregido `[{last_r.id}]`: "{last_r.task_text}" — '
                    f'ahora a las {new_dt.strftime("%H:%M")}.'
                )
                await send_and_log(db, user.id, chat_id, reply, "reminder_corrected")
                return {"status": "ok", "action": "reminder_corrected", "reminder_id": last_r.id}

        # Tarea sin fecha — va antes del parser de recordatorios
        pending_task = extract_pending_task(lowered)
        if pending_task is not None:
            return await handle_pending_task(db, user, chat_id, pending_task)

        parsed = parse_reminder(text_in, context=_get_recent_context(db, user.id))
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
                is_persistent=parsed.get("is_persistent", False),
                repeat_every_minutes=parsed.get("repeat_every_minutes"),
                stop_at=parsed.get("stop_at"),
                awaiting_ack=parsed.get("awaiting_ack", False),
            )
            db.add(reminder)
            db.commit()
            db.refresh(reminder)

            db.add(
                Event(
                    user_id=user.id,
                    event_type="reminder_created",
                    event_value=str(reminder.id),
                    source="telegram",
                    payload={
                        "source_text": text_in,
                        "task_text": reminder.task_text,
                        "mode": parsed.get("mode"),
                        "is_persistent": parsed.get("is_persistent", False),
                    },
                )
            )
            db.commit()

            reply_text = build_confirmation_text_from_parsed(text_in, parsed, reminder.id)
            await send_message(chat_id, reply_text)

            db.add(
                Message(
                    user_id=user.id,
                    direction="outbound",
                    message_text=reply_text,
                    message_type="reminder_confirmation",
                )
            )
            db.commit()

            return {"status": "ok", "action": "reminder_created", "reminder_id": reminder.id}

        help_text = build_help_text()
        await send_message(chat_id, help_text)

        db.add(
            Message(
                user_id=user.id,
                direction="outbound",
                message_text=help_text,
                message_type="help",
            )
        )
        db.commit()

        return {"status": "ok", "action": "help_sent"}

    except Exception as exc:
        db.rollback()
        print("=== TELEGRAM WEBHOOK ERROR ===")
        try:
            print("PAYLOAD:", payload)
        except Exception:
            print("PAYLOAD: <unavailable>")
        print("ERROR:", repr(exc))
        traceback.print_exc()

        return JSONResponse(
            status_code=500,
            content={"status": "error", "reason": str(exc)}
        )
    finally:
        db.close()

# =========================
# RESUMEN DIARIO — ENDPOINTS
# =========================

@app.post("/digest/send")
async def trigger_daily_digest(user_id: int | None = None):
    """
    Dispara el resumen diario manualmente.
    - Sin parámetros: envía a todos los usuarios.
    - Con user_id: envía solo a ese usuario.
    Útil para: cron externo, pruebas, o botón en panel de admin.

    Cron diario a las 08:00 (ejemplo con curl):
        0 8 * * * curl -s -X POST http://localhost:8000/digest/send
    """
    db = SessionLocal()
    try:
        async def _send(chat_id: int, text_out: str, parse_mode: str = "MarkdownV2"):
            await send_message(chat_id, text_out, parse_mode=parse_mode)

        if user_id is not None:
            user = db.execute(
                select(User).where(User.id == user_id)
            ).scalar_one_or_none()
            if not user:
                return JSONResponse(status_code=404, content={"status": "error", "reason": "user_not_found"})
            digest = build_daily_digest(db, user)
            if not digest:
                return {"status": "ok", "sent": 0, "reason": "nothing_to_send"}
            await _send(user.telegram_chat_id, digest)
            db.add(Message(
                user_id=user.id,
                direction="outbound",
                message_text=digest,
                message_type="daily_digest",
            ))
            db.add(Event(
                user_id=user.id,
                event_type="daily_digest_sent",
                event_value=str(datetime.now(TZ).date()),
                source="api",
                payload={"triggered_by": "manual"},
            ))
            db.commit()
            return {"status": "ok", "sent": 1}

        sent = await send_daily_digest_to_all(db, _send)
        return {"status": "ok", "sent": sent}

    finally:
        db.close()


@app.get("/digest/preview/{user_id}")
async def preview_daily_digest(user_id: int):
    """
    Devuelve el texto del resumen sin enviarlo. Útil para depurar.
    GET /digest/preview/1
    """
    db = SessionLocal()
    try:
        user = db.execute(
            select(User).where(User.id == user_id)
        ).scalar_one_or_none()
        if not user:
            return JSONResponse(status_code=404, content={"status": "error", "reason": "user_not_found"})
        digest = build_daily_digest(db, user)
        return {"status": "ok", "digest": digest or "", "has_content": digest is not None}
    finally:
        db.close()