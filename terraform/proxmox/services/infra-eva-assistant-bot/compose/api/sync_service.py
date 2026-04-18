"""
sync_service.py — Sincronización bidireccional EVA ↔ Focalboard

Usa la propiedad "Status EVA" (id: eva_status_prop) añadida al board
con opciones fijas mapeadas a los estados de EVA.

Arranque: python sync_service.py
"""

import asyncio
import os
import traceback
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import httpx
from sqlalchemy import select, text

from db import SessionLocal
from models import Reminder, User, Event
from telegram_service import send_message
from scheduler import to_local

TZ = ZoneInfo(os.getenv("TIMEZONE", "Europe/Madrid"))
POLL_INTERVAL   = int(os.getenv("SYNC_POLL_SECONDS", "60"))
FOCALBOARD_URL  = os.getenv("FOCALBOARD_URL", "http://focalboard:8000")
FOCALBOARD_TOKEN   = os.getenv("FOCALBOARD_TOKEN", "")
FOCALBOARD_BOARD_ID = os.getenv("FOCALBOARD_BOARD_ID", "")

# IDs fijos de la propiedad "Status EVA" creada en el board
STATUS_PROP_ID = "aevastatus00000000000000001"
DATE_PROP_ID   = "a14y4uzprb1maieayt1ouhca47o"
TEXT_PROP_ID   = "a6bxuk4rgxp7wn6bashiadwaiiy"  # propiedad "Texto" para notas
URL_PROP_ID    = "asztuket5mjeeongrzooyx5utbo"   # propiedad "URL"
PRIORITY_PROP_ID = "ann9q8kbmc67mb7p4d8xrmma6rr"  # propiedad "Prioridad"
PRIORITY_OPTIONS = {
    "P0": "akgjwzzkom6j5hnqkw5nxaq4pmo",  # Critical
    "P1": "a44z9q4cj9jamiqip5gih6okzco",  # High
    "P2": "aqtsqbngmejgxwswgciahqubfoo",  # Moderate
    "P3": "argk36ea34napsf8dq78d4pg8go",  # Low
    "P4": "auoqqox58bui398gu1itti85d9a",  # Negligible
}
PRIORITY_DEFAULT = "P3"  # Por defecto: Low
# Inverso: option_id → status EVA
OPTION_TO_STATUS = {
    "aoptpendiente00000000000001":  "scheduled",
    "aoptenviado000000000000001":   "sent",
    "aoptcompletado0000000000001":  "completed",
    "aoptcancelado00000000000001":  "cancelled",
    "atknam74n43b9rezq13w9tz8dsc":  "in_progress",
}
STATUS_OPTIONS = {
    "scheduled":   "aoptpendiente00000000000001",
    "pending":     "aoptpendiente00000000000001",
    "sent":        "aoptenviado000000000000001",
    "completed":   "aoptcompletado0000000000001",
    "cancelled":   "aoptcancelado00000000000001",
    "expired":     "aoptcancelado00000000000001",
    "in_progress": "atknam74n43b9rezq13w9tz8dsc",
}


def _h() -> dict:
    return {
        "Authorization": f"Bearer {FOCALBOARD_TOKEN}",
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest",
    }


# ══════════════════════════════════════════
# EVA → FOCALBOARD
# ══════════════════════════════════════════

async def fb_create_card(reminder: Reminder, user: User) -> str | None:
    import time
    import uuid

    local_dt = to_local(reminder.remind_at)
    due_str  = local_dt.strftime("%d/%m %H:%M") if local_dt else ""

    recurrence = ""
    if reminder.recurrence_type == "weekly":
        recurrence = f" ↻ {reminder.recurrence_value}"
    elif reminder.recurrence_type == "weekdays":
        recurrence = " ↻ lab"
    elif reminder.is_persistent and reminder.repeat_every_minutes:
        recurrence = f" ↻ {reminder.repeat_every_minutes}min"

    opt_id = STATUS_OPTIONS.get(reminder.status, "opt_pendiente")
    now_ms = int(time.time() * 1000)
    card_id = uuid.uuid4().hex[:26]  # Focalboard usa IDs de 26 chars

    title = f"{reminder.task_text}{recurrence}"
    if due_str:
        title += f" — {due_str}"

    # Focalboard date format: stringified JSON — {"from": epoch_ms}
    properties = {STATUS_PROP_ID: opt_id}
    if local_dt:
        import json as _json
        properties[DATE_PROP_ID] = _json.dumps({"from": int(local_dt.timestamp() * 1000)})
    # Notas opcionales del usuario → propiedad "Texto"
    notes = getattr(reminder, "notes", None)
    if notes:
        import re as _re
        _url_match = _re.search(r'https?://\S+', notes)
        if _url_match:
            properties[URL_PROP_ID] = _url_match.group(0)
            _remaining = notes.replace(_url_match.group(0), "").strip().strip(",").strip()
            if _remaining:
                properties[TEXT_PROP_ID] = _remaining
        else:
            properties[TEXT_PROP_ID] = notes

    # Prioridad — inferida por IA o guardada en el reminder
    priority_key = getattr(reminder, "priority", None) or PRIORITY_DEFAULT
    if priority_key in PRIORITY_OPTIONS:
        properties[PRIORITY_PROP_ID] = PRIORITY_OPTIONS[priority_key]

    block = {
        "id": card_id,
        "type": "card",
        "schema": 1,
        "boardId": FOCALBOARD_BOARD_ID,
        "parentId": FOCALBOARD_BOARD_ID,
        "title": title,
        "createAt": now_ms,
        "updateAt": now_ms,
        "deleteAt": 0,
        "fields": {
            "isTemplate": False,
            "contentOrder": [],
            "properties": properties,
        },
    }

    url = f"{FOCALBOARD_URL}/api/v2/boards/{FOCALBOARD_BOARD_ID}/blocks"
    async with httpx.AsyncClient(timeout=10) as c:
        r = await c.post(url, headers=_h(), json=[block])
        if r.status_code in (200, 201):
            data = r.json()
            cid = data[0]["id"] if isinstance(data, list) else data.get("id", card_id)
            print(f"[sync] ✅ card {cid} ← reminder {reminder.id} '{reminder.task_text}'")
            return cid
        print(f"[sync] ❌ create card failed {r.status_code}: {r.text[:300]}")
        return None


async def fb_update_card_status(card_id: str, status: str, remind_at=None,
                               notes: str | None = None, url: str | None = None,
                               priority: str | None = None) -> bool:
    """
    Siempre envía todas las properties conocidas para evitar que Focalboard
    borre las que no se incluyen (no hace merge, reemplaza el objeto completo).
    """
    props = {}
    props[STATUS_PROP_ID] = STATUS_OPTIONS.get(status, "aoptpendiente00000000000001")
    if remind_at:
        local_dt = to_local(remind_at)
        if local_dt and local_dt.year < 2099:
            import json as _json
            props[DATE_PROP_ID] = _json.dumps({"from": int(local_dt.timestamp() * 1000)})
    if notes is not None:
        props[TEXT_PROP_ID] = notes
    if url is not None:
        props[URL_PROP_ID] = url
    if priority is not None and priority in PRIORITY_OPTIONS:
        props[PRIORITY_PROP_ID] = PRIORITY_OPTIONS[priority]
    fb_url = f"{FOCALBOARD_URL}/api/v2/boards/{FOCALBOARD_BOARD_ID}/blocks/{card_id}"
    async with httpx.AsyncClient(timeout=10) as c:
        r = await c.patch(fb_url, headers=_h(), json={"updatedFields": {"properties": props}})
        ok = r.status_code in (200, 204)
        if ok:
            print(f"[sync] ✅ card {card_id} → {status}")
        else:
            print(f"[sync] ❌ card {card_id} update failed {r.status_code}: {r.text[:100]}")
        return ok


# ══════════════════════════════════════════
# FOCALBOARD → EVA
# ══════════════════════════════════════════

_last_poll: datetime = datetime.now(timezone.utc)


async def fb_get_cards_since(since: datetime) -> list[dict]:
    url = f"{FOCALBOARD_URL}/api/v2/boards/{FOCALBOARD_BOARD_ID}/blocks?type=card"
    async with httpx.AsyncClient(timeout=15) as c:
        r = await c.get(url, headers=_h())
        if r.status_code != 200:
            return []
        cards = r.json()
        since_ms = since.timestamp() * 1000
        return [card for card in cards if card.get("updateAt", 0) > since_ms]


# ══════════════════════════════════════════
# CICLOS DE SYNC
# ══════════════════════════════════════════

async def sync_new_reminders() -> int:
    if not FOCALBOARD_TOKEN or not FOCALBOARD_BOARD_ID:
        return 0
    db = SessionLocal()
    synced = 0
    try:
        db.rollback()
        # Doble check: solo reminders SIN card_id Y que no estén ya en Focalboard
        from datetime import timedelta as _td
        _cutoff = datetime.now(TZ) - _td(seconds=10)
        rows = db.execute(
            select(Reminder)
            .where(Reminder.focalboard_card_id.is_(None))
            .where(Reminder.status.in_(["scheduled", "pending", "sent"]))
            .where(Reminder.created_at < _cutoff)
        ).scalars().all()
        rows = rows[:10]

        for r in rows:
            try:
                user = db.execute(select(User).where(User.id == r.user_id)).scalar_one_or_none()
                if not user:
                    continue
                cid = await fb_create_card(r, user)
                if cid:
                    r.focalboard_card_id = cid
                    r.focalboard_synced_at = datetime.now(TZ)
                    _log(db, "reminder", r.id, "eva_to_fb", "create", cid)
                    db.commit()
                    synced += 1
            except Exception as exc:
                db.rollback()
                print(f"[sync] error reminder {r.id}: {exc}")
    except Exception as exc:
        db.rollback()
        print(f"[sync] sync_new_reminders error: {exc}")
    finally:
        db.close()
    return synced


async def sync_status_changes() -> int:
    if not FOCALBOARD_TOKEN or not FOCALBOARD_BOARD_ID:
        return 0
    db = SessionLocal()
    synced = 0
    try:
        rows = db.execute(
            select(Reminder)
            .where(Reminder.focalboard_card_id.isnot(None))
            .where(Reminder.status.in_(["sent", "completed", "cancelled", "expired"]))
            # NOTE: "in_progress" is excluded — it's managed from Focalboard UI
            # "scheduled" and "pending" are excluded — they are the default state
        ).scalars().all()

        for r in rows:
            try:
                # Skip if reminder was recently synced FROM Focalboard (avoid overwrite loop)
                if r.focalboard_synced_at:
                    from datetime import timedelta as _td2
                    _age = (datetime.now(TZ) - r.focalboard_synced_at.replace(tzinfo=TZ) if r.focalboard_synced_at.tzinfo is None else datetime.now(TZ) - r.focalboard_synced_at).total_seconds()
                    if _age < 120:  # skip if synced from FB in last 2 minutes
                        continue
                ok = await fb_update_card_status(r.focalboard_card_id, r.status, r.remind_at, getattr(r, "notes", None), getattr(r, "url", None), getattr(r, "priority", None))
                if ok:
                    r.focalboard_synced_at = datetime.now(TZ)
                    _log(db, "reminder", r.id, "eva_to_fb", "update", r.focalboard_card_id)
                    synced += 1
            except Exception as exc:
                print(f"[sync] error update {r.focalboard_card_id}: {exc}")

        db.commit()
    finally:
        db.close()
    return synced


async def sync_recurring_dates() -> int:
    """
    Sincroniza la propiedad Fecha de Focalboard para recordatorios recurrentes/persistentes.
    Estos tienen status='scheduled' y nunca pasan por sync_status_changes.
    También hace backfill de tarjetas con fecha vacía en Focalboard.
    """
    if not FOCALBOARD_TOKEN or not FOCALBOARD_BOARD_ID:
        return 0
    db = SessionLocal()
    synced = 0
    try:
        # Todos los recurrentes/persistentes con focalboard_card_id
        rows = db.execute(
            select(Reminder)
            .where(Reminder.focalboard_card_id.isnot(None))
            .where(Reminder.status.in_(["scheduled", "pending"]))
            .where(
                (Reminder.recurrence_type.isnot(None)) |
                (Reminder.weekdays_only.is_(True)) |
                (Reminder.is_persistent.is_(True))
            )
        ).scalars().all()

        for r in rows:
            if not r.remind_at:
                continue
            local_dt = to_local(r.remind_at)
            if not local_dt or local_dt.year >= 2099:
                continue
            try:
                import json as _json
                date_val = _json.dumps({"from": int(local_dt.timestamp() * 1000)})
                props = {
                    STATUS_PROP_ID: STATUS_OPTIONS.get(r.status, "aoptpendiente00000000000001"),
                    DATE_PROP_ID: date_val,
                }
                if getattr(r, "notes", None):
                    props[TEXT_PROP_ID] = r.notes
                if getattr(r, "url", None):
                    props[URL_PROP_ID] = r.url
                if getattr(r, "priority", None) and r.priority in PRIORITY_OPTIONS:
                    props[PRIORITY_PROP_ID] = PRIORITY_OPTIONS[r.priority]

                fb_url = f"{FOCALBOARD_URL}/api/v2/boards/{FOCALBOARD_BOARD_ID}/blocks/{r.focalboard_card_id}"
                async with httpx.AsyncClient(timeout=8) as c:
                    resp = await c.patch(fb_url, headers=_h(),
                                         json={"updatedFields": {"properties": props}})
                    if resp.status_code in (200, 204):
                        synced += 1
                        print(f"[sync] ✅ fecha updated for recurring reminder {r.id} → {local_dt.strftime('%d/%m %H:%M')}")
            except Exception as exc:
                print(f"[sync] fecha update error reminder {r.id}: {exc}")

    except Exception as exc:
        print(f"[sync] sync_recurring_dates error: {exc}")
    finally:
        db.close()
    return synced


async def sync_from_focalboard() -> int:
    """
    Sincroniza cambios de Focalboard → EVA.
    Detecta:
      - Status cambiado (Completado/Cancelado/Pendiente) → actualiza reminder + notifica Telegram
      - Fecha cambiada → actualiza remind_at del reminder
      - Texto cambiado → actualiza notes del reminder
      - Título cambiado → actualiza task_text del reminder
    """
    global _last_poll
    if not FOCALBOARD_TOKEN or not FOCALBOARD_BOARD_ID:
        return 0

    since = _last_poll
    _last_poll = datetime.now(timezone.utc)

    try:
        cards = await fb_get_cards_since(since)
    except Exception as exc:
        print(f"[sync] fb fetch error: {exc}")
        return 0

    if not cards:
        return 0

    db = SessionLocal()
    synced = 0
    try:
        db.rollback()
        for card in cards:
            cid = card.get("id")
            if not cid:
                continue

            reminder = db.execute(
                select(Reminder).where(Reminder.focalboard_card_id == cid)
            ).scalar_one_or_none()

            # Tarjeta sin reminder asociado — adoptarla si tiene status relevante
            if not reminder:
                props_check = card.get("fields", {}).get("properties", {})
                opt_check = props_check.get(STATUS_PROP_ID)
                status_check = OPTION_TO_STATUS.get(opt_check)
                if status_check in ("completed", "cancelled"):
                    # Buscar el usuario por defecto (el único o el primero)
                    from models import User as _User
                    default_user = db.execute(select(_User).limit(1)).scalars().first()
                    if default_user:
                        # Crear reminder para poder rastrear este cambio
                        fb_title = card.get("title", "Tarea de Focalboard")
                        import re as _re
                        fb_title_clean = _re.sub(r"\s+[↻—–-]\s+.*$", "", fb_title).strip()
                        reminder = Reminder(
                            user_id=default_user.id,
                            source_text=fb_title_clean,
                            task_text=fb_title_clean,
                            remind_at=datetime.now(TZ).replace(year=2099),
                            status="pending",
                            focalboard_card_id=cid,
                            focalboard_synced_at=now,
                        )
                        db.add(reminder)
                        db.flush()  # get the ID
                        print(f"[sync] adopted orphan card {cid} → reminder {reminder.id}")
                    else:
                        continue
                else:
                    continue

            props = card.get("fields", {}).get("properties", {})
            now = datetime.now(TZ)
            changed = False
            notify_msg = None

            # ── 1. STATUS ──────────────────────────────────────────────────
            opt_id = props.get(STATUS_PROP_ID)
            new_status = OPTION_TO_STATUS.get(opt_id)

            if new_status and new_status != reminder.status:
                old_status = reminder.status

                # Aplicar el nuevo status — TODOS los cambios se sincronizan
                reminder.status = new_status
                reminder.awaiting_ack = False

                # Acciones específicas según el nuevo status
                if new_status == "completed":
                    reminder.completed_at = now
                    reminder.acked_at = now
                    db.add(Event(user_id=reminder.user_id, event_type="reminder_completed",
                                 event_value=str(reminder.id), source="focalboard",
                                 payload={"card_id": cid, "from": old_status}))
                    notify_msg = f'✅ "{reminder.task_text}" completado desde Focalboard [{reminder.id}]'

                elif new_status == "cancelled":
                    reminder.cancelled_at = now
                    reminder.error_message = "cancelled_via_focalboard"
                    db.add(Event(user_id=reminder.user_id, event_type="reminder_cancelled",
                                 event_value=str(reminder.id), source="focalboard",
                                 payload={"card_id": cid, "from": old_status}))
                    notify_msg = f'🗑️ "{reminder.task_text}" cancelado desde Focalboard [{reminder.id}]'

                elif new_status == "scheduled":
                    # Reactivación o movimiento a Pendiente
                    reminder.completed_at = None
                    reminder.cancelled_at = None
                    db.add(Event(user_id=reminder.user_id, event_type="reminder_reactivated",
                                 event_value=str(reminder.id), source="focalboard",
                                 payload={"card_id": cid, "from": old_status}))
                    if old_status in ("completed", "cancelled"):
                        notify_msg = f'🔄 "{reminder.task_text}" reactivado desde Focalboard [{reminder.id}]'
                    else:
                        notify_msg = f'📋 "{reminder.task_text}" movido a Pendiente [{reminder.id}]'

                elif new_status == "in_progress":
                    db.add(Event(user_id=reminder.user_id, event_type="reminder_in_progress",
                                 event_value=str(reminder.id), source="focalboard",
                                 payload={"card_id": cid, "from": old_status}))
                    notify_msg = f'🔵 "{reminder.task_text}" en progreso [{reminder.id}]'

                elif new_status == "sent":
                    # Marcado como Enviado manualmente desde Focalboard
                    db.add(Event(user_id=reminder.user_id, event_type="reminder_sent_manual",
                                 event_value=str(reminder.id), source="focalboard",
                                 payload={"card_id": cid, "from": old_status}))
                    notify_msg = f'📨 "{reminder.task_text}" marcado como Enviado desde Focalboard [{reminder.id}]'

                else:
                    # Cualquier otro cambio de status
                    db.add(Event(user_id=reminder.user_id, event_type="reminder_status_changed",
                                 event_value=str(reminder.id), source="focalboard",
                                 payload={"card_id": cid, "from": old_status, "to": new_status}))
                    notify_msg = f'🔀 "{reminder.task_text}" → {new_status} [{reminder.id}]'

                # Asegurar que el task_text no esté vacío en el mensaje
                task_display = reminder.task_text or card.get("title", "")[:40]
                import re as _re2
                task_display = _re2.sub(r"\s+[↻—–-]\s+.*$", "", task_display).strip()
                if notify_msg:
                    notify_msg = notify_msg.replace(f'"{reminder.task_text}"', f'"{task_display}"')
                print(f"[sync] ✅ reminder {reminder.id} {old_status}→{new_status} via Focalboard: {task_display}")
                changed = True

            # ── 2. FECHA — sincronizar remind_at si cambió en Focalboard ──
            import json as _json
            fecha_raw = props.get(DATE_PROP_ID)
            if fecha_raw:
                try:
                    if isinstance(fecha_raw, str):
                        fecha_obj = _json.loads(fecha_raw)
                    else:
                        fecha_obj = fecha_raw
                    fb_ts_ms = fecha_obj.get("from", 0)
                    if fb_ts_ms:
                        fb_dt = datetime.fromtimestamp(fb_ts_ms / 1000, tz=TZ)
                        current_dt = to_local(reminder.remind_at) if reminder.remind_at else None
                        # Solo actualizar si la diferencia es > 2 minutos (evitar loops)
                        if not current_dt or abs((fb_dt - current_dt).total_seconds()) > 120:
                            old_dt = current_dt
                            reminder.remind_at = fb_dt
                            if reminder.status in ("completed", "cancelled"):
                                reminder.status = "scheduled"
                            changed = True
                            if not notify_msg:
                                days = ["lunes","martes","miércoles","jueves","viernes","sábado","domingo"]
                                day_str = f"{days[fb_dt.weekday()]} {fb_dt.strftime('%d/%m')}"
                                notify_msg = (f'📅 Fecha actualizada desde Focalboard: "{reminder.task_text}" [{reminder.id}]\n'
                                              f'Nueva fecha: {day_str} a las {fb_dt.strftime("%H:%M")}')
                            db.add(Event(user_id=reminder.user_id, event_type="reminder_rescheduled",
                                         event_value=str(reminder.id), source="focalboard",
                                         payload={"card_id": cid, "new_dt": fb_dt.isoformat()}))
                            print(f"[sync] ✅ reminder {reminder.id} rescheduled to {fb_dt} via Focalboard")
                except Exception as exc:
                    print(f"[sync] fecha parse error for card {cid}: {exc}")

            # ── 3. TEXTO — sincronizar notes/tags si cambió en Focalboard ──
            fb_texto = props.get(TEXT_PROP_ID)
            if fb_texto:
                import re as _re_t
                # Separar hashtags del texto libre
                _fb_tags_list = _re_t.findall(r'#[a-zA-Z]\w*', fb_texto)
                _fb_tags = " ".join(_fb_tags_list) if _fb_tags_list else None
                _fb_notes = _re_t.sub(r'\s*#[a-zA-Z]\w*', '', fb_texto).strip().strip("|").strip() or None

                if _fb_tags != getattr(reminder, "tags", None):
                    reminder.tags = _fb_tags
                    changed = True
                    print(f"[sync] ✅ reminder {reminder.id} tags updated: {_fb_tags}")

                if _fb_notes != getattr(reminder, "notes", None):
                    reminder.notes = _fb_notes
                    changed = True
                    print(f"[sync] ✅ reminder {reminder.id} notes updated: {_fb_notes}")

            # ── 3b. URL — sincronizar url si cambió en Focalboard ────────────
            fb_url_val = props.get(URL_PROP_ID)
            if fb_url_val and fb_url_val != getattr(reminder, "url", None):
                reminder.url = fb_url_val
                changed = True
                print(f"[sync] ✅ reminder {reminder.id} url updated via Focalboard")

            # ── 4. TÍTULO — sincronizar task_text si cambió en Focalboard ─
            fb_title = card.get("title", "").strip()
            # Limpiar el título de Focalboard (puede tener " — DD/MM HH:MM" al final)
            import re as _re
            fb_title_clean = _re.sub(r'\s+[↻—–-]\s+.*$', '', fb_title).strip()
            if (fb_title_clean and len(fb_title_clean) >= 3
                    and fb_title_clean.lower() != reminder.task_text.lower()
                    and len(fb_title_clean) < 200):
                # Solo actualizar si el cambio es sustancial (no solo espacios)
                old_task = reminder.task_text
                reminder.task_text = fb_title_clean
                changed = True
                print(f"[sync] ✅ reminder {reminder.id} task_text updated: '{old_task}' → '{fb_title_clean}'")

            if changed:
                reminder.focalboard_synced_at = now
                _log(db, "reminder", reminder.id, "fb_to_eva", "update", cid)
                db.commit()
                synced += 1

                # Notificar al usuario por Telegram si hay mensaje
                if notify_msg:
                    try:
                        user = db.execute(
                            select(User).where(User.id == reminder.user_id)
                        ).scalar_one_or_none()
                        if user and user.telegram_chat_id:
                            await send_message(user.telegram_chat_id, notify_msg)
                    except Exception as exc:
                        print(f"[sync] telegram notify error: {exc}")

    except Exception as exc:
        db.rollback()
        print(f"[sync] sync_from_focalboard error: {exc}")
        traceback.print_exc()
    finally:
        db.close()
    return synced


def _log(db, entity_type, entity_id, direction, action, focalboard_id, error=None):
    try:
        db.execute(text("""
            INSERT INTO sync_log (entity_type, entity_id, direction, action, focalboard_id, error)
            VALUES (:et, :eid, :dir, :act, :fbid, :err)
        """), {"et": entity_type, "eid": entity_id, "dir": direction,
               "act": action, "fbid": focalboard_id, "err": error})
    except Exception:
        pass


# ══════════════════════════════════════════
# LOOP
# ══════════════════════════════════════════

async def main_loop():
    print(f"[sync] Starting EVA ↔ Focalboard (poll {POLL_INTERVAL}s)")
    print(f"[sync] URL={FOCALBOARD_URL} board={FOCALBOARD_BOARD_ID}")
    if not FOCALBOARD_TOKEN:
        print("[sync] ⚠️  FOCALBOARD_TOKEN not set — sync disabled")

    while True:
        try:
            n1 = await sync_new_reminders()
            n2 = await sync_status_changes()
            n3 = await sync_from_focalboard()
            n4 = await sync_recurring_dates()
            if n1 or n2 or n3 or n4:
                print(f"[sync] cycle — new:{n1} status:{n2} fb→eva:{n3} dates:{n4}")
        except Exception as exc:
            print(f"[sync] unhandled: {exc}")
            traceback.print_exc()
        await asyncio.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    asyncio.run(main_loop())