"""Record delivery work in the same transaction as contact creation."""
from uuid import UUID

from asyncpg import Connection


async def enqueue_contact(conn: Connection, contact_id: UUID) -> None:
    await conn.execute(
        """
        INSERT INTO crm_notifications.contact_delivery(contact_id, recipient)
        SELECT $1, unnest(recipients)
        FROM crm_notifications.preferences
        WHERE id AND enabled
        ON CONFLICT DO NOTHING
        """,
        contact_id,
    )
