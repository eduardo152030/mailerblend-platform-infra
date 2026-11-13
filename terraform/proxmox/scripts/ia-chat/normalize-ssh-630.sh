#!/bin/sh
# Debian12: SSH en modo servicio; evita conflicto socket/SIGHUP del bootstrap.
set -eu
[ "$(cat /etc/hostname)" = infra-llm ]
if ! dpkg-query -W -f='${Status}' dbus 2>/dev/null | grep -q 'install ok installed'; then
  apt-get update -qq
  DEBIAN_FRONTEND=noninteractive apt-get install -y -qq dbus
fi
systemctl start dbus
systemctl start systemd-logind || true
if systemctl is-active --quiet ssh.socket; then systemctl disable --now ssh.socket; fi
if ! systemctl is-active --quiet ssh.service; then
  install -d -m 0755 /run/sshd
  systemctl reset-failed ssh.service
  systemctl enable --now ssh.service
fi
/usr/sbin/sshd -t
