"""Administrator-managed preferences for new-contact notices."""
from asyncpg import Connection
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field, model_validator

from app.core.crm_access import CRMAccess, require_crm_access
from app.db import get_db

router = APIRouter(prefix="/v1/notifications", tags=["notifications"])


class NotificationPreferences(BaseModel):
    enabled: bool
    recipients: list[EmailStr] = Field(max_length=25)

    @model_validator(mode="after")
    def validate_recipients(self):
        self.recipients = list(dict.fromkeys(email.lower() for email in self.recipients))
        if self.enabled and not self.recipients:
            raise ValueError("Añade al menos un destinatario para habilitar el aviso")
        return self


def require_admin(access: CRMAccess = Depends(require_crm_access)):
    if not access.is_admin:
        raise HTTPException(403, "Administrator access required")


@router.get("", response_model=NotificationPreferences, dependencies=[Depends(require_admin)])
async def get_preferences(conn: Connection = Depends(get_db)):
    row = await conn.fetchrow("SELECT enabled, recipients FROM crm_notifications.preferences WHERE id")
    return dict(row)


@router.put("", response_model=NotificationPreferences, dependencies=[Depends(require_admin)])
async def save_preferences(data: NotificationPreferences, conn: Connection = Depends(get_db)):
    row = await conn.fetchrow(
        """
        UPDATE crm_notifications.preferences SET enabled=$1, recipients=$2
        WHERE id RETURNING enabled, recipients
        """,
        data.enabled, data.recipients,
    )
    return dict(row)
