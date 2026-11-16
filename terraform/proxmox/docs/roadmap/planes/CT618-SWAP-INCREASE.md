# CT618 Swap Increase — Plan de Implementación

**Servicio**: infra-composable-crm
**VMID**: 618
**Fecha**: 2026-11-16
**Estado**: Preparado — pendiente ejecución
**Autorización**: Pendiente

---

## 1. Contexto

El contenedor CT618 (infra-composable-crm) tiene 6144 MiB de RAM y utiliza el
valor por defecto de swap (512 MiB) porque el inventario **no declara** el campo
`swap` en el bloque `resources`. El bloque `memory` de `main.tf` aplica este
default:

```hcl
memory {
    dedicated = each.value.memory
    swap      = try(local.services_raw[each.key].resources.swap, 512)
}
```

El swap efectivo actual es **512 MiB** (valor por defecto de Terraform), no un
valor explícito. Esto debe verificarse en el nodo antes de implementar.

## 2. Análisis de la escalera

La escalera de swap definida en `scripts/next-swap-step.py` es:

```
LADDER = [512, 1229, 1024, 1741, 2048, 2765, 3072, 3789, 4096]
```

El orden es: **512 → 1229 → 1024 → 1741 → 2048 → 2765 → 3072 → 3789 → 4096**.

El valor 1229 MiB es el **siguiente peldaño** tras 512 MiB (índice 0 → índice 1).
Aunque 1229 > 1024, este es el diseño canónico de la escalera: cada peldaño N GiB
se eleva a N GiB + 717 MiB antes de saltar al siguiente GiB completo.

**Tope de seguridad**: `min(2 × 6144, 4096) = 4096 MiB`.
1229 MiB está dentro del tope → **aprobado**.

## 3. Cambio propuesto

### YAML actual (`inventory/services/infra-composable-crm.yml`)

```yaml
service:
  name: infra-composable-crm
  vmid: 618
  ip: 192.168.1.118/24

resources:
  cpu: 2
  memory: 6144
  disk_gb: 50

tags:
  - internal
  - crm
  - composable
  - Parte_LinkedIn_Stealth_Sourcing
  - supabase_postgresql
  - budibase_crm_ui
```

### YAML propuesto

```yaml
service:
  name: infra-composable-crm
  vmid: 618
  ip: 192.168.1.118/24

resources:
  cpu: 2
  memory: 6144
  swap: 1229
  disk_gb: 50

tags:
  - internal
  - crm
  - composable
  - Parte_LinkedIn_Stealth_Sourcing
  - supabase_postgresql
  - budibase_crm_ui
```

**Cambio único**: añadir `swap: 1229` bajo `resources:`.
No se modifican `cpu`, `memory`, `disk_gb` ni ningún otro campo.

## 4. Pasos de implementación

### Paso 1 — Verificación previa en el nodo (solo lectura)

```bash
pct exec 618 -- free -m
```

Confirmar que el swap actual es ~512 MiB. Si es diferente, documentar la discrepancia.

### Paso 2 — Editar inventario

Añadir `swap: 1229` en `inventory/services/infra-composable-crm.yml` bajo
`resources:`.

### Paso 3 — Terraform Plan

```bash
terraform plan -parallelism=1 -target=proxmox_virtual_environment_container.svc["infra-composable-crm"]
```

**Criterios de revisión del resultado**:
- El plan debe mostrar **exactamente un recurso** a modificar:
  `proxmox_virtual_environment_container.svc["infra-composable-crm"]`.
- El diff debe mostrar el cambio de `memory.0.swap` de `512` a `1229`.
- **No debe haber** cambios en otros recursos, recargas de VM, ni recreaciones.
- El plan debe terminar sin errores.

Si el plan muestra cambios no esperados, **detener** y revisar antes de continuar.

### Paso 4 — Confirmación del propietario

**STOP OBLIGATORIO** antes de `terraform apply`. Solicitar autorización explícita
al propietario con el diff del plan.

### Paso 5 — Terraform Apply (tras autorización)

```bash
terraform apply -parallelism=1 -target=proxmox_virtual_environment_container.svc["infra-composable-crm"]
```

### Paso 6 — Verificación post-cambio (solo lectura)

```bash
pct exec 618 -- free -m
```

Confirmar que el swap es ahora ~1229 MiB.

### Paso 7 — Validación de idempotencia

```bash
terraform plan -parallelism=1 -target=proxmox_virtual_environment_container.svc["infra-composable-crm"]
```

Debe mostrar: `No changes. Your infrastructure matches the configuration.`

## 5. Rollback

Si algo falla durante la aplicación:

```bash
# Revertir el YAML al estado anterior (sin swap: 1229)
# Luego aplicar:
terraform apply -parallelism=1 -target=proxmox_virtual_environment_container.svc["infra-composable-crm"]
```

El swap se puede reducir en caliente sin reiniciar el CT.

## 6. Efectos secundarios a verificar

- **Reinicio del CT**: No se requiere. El swap se aplica en caliente.
- **Otros recursos**: No se modifican. El `-target` acota el alcance exclusivamente
  a CT618.
- **Servicios en ejecución**: No se recargan ni reinician.
- **Prometheus/monitoring**: No se modifican reglas ni targets.
- **Backups**: Se recomienda verificar que el backup más reciente de CT618 es
  funcional antes de aplicar.

## 7. Criterios de éxito

1. `inventory/services/infra-composable-crm.yml` incluye `swap: 1229`.
2. `terraform plan` muestra solo el cambio de swap de 512 a 1229.
3. `terraform apply` completa sin errores.
4. `pct exec 618 -- free -m` muestra swap ~1229 MiB.
5. Segunda aplicación sin cambios: `terraform plan` reporta "no changes".
6. El servicio infra-composable-crm sigue operativo (healthcheck/API).
