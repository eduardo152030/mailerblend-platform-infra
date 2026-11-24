# CT 636 — infra-eva-ui

Estado: **PENDING VERIFICATION**. Declaración preparada, no despliegue ni aceptación.

**Purpose**
UI web de EVA con API y datos en CT622
Deployment: PENDING VERIFICATION — declared only, no live observation.

**Environment**
internal; owner: eduardo152030

**Network**
CT 636; DHCP; gateway 192.168.1.254; DNS 192.168.1.254; bridge vmbr0. Domains: infra-eva-ui.mailerblend.com

**Applications**
EVA UI (docker): 8080/tcp mediante proxy HTTPS
All application health: PENDING VERIFICATION

**Dependencies**
CT109; CT618; CT622; CT632

**Monitoring**
Node Exporter 1.10.2 native systemd; CPU cgroup v2 textfile (native CPU collector disabled), RAM LXCFS/root disk. cAdvisor 0.60.6 planned; exact socket/namespace approval required.
Uptime: existing PVE exporter; dashboards join published inventory. Endpoints: PENDING VERIFICATION
All deployed monitoring/functional status: PENDING VERIFICATION

**Infrastructure as Code**
inventory/services/infra-eva-ui.yml; Terraform resource svc["infra-eva-ui"]; 1 CPU / 1024 MiB / 12 GiB; template local:vztmpl/debian-12-standard_12.12-1_amd64.tar.zst (Debian 12); storage local-lvm.

**Documentation**
docs/inventory/636-LXC-INVENTORY.md; docs/runbooks/NEW-LXC-PROVISIONING.md

**Known Issues**
Pendientes validación de nodo y recursos, DHCP y contratos de autenticación y correo.
Backup/recovery: PENDING VERIFICATION: política PVE y restauración aislada

## Arquitectura y operaciones

Aplicaciones y dependencias corresponden a declaraciones anteriores, no a procesos
observados. Validar plantilla/SO/LXCFS/cgroup, puertos, acceso y contrato funcional
antes de integrar monitorización. No aplicar el ejemplo ni usar deploy-all.
Operación: docs/runbooks/NEW-LXC-PROVISIONING.md. Sin reinicios automáticos de apps.
Rollback de alta: retirar primero discovery del CT nuevo, detener solo sus nuevos
exporters y conservar CT/volúmenes/datos para diagnóstico; no destroy automático.
Restauración/RPO/RTO/retención: PENDING VERIFICATION; no se afirma backup realizado.
Limitaciones: ejecución real, permisos/namespaces, origen de métricas y cadena de
alertas requieren primer ensayo autorizado y evidencia fechada.
