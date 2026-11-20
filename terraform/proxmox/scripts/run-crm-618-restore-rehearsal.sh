#!/usr/bin/env bash
# Run from the repository; the host adapter only starts and stops CT9618.
set -euo pipefail
[[ "$#" == 1 && "$1" =~ ^storage:backup/vzdump-lxc-618-[0-9_:-]+\.tar\.zst$ ]] || {
    echo 'Uso: run-crm-618-restore-rehearsal.sh storage:backup/vzdump-lxc-618-FECHA.tar.zst' >&2
    exit 2
}
root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
ssh_pve=(ssh -o "UserKnownHostsFile=$HOME/.ssh/known_hosts" -o StrictHostKeyChecking=yes -o BatchMode=yes pve)

stop_clone() {
    if ! "${ssh_pve[@]}" 'if [ "$(pct status 9618)" = "status: running" ]; then pct shutdown 9618 --timeout 90; fi; test "$(pct status 9618)" = "status: stopped"'; then
        echo 'BLOCKED: comprobar el estado del clon aislado 9618' >&2
        return 1
    fi
}
"${ssh_pve[@]}" "bash -s -- '$1'" < "$root/restore-crm-618-rehearsal.sh"
"${ssh_pve[@]}" 'bash -s -- 9618' < "$root/setup-isolated-recovery.sh"
trap 'status=$?; stop_clone || status=1; exit "$status"' EXIT
"${ssh_pve[@]}" 'pct start 9618'
for ((attempt=0; attempt<36; attempt++)); do
    if "${ssh_pve[@]}" 'pct exec 9618 -- systemctl is-active --quiet docker'; then
        "${ssh_pve[@]}" 'pct exec 9618 -- python3 -' < "$root/check-crm-618-restored-login.py"
        exit 0
    fi
    sleep 5
done
echo 'BLOCKED: Docker no alcanzó readiness en el clon aislado' >&2
exit 1
