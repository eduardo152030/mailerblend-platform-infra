"""Run inside Voicebox: register the accepted pilot WAV once, without inference."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import uuid

from backend import config
from backend.database import Generation, VoiceProfile
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

assert os.geteuid() == 999, "Publish as the Voicebox user, never root"

OWNER = "1fd00418-2a79-4178-883f-af6c3f5e07ee"
SHA = "881542af39639c5fbc82802206c4bd039ed76cd60d94a86c1cb2cea8deac8517"
TEXT = "Hola, soy Eduardo. Bienvenidos a un nuevo análisis de trading. Hoy vamos a revisar el mercado y buscar oportunidades de entrada. Recuerda que una buena gestión del riesgo es fundamental para proteger nuestro capital."
source = Path("/qwen-jobs/accepted-sample/accepted.wav")
assert hashlib.sha256(source.read_bytes()).hexdigest() == SHA
ident = str(uuid.uuid5(uuid.NAMESPACE_URL, "voicebox:d077:" + SHA))
db = Session(create_engine("sqlite:///" + str(config.get_db_path()), connect_args={"timeout": 5}))
assert db.query(VoiceProfile).filter_by(id=OWNER).one().name == "Eduardo — Mi Voz"
existing = db.query(Generation).filter_by(id=ident).first()
if existing:
    assert existing.profile_id == OWNER and existing.text == TEXT and existing.model_size == "0.6B"
    assert hashlib.sha256(config.resolve_storage_path(existing.audio_path).read_bytes()).hexdigest() == SHA
else:
    destination = config.get_generations_dir() / (ident + ".wav")
    if destination.exists():
        assert hashlib.sha256(destination.read_bytes()).hexdigest() == SHA
    else:
        with destination.open("xb") as f:
            destination.chmod(0o600); f.write(source.read_bytes())
    row = Generation(id=ident, profile_id=OWNER, text=TEXT, language="es", seed=42,
                     engine="qwen", model_size="0.6B", status="completed", duration=10.8,
                     audio_path=config.to_storage_path(destination), source="manual")
    db.add(row); db.commit()
db.close()
print(json.dumps({"generation_id": ident, "audio_url": "http://192.168.1.127:17493/audio/" + ident,
                  "sha256": SHA, "imported_accepted_pilot_no_new_inference": True}))
