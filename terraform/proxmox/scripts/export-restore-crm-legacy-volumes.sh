#!/bin/bash
# Run on PVE. Only the disposable CT9619 is changed. Standard input is the catalogue exporter.
set -euo pipefail
umask 077
ct=9619
[[ "$(pct status "$ct")" == 'status: running' ]]
config=$(pct config "$ct")
grep -qx "hostname: crm-rehearsal-$ct" <<< "$config"
grep -qx 'onboot: 0' <<< "$config"
awk '/^net0:/ && /link_down=1/ && /ip=manual/ { seen++ } /^net[1-9]/ { bad++ } END { exit !(seen==1 && !bad) }' <<< "$config"
[[ "$(findmnt -n -o TARGET /mnt/storage)" == /mnt/storage ]]
directory=$(mktemp -d /mnt/storage/crm-legacy-final.XXXXXXXX)
echo "Private export directory: $directory"

names=(budibase-app budibase-couchdb budibase-redis)
targets=(/data /opt/couchdb/data /data)
sources=()
for index in "${!names[@]}"; do
    source=$(pct exec "$ct" -- docker inspect --format '{{range .Mounts}}{{println .Type .Source .Destination}}{{end}}' "${names[index]}" |
        awk -v path="${targets[index]}" '$1=="volume" && $3==path {print $2}')
    [[ "$source" =~ ^/var/lib/docker/volumes/[a-zA-Z0-9_-]+/_data$ ]]
    sources+=("$source")
done

pct exec "$ct" -- docker stop budibase-app >/dev/null
pct exec "$ct" -- python3 - | zstd -T1 -q > "$directory/catalogue.json.zst"
pct exec "$ct" -- docker stop budibase-couchdb budibase-redis >/dev/null
for index in "${!names[@]}"; do
    pct exec "$ct" -- tar --numeric-owner --xattrs -cpf - -C "${sources[index]}" . |
      zstd -T1 -q > "$directory/${names[index]}.tar.zst"
done
(
    cd "$directory"
    sha256sum ./*.zst > SHA256SUMS
    sha256sum -c SHA256SUMS
    zstd -t -- ./*.zst
)
for index in "${!names[@]}"; do
    source=${sources[index]}
    restored=$(pct exec "$ct" -- mktemp -d "$source.rehearsal.XXXXXXXX")
    zstd -dc "$directory/${names[index]}.tar.zst" |
      pct exec "$ct" -- tar --numeric-owner --xattrs -xpf - -C "$restored"
    pct exec "$ct" -- test ! -e "$source.before-final-rehearsal"
    pct exec "$ct" -- mv -T "$source" "$source.before-final-rehearsal"
    pct exec "$ct" -- mv -T "$restored" "$source"
done
pct exec "$ct" -- docker start budibase-couchdb budibase-redis budibase-app >/dev/null
echo 'PASS: SHA-256 and restore of three archives into the disconnected clone.'
