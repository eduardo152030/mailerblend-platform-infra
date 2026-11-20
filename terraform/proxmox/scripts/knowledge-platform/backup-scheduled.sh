#!/usr/bin/env bash
set -euo pipefail
umask 077
root="${KNOWLEDGE_BACKUP_ROOT:?Backup directory required}"
key="${KNOWLEDGE_BACKUP_KEY:?Private key file required}"
material="${KNOWLEDGE_OPERATOR_MATERIAL:?Operator material required}"
[[ -d "$root" && ! -L "$root" && "$(stat -c %a "$root")" == 700 ]]
exec 9>"$root/.backup.lock"
flock -n 9
here="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$here/backup-private.py" \
  --output "$root/backup-$(date -u +%Y%m%dT%H%M%SZ)" \
  --key-file "$key" --operator-material "$material" --retention-days 30
