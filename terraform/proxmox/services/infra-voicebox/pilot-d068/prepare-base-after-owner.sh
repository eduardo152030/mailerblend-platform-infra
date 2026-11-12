#!/usr/bin/env bash
# Only after actual owner reference upload; exactly one pinned Base download, no TTS load.
set -euo pipefail
[[ $(hostname) == infra-voicebox ]]
python3 - <<'PY'
import sqlite3,shutil
p='/srv/voicebox/data/voicebox.db';db=sqlite3.connect('file:'+p+'?mode=ro',uri=True)
assert db.execute("select count(*) from profiles p join profile_samples s on s.profile_id=p.id where p.id=?",('1fd00418-2a79-4178-883f-af6c3f5e07ee',)).fetchone()[0]>0,'Upload actual owner references first'
assert shutil.disk_usage('/srv/voicebox').free>3*2**30,'Insufficient free disk; do not expand automatically'
PY
image=$(python3 -c 'import json;print(json.load(open("/opt/voicebox/image-lock.json"))["image"])')
docker run --rm --name voicebox-base-owner-download --no-healthcheck --cpus=1 --memory=512m --memory-swap=512m \
  -e HF_HUB_OFFLINE=0 -e HF_HUB_DISABLE_XET=1 \
  -v /srv/voicebox/huggingface:/home/voicebox/.cache/huggingface \
  -v /opt/voicebox/pilot-d068/download-base-model.py:/download.py:ro \
  -v /opt/voicebox/pilot-d068/base-model-lock.json:/model-lock.json:ro \
  "$image" python /download.py
