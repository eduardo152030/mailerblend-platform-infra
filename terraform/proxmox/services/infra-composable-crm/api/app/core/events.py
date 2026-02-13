import json
from typing import Any, Dict, Optional
from uuid import UUID
from asyncpg import Connection

def _json_text(payload: Optional[Dict[str, Any]]) -> str:
    if not payload:
        return "{}"
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))

async def log_event(
    conn: Connection,
    *,
    contacto_id: Optional[UUID],
    event_key: str,
    payload: Optional[Dict[str, Any]] = None,
    created_by: str = "api",
    outcome: Optional[str] = None,
    oportunidad_id: Optional[UUID] = None,
    linkedin_lead_id: Optional[UUID] = None,
) -> UUID:
    """
    Inserta un evento en historial usando type='NOTE' para cumplir el CHECK.
    subject: EVENT::<event_key>
    notes: JSON serializado
    """
    subject = f"EVENT::{event_key}"

    row = await conn.fetchrow(
        """
        INSERT INTO historial (
          contacto_id,
          oportunidad_id,
          linkedin_lead_id,
          type,
          subject,
          notes,
          outcome,
          activity_date,
          created_by,
          created_at
        ) VALUES (
          $1,$2,$3,
          'NOTE',
          $4,
          $5,
          $6,
          NOW(),
          $7,
          NOW()
        )
        RETURNING id
        """,
        contacto_id,
        oportunidad_id,
        linkedin_lead_id,
        subject,
        _json_text(payload),
        outcome,
        created_by,
    )
    return row["id"]
