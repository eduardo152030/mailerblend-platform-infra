"""
repositories/message_repository.py
=====================================
All SQLAlchemy queries for the Message model.

Rules:
  - No HTTP calls here.
  - No business logic here.
  - No commits here — callers control transactions.
  - Receives db session as argument.

To debug message history issues: inspect only this file.
"""
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import select

from models import Message


def get_last_outbound(db: Session, user_id: int) -> Optional[Message]:
    """Most recent outbound message from EVA to the user."""
    return db.execute(
        select(Message)
        .where(Message.user_id == user_id)
        .where(Message.direction == "outbound")
        .order_by(Message.id.desc())
        .limit(1)
    ).scalars().first()


def get_last_inbound(db: Session, user_id: int, limit: int = 2) -> list[Message]:
    """Most recent inbound messages from the user."""
    return db.execute(
        select(Message)
        .where(Message.user_id == user_id)
        .where(Message.direction == "inbound")
        .order_by(Message.id.desc())
        .limit(limit)
    ).scalars().all()


def get_recent(db: Session, user_id: int, limit: int = 5) -> list[dict]:
    """
    Last N messages for conversational context.
    Returns list of {"direction": str, "text": str} dicts (not model instances)
    so callers don't need to import Message.
    """
    rows = db.execute(
        select(Message)
        .where(Message.user_id == user_id)
        .order_by(Message.id.desc())
        .limit(limit)
    ).scalars().all()
    return [{"direction": m.direction, "text": m.message_text} for m in reversed(rows)]


def get_last_outbound_few(db: Session, user_id: int, limit: int = 3) -> list[Message]:
    """Last N outbound messages (for context checks like cancel_all_date)."""
    return db.execute(
        select(Message)
        .where(Message.user_id == user_id)
        .where(Message.direction == "outbound")
        .order_by(Message.id.desc())
        .limit(limit)
    ).scalars().all()


def add(db: Session, user_id: int, direction: str, text: str, message_type: str) -> Message:
    """
    Create and add a Message to the session (does NOT commit).
    Caller is responsible for db.commit().
    """
    msg = Message(
        user_id=user_id,
        direction=direction,
        message_text=text,
        message_type=message_type,
    )
    db.add(msg)
    return msg
