ssh root@192.168.1.117 "sed -i 's/^INGEST_SECRET=.*/INGEST_SECRET=ff67d47984cc545f8b1510b4a34f6ff6cf5a40f0458849bc/' /opt/infra-orbit/gcp/.env || echo 'INGEST_SECRET=ff67d47984cc545f8b1510b4a34f6ff6cf5a40f0458849bc' >> /opt/infra-orbit/gcp/.env"

--
