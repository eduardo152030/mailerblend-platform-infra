# CT633–635 — Plataforma interna de conocimiento y diagramas

**Propuesto · Fase 7. IaC Reliability, Security & Disaster Recovery · 20/11/2026 (Europe/Madrid).**
Ronda `implementation`, inicio `6be70af601ff0775b19765dcecba590de73a8c15`,
base `origin/main`, rama `feat/knowledge-platform`, worktree
`../mailerblend-platform-infra-knowledge` relativo al checkout principal.
PR de revisión pendiente de apertura.

## Alcance y descubrimiento

Tres altas nuevas siguiendo el [runbook de alta](../../runbooks/NEW-LXC-PROVISIONING.md).
El nodo `pve` verificado por SSH estricto devolvió los tres VMID como disponibles
mediante `/cluster/nextid`. Tampoco están declarados en `inventory/services/`.
Repetir la comprobación antes de aplicar. CT101 (Docmost) y CT107 (Draw.io
existente) están activos y quedan fuera de los cambios. CT109 aloja el proxy
existente. No hay migración de datos.

Lectura del 20/11/2026, 23:38 CET: 4 CPU lógicas, carga a 15 min 1,25,
22 815 MiB de RAM disponible y 6 163 MiB de swap ocupada. `local-lvm` tenía
139 826 186 KiB disponibles, cerca de 133 GiB. Los valores son una muestra del
nodo, no una reserva ni una prueba de margen sostenido.

| VMID | Servicio | vCPU | RAM MiB | Swap MiB | Disco GiB | Justificación inicial |
|---|---|---:|---:|---:|---:|---|
| 633 | infra-knowledge | 2 | 3072 | 512 | 30 | Outline más PostgreSQL y Redis dedicados. CT101 ocupa unos 6 GiB, con 1 GiB RAM y 503 MiB swap en la muestra. Dejar margen para Docker, adjuntos, base y crecimiento. |
| 634 | infra-diagrams | 1 | 1536 | 512 | 12 | CT107 utilizaba unos 4,5 GiB de disco y 390 MiB de swap con 1080 MiB asignados. La edición corre en el navegador y el servidor arranca Tomcat. |
| 635 | infra-modeling | 1 | 2048 | 512 | 12 | Jetty y Graphviz en la imagen oficial. Proponer límite inicial de 1 GiB al contenedor de render y verificar con diagramas representativos y concurrencia acotada. |

Total propuesto 4 vCPU, 6,5 GiB RAM y 54 GiB de disco. Como el nodo tiene cuatro
CPU lógicas y swap ya ocupada, verificar CPU, PSI, swap, memoria disponible y
thin pool antes de cada alta y durante la observación. Confirmar margen de
almacenamiento también para backups y crecimiento.

Debian 12 `local:vztmpl/debian-12-standard_12.12-1_amd64.tar.zst` presente
en PVE, `local-lvm`, LXC sin privilegios, `vmbr0`, gateway y DNS
`192.168.1.254`. Proponer DHCP con MAC declarada como en CT631/632. IP,
reservas y nombres HTTPS pendientes de confirmar con el propietario y el
router. PlantUML se consumirá inicialmente por IP privada y desde orígenes
permitidos. Validar firewall efectivo y ausencia de publicación WAN.

## Diseño y contratos

- **633**. Outline Community v1.13.0 candidata. PostgreSQL y Redis en red
  privada Compose y sin publicar puertos. Persistencia en volúmenes declarados
  para PostgreSQL, Redis y adjuntos locales de Outline. Usar HTTPS y WebSocket
  en el proxy existente. El flujo por correo de v1.13.0 requiere workspace
  y usuario existentes. Para inicializar, validar en Community el plugin
  OIDC de entorno con un proveedor interno aprobado. Evaluar CT632 para
  correo posterior, con identidad y credenciales propias. Verificar el primer
  administrador y el usuario agente de forma independiente. Se comprobó la
  presencia de la credencial CRM con modo 0600 por metadatos. Su uso en este
  proyecto queda pendiente de confirmar que el emisor y el cliente realmente
  la admiten. No transferir esa credencial a los nuevos servicios.
  [Requisitos de Outline](https://docs.getoutline.com/s/hosting/doc/requirements-ULdYnwi4wG)
  · [Autenticación](https://docs.getoutline.com/s/guide/doc/authentication-Wr4sfjvmL1)
  · [Flujo por correo](https://github.com/outline/outline/blob/v1.13.0/plugins/email/server/auth/email.ts)
  · [Plugin OIDC](https://github.com/outline/outline/blob/v1.13.0/plugins/oidc/server/index.ts).
- **634**. Imagen oficial `jgraph/drawio:32.7.4` candidata
  (`sha256:3e3281733f69416b2b632adad05c9c07d434ebb775e01070d55e9f3247cebe31`).
  Configurar la URL propia mediante el ajuste Diagrams.net de Outline.
  El código de v1.13.0 utiliza la URL de la integración al abrir el editor
  desde el navegador, con una URL pública por defecto si se omite el ajuste.
  Declarar la configuración en el bootstrap idempotente a través de la
  interfaz soportada que supere el ensayo local. Validar origen, CSP,
  recursos externos y modo offline en el navegador. Outline conserva el
  diagrama editable como SVG/PNG con datos embebidos en su almacenamiento.
  [Ajuste de instalación](https://github.com/outline/outline/blob/v1.13.0/plugins/diagrams/client/Settings.tsx)
  · [Apertura y guardado](https://github.com/outline/outline/blob/v1.13.0/shared/editor/extensions/Diagrams.ts)
  · [Autoalojamiento Draw.io](https://github.com/jgraph/drawio/wiki/Self-Hosting).
- **635**. Imagen oficial `plantuml/plantuml-server:jetty-v1.2026.10`
  (`sha256:3719f4a9b0b061f1aa42d14d130388f831954ca65685d521b6c5b72301e993e6`).
  Incluye Graphviz. Aplicar perfil SANDBOX, límites de recursos y
  restricción de salida. El agente enviará diagramas al renderizador por
  la red interna y publicará desde el cliente usando la API de Outline.
  Validar render SVG y PNG. Conservar fuente `.puml` como adjunto descargable
  y mostrar el PNG generado en el documento. Ensayar ambos adjuntos con
  almacenamiento local y conservar el ID del documento para actualizarlo.
  [Imagen y Graphviz](https://github.com/plantuml/plantuml-server/blob/v1.2026.10/Dockerfile.jetty)
  · [Perfil de seguridad](https://plantuml.com/security).
- **API y MCP**. La tabla On-Premises incluye API y webhooks en Community.
  El contrato público enumera autenticación, colecciones, documentos y
  adjuntos. Probar credenciales de mínimo privilegio, `collections.list`,
  `documents.list/info/create/update/search` y `attachments.create` más
  la subida devuelta por la API. La tabla On-Premises no especifica MCP.
  La guía documenta la ruta self-hosted `/mcp` y la versión candidata
  contiene su código. Verificar acceso real en imagen Community sin licencia
  con una sesión autenticada y herramientas permitidas. Si MCP no está
  disponible, el flujo gratuito usa la API oficial desde el cliente de
  automatización. Mantener esa API como contrato del publicador.
  La licencia BSL de la versión permite el uso interno descrito y limita
  ofrecer un servicio documental comercial a terceros.
  [Ediciones](https://www.getoutline.com/pricing)
  · [API](https://www.getoutline.com/developers)
  · [MCP](https://docs.getoutline.com/s/guide/doc/mcp-6j9jtENNKL)
  · [Licencia](https://github.com/outline/outline/blob/v1.13.0/LICENSE).

## Implementación, validación y autorización

1. Revisar y aprobar el alcance del plan. Confirmar IP/reservas, dominios,
   método de alta y acceso, alcance del proxy/DNS/TLS, política de firewall,
   backup PVE y activación Prometheus/Blackbox/Grafana. Autorizar por separado
   los sockets exactos si se aprueba cAdvisor. Los jobs PVE actuales verificables
   seleccionan CT630 o CT631 explícitamente, así que no cubren estas altas.
2. Preparar declaraciones con `new-lxc.py`, Compose con imágenes por digest,
   plantillas de secretos separadas y fichas/Notes según el
   [proceso documental](../../runbooks/LXC-DOCUMENTATION-PROCESS.md).
   Reutilizar despliegue Compose versionado con identidad SSH verificada
   por el bootstrap canónico. Los scripts genéricos `deploy-service.sh` y
   `deploy-service2.sh` desactivan verificación de host. No ejecutarlos en esa
   forma. Adaptar el flujo común para los tres CT sin afectar llamadores existentes.
3. Ejecutar generador, validadores de inventario, Terraform fmt/validate,
   mock de alta por CT y Compose config. Ensayar localmente arranque,
   licencias/capacidades y flujos de integración con contenido sintético.
   Revisar enlaces y `git diff --check`. Definir prueba de carga sostenida
   con umbrales antes de asignar recursos definitivos.
4. Una vez autorizadas las identidades y recursos, generar un plan real
   guardado por CT. Cada plan debe mostrar solo su alta, con cero cambios
   o destrucciones de recursos existentes. La aplicación requiere revisión de
   ese binario exacto. Crear y verificar secuencialmente. Aplicar solo cambios
   compartidos expresamente autorizados, con preflight, backup y rollback.
5. Verificar HTTPS, login humano, lectura y escritura del agente, render
   SVG/PNG, ausencia de egress no previsto y publicación de PNG más fuente.
   Verificar Draw.io creando, guardando, reabriendo y editando desde Outline,
   con evidencia de origen propio y contenido editable después de reiniciar.
   Verificar recuperación tras reinicio, salud de base y volúmenes, y que la
   reaplicación no reinicie ni recree servicios. Añadir las colecciones
   iniciales solicitadas tras confirmar acceso administrativo.
6. Verificar backups PVE y restauración aislada. Incluir backup consistente
   de PostgreSQL y adjuntos de Outline, persistencia Redis y recuperación
   cifrada de secretos. Probar restauración de un documento, su Draw.io
   editable y el PNG con fuente PlantUML. Acreditar exporters y sondas nuevas
   conservando la línea base de observabilidad. Ante fallo, revertir solo
   el cambio afectado y preservar CT, volúmenes e imágenes según el runbook.

## Estado

Descubrimiento y propuesta documentados. Implementación IaC, validaciones de
runtime y despliegue pendientes. La aprobación solicitada para esta fase es
la revisión del diseño y la autorización específica de red, identidad y
dependencias compartidas, seguida de la revisión de cada plan real de alta.
