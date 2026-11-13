provider "proxmox" {
  endpoint  = var.proxmox_endpoint
  api_token = var.proxmox_api_token
  insecure  = true
}

# Multi-service LXC: inventory/services/*.yml
resource "proxmox_virtual_environment_container" "svc" {
  for_each = local.services

  node_name     = var.node_name
  vm_id         = each.value.vmid
  description   = local.lxc_descriptions[each.key]
  start_on_boot = true
  # PVE automation adds the IP tag and returns sorted tags. Only new SSH-managed
  # CTs opt in; legacy CT expressions and recovery overrides remain unchanged.
  tags = lookup(var.recovery_preserve_service_tags, each.key,
    try(local.services_raw[each.key].provisioning.ssh.enabled, false) ?
    sort(distinct(concat(each.value.tags, [split("/", each.value.ip)[0]]))) : each.value.tags
  )

  # --- CONFIGURACIÓN CRÍTICA PARA DOCKER ---
  unprivileged = false # <--- Obligatorio para Grafana/Docker sin errores de kernel

  features {
    nesting = each.value.docker
    keyctl  = each.value.docker
  }

  # Clone from CT template
  clone {
    vm_id        = each.value.template_vmid
    node_name    = var.node_name
    datastore_id = each.value.storage
  }

  lifecycle {
    precondition {
      condition     = each.key != "infra-voicebox" || (each.value.memory <= 20480 && each.value.cpu == 3 && contains([50, 100], each.value.disk_gb))
      error_message = "D087 CT627: maximum20480 MiB,3 vCPU and approved50/100 GiB SSD; other resource changes require new authorization."
    }
    precondition {
      condition     = !try(local.services_raw[each.key].provisioning.ssh.enabled, false) || contains(keys(var.lxc_ssh_bootstrap_configs), each.key)
      error_message = "New SSH-managed LXC requires its private bootstrap config; pass the prepared ssh-bootstrap.auto.tfvars.json."
    }
    precondition {
      condition     = !contains(keys(var.lxc_ssh_public_keys), each.key) || (try(local.services_raw[each.key].provisioning.ssh.enabled, false) && try(local.services_raw[each.key].provisioning.ssh.provider_key_set_complete, false))
      error_message = "Provider injection requires a reviewed complete template key set; default clone bootstrap merges via pct exec."
    }
    precondition {
      condition     = local.lxc_notes_fresh && length(local.lxc_notes_input) == length(local.services) && toset(keys(local.lxc_notes_input)) == toset(keys(local.services))
      error_message = "LXC notes are stale or incomplete. Run python3 scripts/generate-lxc-inventory.py and review all service records."
    }

    ignore_changes = [
      clone, # Evita que cambie/destruya los LXC si actualizas la plantilla base
      disk,  # Evita errores de API al intentar encoger discos en Proxmox
    ]
  }

  initialization {
    hostname = each.value.name

    dns {
      servers = each.value.dns
    }

    ip_config {
      ipv4 {
        address = each.value.ip
        gateway = each.value.gateway
      }
    }

    # Never inject into legacy CTs: keys are ForceNew in this provider.
    dynamic "user_account" {
      for_each = contains(keys(var.lxc_ssh_public_keys), each.key) && try(local.services_raw[each.key].provisioning.ssh.enabled, false) ? [1] : []
      content {
        keys = var.lxc_ssh_public_keys[each.key]
      }
    }
  }

  disk {
    datastore_id = each.value.storage
    size         = each.value.disk_gb # Nuestro script de auto-resize se encargará del resto
  }

  cpu {
    cores = each.value.cpu
  }

  memory {
    dedicated = each.key == "infra-voicebox" && var.voicebox_pilot_memory_mib != null ? var.voicebox_pilot_memory_mib : each.value.memory
    swap      = each.key == "infra-voicebox" ? try(local.services_raw[each.key].resources.swap, 512) : 512
  }
  # Creation only; existing resources never execute this provisioner.
  provisioner "local-exec" {
    command     = "python3 scripts/bootstrap-new-lxc-ssh.py --execute --if-configured"
    working_dir = path.module
    environment = {
      LXC_SSH_CONFIG = lookup(var.lxc_ssh_bootstrap_configs, each.key, "")
      LXC_PVE_NODE   = var.node_name
    }
  }

}
