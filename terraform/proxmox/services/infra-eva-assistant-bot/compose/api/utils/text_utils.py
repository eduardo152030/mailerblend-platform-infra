"""
utils/text_utils.py
===================
Pure text parsing utilities — no DB, no network, no side effects.

Isolated here so:
- Telegram intent bugs → inspect only this file.
- Snooze parsing bugs → inspect only this file.
- Adding new command phrases → inspect only this file.
"""
import re
import unicodedata
from datetime import datetime, timedelta
from typing import Optional

from core.config import TZ
from models import Reminder
from utils.time_utils import to_local


# ── Normalization ─────────────────────────────────────────────────────────

def normalize_text(text_in: str) -> str:
    txt = text_in.lower().strip()
    txt = re.sub(r"\s+", " ", txt)
    return txt


def norm_ascii(s: str) -> str:
    """Strip accents for robust matching."""
    return unicodedata.normalize("NFD", s.lower()).encode("ascii", "ignore").decode()


# ── Command detection ─────────────────────────────────────────────────────

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


def is_ack_text(lowered: str) -> bool:
    ack_values = {
        "ok", "okay", "vale", "listo", "gracias", "hecho",
        "ya está", "ya esta", "si", "sí", "ya", "perfecto",
    }
    if lowered in ack_values:
        return True
    simple_snooze = {
        "luego", "después", "despues", "ahora no", "más tarde",
        "mas tarde", "mañana", "manana", "en un rato", "media hora",
    }
    if lowered in simple_snooze:
        return True
    if re.match(r'^en\s+\d+\s+(?:minutos?|horas?)$', lowered):
        return True
    # "recuérdamelo a las X" / "a las X solo hoy" with active reminder = snooze
    if re.search(r'\ba\s+las?\s+\d{1,2}(?::\d{2})?\b', lowered):
        if re.search(r'\b(?:recu[eé]rdamelo?|solo\s+hoy|para\s+hoy|hoy)\b', lowered):
            return True
    return False


# ── Pending task extraction ───────────────────────────────────────────────

def extract_pending_task(lowered: str) -> Optional[str]:
    """
    Detects undated task intent. Returns task text or None.
    Examples: "tengo que revisar X", "pendiente: X", "tarea: X"
    """
    # Discard if it has a time — that's a regular reminder
    if re.search(r'\ba las?\s+\d{1,2}([:\s]|$)', lowered):
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
        r'^(?:eva[,\s]+)?crear?\s+(?:un\s+)?(?:recordatorio|tarea|nota)\s+(?:para\s+|de\s+|sobre\s+)?(.+)$',
        r'^(?:eva[,\s]+)?crea\s+(?:un\s+)?(?:recordatorio|tarea|nota)\s+(?:para\s+|de\s+)?(.+)$',
        r'^(?:eva[,\s]+)?guarda\s+(?:esto|una?\s+nota)[:\s]+(.+)$',
        r'^(?:eva[,\s]+)?recu[eé]rdame[,\s]+(?:que\s+)?(.+)$',
    ]

    for pattern in patterns:
        m = re.match(pattern, lowered, re.IGNORECASE)
        if m:
            task = m.group(1).strip()
            if len(task) >= 4:
                return task
    return None


# ── Cancel / Edit extraction ──────────────────────────────────────────────

def extract_cancel_task(lowered: str) -> Optional[str]:
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
                if re.match(r'^(?:el\s+)?\d+$', captured):
                    return None
                return captured
            return ""
    return None


def extract_edit_command(lowered: str) -> Optional[tuple[int, dict]]:
    """
    Detects edit commands by ID. Returns (reminder_id, updates) or None.
    Examples: "cambia el 28 a las 11:00", "renombra el 7 a revisar correos"
    """
    edit_keywords = (
        "cambia", "cambiar", "mueve", "mover", "edita", "editar",
        "actualiza", "actualizar", "renombra", "renombrar", "modifica", "modificar",
    )
    if not any(w in lowered for w in edit_keywords):
        return None

    id_match = re.search(r'\b(\d{1,6})\b', lowered)
    if not id_match:
        return None

    reminder_id = int(id_match.group(1))
    updates: dict = {}

    time_match = re.search(r'a\s+las?\s+(\d{1,2}):(\d{2})', lowered)
    if time_match:
        updates["hour"]   = int(time_match.group(1))
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


# ── Snooze parsing ────────────────────────────────────────────────────────

def _extract_snooze_note(text: str) -> tuple[str, Optional[str]]:
    """
    Split time expression from optional context note.
    "a las 13:00, confirmar con Luis" → ("a las 13:00", "confirmar con Luis")
    "en 10 minutos" → ("en 10 minutos", None)
    """
    m = re.search(r',\s*(.+)$', text)
    if m:
        context = m.group(1).strip()
        time_part = text[:m.start()].strip()
        if len(context.split()) >= 2:
            return time_part, context
    return text, None


def _parse_snooze(lowered: str) -> Optional[timedelta]:
    """
    Detect postpone intent. Returns timedelta or None.
    Covers: "en 10 minutos", "en 1 hora", "mañana", "luego",
            "a las 13:00", "para mañana a las 9"
    """
    norm = norm_ascii(lowered)
    now  = datetime.now(TZ)

    m = re.match(r'^(?:en\s+)?(\d+)\s+minutos?$', norm)
    if m:
        return timedelta(minutes=int(m.group(1)))

    m = re.match(r'^(?:en\s+)?(\d+)\s+horas?$', norm)
    if m:
        return timedelta(hours=int(m.group(1)))

    if re.match(r'^(?:en\s+)?media\s+hora$', norm):
        return timedelta(minutes=30)

    if re.match(r'^en\s+un\s+(?:rato|momento)$', norm):
        return timedelta(minutes=15)

    if norm in ("manana", "tomorrow"):
        return timedelta(hours=24)

    if norm in ("luego", "despues", "ahora no", "mas tarde", "ahorita no"):
        return timedelta(hours=1)

    # "a las HH:MM" optionally followed by "solo hoy", "para hoy", "hoy" etc.
    # Use search instead of match so it finds the time anywhere in the string
    m = re.search(r'a\s+las?\s+(\d{1,2})(?::(\d{2}))?', norm)
    if m:
        h    = int(m.group(1))
        mins = int(m.group(2)) if m.group(2) else 0
        target = now.replace(hour=h, minute=mins, second=0, microsecond=0)
        # "solo hoy" / "para hoy" → don't advance to next day even if past
        _force_today = bool(re.search(r'\b(?:solo\s+)?hoy\b', norm))
        if target <= now and not _force_today:
            target += timedelta(days=1)
        return target - now

    m = re.match(
        r'^(?:para\s+)?(?:hoy|manana|mañana)?\s*(?:a\s+las?\s+)?(\d{1,2})(?::(\d{2}))?\s*(?:en\s+punto)?$',
        norm,
    )
    if m and m.group(1):
        h    = int(m.group(1))
        mins = int(m.group(2)) if m.group(2) else 0
        manana = "manana" in norm or "mañana" in lowered
        target = now.replace(hour=h, minute=mins, second=0, microsecond=0)
        if manana:
            target += timedelta(days=1)
        elif target <= now:
            target += timedelta(days=1)
        return target - now

    return None


# ── Response builders ─────────────────────────────────────────────────────

def build_list_reply(active: list, awaiting: list) -> str:
    if not active and not awaiting:
        return "📋 No tienes recordatorios activos."

    lines = []

    if active:
        lines.append(f"📋 *Próximos recordatorios ({len(active)}):*")
        for r in active:
            local_dt = to_local(r.remind_at)
            dt_str   = local_dt.strftime("%d/%m %H:%M") if local_dt else "sin hora"
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
            dt_str   = local_dt.strftime("%d/%m %H:%M") if local_dt else "sin hora"
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


def build_confirmation_text_from_parsed(
    source_text: str,
    parsed: dict,
    reminder_id: int | None = None,
) -> str:
    remind_at_local = to_local(parsed["remind_at"])
    now_local = datetime.now(TZ)
    DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]

    if remind_at_local.date() == now_local.date():
        date_str = f"hoy a las {remind_at_local.strftime('%H:%M')}"
    elif remind_at_local.date() == (now_local + timedelta(days=1)).date():
        date_str = f"mañana a las {remind_at_local.strftime('%H:%M')}"
    else:
        date_str = f"el {DIAS[remind_at_local.weekday()]} {remind_at_local.strftime('%d/%m')} a las {remind_at_local.strftime('%H:%M')}"

    remind_time_str = remind_at_local.strftime("%H:%M")
    task_text = parsed["task_text"]
    id_hint   = f" [{reminder_id}]" if reminder_id else ""

    if parsed.get("mode") == "before_time":
        minutes_before   = parsed.get("minutes_before")
        target_time_text = parsed.get("target_time_text")
        if minutes_before is not None and target_time_text:
            base = f"✅ Anotado{id_hint}: te aviso a las {remind_time_str} ({minutes_before} min antes de las {target_time_text})."
        else:
            base = f'✅ "{task_text}" — {date_str}.{id_hint}'

    elif parsed.get("mode") == "interval_minutes":
        interval = parsed.get("repeat_every_minutes", 0)
        stop_at  = parsed.get("stop_at")
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
        dia  = DIAS[remind_at_local.weekday()]
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

    correction_hint = '\n_Si la hora es incorrecta responde "no, a las HH:MM"_'

    if parsed.get("is_persistent"):
        repeat_every_minutes = parsed.get("repeat_every_minutes") or 2
        stop_at = parsed.get("stop_at")
        if stop_at:
            stop_at_local = to_local(stop_at)
            return (
                f"{base}\n"
                f"🔁 Repetiré cada {repeat_every_minutes} min "
                f'hasta las {stop_at_local.strftime("%H:%M")} o hasta "listo".'
            )
        return (
            f"{base}\n"
            f'🔁 Repetiré cada {repeat_every_minutes} min hasta "listo".'
        )

    return f"{base}{correction_hint}"