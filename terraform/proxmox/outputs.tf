output "services" {
  description = "Services created from inventory (source of truth = inventory locals)"
  value = {
    for k, s in local.services :
    k => {
      vm_id    = proxmox_virtual_environment_container.svc[k].vm_id
      name     = s.name
      ip       = s.ip
      tags     = s.tags
      cpu      = s.cpu
      memory   = s.memory
      disk_gb  = s.disk_gb
      gateway  = s.gateway
      dns      = s.dns
      storage  = s.storage
      template = s.template_vmid
    }
  }
}
