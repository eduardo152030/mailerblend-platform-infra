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
from scheduler import to_local

TZ = ZoneInfo(os.getenv("TIMEZONE", "Europe/Madrid"))
POLL_INTERVAL   = int(os.getenv("SYNC_POLL_SECONDS", "60"))
FOCALBOARD_URL  = os.getenv("FOCALBOARD_URL", "http://focalboard:8000")
FOCALBOARD_TOKEN   = os.getenv("FOCALBOARD_TOKEN", "")
FOCALBOARD_BOARD_ID = os.getenv("FOCALBOARD_BOARD_ID", "")

# IDs fijos de la propiedad "Status EVA" creada en el board
STATUS_PROP_ID = "aevastatus00000000000000001"
DATE_PROP_ID   = "a14y4uzprb1maieayt1ouhca47o"
STATUS_OPTIONS = {
    "scheduled": "aoptpendiente00000000000001",
    "pending":   "aoptpendiente00000000000001",
    "sent":      "aoptenviado000000000000001",
    "completed": "aoptcompletado0000000000001",
    "cancelled": "aoptcancelado00000000000001",
    "expired":   "aoptcancelado00000000000001",
}
# Inverso: option_id → status EVA
OPTION_TO_STATUS = {
    "aoptpendiente00000000000001":  "scheduled",
    "aoptenviado000000000000001":   "sent",
    "aoptcompletado0000000000001":  "completed",
    "aoptcancelado00000000000001":  "cancelled",
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
    # El valor debe ser un STRING no un objeto para que la UI lo renderice
    properties = {STATUS_PROP_ID: opt_id}
    if local_dt:
        import json as _json
        properties[DATE_PROP_ID] = _json.dumps({"from": int(local_dt.timestamp() * 1000)})

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


async def fb_update_card_status(card_id: str, status: str, remind_at=None) -> bool:
    opt_id = STATUS_OPTIONS.get(status, "opt_pendiente")
    props = {STATUS_PROP_ID: opt_id}
    if remind_at:
        local_dt = to_local(remind_at)
        if local_dt:
            import json as _json
            props[DATE_PROP_ID] = _json.dumps({"from": int(local_dt.timestamp() * 1000)})
    url = f"{FOCALBOARD_URL}/api/v2/boards/{FOCALBOARD_BOARD_ID}/blocks/{card_id}"
    async with httpx.AsyncClient(timeout=10) as c:
        r = await c.patch(url, headers=_h(), json={
            "updatedFields": {"properties": props}
        })
        ok = r.status_code in (200, 204)
        if ok:
            print(f"[sync] ✅ card {card_id} → {status}")
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
        rows = db.execute(
            select(Reminder)
            .where(Reminder.focalboard_card_id.is_(None))
            .where(Reminder.status.in_(["scheduled", "pending", "sent"]))
        ).scalars().all()
        # Limitar a 10 por ciclo para evitar crear muchos duplicados en caso de error
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
        ).scalars().all()

        for r in rows:
            try:
                ok = await fb_update_card_status(r.focalboard_card_id, r.status, r.remind_at)
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


async def sync_from_focalboard() -> int:
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
        for card in cards:
            cid = card.get("id")
            if not cid:
                continue

            reminder = db.execute(
                select(Reminder).where(Reminder.focalboard_card_id == cid)
            ).scalar_one_or_none()
            if not reminder:
                continue

            props = card.get("fields", {}).get("properties", {})
            opt_id = props.get(STATUS_PROP_ID)
            new_status = OPTION_TO_STATUS.get(opt_id)

            if not new_status or new_status == reminder.status:
                continue

            now = datetime.now(TZ)
            if new_status == "completed" and reminder.status != "completed":
                reminder.status = "completed"
                reminder.completed_at = now
                reminder.awaiting_ack = False
                db.add(Event(user_id=reminder.user_id, event_type="reminder_completed",
                    event_value=str(reminder.id), source="focalboard",
                    payload={"card_id": cid}))
                print(f"[sync] ✅ reminder {reminder.id} completed via Focalboard")
                synced += 1

            elif new_status == "cancelled" and reminder.status not in ("cancelled", "completed"):
                reminder.status = "cancelled"
                reminder.cancelled_at = now
                reminder.awaiting_ack = False
                reminder.error_message = "cancelled_via_focalboard"
                db.add(Event(user_id=reminder.user_id, event_type="reminder_cancelled",
                    event_value=str(reminder.id), source="focalboard",
                    payload={"card_id": cid}))
                print(f"[sync] ✅ reminder {reminder.id} cancelled via Focalboard")
                synced += 1

            _log(db, "reminder", reminder.id, "fb_to_eva", "update", cid)

        db.commit()
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
            if n1 or n2 or n3:
                print(f"[sync] cycle — new:{n1} status:{n2} fb→eva:{n3}")
        except Exception as exc:
            print(f"[sync] unhandled: {exc}")
            traceback.print_exc()
        await asyncio.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    asyncio.run(main_loop())