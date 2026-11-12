FROM local/voicebox:8af7efe62fab-personal-d069
USER root
COPY --chown=999:999 isolated_backend.py /app/backend/backends/isolated_backend.py
COPY --chown=999:999 d077_contract.py /app/backend/backends/d077_contract.py
COPY patch.py /tmp/d077-patch.py
RUN python /tmp/d077-patch.py && python -m compileall -q /app/backend
