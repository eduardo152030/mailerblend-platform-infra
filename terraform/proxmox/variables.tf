variable "proxmox_endpoint" {
  type        = string
  description = "Proxmox API endpoint, e.g. https://pve:8006/"
}

variable "proxmox_api_token" {
  type        = string
  description = "Proxmox API token in the form 'user@pam!token=VALUE'"
  sensitive   = true
}

variable "node_name" {
  type        = string
  description = "Proxmox node name, e.g. pve"
}
