"""Postfix policy for per-identity recipient quotas."""
import os
import socketserver
import sqlite3
import time
from contextlib import closing
from pathlib import Path

DATA = Path("/var/lib/infra-mail/policy.sqlite3")
LIMIT = int(os.environ.get("RELAY_RECIPIENTS_PER_MINUTE", "30"))


def evaluate(attributes):
    user = attributes.get("sasl_username")
    if not user:
        return "REJECT SMTP authentication required"
    bucket = int(time.time()) // 60
    with closing(sqlite3.connect(DATA, timeout=5)) as connection, connection:
        connection.execute("DELETE FROM quota WHERE minute < ?", (bucket - 1,))
        cursor = connection.execute(
            """INSERT INTO quota (identity, minute, recipients) VALUES (?, ?, 1)
               ON CONFLICT (identity, minute) DO UPDATE SET recipients = recipients + 1
               WHERE recipients < ?""",
            (user, bucket, LIMIT),
        )
        if cursor.rowcount == 0:
            return "451 4.7.1 Recipient quota exceeded"
    return "DUNNO"


class PolicyHandler(socketserver.StreamRequestHandler):
    def handle(self):
        self.request.settimeout(15)
        attributes = {}
        for line in self.rfile:
            if not line.strip():
                try:
                    action = evaluate(attributes)
                except sqlite3.Error:
                    action = "451 4.3.0 Policy temporarily unavailable"
                self.wfile.write(f"action={action}\n\n".encode())
                attributes.clear()
                continue
            key, _, value = line.decode(errors="replace").strip().partition("=")
            attributes[key] = value


if __name__ == "__main__":
    if LIMIT < 1:
        raise ValueError("RELAY_RECIPIENTS_PER_MINUTE must be positive")
    with closing(sqlite3.connect(DATA)) as connection, connection:
        connection.execute(
            """CREATE TABLE IF NOT EXISTS quota (
                identity TEXT, minute INTEGER, recipients INTEGER,
                PRIMARY KEY (identity, minute)
            )"""
        )
    with socketserver.ThreadingTCPServer(("127.0.0.1", 10031), PolicyHandler) as server:
        server.serve_forever()
