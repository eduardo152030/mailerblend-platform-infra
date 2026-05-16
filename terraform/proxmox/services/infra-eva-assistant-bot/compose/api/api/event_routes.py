"""
api/event_routes.py
===================
REST endpoints for system events.
To debug event logging issues: inspect only this file.
"""
from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import select

from db import SessionLocal
from models import Event
from utils.time_utils import serialize_event

router = APIRouter()


class EventCreateRequest(BaseModel):
    user_id: int | None = None
    event_type: str
    event_value: str | None = None
    source: str = "api"
    payload: dict = {}


@router.post("/events")
async def create_event(body: EventCreateRequest):
    db = SessionLocal()
    try:
        event = Event(
            user_id=body.user_id,
            event_type=body.event_type,
            event_value=body.event_value,
            source=body.source,
            payload=body.payload,
        )
        db.add(event)
        db.commit()
        db.refresh(event)
        return {"status": "ok", "item": serialize_event(event)}
    finally:
        db.close()


@router.get("/events")
async def list_events(user_id: int | None = None, event_type: str | None = None):
    db = SessionLocal()
    try:
        stmt = select(Event).order_by(Event.id.desc())
        if user_id is not None:
            stmt = stmt.where(Event.user_id == user_id)
        if event_type:
            stmt = stmt.where(Event.event_type == event_type)
        rows = db.execute(stmt).scalars().all()
        return {"items": [serialize_event(e) for e in rows]}
    finally:
        db.close()
