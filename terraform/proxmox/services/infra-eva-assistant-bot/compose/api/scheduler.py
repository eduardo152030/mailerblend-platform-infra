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


async def humanize_task_message(task_text: str, retry_count: int = 0,
                                is_last: bool = False) -> str:
    """
    Usa Claude para transformar task_text en un mensaje natural en español.
    Ejemplos:
      "Lavar los dientes a los hijos" → "lavarles los dientes a los niños"
      "Fichar la salida" → "fichar la salida"
      "Revisar el servidor" → "revisar el servidor"
    """
    import httpx as _hx
    import os as _os
    import json as _json

    ANTHROPIC_API_KEY = _os.getenv("ANTHROPIC_API_KEY", "")
    if not ANTHROPIC_API_KEY:
        return task_text  # fallback sin API

    tone_hint = ""
    if is_last:
        tone_hint = "Es el último aviso antes de que expire."
    elif retry_count >= 3:
        tone_hint = "Lleva varios avisos sin respuesta."
    elif retry_count == 0:
        tone_hint = "Es el primer aviso."

    prompt = (
        f"Transforma esta tarea en una frase natural en español para un recordatorio de Telegram. "
        f"Usa español coloquial real, no formal. "
        f"Si hay 'a los hijos/niños' usa pronombre indirecto (lavarles, recordarles). "
        f"Devuelve SOLO la frase transformada, sin comillas, sin explicación. "
        f"Máximo 8 palabras. {tone_hint}\n\n"
        f"Tarea: {task_text}"
    )

    try:
        async with _hx.AsyncClient(timeout=5) as c:
            r = await c.post(
                "https://api.anthropic.com/v1/messages",
                headers={"x-api-key": ANTHROPIC_API_KEY,
                         "anthropic-version": "2023-06-01",
                         "content-type": "application/json"},
                json={"model": "claude-haiku-4-5-20251001",
                      "max_tokens": 50,
                      "messages": [{"role": "user", "content": prompt}]}
            )
            if r.status_code == 200:
                text = r.json()["content"][0]["text"].strip().strip('"').strip("'")
                return text if text else task_text
    except Exception as exc:
        print(f"[scheduler] humanize error: {exc}")
    return task_text


async def build_due_text_ai(reminder: Reminder) -> str:
    """Versión mejorada de build_due_text con humanización por IA."""
    notes = getattr(reminder, "notes", None)
    note_str = f"\n📝 {notes}" if notes else ""
    rid = reminder.id
    retry = getattr(reminder, "retry_count", 0) or 0

    # Detectar si es el último aviso
    is_last = False
    if getattr(reminder, "stop_at", None) and getattr(reminder, "repeat_every_minutes", None):
        from datetime import datetime
        from zoneinfo import ZoneInfo
        import os
        _tz = ZoneInfo(os.getenv("TIMEZONE", "Europe/Madrid"))
        _now = datetime.now(_tz)
        _stop = reminder.stop_at
        if _stop.tzinfo is None:
            _stop = _stop.replace(tzinfo=_tz)
        minutes_left = (_stop - _now).total_seconds() / 60
        is_last = 0 < minutes_left <= reminder.repeat_every_minutes

    task = await humanize_task_message(reminder.task_text, retry, is_last)

    if getattr(reminder, "awaiting_ack", False):
        if is_last:
            return f'⚡ Último aviso: {task} [{rid}].{note_str}'
        if retry <= 1:
            return f'👆 Oye, pendiente: {task} [{rid}].{note_str}'
        elif retry == 2:
            return f'🔔 {task} [{rid}] — ¿ya?{note_str}'
        elif retry == 3:
            return f'⏰ Van {retry} avisos. {task} [{rid}].{note_str}'
        else:
            return f'🔔 #{retry}: {task} [{rid}].{note_str}'

    return f'⏰ {task} [{rid}]. Di "listo" cuando lo hayas hecho.{note_str}'





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


async def check_content_publication_reminders(db, send_fn) -> int:
    """
    Revisa tarjetas de contenido con fecha de publicación en las próximas 24h.
    Si status != Publicado → avisa por Telegram.
    """
    import httpx as _hx, json as _json, os as _os
    from datetime import timedelta

    FOCALBOARD_URL   = _os.getenv("FOCALBOARD_URL", "")
    FOCALBOARD_TOKEN = _os.getenv("FOCALBOARD_TOKEN", "")
    CONTENT_BOARD_ID = _os.getenv("FOCALBOARD_CONTENT_BOARD_ID", "bbhzrrkbxubgm8brd7bmoinekbr")

    if not FOCALBOARD_TOKEN:
        return 0

    now = datetime.now(TZ)
    tomorrow_start = now.replace(hour=0, minute=0, second=0) + timedelta(days=1)
    tomorrow_end   = tomorrow_start + timedelta(days=1)

    sent = 0
    try:
        async with _hx.AsyncClient(timeout=10) as client:
            r = await client.get(
                f"{FOCALBOARD_URL}/api/v2/boards/{CONTENT_BOARD_ID}/blocks?type=card",
                headers={"Authorization": f"Bearer {FOCALBOARD_TOKEN}",
                         "X-Requested-With": "XMLHttpRequest"}
            )
            if r.status_code != 200:
                return 0
            cards = r.json()

        for card in cards:
            props = card.get("fields", {}).get("properties", {})
            status = props.get("content_status_001", "")
            if status == "copt_publicado":
                continue

            fecha_raw = props.get("content_fechapub_001")
            if not fecha_raw:
                continue
            try:
                if isinstance(fecha_raw, str):
                    fecha_obj = _json.loads(fecha_raw)
                else:
                    fecha_obj = fecha_raw
                pub_ts_ms = fecha_obj.get("from", 0)
                if not pub_ts_ms:
                    continue
                pub_dt = datetime.fromtimestamp(pub_ts_ms / 1000, tz=TZ)
                if not (tomorrow_start <= pub_dt <= tomorrow_end):
                    continue
            except Exception:
                continue

            # Limpiar título — puede contener URLs o saltos de línea
            import re as _re_title
            title = card.get("title", "Sin título")
            title = title.split("\n")[0].strip()  # solo primera línea
            title = _re_title.sub(r'https?://\S+', '', title).strip()  # quitar URLs
            title = _re_title.sub(r'\s+[↻—–-].*$', '', title).strip()  # quitar sufijos de fecha
            if not title:
                title = "Sin título"
            formato_raw = props.get("content_formato_001", "")
            formato_map = {
                "copt_youtube": "YouTube",
                "copt_shortreel": "Short/Reel",
                "copt_linkedin": "LinkedIn"
            }
            # Soportar tanto string (legacy) como array (nuevo multiSelect)
            if isinstance(formato_raw, list):
                formatos = [formato_map.get(f, f) for f in formato_raw if f]
            elif formato_raw:
                formatos = [formato_map.get(formato_raw, formato_raw)]
            else:
                formatos = []
            formato_str = f" en {' + '.join(formatos)}" if formatos else ""

            users = db.execute(select(User)).scalars().all()
            for user in users:
                if not user.telegram_chat_id:
                    continue
                msg = f"📅 Mañana tienes que publicar{formato_str}:\n\"{title}\"\n\nRecuerda tenerlo listo antes de las 09:00."
                try:
                    await send_fn(user.telegram_chat_id, msg)
                    sent += 1
                except Exception as exc:
                    print(f"[content_reminder] error: {exc}")
    except Exception as exc:
        print(f"[content_reminder] error: {exc}")

    return sent


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