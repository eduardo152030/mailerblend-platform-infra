#!/usr/bin/env bash
set -euo pipefail

hostname_expected="${1:?Expected hostname required}"
case "$hostname_expected" in
  infra-knowledge|infra-diagrams|infra-modeling) ;;
  *) exit 2 ;;
esac
[[ "$(hostname)" == "$hostname_expected" ]]
. /etc/os-release
[[ "$ID" == debian && "$VERSION_CODENAME" == bookworm ]]

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y --no-install-recommends ca-certificates curl
install -d -m 0755 /etc/apt/keyrings
if [[ ! -f /etc/apt/keyrings/docker.asc ]]; then
  key_file=$(mktemp)
  trap 'unlink "$key_file"' EXIT
  curl --fail --silent --show-error --location https://download.docker.com/linux/debian/gpg -o "$key_file"
  install -m 0644 "$key_file" /etc/apt/keyrings/docker.asc
fi
cat > /etc/apt/sources.list.d/docker.sources <<'APT'
Types: deb
URIs: https://download.docker.com/linux/debian
Suites: bookworm
Components: stable
Signed-By: /etc/apt/keyrings/docker.asc
APT

apt-get update
apt-get install -y --no-install-recommends \
  'docker-ce=5:29.9.3-1~debian.12~bookworm' \
  'docker-ce-cli=5:29.9.3-1~debian.12~bookworm' \
  'containerd.io=2.4.2-4~debian.12~bookworm' \
  'docker-compose-plugin=5.7.1-1~debian.12~bookworm'
docker version --format '{{.Server.Version}}'
docker compose version
