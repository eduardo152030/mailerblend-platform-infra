"""
run_scheduler.py — Loop principal del scheduler de EVA.

Este es el proceso que corre en el contenedor eva-scheduler.
Cada 30 segundos:
  1. Dispara recordatorios vencidos (scheduled/pending → sent)
  2. Reintenta persistentes con awaiting_ack
  3. Expira persistentes que superaron stop_at
  4. Reprograma recurrentes (weekly, weekdays)
  5. Cancela recordatorios si se cumplió cancel_on_event_type
  6. A las 08:00 (configurable) envía el resumen diario

Arranque: python run_scheduler.py
"""

import asyncio
import os
import traceback
from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import select

from db import SessionLocal
from models import Reminder, Event, User, Message
from scheduler import (
    to_local,
    next_occurrence,
    should_cancel_due_to_event,
    build_due_text,
    build_expired_text,
    is_digest_time,
    send_daily_digest_to_all,
    DAILY_DIGEST_HOUR,
    DAILY_DIGEST_MINUTE,
)
from telegram_service import send_message

TZ = ZoneInfo(os.getenv("TIMEZONE", "Europe/Madrid"))
POLL_INTERVAL = int(os.getenv("SCHEDULER_POLL_SECONDS", "30"))

# Evita enviar el digest dos veces en el mismo minuto
_digest_sent_today: str = ""


async def _send_telegram(chat_id: int, text: str, parse_mode: str = "MarkdownV2") -> None:
    await send_message(chat_id, text, parse_mode=parse_mode)


async def process_reminders() -> None:
    db = SessionLocal()
    try:
        now = datetime.now(TZ)

        # ── 1. Recordatorios vencidos ──────────────────────────────────────
        due = db.execute(
            select(Reminder)
            .where(Reminder.status.in_(["scheduled", "pending"]))
            .where(Reminder.remind_at <= now)
        ).scalars().all()

        for r in due:
            try:
                user = db.execute(
                    select(User).where(User.id == r.user_id)
                ).scalar_one_or_none()
                if not user or not user.telegram_chat_id:
                    continue

                # ¿Cancelar por evento externo?
                if should_cancel_due_to_event(db, r):
                    r.status = "cancelled"
                    r.cancelled_at = now
                    r.error_message = "cancelled_by_event"
                    db.add(Event(
                        user_id=r.user_id,
                        event_type="reminder_cancelled",
                        event_value=str(r.id),
                        source="scheduler",
                        payload={"reason": "cancel_on_event_type", "event_type": r.cancel_on_event_type},
                    ))
                    print(f"[scheduler] reminder {r.id} cancelled by event {r.cancel_on_event_type}")
                    continue

                # Enviar aviso
                text_out = build_due_text(r)
                await send_message(user.telegram_chat_id, text_out)

                r.status = "sent"
                r.sent_at = r.sent_at or now
                r.last_sent_at = now
                r.retry_count = (r.retry_count or 0) + 1

                if r.is_persistent:
                    r.awaiting_ack = True

                db.add(Message(
                    user_id=r.user_id,
                    direction="outbound",
                    message_text=text_out,
                    message_type="reminder_due",
                ))
                db.add(Event(
                    user_id=r.user_id,
                    event_type="reminder_sent",
                    event_value=str(r.id),
                    source="scheduler",
                    payload={"retry_count": r.retry_count},
                ))
                print(f"[scheduler] reminder {r.id} sent to user {r.user_id} → '{r.task_text}'")

            except Exception as exc:
                print(f"[scheduler] ERROR processing reminder {r.id}: {exc}")
                traceback.print_exc()

        db.commit()

        # ── 2. Persistentes: reintento ─────────────────────────────────────
        persistent = db.execute(
            select(Reminder)
            .where(Reminder.status == "sent")
            .where(Reminder.awaiting_ack.is_(True))
            .where(Reminder.is_persistent.is_(True))
        ).scalars().all()

        for r in persistent:
            try:
                # ¿Expirado?
                if r.stop_at:
                    stop_local = to_local(r.stop_at)
                    if now >= stop_local:
                        user = db.execute(select(User).where(User.id == r.user_id)).scalar_one_or_none()
                        if user and user.telegram_chat_id:
                            text_out = build_expired_text(r)
                            await send_message(user.telegram_chat_id, text_out)
                            db.add(Message(
                                user_id=r.user_id,
                                direction="outbound",
                                message_text=text_out,
                                message_type="reminder_expired",
                            ))
                        r.status = "expired"
                        r.expired_at = now
                        r.awaiting_ack = False
                        db.add(Event(
                            user_id=r.user_id,
                            event_type="reminder_expired",
                            event_value=str(r.id),
                            source="scheduler",
                            payload={},
                        ))
                        print(f"[scheduler] reminder {r.id} expired")
                        continue

                # ¿Es hora de reintentar?
                repeat_minutes = r.repeat_every_minutes or 2
                if r.last_sent_at:
                    last_local = to_local(r.last_sent_at)
                    elapsed = (now - last_local).total_seconds() / 60
                    if elapsed < repeat_minutes:
                        continue

                user = db.execute(select(User).where(User.id == r.user_id)).scalar_one_or_none()
                if not user or not user.telegram_chat_id:
                    continue

                text_out = build_due_text(r)
                await send_message(user.telegram_chat_id, text_out)

                r.last_sent_at = now
                r.retry_count = (r.retry_count or 0) + 1

                db.add(Message(
                    user_id=r.user_id,
                    direction="outbound",
                    message_text=text_out,
                    message_type="reminder_retry",
                ))
                db.add(Event(
                    user_id=r.user_id,
                    event_type="reminder_retried",
                    event_value=str(r.id),
                    source="scheduler",
                    payload={"retry_count": r.retry_count},
                ))
                print(f"[scheduler] reminder {r.id} retried ({r.retry_count}x) → '{r.task_text}'")

            except Exception as exc:
                print(f"[scheduler] ERROR retrying reminder {r.id}: {exc}")
                traceback.print_exc()

        db.commit()

        # ── 3. Recurrentes: reprogramar completados/enviados ───────────────
        sent_recurrent = db.execute(
            select(Reminder)
            .where(Reminder.status == "sent")
            .where(Reminder.awaiting_ack.is_(False))
            .where(Reminder.recurrence_type.isnot(None))
        ).scalars().all()

        for r in sent_recurrent:
            try:
                nxt = next_occurrence(r)
                if nxt:
                    r.remind_at = nxt
                    r.status = "scheduled"
                    r.sent_at = None
                    r.last_sent_at = None
                    r.retry_count = 0
                    print(f"[scheduler] reminder {r.id} rescheduled → {nxt}")
            except Exception as exc:
                print(f"[scheduler] ERROR rescheduling reminder {r.id}: {exc}")

        db.commit()

    except Exception as exc:
        db.rollback()
        print(f"[scheduler] CRITICAL ERROR in process_reminders: {exc}")
        traceback.print_exc()
    finally:
        db.close()


async def process_daily_digest() -> None:
    global _digest_sent_today
    now = datetime.now(TZ)

    if not is_digest_time(now):
        return

    # Clave única por día + hora para no enviar dos veces en el mismo minuto
    digest_key = f"{now.date()}_{now.hour}:{now.minute}"
    if _digest_sent_today == digest_key:
        return

    db = SessionLocal()
    try:
        sent = await send_daily_digest_to_all(db, _send_telegram)
        _digest_sent_today = digest_key
        print(f"[scheduler] daily digest sent to {sent} users")
    except Exception as exc:
        print(f"[scheduler] ERROR sending daily digest: {exc}")
        traceback.print_exc()
    finally:
        db.close()


async def main_loop() -> None:
    print(f"[scheduler] Starting EVA scheduler (poll every {POLL_INTERVAL}s, digest at {DAILY_DIGEST_HOUR:02d}:{DAILY_DIGEST_MINUTE:02d} {TZ})")

    while True:
        try:
            await process_reminders()
            await process_daily_digest()
        except Exception as exc:
            print(f"[scheduler] Unhandled error in main loop: {exc}")
            traceback.print_exc()

        await asyncio.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    asyncio.run(main_loop())