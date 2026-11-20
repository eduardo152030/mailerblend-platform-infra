#!/bin/bash
set -euo pipefail
umask 077
test "$(hostname -s)" = infra-mail
source_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
map=/etc/postfix/outbound-header-checks
lookup=regexp:$map
backup=$(mktemp -d /etc/postfix/.before-headers.XXXXXXXX)
cp -a /etc/postfix/main.cf "$backup/"
if test -f "$map"; then cp -a "$map" "$backup/"; fi

rollback() {
    cp -a "$backup/main.cf" /etc/postfix/main.cf
    if test -f "$backup/outbound-header-checks"; then
        cp -a "$backup/outbound-header-checks" "$map"
    else
        rm -f -- "$map"
    fi
    postfix check && postfix reload
}
trap rollback ERR
install -m 0644 "$source_dir/outbound-header-checks" "$map"
test "$(postmap -q 'Received: from sender [192.168.1.65] by infra-mail.localdomain (Postfix)' "$lookup")" = IGNORE
postconf -e "smtp_header_checks = $lookup" 'smtp_helo_name = nucleotecnologico.es'
postfix check
postfix reload
trap - ERR
printf 'Filtro activo. Respaldo: %s\n' "$backup"
