"""
services/reminder_handlers.py
==============================
Business logic for Telegram reminder commands.

To debug:
- ACK / listo not working        → inspect handle_ack_command
- Cancel not working             → inspect handle_cancel_by_id / handle_cancel_command
- Snooze / move not working      → inspect handle_ack_command (snooze block)
- Edit not working               → inspect handle_edit_reminder
- Note not saving                → inspect handle_add_note
- Bulk delete not working        → inspect handle_bulk_cleanup
- List command empty/wrong       → inspect handle_list_command

No FastAPI imports here. No routes. Pure business logic + DB + Telegram send.
"""
import os
import re
import json
from datetime import datetime, timedelta

from sqlalchemy import select
from integrations import focalboard_client as fb

from db import SessionLocal
from models import User, Reminder, Message, Event
from telegram_service import send_message
from core.config import TZ
from utils.time_utils import to_local
from utils.text_utils import (
    _extract_snooze_note, _parse_snooze, build_list_reply,
)
from utils.tag_utils import (
    extract_tags, tags_str, remove_tags, merge_tags, build_text_prop,
)
from repositories import reminder_repository as rr
from repositories import message_repository as mr
from repositories import event_repository as er

RECENT_TASK_WINDOW_MINUTES = 30  # max age for "latest relevant task" in tag updates


# ── Shared helpers ────────────────────────────────────────────────────────

def _get_recent_context(db, user_id: int, limit: int = 5) -> list[dict]:
    """Return last N messages for conversational context."""
    return mr.get_recent(db, user_id, limit)


async def send_and_log(db, user_id: int, chat_id: int, text_out: str, message_type: str) -> None:
    """Send Telegram message and persist it to messages table."""
    await send_message(chat_id, text_out)
    mr.add(db, user_id, "outbound", text_out, message_type)
    db.commit()


async def handle_tag_update(
    db,
    user: User,
    chat_id: int,
    tags: list[str],
    task_id: int | None = None,
) -> dict:
    """
    Apply tags to a reminder without touching notes, URL, attachments,
    status, date, or priority.

    Target resolution order:
      1. Explicit task_id if provided ("196 #personal")
      2. Task ID from last EVA outbound message ("[196]" in text)
      3. Most recent reminder with a Focalboard card created in last 30 min
      4. If nothing found → ask user to specify ID

    Logs: [capture:tag] prefix for all steps.
    """
    from datetime import timedelta

    target = None

    # ── 1. Explicit ID ────────────────────────────────────────────────────
    if task_id is not None:
        target = rr.get_by_id_and_user(db, task_id, user.id)
        if not target:
            await send_and_log(db, user.id, chat_id,
                               f"❌ No encontré la tarea [{task_id}].",
                               "tag_update_not_found")
            return {"status": "ok", "action": "tag_update_not_found"}
        print(f"[capture:tag] target from explicit id={task_id}")

    # ── 2. ID from last EVA message ───────────────────────────────────────
    # Accept any reminder — including freshly created ones without a card yet
    # (sync creates the card within 60s, but tag update happens immediately)
    if not target:
        last_out = mr.get_last_outbound(db, user.id)
        if last_out:
            id_match = re.search(r'\[(\d+)\]', last_out.message_text)
            if id_match:
                candidate = rr.get_by_id_and_user(db, int(id_match.group(1)), user.id)
                if candidate:
                    target = candidate
                    print(f"[capture:tag] target from last message id={target.id} "
                          f"card={'yes' if target.focalboard_card_id else 'pending'}")

    # ── 3. Most recent card created in last 30 min ────────────────────────
    if not target:
        cutoff = datetime.now(TZ) - timedelta(minutes=RECENT_TASK_WINDOW_MINUTES)
        candidate = rr.get_last_with_card(db, user.id)
        if candidate and candidate.focalboard_card_id:
            # Check created_at is within window
            created = getattr(candidate, "focalboard_synced_at", None) or candidate.remind_at
            from utils.time_utils import to_local as _to_local
            created_local = _to_local(created)
            if created_local and created_local >= cutoff:
                target = candidate
                print(f"[capture:tag] target from recent card id={target.id} "
                      f"(within {RECENT_TASK_WINDOW_MINUTES}min window)")
            else:
                print(f"[capture:tag] most recent card id={candidate.id} is older than "
                      f"{RECENT_TASK_WINDOW_MINUTES}min — skipping")

    # ── 4. No target found ────────────────────────────────────────────────
    if not target:
        await send_and_log(db, user.id, chat_id,
                           f"No sé a qué tarea aplicar el tag. "
                           f"Dime el ID, por ejemplo: '196 {tags[0]}'",
                           "tag_update_no_target")
        return {"status": "ok", "action": "tag_update_no_target"}

    # ── Apply tags ────────────────────────────────────────────────────────
    existing_tags_str = target.tags or ""
    print(f"[capture:tag] existing tags='{existing_tags_str}' incoming={tags}")

    target.tags = merge_tags(existing_tags_str, tags)
    db.commit()
    print(f"[capture:tag] merged tags='{target.tags}' for reminder [{target.id}]")

    # ── Sync to Focalboard — preserve all existing properties ─────────────
    if target.focalboard_card_id and fb.is_configured():
        try:
            from sync_service import (STATUS_OPTIONS, STATUS_PROP_ID, TEXT_PROP_ID,
                                       URL_PROP_ID, DATE_PROP_ID, PRIORITY_PROP_ID,
                                       PRIORITY_OPTIONS)
            _props = {STATUS_PROP_ID: STATUS_OPTIONS.get(target.status,
                                                          "aoptpendiente00000000000001")}
            if target.remind_at:
                _local_dt = to_local(target.remind_at)
                if _local_dt and _local_dt.year < 2099:
                    _props[DATE_PROP_ID] = json.dumps(
                        {"from": int(_local_dt.timestamp() * 1000)})
            if getattr(target, "url", None):
                _props[URL_PROP_ID] = target.url
            _prio = getattr(target, "priority", "P3") or "P3"
            if _prio in PRIORITY_OPTIONS:
                _props[PRIORITY_PROP_ID] = PRIORITY_OPTIONS[_prio]
            # TEXT_PROP: notes take priority; fall back to tags display
            _current_tags = extract_tags(target.tags or "")
            _text_val = build_text_prop(target.notes, _current_tags)
            if _text_val:
                _props[TEXT_PROP_ID] = _text_val
            ok = await fb.update_card_properties(target.focalboard_card_id, _props)
            print(f"[capture:tag] focalboard update {'✅ ok' if ok else '❌ failed'} "
                  f"card={target.focalboard_card_id}")
        except Exception as exc:
            print(f"[capture:tag] focalboard error: {exc}")

    # ── Reply ─────────────────────────────────────────────────────────────
    tags_display = " ".join(tags)
    reply = f'🏷️ Tag añadido a "{target.task_text}" [{target.id}]: {tags_display}'
    await send_and_log(db, user.id, chat_id, reply, "tag_update_done")
    return {"status": "ok", "action": "tag_update_done",
            "reminder_id": target.id, "tags": target.tags}


# ── Reminder handlers ─────────────────────────────────────────────────────

async def handle_list_command(db, user: User, chat_id: int):
    """Handle 'lista mis recordatorios' and variants."""
    active  = rr.get_active_for_user(db, user.id)
    awaiting = rr.get_awaiting_ack_for_user(db, user.id)

    reply = build_list_reply(active, awaiting)
    await send_and_log(db, user.id, chat_id, reply, "reminders_list")
    return {"status": "ok", "action": "reminders_list_sent"}


async def handle_ack_command(db, user: User, chat_id: int, lowered: str):
    """Handle 'listo', 'ok', snooze expressions, and simple ack."""
    _thirty_min_ago = datetime.now(TZ) - timedelta(minutes=30)
    reminder = db.execute(
        select(Reminder)
        .where(Reminder.user_id == user.id)
        .where(
            (Reminder.awaiting_ack.is_(True)) |
            (Reminder.status == "sent") |
            (
                (Reminder.last_sent_at >= _thirty_min_ago) &
                (Reminder.status.in_(["sent", "scheduled"]))
            )
        )
        .order_by(Reminder.last_sent_at.desc().nullslast(), Reminder.id.desc())
        .limit(1)
    ).scalars().first()

    if not reminder:
        reply = "👌 No tengo ningún recordatorio pendiente de confirmación ahora mismo."
        await send_and_log(db, user.id, chat_id, reply, "ack_no_pending")
        return {"status": "ok", "action": "ack_no_pending"}

    # ── Snooze ──────────────────────────────────────────────────────────
    time_part, snooze_note = _extract_snooze_note(lowered)
    snooze_delta = _parse_snooze(time_part)
    if snooze_delta is not None:
        now = datetime.now(TZ)
        new_remind_at = now + snooze_delta
        reminder.remind_at  = new_remind_at
        reminder.status     = "scheduled"
        reminder.awaiting_ack = False

        if reminder.stop_at:
            old_stop = to_local(reminder.stop_at)
            old_remind = to_local(reminder.remind_at) if reminder.remind_at else None
            if old_remind:
                _ = old_stop - old_stop.replace(
                    hour=old_remind.hour, minute=old_remind.minute, second=0, microsecond=0)
            new_stop = new_remind_at.replace(
                hour=old_stop.hour, minute=old_stop.minute, second=0, microsecond=0)
            if new_stop <= new_remind_at:
                new_stop += timedelta(days=1)
            reminder.stop_at = new_stop

        if snooze_note and hasattr(reminder, "notes"):
            reminder.notes = snooze_note

        er.add(db, user.id, "reminder_snoozed", str(reminder.id),
               payload={"snooze_text": lowered,
                        "new_remind_at": new_remind_at.isoformat(),
                        "note": snooze_note})
        db.commit()
        dt_str = to_local(new_remind_at).strftime("%H:%M")
        reply = (f'Movido a las {dt_str}. Apuntado: "{snooze_note}"'
                 if snooze_note else f"Movido a las {dt_str}.")
        await send_and_log(db, user.id, chat_id, reply, "snooze_confirmation")
        return {"status": "ok", "action": "reminder_snoozed", "reminder_id": reminder.id}

    # ── ACK ──────────────────────────────────────────────────────────────
    now = datetime.now(TZ)
    reminder.acked_at    = now
    reminder.awaiting_ack = False
    reminder.ack_text    = lowered

    is_recurring = (
        reminder.recurrence_type is not None or
        reminder.weekdays_only or
        (reminder.is_persistent and reminder.repeat_every_minutes and reminder.stop_at is None)
    )

    if is_recurring:
        from scheduler import next_occurrence as _next_occ
        nxt = _next_occ(reminder)

        # Persistent with daily window — advance to next day manually
        if nxt is None and reminder.is_persistent and reminder.stop_at:
            _base = to_local(reminder.remind_at)
            _days = 1
            if reminder.weekdays_only:
                while (_base + timedelta(days=_days)).weekday() >= 5:
                    _days += 1
            _candidate = _base + timedelta(days=_days)
            _stop_base = to_local(reminder.stop_at)
            reminder.stop_at = _stop_base + timedelta(days=_days)
            nxt = _candidate

        if nxt:
            reminder.remind_at     = nxt
            reminder.status        = "scheduled"
            reminder.sent_at       = None
            reminder.last_sent_at  = None
            reminder.retry_count   = 0
            reminder.completed_at  = None
            if getattr(reminder, "focalboard_card_id", None):
                reminder.focalboard_synced_at = now
            er.add(db, user.id, "reminder_acked_rescheduled", str(reminder.id),
                   payload={"text": lowered, "next": nxt.isoformat()})
            db.commit()
            nxt_local = to_local(nxt)
            days = ["lunes","martes","miércoles","jueves","viernes","sábado","domingo"]
            reply = f'✅ Perfecto. Próximo aviso: {days[nxt_local.weekday()]} {nxt_local.strftime("%d/%m a las %H:%M")}.'
            await send_and_log(db, user.id, chat_id, reply, "ack_rescheduled")
            return {"status": "ok", "action": "reminder_acked_rescheduled", "reminder_id": reminder.id}

    # Non-recurring: complete
    reminder.completed_at = now
    reminder.status       = "completed"
    if getattr(reminder, "focalboard_card_id", None):
        reminder.focalboard_synced_at = now
    er.add(db, user.id, "reminder_completed", str(reminder.id),
           payload={"text": lowered})
    db.commit()
    reply = f'✅ Entendido. Marco como completado: "{reminder.task_text}".'
    await send_and_log(db, user.id, chat_id, reply, "ack_confirmation")
    return {"status": "ok", "action": "reminder_acknowledged", "reminder_id": reminder.id}


async def handle_cancel_command(db, user: User, chat_id: int, cancel_task: str):
    """Cancel reminder by text match."""
    rows = rr.get_cancellable_for_user(db, user.id)

    if not rows:
        await send_and_log(db, user.id, chat_id,
                           "📋 No tienes recordatorios activos para cancelar.", "cancel_none")
        return {"status": "ok", "action": "cancel_no_active"}

    target = rows[0] if cancel_task == "" else next(
        (r for r in rows if cancel_task.strip().lower() in (r.task_text or "").lower()), None)

    if not target:
        await send_and_log(db, user.id, chat_id,
                           "No encontré un recordatorio activo que coincida con ese texto.",
                           "cancel_not_found")
        return {"status": "ok", "action": "cancel_not_found"}

    now = datetime.now(TZ)
    target.status       = "cancelled"
    target.awaiting_ack = False
    target.cancelled_at = now
    target.error_message = "cancelled_by_user"
    er.add(db, user.id, "reminder_cancelled", str(target.id),
           payload={"task_match": cancel_task})
    db.commit()
    await send_and_log(db, user.id, chat_id,
                       f'🛑 He cancelado el recordatorio: "{target.task_text}".', "cancel_confirmation")
    return {"status": "ok", "action": "reminder_cancelled", "reminder_id": target.id}


async def handle_cancel_by_id(db, user: User, chat_id: int, reminder_id: int):
    """Cancel reminder by ID."""
    reminder = rr.get_by_id(db, reminder_id)

    if not reminder:
        await send_and_log(db, user.id, chat_id,
                           f"❌ No encontré ningún recordatorio con id {reminder_id}.",
                           "cancel_by_id_not_found")
        return {"status": "ok", "action": "cancel_by_id_not_found"}

    if reminder.status in ("cancelled", "completed"):
        await send_and_log(db, user.id, chat_id,
                           f"ℹ️ El recordatorio [{reminder_id}] ya estaba {reminder.status}.",
                           "cancel_by_id_already_done")
        return {"status": "ok", "action": "cancel_by_id_already_done"}

    now = datetime.now(TZ)
    reminder.status        = "cancelled"
    reminder.awaiting_ack  = False
    reminder.cancelled_at  = now
    reminder.error_message = "cancelled_by_user_command"
    if getattr(reminder, "focalboard_card_id", None):
        reminder.focalboard_synced_at = now
    er.add(db, user.id, "reminder_cancelled", str(reminder.id),
           payload={"cancel_method": "by_id", "reminder_id": reminder_id})
    db.commit()
    await send_and_log(db, user.id, chat_id,
                       f'🛑 He cancelado [{reminder_id}]: "{reminder.task_text}".',
                       "cancel_by_id_confirmation")
    return {"status": "ok", "action": "reminder_cancelled", "reminder_id": reminder_id}


async def handle_cancel_all_date(db, user: User, chat_id: int,
                                  date_hint: str | None, original_text: str):
    """Cancel all reminders on a specific date."""
    now = datetime.now(TZ)
    target_date = None
    if date_hint:
        try:
            target_date = datetime.fromisoformat(date_hint).date()
        except Exception:
            pass
    if not target_date:
        lowered = original_text.lower()
        if "mañana" in lowered:
            target_date = (now + timedelta(days=1)).date()
        elif "hoy" in lowered:
            target_date = now.date()
        elif "pasado mañana" in lowered:
            target_date = (now + timedelta(days=2)).date()

    if not target_date:
        await send_and_log(db, user.id, chat_id,
                           "No entendí qué fecha quieres limpiar. Di por ejemplo: 'cancela todo lo de mañana'.",
                           "cancel_all_date_no_date")
        return {"status": "ok", "action": "cancel_all_date_no_date"}

    rows = db.execute(
        select(Reminder).where(Reminder.user_id == user.id)
        .where(Reminder.status.in_(["scheduled", "pending", "sent"]))
    ).scalars().all()
    to_cancel = [r for r in rows
                 if to_local(r.remind_at) and to_local(r.remind_at).date() == target_date]

    DAYS = ["lunes","martes","miércoles","jueves","viernes","sábado","domingo"]
    day_name = DAYS[target_date.weekday()]

    if not to_cancel:
        await send_and_log(db, user.id, chat_id,
                           f"No hay recordatorios activos el {day_name} {target_date.strftime('%d/%m')}.",
                           "cancel_all_date_empty")
        return {"status": "ok", "action": "cancel_all_date_empty"}

    cancelled_texts = []
    for r in to_cancel:
        r.status        = "cancelled"
        r.awaiting_ack  = False
        r.cancelled_at  = now
        r.error_message = "cancelled_by_user_all_date"
        cancelled_texts.append(f'"{r.task_text}"')

    er.add(db, user.id, "cancel_all_date",
           payload={"date": str(target_date), "count": len(to_cancel)})
    db.commit()
    reply = (f"Cancelados {len(to_cancel)} recordatorios del {day_name} {target_date.strftime('%d/%m')}:\n"
             + "\n".join(f"  • {t}" for t in cancelled_texts))
    await send_and_log(db, user.id, chat_id, reply, "cancel_all_date_done")
    return {"status": "ok", "action": "cancel_all_date_done", "count": len(to_cancel)}


async def handle_edit_reminder(db, user: User, chat_id: int, reminder_id: int, updates: dict):
    """Edit reminder time or text by ID."""
    reminder = rr.get_by_id(db, reminder_id)

    if not reminder:
        await send_and_log(db, user.id, chat_id,
                           f"❌ No encontré ningún recordatorio con id {reminder_id}.", "edit_not_found")
        return {"status": "ok", "action": "edit_not_found"}

    if reminder.status in ("cancelled", "completed"):
        await send_and_log(db, user.id, chat_id,
                           f"ℹ️ El recordatorio {reminder_id} ya está {reminder.status}, no se puede editar.",
                           "edit_invalid_status")
        return {"status": "ok", "action": "edit_invalid_status"}

    now = datetime.now(TZ)
    base_dt = to_local(reminder.remind_at) or now
    if updates.get("tomorrow"):
        base_dt += timedelta(days=1)
    if "hour" in updates:
        base_dt = base_dt.replace(hour=updates["hour"],
                                  minute=updates.get("minute", 0), second=0, microsecond=0)
        if base_dt <= now and not updates.get("tomorrow"):
            base_dt += timedelta(days=1)
        reminder.remind_at = base_dt
        reminder.status    = "scheduled"
    if "task_text" in updates:
        reminder.task_text = updates["task_text"]

    er.add(db, user.id, "reminder_edited", str(reminder.id),
           payload={"updates": {k: str(v) for k, v in updates.items()}})
    db.commit()
    local_dt = to_local(reminder.remind_at)
    dt_str   = local_dt.strftime("%Y-%m-%d %H:%M") if local_dt else "—"
    await send_and_log(db, user.id, chat_id,
                       f'✏️ Recordatorio [{reminder_id}] actualizado: "{reminder.task_text}" → {dt_str}.',
                       "edit_confirmation")
    return {"status": "ok", "action": "reminder_edited", "reminder_id": reminder_id}


async def handle_add_note(db, user: User, chat_id: int,
                           note_text: str, ref_id: int | None = None):
    """
    Add a note OR apply tags to a reminder.

    If note_text consists only of hashtags → applies them as tags (does NOT
    overwrite existing notes). This handles the post-creation tag flow:
      User sends URL → EVA creates task [42]
      User sends '#personal' → EVA applies tag, not note

    If note_text has real content → saves as note (existing behavior).
    Both paths sync to Focalboard TEXT_PROP keeping notes and tags separate.
    """
    from utils.tag_utils import extract_tags, tags_str, remove_tags, build_text_prop

    # ── Resolve target reminder ───────────────────────────────────────────
    if ref_id:
        target = rr.get_by_id_and_user(db, ref_id, user.id)
        if not target:
            await send_and_log(db, user.id, chat_id,
                               f"No encontré la tarea [{ref_id}].", "add_note_not_found")
            return {"status": "ok", "action": "add_note_not_found"}
    else:
        last_out = mr.get_last_outbound(db, user.id)
        target = None
        if last_out:
            id_match = re.search(r'\[(\d+)\]', last_out.message_text)
            if id_match:
                target = rr.get_by_id_and_user(db, int(id_match.group(1)), user.id)
        if not target:
            target = rr.get_last_with_card(db, user.id)
        if not target:
            await send_and_log(db, user.id, chat_id,
                               "No sé a qué tarea te refieres. Dime el ID, por ejemplo: '52 agrégale una nota: texto'",
                               "add_note_no_target")
            return {"status": "ok", "action": "add_note_no_target"}

    # ── Detect: tags-only vs note+tags vs real note ──────────────────────
    incoming_tags  = extract_tags(note_text)
    content_part   = remove_tags(note_text).strip()
    tags_only      = bool(incoming_tags) and not content_part
    mixed          = bool(incoming_tags) and bool(content_part)

    reply_action = "add_tag_done" if tags_only else "add_note_done"

    if tags_only:
        # ── Tags-only: merge into existing tags, don't touch notes ────────
        existing_tags = extract_tags(target.tags or "")
        merged_tags   = list(dict.fromkeys(existing_tags + incoming_tags))
        target.tags   = tags_str(merged_tags)
        print(f"[tag] applied tags={target.tags} to reminder [{target.id}]")
        reply_text = f'🏷️ Tag aplicado a "{target.task_text}" [{target.id}]: {" ".join(incoming_tags)}'

    elif mixed:
        # ── Note + tags: save clean note, merge tags separately ───────────
        # "confirmar con Luis #personal" → notes="confirmar con Luis", tags+="#personal"
        existing_tags = extract_tags(target.tags or "")
        merged_tags   = list(dict.fromkeys(existing_tags + incoming_tags))
        target.tags   = tags_str(merged_tags)
        target.notes  = content_part  # clean note without hashtags
        print(f"[note+tag] note='{content_part}' tags={target.tags} for reminder [{target.id}]")
        tags_display  = f" · {' '.join(incoming_tags)}"
        reply_text = (f'✅ Nota añadida a "{target.task_text}" [{target.id}]: "{content_part}"'
                      f'\n🏷️ Tag aplicado: {" ".join(incoming_tags)}')
        reply_action = "add_note_and_tag_done"

    else:
        # ── Note only: save note, preserve existing tags ──────────────────
        target.notes = note_text
        print(f"[note] saved note for reminder [{target.id}]")
        reply_text = f'✅ Nota añadida a "{target.task_text}" [{target.id}]: "{note_text}"'

    db.commit()

    # ── Sync to Focalboard — notes and tags in separate properties ────────
    if target.focalboard_card_id and fb.is_configured():
        try:
            from sync_service import (STATUS_OPTIONS, STATUS_PROP_ID, TEXT_PROP_ID,
                                       URL_PROP_ID, DATE_PROP_ID, PRIORITY_PROP_ID,
                                       PRIORITY_OPTIONS)
            _merged = {STATUS_PROP_ID: STATUS_OPTIONS.get(target.status, "aoptpendiente00000000000001")}
            if target.remind_at:
                _local_dt = to_local(target.remind_at)
                if _local_dt and _local_dt.year < 2099:
                    _merged[DATE_PROP_ID] = json.dumps({"from": int(_local_dt.timestamp() * 1000)})
            if getattr(target, "url", None):
                _merged[URL_PROP_ID] = target.url
            _prio = getattr(target, "priority", "P3") or "P3"
            if _prio in PRIORITY_OPTIONS:
                _merged[PRIORITY_PROP_ID] = PRIORITY_OPTIONS[_prio]
            # TEXT_PROP: notes take priority; fall back to tags if no notes
            _current_tags = extract_tags(target.tags or "")
            _text_val     = build_text_prop(target.notes, _current_tags)
            if _text_val:
                _merged[TEXT_PROP_ID] = _text_val
            await fb.update_card_properties(target.focalboard_card_id, _merged)
        except Exception as exc:
            print(f"[add_note] Focalboard sync error: {exc}")

    await send_and_log(db, user.id, chat_id, reply_text, reply_action)
    return {"status": "ok", "action": reply_action, "reminder_id": target.id}


async def handle_bulk_cleanup(db, user: User, chat_id: int, statuses: list[str]):
    """Delete all reminders with given statuses + their Focalboard cards."""
    rows = db.execute(
        select(Reminder).where(Reminder.user_id == user.id).where(Reminder.status.in_(statuses))
    ).scalars().all()

    if not rows:
        status_names = " y ".join("completados" if s == "completed" else "cancelados" for s in statuses)
        await send_and_log(db, user.id, chat_id,
                           f"No tienes recordatorios {status_names} ahora mismo.", "bulk_cleanup_empty")
        return {"status": "ok", "action": "bulk_cleanup_empty"}

    deleted_fb = 0
    for r in rows:
        if r.focalboard_card_id and fb.is_configured():
            if await fb.delete_card(r.focalboard_card_id):
                deleted_fb += 1

    count = len(rows)
    for r in rows:
        db.delete(r)
    er.add(db, user.id, "bulk_cleanup", str(count),
           payload={"statuses": statuses, "deleted_fb": deleted_fb})
    db.commit()

    status_names = " y ".join("completadas" if s == "completed" else "canceladas" for s in statuses)
    fb_note = " También eliminadas de Focalboard." if deleted_fb > 0 else ""
    await send_and_log(db, user.id, chat_id,
                       f"🗑️ Eliminadas {count} tareas {status_names}.{fb_note}", "bulk_cleanup_done")
    return {"status": "ok", "action": "bulk_cleanup_done", "count": count}


async def handle_admin_cleanup(db, user: User, chat_id: int):
    """Clean test reminders from DB and Focalboard."""
    await send_and_log(db, user.id, chat_id, "Limpiando... un momento.", "admin_cleanup_start")

    test_keywords = ["probar", "prueba", "test", "sistema", "focalboard", "integración"]
    rows = db.execute(
        select(Reminder).where(Reminder.user_id == user.id)
        .where(Reminder.status.in_(["sent", "cancelled", "scheduled", "pending"]))
    ).scalars().all()
    cleaned_db = sum(1 for r in rows if any(kw in r.task_text.lower() for kw in test_keywords)
                     and not setattr(r, "status", "cancelled") and not setattr(r, "error_message", "cleaned_by_admin"))
    # simpler version:
    cleaned_db = 0
    for r in rows:
        if any(kw in r.task_text.lower() for kw in test_keywords):
            r.status = "cancelled"
            r.error_message = "cleaned_by_admin"
            cleaned_db += 1
    if cleaned_db:
        db.commit()

    cleaned_fb = 0
    if fb.is_configured():
        try:
            from collections import defaultdict
            cards = await fb.get_all_cards()
            test_words = ["probar","prueba","test","sistema","focalboard",
                          "integración","aviso previo","card con fecha","createat"]
            by_title = defaultdict(list)
            for card in cards:
                by_title[card["title"].lower()].append(card)
            to_delete = {card["id"] for card in cards
                         if any(kw in card["title"].lower() for kw in test_words)}
            for dupes in by_title.values():
                if len(dupes) > 1:
                    for dup in sorted(dupes, key=lambda x: x.get("createAt", 0), reverse=True)[1:]:
                        to_delete.add(dup["id"])
            for card_id in to_delete:
                if await fb.delete_card(card_id):
                    cleaned_fb += 1
        except Exception as exc:
            print(f"[admin_cleanup] Focalboard error: {exc}")

    reply = (f"Limpieza completada:\n"
             f"  • BD: {cleaned_db} recordatorios de prueba cancelados\n"
             f"  • Focalboard: {cleaned_fb} tarjetas eliminadas")
    await send_and_log(db, user.id, chat_id, reply, "admin_cleanup_done")
    return {"status": "ok", "action": "admin_cleanup_done",
            "cleaned_db": cleaned_db, "cleaned_fb": cleaned_fb}