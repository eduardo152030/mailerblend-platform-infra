output "ct_id" {
  value = proxmox_virtual_environment_container.tf_test.vm_id
}

output "ct_hostname" {
  value = var.ct_hostname
}

output "ct_ip" {
  value = var.ct_ip_cidr
}
