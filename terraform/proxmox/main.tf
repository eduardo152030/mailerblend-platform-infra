provider "proxmox" {
  endpoint  = var.proxmox_endpoint
  api_token = var.proxmox_api_token
  insecure  = true
}

resource "proxmox_virtual_environment_container" "tf_test" {
  node_name     = var.node_name
  vm_id         = var.ct_id
  description   = "Managed by Terraform (smoke test: clone CT template)"
  start_on_boot = true
  tags          = ["infra", "terraform", "test"]

  # Clone from your CT template (VMID 106)
  clone {
    vm_id        = var.template_ct_id
    node_name    = var.node_name
    datastore_id = var.datastore_id
  }

  # Override basics after clone
  initialization {
    hostname = var.ct_hostname

    dns {
      servers = [var.dns_server]
    }

    ip_config {
      ipv4 {
        address = var.ct_ip_cidr
        gateway = var.gateway
      }
    }
  }
}
