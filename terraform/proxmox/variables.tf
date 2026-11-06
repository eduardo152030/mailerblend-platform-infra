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

# Opt-in recovery scope: preserve observed labels while changing only approved resources.
variable "recovery_preserve_service_tags" {
  type        = map(list(string))
  description = "Temporary recovery overrides; empty by default so normal inventory behavior is unchanged."
  default     = {}
}
