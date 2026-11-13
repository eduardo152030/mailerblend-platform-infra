"""D085 CT627-only pre-deployment data/config backup; no duplicate read-only HF model cache."""
from pathlib import Path
import datetime
import hashlib
import json
import shutil
import socket
import sqlite3
import subprocess
import tarfile

assert socket.gethostname() == "infra-voicebox"
out = Path("/opt/voicebox/backups/d085-before-deploy")
assert not out.exists(), "Never replace a backup"
out.mkdir(mode=0o700, parents=True)
data = Path("/srv/voicebox/data")
db = sqlite3.connect("file:" + str(data / "voicebox.db") + "?mode=ro", uri=True)
assert db.execute("select count(*) from generations where status in ('generating','loading_model')").fetchone()[0] == 0
shutil.copytree(data, out / "data", ignore=shutil.ignore_patterns("voicebox.db", "voicebox.db-wal", "voicebox.db-shm"))
target = sqlite3.connect(out / "data/voicebox.db"); db.backup(target)
assert target.execute("pragma integrity_check").fetchone()[0] == "ok"
counts = {table: target.execute("select count(*) from " + table).fetchone()[0] for table in ["profiles", "profile_samples", "generations"]}
target.close(); db.close()
shutil.copytree("/srv/voicebox/private-originals", out / "private-originals")
shutil.copytree('/srv/voicebox/qwen-worker/jobs', out/'qwen-jobs')
shutil.copytree('/srv/voicebox/qwen-worker/src',out/'worker-source')
for name in ["compose.yml", "image-lock.json", "image-id.txt"]:
    p = Path("/opt/voicebox") / name
    if p.is_file():
        shutil.copy2(p, out / name)
c = json.loads(subprocess.check_output(["docker", "inspect", "voicebox"]))[0]
(out / "container.json").write_text(json.dumps(c)); (out / "container.json").chmod(0o600)

def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

manifest = {str(p.relative_to(out)): digest(p) for p in out.rglob("*") if p.is_file()}
(out / "manifest.json").write_text(json.dumps(manifest))
archive = out.with_suffix(".tar.gz")
with tarfile.open(archive, "x:gz") as t:
    t.add(out, arcname="snapshot")
archive.chmod(0o600)
print(json.dumps({"at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(), "archive": str(archive),
                  "sha256": digest(archive), "files": len(manifest), "database_counts": counts,
                  "original_image": c["Image"], "models_readonly_unchanged_not_duplicated": True}))
