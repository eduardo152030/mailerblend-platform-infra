"""Validate the shared GoTrue identity used by the EVA web application."""

import os
from uuid import UUID

import httpx
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

router = APIRouter(prefix="/ui", tags=["eva-ui"])
bearer = HTTPBearer(auto_error=False)
GOTRUE_USER_URL = "https://infra-svc01.mailerblend.com/auth/v1/user"


async def require_ui_owner(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
) -> UUID:
    if credentials is None:
        raise HTTPException(401, "Sesión requerida", headers={"WWW-Authenticate": "Bearer"})

    try:
        owner = UUID(os.environ["EVA_UI_OWNER_SUBJECT"])
    except (KeyError, ValueError):
        raise HTTPException(503, "Acceso web de EVA sin configurar") from None

    try:
        async with httpx.AsyncClient(timeout=5, follow_redirects=False) as client:
            response = await client.get(
                GOTRUE_USER_URL,
                headers={"Authorization": f"Bearer {credentials.credentials}"},
            )
    except httpx.RequestError:
        raise HTTPException(503, "Servicio de identidad no disponible") from None

    if response.status_code in (401, 403):
        raise HTTPException(401, "Sesión inválida", headers={"WWW-Authenticate": "Bearer"})
    if response.status_code != 200:
        raise HTTPException(503, "Servicio de identidad no disponible")

    try:
        subject = UUID(response.json()["id"])
    except (KeyError, ValueError, TypeError, AttributeError):
        raise HTTPException(503, "Respuesta de identidad inválida") from None
    if subject != owner:
        raise HTTPException(403, "Cuenta sin acceso a EVA")
    return subject


@router.get("/session")
async def ui_session(owner: UUID = Depends(require_ui_owner)):
    return {"subject": str(owner)}
