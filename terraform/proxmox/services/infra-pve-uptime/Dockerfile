# Python 3.14 upstream rejects the existing PVE CA (missing keyUsage).
# Use supported Python 3.12, without disabling verification or changing CA/ACL.
FROM python:3.12-slim-bookworm@sha256:935c3c5b12357a7e10caa9c1e6ca5692344d97cf229832ef584be2cec9fc03df
COPY requirements.lock /tmp/requirements.lock
RUN pip install --no-cache-dir -r /tmp/requirements.lock
USER 65534:65534
ENV PYTHONDONTWRITEBYTECODE=1
ENTRYPOINT ["pve_exporter"]
