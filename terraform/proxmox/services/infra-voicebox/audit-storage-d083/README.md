# D083 — auditoría de almacenamiento, solo lectura

Prioridad vigente: [rootfs50→100GiB enSSD](../../../docs/roadmap/PHASE7-D083-CT627-SSD-CAPACITY-AUDIT.md).
No se autoriza resize, crear discos, mover modelos oDocker, descargar, limpiar,
reiniciar ni hacer commit/push. La producción D081 sigue conrootfs50GiB.

- `inspect-ct.py`: ejecutar mediantepctexec627; solo metadatos,du/df yDockerinspect
  filtrado. No imprime entornos generales nicontenido de grabaciones.
- `inspect-ssd.py`: lectura enPVE de pool/LVM/ext4/snapshots, sinresize/trim/fsck.
- `mp0.proposed.hcl`: propuestaHDD histórica SUPERSEDED; no copiar a main.tf.

Los planes fueron simulados enunmódulo privado separado, sinrefresh remoto niapply.
No se publicó tfstate, tfvars oplanesbinarios. Actualizar elinventario activo a100
antes deuna aprobación falsearía elestado real: no se hizo.
