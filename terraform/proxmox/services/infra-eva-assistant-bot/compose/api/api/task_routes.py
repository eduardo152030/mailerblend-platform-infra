"""
api/task_routes.py
==================
Task management endpoints (CRUD, link-card, duplicate, description).
To debug UI task issues: inspect only this file.
"""
import re
import os
from datetime import datetime
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from sqlalchemy import select, text

from db import SessionLocal
from models import Reminder, User
from core.config import TZ, UPLOADS_DIR

router = APIRouter()


@router.post("/tasks/link-card")
async def link_card_to_task(request: Request):
    """Create or update a reminder linked to a Focalboard card. Called from UI."""
    db = SessionLocal()
    try:
        body      = await request.json()
        card_id   = body.get("focalboard_card_id", "").strip()
        task_text = body.get("task_text", "Tarea sin título").strip()
        status    = body.get("status", "pending")
        priority  = body.get("priority", "P3")

        if not card_id:
            return JSONResponse(status_code=400, content={"error": "focalboard_card_id required"})

        existing = db.execute(
            select(Reminder).where(Reminder.focalboard_card_id == card_id)
        ).scalar_one_or_none()

        if existing:
            return {
                "id": existing.id, "focalboard_card_id": card_id,
                "task_text": existing.task_text, "status": existing.status, "created": False,
            }

        user = db.execute(select(User).limit(1)).scalars().first()
        if not user:
            return JSONResponse(status_code=500, content={"error": "no_user_found"})

        tags_found  = re.findall(r'#[a-zA-Z]\w*', task_text)
        tags        = " ".join(tags_found) if tags_found else None
        task_clean  = re.sub(r'\s*#[a-zA-Z]\w*', '', task_text).strip()

        reminder = Reminder(
            user_id=user.id,
            source_text=f"created_from_ui:{card_id}",
            task_text=task_clean,
            remind_at=datetime.now(TZ).replace(year=2099),
            status=status,
            priority=priority,
            tags=tags,
            focalboard_card_id=card_id,
            focalboard_synced_at=datetime.now(TZ),
        )
        db.add(reminder)
        db.commit()
        db.refresh(reminder)

        return {
            "id": reminder.id, "focalboard_card_id": card_id,
            "task_text": task_text, "status": status, "created": True,
        }
    finally:
        db.close()


@router.get("/tasks/by-card/{card_id}")
async def get_task_by_card(card_id: str):
    """Look up a task by its focalboard_card_id."""
    db = SessionLocal()
    try:
        reminder = db.execute(
            select(Reminder).where(Reminder.focalboard_card_id == card_id)
        ).scalar_one_or_none()
        if not reminder:
            return JSONResponse(status_code=404, content={"error": "task_not_found"})
        return {
            "id": reminder.id, "focalboard_card_id": card_id,
            "task_text": reminder.task_text, "status": reminder.status,
        }
    finally:
        db.close()


@router.get("/tasks/{task_id}")
async def get_task(task_id: int):
    """Return a task with its description and attachments."""
    db = SessionLocal()
    try:
        reminder = db.execute(
            select(Reminder).where(Reminder.id == task_id)
        ).scalar_one_or_none()
        if not reminder:
            return JSONResponse(status_code=404, content={"error": "task_not_found"})

        attachments = db.execute(
            text("SELECT id, filename, original_name, mime_type, size_bytes, created_at "
                 "FROM task_attachments WHERE reminder_id = :rid ORDER BY id"),
            {"rid": task_id},
        ).fetchall()

        from core.config import FOCALBOARD_BOARD_ID, CONTENT_BOARD_ID

        # Determine which board this task belongs to by checking tags
        _tags = getattr(reminder, "tags", "") or ""
        _is_content = "#contenido" in _tags.lower()
        _board_id = CONTENT_BOARD_ID if _is_content else FOCALBOARD_BOARD_ID

        return {
            "id": reminder.id,
            "task_text": reminder.task_text,
            "status": reminder.status,
            "priority": getattr(reminder, "priority", "P3"),
            "notes": reminder.notes,
            "tags": getattr(reminder, "tags", None),
            "url": getattr(reminder, "url", None),
            "description": getattr(reminder, "description", None),
            "remind_at": reminder.remind_at.isoformat() if reminder.remind_at else None,
            "focalboard_card_id": getattr(reminder, "focalboard_card_id", None),
            "board_id": _board_id,
            "attachments": [
                {
                    "id": a[0], "filename": a[1], "original_name": a[2],
                    "mime_type": a[3], "size_bytes": a[4],
                    "created_at": a[5].isoformat() if a[5] else None,
                    "url": f"/tasks/{task_id}/attachments/{a[0]}/file",
                }
                for a in attachments
            ],
        }
    finally:
        db.close()


@router.patch("/tasks/{task_id}")
async def update_task(task_id: int, request: Request):
    """Update task_text (extracts hashtags→tags), notes, status, priority."""
    db = SessionLocal()
    try:
        body     = await request.json()
        reminder = db.execute(
            select(Reminder).where(Reminder.id == task_id)
        ).scalar_one_or_none()
        if not reminder:
            return JSONResponse(status_code=404, content={"error": "task_not_found"})

        if "task_text" in body:
            raw = body["task_text"].strip()
            tags_found     = re.findall(r'#[a-zA-Z]\w*', raw)
            reminder.tags  = " ".join(tags_found) if tags_found else None
            reminder.task_text = re.sub(r'\s*#[a-zA-Z]\w*', '', raw).strip()
            # Sync top-level title to Focalboard
            if getattr(reminder, "focalboard_card_id", None):
                try:
                    from integrations import focalboard_client as fb
                    await fb.update_card_title(reminder.focalboard_card_id, reminder.task_text)
                except Exception as _e:
                    print(f"[task_routes] focalboard title sync error: {_e}")
        if "notes"    in body: reminder.notes    = body["notes"] or None
        if "tags"     in body: reminder.tags     = body["tags"] or None
        if "status"   in body: reminder.status   = body["status"]
        if "priority" in body: reminder.priority = body["priority"]

        db.commit()
        return {
            "id": reminder.id, "task_text": reminder.task_text,
            "tags": reminder.tags, "notes": reminder.notes,
            "status": reminder.status, "priority": reminder.priority,
        }
    finally:
        db.close()


@router.patch("/tasks/{task_id}/description")
async def update_task_description(task_id: int, request: Request):
    """
    Update the WYSIWYG HTML description of a task.

    Also extracts hashtags from the HTML and merges them into reminder.tags
    (same behavior as task_text updates from Telegram).

    Returns the updated task object so the UI can confirm the save.
    """
    db = SessionLocal()
    try:
        body = await request.json()
        html = body.get("description", "")

        reminder = db.execute(
            select(Reminder).where(Reminder.id == task_id)
        ).scalar_one_or_none()
        if not reminder:
            return JSONResponse(status_code=404, content={"error": "task_not_found"})

        # Persist HTML as-is — do not sanitize to empty
        reminder.description = html if html else None

        # Extract hashtags from HTML and merge into tags
        # Strip HTML tags first to get plain text for tag extraction
        plain_text = re.sub(r'<[^>]+>', ' ', html)
        new_tags   = re.findall(r'#[a-zA-Z]\w*', plain_text)
        if new_tags:
            existing   = re.findall(r'#[a-zA-Z]\w*', reminder.tags or "")
            existing_l = {t.lower() for t in existing}
            merged     = existing + [t for t in new_tags if t.lower() not in existing_l]
            reminder.tags = " ".join(merged)

        db.commit()
        db.refresh(reminder)

        return {
            "id":          reminder.id,
            "task_text":   reminder.task_text,
            "description": reminder.description,
            "tags":        reminder.tags,
            "notes":       reminder.notes,
            "status":      reminder.status,
            "priority":    getattr(reminder, "priority", "P3"),
            "focalboard_card_id": getattr(reminder, "focalboard_card_id", None),
        }
    finally:
        db.close()


@router.delete("/tasks/by-card/{card_id}")
async def delete_task_by_card(card_id: str):
    """
    Delete the EVA reminder when a card is deleted from the UI.
    The UI already deleted the card in Focalboard — this cleans up EVA's DB.
    """
    db = SessionLocal()
    try:
        reminder = db.execute(
            select(Reminder).where(Reminder.focalboard_card_id == card_id)
        ).scalar_one_or_none()
        if not reminder:
            return JSONResponse(status_code=404, content={"error": "not_found"})
        rid  = reminder.id
        task = reminder.task_text
        db.delete(reminder)
        db.commit()
        print(f"[delete] reminder {rid} '{task}' deleted (card {card_id})")
        return {"deleted": True, "id": rid, "task_text": task}
    finally:
        db.close()


@router.post("/tasks/duplicate/{card_id}")
async def duplicate_task_by_card(card_id: str, request: Request):
    """
    Create a new EVA reminder for a card duplicated from the UI.
    The UI already created the copy in Focalboard — this creates the reminder in EVA.
    body: { "new_card_id": "...", "title": "Mi tarea (copia)" }
    """
    import shutil as _sh
    db = SessionLocal()
    try:
        body        = await request.json()
        new_card_id = body.get("new_card_id")
        new_title   = body.get("title", "")

        if not new_card_id:
            return JSONResponse(status_code=400, content={"error": "new_card_id required"})

        original = db.execute(
            select(Reminder).where(Reminder.focalboard_card_id == card_id)
        ).scalar_one_or_none()

        user = db.execute(select(User).limit(1)).scalars().first()
        if not user:
            return JSONResponse(status_code=500, content={"error": "no_user"})

        new_reminder = Reminder(
            user_id=original.user_id if original else user.id,
            source_text=f"duplicated_from:{card_id}",
            task_text=new_title or (f"{original.task_text} (copia)" if original else "Copia"),
            remind_at=datetime.now(TZ).replace(year=2099),
            status="pending",
            notes=original.notes if original else None,
            tags=original.tags if original else None,
            url=original.url if original else None,
            priority=original.priority if original else "P3",
            focalboard_card_id=new_card_id,
            focalboard_synced_at=datetime.now(TZ),
        )
        db.add(new_reminder)
        db.commit()
        db.refresh(new_reminder)

        # Copy attachments from original
        attachments_copied = 0
        if original:
            orig_attachments = db.execute(
                text("SELECT filename, original_name, mime_type, size_bytes "
                     "FROM task_attachments WHERE reminder_id = :rid"),
                {"rid": original.id},
            ).fetchall()
            for att in orig_attachments:
                try:
                    old_path     = os.path.join(UPLOADS_DIR, att[0])
                    new_filename = f"{new_reminder.id}_{att[0].split('_', 1)[-1]}"
                    new_path     = os.path.join(UPLOADS_DIR, new_filename)
                    if os.path.exists(old_path):
                        _sh.copy2(old_path, new_path)
                        db.execute(
                            text("""INSERT INTO task_attachments
                                    (reminder_id, filename, original_name, mime_type, size_bytes)
                                    VALUES (:rid, :fn, :on, :mt, :sb)"""),
                            {"rid": new_reminder.id, "fn": new_filename,
                             "on": att[1], "mt": att[2], "sb": att[3]},
                        )
                        attachments_copied += 1
                except Exception as exc:
                    print(f"[duplicate] attachment copy error: {exc}")
            db.commit()

        return {
            "id": new_reminder.id, "focalboard_card_id": new_card_id,
            "task_text": new_reminder.task_text, "created": True,
            "attachments_copied": attachments_copied,
        }
    finally:
        db.close()