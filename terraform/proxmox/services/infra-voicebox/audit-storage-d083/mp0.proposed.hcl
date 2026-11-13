# SUPERSEDED by owner: prefer SSD rootfs50→100GiB. Historical proposal only.
# PROPOSAL ONLY. Not loaded by Terraform and NOT safe to apply directly to CT627.
# Provider0.94.0 plans replacement when adding mount_point; see audit evidence.
# Inside the existing svc resource, after adding an approved per-service inventory map:
dynamic "mount_point" {
  for_each = each.key == "infra-voicebox" ? try(local.services_raw[each.key].resources.additional_mounts, []) : []
  content {
    volume    = mount_point.value.volume
    size      = mount_point.value.size
    path      = mount_point.value.path
    backup    = mount_point.value.backup
    replicate = false
    read_only = false
    shared    = false
  }
}
# Proposed CT627 inventory item, not inserted into the active YAML:
# resources.additional_mounts:
#   - volume: storage
#     size: 100G
#     path: /srv/voicebox/ai-models
#     backup: false
# Public model/cache data ONLY. Explicitly excluded from vzdump, with separate
# pinned manifests/off-host recovery. backup=true is an alternative requiring
# stop/suspend backups because the directory/raw volume cannot snapshot.
