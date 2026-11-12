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

# Future services only. Empty maps preserve the 17 existing CTs exactly.
variable "lxc_ssh_bootstrap_configs" {
  type        = map(string)
  description = "Private local bootstrap.json path by NEW service; opt-in, no existing CTs."
  default     = {}
}
variable "lxc_ssh_public_keys" {
  type        = map(list(string))
  description = "Optional complete key set for NEW CT provider injection. Clone default uses additive pct exec."
  default     = {}
}

# D066/D067: scoped temporary allocation or safety rollback; other services unchanged.
variable "voicebox_pilot_memory_mib" {
  type        = number
  default     = null
  description = "Temporary authorized CT627 pilot only; null preserves inventory."
  validation {
    condition     = var.voicebox_pilot_memory_mib == null || contains([3072, 4096], var.voicebox_pilot_memory_mib)
    error_message = "Only the historical4096 MiB pilot or3072 MiB safety rollback is allowed."
  }
}
