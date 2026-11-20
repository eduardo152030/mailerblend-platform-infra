# CT633–635 — Plataforma interna de conocimiento y diagramas

**Aprobado · Fase 7. IaC Reliability, Security & Disaster Recovery · 20/11/2026 (Europe/Madrid).**
Ronda `implementation`, inicio `6be70af601ff0775b19765dcecba590de73a8c15`,
base `origin/main`, rama `feat/knowledge-platform`, worktree
`../mailerblend-platform-infra-knowledge` relativo al checkout principal.
[PR #84](https://github.com/eduardo152030/mailerblend-platform-infra/pull/84).

## Ronda de ejecución

Ronda `review-01`, base `5cd6b477de148c669121cb5ec902f4166698e1a0`.
El propietario autorizó expresamente IaC, altas con planes acotados y revisión
automática, despliegue, integraciones, pruebas y publicación en el PR #84.
Sin cambios de datos en CT101, 107, 618 ni 632. Se mantiene TLS y SSH estricto.

Preflight 20/11/2026 23:50 CET: VMID disponibles, 22 675 MiB RAM disponibles,
6 163 MiB de swap ocupada y PSI de memoria 0 en las tres ventanas.
CRM usa GoTrue v2.197.0 sin servidor OAuth habilitado en su Compose. Las
consultas HTTPS a discovery, JWKS, autorización, token y userinfo devolvieron
404. Quedan sin acreditar registro de cliente, redirect y claims de OIDC.
Se excluyen cambios en CRM para añadir esa capacidad.

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

## Estado de la ronda — BLOCKED

IaC local para tres altas DHCP, Compose con imágenes fijadas, bootstrap SSH
capaz de descubrir IP después de verificar la identidad y MAC de PVE, script
de despliegue y publicador PlantUML por UUID en
[runbook operativo](../../runbooks/KNOWLEDGE-PLATFORM.md). Sin IP observada,
DNS, certificados ni altas efectivas.

Validaciones: Terraform fmt/validate, validadores de inventario (29 pruebas) y
provisioning (20 pruebas), configuración Compose de los tres servicios y
sintaxis de los scripts. Los planes dirigidos para 633/634/635 produjeron
1 alta y 0 cambios o bajas por CT. El plan real guardado de CT635 se comprobó
por recurso, VMID, hostname, DHCP/MAC, firewall, privilegios, almacenamiento,
recursos, Docker y TLS. Tras recuperar la CA mediante SSH estricto y verificar
la IP en el certificado, el API respondió HTTP 403 a la creación: solo root@pam
puede establecer el flag `keyctl` en PVE. La consulta posterior confirmó los
tres VMID disponibles. Se conserva la guarda Docker y se requiere una
identidad PVE autorizada. No se aplicaron los planes de los dos CT restantes.

La evaluación de CRM concluyó que el servicio existente no publica un IdP
compatible. Compose prepara un cliente OIDC separado. Falta instanciar o
seleccionar un proveedor interno y acreditar bootstrap Community. CT632
documenta SMTP AUTH:587 con STARTTLS obligatorio y mapa de remitente;
no se creó identidad ni se envió correo. Pendientes también la configuración
efectiva del editor en Outline, cuentas de prueba, publicación real,
monitorización, backups y restauración aislada.

## Reanudación tras la fusión — BLOCKED

Ronda `implementation` en `ops/knowledge-platform-rollout`, worktree
`../mailerblend-platform-infra-knowledge-rollout`, base
`576e2c719bb906b785eeb7f36e02ba308c4fcae4`. El propietario autorizó un token
temporal de `root@pam` para los tres planes acotados y su revocación.
El plan estricto de CT635 identificó exactamente una alta, con Debian 12,
firewall, DHCP, nesting y keyctl. PVE respondió HTTP 403 al apply con el
token sin separación de privilegios. El código instalado de PVE trata la
autenticación del usuario y la del token como identidades diferentes para
esta guarda. Se revocó y comprobó la ausencia del token. Los tres VMID
permanecen libres. No se intentaron las otras dos altas bajo el mismo bloqueo.

[PR de seguimiento #85](https://github.com/eduardo152030/mailerblend-platform-infra/pull/85).

## Ronda de autenticación directa

Ronda `review-01`, base `664eb7c101ebd83627b157f18f70f187c40402a2`,
en el worktree de PR #85. El propietario autorizó continuar con la sesión
directa temporal y solicitó documentar el runbook de alta vigente.

La sesión directa verificó TLS con la CA del nodo y usó el mecanismo de
preautenticación del proveedor. Alta secuencial 635 → 634 → 633 confirmada
por Terraform, con PASS de bootstrap y cero cambios en cada plan posterior.
IPs observadas por DHCP el 21/11/2026 Europe/Madrid: 192.168.1.64 (635),
192.168.1.63 (634) y 192.168.1.72 (633). Están en ejecución en PVE. Los valores
son concesiones observadas, pendientes de reserva. El método se documenta en
[el runbook de alta](../../runbooks/NEW-LXC-PROVISIONING.md#docker-sin-privilegios-y-la-guarda-keyctl).

Docker 29.9.3 y Compose 5.7.1 verificados en los tres CT.
En CT634 y CT635, el arranque de Draw.io y PlantUML quedó bloqueado por runc al abrir
`net.ipv4.ip_unprivileged_port_start` dentro del LXC. El host usa
`lxc-pve 6.0.0-1`. No se cambió el perfil AppArmor ni se expusieron servicios.

## Excepción AppArmor autorizada

Ronda `implementation`, base `ba99819f02d6cdd248260c507e78bac0883abf72`,
rama `ops/knowledge-platform-apparmor`, worktree
`../mailerblend-platform-infra-knowledge-apparmor`. El propietario autorizó
la excepción y el reinicio de CT633–635. Piloto en CT635 con respaldo,
arranque local y render SVG/PNG antes de extender. Se conserva LXC sin
privilegios y el alcance excluye el perfil global y otros CT.

Resultado del 21/11/2026 (Europe/Madrid): CT635 reinició, PlantUML arrancó y
renderizó SVG y PNG en loopback. CT634 reinició y Draw.io respondió HTTP 200
en loopback. CT633 ejecutó Node v26.13.1 desde la imagen fijada de Outline.
El arranque de Outline y el inicio de sesión quedan pendientes. Respaldo de configuración
conservado en PVE para los tres CT. Procedimiento en
[runbook vigente](../../runbooks/NEW-LXC-PROVISIONING.md).

[PR #86](https://github.com/eduardo152030/mailerblend-platform-infra/pull/86).

## Arranque privado de Outline

Ronda `implementation`, rama `ops/knowledge-platform-integration`, worktree
`../mailerblend-platform-infra-knowledge-integration`, base
`c235c27b7e3ef34c19a46e8fac6c620a5e762c20`. El PR #86 está fusionado.
Tras descartar el proveedor CRM actual, validar Dex dedicado en CT633 como
fallback autorizado. Arranque HTTPS en loopback con CA privada y usuarios
dedicados. Los nombres nuevos no resuelven y los vhosts de CT109 quedan
fuera del ensayo. No activar rutas definitivas hasta comprobar DNS y TLS.

Resultado privado de CT633, 21/11/2026 Europe/Madrid: Outline Community,
Dex, PostgreSQL, Redis y Nginx sanos. HTTPS comprobado con CA privada,
discovery OIDC y primer acceso administrador PASS. Agente independiente
autenticado como miembro del mismo workspace. Con su clave REST se verificó
listar colecciones y documentos, crear, leer, actualizar y buscar. CT635
renderizó el PNG que se publicó junto con su fuente en el mismo documento
por UUID, usando el formulario de subida firmado. Documento, imagen y
fuente recuperados después de reiniciar Outline. MCP Community respondió
a `initialize` con HTTP 200 y `serverInfo`, mediante clave de lectura.
La disponibilidad del editor Draw.io en CT634 está validada localmente.
Falta probar el ciclo nativo de edición desde Outline con una URL HTTPS
alcanzable por el navegador. Red definitiva, SMTP, monitorización, backups
completos y restauración aislada siguen pendientes.

La reaplicación idéntica conservó IDs y horas de arranque de los cinco
contenedores. Se verificó el catálogo de un dump PostgreSQL (182 553 bytes)
y se restauró en un contenedor temporal sin red, con consulta de documentos
exitosa. Constituye prueba de base de datos. El respaldo integral con los
volúmenes fuera de PostgreSQL y los secretos sigue pendiente.

[PR #87](https://github.com/eduardo152030/mailerblend-platform-infra/pull/87).

## Integración operativa para agentes

Ronda `implementation`, base `91e5617a385ce8b653082256152a61a0cab92e79`,
rama `ops/knowledge-platform-agent-guide`, worktree
`../mailerblend-platform-infra-knowledge-agent`. PR #87 y #88 fusionados.
Alcance autorizado: publicación segura, verificación MCP, guía reproducible,
DNS/TLS, Draw.io, SMTP, observabilidad y recuperación. Conservar contenido
humano y accesos existentes. La publicación de diagramas se limita a un
bloque con marcas explícitas y usa la revisión de Outline para las
escrituras concurrentes.

Resultado 21/11/2026 (Europe/Madrid): un documento de validación conservó
su introducción y conclusión. El patch de diagrama quedó protegido por
`lastRevision`, el servidor devolvió 409 a una revisión obsoleta y la
repetición preservó la revisión y adjuntos. El binario en imagen v1.13.0
acepta IDs de adjunto explícitos UUIDv4. MCP Streamable HTTP con una clave
`read` devolvió ocho herramientas de lectura en `tools/list` y ninguna
de escritura. Se crearon y verificaron seis colecciones de proyecto sin
compartición pública; se usó la terminología nativa de Outline.

Las tres sondas funcionales loopback se incorporaron por textfile a Node
Exporter y devolvieron 1 con frescura. Se cargó y verificó una alerta con
promtool y recarga controlada. El datasource de Grafana devolvió las tres
sondas por su API. Se probaron ocho archivos cifrados AES256,
cron a las 04:40 Europe/Madrid y retención de 30 días en el directorio
dedicado, con guarda de generación verificada. El dump cifrado se descifró y restauró en PostgreSQL aislado sin red.
Se listó el archivo de adjuntos. La copia de la clave a custodia
independiente y la restauración integral del stack siguen pendientes.

El resolver interno devuelve NXDOMAIN para los nombres finales y no hay
un flujo de administración del resolver disponible en el repositorio.
CT109 tiene un certificado wildcard compatible. No se publicaron rutas
provisorias ni se cambió el issuer del workspace. Draw.io conserva el
endpoint loopback. CT632 negocia STARTTLS con una CA válida; con
`SMTP_SECURE=false` Outline v1.13.0 usa `rejectUnauthorized: false`.
Se mantiene pendiente un transporte TLS verificable hacia el relay.
No se cambiaron sus identidades ni se enviaron mensajes en esta ronda.

[Guía de integración para agentes](../../runbooks/KNOWLEDGE-PLATFORM-AI-INTEGRATION.md).
