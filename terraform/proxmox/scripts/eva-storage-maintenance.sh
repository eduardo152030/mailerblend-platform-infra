#!/usr/bin/env bash
# Approved, bounded operations only. Run inside EVA after verified backup/restore.
set -euo pipefail
[[ "${1:-}" == --execute && -n "${2:-}" && -n "${3:-}" ]] || {
  echo 'Usage: eva-storage-maintenance.sh --execute <verified-record.json> <cache|journal>' >&2; exit 2;
}
python3 - "$2" <<'PY'
import json,sys
r=json.load(open(sys.argv[1]));assert all(r.get(k) is True for k in ['backup_verified','offhost_verified','restore_verified','images_preserved','logs_archived'])
PY
case "$3" in
  cache)
    # Installed Docker delegates to Buildx: preserve a 4 GB floor and cap old cache.
    docker builder prune --all --filter until=168h --reserved-space 4GB --max-used-space 4GB --force
    ;;
  journal)
    test -r /tmp/60-mailerblend-retention.conf
    install -d -m 755 /etc/systemd/journald.conf.d
    install -m 644 /tmp/60-mailerblend-retention.conf /etc/systemd/journald.conf.d/60-mailerblend-retention.conf
    systemctl restart systemd-journald
    journalctl --rotate
    journalctl --vacuum-size=1G --vacuum-time=30d
    journalctl --disk-usage
    ;;
  *) echo 'Only reviewed cache/journal operations are supported.' >&2; exit 2 ;;
esac
