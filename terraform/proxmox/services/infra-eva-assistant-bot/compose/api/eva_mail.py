"""Authenticated delivery of an EVA message to its configured owner."""

import argparse
import os
import smtplib
import ssl
import sys
from email.message import EmailMessage


def send_owner_mail(subject: str, body: str) -> None:
    host = os.environ["EVA_SMTP_HOST"]
    username = os.environ["EVA_SMTP_USERNAME"]
    password = os.environ["EVA_SMTP_PASSWORD"]
    context = ssl.create_default_context(cafile=os.getenv("EVA_SMTP_CA_FILE"))
    message = EmailMessage()
    message["From"] = os.environ["EVA_SMTP_FROM"]
    message["To"] = os.environ["EVA_SMTP_OWNER"]
    message["Subject"] = subject
    message.set_content(body)

    with smtplib.SMTP(host, 587, timeout=10) as smtp:
        smtp.ehlo()
        smtp.starttls(context=context)
        smtp.ehlo()
        smtp.login(username, password)
        smtp.send_message(message)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("subject")
    args = parser.parse_args()
    body = sys.stdin.read()
    if not body.strip():
        parser.error("Provide the message body on standard input")
    try:
        send_owner_mail(args.subject, body)
    except (KeyError, ValueError, OSError):
        parser.exit(1, "EVA could not deliver the email. Check the private SMTP configuration.\n")


if __name__ == "__main__":
    main()
