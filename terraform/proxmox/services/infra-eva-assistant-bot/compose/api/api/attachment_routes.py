"""
api/attachment_routes.py
========================
File upload/download/delete endpoints for task attachments.
To debug attachment issues: inspect only this file.
"""
import os
import mimetypes
import uuid

from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse
from sqlalchemy import select, text

from db import SessionLocal
from models import Reminder
from core.config import UPLOADS_DIR, MAX_FILE_SIZE, ALLOWED_MIME_TYPES

# Ensure upload directory exists at import time
os.makedirs(UPLOADS_DIR, exist_ok=True)

router = APIRouter()


@router.post("/tasks/{task_id}/attachments")
async def upload_attachment(task_id: int, file: UploadFile = File(...)):
    """Upload an attachment (image or PDF) to a task."""
    db = SessionLocal()
    try:
        reminder = db.execute(
            select(Reminder).where(Reminder.id == task_id)
        ).scalar_one_or_none()
        if not reminder:
            return JSONResponse(status_code=404, content={"error": "task_not_found"})

        mime = file.content_type or mimetypes.guess_type(file.filename or "")[0] or ""
        if mime not in ALLOWED_MIME_TYPES:
            return JSONResponse(
                status_code=400,
                content={"error": "file_type_not_allowed", "mime": mime},
            )

        content_bytes = await file.read()
        if len(content_bytes) > MAX_FILE_SIZE:
            return JSONResponse(status_code=400, content={"error": "file_too_large"})

        ext         = os.path.splitext(file.filename or "file")[1].lower()
        stored_name = f"{task_id}_{uuid.uuid4().hex}{ext}"
        dest        = os.path.join(UPLOADS_DIR, stored_name)
        with open(dest, "wb") as f:
            f.write(content_bytes)

        result = db.execute(
            text("""INSERT INTO task_attachments
                    (reminder_id, filename, original_name, mime_type, size_bytes)
                    VALUES (:rid, :fn, :on, :mt, :sz)
                    RETURNING id, created_at"""),
            {"rid": task_id, "fn": stored_name, "on": file.filename,
             "mt": mime, "sz": len(content_bytes)},
        ).fetchone()
        db.commit()

        return {
            "status": "ok",
            "id": result[0],
            "filename": stored_name,
            "original_name": file.filename,
            "mime_type": mime,
            "size_bytes": len(content_bytes),
            "created_at": result[1].isoformat(),
            "url": f"/tasks/{task_id}/attachments/{result[0]}/file",
        }
    finally:
        db.close()


import urllib.parse as _urlparse
from fastapi.responses import Response as _Response

@router.get("/tasks/{task_id}/attachments/{attachment_id}/file")
async def download_attachment(task_id: int, attachment_id: int):
    """Download / serve an attachment file."""
    db = SessionLocal()
    try:
        row = db.execute(
            text("SELECT filename, original_name, mime_type FROM task_attachments "
                 "WHERE id = :id AND reminder_id = :rid"),
            {"id": attachment_id, "rid": task_id},
        ).fetchone()
        if not row:
            return JSONResponse(status_code=404, content={"error": "attachment_not_found"})

        filepath = os.path.join(UPLOADS_DIR, row[0])
        if not os.path.exists(filepath):
            return JSONResponse(status_code=404, content={"error": "file_not_found_on_disk"})

        original_name = row[1] or row[0]
        mime_type     = row[2] or "application/octet-stream"

        # RFC 5987 encoding — handles filenames with special chars, long names,
        # underscores, commas, accented chars, etc.
        # Produces: Content-Disposition: attachment; filename*=UTF-8''encoded_name
        encoded_name = _urlparse.quote(original_name, safe="")
        content_disposition = f"attachment; filename*=UTF-8''{encoded_name}"

        with open(filepath, "rb") as f:
            file_bytes = f.read()

        return _Response(
            content=file_bytes,
            media_type=mime_type,
            headers={"Content-Disposition": content_disposition},
        )
    finally:
        db.close()


@router.delete("/tasks/{task_id}/attachments/{attachment_id}")
async def delete_attachment(task_id: int, attachment_id: int):
    """Delete an attachment."""
    db = SessionLocal()
    try:
        row = db.execute(
            text("SELECT filename FROM task_attachments WHERE id = :id AND reminder_id = :rid"),
            {"id": attachment_id, "rid": task_id},
        ).fetchone()
        if not row:
            return JSONResponse(status_code=404, content={"error": "attachment_not_found"})

        filepath = os.path.join(UPLOADS_DIR, row[0])
        if os.path.exists(filepath):
            os.remove(filepath)

        db.execute(
            text("DELETE FROM task_attachments WHERE id = :id"),
            {"id": attachment_id},
        )
        db.commit()
        return {"status": "ok", "deleted": attachment_id}
    finally:
        db.close()


@router.get("/tasks/{task_id}/attachments")
async def list_attachments(task_id: int):
    """List all attachments for a task."""
    db = SessionLocal()
    try:
        rows = db.execute(
            text("SELECT id, filename, original_name, mime_type, size_bytes, created_at "
                 "FROM task_attachments WHERE reminder_id = :rid ORDER BY id"),
            {"rid": task_id},
        ).fetchall()
        return {
            "task_id": task_id,
            "attachments": [
                {
                    "id": r[0], "filename": r[1], "original_name": r[2],
                    "mime_type": r[3], "size_bytes": r[4],
                    "created_at": r[5].isoformat() if r[5] else None,
                    "url": f"/tasks/{task_id}/attachments/{r[0]}/file",
                }
                for r in rows
            ],
        }
    finally:
        db.close()