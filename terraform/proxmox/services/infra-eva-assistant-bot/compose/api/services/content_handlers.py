"""
services/content_handlers.py
=============================
Business logic for content ideas and undated pending tasks.

To debug:
- #contenido tag not routing correctly  → inspect handle_content_idea
- URL not saved as task                 → inspect handle_pending_task
- Wrong Focalboard board targeted       → inspect board IDs in core/config.py
- Priority not inferred correctly       → inspect infer_priority call

No FastAPI imports here. No routes. Pure business logic + DB + Focalboard.
"""
import os
import re
import time
import uuid
from datetime import datetime

from sqlalchemy import select

from models import User, Reminder, Event, Message
from telegram_service import send_message
from core.config import (
    TZ,
    CONTENT_BOARD_ID, CONTENT_STATUS_PROP, CONTENT_FORMATO_PROP,
    CONTENT_PROYECTO_PROP, CONTENT_LINK_PROP, CONTENT_LOCATION_PROP,
    CONTENT_PRIORITY_PROP, CONTENT_PRIORITY_DEFAULT, CONTENT_PRIORITY_MAP,
    CONTENT_STATUS_IDEA, CONTENT_PROYECTO_MAP, CONTENT_FORMATO_MAP,
    PRIORITY_OPTIONS,
)
from services.reminder_handlers import send_and_log
from integrations import focalboard_client as fb


async def handle_content_idea(db, user: User, chat_id: int, task_text: str,
                               tags: str | None = None, notes: str | None = None,
                               url: str | None = None) -> dict:
    """
    Create a content idea in the Content Focalboard board.
    Triggered when message contains #contenido.
    """
    from ai_parser import infer_priority

    # Detect project from tags
    _proyecto_opt = None
    if tags:
        for tag_key, tag_val in CONTENT_PROYECTO_MAP.items():
            if tag_key in tags.lower():
                _proyecto_opt = tag_val
                break

    # Detect format from tags or text
    _formato_opt = None
    _lower_task  = task_text.lower()
    for fmt_key, fmt_val in CONTENT_FORMATO_MAP.items():
        if fmt_key in _lower_task or (tags and fmt_key in tags.lower()):
            _formato_opt = fmt_val
            break

    # Detect local path in text
    _location_match = re.search(r'(?:^|\s)(?:~(?=/)|/home/|[A-Za-z]:[/\\])[^\s,;]+', task_text)
    _location = _location_match.group(0) if _location_match else None
    if _location:
        task_text = task_text.replace(_location, "").strip()

    from utils.tag_utils import extract_tags, build_text_prop

    fb_props = {CONTENT_STATUS_PROP: CONTENT_STATUS_IDEA}
    if _proyecto_opt: fb_props[CONTENT_PROYECTO_PROP] = _proyecto_opt
    if _formato_opt:  fb_props[CONTENT_FORMATO_PROP]  = _formato_opt
    if url:           fb_props[CONTENT_LINK_PROP]      = url
    if _location:     fb_props[CONTENT_LOCATION_PROP]  = _location

    # TEXT_PROP: notes take priority over tags — keeps notes field clean in UI
    # tags are also stored in reminder.tags (DB) for UI tag badges
    _tag_list  = extract_tags(tags or "")
    _text_val  = build_text_prop(notes, _tag_list)
    if _text_val:
        fb_props["a6bxuk4rgxp7wn6bashiadwaiiy"] = _text_val

    try:
        _prio_key = await infer_priority(task_text)
    except Exception:
        _prio_key = "P3"
    fb_props[CONTENT_PRIORITY_PROP] = CONTENT_PRIORITY_MAP.get(_prio_key, CONTENT_PRIORITY_DEFAULT)

    fb_id = await fb.create_card(task_text, fb_props, board_id=CONTENT_BOARD_ID)
    if not fb_id:
        fb_id = uuid.uuid4().hex[:26]  # fallback local ID if Focalboard is down

    _all_tags = " ".join(filter(None, [tags, "#contenido"])) if tags else "#contenido"
    reminder = Reminder(
        user_id=user.id, source_text=task_text, task_text=task_text,
        remind_at=datetime.now(TZ).replace(year=2099), status="pending",
        notes=notes, tags=_all_tags, url=url, priority="P3",
        focalboard_card_id=fb_id, focalboard_synced_at=datetime.now(TZ),
    )
    db.add(reminder)
    db.add(Event(user_id=user.id, event_type="content_idea_created", event_value=fb_id,
                 source="telegram", payload={"task_text": task_text, "tags": _all_tags}))
    db.commit()
    db.refresh(reminder)

    # Build reply
    _proyecto_display = ""
    if tags:
        for p in list(CONTENT_PROYECTO_MAP.keys()):
            if p.lower() in tags.lower():
                _proyecto_display = f" · {p}"
                break
    tags_clean   = " ".join(t for t in (tags or "").split() if t != "#contenido") if tags else ""
    tags_display = f"\n🏷️ {tags_clean}" if tags_clean else ""
    reply = (f'💡 Idea de contenido guardada [{reminder.id}]: "{task_text}"{_proyecto_display}\n'
             f'📋 Estado: Idea → /contenido{tags_display}')
    await send_and_log(db, user.id, chat_id, reply, "content_idea_created")
    return {"status": "ok", "action": "content_idea_created", "reminder_id": reminder.id}


async def handle_pending_task(db, user: User, chat_id: int, task_text: str,
                               url: str | None = None, notes: str | None = None) -> dict:
    """
    Create an undated task in the Tasks Focalboard board + EVA reminders table.
    Triggered by 'tengo que X', 'hay que X', bare URLs, etc.
    """
    from ai_parser import infer_priority

    if not fb.is_configured():
        reply = f'📌 Guardado: "{task_text}"'
        await send_and_log(db, user.id, chat_id, reply, "pending_task_no_fb")
        return {"status": "ok", "action": "pending_task_no_focalboard"}

    try:
        _priority = await infer_priority(task_text)
    except Exception:
        _priority = "P3"

    _fb_props = {
        "aevastatus00000000000000001": "aoptpendiente00000000000001",
        "ann9q8kbmc67mb7p4d8xrmma6rr": PRIORITY_OPTIONS.get(_priority, PRIORITY_OPTIONS["P3"]),
    }
    if url: _fb_props["asztuket5mjeeongrzooyx5utbo"] = url
    # TEXT_PROP: notes only — tags are stored in reminder.tags for the UI
    if notes: _fb_props["a6bxuk4rgxp7wn6bashiadwaiiy"] = notes

    fb_id = await fb.create_card(task_text, _fb_props)
    if fb_id:
        try:
            pending_reminder = Reminder(
                user_id=user.id, source_text=task_text, task_text=task_text,
                remind_at=datetime.now(TZ).replace(year=2099), status="pending",
                notes=notes, tags=None, url=url,
                priority=_priority, focalboard_card_id=fb_id,
                focalboard_synced_at=datetime.now(TZ),
            )
            db.add(pending_reminder)
            db.add(Event(user_id=user.id, event_type="pending_task_created",
                         event_value=fb_id, source="telegram",
                         payload={"task_text": task_text, "card_id": fb_id, "url": url}))
            db.commit()
        except Exception as exc:
            print(f"[pending_task] reminder save error: {exc}")
            db.rollback()

        reply = (f'📌 Guardado: "{task_text}"'
                 + (f'\n🔗 {url}' if url else '')
                 + '\nCuando tengas un momento, asígnale fecha desde la UI.')
        await send_and_log(db, user.id, chat_id, reply, "pending_task_created")
        return {"status": "ok", "action": "pending_task_created", "card_id": fb_id}

    reply = f'📌 Guardado: "{task_text}"'
    await send_and_log(db, user.id, chat_id, reply, "pending_task_fb_error")
    return {"status": "ok", "action": "pending_task_fb_error"}