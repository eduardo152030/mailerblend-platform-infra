#!/usr/bin/env bash
set -euo pipefail

[[ "$(hostname -s)" == infra-eva-ui ]]
. /etc/os-release
[[ "$ID" == debian && "$VERSION_CODENAME" == bookworm ]]

default_site=/etc/nginx/sites-enabled/default
install -d -m 0755 /etc/nginx/sites-enabled
if [[ ! -e "$default_site" && ! -L "$default_site" ]]; then
    ln -s /dev/null "$default_site"
fi
[[ "$(readlink "$default_site")" == /dev/null ]]

export DEBIAN_FRONTEND=noninteractive
if ! dpkg-query -W -f='${db:Status-Status}' nginx-light 2>/dev/null | grep -Fxq installed; then
    apt-get update
    apt-get install -y --no-install-recommends nginx-light curl
fi

install -d -m 0755 /srv/infra-eva-ui
site=/etc/nginx/conf.d/infra-eva-ui-origin.conf
candidate=$(mktemp)
trap 'rm -f "$candidate"' EXIT
cat > "$candidate" <<'NGINX'
server {
    listen 127.0.0.1:8080;
    server_name localhost;
    root /srv/infra-eva-ui;

    location = /healthz {
        access_log off;
        return 204;
    }

    location / {
        add_header Cache-Control "no-store" always;
        try_files $uri /index.html =503;
    }
}
NGINX

if cmp -s "$candidate" "$site"; then
    [[ "$(curl -fsS -o /dev/null -w '%{http_code}' http://127.0.0.1:8080/healthz)" == 204 ]]
    printf '%s\n' 'Native origin verified. Configuration unchanged.'
    exit 0
fi
[[ ! -e "$site" && ! -L "$site" ]]
install -m 0644 "$candidate" "$site"
if ! nginx -t || ! systemctl reload nginx ||
    ! [[ "$(curl --silent --max-time 10 --retry 3 --retry-all-errors --retry-delay 1 -o /dev/null -w '%{http_code}' http://127.0.0.1:8080/healthz)" == 204 ]]; then
    rm -f "$site"
    nginx -t && systemctl reload nginx
    exit 1
fi
printf '%s\n' 'Native origin verified on loopback.'
