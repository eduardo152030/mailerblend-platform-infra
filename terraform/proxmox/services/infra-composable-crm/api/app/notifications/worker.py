"""Deliver pending notifications independently of request processing."""
import asyncio
from dataclasses import dataclass
from email.message import EmailMessage
from hashlib import sha256
import logging
import os
import smtplib
import ssl

import asyncpg

SELECT = """
SELECT d.contact_id, d.recipient, d.attempts, c.nombre, c.email, c.telefono, c.company_name
FROM crm_notifications.contact_delivery d
JOIN public.contactos c ON c.id = d.contact_id
JOIN crm_notifications.preferences p ON p.id AND p.enabled AND d.recipient = ANY(p.recipients)
WHERE d.sent_at IS NULL AND d.attempts < 6 AND d.next_attempt_at <= now()
ORDER BY d.next_attempt_at, d.created_at
LIMIT 1
FOR UPDATE OF d SKIP LOCKED
"""

UPDATE = """
UPDATE crm_notifications.contact_delivery
SET attempts=attempts+1, last_error=$3::text,
    next_attempt_at=now() + $4::int * interval '1 second',
    sent_at=CASE WHEN $3::text IS NULL THEN now() ELSE NULL END
WHERE contact_id=$1 AND recipient=$2
"""


@dataclass(frozen=True)
class MailConfig:
    host: str
    port: int
    tls: str
    user: str
    password: str
    sender: str
    crm_url: str

    @classmethod
    def load(cls):
        mode = os.environ.get("CRM_SMTP_TLS", "starttls")
        if mode not in {"starttls", "implicit", "none"}:
            raise ValueError("Invalid CRM SMTP TLS mode")
        user = os.environ.get("CRM_SMTP_USER", "")
        password = os.environ.get("CRM_SMTP_PASSWORD", "")
        if bool(user) != bool(password) or (mode == "none" and user):
            raise ValueError("SMTP authentication requires user, password and TLS")
        return cls(
            os.environ["CRM_SMTP_HOST"], int(os.environ["CRM_SMTP_PORT"]), mode,
            user, password, os.environ["CRM_SMTP_FROM"], os.environ["CRM_PUBLIC_URL"].rstrip("/"),
        )


def send(config: MailConfig, row) -> None:
    message = EmailMessage()
    message["From"] = config.sender
    message["To"] = row["recipient"]
    message["Subject"] = "Nuevo contacto en CRM"
    identity = sha256(f"{row['contact_id']}:{row['recipient']}".encode()).hexdigest()
    message["Message-ID"] = f"<crm-contact-{identity}@{config.sender.rsplit('@', 1)[-1]}>"
    message.set_content(
        f"Nombre: {row['nombre']}\nCorreo: {row['email']}\n"
        f"Teléfono: {row['telefono'] or '—'}\nEmpresa: {row['company_name'] or '—'}\n\n"
        f"{config.crm_url}/contactos?contacto={row['contact_id']}\n"
    )
    context = ssl.create_default_context()
    mail = (smtplib.SMTP_SSL(config.host, config.port, timeout=10, context=context)
            if config.tls == "implicit" else smtplib.SMTP(config.host, config.port, timeout=10))
    with mail:
        if config.tls == "starttls":
            mail.starttls(context=context)
        if config.user:
            mail.login(config.user, config.password)
        mail.send_message(message)


async def deliver_one(pool, config: MailConfig) -> bool:
    async with pool.acquire() as conn, conn.transaction():
        row = await conn.fetchrow(SELECT)
        if row is None:
            return False
        failure = None
        try:
            await asyncio.to_thread(send, config, row)
        except (OSError, smtplib.SMTPException) as error:
            failure = type(error).__name__
        delay = min(3600, 30 * 2 ** row["attempts"])
        await conn.execute(UPDATE, row["contact_id"], row["recipient"], failure, delay)
        await conn.execute(
            """
            INSERT INTO crm_notifications.delivery_attempt (contact_id, recipient, attempt, error_type)
            VALUES ($1,$2,$3,$4)
            """,
            row["contact_id"], row["recipient"], row["attempts"] + 1, failure,
        )
        return True


async def run():
    config = MailConfig.load()
    async with asyncpg.create_pool(os.environ["CRM_DB_DSN"], min_size=1, max_size=2) as pool:
        while True:
            try:
                if await deliver_one(pool, config):
                    continue
            except (OSError, asyncpg.PostgresError) as error:
                logging.warning("CRM notification worker: %s", type(error).__name__)
            await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(run())
