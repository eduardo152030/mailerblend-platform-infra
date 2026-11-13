# Candidate only; verify this tag's ID against D082 before any future build.
FROM local/voicebox:qwen-isolated-d079
USER root
COPY --chown=999:999 isolated_backend.py /app/backend/backends/isolated_backend.py
COPY --chown=999:999 qwen_language_policy.py /app/backend/backends/qwen_language_policy.py
COPY patch.py /tmp/d083-patch.py
RUN python /tmp/d083-patch.py && python -m compileall -q /app/backend
# UI candidate sources must be built separately against the pinned fork before deployment.
# This Dockerfile is a backend candidate, not a completed deployable UI release.
