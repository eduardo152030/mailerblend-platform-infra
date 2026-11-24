#!/usr/bin/env bash
set -euo pipefail
umask 077

[[ "$(hostname -s)" == edge-router ]]
domain=infra-eva-ui.mailerblend.com
certificate=/etc/letsencrypt/live/mailerblend.com/fullchain.pem
available="/etc/nginx/sites-available/$domain.conf"
enabled="/etc/nginx/sites-enabled/$domain.conf"

openssl x509 -in "$certificate" -noout -checkend 86400 >/dev/null
openssl x509 -in "$certificate" -noout -checkhost "$domain" |
  grep -Fx "Hostname $domain does match certificate" >/dev/null

candidate=$(mktemp)
trap 'rm -f "$candidate"' EXIT
cat > "$candidate" <<'NGINX'
server {
    listen 443 ssl;
    server_name infra-eva-ui.mailerblend.com;

    ssl_certificate /etc/letsencrypt/live/mailerblend.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/mailerblend.com/privkey.pem;

    location / {
        default_type text/plain;
        add_header Cache-Control "no-store" always;
        return 503 "EVA UI en preparacion\n";
    }
}
NGINX

probe() {
    local code attempt
    for attempt in {1..10}; do
        if code=$(curl --silent --show-error --max-time 10 --resolve "$domain:443:127.0.0.1" \
        --output /dev/null --write-out '%{http_code}' "https://$domain/" 2>/dev/null) && [[ "$code" == 503 ]]; then
            return 0
        fi
        sleep 1
    done
    printf '%s\n' 'HTTPS verification failed.' >&2
    return 1
}

if [[ -f "$available" && ! -L "$available" && -L "$enabled" ]] &&
    [[ "$(readlink "$enabled")" == "$available" ]] && cmp -s "$candidate" "$available"; then
    probe
    printf '%s\n' 'TLS verified. Configuration unchanged.'
    exit 0
fi

[[ ! -e "$available" && ! -L "$available" && ! -e "$enabled" && ! -L "$enabled" ]]
nginx_config=$(nginx -T 2>&1)
if printf '%s\n' "$nginx_config" | grep -E '^[[:space:]]*server_name[[:space:]]' |
    tr ' ;\t' '\n' | grep -Fx "$domain"; then
    printf '%s\n' 'An existing vhost owns this hostname.' >&2
    exit 1
fi

backup=$(mktemp -d /var/backups/eva-ui-nginx.XXXXXX)
cp -a /etc/nginx "$backup/nginx"
rollback() {
    rm -f "$enabled" "$available"
    nginx -t && systemctl reload nginx
}
if ! { install -m 644 "$candidate" "$available" &&
    ln -s "$available" "$enabled" &&
    nginx -t && systemctl reload nginx && probe; }; then
    rollback
    exit 1
fi
printf 'TLS verified. Backup %s\n' "$backup"
