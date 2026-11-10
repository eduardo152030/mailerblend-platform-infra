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
  tags          = lookup(var.recovery_preserve_service_tags, each.key, each.value.tags)

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

    # Opcional: Si quieres pasar la clave SSH pública aquí
    # user_account {
    #   keys = [var.ssh_public_key]
    # }
  }

  disk {
    datastore_id = each.value.storage
    size         = each.value.disk_gb # Nuestro script de auto-resize se encargará del resto
  }

  cpu {
    cores = each.value.cpu
  }

  memory {
    dedicated = each.value.memory
    swap      = 512
  }
}