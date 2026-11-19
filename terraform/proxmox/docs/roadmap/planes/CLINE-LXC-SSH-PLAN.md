# Publicación del procedimiento SSH de Cline para LXC

Versión inicial. 19/11/2026, Europe/Madrid. Fase 7.

- Rama `docs/cline-lxc-ssh`, base `origin/main` en `d19b72b7`.
- Alcance autorizado: publicar el workflow, el runbook y el seguimiento de
  la corrección de acceso SSH observada al documentar CT611.
- Criterios: distinguir comandos del nodo y del CT, mantener SSH estricto,
  usar PVE verificado si falla el alias directo y entregar PR hacia `main`.
- Evidencia previa: alias directo de CT611 devolvió 255 por clave ausente.
  `pct status/config` y `pct exec 611` por PVE con SSH estricto dieron PASS.
- Validaciones de publicación: diff, enlace al runbook, sintaxis Bash de los
  ejemplos de lectura, frescura y pruebas de inventario.
- Siguiente paso: revisión independiente del PR. CT611 permanece sin plan
  Terraform ni aplicación en esta intervención.

Validaciones de publicación ejecutadas: PASS en todos los casos.
