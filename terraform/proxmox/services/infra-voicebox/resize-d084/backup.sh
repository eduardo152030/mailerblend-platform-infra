#!/bin/sh
# Authorized D084 only: full CT627 backup to existing HDD, no prune/no restart.
set -eu
umask 077
[ "$(pct status 627)" = 'status: running' ]
[ "$(findmnt -no SOURCE /mnt/storage)" = /dev/sdb ]
[ "$(pct config 627 | sed -n 's/^rootfs: //p')" = 'local-lvm:vm-627-disk-0,size=50G' ]
[ ! -e /mnt/storage/d084-627 ]
install -d -m 0700 /mnt/storage/d084-627
exec vzdump 627 --storage storage --mode snapshot --compress zstd --zstd 1 \
  --bwlimit 51200 --ionice 7 --stdexcludes 0 --remove 0 \
  --tmpdir /mnt/storage/d084-627 --notification-mode legacy-sendmail \
  --notification-policy never --prune-backups keep-all=1
