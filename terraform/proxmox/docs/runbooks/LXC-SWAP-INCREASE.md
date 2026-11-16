# Runbook — Aumento de swap de un LXC

Procedimiento estándar, reproducible y acotado para subir el swap de un único
CT mediante IaC (Terraform + inventario YAML). Basado en el caso de referencia
`30d90a4a` (CT 631 / `infra-webui`, 1024 → 1741 MiB).

> **Regla de oro:** el `terraform plan` debe mostrar **únicamente** el cambio de
> `swap` del CT objetivo (y, si procede, su `description`/notes). Cualquier otro
> cambio en el plan exige confirmación explícita del usuario antes de aplicar.

## 1. Alcance y precondiciones

- Afecta a **un solo** CT. No usar `make deploy-all` ni `apply` general.
- El swap se define en `inventory/services/<service>.yml` bajo `resources.swap`
  (MiB) y lo consume `main.tf` en el bloque `memory { swap = ... }`.
- El swap de un LXC se aplica **en caliente**: no requiere reiniciar el CT.
- Precondiciones:
  - `terraform init` ya ejecutado (`.terraform` presente).
  - Acceso SSH al PVE con configuración estricta
    (`UserKnownHostsFile=$HOME/.ssh/known_hosts`, `StrictHostKeyChecking=yes`,
    `BatchMode=yes`) para el diagnóstico de solo lectura.
  - Autorización explícita del propietario para ese CT y ese cambio.

## 2. Escalera de swap

Peldaños canónicos en MiB (regla `N GiB → N GiB + 717 MiB → (N+1) GiB`):

```
512, 1229, 1024, 1741, 2048, 2765, 3072, 3789, 4096
```

El valor "medio" de cada par es 717 MiB por encima del GiB inferior
(1024 + 717 = 1741), punto medio redondeado hacia arriba (1536 → 1741).

**Tope de seguridad (fail closed):** el nuevo swap no puede superar
`min(2 × RAM, 4096 MiB)`. Si el siguiente peldaño lo supera, el proceso se
detiene y se explica el motivo (revisar RAM o solicitar excepción explícita).

## 3. Diagnóstico (solo lectura)

1. Identificar el servicio por vmid (o el vmid por servicio):

   ```bash
   grep -rn "vmid: <CT>" inventory/services/
   ```

2. Leer el bloque `resources` del `.yml` (RAM y swap actuales):

   ```bash
   sed -n '/^resources:/,/^[a-z]/p' inventory/services/<service>.yml
   ```

3. Confirmar el estado real en el PVE (SSH estricto, solo lectura):

   ```bash
   pct config <CT> | grep -Ei 'memory|swap'
   ```

   y, si el CT está activo, el uso real:

   ```bash
   pct exec <CT> -- free -m
   ```

   Registrar fecha/hora (Europe/Madrid) y valores observados como evidencia.

## 4. Cálculo del siguiente paso

Usar el helper (solo lectura, no modifica nada):

```bash
python3 scripts/next-swap-step.py --service <service>
# o por vmid:
python3 scripts/next-swap-step.py --ct <CT>
# salida máquina:
python3 scripts/next-swap-step.py --service <service> --json
```

El script devuelve `estado` (`OK` / `AT_MAX` / `BLOCKED`) y el `siguiente`
peldaño. Si `BLOCKED` o `AT_MAX`, **detener** y reportar el motivo.

## 5. Edición del inventario

Editar **solo** el campo `swap` en `inventory/services/<service>.yml`:

```yaml
resources:
  memory: 4096
  swap: 2048        # <-- único cambio (antes: 1741)
```

No tocar `memory`, `cores`, `disk`, `network` ni ninguna otra sección.

## 6. Plan acotado y validación

```bash
terraform plan -out=tfplan-swap-<CT>
```

Revisar el plan: debe contener **un único** `# proxmox_virtual_environment_container.svc["<service>"]`
con `~ swap = "1741" -> "2048"` (o el par correspondiente). Si aparece cualquier
otro recurso o campo:

- **Detener.** No aplicar.
- Reportar al usuario los cambios extra y pedir confirmación explícita.

## 7. Aplicación (requiere confirmación del usuario)

Solo tras confirmación explícita del propietario:

```bash
terraform apply -parallelism=1 -target=proxmox_virtual_environment_container.svc["<service>"] tfplan-swap-<CT>
```

- `-parallelism=1` y `-target` acotan la operación al CT objetivo.
- No usar `make deploy-all`.

## 8. Verificación post-aplicación

1. Confirmar en el PVE (solo lectura):

   ```bash
   pct config <CT> | grep -Ei 'swap'
   ```

   El valor debe coincidir con el nuevo peldaño.

2. Si el CT está activo, comprobar que el swap está disponible en caliente:

   ```bash
   pct exec <CT> -- free -m
   ```

3. Idempotencia: una segunda `terraform plan` sin cambios debe mostrar
   `No changes` para ese CT (no debe recrear ni recargar nada).

## 9. Rollback

Para revertir, restaurar el valor anterior de `swap` en el `.yml` y repetir
los pasos 6–8. El swap se aplica en caliente, por lo que el rollback no
requiere reinicio. Conservar el valor original como evidencia antes de aplicar.

## 10. Cierre documental

- Actualizar la ficha `docs/inventory/<CT>-LXC-INVENTORY.md` (línea de swap).
- Registrar la decisión en `docs/roadmap/DECISIONS.md` y el estado en
  `docs/roadmap/CURRENT-STATUS.md` (fecha Europe/Madrid, evidencia fechada).
- No hacer commit/push salvo autorización explícita; revisar `git diff --check`.

## 11. Checklist de seguridad

- [ ] Plan muestra solo el cambio de `swap` del CT objetivo.
- [ ] Confirmación explícita del propietario antes de `apply`.
- [ ] `apply` acotado con `-target` y `-parallelism=1`.
- [ ] Verificación post-apply con `pct config` (solo lectura).
- [ ] Idempotencia: segundo `plan` sin cambios.
- [ ] Valor original registrado para rollback.
- [ ] Ficha y roadmap actualizados.
