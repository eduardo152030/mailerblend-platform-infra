# Workflow — Aumento de swap de un LXC

Antes de modificar archivos, aplica la [regla 03](../03-git-workflow.md)
para identificar el plan o issue y preparar el worktree dedicado.

Orquesta el runbook `docs/runbooks/LXC-SWAP-INCREASE.md`. No duplicar sus
pasos; referenciarlos.

## Disparadores

- "aumentar swap de <service>", "subir swap CT<id>"
- "swap alert <service>", "alerta de swap <service>"
- "aumentar swap", "swap increase"

Si falta `<service>`/`<CT>` o el objetivo es ambiguo, **preguntar antes de
ejecutar**.

## Pasos

1. **Aceptar CTID/servicio.** Resolver el servicio por vmid (o viceversa) en
   `inventory/services/`. Si no existe, detener.

2. **Diagnóstico (solo lectura).** Seguir runbook §3:
   - `grep -rn "vmid: <CT>" inventory/services/`
   - leer `resources` del `.yml` (RAM y swap actuales)
   - `pct config <CT> | grep -Ei 'memory|swap'` (SSH estricto)
   - si está activo: `pct exec <CT> -- free -m`
   - registrar fecha (Europe/Madrid) y valores como evidencia.

3. **Calcular siguiente paso.** Ejecutar:

   ```bash
   python3 scripts/next-swap-step.py --service <service>
   ```

   - `OK` → continuar con el peldaño `siguiente`.
   - `AT_MAX` / `BLOCKED` → **detener** y reportar el motivo. No proponer aumento.

4. **Editar inventario.** Cambiar **solo** `resources.swap` en
   `inventory/services/<service>.yml` al nuevo peldaño. No tocar nada más.

5. **Plan acotado.** `terraform plan -out=tfplan-swap-<CT>`.
   - El plan debe mostrar **únicamente** el cambio de `swap` del CT objetivo
     (y, si procede, su `description`).
   - Cualquier otro cambio → **STOP**: reportar y pedir confirmación explícita.

6. **Confirmación del usuario.** **STOP obligatorio** antes de `apply`:
   confirmación explícita del propietario para ese CT y ese valor.

7. **Aplicar (solo tras confirmación):**

   ```bash
   terraform apply -parallelism=1 -target=proxmox_virtual_environment_container.svc["<service>"] tfplan-swap-<CT>
   ```

8. **Verificar.** Runbook §8:
   - `pct config <CT> | grep -Ei 'swap'` → coincide con el nuevo peldaño.
   - si está activo: `pct exec <CT> -- free -m`.
   - idempotencia: segundo `terraform plan` sin cambios.

9. **Cerrar documental.** Runbook §10: actualizar ficha
   `docs/inventory/<CT>-LXC-INVENTORY.md`, `DECISIONS.md` y `CURRENT-STATUS.md`.

## Reglas de seguridad

- SSH estricto: `UserKnownHostsFile=$HOME/.ssh/known_hosts`,
  `StrictHostKeyChecking=yes`, `BatchMode=yes`.
- Solo `apply -parallelism=1 -target=proxmox_virtual_environment_container.svc["<service>"]`.
  Nunca `apply` general ni `make deploy-all`.
- El swap se aplica en caliente; no reiniciar el CT.
- El cierre Git sigue las reglas 03 y 06, dentro del alcance autorizado.
- Ante cualquier anomalía o cambio no esperado en el plan, **detener** y
  reportar; no avanzar.
