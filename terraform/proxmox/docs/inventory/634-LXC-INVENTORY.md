# CT634 · infra-diagrams

Estado PENDING VERIFICATION. Editor privado de diagramas para Outline.

Debian 12 sin privilegios, 1 vCPU, 1536 MiB RAM, 512 MiB swap y 12 GiB en local-lvm. Red vmbr0 con DHCP. IP, DNS y TLS pendientes de validación.

Draw.io se declara en [Docker Compose](../../services/infra-diagrams/compose/docker-compose.yml). Acceso previsto por 8080/tcp mediante proxy HTTPS. Dependencias: CT109, Navegador de Outline.

Para alta, monitorización y rollback, seguir el [runbook de alta](../runbooks/NEW-LXC-PROVISIONING.md). Backup PVE y restauración pendientes de prueba. Conservar los volúmenes al revertir una versión de Compose.
