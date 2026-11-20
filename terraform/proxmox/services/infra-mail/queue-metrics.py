"""Collect queue lengths without exposing envelope addresses."""
import json
import os
from pathlib import Path
import subprocess
import tempfile

directory = Path("/var/lib/node_exporter/textfile")
records = subprocess.check_output(["postqueue", "-j"], text=True).splitlines()
deferred = sum(json.loads(record)["queue_name"] == "deferred" for record in records)
with tempfile.NamedTemporaryFile(mode="w", dir=directory, delete=False) as stream:
    stream.write(f"infra_mail_queue_messages {len(records)}\n")
    stream.write(f"infra_mail_deferred_messages {deferred}\n")
    pending = stream.name
os.chmod(pending, 0o644)
os.replace(pending, directory / "infra-mail.prom")
