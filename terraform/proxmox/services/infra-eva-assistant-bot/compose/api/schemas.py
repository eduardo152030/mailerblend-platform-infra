from typing import Any
from pydantic import BaseModel


class ParseCommandRequest(BaseModel):
    text: str


class CancelReminderRequest(BaseModel):
    reason: str | None = None


class EventCreateRequest(BaseModel):
    user_id: int | None = None
    event_type: str
    event_value: str | None = None
    source: str = "api"
    payload: dict[str, Any] = {}
