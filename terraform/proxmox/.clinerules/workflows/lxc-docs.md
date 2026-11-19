# Documentar un LXC

Antes de modificar archivos, aplica la [regla 03](../03-git-workflow.md)
para identificar el plan o issue y preparar el worktree dedicado.

Disparadores: «documentar CT<VMID>» (por ejemplo, «documentar CT611»), «documentar <service>»,
«crear ficha de <service>», «actualizar la ficha de <service>» y
«sincronizar Notes de <service>».

1. Trabaja desde el directorio que contiene `inventory/services/` e
   `inventory.tf`. Si ambos ya están en el directorio actual, úsalo. Si
   abriste la raíz del repositorio, entra en `terraform/proxmox`. Lee las
   instrucciones y el [runbook](../../docs/runbooks/LXC-DOCUMENTATION-PROCESS.md).
2. Resuelve la identidad **solo en los YAML de `inventory/services/`**.

   - Si la petición trae un VMID, extrae los dígitos después de `CT` y
     busca el campo `vmid` completo. Para «documentar CT611», ejecuta:

     ```bash
     vmid=611  # Sustituye por el VMID solicitado
     rg -n "^[[:space:]]*vmid:[[:space:]]*${vmid}[[:space:]]*(#.*)?$" inventory/services/*.yml
     ```

     Resultado esperado: `inventory/services/infra-grafana.yml:3:  vmid: 611`.
     Si `rg` no está disponible, usa `grep -En` con el mismo patrón y los
     mismos archivos.
   - Si la petición trae una clave de servicio, abre directamente
     `inventory/services/<service>.yml` y lee su `service.vmid`.
   - Con una única coincidencia, lee ese YAML y confirma `service.vmid`,
     `service.name` e IP. La clave del servicio es el nombre del archivo
     sin `.yml`. Con cero o varias coincidencias, o si falla el comando,
     detente e informa. Evita búsquedas recursivas y consultas al estado
     Terraform, a `.runtime` o a los inventarios generados para resolver el CT.
   - Usa **CREAR** si falta `docs/inventory/<CT>-LXC-INVENTORY.md`, o
     **ACTUALIZAR** si existe. Para CT611, la clave es `infra-grafana` y
     corresponde **CREAR** al 19/11/2026. Comprueba los datos reales
     mediante §3 paso 2 del runbook.
   - Usa SSH estricto desde el primer intento. Ejecuta `pct status` y
     `pct config` en el nodo PVE. Usa el alias directo del CT para lecturas
     internas si su clave está verificada. Si falla la verificación del alias,
     usa `pct exec <VMID> -- ...` desde PVE verificado. Para CT611 el alias
     directo es `infra-grafana` y la ruta verificada es `pve` → `pct exec 611`.
     Si falla también la verificación de PVE, detén las lecturas remotas.
3. Actualiza la ficha y las Notes a partir de lo observado. En el YAML,
   enlázalas con `notes_file` e `inventory_file`. Para «sincronizar Notes»,
   reutiliza las fuentes si están vigentes. Si retomas CT611 con la ficha y
   las Notes ya preparadas, preserva esos borradores y continúa en §6.1.
   Para preparar el plan, ejecuta una sola llamada a
   `bash scripts/prepare-lxc-notes-plan.sh infra-grafana` (sustituye la clave
   para otros CT). Usa el script versionado tal cual, sin reconstruir su
   bloque de comandos, encadenar reintentos ni borrar el directorio privado.
4. Si hay un fallo o drift ajeno a `description`, informa del bloqueo y
   detén la aplicación. Con un plan sin cambios, verifica la nota real.
   Con un cambio validado, muestra el informe seguro y espera la confirmación
   explícita para aplicar el plan guardado según §6.2.
5. Verifica la descripción completa en PVE y comprueba con un segundo
   plan que repetir el proceso produciría cero cambios. Registra por separado ficha, artefactos,
   plan, aplicación y verificación. Sigue el cierre del runbook y comunica
   fase, estado y siguiente paso.
