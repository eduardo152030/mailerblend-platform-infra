# Build only AFTER verifying the local base tag's immutable image ID from D082.
FROM local/voicebox:qwen-isolated-d079
USER root
COPY --chown=999:999 backend/ /app/backend/backends/
COPY patches/ /tmp/d085-patches/
RUN python /tmp/d085-patches/d083.py --root /app/backend \
 && python /tmp/d085-patches/d085.py --root /app/backend \
 && python -m compileall -q /app/backend
COPY --chown=999:999 frontend/ /app/frontend/
LABEL voicebox.candidate="D085-no-production-deploy-no-audio" \
      voicebox.base.image="sha256:09774c5b7c535185c901557ddb6c69a4f8bb38ceff2c6998e19bab403b8e94ea"
USER 999:999
