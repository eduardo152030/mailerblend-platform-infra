"""
repositories/event_repository.py
=====================================
All SQLAlchemy queries for the Event model.

Rules:
  - No HTTP calls here.
  - No business logic here.
  - No commits here — callers control transactions.
  - Receives db session as argument.

To debug event logging issues: inspect only this file.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import select

from models import Event


def add(
    db: Session,
    user_id: int,
    event_type: str,
    event_value: str | None = None,
    source: str = "telegram",
    payload: dict | None = None,
) -> Event:
    """
    Create and add an Event to the session (does NOT commit).
    Caller is responsible for db.commit().
    """
    event = Event(
        user_id=user_id,
        event_type=event_type,
        event_value=event_value,
        source=source,
        payload=payload or {},
    )
    db.add(event)
    return event


def get_recent_for_user(
    db: Session,
    user_id: int,
    event_types: list[str],
    since: datetime,
    limit: int = 10,
) -> list[Event]:
    """Recent events of specified types since a given datetime."""
    return db.execute(
        select(Event)
        .where(Event.user_id == user_id)
        .where(Event.event_type.in_(event_types))
        .where(Event.created_at >= since)
        .order_by(Event.created_at.desc())
        .limit(limit)
    ).scalars().all()


def get_all(
    db: Session,
    user_id: int | None = None,
    event_type: str | None = None,
) -> list[Event]:
    q = select(Event).order_by(Event.id.desc())
    if user_id is not None:
        q = q.where(Event.user_id == user_id)
    if event_type:
        q = q.where(Event.event_type == event_type)
    return db.execute(q).scalars().all()
