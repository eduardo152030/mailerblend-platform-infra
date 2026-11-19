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
     **ACTUALIZAR** si existe. Para CT611, la clave es `infra-grafana`.
     Comprueba los datos reales mediante §3 paso 2 del runbook.
   - Usa SSH estricto desde el primer intento. Ejecuta `pct status` y
     `pct config` en el nodo PVE. Usa el alias directo del CT para lecturas
     internas si su clave está verificada. Si falla la verificación del alias,
     usa `pct exec <VMID> -- ...` desde PVE verificado. Para CT611 el alias
     directo es `infra-grafana` y la ruta verificada es `pve` → `pct exec 611`.
     Si falla también la verificación de PVE, detén las lecturas remotas.
3. Actualiza la ficha, las Notes y sus referencias `notes_file` e
   `inventory_file` en el YAML. Documenta las etiquetas observadas en la
   ficha. Conserva las etiquetas existentes al alinear el YAML con la lectura
   verificada del CT. Para CT611, incluye `192.168.1.111`.
4. Si el encargo dice «solo documentación», completa el
   [cierre documental](../../docs/runbooks/LXC-DOCUMENTATION-PROCESS.md#cierre-documental)
   y termina. En los demás casos, sigue §6 del runbook para sincronizar
   automáticamente las Notes del CT identificado.
5. Ejecuta una vez el script de §6.1 para ese servicio. Si el informe
   devuelve `BLOCKED` o falla alguna comprobación, reporta la causa y
   termina. Con `PASS` y cambios, aplica el binario guardado según §6.2
   sin pedir confirmación adicional. Con `PASS` sin cambios, verifica la
   nota real y cierra. Tras aplicar, verifica PVE y exige un plan posterior
   sin cambios. Reutiliza el informe disponible para el mismo plan.
