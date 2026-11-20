#!/usr/bin/env bash
# Run on the Proxmox node; verify a fresh snapshot and restore only to CT9618.
set -euo pipefail

[[ "$#" == 1 && "$1" =~ ^storage:backup/vzdump-lxc-618-[0-9_:-]+\.tar\.zst$ ]] || {
    echo 'Uso: restore-crm-618-rehearsal.sh storage:backup/vzdump-lxc-618-FECHA.tar.zst' >&2
    exit 2
}
volume=$1
archive=$(pvesm path "$volume")
[[ "$archive" == /mnt/storage/dump/vzdump-lxc-618-*.tar.zst && -f "$archive" && ! -L "$archive" && -O "$archive" ]]
[[ $(find "$archive" -maxdepth 0 -mmin -720 -print) == "$archive" ]]
log=${archive%.tar.zst}.log
grep -q 'backup mode: snapshot' "$log"
grep -q 'Finished Backup of VM 618' "$log"
! grep -Eq "trying '(stop|suspend)'|ERROR:" "$log"
[[ $(pvesh get /cluster/nextid --vmid 9618 --output-format json) == '"9618"' ]]
[[ "$(pct status 618)" == 'status: running' ]]
pvesm status | awk '$1 == "storage" && $3 == "active" && $6 >= 104857600 { ok=1 } END { exit !ok }'
[[ $(awk '/^MemAvailable:/ {print $2}' /proc/meminfo) -ge 10485760 ]]

chmod 600 -- "$archive"
ionice -c 3 nice -n 15 zstd -t -- "$archive"
(
    cd "$(dirname "$archive")"
    file=$(basename "$archive")
    umask 077
    set -o noclobber
    if [[ ! -e "$file.sha256" ]]; then
        checksum=$(ionice -c 3 nice -n 15 sha256sum -- "$file")
        printf '%s\n' "$checksum" > "$file.sha256"
    fi
    [[ -f "$file.sha256" && ! -L "$file.sha256" && -O "$file.sha256" ]]
    ionice -c 3 nice -n 15 sha256sum -c -- "$file.sha256"
)
info=$(pvesm extractconfig "$volume")
awk -F: '
    $1 == "rootfs" { root++ }
    $1 == "net0" { net++ }
    $1 ~ /^(hookscript|mp[0-9]+|unused[0-9]+|net[1-9][0-9]*)$/ { blocked++ }
    END { exit !(root == 1 && net == 1 && !blocked) }' <<< "$info"

pct restore 9618 "$volume" --storage storage --onboot 0 --start 0 --bwlimit 40960 \
    --hostname crm-rehearsal-9618 \
    --net0 name=eth0,bridge=vmbr0,firewall=1,ip=manual,ip6=manual,link_down=1,type=veth
[[ "$(pct status 9618)" == 'status: stopped' ]]
config=$(pct config 9618)
grep -qx 'onboot: 0' <<< "$config"
awk -F: '
    $1 == "net0" && /link_down=1/ && /ip=manual/ && /ip6=manual/ { net++ }
    $1 ~ /^net[1-9]/ { blocked++ }
    END { exit !(net == 1 && !blocked) }' <<< "$config"
[[ "$(pct status 618)" == 'status: running' ]]
echo 'PASS: CT9618 restaurado, apagado, con arranque automático desactivado y NIC desconectada.'
