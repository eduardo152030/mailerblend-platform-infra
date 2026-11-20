# CT635 · infra-modeling

Estado PENDING VERIFICATION. Render privado de diagramas PlantUML.

Debian 12 sin privilegios, 1 vCPU, 2048 MiB RAM, 512 MiB swap y 12 GiB en local-lvm. Red vmbr0 con DHCP. IP, DNS y TLS pendientes de validación.

PlantUML Server se declara en [Docker Compose](../../services/infra-modeling/compose/docker-compose.yml). Acceso previsto por 8080/tcp en red privada. Dependencias: Cliente de publicación en Outline.

Para alta, monitorización y rollback, seguir el [runbook de alta](../runbooks/NEW-LXC-PROVISIONING.md). Backup PVE y restauración pendientes de prueba. Conservar los volúmenes al revertir una versión de Compose.
