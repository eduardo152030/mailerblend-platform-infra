"""
users.py — CRUD de usuarios y permisos para EVA
Estado: DISEÑADO, pendiente de activar
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from typing import Optional

from db import SessionLocal
from models import EVAUser, UserPermission

router = APIRouter(prefix="/admin", tags=["admin"])


# ── Modelos ────────────────────────────────────────────────────────────────

class CreateUserRequest(BaseModel):
    username: str
    password: str
    display_name: Optional[str] = None
    permissions: list[dict] = []
    # permissions: [{"area": "tareas", "can_read": true, "can_write": true, "can_delete": false}]

class UpdateUserRequest(BaseModel):
    display_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    permissions: Optional[list[dict]] = None


# ── Endpoints (todos requieren admin) ──────────────────────────────────────

def require_admin():
    """Dependency — solo usuarios con permisos en todas las áreas"""
    from auth import get_current_user
    async def checker(user=Depends(get_current_user)):
        db = SessionLocal()
        try:
            perms = db.execute(
                select(UserPermission).where(UserPermission.user_id == user.id)
            ).scalars().all()
            areas = {p.area for p in perms}
            if "tareas" not in areas or "contenido" not in areas:
                raise HTTPException(status_code=403, detail="Requiere permisos de admin")
            return user
        finally:
            db.close()
    return checker


@router.get("/users")
async def list_users(admin=Depends(require_admin())):
    db = SessionLocal()
    try:
        users = db.execute(select(EVAUser)).scalars().all()
        result = []
        for u in users:
            perms = db.execute(
                select(UserPermission).where(UserPermission.user_id == u.id)
            ).scalars().all()
            result.append({
                "id": u.id, "username": u.username,
                "display_name": u.display_name, "is_active": u.is_active,
                "created_at": u.created_at.isoformat(),
                "permissions": [
                    {"area": p.area, "can_read": p.can_read,
                     "can_write": p.can_write, "can_delete": p.can_delete}
                    for p in perms
                ]
            })
        return {"users": result}
    finally:
        db.close()


@router.post("/users")
async def create_user(body: CreateUserRequest, admin=Depends(require_admin())):
    from auth import hash_password
    db = SessionLocal()
    try:
        existing = db.execute(
            select(EVAUser).where(EVAUser.username == body.username)
        ).scalar_one_or_none()
        if existing:
            raise HTTPException(status_code=400, detail="Usuario ya existe")

        user = EVAUser(
            username=body.username,
            password_hash=hash_password(body.password),
            display_name=body.display_name or body.username,
            is_active=True,
        )
        db.add(user)
        db.flush()

        for perm_data in body.permissions:
            perm = UserPermission(
                user_id=user.id,
                area=perm_data["area"],
                can_read=perm_data.get("can_read", True),
                can_write=perm_data.get("can_write", False),
                can_delete=perm_data.get("can_delete", False),
            )
            db.add(perm)

        db.commit()
        return {"id": user.id, "username": user.username, "created": True}
    finally:
        db.close()


@router.patch("/users/{user_id}")
async def update_user(user_id: int, body: UpdateUserRequest, admin=Depends(require_admin())):
    from auth import hash_password
    db = SessionLocal()
    try:
        user = db.execute(select(EVAUser).where(EVAUser.id == user_id)).scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        if body.display_name is not None:
            user.display_name = body.display_name
        if body.password is not None:
            user.password_hash = hash_password(body.password)
        if body.is_active is not None:
            user.is_active = body.is_active

        if body.permissions is not None:
            # Reemplazar permisos completos
            db.execute(
                UserPermission.__table__.delete().where(UserPermission.user_id == user_id)
            )
            for perm_data in body.permissions:
                perm = UserPermission(
                    user_id=user_id,
                    area=perm_data["area"],
                    can_read=perm_data.get("can_read", True),
                    can_write=perm_data.get("can_write", False),
                    can_delete=perm_data.get("can_delete", False),
                )
                db.add(perm)

        db.commit()
        return {"updated": True}
    finally:
        db.close()


@router.delete("/users/{user_id}")
async def deactivate_user(user_id: int, admin=Depends(require_admin())):
    db = SessionLocal()
    try:
        user = db.execute(select(EVAUser).where(EVAUser.id == user_id)).scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        user.is_active = False
        db.commit()
        return {"deactivated": True, "username": user.username}
    finally:
        db.close()