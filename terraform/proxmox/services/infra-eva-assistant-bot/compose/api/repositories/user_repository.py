"""
repositories/user_repository.py
=====================================
All SQLAlchemy queries for the User model.

Rules:
  - No HTTP calls here.
  - No business logic here.
  - No commits here — callers control transactions.
  - Receives db session as argument.

To debug user lookup issues: inspect only this file.
"""
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import select

from models import User


def get_by_chat_id(db: Session, chat_id: int) -> Optional[User]:
    return db.execute(
        select(User).where(User.telegram_chat_id == chat_id)
    ).scalar_one_or_none()


def get_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.execute(
        select(User).where(User.id == user_id)
    ).scalar_one_or_none()


def get_default(db: Session) -> Optional[User]:
    """Return the first user — for single-user setups."""
    return db.execute(select(User).limit(1)).scalars().first()


def get_all(db: Session) -> list[User]:
    return db.execute(select(User)).scalars().all()
