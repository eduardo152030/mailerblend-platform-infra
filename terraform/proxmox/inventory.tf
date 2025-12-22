locals {
  defaults = yamldecode(file("${path.module}/inventory/defaults.yml"))

  service_files = fileset("${path.module}/inventory/services", "*.yml")

  services_raw = {
    for f in local.service_files :
    trimsuffix(basename(f), ".yml") => yamldecode(file("${path.module}/inventory/services/${f}"))
  }

  # Merge defaults + overrides por servicio
  services = {
    for k, s in local.services_raw : k => {
      name = s.service.name
      vmid = s.service.vmid
      ip   = s.service.ip

      cpu     = try(s.resources.cpu, local.defaults.lxc.cpu)
      memory  = try(s.resources.memory, local.defaults.lxc.memory)
      disk_gb = try(s.resources.disk_gb, local.defaults.lxc.disk_gb)

      gateway = try(s.network.gateway, local.defaults.lxc.gateway)
      dns     = try(s.network.dns, local.defaults.lxc.dns)

      bridge        = try(s.network.bridge, local.defaults.lxc.bridge)
      storage       = try(s.storage.name, local.defaults.lxc.storage)
      template_vmid = local.defaults.lxc.template_vmid

      tags = distinct(concat(
        try(local.defaults.lxc.tags, []),
        try(s.tags, [])
      ))
    }
  }
}
