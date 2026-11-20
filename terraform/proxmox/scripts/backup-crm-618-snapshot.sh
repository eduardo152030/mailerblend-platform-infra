#!/usr/bin/env bash
# Run on the authorized Proxmox node. Backup only, never restore or restart.
set -euo pipefail

[[ "$#" == 1 && "$1" == --snapshot-618 ]] || {
    echo 'Uso: backup-crm-618-snapshot.sh --snapshot-618' >&2
    exit 2
}

vmid=618
storage=storage
[[ "$(pct status "$vmid")" == "status: running" ]]
pct config "$vmid" | awk '
    /^rootfs: local-lvm:vm-618-disk-0,/ { root++ }
    /^(lock|mp[0-9]+|unused[0-9]+|hookscript):/ { blocked++ }
    END { exit !(root == 1 && !blocked) }'
pct listsnapshot "$vmid" | awk '/[[:space:]]vzdump[[:space:]]/ { bad=1 } END { exit bad }'
[[ "$(findmnt -n -o TARGET /mnt/storage)" == /mnt/storage ]]
pvesm status | awk '$1 == "storage" && $3 == "active" && $6 >= 104857600 { ok=1 } END { exit !ok }'
pvesh get "/nodes/$(hostname)/lxc/$vmid/feature" --feature snapshot --output-format json |
    python3 -c 'import json,sys; assert json.load(sys.stdin)["hasFeature"]'

inventory() {
    pct exec "$vmid" -- docker inspect --format '{{.Name}} {{.Id}} {{.State.Running}} {{.State.StartedAt}}' \
        budibase-app budibase-couchdb budibase-redis crm-api supabase-db
}

before=$(inventory)
awk '$3 != "true" { fail=1 } END { exit (fail || NR != 5) }' <<< "$before"
archives() {
    pvesh get "/nodes/$(hostname)/storage/$storage/content" --vmid "$vmid" \
        --content backup --output-format json
}

prior=$(archives)
vzdump "$vmid" --mode snapshot --storage "$storage" --compress zstd --remove 0 --bwlimit 40960 --ionice 7
[[ "$(pct status "$vmid")" == "status: running" ]]
[[ "$before" == "$(inventory)" ]]
archives |
    CRM_PRIOR_ARCHIVES="$prior" python3 -c '
import json, os, sys
before={item["volid"] for item in json.loads(os.environ["CRM_PRIOR_ARCHIVES"])}
new=[item for item in json.load(sys.stdin) if item["volid"] not in before]
assert len(new)==1 and int(new[0]["size"])>0
print("NEW_ARCHIVE", new[0]["volid"], new[0]["size"])
'
echo 'PASS: CT618 y los cinco contenedores conservan su inicio.'
