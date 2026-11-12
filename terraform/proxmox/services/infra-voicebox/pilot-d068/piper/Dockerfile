FROM local/voicebox:8af7efe62fab-cpu-d063
USER root
COPY wheels/ /tmp/d068-wheels/
RUN pip install --no-cache-dir --no-deps --no-index /tmp/d068-wheels/*.whl && rm -r /tmp/d068-wheels
COPY piper_backend.py /app/backend/backends/piper_backend.py
COPY apply-patches.py /tmp/d068-apply.py
RUN python /tmp/d068-apply.py && python -m compileall -q /app/backend
