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
from ai_parser import (parse_reminder_ai, detect_intent, answer_question_ai,
                        build_reply_ai, chat_reply_ai, infer_priority)
from memory_service import get_user_facts, build_memory_context, process_message_for_memory
from persona_service import load_persona, build_system_prompt, get_phrase
from telegram_service import send_message
from scheduler import build_daily_digest, send_daily_digest_to_all
# Schemas inline (evita dependencia de schemas.py)
from pydantic import BaseModel as _BaseModel
class ParseCommandRequest(_BaseModel):
    text: str
class CancelReminderRequest(_BaseModel):
    reason: str | None = None
class EventCreateRequest(_BaseModel):
    user_id: int | None = None
    event_type: str
    event_value: str | None = None
    source: str = "api"
    payload: dict = {}

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
    # Solo captura snooze simples SIN hora concreta — los que tienen hora
    # los maneja el bloque SNOOZE CONTEXTUAL para evitar doble respuesta
    simple_snooze = {"luego", "después", "despues", "ahora no", "más tarde",
                     "mas tarde", "mañana", "manana", "en un rato", "media hora"}
    if lowered in simple_snooze:
        return True
    # "en X minutos" / "en X horas" simples
    if re.match(r'^en\s+\d+\s+(?:minutos?|horas?)$', lowered):
        return True
    return False


def _extract_snooze_note(text: str) -> tuple[str, str | None]:
    """
    Separa la expresión de tiempo del contexto adicional.
    "a las 13:00, tengo que confirmar con Luis" → ("a las 13:00", "tengo que confirmar con Luis")
    "en 10 minutos" → ("en 10 minutos", None)
    """
    # Buscar coma + contexto después de la expresión de tiempo
    m = re.search(r',\s*(.+)$', text)
    if m:
        context = m.group(1).strip()
        time_part = text[:m.start()].strip()
        # Solo extraer nota si el contexto es sustancial (> 3 palabras)
        if len(context.split()) >= 2:
            return time_part, context
    return text, None


def _parse_snooze(lowered: str) -> timedelta | None:
    """
    Detecta intención de posponer. Devuelve timedelta o None.
    Cubre: "en 10 minutos", "en 1 hora", "mañana", "luego",
           "a las 13:00", "para hoy a la 1:00", "para mañana a las 9"
    Ignora el contexto después de la coma (manejado por _extract_snooze_note).
    """
    import unicodedata as _ud
    norm = _ud.normalize("NFD", lowered).encode("ascii","ignore").decode()
    now = datetime.now(TZ)

    # "en X minutos"
    m = re.match(r'^(?:en\s+)?(\d+)\s+minutos?$', norm)
    if m: return timedelta(minutes=int(m.group(1)))

    # "en X horas"
    m = re.match(r'^(?:en\s+)?(\d+)\s+horas?$', norm)
    if m: return timedelta(hours=int(m.group(1)))

    # "media hora" / "en media hora"
    if re.match(r'^(?:en\s+)?media\s+hora$', norm):
        return timedelta(minutes=30)

    # "en un rato" / "en un momento"
    if re.match(r'^en\s+un\s+(?:rato|momento)$', norm):
        return timedelta(minutes=15)

    # "mañana" solo
    if norm in ("manana", "tomorrow"):
        return timedelta(hours=24)

    # "luego", "más tarde", "ahora no", "después"
    if norm in ("luego", "despues", "ahora no", "mas tarde", "mas tarde", "ahorita no"):
        return timedelta(hours=1)

    # "a las HH:MM" / "a la HH:MM" → hora concreta hoy o mañana
    m = re.match(r'^(?:.+\s+)?a\s+las?\s+(\d{1,2})(?::(\d{2}))?$', norm)
    if m:
        h = int(m.group(1))
        mins = int(m.group(2)) if m.group(2) else 0
        target = now.replace(hour=h, minute=mins, second=0, microsecond=0)
        if target <= now:
            target = target + timedelta(days=1)
        return target - now

    # "para hoy a las HH" / "para mañana a las HH"
    m = re.match(r'^(?:para\s+)?(?:hoy|manana|mañana)?\s*(?:a\s+las?\s+)?(\d{1,2})(?::(\d{2}))?\s*(?:en\s+punto)?$', norm)
    if m and m.group(1):
        h = int(m.group(1))
        mins = int(m.group(2)) if m.group(2) else 0
        manana = "manana" in norm or "mañana" in lowered
        target = now.replace(hour=h, minute=mins, second=0, microsecond=0)
        if manana:
            target = target + timedelta(days=1)
        elif target <= now:
            target = target + timedelta(days=1)
        return target - now

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


async def build_confirmation_ai(source_text: str, parsed: dict, reminder_id: int | None = None) -> str | None:
    """
    Genera una respuesta natural con Claude para confirmar el recordatorio.
    Devuelve None si no hay API key o falla — main.py usa el fallback síncrono.
    """
    from ai_parser import ANTHROPIC_API_KEY, MODEL
    if not ANTHROPIC_API_KEY:
        return None

    local_dt = to_local(parsed["remind_at"])
    day_names = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
    now_local = datetime.now(TZ)

    if local_dt.date() == now_local.date():
        fecha = f"hoy a las {local_dt.strftime('%H:%M')}"
    elif local_dt.date() == (now_local + timedelta(days=1)).date():
        fecha = f"mañana a las {local_dt.strftime('%H:%M')}"
    else:
        fecha = f"el {day_names[local_dt.weekday()]} {local_dt.strftime('%d/%m')} a las {local_dt.strftime('%H:%M')}"

    recurrence_info = ""
    if parsed.get("recurrence_type") == "weekly":
        recurrence_info = f" (se repite cada {parsed.get('recurrence_value', 'semana')})"
    elif parsed.get("recurrence_type") == "weekdays":
        recurrence_info = " (días laborables)"
    elif parsed.get("is_persistent"):
        mins = parsed.get("repeat_every_minutes", 2)
        recurrence_info = f" (repetiré cada {mins} min hasta que digas listo)"

    id_suffix = f" [{reminder_id}]" if reminder_id else ""

    prompt = (
        f"El usuario dijo: '{source_text}'\n"
        f"He creado el recordatorio: '{parsed['task_text']}' para {fecha}{recurrence_info}.{id_suffix}\n\n"
        f"Confirma esto en 1 frase corta y natural en español, sin emojis de cerebro, "
        f"sin 'EVA:' al principio. Incluye el ID {id_suffix} al final si existe. "
        f"Añade 'Di \"no, a las HH:MM\" si la hora es incorrecta.' en una segunda línea breve."
    )

    try:
        import httpx as _httpx
        async with _httpx.AsyncClient(timeout=8) as client:
            r = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": MODEL,
                    "max_tokens": 120,
                    "messages": [{"role": "user", "content": prompt}],
                },
            )
            r.raise_for_status()
            data = r.json()
            text_out = data["content"][0]["text"].strip()
            return text_out
    except Exception as exc:
        print(f"[ai_reply] error: {exc}")
        return None


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
    # Separar expresión de tiempo del contexto opcional: "a las 13:00, confirmar con Luis"
    time_part, snooze_note = _extract_snooze_note(lowered)
    snooze_delta = _parse_snooze(time_part)
    if snooze_delta is not None:
        now = datetime.now(TZ)
        new_remind_at = now + snooze_delta
        reminder.remind_at = new_remind_at
        reminder.status = "scheduled"
        reminder.awaiting_ack = False
        # Guardar nota si existe
        if snooze_note and hasattr(reminder, 'notes'):
            reminder.notes = snooze_note

        db.add(Event(
            user_id=user.id,
            event_type="reminder_snoozed",
            event_value=str(reminder.id),
            source="telegram",
            payload={"snooze_text": lowered, "new_remind_at": new_remind_at.isoformat(),
                     "note": snooze_note},
        ))
        db.commit()

        dt_str = to_local(new_remind_at).strftime("%H:%M")
        if snooze_note:
            reply = f'Movido a las {dt_str}. Apuntado: "{snooze_note}"'
        else:
            reply = f'Movido a las {dt_str}.'
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


async def handle_cancel_all_date(db, user: User, chat_id: int, date_hint: str | None, original_text: str):
    """
    Cancela todos los recordatorios de una fecha específica.
    date_hint: fecha en ISO (YYYY-MM-DD) extraída por el LLM, o None.
    """
    from datetime import date as date_type
    now = datetime.now(TZ)

    # Resolver la fecha objetivo
    target_date = None
    if date_hint:
        try:
            target_date = datetime.fromisoformat(date_hint).date()
        except Exception:
            pass

    # Si no hay fecha del LLM, inferir de palabras clave
    if not target_date:
        lowered = original_text.lower()
        if "mañana" in lowered:
            target_date = (now + timedelta(days=1)).date()
        elif "hoy" in lowered:
            target_date = now.date()
        elif "pasado mañana" in lowered:
            target_date = (now + timedelta(days=2)).date()

    if not target_date:
        reply = "No entendí qué fecha quieres limpiar. Di por ejemplo: 'cancela todo lo de mañana'."
        await send_and_log(db, user.id, chat_id, reply, "cancel_all_date_no_date")
        return {"status": "ok", "action": "cancel_all_date_no_date"}

    # Buscar recordatorios activos en esa fecha
    rows = db.execute(
        select(Reminder)
        .where(Reminder.user_id == user.id)
        .where(Reminder.status.in_(["scheduled", "pending", "sent"]))
    ).scalars().all()

    to_cancel = [r for r in rows if to_local(r.remind_at) and to_local(r.remind_at).date() == target_date]

    if not to_cancel:
        days = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
        day_name = days[target_date.weekday()]
        reply = f"No hay recordatorios activos el {day_name} {target_date.strftime('%d/%m')}."
        await send_and_log(db, user.id, chat_id, reply, "cancel_all_date_empty")
        return {"status": "ok", "action": "cancel_all_date_empty"}

    cancelled_texts = []
    for r in to_cancel:
        r.status = "cancelled"
        r.awaiting_ack = False
        r.cancelled_at = now
        r.error_message = "cancelled_by_user_all_date"
        cancelled_texts.append(f'"{r.task_text}"')

    db.add(Event(user_id=user.id, event_type="cancel_all_date", source="telegram",
                 payload={"date": str(target_date), "count": len(to_cancel)}))
    db.commit()

    days = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
    day_name = days[target_date.weekday()]
    reply = (f"Cancelados {len(to_cancel)} recordatorios del {day_name} {target_date.strftime('%d/%m')}:\n"
             + "\n".join(f"  • {t}" for t in cancelled_texts))
    await send_and_log(db, user.id, chat_id, reply, "cancel_all_date_done")
    return {"status": "ok", "action": "cancel_all_date_done", "count": len(to_cancel)}


async def handle_admin_cleanup(db, user: User, chat_id: int):
    """
    Limpia recordatorios de prueba (status=sent/cancelled con task_text de test)
    y elimina tarjetas duplicadas o de prueba en Focalboard.
    """
    import httpx as _httpx
    import time

    FOCALBOARD_URL   = os.getenv("FOCALBOARD_URL", "")
    FOCALBOARD_TOKEN = os.getenv("FOCALBOARD_TOKEN", "")
    FOCALBOARD_BOARD_ID = os.getenv("FOCALBOARD_BOARD_ID", "")

    await send_and_log(db, user.id, chat_id, "Limpiando... un momento.", "admin_cleanup_start")

    # 1. Cancelar en BD todos los reminders de test/prueba
    test_keywords = ["probar", "prueba", "test", "sistema", "focalboard", "integración"]
    rows = db.execute(
        select(Reminder)
        .where(Reminder.user_id == user.id)
        .where(Reminder.status.in_(["sent", "cancelled", "scheduled", "pending"]))
    ).scalars().all()

    cleaned_db = 0
    for r in rows:
        task_lower = r.task_text.lower()
        if any(kw in task_lower for kw in test_keywords):
            r.status = "cancelled"
            r.error_message = "cleaned_by_admin"
            cleaned_db += 1

    if cleaned_db:
        db.commit()

    # 2. Limpiar tarjetas de Focalboard — borrar duplicados y de test
    cleaned_fb = 0
    if FOCALBOARD_TOKEN and FOCALBOARD_BOARD_ID:
        try:
            # Renovar token
            headers = {"Authorization": f"Bearer {FOCALBOARD_TOKEN}",
                       "X-Requested-With": "XMLHttpRequest"}
            async with _httpx.AsyncClient(timeout=15) as client:
                r = await client.get(
                    f"{FOCALBOARD_URL}/api/v2/boards/{FOCALBOARD_BOARD_ID}/blocks?type=card",
                    headers=headers)
                if r.status_code == 200:
                    cards = r.json()
                    # Identificar tarjetas a borrar: test/prueba/duplicadas
                    test_words = ["probar", "prueba", "test", "sistema", "focalboard",
                                  "integración", "aviso previo", "card con fecha", "createat"]
                    # También detectar duplicados por título
                    from collections import defaultdict
                    by_title = defaultdict(list)
                    for card in cards:
                        by_title[card["title"].lower()].append(card)

                    to_delete = set()
                    for card in cards:
                        if any(kw in card["title"].lower() for kw in test_words):
                            to_delete.add(card["id"])
                    # Duplicados: mantener solo el más reciente
                    for title, dupes in by_title.items():
                        if len(dupes) > 1:
                            dupes_sorted = sorted(dupes, key=lambda x: x.get("createAt", 0), reverse=True)
                            for dup in dupes_sorted[1:]:  # borrar todos menos el más reciente
                                to_delete.add(dup["id"])

                    for card_id in to_delete:
                        del_r = await client.delete(
                            f"{FOCALBOARD_URL}/api/v2/boards/{FOCALBOARD_BOARD_ID}/blocks/{card_id}",
                            headers=headers)
                        if del_r.status_code in (200, 204):
                            cleaned_fb += 1
        except Exception as exc:
            print(f"[admin_cleanup] Focalboard error: {exc}")

    reply = (f"Limpieza completada:\n"
             f"  • BD: {cleaned_db} recordatorios de prueba cancelados\n"
             f"  • Focalboard: {cleaned_fb} tarjetas eliminadas")
    await send_and_log(db, user.id, chat_id, reply, "admin_cleanup_done")
    return {"status": "ok", "action": "admin_cleanup_done",
            "cleaned_db": cleaned_db, "cleaned_fb": cleaned_fb}


async def handle_add_note(db, user: User, chat_id: int, note_text: str, ref_id: int | None = None):
    """
    Añade una nota/texto a la última tarjeta/reminder mencionado o al indicado por ID.
    Actualiza campo 'notes' en la BD y la propiedad Texto en Focalboard.
    """
    import httpx as _httpx

    # Resolver el reminder objetivo
    if ref_id:
        target = db.execute(
            select(Reminder).where(Reminder.id == ref_id).where(Reminder.user_id == user.id)
        ).scalar_one_or_none()
        if not target:
            reply = f"No encontré la tarea [{ref_id}]."
            await send_and_log(db, user.id, chat_id, reply, "add_note_not_found")
            return {"status": "ok", "action": "add_note_not_found"}
    else:
        # Buscar la última tarea mencionada en el último mensaje saliente de EVA
        last_out = db.execute(
            select(Message).where(Message.user_id == user.id)
            .where(Message.direction == "outbound")
            .order_by(Message.id.desc()).limit(1)
        ).scalars().first()

        target = None
        if last_out:
            id_match = re.search(r'\[(\d+)\]', last_out.message_text)
            if id_match:
                rid = int(id_match.group(1))
                target = db.execute(
                    select(Reminder).where(Reminder.id == rid).where(Reminder.user_id == user.id)
                ).scalar_one_or_none()

        if not target:
            # Fallback: el reminder activo más reciente con focalboard_card_id
            target = db.execute(
                select(Reminder).where(Reminder.user_id == user.id)
                .where(Reminder.focalboard_card_id.isnot(None))
                .order_by(Reminder.id.desc()).limit(1)
            ).scalars().first()

        if not target:
            reply = "No sé a qué tarea te refieres. Dime el ID, por ejemplo: '52 agrégale una nota: texto'"
            await send_and_log(db, user.id, chat_id, reply, "add_note_no_target")
            return {"status": "ok", "action": "add_note_no_target"}

    # Actualizar notes en BD
    target.notes = note_text
    db.commit()

    # Actualizar propiedad Texto en Focalboard
    FOCALBOARD_URL   = os.getenv("FOCALBOARD_URL", "")
    FOCALBOARD_TOKEN = os.getenv("FOCALBOARD_TOKEN", "")
    FOCALBOARD_BOARD_ID = os.getenv("FOCALBOARD_BOARD_ID", "")

    if target.focalboard_card_id and FOCALBOARD_TOKEN:
        try:
            async with _httpx.AsyncClient(timeout=8) as client:
                await client.patch(
                    f"{FOCALBOARD_URL}/api/v2/boards/{FOCALBOARD_BOARD_ID}/blocks/{target.focalboard_card_id}",
                    headers={"Authorization": f"Bearer {FOCALBOARD_TOKEN}",
                             "X-Requested-With": "XMLHttpRequest",
                             "Content-Type": "application/json"},
                    json={"updatedFields": {"properties": {
                        "a6bxuk4rgxp7wn6bashiadwaiiy": note_text
                    }}}
                )
        except Exception as exc:
            print(f"[add_note] Focalboard error: {exc}")

    reply = f'✅ Nota añadida a "{target.task_text}" [{target.id}]: "{note_text}"'
    await send_and_log(db, user.id, chat_id, reply, "add_note_done")
    return {"status": "ok", "action": "add_note_done", "reminder_id": target.id}


async def handle_pending_task(db, user: User, chat_id: int, task_text: str,
                              url: str | None = None):
    """
    Crea una tarea sin fecha en Focalboard Y en la tabla reminders (remind_at=NULL).
    Así el sync bidireccional puede detectar cambios desde Focalboard.
    url: URL opcional, se guarda en propiedad URL de Focalboard y en notes.
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
                **{"aevastatus00000000000000001": "aoptpendiente00000000000001"},
                **({"asztuket5mjeeongrzooyx5utbo": url} if url else {}),
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
                # Inferir prioridad para la tarea pendiente
                try:
                    _task_priority = await infer_priority(task_text)
                except Exception:
                    _task_priority = "P3"

                # Guardar también en reminders para que el sync bidireccional funcione
                try:
                    pending_reminder = Reminder(
                        user_id=user.id,
                        source_text=task_text,
                        task_text=task_text,
                        remind_at=datetime.now(TZ).replace(year=2099),
                        status="pending",
                        notes=url if url else None,
                        priority=_task_priority,
                        focalboard_card_id=fb_id,
                        focalboard_synced_at=datetime.now(TZ),
                    )
                    db.add(pending_reminder)
                    db.add(Event(
                        user_id=user.id,
                        event_type="pending_task_created",
                        event_value=fb_id,
                        source="telegram",
                        payload={"task_text": task_text, "card_id": fb_id, "url": url},
                    ))
                    db.commit()
                except Exception as exc:
                    print(f"[pending_task] reminder save error: {exc}")
                    db.rollback()

                reply = (
                    f'📌 Apuntado en Focalboard: "{task_text}"'
                    + (f'\n🔗 {url}' if url else '')
                    + '\nCuando tengas un momento, asígnale fecha desde la UI.'
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

        # ── Extraer URL del mensaje si existe ───────────────────────────────
        _url_in_msg = re.search(r'https?://\S+', text_in)
        _extracted_url = _url_in_msg.group(0) if _url_in_msg else None
        # Texto sin la URL para analizar la intención
        _text_no_url = text_in.replace(_extracted_url, "").strip() if _extracted_url else text_in

        # ── Mensaje que ES solo una URL → tarea sin fecha con URL ────────────
        if _extracted_url and len(_text_no_url.strip()) < 5:
            # Solo URL, sin texto descriptivo → apuntar con dominio como título
            import urllib.parse as _up
            _domain = _up.urlparse(_extracted_url).netloc.replace("www.", "")
            task_title = f"Revisar {_domain}"
            return await handle_pending_task(db, user, chat_id, task_title, url=_extracted_url)

        # ── Gestión de notas/recordatorios por ID: "52 eliminala", "la tarea 52 marcala como hecha" ──
        _id_op = re.match(
            r'^(?:(?:la|el)\s+)?(?:tarea|nota|recordatorio)?\s*(\d+)\s+(.+)$',
            lowered.strip(), re.IGNORECASE
        )
        if _id_op:
            _ref_id = int(_id_op.group(1))
            _op_text = _id_op.group(2).strip()
            # Cancelar/eliminar
            if re.match(r'^(?:cancela(?:la|lo)?|elimina(?:la|lo)?|borra(?:la|lo)?|quita(?:la|lo)?)[\s.!?]*$', _op_text):
                return await handle_cancel_by_id(db, user, chat_id, _ref_id)
            # Completar
            if re.match(r'^(?:marca(?:la|lo)?\s+(?:como\s+)?(?:hecha?|completad[ao]|lista?)|completa(?:la|lo)?)[\s.!?]*$', _op_text):
                _ref_r = db.execute(
                    select(Reminder).where(Reminder.id == _ref_id).where(Reminder.user_id == user.id)
                ).scalar_one_or_none()
                if _ref_r:
                    _ref_r.status = "completed"
                    _ref_r.completed_at = datetime.now(TZ)
                    db.commit()
                    reply = f'Completado [{_ref_id}]: "{_ref_r.task_text}".'
                    await send_and_log(db, user.id, chat_id, reply, "completed_by_id_ref")
                    return {"status": "ok", "action": "completed_by_id_ref"}
            # Añadir nota
            _note_match = re.match(r'^(?:agr[eé]ga(?:le)?(?:\s+una?)?\s+nota[:\s]+|a[ñn]ade(?:le)?(?:\s+una?)?\s+nota[:\s]+)(.+)$', _op_text, re.IGNORECASE)
            if _note_match:
                return await handle_add_note(db, user, chat_id, _note_match.group(1).strip(), ref_id=_ref_id)

            # Posponer/snooze por ID: "71 posponlo 30 minutos" / "71 muévelo al lunes"
            _move_by_id = re.match(
                r'^(?:pospon(?:lo|la)?|mueve(?:lo|la)?|pasa(?:lo|la)?|aplaza(?:lo|la)?)(?:\s+(?:para|en|al?|a))?\s+(.+)$',
                _op_text, re.IGNORECASE
            )
            if _move_by_id:
                _new_time_text = _move_by_id.group(1).strip()
                _target_r = db.execute(
                    select(Reminder).where(Reminder.id == _ref_id).where(Reminder.user_id == user.id)
                ).scalar_one_or_none()
                if _target_r:
                    from parser_service import parse_reminder as _parse_regex
                    _synthetic = f"recuérdame {_target_r.task_text} {_new_time_text}"
                    _new_parsed = await parse_reminder_ai(_synthetic, memory_context=system_prompt)
                    if _new_parsed is None:
                        _new_parsed = _parse_regex(_synthetic)
                    if _new_parsed:
                        _target_r.remind_at = _new_parsed["remind_at"]
                        _target_r.status = "scheduled"
                        _target_r.awaiting_ack = False
                        db.commit()
                        new_dt = to_local(_target_r.remind_at)
                        days_es = ["lunes","martes","miércoles","jueves","viernes","sábado","domingo"]
                        now_tz = datetime.now(TZ)
                        if new_dt.date() == now_tz.date(): day_str = "hoy"
                        elif new_dt.date() == (now_tz+timedelta(days=1)).date(): day_str = "mañana"
                        else: day_str = f"el {days_es[new_dt.weekday()]} {new_dt.strftime('%d/%m')}"
                        reply = f'Movido [{_ref_id}]: "{_target_r.task_text}" → {day_str} a las {new_dt.strftime("%H:%M")}.'
                        await send_and_log(db, user.id, chat_id, reply, "move_by_id")
                        return {"status": "ok", "action": "move_by_id"}
                    else:
                        reply = f'No entendí la nueva fecha. Di por ejemplo: "{_ref_id} posponlo para el lunes a las 10".'
                        await send_and_log(db, user.id, chat_id, reply, "move_by_id_fail")
                        return {"status": "ok", "action": "move_by_id_fail"}
            # Cambiar nombre: "53 cámbiala a nuevo nombre"
            _rename_match = re.match(r'^(?:cambia(?:la|lo)?\s+(?:a|el\s+nombre\s+a)[:\s]+)(.+)$', _op_text, re.IGNORECASE)
            if _rename_match:
                _ref_r = db.execute(
                    select(Reminder).where(Reminder.id == _ref_id).where(Reminder.user_id == user.id)
                ).scalar_one_or_none()
                if _ref_r:
                    _ref_r.task_text = _rename_match.group(1).strip()
                    db.commit()
                    reply = f'Renombrado [{_ref_id}]: ahora es "{_ref_r.task_text}".'
                    await send_and_log(db, user.id, chat_id, reply, "renamed_by_id_ref")
                    return {"status": "ok", "action": "renamed_by_id_ref"}


        user_facts = get_user_facts(db, user.id)
        memory_ctx = build_memory_context(user_facts)
        persona = load_persona(telegram_username)
        system_prompt = build_system_prompt(persona, memory_context=memory_ctx)

        # ── Extraer memoria del mensaje en background (sesión propia) ────────
        async def _extract_memory_bg(user_id: int, text: str):
            _db = SessionLocal()
            try:
                await process_message_for_memory(_db, user_id, text)
            finally:
                _db.close()

        import asyncio
        asyncio.ensure_future(_extract_memory_bg(user.id, text_in))

        # ── Detección de intención: regex rápidos primero, LLM para el resto ─

        # Comandos deterministas que no necesitan LLM
        if is_list_command(lowered):
            return await handle_list_command(db, user, chat_id)

        _cancel_keywords = ("cancela", "cancelar", "elimina", "eliminar", "borra", "borrar")
        _id_match = re.search(r'\b(\d{1,6})\b', lowered)
        if any(w in lowered for w in _cancel_keywords) and _id_match:
            return await handle_cancel_by_id(db, user, chat_id, int(_id_match.group(1)))

        if is_ack_text(lowered):
            return await handle_ack_command(db, user, chat_id, lowered)

        # "recuérdame en X minutos/horas" cuando hay aviso activo → snooze
        # No crear nuevo recordatorio si hay uno esperando ACK
        _snooze_when_active = re.match(
            r'^(?:recu[eé]rdame\s+)?(?:en\s+)?(\d+)\s+(minutos?|horas?)[\s.!?]*$',
            lowered.strip(), re.IGNORECASE
        )
        if _snooze_when_active:
            _active_now = db.execute(
                select(Reminder)
                .where(Reminder.user_id == user.id)
                .where(
                    (Reminder.awaiting_ack.is_(True)) |
                    (Reminder.status == "sent")
                )
                .limit(1)
            ).scalars().first()
            if _active_now:
                return await handle_ack_command(db, user, chat_id, lowered)

        # Corrección rápida: "no, a las 11"
        _correction = re.match(r'^no[,.]?\s+(?:era\s+)?a las?\s+(\d{1,2})(?::(\d{2}))?$', lowered, re.IGNORECASE)
        if _correction:
            new_hour = int(_correction.group(1))
            new_minute = int(_correction.group(2)) if _correction.group(2) else 0
            last_r = db.execute(
                select(Reminder).where(Reminder.user_id == user.id)
                .where(Reminder.status.in_(["scheduled", "pending"]))
                .order_by(Reminder.id.desc()).limit(1)
            ).scalars().first()
            if last_r:
                now_tz = datetime.now(TZ)
                new_dt = to_local(last_r.remind_at).replace(hour=new_hour, minute=new_minute, second=0, microsecond=0)
                if new_dt <= now_tz:
                    new_dt = new_dt + timedelta(days=1)
                last_r.remind_at = new_dt
                last_r.status = "scheduled"
                db.add(Event(user_id=user.id, event_type="reminder_corrected",
                             event_value=str(last_r.id), source="telegram",
                             payload={"new_time": f"{new_hour:02d}:{new_minute:02d}"}))
                db.commit()
                reply = f'Corregido [{last_r.id}]: "{last_r.task_text}" — ahora a las {new_dt.strftime("%H:%M")}.'
                await send_and_log(db, user.id, chat_id, reply, "reminder_corrected")
                return {"status": "ok", "action": "reminder_corrected", "reminder_id": last_r.id}

        # ── Plural pronoun cancel: "cancelarlos", "eliminarlos" ───────────────
        # "puedes cancelarlos" → cancela todos los del contexto activo
        _plural_cancel = re.match(
            r'^(?:puedes\s+)?(?:cancela(?:r)?los|elimina(?:r)?los|borra(?:r)?los|quita(?:r)?los)[\s.!?]*$',
            lowered.strip(), re.IGNORECASE
        )
        if _plural_cancel:
            # Buscar fecha en los últimos mensajes de EVA
            last_msgs = db.execute(
                select(Message).where(Message.user_id == user.id)
                .where(Message.direction == "outbound")
                .order_by(Message.id.desc()).limit(3)
            ).scalars().all()
            date_hint = None
            now_tz = datetime.now(TZ)
            for msg in last_msgs:
                txt = msg.message_text.lower()
                if "mañana" in txt:
                    date_hint = (now_tz + timedelta(days=1)).strftime("%Y-%m-%d")
                    break
                elif "hoy" in txt:
                    date_hint = now_tz.strftime("%Y-%m-%d")
                    break
                elif "viernes" in txt or "lunes" in txt or "martes" in txt:
                    # Buscar fecha explícita en el texto
                    import re as _re2
                    m = _re2.search(r'(\d{1,2}/\d{2})', txt)
                    if m:
                        try:
                            d, mo = m.group(1).split("/")
                            date_hint = f"{now_tz.year}-{mo}-{d.zfill(2)}"
                        except Exception:
                            pass
                    break
            return await handle_cancel_all_date(db, user, chat_id, date_hint, text_in)

        # ── Resolución de pronombres ──────────────────────────────────────────
        # "cancelalo", "posponlo para el lunes", "cambialo a las 11", etc.
        # Opera sobre el próximo reminder activo (el que EVA acaba de mencionar)

        def _get_next_reminder():
            """
            Devuelve el reminder más relevante para operar con pronombres.
            Orden de prioridad:
              1. Reminder con awaiting_ack=True (está esperando confirmación AHORA)
              2. Reminder mencionado por ID en el último mensaje de EVA
              3. Reminder mencionado por texto en el último mensaje de EVA
              4. Próximo reminder activo por fecha
            """
            # 1. Prioridad máxima: reminder esperando ACK ahora mismo
            ack_r = db.execute(
                select(Reminder)
                .where(Reminder.user_id == user.id)
                .where(Reminder.awaiting_ack.is_(True))
                .order_by(Reminder.last_sent_at.desc().nullslast())
                .limit(1)
            ).scalars().first()
            if ack_r:
                return ack_r

            # 2. Buscar ID en el último mensaje saliente de EVA
            last_out = db.execute(
                select(Message)
                .where(Message.user_id == user.id)
                .where(Message.direction == "outbound")
                .order_by(Message.id.desc())
                .limit(1)
            ).scalars().first()

            if last_out:
                id_match = re.search(r'\[(\d+)\]', last_out.message_text)
                if id_match:
                    rid = int(id_match.group(1))
                    r = db.execute(
                        select(Reminder)
                        .where(Reminder.id == rid)
                        .where(Reminder.user_id == user.id)
                        .where(Reminder.status.in_(["scheduled", "pending", "sent"]))
                    ).scalar_one_or_none()
                    if r:
                        return r

                # 3. Buscar por task_text entre comillas en el último mensaje
                text_match = re.search(r'"([^"]+)"', last_out.message_text)
                if text_match:
                    mentioned = text_match.group(1).lower()
                    rows = db.execute(
                        select(Reminder)
                        .where(Reminder.user_id == user.id)
                        .where(Reminder.status.in_(["scheduled", "pending", "sent"]))
                    ).scalars().all()
                    for r in rows:
                        if mentioned in r.task_text.lower() or r.task_text.lower() in mentioned:
                            return r

            # 4. Fallback: el próximo por fecha
            return db.execute(
                select(Reminder)
                .where(Reminder.user_id == user.id)
                .where(Reminder.status.in_(["scheduled", "pending", "sent"]))
                .order_by(Reminder.remind_at.asc())
                .limit(1)
            ).scalars().first()

        # Normalizar sin acentos para matching robusto
        import unicodedata as _ud
        def _norm(s): return _ud.normalize("NFD", s.lower()).encode("ascii","ignore").decode()
        lowered_norm = _norm(lowered)

        # Cancelar con pronombre: "cancelalo", "cancélalo", "eliminalo", "bórralo", "quítalo"
        _pronoun_cancel = re.match(
            r'^(?:cancela(?:lo|la)?|elimina(?:lo|la)?|borra(?:lo|la)?|quita(?:lo|la)?)[\s.!?]*$',
            lowered_norm.strip()
        )
        if _pronoun_cancel:
            last_r = _get_next_reminder()
            if last_r:
                return await handle_cancel_by_id(db, user, chat_id, last_r.id)

        # Posponer/mover con pronombre:
        # "posponlo para el lunes", "muévelo al martes", "pásalo a mañana",
        # "posponlo para el próximo lunes a las 10", "muévelo al 15/05"
        _pronoun_move = re.match(
            r'^(?:pospon(?:lo|la)?|mueve(?:lo|la)?|pasa(?:lo|la)?'
            r'|retrasa(?:lo|la)?|aplaza(?:lo|la)?|deja(?:lo|la)?(?:\s+para))'
            r'(?:\s+(?:para|al?|hasta|a))?\s+(.+)$',
            lowered_norm.strip()
        )
        if _pronoun_move:
            last_r = _get_next_reminder()
            if last_r:
                new_time_text = _pronoun_move.group(1).strip()
                # Parsear la nueva fecha/hora
                from parser_service import parse_reminder as _parse_regex
                _synthetic = f"recuérdame {last_r.task_text} {new_time_text}"
                _parsed_new = await parse_reminder_ai(_synthetic, memory_context=memory_ctx)
                if _parsed_new is None:
                    _parsed_new = _parse_regex(_synthetic)
                if _parsed_new:
                    last_r.remind_at = _parsed_new["remind_at"]
                    last_r.status = "scheduled"
                    last_r.awaiting_ack = False
                    db.add(Event(user_id=user.id, event_type="reminder_rescheduled",
                                 event_value=str(last_r.id), source="telegram",
                                 payload={"new_time": str(_parsed_new["remind_at"]), "via": "pronoun"}))
                    db.commit()
                    now_l = datetime.now(TZ)
                    new_dt = to_local(last_r.remind_at)
                    days_es = ["lunes","martes","miércoles","jueves","viernes","sábado","domingo"]
                    if new_dt.date() == now_l.date(): day_str = "hoy"
                    elif new_dt.date() == (now_l + timedelta(days=1)).date(): day_str = "mañana"
                    else: day_str = f"el {days_es[new_dt.weekday()]} {new_dt.strftime('%d/%m')}"
                    reply = f'Movido [{last_r.id}]: "{last_r.task_text}" → {day_str} a las {new_dt.strftime("%H:%M")}.'
                    await send_and_log(db, user.id, chat_id, reply, "reminder_rescheduled_pronoun")
                    return {"status": "ok", "action": "reminder_rescheduled", "reminder_id": last_r.id}
                else:
                    reply = f'No entendí la nueva fecha. Di por ejemplo: "posponlo para el lunes a las 10".'
                    await send_and_log(db, user.id, chat_id, reply, "pronoun_move_parse_fail")
                    return {"status": "ok", "action": "pronoun_move_parse_fail"}

        # Editar hora con pronombre: "cambialo a las 11", "ponlo a las 3", "muévelo a las 15:00"
        _pronoun_edit_time = re.match(
            r'^(?:cambia(?:lo|la)?|pon(?:lo|la)?|mueve(?:lo|la)?|edita(?:lo|la)?)'
            r'(?:\s+(?:al?|a))?\s+(?:las?\s+)?(\d{1,2})(?::(\d{2}))?[\s.!?]*$',
            lowered_norm.strip()
        )
        if _pronoun_edit_time:
            last_r = _get_next_reminder()
            if last_r:
                new_hour   = int(_pronoun_edit_time.group(1))
                new_minute = int(_pronoun_edit_time.group(2)) if _pronoun_edit_time.group(2) else 0
                now_tz = datetime.now(TZ)
                new_dt = to_local(last_r.remind_at).replace(hour=new_hour, minute=new_minute, second=0, microsecond=0)
                if new_dt <= now_tz:
                    new_dt = new_dt + timedelta(days=1)
                last_r.remind_at = new_dt
                last_r.status = "scheduled"
                db.add(Event(user_id=user.id, event_type="reminder_edited_pronoun",
                             event_value=str(last_r.id), source="telegram",
                             payload={"new_time": f"{new_hour:02d}:{new_minute:02d}"}))
                db.commit()
                reply = f'Cambiado [{last_r.id}]: "{last_r.task_text}" → ahora a las {new_dt.strftime("%H:%M")}.'
                await send_and_log(db, user.id, chat_id, reply, "reminder_edited_pronoun")
                return {"status": "ok", "action": "reminder_edited_pronoun", "reminder_id": last_r.id}

        # ── Detección unificada con LLM ──────────────────────────────────────
        intent_result = await detect_intent(text_in, memory_context=system_prompt)
        intent = intent_result.get("intent", "unknown")
        confidence = intent_result.get("confidence", 0.0)

        # ── SNOOZE CONTEXTUAL: si hay aviso activo + intent de mover → snooze ─
        if intent in ("snooze_reminder", "edit_reminder") and confidence >= 0.6:
            active_ack = db.execute(
                select(Reminder)
                .where(Reminder.user_id == user.id)
                .where(
                    (Reminder.awaiting_ack.is_(True)) |
                    (Reminder.status == "sent")
                )
                .order_by(Reminder.last_sent_at.desc().nullslast(), Reminder.id.desc())
                .limit(1)
            ).scalars().first()
            if active_ack:
                # Separar tiempo de nota opcional: "a las 13:00, confirmar con Luis"
                time_part, snooze_note = _extract_snooze_note(lowered)
                snooze_delta = _parse_snooze(time_part)
                if snooze_delta is not None:
                    # Procesar snooze directamente aquí — NO delegar a handle_ack_command
                    # para evitar doble respuesta
                    now_tz = datetime.now(TZ)
                    new_remind_at = now_tz + snooze_delta
                    active_ack.remind_at = new_remind_at
                    active_ack.status = "scheduled"
                    active_ack.awaiting_ack = False
                    if snooze_note and hasattr(active_ack, "notes"):
                        active_ack.notes = snooze_note
                    db.add(Event(user_id=user.id, event_type="reminder_snoozed",
                                 event_value=str(active_ack.id), source="telegram",
                                 payload={"snooze_text": lowered, "note": snooze_note,
                                          "new_remind_at": new_remind_at.isoformat()}))
                    db.commit()
                    dt_str = to_local(new_remind_at).strftime("%H:%M")
                    # Generar respuesta con AI incluyendo la nota si existe
                    _note_ctx = f" Nota guardada: '{snooze_note}'." if snooze_note else ""
                    _ai_reply = await build_reply_ai(
                        text_in,
                        {"task_text": active_ack.task_text, "remind_at": new_remind_at,
                         "mode": "today_or_tomorrow_at_time", "is_persistent": False,
                         "recurrence_type": None, "repeat_every_minutes": None},
                        memory_context=system_prompt + f"\nContexto adicional: el usuario pospuso '{active_ack.task_text}' a las {dt_str}.{_note_ctx}"
                    )
                    reply = _ai_reply or (
                        f'Movido a las {dt_str}.'
                        + (f' Apuntado: "{snooze_note}"' if snooze_note else "")
                    )
                    await send_and_log(db, user.id, chat_id, reply, "snooze_contextual")
                    return {"status": "ok", "action": "reminder_snoozed", "reminder_id": active_ack.id}

                # Sin delta concreto → AI parser para obtener la nueva hora
                _snooze_parsed = await parse_reminder_ai(
                    f"recuérdame {active_ack.task_text} {text_in}",
                    memory_context=system_prompt
                )
                if _snooze_parsed:
                    now_tz = datetime.now(TZ)
                    active_ack.remind_at = _snooze_parsed["remind_at"]
                    active_ack.status = "scheduled"
                    active_ack.awaiting_ack = False
                    if snooze_note and hasattr(active_ack, "notes"):
                        active_ack.notes = snooze_note
                    db.add(Event(user_id=user.id, event_type="reminder_snoozed",
                                 event_value=str(active_ack.id), source="telegram",
                                 payload={"via": "ai_snooze", "text": text_in, "note": snooze_note}))
                    db.commit()
                    new_dt = to_local(active_ack.remind_at)
                    days_es = ["lunes","martes","miércoles","jueves","viernes","sábado","domingo"]
                    if new_dt.date() == now_tz.date(): day_str = "hoy"
                    elif new_dt.date() == (now_tz + timedelta(days=1)).date(): day_str = "mañana"
                    else: day_str = f"el {days_es[new_dt.weekday()]} {new_dt.strftime('%d/%m')}"
                    reply = (f'Movido: "{active_ack.task_text}" → {day_str} a las {new_dt.strftime("%H:%M")}.'
                             + (f' Apuntado: "{snooze_note}"' if snooze_note else ""))
                    await send_and_log(db, user.id, chat_id, reply, "snooze_ai_contextual")
                    return {"status": "ok", "action": "reminder_snoozed_ai"}

        # ── QUESTION: EVA responde preguntas sobre recordatorios ─────────────
        if intent == "question" and confidence >= 0.7:
            active = db.execute(
                select(Reminder)
                .where(Reminder.user_id == user.id)
                .where(Reminder.status.in_(["scheduled", "pending", "sent"]))
                .order_by(Reminder.remind_at.asc())
                .limit(20)
            ).scalars().all()
            now_local = datetime.now(TZ)
            days = ["lunes","martes","miércoles","jueves","viernes","sábado","domingo"]
            summary_lines = []
            for r in active:
                dt = to_local(r.remind_at)
                if dt:
                    if dt.date() == now_local.date(): day_str = "hoy"
                    elif dt.date() == (now_local + timedelta(days=1)).date(): day_str = "mañana"
                    else: day_str = f"{days[dt.weekday()]} {dt.strftime('%d/%m')}"
                    summary_lines.append(f"- [{r.id}] {r.task_text} — {day_str} a las {dt.strftime('%H:%M')} ({r.status})")
                else:
                    summary_lines.append(f"- [{r.id}] {r.task_text} (sin fecha)")
            summary = "\n".join(summary_lines)
            answer = await answer_question_ai(text_in, summary, memory_context=system_prompt)
            if answer:
                await send_and_log(db, user.id, chat_id, answer, "question_answer")
                return {"status": "ok", "action": "question_answered"}

        # ── CANCEL sin ID — busca por texto ─────────────────────────────────
        if intent == "cancel_reminder" and confidence >= 0.7:
            cancel_task = extract_cancel_task(lowered)
            if cancel_task:
                return await handle_cancel_command(db, user, chat_id, cancel_task)

        # ── CANCEL ALL DATE — cancela todos los de una fecha ─────────────────
        if intent == "cancel_all_date" and confidence >= 0.7:
            date_hint = intent_result.get("date_hint")
            return await handle_cancel_all_date(db, user, chat_id, date_hint, text_in)

        # ── ADD NOTE — añadir nota a la última tarea/reminder ────────────────
        if intent == "add_note" and confidence >= 0.7:
            # Extraer el texto de la nota del mensaje
            _note_text = re.sub(
                r'^(?:agr[eé]ga(?:le)?(?:\s+una?)?\s+nota[:\s]+|'
                r'a[ñn]ade(?:le)?(?:\s+una?)?\s+nota[:\s]+|'
                r'agrega\s+(?:esto|que)[:\s]+|'
                r'apunta\s+(?:que|esto)[:\s]+)',
                '', lowered, flags=re.IGNORECASE
            ).strip()
            if not _note_text:
                _note_text = text_in  # usar texto completo si no se pudo extraer
            return await handle_add_note(db, user, chat_id, _note_text)

        # ── ADMIN CLEANUP ─────────────────────────────────────────────────────
        if intent == "admin_cleanup" and confidence >= 0.7:
            return await handle_admin_cleanup(db, user, chat_id)

        # ── EDIT ─────────────────────────────────────────────────────────────
        if intent == "edit_reminder" and confidence >= 0.7:
            edit_result = extract_edit_command(lowered)
            if edit_result:
                reminder_id, updates = edit_result
                return await handle_edit_reminder(db, user, chat_id, reminder_id, updates)

        # ── PENDING TASK ─────────────────────────────────────────────────────
        # Detección directa: "recuérdame que tengo que X" sin hora → tarea sin fecha
        _no_time = not re.search(r'\ba las\s+\d|\ben\s+\d+\s+min|\bmañana\b', lowered)
        _pending_direct = re.match(
            r'^(?:eva[,\s]+)?recu[eé]rdame\s+que\s+(?:tengo\s+que|hay\s+que|debo|necesito)\s+(.+)$',
            lowered, re.IGNORECASE
        )
        if _pending_direct and _no_time:
            task = _pending_direct.group(1).strip()
            if len(task) >= 4:
                return await handle_pending_task(db, user, chat_id, task, url=_extracted_url)

        if intent == "pending_task" and confidence >= 0.7:
            pending_task = extract_pending_task(lowered)
            if pending_task:
                return await handle_pending_task(db, user, chat_id, pending_task, url=_extracted_url)
            await handle_pending_task(db, user, chat_id, text_in, url=_extracted_url)
            return {"status": "ok", "action": "pending_task_created"}

        # ── CREATE REMINDER ──────────────────────────────────────────────────
        if intent in ("create_reminder", "unknown") or confidence < 0.7:
            parsed = await parse_reminder_ai(text_in,
                                              context=_get_recent_context(db, user.id),
                                              memory_context=system_prompt)
            if parsed is None:
                parsed = parse_reminder(text_in, context=_get_recent_context(db, user.id))
        else:
            parsed = None


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
            # Inferir prioridad con IA en background
            try:
                _priority = await infer_priority(reminder.task_text)
                reminder.priority = _priority
            except Exception:
                reminder.priority = "P3"

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

            reply_text = await build_reply_ai(text_in, parsed, reminder.id, memory_context=system_prompt)
            if reply_text is None:
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

        # ── CHAT o mensaje no reconocido ─────────────────────────────────────
        if intent == "chat" and confidence >= 0.7:
            chat_reply = await chat_reply_ai(text_in, memory_context=system_prompt)
            if chat_reply:
                await send_and_log(db, user.id, chat_id, chat_reply, "chat_reply")
                return {"status": "ok", "action": "chat_reply"}

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
    Dispara el resumen diario con IA.
    - Sin parámetros: envía a todos los usuarios.
    - Con user_id: envía solo a ese usuario.
    """
    from ai_parser import build_briefing_ai
    from memory_service import get_user_facts
    from persona_service import load_persona
    from sqlalchemy import text as sql_text

    db = SessionLocal()
    try:
        async def _send(chat_id: int, text_out: str, parse_mode: str = "Markdown"):
            await send_message(chat_id, text_out, parse_mode=parse_mode)

        async def _send_briefing_to_user(user: User) -> bool:
            now = datetime.now(TZ)
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            today_end   = now.replace(hour=23, minute=59, second=59, microsecond=0)

            # Recordatorios de hoy
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

            # Eventos relevantes de ayer
            yesterday_start = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            recent_events_raw = db.execute(
                select(Event)
                .where(Event.user_id == user.id)
                .where(Event.event_type.in_([
                    "reminder_rescheduled", "reminder_cancelled",
                    "reminder_corrected", "reminder_created"
                ]))
                .where(Event.created_at >= yesterday_start)
                .order_by(Event.created_at.desc())
                .limit(10)
            ).scalars().all()

            events_data = [
                {"type": e.event_type, "value": e.event_value or "", "payload": e.payload}
                for e in recent_events_raw
            ]

            # Enriquecer eventos con task_text del payload
            for ev in events_data:
                if "task_text" in (ev["payload"] or {}):
                    ev["value"] = ev["payload"]["task_text"]

            # Memoria y persona
            user_facts = get_user_facts(db, user.id)
            persona = load_persona(user.telegram_username)

            # Generar briefing con IA
            briefing = await build_briefing_ai(
                reminders_today=reminders_data,
                recent_events=events_data,
                user_facts=user_facts,
                persona=persona,
            )

            # Fallback al briefing clásico si IA falla
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
                return JSONResponse(status_code=404, content={"status": "error", "reason": "user_not_found"})
            sent = await _send_briefing_to_user(user)
            return {"status": "ok", "sent": 1 if sent else 0}

        # Enviar a todos
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