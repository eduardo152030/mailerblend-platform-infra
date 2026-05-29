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
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import select

from db import SessionLocal
from models import Reminder, Event, User, Message
from scheduler import (
    to_local,
    next_occurrence,
    should_cancel_due_to_event,
    build_due_text,
    build_due_text_ai,
    build_expired_text,
    is_digest_time,
    send_daily_digest_to_all,
    check_content_publication_reminders,
    DAILY_DIGEST_HOUR,
    DAILY_DIGEST_MINUTE,
)
from undated_tasks_reminder import check_undated_tasks
from publishing_channels import check_publishing_reminders
from telegram_service import send_message

TZ = ZoneInfo(os.getenv("TIMEZONE", "Europe/Madrid"))
POLL_INTERVAL = int(os.getenv("SCHEDULER_POLL_SECONDS", "30"))

# Evita enviar el digest dos veces en el mismo minuto


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
                text_out = await build_due_text_ai(r)
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
                    # Expire when:
                    # - stop_at has passed (now >= stop_at)
                    # - AND stop_at is not in the future relative to remind_at
                    #   (if stop_at > remind_at it means this cycle hasn't started yet)
                    should_expire = (
                        now >= stop_local and
                        stop_local <= to_local(r.remind_at) + timedelta(hours=24)
                    )

                    if should_expire:
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
                        print(f"[scheduler] reminder {r.id} expired (stop_at={stop_local})")
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

                text_out = await build_due_text_ai(r)
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
    """
    Envía el digest diario a las 08:00.
    Estado persistido en DB — sobrevive reinicios del contenedor.
    """
    now = datetime.now(TZ)
    if not is_digest_time(now):
        return

    db = SessionLocal()
    try:
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        already_sent = db.execute(
            select(Event)
            .where(Event.event_type == "daily_digest_sent")
            .where(Event.created_at >= today_start)
            .limit(1)
        ).scalars().first()
        if already_sent:
            return

        sent = await send_daily_digest_to_all(db, _send_telegram)
        db.add(Event(
            user_id=None,
            event_type="daily_digest_sent",
            event_value=str(sent),
            source="scheduler",
            payload={"date": str(now.date()), "users": sent},
        ))
        db.commit()
        print(f"[scheduler] daily digest sent to {sent} users")
    except Exception as exc:
        print(f"[scheduler] ERROR sending daily digest: {exc}")
        traceback.print_exc()
    finally:
        db.close()


_weekly_cleanup_done: str = ""  # tracks last weekly cleanup (YYYY-WW format)


async def process_publishing_reminders() -> None:
    """
    Revisa canales de publicación a las 09:00.
    Estado persistido en DB — sobrevive reinicios del contenedor.
    """
    now = datetime.now(TZ)
    if now.hour != 9 or now.minute not in range(0, 6):
        return
    db = SessionLocal()
    try:
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        already_sent = db.execute(
            select(Event)
            .where(Event.event_type == "publishing_reminders_sent")
            .where(Event.created_at >= today_start)
            .limit(1)
        ).scalars().first()
        if already_sent:
            return
        sent = await check_publishing_reminders(_send_telegram)
        db.add(Event(
            user_id=None,
            event_type="publishing_reminders_sent",
            event_value=str(sent),
            source="scheduler",
            payload={"date": str(now.date()), "count": sent},
        ))
        db.commit()
        if sent:
            print(f"[scheduler] publishing reminders sent: {sent}")
    except Exception as exc:
        print(f"[scheduler] ERROR publishing reminders: {exc}")
    finally:
        db.close()


async def process_content_reminders() -> None:
    """
    Revisa recordatorios de contenido a las 20:00.
    Estado persistido en DB — sobrevive reinicios del contenedor.
    """
    now = datetime.now(TZ)
    if now.hour != 20 or now.minute not in range(0, 6):
        return
    db = SessionLocal()
    try:
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        already_sent = db.execute(
            select(Event)
            .where(Event.event_type == "content_reminders_sent")
            .where(Event.created_at >= today_start)
            .limit(1)
        ).scalars().first()
        if already_sent:
            return
        sent = await check_content_reminders(_send_telegram)
        db.add(Event(
            user_id=None,
            event_type="content_reminders_sent",
            event_value=str(sent),
            source="scheduler",
            payload={"date": str(now.date()), "count": sent},
        ))
        db.commit()
        if sent:
            print(f"[scheduler] content reminders sent: {sent}")
    except Exception as exc:
        print(f"[scheduler] ERROR content reminders: {exc}")
    finally:
        db.close()


_weekly_cleanup_done: str = ""  # tracks last weekly cleanup (YYYY-WW format)


async def process_undated_tasks() -> None:
    """
    Revisa tareas sin fecha a las 09:30 cada día.
    Estado persistido en DB (events) — sobrevive reinicios del contenedor.
    """
    now = datetime.now(TZ)
    if now.hour != 9 or now.minute not in range(30, 36):
        return

    # Check DB — did we already send today?
    db = SessionLocal()
    try:
        from sqlalchemy import func
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        already_sent = db.execute(
            select(Event)
            .where(Event.event_type == "undated_tasks_alert")
            .where(Event.created_at >= today_start)
            .limit(1)
        ).scalars().first()
        if already_sent:
            return

        try:
            sent = await check_undated_tasks(_send_telegram)
            if sent:
                # Record in DB so restarts don't re-send
                db.add(Event(
                    user_id=None,
                    event_type="undated_tasks_alert",
                    event_value=str(sent),
                    source="scheduler",
                    payload={"date": str(now.date()), "count": sent},
                ))
                db.commit()
                print(f"[scheduler] undated task alerts sent: {sent}")
        except Exception as exc:
            print(f"[scheduler] ERROR undated tasks: {exc}")
    finally:
        db.close()


async def process_weekly_cleanup() -> None:
    """
    Every Sunday at 10:00 — delete all completed and cancelled reminders
    from DB and their Focalboard cards.

    Runs silently (no Telegram notification) — it's background maintenance.
    To debug: docker logs eva-scheduler | grep weekly_cleanup
    """
    global _weekly_cleanup_done
    now = datetime.now(TZ)

    # Only on Sundays (weekday=6) at 10:00
    if now.weekday() != 6 or now.hour != 10 or now.minute != 0:
        return

    # Deduplicate — only run once per week (keyed by year+week number)
    week_key = f"{now.year}-W{now.isocalendar()[1]}"
    if _weekly_cleanup_done == week_key:
        return

    db = SessionLocal()
    try:
        from integrations import focalboard_client as fb

        rows = db.execute(
            select(Reminder).where(Reminder.status.in_(["completed", "cancelled"]))
        ).scalars().all()

        if not rows:
            print(f"[scheduler] weekly_cleanup: nothing to clean")
            _weekly_cleanup_done = week_key
            return

        deleted_fb = 0
        for r in rows:
            if r.focalboard_card_id and fb.is_configured():
                try:
                    if await fb.delete_card(r.focalboard_card_id):
                        deleted_fb += 1
                except Exception as exc:
                    print(f"[scheduler] weekly_cleanup: FB delete error {r.id}: {exc}")

        count = len(rows)
        for r in rows:
            db.delete(r)

        db.add(Event(
            user_id=rows[0].user_id if rows else None,
            event_type="weekly_cleanup",
            event_value=str(count),
            source="scheduler",
            payload={"deleted_db": count, "deleted_fb": deleted_fb, "week": week_key},
        ))
        db.commit()
        _weekly_cleanup_done = week_key
        print(f"[scheduler] weekly_cleanup ✅ — deleted {count} reminders "
              f"({deleted_fb} Focalboard cards) — week {week_key}")

    except Exception as exc:
        db.rollback()
        print(f"[scheduler] weekly_cleanup ERROR: {exc}")
        traceback.print_exc()
    finally:
        db.close()


async def main_loop() -> None:
    print(f"[scheduler] Starting EVA scheduler (poll every {POLL_INTERVAL}s, digest at {DAILY_DIGEST_HOUR:02d}:{DAILY_DIGEST_MINUTE:02d} {TZ})")

    while True:
        try:
            await process_reminders()
            await process_daily_digest()
            await process_content_reminders()
            await process_publishing_reminders()
            await process_undated_tasks()
            await process_weekly_cleanup()
        except Exception as exc:
            print(f"[scheduler] Unhandled error in main loop: {exc}")
            traceback.print_exc()

        await asyncio.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    asyncio.run(main_loop())