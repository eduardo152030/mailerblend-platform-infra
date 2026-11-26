#!/usr/bin/env bash
set -euo pipefail
umask 077
stage="${2:?Private staging directory required}"
case "${1:?Expected origin or edge}" in
    origin)
        [[ "$(hostname -s)" == infra-eva-ui ]]
        site=/etc/nginx/conf.d/infra-eva-ui-tls.conf
        install -d -m 0700 /etc/nginx/eva-ui
        install -m 0644 "$stage/server.crt" /etc/nginx/eva-ui/server.crt
        install -m 0600 "$stage/server.key" /etc/nginx/eva-ui/server.key
        if cmp -s "$stage/ui-origin.conf" "$site"; then
            nginx -t
            exit 0
        fi
        [[ ! -e "$site" && ! -L "$site" ]]
        install -m 0644 "$stage/ui-origin.conf" "$site"
        if ! nginx -t || ! systemctl reload nginx; then
            unlink "$site"
            nginx -t && systemctl reload nginx
            exit 1
        fi
        ;;
    edge)
        [[ "$(hostname -s)" == edge-router ]]
        site=/etc/nginx/sites-available/infra-eva-ui.mailerblend.com.conf
        enabled=/etc/nginx/sites-enabled/infra-eva-ui.mailerblend.com.conf
        [[ "$(readlink "$enabled")" == "$site" ]]
        curl -fsS --max-time 8 --cacert "$stage/origin-ca.crt" \
            --resolve eva-ui.internal:18443:192.168.1.73 https://eva-ui.internal:18443/healthz -o /dev/null
        curl -fsS --max-time 8 --cacert "$stage/origin-ca.crt" \
            --resolve eva-api.internal:18443:192.168.1.122 https://eva-api.internal:18443/health -o /dev/null
        if cmp -s "$stage/web-vhost.conf" "$site"; then
            nginx -t
            exit 0
        fi
        if ! grep -F 'return 503 "EVA UI en preparacion' "$site" >/dev/null; then
            cmp -s "$stage/web-vhost.previous.conf" "$site"
        fi
        backup=$(mktemp -d /var/backups/eva-ui-cutover.XXXXXX)
        cp -p "$site" "$backup/vhost.conf"
        install -d -m 0755 /etc/nginx/eva-ui
        install -m 0644 "$stage/origin-ca.crt" /etc/nginx/eva-ui/origin-ca.crt
        install -m 0644 "$stage/web-vhost.conf" "$site"
        check() {
            local root auth login
            root=$(curl -sS --max-time 5 --resolve infra-eva-ui.mailerblend.com:443:127.0.0.1 \
                -o /dev/null -w '%{http_code}' https://infra-eva-ui.mailerblend.com/) || return 1
            auth=$(curl -sS --max-time 5 --resolve infra-eva-ui.mailerblend.com:443:127.0.0.1 \
                -o /dev/null -w '%{http_code}' https://infra-eva-ui.mailerblend.com/eva-api/ui/session) || return 1
            [[ "$root" == 200 && "$auth" == 401 ]] || return 1
            login=$(curl -sS --max-time 5 --resolve infra-eva-ui.mailerblend.com:443:127.0.0.1 \
                -o /dev/null -w '%{http_code}' -H 'Content-Type: application/json' --data '{}' \
                'https://infra-eva-ui.mailerblend.com/auth/v1/token?grant_type=password') || return 1
            [[ "$login" == 400 || "$login" == 422 ]]
        }
        if nginx -t && systemctl reload nginx; then
            for attempt in {1..8}; do
                if check; then
                    printf 'Edge verified. Maintenance vhost backup: %s\n' "$backup"
                    exit 0
                fi
                sleep 1
            done
        fi
        cp -p "$backup/vhost.conf" "$site"
        nginx -t && systemctl reload nginx
        exit 1
        ;;
    *) exit 2 ;;
esac
