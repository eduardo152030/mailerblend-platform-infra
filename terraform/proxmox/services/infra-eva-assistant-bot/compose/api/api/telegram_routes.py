"""
api/telegram_routes.py
=======================
Telegram webhook endpoint + photo handler.

To debug:
- EVA not responding to messages     → check logs here first
- Intent detection wrong             → inspect the intent decision tree
- Photo messages not saved           → inspect _handle_photo_message
- Content routing (#contenido)       → inspect the tag detection block

Business logic lives in:
  services/reminder_handlers.py  ← handle_ack, cancel, edit, note, list
  services/content_handlers.py   ← handle_content_idea, handle_pending_task
"""
import os
import re
import traceback
import unicodedata
from datetime import datetime, timedelta

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from db import SessionLocal
from models import User, Reminder, Message, Event
from parser_service import parse_reminder
from ai_parser import (parse_reminder_ai, detect_intent, answer_question_ai,
                        build_reply_ai, chat_reply_ai, infer_priority)
from memory_service import get_user_facts, build_memory_context, process_message_for_memory
from persona_service import load_persona, build_system_prompt
from telegram_service import send_message

from core.config import TZ, DEFAULT_TIMEZONE, CONTENT_BOARD_ID
from utils.time_utils import to_local
from utils.text_utils import (
    normalize_text, is_list_command, is_ack_text,
    _extract_snooze_note, _parse_snooze,
    extract_cancel_task, extract_edit_command,
    extract_pending_task, build_help_text,
    build_confirmation_text_from_parsed,
)
from services.reminder_handlers import (
    send_and_log, _get_recent_context,
    handle_list_command, handle_ack_command,
    handle_cancel_command, handle_cancel_by_id, handle_cancel_all_date,
    handle_edit_reminder, handle_add_note, handle_tag_update,
    handle_bulk_cleanup, handle_admin_cleanup,
)
from services.content_handlers import handle_content_idea, handle_pending_task
from integrations import telegram_client as tg
from integrations import focalboard_client as fb
from repositories import reminder_repository as rr
from repositories import message_repository as mr
from repositories import user_repository as ur
from repositories import event_repository as er
from utils.url_utils import extract_url, extract_title_from_message, clean_domain, is_social_url, filename_to_title
from utils.tag_utils import (
    extract_tags, tags_str, remove_tags, is_content_tag, filter_content_tag,
    parse_tag_update_message,
)

router = APIRouter()


def _extract_telegram_message(payload: dict) -> dict | None:
    return (payload.get("message") or payload.get("edited_message")
            or payload.get("channel_post") or payload.get("edited_channel_post"))


def _norm_ascii(s: str) -> str:
    return unicodedata.normalize("NFD", s.lower()).encode("ascii", "ignore").decode()


@router.post("/telegram/webhook")
async def telegram_webhook(request: Request):
    payload = await request.json()
    message = _extract_telegram_message(payload)

    if not message:
        return {"status": "ignored", "reason": "unsupported_update_type"}

    # ── Photo messages ────────────────────────────────────────────────────
    if message.get("photo"):
        return await _handle_photo_message(message)

    # ── Document messages (PDF, files) ────────────────────────────────────
    if message.get("document"):
        return await _handle_document_message(message)

    text_in = message.get("text")
    if not text_in:
        return {"status": "ignored", "reason": "no_text_message"}

    chat      = message.get("chat") or {}
    from_user = message.get("from") or {}
    chat_id   = chat.get("id")
    if chat_id is None:
        return {"status": "ignored", "reason": "missing_chat_id"}

    telegram_username = from_user.get("username")
    display_name = " ".join(
        x for x in [from_user.get("first_name"), from_user.get("last_name")] if x
    ) or telegram_username or "Unknown"

    db = SessionLocal()
    try:
        # ── User upsert ───────────────────────────────────────────────────
        user = ur.get_by_chat_id(db, chat_id)
        if user is None:
            user = User(telegram_chat_id=chat_id, telegram_username=telegram_username,
                        display_name=display_name, timezone=DEFAULT_TIMEZONE)
            db.add(user)
            db.flush()
        else:
            user.telegram_username = telegram_username
            user.display_name      = display_name

        db.add(Message(user_id=user.id, direction="inbound",
                       message_text=text_in, message_type="chat"))
        db.commit()

        lowered = normalize_text(text_in)

        # ── URL + tag extraction ──────────────────────────────────────────
        _extracted_url = extract_url(text_in)
        _text_no_url   = text_in.replace(_extracted_url, "").strip() if _extracted_url else text_in
        _tags_list     = extract_tags(text_in)
        _tags_str      = tags_str(_tags_list)
        _text_no_tags  = remove_tags(_text_no_url).strip()
        # Context = text without URL and without tags, used as notes
        _url_context   = _text_no_tags if _extracted_url and len(_text_no_tags) >= 3 else None

        # ── Tag update — "#personal", "196 #personal", "196 tags #personal #NT" ──
        # Must run BEFORE content routing to catch tag-only messages early.
        # Only fires when: no URL present, no reminder time, message parses as tag update.
        if not _extracted_url:
            _tag_update = parse_tag_update_message(text_in)
            if _tag_update:
                print(f"[capture:tag] detected tag update: {_tag_update}")
                return await handle_tag_update(
                    db, user, chat_id,
                    tags=_tag_update["tags"],
                    task_id=_tag_update["task_id"],
                )

        # ── Content routing — #contenido ──────────────────────────────────
        # Single check — was duplicated 3x in old code.
        if _tags_str and is_content_tag(_tags_list):
            _content_tags_list = filter_content_tag(_tags_list)
            _content_tags      = tags_str(_content_tags_list)
            # Title: text without tags, or smart URL title, or fallback
            _content_title = remove_tags(text_in).strip()
            if _extracted_url:
                _content_title = _content_title.replace(_extracted_url, "").strip()
            if not _content_title and _extracted_url:
                _content_title = extract_title_from_message(message, _extracted_url)
            if not _content_title:
                _content_title = "Idea de contenido"
            print(f"[capture:url] #contenido → title='{_content_title}' url={_extracted_url} tags={_content_tags}")
            return await handle_content_idea(db, user, chat_id, _content_title,
                                             tags=_content_tags, url=_extracted_url)

        # ── Bare URL (or URL with short/no text) → pending task ───────────
        # Uses smart title extraction instead of always "Revisar domain.com"
        if _extracted_url and len(_text_no_tags.strip()) < 5:
            _title = extract_title_from_message(message, _extracted_url)
            print(f"[capture:url] bare URL → title='{_title}' url={_extracted_url}")
            return await handle_pending_task(db, user, chat_id, _title,
                                             url=_extracted_url, notes=_url_context)

        # ── URL with surrounding text → use text as title ─────────────────
        # Telegram often sends "Page Title\nhttps://..." — use the title.
        if _extracted_url and len(_text_no_tags.strip()) < 120:
            _title = extract_title_from_message(message, _extracted_url)
            print(f"[capture:url] URL+text → title='{_title}' url={_extracted_url} tags={_tags_str}")
            return await handle_pending_task(db, user, chat_id, _title,
                                             url=_extracted_url, notes=_url_context,
                                             tags=_tags_str)

        # ── Last EVA message (used in multiple checks below) ──────────────
        _last_eva_msg = mr.get_last_outbound(db, user.id)

        # ── "Yes, save it" after EVA asked about a URL ───────────────────
        _save_intent = re.match(
            r'^(?:es\s+un\s+recordatorio|guarda(?:lo)?|apunta(?:lo)?|s[ií](?:\s+guarda(?:lo)?)?'
            r'|recuerda(?:lo)?|s[ií]\s*,?\s*(?:por\s+favor)?|anota(?:lo)?)[\s.!?]*$',
            lowered.strip(), re.IGNORECASE)
        if _save_intent and _last_eva_msg and "?" in _last_eva_msg.message_text:
            _prev_msgs = mr.get_last_inbound(db, user.id, limit=2)
            for _um in _prev_msgs[1:]:
                _prev_url = extract_url(_um.message_text)
                if _prev_url:
                    _prev_title = extract_title_from_message(_um, _prev_url)
                    print(f"[capture:url] save_intent → title='{_prev_title}' url={_prev_url}")
                    return await handle_pending_task(db, user, chat_id, _prev_title, url=_prev_url)

        # ── Post-creation context: add note OR tag to last created task ──
        # Triggers when:
        #   a) EVA just confirmed a task creation (📌 Guardado / 💡 Idea guardada)
        #   b) The next message is either a plain note OR just hashtags
        _is_post_creation = (
            _last_eva_msg and
            ("📌 Guardado" in _last_eva_msg.message_text or
             "📌 Apuntado" in _last_eva_msg.message_text or  # backward compat
             "💡 Idea de contenido guardada" in _last_eva_msg.message_text or
             "✅ Nota añadida" in _last_eva_msg.message_text or
             "🏷️" in _last_eva_msg.message_text) and
            len(lowered.strip()) >= 2 and
            not re.match(r'^(?:cancela|elimina|borra|lista|mis recordatorios|recuérdame|recuerdame|eva[,\s]|/)',
                         lowered.strip()) and
            not re.match(r'^(?:crear?\s+un?|crea\s+un?|quiero\s+(?:crear|hacer|un)|tengo\s+que|hay\s+que|pendiente[:\s])',
                         lowered.strip(), re.IGNORECASE) and
            not re.search(r'a las\s+\d|en\s+\d+\s+min|mañana\s|el\s+\d+\s|'
                          r'para\s+el\s+(?:lunes|martes|miércoles|jueves|viernes|sábado|domingo|\d)|'
                          r'cada\s+\d|todos\s+los', lowered)
        )
        if _is_post_creation:
            _id_m = re.search(r'\[(\d+)\]', _last_eva_msg.message_text)
            if _id_m:
                return await handle_add_note(db, user, chat_id, text_in, ref_id=int(_id_m.group(1)))
            _last_task = rr.get_last_with_card(db, user.id)
            if _last_task:
                return await handle_add_note(db, user, chat_id, text_in, ref_id=_last_task.id)

        # ── Operations by ID: "52 cancelala", "52 agrégale nota: X" ──────
        _id_op = re.match(r'^(?:(?:la|el)\s+)?(?:tarea|nota|recordatorio)?\s*(\d+)\s+(.+)$',
                          lowered.strip(), re.IGNORECASE)
        if _id_op:
            _ref_id  = int(_id_op.group(1))
            _op_text = _id_op.group(2).strip()

            if re.match(r'^(?:cancela(?:la|lo)?|elimina(?:la|lo)?|borra(?:la|lo)?|quita(?:la|lo)?)[\s.!?]*$', _op_text):
                return await handle_cancel_by_id(db, user, chat_id, _ref_id)

            if re.match(r'^(?:(?:marca(?:la|lo)?\s+(?:como\s+)?|ponla\s+(?:como\s+)?|esta\s+)?en\s+progreso|'
                        r'empez(?:ar|ando|é)\s+(?:con\s+)?(?:esta?|la?))[\s.!?]*$', _op_text, re.IGNORECASE):
                _ref_r = rr.get_by_id_and_user(db, _ref_id, user.id)
                if _ref_r:
                    _ref_r.status = "in_progress"
                    db.commit()
                    await send_and_log(db, user.id, chat_id,
                                       f'🔵 En progreso [{_ref_id}]: "{_ref_r.task_text}".', "in_progress_by_id")
                    return {"status": "ok", "action": "in_progress_by_id"}

            if re.match(r'^(?:marca(?:la|lo)?\s+(?:como\s+)?(?:hecha?|completad[ao]|lista?)|completa(?:la|lo)?)[\s.!?]*$', _op_text):
                _ref_r = rr.get_by_id_and_user(db, _ref_id, user.id)
                if _ref_r:
                    _ref_r.status       = "completed"
                    _ref_r.completed_at = datetime.now(TZ)
                    db.commit()
                    await send_and_log(db, user.id, chat_id,
                                       f'Completado [{_ref_id}]: "{_ref_r.task_text}".', "completed_by_id_ref")
                    return {"status": "ok", "action": "completed_by_id_ref"}

            _note_m = re.match(r'^(?:agr[eé]ga(?:le)?(?:\s+una?)?\s+nota[:\s]+|'
                                r'a[ñn]ade(?:le)?(?:\s+una?)?\s+nota[:\s]+)(.+)$', _op_text, re.IGNORECASE)
            if _note_m:
                return await handle_add_note(db, user, chat_id, _note_m.group(1).strip(), ref_id=_ref_id)

            _move_m = re.match(r'^(?:pospon(?:lo|la)?|mueve(?:lo|la)?|pasa(?:lo|la)?|aplaza(?:lo|la)?)'
                               r'(?:\s+(?:para|en|al?|a))?\s+(.+)$', _op_text, re.IGNORECASE)
            if _move_m:
                _target_r = rr.get_by_id_and_user(db, _ref_id, user.id)
                if _target_r:
                    user_facts    = get_user_facts(db, user.id)
                    memory_ctx    = build_memory_context(user_facts)
                    persona       = load_persona(telegram_username)
                    system_prompt = build_system_prompt(persona, memory_context=memory_ctx)
                    _synthetic    = f"recuérdame {_target_r.task_text} {_move_m.group(1).strip()}"
                    _new_p        = await parse_reminder_ai(_synthetic, memory_context=system_prompt) or parse_reminder(_synthetic)
                    if _new_p:
                        _target_r.remind_at    = _new_p["remind_at"]
                        _target_r.status       = "scheduled"
                        _target_r.awaiting_ack = False
                        db.commit()
                        new_dt  = to_local(_target_r.remind_at)
                        now_tz  = datetime.now(TZ)
                        DAYS    = ["lunes","martes","miércoles","jueves","viernes","sábado","domingo"]
                        day_str = "hoy" if new_dt.date() == now_tz.date() else \
                                  "mañana" if new_dt.date() == (now_tz+timedelta(days=1)).date() else \
                                  f"el {DAYS[new_dt.weekday()]} {new_dt.strftime('%d/%m')}"
                        await send_and_log(db, user.id, chat_id,
                                           f'Movido [{_ref_id}]: "{_target_r.task_text}" → {day_str} a las {new_dt.strftime("%H:%M")}.',
                                           "move_by_id")
                        return {"status": "ok", "action": "move_by_id"}
                    await send_and_log(db, user.id, chat_id,
                                       f'No entendí la nueva fecha. Di por ejemplo: "{_ref_id} posponlo para el lunes a las 10".',
                                       "move_by_id_fail")
                    return {"status": "ok", "action": "move_by_id_fail"}

            _rename_m = re.match(r'^(?:cambia(?:la|lo)?\s+(?:a|el\s+nombre\s+a)[:\s]+)(.+)$', _op_text, re.IGNORECASE)
            if _rename_m:
                _ref_r = rr.get_by_id_and_user(db, _ref_id, user.id)
                if _ref_r:
                    _ref_r.task_text = _rename_m.group(1).strip()
                    db.commit()
                    await send_and_log(db, user.id, chat_id,
                                       f'Renombrado [{_ref_id}]: ahora es "{_ref_r.task_text}".', "renamed_by_id_ref")
                    return {"status": "ok", "action": "renamed_by_id_ref"}

        # ── Load persona + memory (needed for LLM calls below) ────────────
        user_facts    = get_user_facts(db, user.id)
        memory_ctx    = build_memory_context(user_facts)
        persona       = load_persona(telegram_username)
        system_prompt = build_system_prompt(persona, memory_context=memory_ctx)

        # Memory extraction in background
        import asyncio
        async def _mem_bg(uid: int, txt: str):
            _db = SessionLocal()
            try:    await process_message_for_memory(_db, uid, txt)
            finally: _db.close()
        asyncio.ensure_future(_mem_bg(user.id, text_in))

        # ── Fast deterministic commands ───────────────────────────────────
        if is_list_command(lowered):
            return await handle_list_command(db, user, chat_id)

        _cancel_kw = ("cancela", "cancelar", "elimina", "eliminar", "borra", "borrar")
        _id_m2     = re.search(r'\b(\d{1,6})\b', lowered)
        if any(w in lowered for w in _cancel_kw) and _id_m2:
            return await handle_cancel_by_id(db, user, chat_id, int(_id_m2.group(1)))

        if is_ack_text(lowered):
            return await handle_ack_command(db, user, chat_id, lowered)

        # "en X minutos" when reminder is active → snooze
        if re.match(r'^(?:recu[eé]rdame\s+)?(?:en\s+)?(\d+)\s+(minutos?|horas?)[\s.!?]*$',
                    lowered.strip(), re.IGNORECASE):
            _active = rr.get_awaiting_ack_active(db, user.id)
            if _active:
                return await handle_ack_command(db, user, chat_id, lowered)

        # "no, a las HH:MM" correction
        _corr = re.match(r'^no[,.]?\s+(?:era\s+)?a las?\s+(\d{1,2})(?::(\d{2}))?$', lowered, re.IGNORECASE)
        if _corr:
            new_h = int(_corr.group(1))
            new_m = int(_corr.group(2)) if _corr.group(2) else 0
            last_r = rr.get_last_scheduled(db, user.id)
            if last_r:
                now_tz = datetime.now(TZ)
                new_dt = to_local(last_r.remind_at).replace(hour=new_h, minute=new_m, second=0, microsecond=0)
                if new_dt <= now_tz:
                    new_dt += timedelta(days=1)
                last_r.remind_at = new_dt
                last_r.status    = "scheduled"
                db.add(Event(user_id=user.id, event_type="reminder_corrected",
                             event_value=str(last_r.id), source="telegram",
                             payload={"new_time": f"{new_h:02d}:{new_m:02d}"}))
                db.commit()
                await send_and_log(db, user.id, chat_id,
                                   f'Corregido [{last_r.id}]: "{last_r.task_text}" — ahora a las {new_dt.strftime("%H:%M")}.',
                                   "reminder_corrected")
                return {"status": "ok", "action": "reminder_corrected", "reminder_id": last_r.id}

        # "cancelarlos" plural
        if re.match(r'^(?:puedes\s+)?(?:cancela(?:r)?los|elimina(?:r)?los|borra(?:r)?los|quita(?:r)?los)[\s.!?]*$',
                    lowered.strip(), re.IGNORECASE):
            last_msgs = mr.get_last_outbound_few(db, user.id, limit=3)
            date_hint = None
            now_tz    = datetime.now(TZ)
            for msg in last_msgs:
                txt = msg.message_text.lower()
                if "mañana" in txt:
                    date_hint = (now_tz + timedelta(days=1)).strftime("%Y-%m-%d"); break
                elif "hoy" in txt:
                    date_hint = now_tz.strftime("%Y-%m-%d"); break
                elif any(d in txt for d in ["viernes","lunes","martes"]):
                    m2 = re.search(r'(\d{1,2}/\d{2})', txt)
                    if m2:
                        try:
                            d2, mo2 = m2.group(1).split("/")
                            date_hint = f"{now_tz.year}-{mo2}-{d2.zfill(2)}"
                        except Exception: pass
                    break
            return await handle_cancel_all_date(db, user, chat_id, date_hint, text_in)

        # ── Pronoun resolution (cancelalo, posponlo, cambialo) ────────────
        lowered_norm = _norm_ascii(lowered)

        def _get_next_reminder():
            ack_r = rr.get_awaiting_ack_active(db, user.id)
            if ack_r: return ack_r
            last_out = mr.get_last_outbound(db, user.id)
            if last_out:
                id_m3 = re.search(r'\[(\d+)\]', last_out.message_text)
                if id_m3:
                    r3 = rr.get_by_id_and_user(db, int(id_m3.group(1)), user.id)
                    if r3 and r3.status in ("scheduled","pending","sent"): return r3
                txt_m = re.search(r'"([^"]+)"', last_out.message_text)
                if txt_m:
                    mentioned = txt_m.group(1).lower()
                    for r4 in rr.get_cancellable_for_user(db, user.id):
                        if mentioned in r4.task_text.lower() or r4.task_text.lower() in mentioned:
                            return r4
            return rr.get_next_scheduled(db, user.id)

        if re.match(r'^(?:cancela(?:lo|la)?|elimina(?:lo|la)?|borra(?:lo|la)?|quita(?:lo|la)?)[\s.!?]*$',
                    lowered_norm.strip()):
            last_r = _get_next_reminder()
            if last_r:
                return await handle_cancel_by_id(db, user, chat_id, last_r.id)

        _pm = re.match(
            r'^(?:pospon(?:lo|la)?|mueve(?:lo|la)?|pasa(?:lo|la)?|retrasa(?:lo|la)?|'
            r'aplaza(?:lo|la)?|deja(?:lo|la)?(?:\s+para))(?:\s+(?:para|al?|hasta|a))?\s+(.+)$',
            lowered_norm.strip())
        if _pm:
            last_r = _get_next_reminder()
            if last_r:
                _new_p2 = await parse_reminder_ai(f"recuérdame {last_r.task_text} {_pm.group(1).strip()}",
                                                   memory_context=memory_ctx) or \
                          parse_reminder(f"recuérdame {last_r.task_text} {_pm.group(1).strip()}")
                if _new_p2:
                    last_r.remind_at    = _new_p2["remind_at"]
                    last_r.status       = "scheduled"
                    last_r.awaiting_ack = False
                    db.add(Event(user_id=user.id, event_type="reminder_rescheduled",
                                 event_value=str(last_r.id), source="telegram",
                                 payload={"via": "pronoun"}))
                    db.commit()
                    now_l   = datetime.now(TZ)
                    new_dt  = to_local(last_r.remind_at)
                    DAYS    = ["lunes","martes","miércoles","jueves","viernes","sábado","domingo"]
                    day_str = "hoy" if new_dt.date() == now_l.date() else \
                              "mañana" if new_dt.date() == (now_l+timedelta(days=1)).date() else \
                              f"el {DAYS[new_dt.weekday()]} {new_dt.strftime('%d/%m')}"
                    await send_and_log(db, user.id, chat_id,
                                       f'Movido [{last_r.id}]: "{last_r.task_text}" → {day_str} a las {new_dt.strftime("%H:%M")}.',
                                       "reminder_rescheduled_pronoun")
                    return {"status": "ok", "action": "reminder_rescheduled", "reminder_id": last_r.id}
                await send_and_log(db, user.id, chat_id,
                                   'No entendí la nueva fecha. Di por ejemplo: "posponlo para el lunes a las 10".',
                                   "pronoun_move_parse_fail")
                return {"status": "ok", "action": "pronoun_move_parse_fail"}

        _pet = re.match(
            r'^(?:cambia(?:lo|la)?|pon(?:lo|la)?|mueve(?:lo|la)?|edita(?:lo|la)?)(?:\s+(?:al?|a))?\s+'
            r'(?:las?\s+)?(\d{1,2})(?::(\d{2}))?[\s.!?]*$', lowered_norm.strip())
        if _pet:
            last_r = _get_next_reminder()
            if last_r:
                new_h2  = int(_pet.group(1))
                new_m2  = int(_pet.group(2)) if _pet.group(2) else 0
                now_tz2 = datetime.now(TZ)
                new_dt2 = to_local(last_r.remind_at).replace(hour=new_h2, minute=new_m2, second=0, microsecond=0)
                if new_dt2 <= now_tz2:
                    new_dt2 += timedelta(days=1)
                last_r.remind_at = new_dt2
                last_r.status    = "scheduled"
                db.add(Event(user_id=user.id, event_type="reminder_edited_pronoun",
                             event_value=str(last_r.id), source="telegram",
                             payload={"new_time": f"{new_h2:02d}:{new_m2:02d}"}))
                db.commit()
                await send_and_log(db, user.id, chat_id,
                                   f'Cambiado [{last_r.id}]: "{last_r.task_text}" → ahora a las {new_dt2.strftime("%H:%M")}.',
                                   "reminder_edited_pronoun")
                return {"status": "ok", "action": "reminder_edited_pronoun", "reminder_id": last_r.id}

        # ── LLM intent detection ──────────────────────────────────────────
        parsed = None  # may be set early by pending_task guard
        _conv_history = _get_recent_context(db, user.id, limit=10)
        intent_result = await detect_intent(text_in, memory_context=system_prompt,
                                            conversation_history=_conv_history)
        intent     = intent_result.get("intent", "unknown")
        confidence = intent_result.get("confidence", 0.0)

        # Contextual snooze when reminder is active
        if intent in ("snooze_reminder", "edit_reminder") and confidence >= 0.6:
            active_ack = rr.get_pending_ack_or_sent(db, user.id)
            if active_ack:
                time_part, snooze_note = _extract_snooze_note(lowered)
                snooze_delta = _parse_snooze(time_part)
                if snooze_delta is not None:
                    now_tz3       = datetime.now(TZ)
                    new_remind_at = now_tz3 + snooze_delta
                    active_ack.remind_at    = new_remind_at
                    active_ack.status       = "scheduled"
                    active_ack.awaiting_ack = False
                    if snooze_note and hasattr(active_ack, "notes"):
                        active_ack.notes = snooze_note
                    db.add(Event(user_id=user.id, event_type="reminder_snoozed",
                                 event_value=str(active_ack.id), source="telegram",
                                 payload={"snooze_text": lowered, "note": snooze_note,
                                          "new_remind_at": new_remind_at.isoformat()}))
                    db.commit()
                    dt_str    = to_local(new_remind_at).strftime("%H:%M")
                    _note_ctx = f" Nota guardada: '{snooze_note}'." if snooze_note else ""
                    _ai_r     = await build_reply_ai(
                        text_in,
                        {"task_text": active_ack.task_text, "remind_at": new_remind_at,
                         "mode": "today_or_tomorrow_at_time", "is_persistent": False,
                         "recurrence_type": None, "repeat_every_minutes": None},
                        memory_context=system_prompt + f"\nContexto: pospuso '{active_ack.task_text}' a las {dt_str}.{_note_ctx}"
                    )
                    reply = _ai_r or (f"Movido a las {dt_str}." + (f' Apuntado: "{snooze_note}"' if snooze_note else ""))
                    await send_and_log(db, user.id, chat_id, reply, "snooze_contextual")
                    return {"status": "ok", "action": "reminder_snoozed", "reminder_id": active_ack.id}

                _sp = await parse_reminder_ai(f"recuérdame {active_ack.task_text} {text_in}", memory_context=system_prompt)
                if _sp:
                    active_ack.remind_at    = _sp["remind_at"]
                    active_ack.status       = "scheduled"
                    active_ack.awaiting_ack = False
                    db.add(Event(user_id=user.id, event_type="reminder_snoozed",
                                 event_value=str(active_ack.id), source="telegram",
                                 payload={"via": "ai_snooze", "text": text_in}))
                    db.commit()
                    new_dt3 = to_local(active_ack.remind_at)
                    now_tz4 = datetime.now(TZ)
                    DAYS    = ["lunes","martes","miércoles","jueves","viernes","sábado","domingo"]
                    day_str = "hoy" if new_dt3.date() == now_tz4.date() else \
                              "mañana" if new_dt3.date() == (now_tz4+timedelta(days=1)).date() else \
                              f"el {DAYS[new_dt3.weekday()]} {new_dt3.strftime('%d/%m')}"
                    await send_and_log(db, user.id, chat_id,
                                       f'Movido: "{active_ack.task_text}" → {day_str} a las {new_dt3.strftime("%H:%M")}.',
                                       "snooze_ai_contextual")
                    return {"status": "ok", "action": "reminder_snoozed_ai"}

        if intent == "question" and confidence >= 0.7:
            active = rr.get_active_for_user(db, user.id)[:20]
            now_l2 = datetime.now(TZ)
            DAYS   = ["lunes","martes","miércoles","jueves","viernes","sábado","domingo"]
            lines  = []
            for r in active:
                dt = to_local(r.remind_at)
                if dt:
                    day_str = "hoy" if dt.date() == now_l2.date() else \
                              "mañana" if dt.date() == (now_l2+timedelta(days=1)).date() else \
                              f"{DAYS[dt.weekday()]} {dt.strftime('%d/%m')}"
                    lines.append(f"- [{r.id}] {r.task_text} — {day_str} a las {dt.strftime('%H:%M')} ({r.status})")
                else:
                    lines.append(f"- [{r.id}] {r.task_text} (sin fecha)")
            answer = await answer_question_ai(text_in, "\n".join(lines), memory_context=system_prompt)
            if answer:
                await send_and_log(db, user.id, chat_id, answer, "question_answer")
                return {"status": "ok", "action": "question_answered"}

        if intent == "cancel_reminder" and confidence >= 0.7:
            ct = extract_cancel_task(lowered)
            if ct:
                return await handle_cancel_command(db, user, chat_id, ct)

        if intent == "cancel_all_date" and confidence >= 0.7:
            return await handle_cancel_all_date(db, user, chat_id,
                                                intent_result.get("date_hint"), text_in)

        if intent == "add_note" and confidence >= 0.7:
            _note_txt = re.sub(
                r'^(?:agr[eé]ga(?:le)?(?:\s+una?)?\s+nota[:\s]+|a[ñn]ade(?:le)?(?:\s+una?)?\s+nota[:\s]+|'
                r'agrega\s+(?:esto|que)[:\s]+|apunta\s+(?:que|esto)[:\s]+)',
                '', lowered, flags=re.IGNORECASE).strip() or text_in
            return await handle_add_note(db, user, chat_id, _note_txt)

        # Bulk cleanup
        _bc = re.match(
            r'^(?:eva[,\s]+)?(?:elimina|borra|cancela|limpia)\s+(?:todas?\s+(?:las?\s+)?)?'
            r'(?:tarjetas?\s+(?:en\s+estado\s+(?:de\s+)?)?|(?:las?\s+))?'
            r'(completadas?|canceladas?|completadas?\s+y\s+canceladas?|canceladas?\s+y\s+completadas?)[\s.!?]*$',
            lowered.strip(), re.IGNORECASE)
        if _bc:
            _ct = _bc.group(1).lower()
            _st = []
            if "completad" in _ct: _st.append("completed")
            if "cancelad" in _ct:  _st.append("cancelled")
            return await handle_bulk_cleanup(db, user, chat_id, _st or ["completed","cancelled"])

        if intent == "admin_cleanup" and confidence >= 0.7:
            return await handle_admin_cleanup(db, user, chat_id)

        if intent == "edit_reminder" and confidence >= 0.7:
            er = extract_edit_command(lowered)
            if er:
                return await handle_edit_reminder(db, user, chat_id, er[0], er[1])

        # ── Pending task (no time) ────────────────────────────────────────
        _no_time = not re.search(r'\ba las\s+\d|\ben\s+\d+\s+min|\bmañana\b', lowered)
        if _no_time:
            _pd = re.match(
                r'^(?:eva[,\s]+)?recu[eé]rdame\s+que\s+(?:tengo\s+que|hay\s+que|debo|necesito)\s+(.+)$',
                lowered, re.IGNORECASE)
            if _pd and len(_pd.group(1).strip()) >= 4:
                return await handle_pending_task(db, user, chat_id, _pd.group(1).strip(), url=_extracted_url)
            _dt = extract_pending_task(lowered)
            if _dt:
                return await handle_pending_task(db, user, chat_id, _dt, url=_extracted_url, notes=_url_context)

        if intent == "pending_task" and confidence >= 0.7:
            # Guard: if message has an explicit time, it's a reminder — not a pending task.
            # The LLM sometimes misclassifies complex recurring reminders as pending_task.
            _has_explicit_time = bool(re.search(r'\ba las\s+\d{1,2}|\ben\s+\d+\s+min', lowered))
            if _has_explicit_time:
                # Try reminder parser first — fall through to pending_task only if it fails
                _parsed_check = await parse_reminder_ai(
                    text_in, context=_get_recent_context(db, user.id),
                    memory_context=system_prompt
                ) or parse_reminder(text_in, context=_get_recent_context(db, user.id))
                if _parsed_check:
                    # Let it fall through to the create_reminder block below
                    intent = "create_reminder"
                    parsed = _parsed_check
                else:
                    pt = extract_pending_task(lowered)
                    return await handle_pending_task(db, user, chat_id, pt or text_in, url=_extracted_url)
            else:
                pt = extract_pending_task(lowered)
                return await handle_pending_task(db, user, chat_id, pt or text_in, url=_extracted_url)

        # ── Create reminder ───────────────────────────────────────────────
        if intent in ("create_reminder", "unknown") or confidence < 0.7:
            if not parsed:  # may already be set by pending_task guard above
                parsed = await parse_reminder_ai(text_in, context=_get_recent_context(db, user.id),
                                                 memory_context=system_prompt) or \
                         parse_reminder(text_in, context=_get_recent_context(db, user.id))
        elif intent != "create_reminder":
            parsed = None

        if parsed:
            reminder = Reminder(
                user_id=user.id, source_text=text_in, task_text=parsed["task_text"],
                remind_at=parsed["remind_at"], status=parsed["status"],
                recurrence_type=parsed["recurrence_type"], recurrence_value=parsed["recurrence_value"],
                weekdays_only=parsed["weekdays_only"], remind_if_no_response=parsed["remind_if_no_response"],
                retry_delay_minutes=parsed["retry_delay_minutes"],
                cancel_on_event_type=parsed["cancel_on_event_type"],
                is_persistent=parsed.get("is_persistent", False),
                repeat_every_minutes=parsed.get("repeat_every_minutes"),
                stop_at=parsed.get("stop_at"), awaiting_ack=parsed.get("awaiting_ack", False),
            )
            try:
                reminder.priority = await infer_priority(reminder.task_text)
            except Exception:
                reminder.priority = "P3"
            db.add(reminder)
            db.commit()
            db.refresh(reminder)
            db.add(Event(user_id=user.id, event_type="reminder_created",
                         event_value=str(reminder.id), source="telegram",
                         payload={"source_text": text_in, "task_text": reminder.task_text,
                                  "mode": parsed.get("mode"),
                                  "is_persistent": parsed.get("is_persistent", False)}))
            db.commit()
            reply_text = await build_reply_ai(text_in, parsed, reminder.id, memory_context=system_prompt) or \
                         build_confirmation_text_from_parsed(text_in, parsed, reminder.id)
            await send_message(chat_id, reply_text)
            db.add(Message(user_id=user.id, direction="outbound",
                           message_text=reply_text, message_type="reminder_confirmation"))
            db.commit()
            return {"status": "ok", "action": "reminder_created", "reminder_id": reminder.id}

        # ── Chat reply fallback ───────────────────────────────────────────
        if intent == "chat" and confidence >= 0.7:
            chat_reply = await chat_reply_ai(text_in, memory_context=system_prompt)
            if chat_reply:
                await send_and_log(db, user.id, chat_id, chat_reply, "chat_reply")
                return {"status": "ok", "action": "chat_reply"}

        if not parsed:
            chat_reply = await chat_reply_ai(text_in, memory_context=system_prompt)
            if chat_reply:
                await send_and_log(db, user.id, chat_id, chat_reply, "chat_reply")
                return {"status": "ok", "action": "chat_reply"}

        # ── Help text (last resort) ───────────────────────────────────────
        help_text = build_help_text()
        await send_message(chat_id, help_text)
        db.add(Message(user_id=user.id, direction="outbound",
                       message_text=help_text, message_type="help"))
        db.commit()
        return {"status": "ok", "action": "help_sent"}

    except Exception as exc:
        db.rollback()
        print("=== TELEGRAM WEBHOOK ERROR ===")
        try:    print("PAYLOAD:", payload)
        except: print("PAYLOAD: <unavailable>")
        print("ERROR:", repr(exc))
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"status": "error", "reason": str(exc)})
    finally:
        db.close()



async def _handle_photo_message(message: dict) -> dict:
    """Handle Telegram photo messages — create task + upload attachment."""
    import mimetypes as _mt
    import httpx as _hx

    chat    = message.get("chat") or {}
    chat_id = chat.get("id")
    if not chat_id:
        return {"status": "ignored", "reason": "missing_chat_id"}

    caption       = message.get("caption", "") or ""
    _cap_tags     = extract_tags(caption)
    tags_raw      = tags_str(_cap_tags)
    caption_clean = remove_tags(caption).strip()
    task_title    = caption_clean or "Revisar screenshot"
    _is_content   = is_content_tag(_cap_tags)

    SELF_API = os.getenv("SELF_API_URL", "http://localhost:8000")

    db = SessionLocal()
    try:
        user = ur.get_by_chat_id(db, chat_id)
        if not user:
            return {"status": "ignored", "reason": "user_not_found"}

        # ── Step 1: Download photo ────────────────────────────────────────
        photos     = message.get("photo", [])
        best_photo = max(photos, key=lambda p: p.get("file_size", 0))
        file_id    = best_photo.get("file_id")
        print(f"[capture:photo] step1 get_file file_id={file_id[:12]}...")
        file_path = await tg.get_file(file_id)
        if not file_path:
            print(f"[capture:photo] ❌ step1 failed: could not resolve file_id={file_id[:12]}")
            await send_message(chat_id, "❌ No pude descargar la imagen (error al obtener ruta). Prueba de nuevo.")
            return {"status": "error", "reason": "get_file_failed"}

        print(f"[capture:photo] step1 ✅ file_path={file_path}")
        img_bytes = await tg.download_file(file_path)
        if not img_bytes:
            print(f"[capture:photo] ❌ step1 failed: could not download file_path={file_path}")
            await send_message(chat_id, "❌ No pude descargar la imagen (error de red). Prueba de nuevo.")
            return {"status": "error", "reason": "download_failed"}

        img_ext  = file_path.split(".")[-1] if "." in file_path else "jpg"
        img_name = f"screenshot_{file_id[:8]}.{img_ext}"
        print(f"[capture:photo] step1 ✅ downloaded {len(img_bytes)} bytes as {img_name}")

        # ── Step 2: Infer priority ────────────────────────────────────────
        try:
            _photo_prio = await infer_priority(task_title)
        except Exception:
            _photo_prio = "P3"

        # ── Step 3: Create Focalboard card ───────────────────────────────
        _photo_board = CONTENT_BOARD_ID if _is_content else os.getenv("FOCALBOARD_BOARD_ID", "")
        from sync_service import STATUS_OPTIONS, PRIORITY_OPTIONS, STATUS_PROP_ID, PRIORITY_PROP_ID
        fb_props = {STATUS_PROP_ID: STATUS_OPTIONS.get("pending", "aoptpendiente00000000000001")}
        if _photo_prio in PRIORITY_OPTIONS:
            fb_props[PRIORITY_PROP_ID] = PRIORITY_OPTIONS[_photo_prio]
        if tags_raw:
            fb_props["a6bxuk4rgxp7wn6bashiadwaiiy"] = tags_raw

        print(f"[capture:photo] step3 creating card title=\'{task_title}\' board={_photo_board}")
        fb_id = await fb.create_card(task_title, fb_props, board_id=_photo_board)
        if not fb_id:
            import uuid as _uuid2
            fb_id = _uuid2.uuid4().hex[:26]
            print(f"[capture:photo] step3 ⚠️ Focalboard creation failed, using local ID={fb_id}")
        else:
            print(f"[capture:photo] step3 ✅ card created fb_id={fb_id}")

        # ── Step 4: Save reminder in DB ───────────────────────────────────
        _final_tags = tags_raw
        if _is_content:
            if _final_tags and "#contenido" not in _final_tags.lower():
                _final_tags = f"{_final_tags} #contenido".strip()
            elif not _final_tags:
                _final_tags = "#contenido"

        pending_reminder = Reminder(
            user_id=user.id, source_text=f"photo:{file_id[:16]}",
            task_text=task_title, remind_at=datetime.now(TZ).replace(year=2099),
            status="pending", notes=None, tags=_final_tags,
            priority=_photo_prio, focalboard_card_id=fb_id,
            focalboard_synced_at=datetime.now(TZ),
        )
        db.add(pending_reminder)
        db.commit()
        db.refresh(pending_reminder)
        print(f"[capture:photo] step4 ✅ reminder saved id={pending_reminder.id}")

        # ── Step 5: Upload attachment ─────────────────────────────────────
        mime   = _mt.guess_type(img_name)[0] or "image/jpeg"
        print(f"[capture:photo] step5 uploading attachment to /tasks/{pending_reminder.id}/attachments")
        try:
            async with _hx.AsyncClient(timeout=30) as client:
                att_r  = await client.post(f"{SELF_API}/tasks/{pending_reminder.id}/attachments",
                                           files={"file": (img_name, img_bytes, mime)})
                att_ok = att_r.status_code == 200
                if att_ok:
                    print(f"[capture:photo] step5 ✅ attachment uploaded")
                else:
                    print(f"[capture:photo] step5 ❌ HTTP={att_r.status_code} body={att_r.text[:200]}")
        except Exception as att_exc:
            att_ok = False
            print(f"[capture:photo] step5 ❌ exception: {att_exc}")

        # ── Step 6: Reply ─────────────────────────────────────────────────
        _tags_display = ""
        if _final_tags:
            _tc = " ".join(t for t in _final_tags.split() if t.lower() != "#contenido")
            if _tc: _tags_display = f"\n🏷️ {_tc}"

        _att_note = "." if att_ok else " (imagen guardada, adjunto pendiente de sincronizar)."
        reply = (
            f'💡 Idea de contenido guardada [{pending_reminder.id}]: "{task_title}"\n'
            f'🖼️ Screenshot adjunto{_att_note}\n'
            f'📋 Estado: Idea → /contenido{_tags_display}'
        ) if _is_content else (
            f'📌 Guardado para revisar más tarde [{pending_reminder.id}]: "{task_title}"\n'
            f'🖼️ Screenshot adjunto{_att_note}{_tags_display}'
        )
        await send_message(chat_id, reply)
        db.add(Message(user_id=user.id, direction="outbound",
                       message_text=reply, message_type="photo_task"))
        db.commit()
        return {"status": "ok", "action": "photo_task_created",
                "reminder_id": pending_reminder.id, "attachment_ok": att_ok}

    except Exception as exc:
        print(f"[capture:photo] ❌ unhandled error: {exc}")
        traceback.print_exc()
        try:
            await send_message(chat_id,
                "❌ No pude guardar la imagen. Revisa los logs del servidor para más detalles.")
        except Exception:
            pass
        return {"status": "error", "reason": str(exc)}
    finally:
        db.close()


async def _handle_document_message(message: dict) -> dict:
    """
    Handle Telegram document (PDF, file) messages.
    Minimal safe implementation — same pattern as photo handler.
    """
    import mimetypes as _mt
    import httpx as _hx

    chat    = message.get("chat") or {}
    chat_id = chat.get("id")
    if not chat_id:
        return {"status": "ignored", "reason": "missing_chat_id"}

    doc      = message.get("document", {})
    file_id  = doc.get("file_id")
    filename = doc.get("file_name") or "documento"
    mime_in  = doc.get("mime_type") or ""

    ALLOWED = {"image/jpeg", "image/png", "image/gif", "image/webp",
               "application/pdf", "text/plain"}
    if mime_in and mime_in not in ALLOWED:
        print(f"[capture:document] unsupported mime_type={mime_in} filename={filename}")
        await send_message(chat_id,
            f"⚠️ Tipo de archivo no soportado ({mime_in}). Soportados: PDF, imágenes, texto.")
        return {"status": "ignored", "reason": "unsupported_mime"}

    caption    = message.get("caption", "") or ""
    _cap_tags  = extract_tags(caption)
    tags_raw   = tags_str(_cap_tags)
    cap_clean  = remove_tags(caption).strip()
    task_title = cap_clean or (filename_to_title(filename) if filename else "Documento adjunto")
    _is_content = is_content_tag(_cap_tags)

    SELF_API = os.getenv("SELF_API_URL", "http://localhost:8000")

    db = SessionLocal()
    try:
        user = ur.get_by_chat_id(db, chat_id)
        if not user:
            return {"status": "ignored", "reason": "user_not_found"}

        print(f"[capture:document] step1 get_file file_id={str(file_id)[:12]}...")
        file_path = await tg.get_file(file_id)
        if not file_path:
            await send_message(chat_id, "❌ No pude descargar el documento. Prueba de nuevo.")
            return {"status": "error", "reason": "get_file_failed"}

        doc_bytes = await tg.download_file(file_path)
        if not doc_bytes:
            await send_message(chat_id, "❌ No pude descargar el documento (error de red).")
            return {"status": "error", "reason": "download_failed"}

        print(f"[capture:document] step1 ✅ {len(doc_bytes)} bytes — {filename}")

        _doc_board = CONTENT_BOARD_ID if _is_content else os.getenv("FOCALBOARD_BOARD_ID", "")
        from sync_service import STATUS_OPTIONS, PRIORITY_OPTIONS, STATUS_PROP_ID, PRIORITY_PROP_ID
        try:
            _prio = await infer_priority(task_title)
        except Exception:
            _prio = "P3"

        fb_props = {STATUS_PROP_ID: STATUS_OPTIONS.get("pending", "aoptpendiente00000000000001")}
        if _prio in PRIORITY_OPTIONS:
            fb_props[PRIORITY_PROP_ID] = PRIORITY_OPTIONS[_prio]
        if tags_raw:
            fb_props["a6bxuk4rgxp7wn6bashiadwaiiy"] = tags_raw

        fb_id = await fb.create_card(task_title, fb_props, board_id=_doc_board)
        if not fb_id:
            import uuid as _uuid2
            fb_id = _uuid2.uuid4().hex[:26]

        _final_tags = tags_raw
        if _is_content:
            _final_tags = ((_final_tags + " #contenido").strip()) if _final_tags else "#contenido"

        pending_reminder = Reminder(
            user_id=user.id, source_text=f"doc:{str(file_id)[:16]}",
            task_text=task_title, remind_at=datetime.now(TZ).replace(year=2099),
            status="pending", notes=cap_clean or None, tags=_final_tags,
            priority=_prio, focalboard_card_id=fb_id,
            focalboard_synced_at=datetime.now(TZ),
        )
        db.add(pending_reminder)
        db.commit()
        db.refresh(pending_reminder)
        print(f"[capture:document] step3 ✅ reminder saved id={pending_reminder.id}")

        mime_out = mime_in or _mt.guess_type(filename)[0] or "application/octet-stream"
        att_ok = False
        try:
            async with _hx.AsyncClient(timeout=60) as client:
                att_r  = await client.post(f"{SELF_API}/tasks/{pending_reminder.id}/attachments",
                                           files={"file": (filename, doc_bytes, mime_out)})
                att_ok = att_r.status_code == 200
                if not att_ok:
                    print(f"[capture:document] step4 ❌ HTTP={att_r.status_code} body={att_r.text[:200]}")
        except Exception as att_exc:
            print(f"[capture:document] step4 ❌ exception: {att_exc}")

        _tags_display = f"\n🏷️ {tags_raw}" if tags_raw else ""
        _att_note = "." if att_ok else " (guardado, adjunto pendiente de sincronizar)."
        reply = f'📎 Documento guardado [{pending_reminder.id}]: "{task_title}"\n📄 {filename}{_att_note}{_tags_display}'
        await send_message(chat_id, reply)
        db.add(Message(user_id=user.id, direction="outbound",
                       message_text=reply, message_type="doc_task"))
        db.commit()
        return {"status": "ok", "action": "doc_task_created",
                "reminder_id": pending_reminder.id, "attachment_ok": att_ok}

    except Exception as exc:
        print(f"[capture:document] ❌ unhandled error: {exc}")
        traceback.print_exc()
        try:
            await send_message(chat_id, "❌ No pude guardar el documento.")
        except Exception:
            pass
        return {"status": "error", "reason": str(exc)}
    finally:
        db.close()