FROM oven/bun:1@sha256:3f23864d3e8c923975c61971cabe67ee3d5a728f1e25a559256b95af719a3478 AS frontend
WORKDIR /build
ADD --checksum=sha256:3a8b520cc7d4cfe36b5e9dccfd6e399724127e19602df9b1ee8f3c05bcebbf91 https://codeload.github.com/eduardo152030/voicebox/tar.gz/8af7efe62fab8d33e2a5dfbedabaa45f68a5184f /tmp/source.tar.gz
RUN tar -xzf /tmp/source.tar.gz --strip-components=1 -C /build
COPY patch-ui.py /tmp/patch-ui.py
# Bun image also includes a node runtime; use a small Python-free application of the patch below.
COPY patch-ui.mjs /tmp/patch-ui.mjs
RUN bun /tmp/patch-ui.mjs
RUN sed -i 's/\r$//' package.json && sed -i '/"tauri"/d' package.json && sed -i -z 's/,\n  ]/\n  ]/' package.json
RUN bun install --no-save
RUN cd web && bunx --bun vite build
FROM local/voicebox:8af7efe62fab-personal-d069
USER root
COPY openvoice_backend.py /app/backend/backends/openvoice_backend.py
COPY patch-app.py /tmp/d071-patch-app.py
RUN python /tmp/d071-patch-app.py && python -m compileall -q /app/backend
COPY --from=frontend /build/web/dist /app/frontend/
COPY --from=frontend /build/bun.lock /app/d071-frontend.lock
