#!/bin/bash
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y --no-install-recommends ca-certificates curl python3 espeak-ng
install -m 0755 -d /etc/apt/keyrings
if [ ! -f /etc/apt/keyrings/docker.asc ]; then
 curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
 chmod a+r /etc/apt/keyrings/docker.asc
fi
cat > /etc/apt/sources.list.d/docker.sources <<'EOF'
Types: deb
URIs: https://download.docker.com/linux/debian
Suites: bookworm
Components: stable
Signed-By: /etc/apt/keyrings/docker.asc
EOF
apt-get update
apt-get install -y --no-install-recommends 'docker-ce=5:29.9.3-1~debian.12~bookworm' 'docker-ce-cli=5:29.9.3-1~debian.12~bookworm' 'containerd.io=2.4.2-4~debian.12~bookworm' 'docker-buildx-plugin=0.39.0-1~debian.12~bookworm' 'docker-compose-plugin=5.7.1-1~debian.12~bookworm'
install -d -m 700 /opt/ia-chat
install -d -m 700 /opt/ia-chat/data /opt/ia-chat/searxng
docker version --format '{{.Server.Version}}'
docker compose version
