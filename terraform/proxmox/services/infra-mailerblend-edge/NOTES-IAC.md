# CT615 — Notes mediante Terraform (D-049)

Fuente exacta: [NOTES.md](NOTES.md). Ficha principal:
[615-LXC-INVENTORY.md](../../docs/inventory/615-LXC-INVENTORY.md).
`documentation.notes_file` y `documentation.inventory_file` en el inventario del
servicio vinculan ambas fuentes. El generador alimenta plantilla Terraform y
índice Markdown; este último enlaza la ficha sin duplicarla.

## Aplicación realizada

06/11/2026: plan dirigido exclusivamente a
`proxmox_virtual_environment_container.svc["infra-mailerblend-edge"]`, usando
`inventory/notes-615.tfvars.json` para conservar exactamente sus tags observados.
Único cambio autorizado: `description`. No creación/destrucción/recreación, tags
ni otros atributos. Archivo de Notes comprobado directamente en Proxmox, seguido
por plan dirigido sin cambios. Las fuentes contienen solo información pública/no
sensible, nunca el valor de la configuración GTM.

[Evidencia del plan](../../docs/roadmap/evidence/2026-11-06-d049-plan-review.json),
[resultado](../../docs/roadmap/evidence/2026-11-06-d049-result.json).
Respaldos de configuración/estado, plan binario, JSON completo y logs privados:
`~/.local/share/mailerblend-recovery/inventory-615-d049/`. No publicarlos.

Verificado: configuración completa de CT615 salvo description, tags, boot ID,
IDs/StartedAt/restarts/imágenes/env/HostConfig de sus contenedores y hashes de
Compose/Nginx sin cambios. Estado Terraform de otros recursos idéntico. D049 no
reinició ni recreó ningún contenedor. No se envió evento GA4 ni se modificaron
aplicaciones, Nginx, DNS o certificados. Sin commit/push.

## Actualizaciones futuras (requieren autorización correspondiente)

Desde `terraform/proxmox`, editar las fuentes y generar; no sobrescribir a mano
la descripción de Proxmox ni los JSON generados. Crear un directorio privado
**nuevo**, conservar evidencias y revisar tags antes de usar el var-file.

```bash
python3 scripts/generate-lxc-inventory.py
python3 scripts/generate-lxc-inventory.py --check
terraform validate
# Directorio nuevo con permisos 0700; archivos privados mediante umask077.
umask 077
task_notes_dir="$HOME/.local/share/mailerblend-recovery/notes-615-next-review"
mkdir -m 700 "$task_notes_dir"
terraform plan -input=false -target='proxmox_virtual_environment_container.svc["infra-mailerblend-edge"]' -var-file=inventory/notes-615.tfvars.json -out="$task_notes_dir/notes.tfplan"
terraform show -json "$task_notes_dir/notes.tfplan" > "$task_notes_dir/plan.json"
python3 scripts/validate-lxc-notes-plan.py "$task_notes_dir/plan.json" --service infra-mailerblend-edge --report "$task_notes_dir/review.json"
```

El plan dirigido cumple el alcance exclusivo, sin refrescar otros LXC por API.
No aplicar si aparece otra propiedad/recurso ni usar el var-file de CT614 por error.
Aplicar solo el plan guardado revisado cuando esté autorizado y verificar estado
posterior. No repetir apply para consultar esta guía. No usar deploy-all.

Para revertir Notes, recuperar únicamente la descripción previa del respaldo,
representarla en IaC y revisar un nuevo plan exclusivo; no restaurar todo el estado
Terraform ni recrear el LXC por documentación. La recuperación de aplicación es
otro procedimiento: [D048](../../docs/roadmap/CT615-SGTM-D048-RECOVERY.md).
