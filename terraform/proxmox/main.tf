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
  description   = "Managed by Terraform (inventory-driven)"
  start_on_boot = true
  tags          = each.value.tags

  # Clone from CT template
  clone {
    vm_id        = each.value.template_vmid
    node_name    = var.node_name
    datastore_id = each.value.storage
  }

  # Override basics after clone
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
  }

  # Optional: ensure NIC is on the right bridge (if your provider supports it)
  # network_interface {
  #   name   = "eth0"
  #   bridge = each.value.bridge
  # }

  # Disk sizing: only enable if your provider resource supports resizing here.
  # If you get a schema error, comment this block and we'll handle disk separately.
  disk {
    datastore_id = each.value.storage
    size         = each.value.disk_gb
  }

  # Resources: only enable if supported by your provider schema.
  # If you get errors, we adapt to the exact attribute names your version expects.
  cpu {
    cores = each.value.cpu
  }

  memory {
    dedicated = each.value.memory
  }
}
