"""Exercise authenticated STARTTLS submission and Mailpit capture."""
from contextlib import contextmanager
from email import policy
from email.message import EmailMessage
from email.parser import BytesParser
import json
from pathlib import Path
import smtplib
import ssl
import time
from urllib.request import urlopen

FIXTURE = Path("/etc/infra-mail/private")
SENDER = "smtp-sender@example.test"
RECIPIENT = "recipient@example.test"


@contextmanager
def connect():
    with smtplib.SMTP("127.0.0.1", 587, timeout=10) as client:
        client.ehlo()
        yield client


def reject(expected, response):
    assert response[0] == expected, (expected, response[0])


def starttls(client):
    client.starttls(context=ssl.create_default_context(cafile=str(FIXTURE / "tls.crt")))
    client.ehlo()


def message(subject):
    mail = EmailMessage()
    mail["From"] = SENDER
    mail["To"] = RECIPIENT
    mail["Subject"] = subject
    mail["Received"] = "from internal.example [192.168.1.120] by onward.example"
    mail["Received"] = "from external.example [203.0.113.1] by infra-mail.localdomain (Postfix)"
    mail["Received"] = "from device.lan by onward.example"
    mail["Received"] = "from preserved.example [203.0.113.7] by onward.example"
    mail.set_content("Synthetic SMTP rehearsal.")
    return mail


with connect() as unauthenticated:
    assert not unauthenticated.has_extn("auth")
    reject(530, unauthenticated.mail(SENDER))
    starttls(unauthenticated)
    unauthenticated.mail(SENDER)
    reject(554, unauthenticated.rcpt(RECIPIENT))

seconds_into_minute = time.time() % 60
if seconds_into_minute > 50:
    time.sleep(61 - seconds_into_minute)

with connect() as crm:
    starttls(crm)
    crm.login("crm", (FIXTURE / "crm.fixture").read_text())
    crm.mail("unowned@example.test")
    reject(553, crm.rcpt(RECIPIENT))
    crm.rset()
    crm.send_message(message("CRM test"))
    crm.mail(SENDER)
    reject(451, crm.rcpt(RECIPIENT))

with connect() as gotrue:
    starttls(gotrue)
    gotrue.login("gotrue", (FIXTURE / "gotrue.fixture").read_text())
    gotrue.send_message(message("GoTrue test"))

for _ in range(20):
    with urlopen("http://127.0.0.1:8025/api/v1/messages", timeout=3) as response:
        messages = json.load(response)["messages"]
        subjects = sorted(row["Subject"] for row in messages)
    if subjects == ["CRM test", "GoTrue test"]:
        break
    time.sleep(1)
else:
    raise AssertionError("Mailpit did not capture the two expected messages")

for summary in messages:
    with urlopen(f"http://127.0.0.1:8025/api/v1/message/{summary['ID']}/raw", timeout=3) as response:
        captured = BytesParser(policy=policy.default).parse(response)
    received = "\n".join(map(str, captured.get_all("Received", [])))
    assert "preserved.example" in received
    assert "internal.example" not in received and "device.lan" not in received
    assert "infra-mail.localdomain" not in received and "(Postfix)" not in received
    assert captured["From"] == SENDER

print("PASS: outbound privacy filter keeps public trace and removes internal hops")
print("PASS: STARTTLS, anonymous rejection, sender ownership, per-user quota and Mailpit delivery")
