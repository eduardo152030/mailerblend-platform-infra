#!/bin/bash
# Ejecutar como root en el CT con los ficheros privados ya instalados.
set -euo pipefail
umask 077
config=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
private=/etc/infra-mail/private
mode=${1:-production}
case "$mode" in
    production) test -s "$private/relay-host" && test -s "$private/relay-password" ;;
    --mailpit) systemctl is-active --quiet infra-mail-mailpit ;;
    *) echo 'Modo desconocido' >&2; exit 1 ;;
esac
for name in tls.crt tls.key service-users sender-login; do
    test -s "$private/$name"
done
openssl x509 -checkend 604800 -noout -in "$private/tls.crt" >/dev/null
relay='[127.0.0.1]:1025'
transport_security=none
upstream_auth=no
if [[ "$mode" == production ]]; then
    relay=$(<"$private/relay-host")
    transport_security=secure
    upstream_auth=yes
fi
if [[ "$mode" == production && ! "$relay" =~ ^\[[a-zA-Z0-9.-]+\]:(465|587)$ ]]; then
    echo 'Formato o puerto del SMTP upstream inválido' >&2
    exit 1
fi
wrapper=no
if [[ "$relay" == *:465 ]]; then
    wrapper=yes
fi

export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq -o Dpkg::Options::=--force-confold postfix dovecot-core libsasl2-modules ca-certificates
systemctl stop postfix dovecot
install -d /usr/local/lib/infra-mail
install -m 0644 "$config/submission-policy.py" /usr/local/lib/infra-mail/
install -m 0644 "$config/queue-metrics.py" /usr/local/lib/infra-mail/
install -m 0644 "$config/infra-mail-policy.service" /etc/systemd/system/
install -m 0644 "$config/infra-mail-queue.service" "$config/infra-mail-queue.timer" /etc/systemd/system/
install -m 0644 "$config/dovecot-auth.conf" /etc/dovecot/dovecot.conf
install -o root -g dovecot -m 0640 "$private/service-users" /etc/dovecot/
install -m 0644 "$config/submission-clients" /etc/postfix/
install -m 0600 "$private/sender-login" /etc/postfix/
postmap hash:/etc/postfix/sender-login
if [[ "$mode" == production ]]; then
    install -m 0600 "$private/relay-password" /etc/postfix/
    postmap hash:/etc/postfix/relay-password
fi

# Solo submission escucha por TCP; se conservan los servicios internos Unix.
postconf -MX smtp/inet
if ! postconf -M submission/inet >/dev/null 2>&1; then
    cat "$config/submission.cf" >> /etc/postfix/master.cf
fi
postconf -e 'inet_protocols = ipv4' 'inet_interfaces = all' \
    'mydestination = localhost' \
    "smtpd_tls_cert_file = $private/tls.crt" "smtpd_tls_key_file = $private/tls.key" \
    "relayhost = $relay" "smtp_tls_wrappermode = $wrapper" \
    "smtp_tls_security_level = $transport_security" \
    'smtp_tls_CAfile = /etc/ssl/certs/ca-certificates.crt' \
    "smtp_sasl_auth_enable = $upstream_auth" \
    'smtp_sasl_security_options = noanonymous' \
    'smtp_sasl_password_maps = hash:/etc/postfix/relay-password' \
    'disable_vrfy_command = yes'
postfix check
doveconf -n >/dev/null
systemctl daemon-reload
systemctl enable --now infra-mail-policy dovecot postfix
systemctl enable --now infra-mail-queue.timer
