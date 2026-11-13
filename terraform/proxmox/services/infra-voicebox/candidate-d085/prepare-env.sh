#!/bin/sh
# CT627 only, new isolated directory; no models loaded and no production changes.
set -eu
[ "$(hostname)" = infra-voicebox ]
[ ! -e /srv/voicebox/chatterbox-d085/venv/pyvenv.cfg ] || { echo "Existing environment: never overwrite or reinstall automatically" >&2; exit 1; }
[ "$(df -Pk / | awk 'NR==2 {print $4}')" -gt 20971520 ]
exec docker run --rm --name d085-prepare-dependencies --cpus 1 --memory 2g \
 --memory-swap 2g --pids-limit 128 --user 999:999 --read-only \
 --cap-drop ALL --security-opt no-new-privileges --tmpfs /tmp:rw,size=1g \
 -e HF_HOME=/cb/hf-cache -e UV_CACHE_DIR=/cb/cache -e HF_HUB_OFFLINE=1 -e TRANSFORMERS_OFFLINE=1 \
 -e OMP_NUM_THREADS=1 -e MKL_NUM_THREADS=1 -e NUMBA_CACHE_DIR=/tmp/numba \
 -v /srv/voicebox/chatterbox-d085:/cb:rw --entrypoint /bin/sh \
 sha256:bcc5c14f88064ffa76f813d788d183918b208deba45075d8118a2b07c60c248b -ec '
 /cb/uv venv --python /usr/local/bin/python /cb/venv
 /cb/uv pip sync --python /cb/venv/bin/python --require-hashes --torch-backend cpu --build-constraints /cb/build-constraints.txt /cb/requirements.lock
 /cb/uv pip install --python /cb/venv/bin/python --no-deps --no-build-isolation /cb/chatterbox
 /cb/uv pip check --python /cb/venv/bin/python
 /cb/venv/bin/python /cb/imports.py
 '
