#!/bin/bash
set -euo pipefail
umask 077
config=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
stage=$(mktemp -d)
trap 'rmdir "$stage" 2>/dev/null || rm -r -- "$stage"' EXIT
curl -fsSL https://github.com/axllent/mailpit/releases/download/v1.34.0/mailpit-linux-amd64.tar.gz -o "$stage/mailpit.tar.gz"
printf 'af236b42f171b1c74f0ac5ff444f44d36f2f2ecc0134f5a2f1d4e307e56a0d2c  %s\n' "$stage/mailpit.tar.gz" | sha256sum -c
tar -xzf "$stage/mailpit.tar.gz" -C "$stage" mailpit
install -m 0755 "$stage/mailpit" /usr/local/bin/
install -m 0644 "$config/infra-mail-mailpit.service" /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now infra-mail-mailpit
