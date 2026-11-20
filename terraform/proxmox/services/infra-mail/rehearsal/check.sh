#!/bin/bash
# Ejecutar exclusivamente en una máquina desechable con systemd.
set -euo pipefail
umask 077
if [[ ${GITHUB_ACTIONS:-} != true || ${RUNNER_ENVIRONMENT:-} != github-hosted || $EUID != 0 ]]; then
    echo 'La prueba instala servicios en una VM desechable de GitHub Actions' >&2
    exit 1
fi
relay=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
fixture=/etc/infra-mail/private
install -m 0700 -d "$fixture"
openssl req -x509 -newkey rsa:2048 -nodes -days 10 -subj /CN=127.0.0.1 \
    -addext subjectAltName=IP:127.0.0.1 -keyout "$fixture/tls.key" -out "$fixture/tls.crt" 2>/dev/null
for identity in crm gotrue; do
    password=$(openssl rand -hex 20)
    printf '%s' "$password" > "$fixture/$identity.fixture"
    printf '%s:{PLAIN}%s\n' "$identity" "$password" >> "$fixture/service-users"
done
printf '%s\n' 'smtp-sender@example.test crm,gotrue' > "$fixture/sender-login"
install -d /etc/systemd/system/infra-mail-policy.service.d /var/lib/node_exporter/textfile
printf '%s\n' '[Service]' 'Environment=RELAY_RECIPIENTS_PER_MINUTE=1' > /etc/systemd/system/infra-mail-policy.service.d/quota.conf
"$relay/install-mailpit.sh"
"$relay/install-relay.sh" --mailpit
python3 "$relay/rehearsal/check.py"
