# CT633 · infra-knowledge

Estado PENDING VERIFICATION. Outline con PostgreSQL y Redis dedicados.

Debian 12 sin privilegios, 2 vCPU, 3072 MiB RAM, 512 MiB swap y 30 GiB en local-lvm. Red vmbr0 con DHCP. IP, DNS y TLS pendientes de validación.

Outline + PostgreSQL + Redis se declara en [Docker Compose](../../services/infra-knowledge/compose/docker-compose.yml). Acceso previsto por 3000/tcp mediante proxy HTTPS. Dependencias: OIDC, CT109, CT632 SMTP opcional.

Para alta, monitorización y rollback, seguir el [runbook de alta](../runbooks/NEW-LXC-PROVISIONING.md). Backup PVE y restauración pendientes de prueba. Conservar los volúmenes al revertir una versión de Compose.
