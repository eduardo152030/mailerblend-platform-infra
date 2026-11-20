#!/usr/bin/env bash
# Run from the reviewed worktree with an authorized, verified CT618 archive.
set -euo pipefail
[[ "$#" == 2 && "$1" =~ ^storage:backup/vzdump-lxc-618-[0-9_:-]+\.tar\.zst$ && "$2" =~ ^(prepare|execute)$ ]] || {
    echo 'Uso: run-crm-618-couchdb-rotation.sh storage:backup/vzdump-lxc-618-FECHA.tar.zst prepare|execute' >&2
    exit 2
}
root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
ssh_pve=(ssh -o "UserKnownHostsFile=$HOME/.ssh/known_hosts" -o StrictHostKeyChecking=yes -o BatchMode=yes pve)
"${ssh_pve[@]}" "bash -s -- '$1'" <<'BASH'
set -euo pipefail
archive=$(pvesm path "$1")
[[ "$archive" == /mnt/storage/dump/vzdump-lxc-618-*.tar.zst ]]
[[ -f "$archive" && -f "$archive.sha256" && ! -L "$archive" && ! -L "$archive.sha256" ]]
[[ "$(stat -c %a "$archive")" == 600 && "$(stat -c %a "$archive.sha256")" == 600 ]]
[[ $(find "$archive" -maxdepth 0 -mmin -720 -print) == "$archive" ]]
[[ "$(pct status 618)" == 'status: running' && "$(pct status 9618)" == 'status: stopped' ]]
(cd "$(dirname "$archive")" && ionice -c 3 nice -n 15 sha256sum -c -- "$(basename "$archive").sha256")
BASH
tar -C "$root" -cf - rotate-crm-618-couchdb.py check-crm-couchdb-rotation.py |
    "${ssh_pve[@]}" "pct exec 618 -- bash -c 'set -euo pipefail; umask 077; stage=\$(mktemp -d /root/crm-couchdb-rotation.XXXXXXXX); tar -xf - -C \"\$stage\"; exec python3 \"\$stage/rotate-crm-618-couchdb.py\" $2 \"\$stage\"'"
