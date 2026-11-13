# Verify this immutable base ID before building; preserve its non-root entrypoint/CMD.
FROM local/voicebox:d086-uid999-candidate
LABEL voicebox.input-limit="1200" \
      voicebox.source="3987cabf9be44ed362c3a86c8a5924bd7a76ee04" \
      voicebox.base.image="sha256:212703647c03d428adc30f8bf4b864af82690eb41f4fe8ca052ff10dbaa45386"
COPY --chown=999:999 engine_policy.py /app/backend/backends/engine_policy.py
COPY --chown=999:999 frontend/ /app/frontend/
USER 999:999
# Inherit ENTRYPOINT uid999 and the original Uvicorn CMD without additional privileges.
