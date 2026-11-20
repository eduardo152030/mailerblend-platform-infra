#!/usr/bin/env bash
# Run from the repository; the host adapter only starts and stops CT9618.
set -euo pipefail
[[ "$#" -ge 1 && "$#" -le 2 && "$1" =~ ^storage:backup/vzdump-lxc-618-[0-9_:-]+\.tar\.zst$ ]] || {
    echo 'Uso: run-crm-618-restore-rehearsal.sh storage:backup/vzdump-lxc-618-FECHA.tar.zst [--resume-restored|--recheck-fixture]' >&2
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
case "${2:-}" in
    "")
        "${ssh_pve[@]}" "bash -s -- '$1'" < "$root/restore-crm-618-rehearsal.sh"
        ;;
    --resume-restored|--recheck-fixture)
        "${ssh_pve[@]}" 'test "$(pct status 9618)" = "status: stopped" &&
            pct config 9618 | grep -qx "hostname: crm-rehearsal-9618" &&
            test -f /mnt/storage/images/9618/vm-9618-disk-0.raw'
        ;;
    *) exit 2 ;;
esac
"${ssh_pve[@]}" 'bash -s -- 9618' < "$root/setup-isolated-recovery.sh"
trap 'status=$?; stop_clone || status=1; exit "$status"' EXIT
"${ssh_pve[@]}" 'pct start 9618'
for ((attempt=0; attempt<60; attempt++)); do
    if "${ssh_pve[@]}" 'pct exec 9618 -- systemctl is-active --quiet docker'; then
        if [[ "${2:-}" == --recheck-fixture ]]; then
            "${ssh_pve[@]}" 'pct exec 9618 -- python3 - --recheck-fixture' < "$root/check-crm-618-restored-login.py"
        else
            "${ssh_pve[@]}" 'pct exec 9618 -- python3 -' < "$root/check-crm-618-restored-login.py"
        fi
        exit 0
    fi
    sleep 5
done
echo 'BLOCKED: Docker no alcanzó readiness en el clon aislado' >&2
exit 1
