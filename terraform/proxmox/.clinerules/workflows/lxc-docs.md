# Workflow: documentar un LXC (ficha + Notes)

Orquesta `docs/runbooks/LXC-DOCUMENTATION-PROCESS.md`. **No duplica sus
pasos**: los referencia por sección. La fuente de verdad de cada comando son
`scripts/` e `inventory/`; si el runbook y el código discrepan, gana el código.

## Disparadores

- "documentar CT<id>", "crear ficha de <service>", "actualizar la ficha de
  <service>", "sincronizar Notes de <service>", "documentar <service>".

## Entrada mínima

- `<service>` (nombre del archivo del inventario sin extensión, p. ej.
  `infra-pulpo`) o `<CT>` (vmid, p. ej. 619).
- Modo: **CREAR** (no existe `docs/inventory/<CT>-LXC-INVENTORY.md`) o
  **ACTUALIZAR** (ya existe).

Si falta `<service>`/`<CT>` o el modo es ambiguo, preguntar antes de
ejecutar. No adivinar.

## Flujo

1. **Leer el runbook** `docs/runbooks/LXC-DOCUMENTATION-PROCESS.md`
   (secciones 1 y 2 siempre; 3 si CREAR, 4 si ACTUALIZAR).
2. **Confirmar identidad** desde `inventory/services/<service>.yml`
   (`service.vmid`, `service.name`, `service.ip`). Si el CT no está
   declarado, detener: este flujo no da de alta CTs (ver
   `NEW-LXC-PROVISIONING.md`).
3. **Ejecutar los pasos del modo** correspondiente del runbook:
   - CREAR → §3 pasos 1–13.
   - ACTUALIZAR → §4 pasos 1–7.
4. **Regenerar siempre antes de planear** (runbook §3 paso 6 / §4 paso 3):
   `python3 scripts/generate-lxc-inventory.py` y `--check`.
5. **Plan acotado** (runbook §3 paso 8 / §4 paso 4):
   `terraform plan -parallelism=1 -target=proxmox_virtual_environment_container.svc["<service>"]`.
6. **Validar que el plan es solo `description`** (runbook §3 paso 9 / §4 paso 4):
   `python3 scripts/validate-lxc-notes-plan.py <plan> --report <report> --service <service>`.
   - `PASS` → continuar.
   - `BLOCKED` → **PARAR** (regla de seguridad §2.4). Diagnosticar con
     `report.json` (drift de `tags` → runbook §5.1). No aplicar.

## STOP obligatorio (no saltar)

- **Antes de `terraform apply`** (runbook §3 paso 10 / §4 paso 5): mostrar el
  diff del plan y **pedir confirmación explícita del usuario**. Sin
  confirmación, no aplicar.
- **Ante cualquier `BLOCKED`** o precondition fallido: detener y reportar.
- **Ante un plan que no sea solo `description`**: detener (regla §2.4).

## Reglas de seguridad (duplican runbook §2, no las sustituyen)

- SSH al CT **solo lectura** (`pct status/config`, `docker ps/inspect`,
  `cat`, `df`, `free`). Nunca `pct start/stop/restart/destroy`, `docker down
  -v`, `prune`, `rm`, ni escritura de configuración.
- SSH estricto: `UserKnownHostsFile=$HOME/.ssh/known_hosts`,
  `StrictHostKeyChecking=yes`, `BatchMode=yes`.
- **Nunca** `terraform apply` general ni `make apply`/`make deploy-all`.
  Solo `apply -parallelism=1 -target=proxmox_virtual_environment_container.svc["<service>"]`.
- No editar artefactos generados a mano (`lxc-notes.json`,
  `lxc-notes-manifest.json`, `LXC-INVENTORY.md`).
- Sin secretos en fuentes (el generador falla en cerrado).
- No tocar volúmenes, imágenes ni backups.

## Verificación final (siempre)

- `terraform apply` solo si el usuario confirmó y el plan era solo
  `description`.
- SSH solo lectura: confirmar que la `description` del CT coincide con
  `NOTES.md` y que no cambió nada más (runbook §3 paso 12).
- `git diff --check`; revisar que el diff solo toca las fuentes + artefactos
  generados.
- Actualizar `docs/roadmap/CURRENT-STATUS.md` (estado, evidencia, fecha
  Europe/Madrid). Registrar decisión en `DECISIONS.md` si aplica.
- **No** commit/push salvo autorización explícita.

## Salida al usuario

Resumen: modo (CREAR/ACTUALIZAR), CT/service, fuentes editadas, resultado del
plan (solo `description`), validación (`PASS`), apply (sí/no + confirmación),
verificación en producción, y siguiente paso. Indicar fase actual y siguiente
paso según el roadmap.
