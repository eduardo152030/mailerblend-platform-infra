#!/usr/bin/env bash
# Run on PVE only; never edits a production CT or starts it automatically.
set -euo pipefail
CT="${1:?Expected approved rehearsal CT ID}"
case "$CT" in
  9618) ADDRESS=192.168.1.118 ;;
  9622) ADDRESS=192.168.1.122 ;;
  *) echo 'Only approved isolated rehearsal CTs 9618/9622 are allowed.' >&2; exit 2 ;;
esac
[[ "$(pct status "$CT")" == 'status: stopped' ]]
CONFIG=$(pct config "$CT")
grep -q '^onboot: 0$' <<< "$CONFIG"
grep '^net0:' <<< "$CONFIG" | grep -q 'link_down=1'
grep '^net0:' <<< "$CONFIG" | grep -q 'ip=manual'
pct mount "$CT" >/dev/null
ROOT="/var/lib/lxc/$CT/rootfs"
test -x "$ROOT/usr/sbin/ip"
install -d -m 755 "$ROOT/etc/systemd/system/docker.service.d"
printf '[Service]\nExecStartPre=-/usr/sbin/ip address add %s/32 dev lo\n' "$ADDRESS" > "$ROOT/etc/systemd/system/docker.service.d/recovery-isolation.conf"
pct unmount "$CT"
echo 'Clone-only loopback binding configured. Verify isolation before starting.'
