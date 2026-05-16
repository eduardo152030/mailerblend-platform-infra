"""
utils/time_utils.py
===================
Timezone helpers and model serializers.

Isolated here so:
- Timezone bugs → inspect only this file.
- Serializer changes (add/remove field) → inspect only this file.
"""
from datetime import datetime
from core.config import TZ
from models import Reminder, Event


def to_local(dt: datetime | None) -> datetime | None:
    """Convert any datetime to the app timezone. Handles naive datetimes."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=TZ)
    return dt.astimezone(TZ)


def serialize_reminder(r: Reminder) -> dict:
    return {
        "id": r.id,
        "user_id": r.user_id,
        "task_text": r.task_text,
        "source_text": r.source_text,
        "status": r.status,
        "remind_at": r.remind_at.isoformat() if r.remind_at else None,
        "recurrence_type": r.recurrence_type,
        "recurrence_value": r.recurrence_value,
        "weekdays_only": r.weekdays_only,
        "remind_if_no_response": r.remind_if_no_response,
        "retry_delay_minutes": r.retry_delay_minutes,
        "cancel_on_event_type": r.cancel_on_event_type,
        "is_persistent": getattr(r, "is_persistent", False),
        "repeat_every_minutes": getattr(r, "repeat_every_minutes", None),
        "stop_at": r.stop_at.isoformat() if getattr(r, "stop_at", None) else None,
        "awaiting_ack": getattr(r, "awaiting_ack", False),
        "retry_count": getattr(r, "retry_count", 0),
        "max_retries": getattr(r, "max_retries", 0),
        "created_at": r.created_at.isoformat() if r.created_at else None,
        "sent_at": r.sent_at.isoformat() if r.sent_at else None,
        "last_sent_at": r.last_sent_at.isoformat() if r.last_sent_at else None,
        "acked_at": r.acked_at.isoformat() if r.acked_at else None,
        "completed_at": r.completed_at.isoformat() if getattr(r, "completed_at", None) else None,
        "expired_at": r.expired_at.isoformat() if getattr(r, "expired_at", None) else None,
        "cancelled_at": r.cancelled_at.isoformat() if getattr(r, "cancelled_at", None) else None,
        "ack_text": getattr(r, "ack_text", None),
        "error_message": r.error_message,
    }


def serialize_event(e: Event) -> dict:
    return {
        "id": e.id,
        "user_id": e.user_id,
        "event_type": e.event_type,
        "event_value": e.event_value,
        "source": e.source,
        "payload": e.payload,
        "created_at": e.created_at.isoformat() if e.created_at else None,
    }
