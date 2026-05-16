"""
repositories/reminder_repository.py
=====================================
All SQLAlchemy queries for the Reminder model.

Rules:
  - No HTTP calls here.
  - No business logic here.
  - No commits here — callers control transactions.
  - Receives db session as argument — never calls SessionLocal() internally.
  - Returns model instances or lists, never raw rows.

To debug reminder query issues: inspect only this file.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import select

from models import Reminder


def get_by_id(db: Session, reminder_id: int) -> Optional[Reminder]:
    return db.execute(
        select(Reminder).where(Reminder.id == reminder_id)
    ).scalar_one_or_none()


def get_by_id_and_user(db: Session, reminder_id: int, user_id: int) -> Optional[Reminder]:
    return db.execute(
        select(Reminder)
        .where(Reminder.id == reminder_id)
        .where(Reminder.user_id == user_id)
    ).scalar_one_or_none()


def get_by_card_id(db: Session, card_id: str) -> Optional[Reminder]:
    return db.execute(
        select(Reminder).where(Reminder.focalboard_card_id == card_id)
    ).scalar_one_or_none()


def get_active_for_user(db: Session, user_id: int) -> list[Reminder]:
    """Scheduled/pending reminders ordered by remind_at."""
    return db.execute(
        select(Reminder)
        .where(Reminder.user_id == user_id)
        .where(Reminder.status.in_(["pending", "scheduled"]))
        .order_by(Reminder.remind_at.asc())
    ).scalars().all()


def get_awaiting_ack_for_user(db: Session, user_id: int) -> list[Reminder]:
    """Reminders in sent+awaiting_ack state, most recent first."""
    return db.execute(
        select(Reminder)
        .where(Reminder.user_id == user_id)
        .where(Reminder.status == "sent")
        .where(Reminder.awaiting_ack.is_(True))
        .order_by(Reminder.last_sent_at.desc().nullslast())
    ).scalars().all()


def get_pending_ack_or_sent(
    db: Session,
    user_id: int,
    since: datetime | None = None,
) -> Optional[Reminder]:
    """
    Most recent reminder that needs a user response.
    Used for ACK / snooze detection.
    """
    q = (
        select(Reminder)
        .where(Reminder.user_id == user_id)
        .where(
            (Reminder.awaiting_ack.is_(True)) |
            (Reminder.status == "sent")
        )
    )
    if since is not None:
        q = q.where(
            (Reminder.awaiting_ack.is_(True)) |
            (Reminder.status == "sent") |
            (
                (Reminder.last_sent_at >= since) &
                (Reminder.status.in_(["sent", "scheduled"]))
            )
        )
    q = q.order_by(Reminder.last_sent_at.desc().nullslast(), Reminder.id.desc()).limit(1)
    return db.execute(q).scalars().first()


def get_cancellable_for_user(db: Session, user_id: int) -> list[Reminder]:
    """All active reminders that can be cancelled."""
    return db.execute(
        select(Reminder)
        .where(Reminder.user_id == user_id)
        .where(Reminder.status.in_(["pending", "scheduled", "sent"]))
        .order_by(Reminder.remind_at.asc(), Reminder.id.desc())
    ).scalars().all()


def get_active_on_date(
    db: Session,
    user_id: int,
    target_date,
) -> list[Reminder]:
    """Active reminders whose remind_at falls on target_date."""
    from scheduler import to_local
    rows = get_cancellable_for_user(db, user_id)
    return [r for r in rows if to_local(r.remind_at) and to_local(r.remind_at).date() == target_date]


def get_all_by_status(db: Session, user_id: int, statuses: list[str]) -> list[Reminder]:
    return db.execute(
        select(Reminder)
        .where(Reminder.user_id == user_id)
        .where(Reminder.status.in_(statuses))
    ).scalars().all()


def get_next_scheduled(db: Session, user_id: int) -> Optional[Reminder]:
    """Next upcoming scheduled/pending reminder."""
    return db.execute(
        select(Reminder)
        .where(Reminder.user_id == user_id)
        .where(Reminder.status.in_(["scheduled", "pending"]))
        .order_by(Reminder.remind_at.asc())
        .limit(1)
    ).scalars().first()


def get_last_scheduled(db: Session, user_id: int) -> Optional[Reminder]:
    """Most recently created scheduled/pending reminder."""
    return db.execute(
        select(Reminder)
        .where(Reminder.user_id == user_id)
        .where(Reminder.status.in_(["scheduled", "pending"]))
        .order_by(Reminder.id.desc())
        .limit(1)
    ).scalars().first()


def get_last_with_card(db: Session, user_id: int) -> Optional[Reminder]:
    """Most recently created reminder that has a Focalboard card."""
    return db.execute(
        select(Reminder)
        .where(Reminder.user_id == user_id)
        .where(Reminder.focalboard_card_id.isnot(None))
        .order_by(Reminder.id.desc())
        .limit(1)
    ).scalars().first()


def get_all_for_user_ordered(db: Session, user_id: int) -> list[Reminder]:
    return db.execute(
        select(Reminder)
        .where(Reminder.user_id == user_id)
        .order_by(Reminder.id.desc())
    ).scalars().all()


def get_all_active(db: Session) -> list[Reminder]:
    """All active reminders across all users (for task list endpoint)."""
    return db.execute(
        select(Reminder)
        .where(Reminder.status.in_(["pending", "scheduled", "sent"]))
        .order_by(Reminder.remind_at.asc())
    ).scalars().all()


def get_all_ordered(db: Session, status: str | None = None) -> list[Reminder]:
    q = select(Reminder).order_by(Reminder.id.desc())
    if status:
        q = q.where(Reminder.status == status)
    return db.execute(q).scalars().all()


def get_awaiting_ack_active(db: Session, user_id: int) -> Optional[Reminder]:
    """Single most recent reminder with awaiting_ack=True."""
    return db.execute(
        select(Reminder)
        .where(Reminder.user_id == user_id)
        .where(Reminder.awaiting_ack.is_(True))
        .order_by(Reminder.last_sent_at.desc().nullslast())
        .limit(1)
    ).scalars().first()
