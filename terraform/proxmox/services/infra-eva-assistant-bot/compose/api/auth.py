"""
auth.py — Autenticación JWT para EVA
Estado: DISEÑADO, pendiente de activar

Dependencias necesarias (añadir a requirements.txt cuando se active):
  python-jose[cryptography]>=3.3.0
  passlib[bcrypt]>=1.7.4

Para activar:
  1. pip install python-jose[cryptography] passlib[bcrypt]
  2. Añadir a .env: JWT_SECRET=<random_secret_256bits>, JWT_EXPIRE_HOURS=24
  3. En main.py: from auth import router as auth_router; app.include_router(auth_router)
  4. En main.py: añadir dependency Depends(get_current_user) a endpoints protegidos
"""

import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy import select

from db import SessionLocal
from models import EVAUser  # ver users.py

router = APIRouter(prefix="/auth", tags=["auth"])

JWT_SECRET    = os.getenv("JWT_SECRET", "CHANGE_ME_IN_PRODUCTION")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_H  = int(os.getenv("JWT_EXPIRE_HOURS", "24"))

pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")
bearer_scheme = HTTPBearer(auto_error=False)


# ── Modelos ────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    display_name: str
    permissions: list[str]  # ["tareas:read", "tareas:write", "contenido:read", ...]


# ── Utilidades ─────────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_token(user_id: int, permissions: list[str]) -> str:
    expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRE_H)
    payload = {"sub": str(user_id), "permissions": permissions, "exp": expire}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_token(token: str) -> dict:
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])


# ── Dependency ─────────────────────────────────────────────────────────────

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme)
):
    """
    Dependency para proteger endpoints.
    Uso: async def my_endpoint(user = Depends(get_current_user))
    """
    if not credentials:
        raise HTTPException(status_code=401, detail="Token requerido")
    try:
        payload = decode_token(credentials.credentials)
        user_id = int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

    db = SessionLocal()
    try:
        user = db.execute(select(EVAUser).where(EVAUser.id == user_id)).scalar_one_or_none()
        if not user or not user.is_active:
            raise HTTPException(status_code=401, detail="Usuario no encontrado o inactivo")
        return user
    finally:
        db.close()

def require_permission(area: str, action: str = "read"):
    """
    Dependency factory para validar permisos por área.
    Uso: async def my_endpoint(user = Depends(require_permission("tareas", "write")))
    """
    async def checker(user = Depends(get_current_user)):
        db = SessionLocal()
        try:
            from models import UserPermission
            perm = db.execute(
                select(UserPermission)
                .where(UserPermission.user_id == user.id)
                .where(UserPermission.area == area)
            ).scalar_one_or_none()
            if not perm:
                raise HTTPException(status_code=403, detail=f"Sin acceso al área '{area}'")
            if action == "write" and not perm.can_write:
                raise HTTPException(status_code=403, detail=f"Sin permiso de escritura en '{area}'")
            if action == "delete" and not perm.can_delete:
                raise HTTPException(status_code=403, detail=f"Sin permiso de eliminación en '{area}'")
            return user
        finally:
            db.close()
    return checker


# ── Endpoints ──────────────────────────────────────────────────────────────

@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest):
    db = SessionLocal()
    try:
        user = db.execute(
            select(EVAUser).where(EVAUser.username == body.username)
        ).scalar_one_or_none()

        if not user or not user.is_active or not verify_password(body.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Credenciales incorrectas")

        from models import UserPermission
        perms = db.execute(
            select(UserPermission).where(UserPermission.user_id == user.id)
        ).scalars().all()

        perm_list = []
        for p in perms:
            if p.can_read:   perm_list.append(f"{p.area}:read")
            if p.can_write:  perm_list.append(f"{p.area}:write")
            if p.can_delete: perm_list.append(f"{p.area}:delete")

        token = create_token(user.id, perm_list)
        return TokenResponse(
            access_token=token,
            user_id=user.id,
            display_name=user.display_name or user.username,
            permissions=perm_list
        )
    finally:
        db.close()


@router.post("/logout")
async def logout(user=Depends(get_current_user)):
    # JWT es stateless — el cliente simplemente descarta el token
    # Para invalidación real: implementar blacklist en Redis o tabla DB
    return {"ok": True, "message": "Sesión cerrada"}


@router.get("/me")
async def me(user=Depends(get_current_user)):
    db = SessionLocal()
    try:
        from models import UserPermission
        perms = db.execute(
            select(UserPermission).where(UserPermission.user_id == user.id)
        ).scalars().all()
        return {
            "id": user.id,
            "username": user.username,
            "display_name": user.display_name,
            "is_active": user.is_active,
            "permissions": [
                {"area": p.area, "can_read": p.can_read,
                 "can_write": p.can_write, "can_delete": p.can_delete}
                for p in perms
            ]
        }
    finally:
        db.close()