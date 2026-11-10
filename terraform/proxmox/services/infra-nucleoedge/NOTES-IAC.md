# Notes de CT 614 — estado vigente D-047

Notes actualizadas mediante plan exclusivo description el 06/11/2026; comprobación
exacta y plan posterior sin cambios. Fuente: [NOTES.md](NOTES.md); ficha principal:
[614-LXC-INVENTORY](../../docs/inventory/614-LXC-INVENTORY.md).
[Evidencia D047](../../docs/roadmap/evidence/2026-11-06-d047-result.json).
No cambios de tags/recursos/apps/contenedores/Compose/Nginx; sin reinicios.

Los comandos y respaldos D046 siguientes son históricos y no deben sobrescribirse
ni aplicarse de nuevo por consultar esta guía. La ejecución D047 usa su propio
respaldo y plan privado en `~/.local/share/mailerblend-recovery/inventory-614-d047/`.
Para futuras Notes, crear un nuevo directorio privado y plan dirigido a CT614;
validar con `validate-lxc-notes-plan.py --service infra-nucleoedge` y exigir cambios
exclusivos description antes de cualquier aplicación autorizada.

## Historial D-046


**Aplicadas y verificadas el 06/11/2026.** Fuente exacta: [NOTES.md](NOTES.md).
La sección `documentation.notes_file` del inventario del servicio selecciona ese
archivo; el generador lo incorpora a Notes y al inventario Markdown. Terraform
renderiza mediante la plantilla común. Los hashes impiden aplicar datos obsoletos.

D-046 autoriza exclusivamente CT 614, incluida consulta del bloque Nginx de su
URL pública. Serving/Preview healthy, healthz local/público 200; configuración
Compose y dependencias verificadas sin publicar variables. Production y el dominio
principal fueron confirmados expresamente por el propietario.

## Procedimiento reproducible acotado

Desde `terraform/proxmox`:

```bash
python3 scripts/generate-lxc-inventory.py
python3 scripts/generate-lxc-inventory.py --check
terraform validate
umask 077
terraform plan -input=false -target='proxmox_virtual_environment_container.svc["infra-nucleoedge"]' -var-file=inventory/notes-614.tfvars.json -out="$HOME/.local/share/mailerblend-recovery/notes-614-d046/notes.tfplan"
terraform show -json "$HOME/.local/share/mailerblend-recovery/notes-614-d046/notes.tfplan" > "$HOME/.local/share/mailerblend-recovery/notes-614-d046/plan.json"
python3 scripts/validate-lxc-notes-plan.py "$HOME/.local/share/mailerblend-recovery/notes-614-d046/plan.json" --service infra-nucleoedge --report docs/roadmap/evidence/2026-11-06-d046-plan-review.json
```

Mantener directorio privado 0700 y archivos sensibles 0600. El var-file conserva
los tags reales de CT614, sin modificar inventario de recursos ni etiquetas.
El uso dirigido es una excepción explícita D046 al procedimiento global D045:
evita refrescar otros LXC, no elimina validaciones ni autoriza su modificación.
No aplicar un plan global ni el var-file propuesto para 17 CT.

Aplicar únicamente el plan revisado si todos sus cambios son `description` de
CT614 y coinciden con NOTES.md. En D046 fue 1 update, cero creación/destrucción,
sin tags; apply PASS y plan dirigido posterior con cero cambios. No repetir apply
por consultar esta documentación. La autorización no cubre nuevos cambios futuros.

## Evidencias y recuperación

- [Plan aprobado](../../docs/roadmap/evidence/2026-11-06-d046-plan-review.json).
- [Resultado y Notes exactas](../../docs/roadmap/evidence/2026-11-06-d046-result.json).
- [Observación inicial filtrada](../../docs/roadmap/evidence/2026-11-06-d046-614-before.json).
- Privados: `~/.local/share/mailerblend-recovery/notes-614-d046/`, con configuración
  inicial/final de CT614, copia del estado Terraform, plan y logs. No publicarlos.

Verificado: solo cambia description en configuración PVE completa de CT614;
boot ID, IDs/fechas de arranque/restarts/imágenes/entornos/HostConfig de todos sus
contenedores y hashes Compose idénticos. Estado Terraform de otros recursos
idéntico, sin consultarlos por API ni SSH. Nginx solo lectura. No cambios de tags,
CPU/RAM/disco/red, aplicaciones, contenedores, imágenes ni reinicios. Sin commit/push.

Para revertir Notes, recuperar únicamente la descripción anterior del respaldo,
representarla en IaC y volver a revisar un plan dirigido exclusivamente a description.
No restaurar el estado completo ni recrear el LXC por un cambio de notas.

La recuperación de sGTM y su prevención pendiente siguen en D043/D044 e Issue #1;
esta tarea no prueba entrega GA4 ni instala reinicios automáticos.
