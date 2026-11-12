FROM local/voicebox:8af7efe62fab-piper-d068-r2
USER root
COPY apply.py /tmp/d069-apply.py
RUN python /tmp/d069-apply.py && python -m compileall -q /app/backend
