# 17 — Principio IaC-only: ningún cambio manual en producción

## Regla principal

Este repositorio gestiona 17 contenedores LXC en Proxmox mediante Terraform.
**Todos los cambios de infraestructura deben ser declarativos y versionados.**

Nunca ejecutes comandos interactivos o imperativos en producción.
Si algo requiere un comando manual, primero pregúntate: ¿puedo escribirlo
como un bloque Terraform o como un script versionado en `scripts/`?

## Prohibido

- **`pct shell`** — nunca entres en un CT de producción.
- **`ssh <service>`** — nunca ejecutes comandos en un CT de producción.
- **`docker exec` / `docker compose exec`** — no ejecutes comandos dentro
  de contenedores en producción.
- **`vim` / `nano` / `ed`** — nunca edites archivos en producción.
- **`systemctl restart/stop/start`** — nunca reinicies servicios manualmente.
- **`pct setcfg` / `pct exec`** — nunca modifiques configuración
  directamente (solo lectura está permitido, ver excepción).
- **`qm/ pct set` imperativo** — nunca cambies configuración sin pasar
  por Terraform.

## Obligatorio

- **Terraform declarativo**: todos los cambios de infraestructura deben
  escribirse como bloques Terraform en `terraform/`.
- **Scripts versionados**: cualquier automatización debe vivir en
  `scripts/` y ser ejecutable sin interacción humana.
- **`terraform plan` antes de `apply`**: siempre verifica el diff antes
  de aplicar cambios.
- **`-parallelism=1 -target=`** para intervenciones acotadas:
  ```
  terraform apply -parallelism=1 -target=proxmox_virtual_environment_container.svc["<service>"]
  ```
- **Idempotencia**: una segunda aplicación sin cambios no debe recrear
  ni recargar servicios innecesariamente.

## Excepción: diagnóstico de lectura

Está permitido ejecutar comandos de **solo lectura** para diagnóstico:

- `pct exec <ct> -- cat /path/to/file` — leer archivos.
- `ssh -o StrictHostKeyChecking=yes -o UserKnownHostsFile=$HOME/.ssh/known_hosts -o BatchMode=yes <service> "cat /path/to/file"` — leer archivos.
- `pct exec <ct> -- uname -a` — verificar estado.

**Reglas del diagnóstico de lectura:**

1. Nunca modifiques nada.
2. Usa siempre SSH estricto: `StrictHostKeyChecking=yes`,
   `UserKnownHostsFile=$HOME/.ssh/known_hosts`, `BatchMode=yes`.
3. No almacenes outputs sensibles en logs o archivos temporales.
4. Si el diagnóstico revela un problema que requiere cambio, documenta
   el cambio necesario y propón el bloque Terraform correspondiente.

## Ejemplos

### Correcto: cambiar memoria de un CT

```bash
# 1. Editar el bloque en terraform/
# 2. Verificar el plan
terraform plan -target=proxmox_virtual_environment_container.svc["<service>"]
# 3. Aplicar
terraform apply -parallelism=1 -target=proxmox_virtual_environment_container.svc["<service>"]
```

### Incorrecto: cambiar memoria manualmente

```bash
# NUNCA:
pct set 624 -memory 8192
# O:
ssh CT624 "fallocate -l 8G /swapfile && swapon /swapfile"
```

### Correcto: diagnóstico de lectura

```bash
# Leer memoria usada en CT624:
pct exec 624 -- free -m
# Verificar configuración actual:
terraform state show proxmox_virtual_environment_container.svc["<service>"]
```

### Incorrecto: diagnóstico que modifica

```bash
# NUNCA:
pct exec 624 -- touch /tmp/.debug
pct exec 624 -- apt update && apt upgrade -y
```

## Verificación post-cambio

Después de cualquier `terraform apply`:

1. Verifica que el estado Terraform coincide con la intención:
   ```
   terraform plan -target=proxmox_virtual_environment_container.svc["<service>"]
   # Debe mostrar "No changes. Your infrastructure matches the configuration."
   ```
2. Verifica que el servicio funciona correctamente (API, healthcheck, etc.).
3. No asumas que un `terraform apply` sin errores significa que el servicio
   está funcionando.

## Relación con otras reglas

- `00-reasoning.md` §6 — principio IaC-only general.
- `18-lxc-docs-workflow-routing.md` — workflow de documentación aplica
  el plan guardado, validado y autorizado según el runbook.
- `16-lxc-swap-workflow-routing.md` — workflow de swap usa
  `terraform apply -target=`.
- `11-test-command-loop-prevention.md` — las pruebas validan la IaC
  antes de desplegar.
