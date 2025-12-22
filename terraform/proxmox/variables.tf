variable "proxmox_endpoint" {
  type        = string
  description = "https://<PVE-IP>:8006/api2/json"
}

variable "proxmox_api_token" {
  type        = string
  sensitive   = true
  description = "Format: user@realm!tokenid=secret"
}

variable "node_name" {
  type    = string
  default = "pve"
}

variable "template_ct_id" {
  type        = number
  description = "Source CT template VMID (your template). Example: 106"
}

variable "ct_id" {
  type        = number
  description = "New CT VMID to create. Example: 601"
}

variable "ct_hostname" {
  type    = string
  default = "infra-tf-test"
}

variable "ct_ip_cidr" {
  type        = string
  description = "Example: 192.168.1.99/24"
}

variable "gateway" {
  type    = string
  default = "192.168.1.254"
}

variable "dns_server" {
  type    = string
  default = "192.168.1.254"
}

variable "datastore_id" {
  type    = string
  default = "local-lvm"
}
