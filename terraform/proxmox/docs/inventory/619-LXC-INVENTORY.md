# CT619 — infra-pulpo · Inventario técnico

Ficha principal de CT619, el servidor n8n del proyecto **LinkedIn Stealth Sourcing**. Captura del **15 de noviembre de 2026**, basada en las consultas de solo lectura y la auditoría de workflows de Cline. El acceso al CT se hizo mediante `ssh pve` y `pct exec 619`. Las evidencias de origen conservan sus marcas de tiempo en UTC.

**Estado al corte.** El CT y el contenedor n8n estaban en ejecución. Los 11 workflows estaban inactivos y PostgreSQL tenía 0 filas en `execution_entity`. La auditoría identificó una posible incompatibilidad entre el nodo **Send Invite** y las rutas de CT620. La integración con el CRM y la ejecución completa del flujo quedaron pendientes de verificación.

- [Inventario declarado](../../inventory/services/infra-pulpo.yml)
- [Inventario LXC observado](../../inventory/lxc-observed.json)
- [Notes operativas de infra-pulpo](../../services/infra-pulpo/NOTES.md)
- [Documentación de workflows del proyecto](../projects/LinkedIn_Stealth_Sourcing_status/WORKFLOWS.md)

## A. Identificación e infraestructura

| Campo | Valor |
|---|---|
| CT / hostname / nodo | `619` / `infra-pulpo` / `pve` |
| Estado observado | `running` |
| Plataforma y sistema | Proxmox LXC con Docker Compose sobre Ubuntu 22.04.5 LTS (Jammy) |
| Clasificación | Etiquetas `internal` y `automation`. Clasificación formal `Not verified` en la metadata |
| Recursos asignados | 2 vCPU, 2048 MiB de RAM y 512 MiB de swap |
| Privilegios y AppArmor | LXC privilegiado (`unprivileged=0`), perfil `unconfined` |
| Red | `192.168.1.119/24`, bridge `vmbr0`, gateway `192.168.1.254`. Firewall de interfaz habilitado |
| Disco observado | `local-lvm:vm-619-disk-0,size=10G` |
| Disco declarado | 16 GiB en el YAML del servicio. Diferencia pendiente de reconciliar |
| Descripción observada en Proxmox | `Managed by Terraform - Service: infra-pulpo` |
| Etiquetas observadas | `192.168.1.119;automation;infra;internal;n8n;parte_linkedin_stealth_sourcing;server` |

## B. Función del servicio

CT619 aloja n8n y su base de datos PostgreSQL. Los workflows definen la búsqueda e importación de leads, el enriquecimiento de señales, la selección de plantillas A/B, los controles de presupuesto y el registro de actividad en el CRM. La instancia incluye también flujos de comprobación de límites y un workflow independiente de recordatorios por Telegram.

## C. Aplicaciones y componentes

| Servicio | Contenedor | Imagen o versión observada | Estado observado |
|---|---|---|---|
| n8n | `infra-pulpo-n8n-1` | `n8nio/n8n:latest`, versión de aplicación **2.8.3** | En ejecución, 0 reinicios observados, sin healthcheck de Docker |
| PostgreSQL | `infra-pulpo-postgres-1` | `postgres:16-alpine` | En ejecución, `healthy`, 0 reinicios observados |
| node_exporter | `node_exporter` | `prom/node-exporter`, referencia corta `3ac34ce007ac` | En ejecución |
| cAdvisor | `cadvisor` | `ghcr.io/google/cadvisor`, referencia corta `b8e7d1093144` | En ejecución, `healthy` |

La ficha de origen registra además las referencias truncadas `53004142…` para n8n y `97ff59a4…` para PostgreSQL. Los `RepoDigests` completos de las imágenes quedan pendientes de verificación.

**Contenedores detenidos observados**

- `cadvisor-phase4-619-rejected-1`
- `cadvisor-pre-phase4-619`
- `node_exporter-pre-phase4-619`

## D. Red y puertos

| Puerto publicado en el CT | Puerto en Docker | Servicio |
|---|---|---|
| `192.168.1.119:15678` | `5678/tcp` | UI y API de n8n |
| `192.168.1.119:9100` | `9100/tcp` | Métricas de node_exporter |
| `192.168.1.119:8085` | `8080/tcp` | Métricas de cAdvisor |
| Sin publicación en el CT | `5432/tcp` | PostgreSQL en la red Docker |

El inventario de routing citado en la ficha de origen no registra un dominio público, un proxy Nginx ni una regla de publicación para CT619. El alcance de acceso efectivo depende de la red y de sus reglas de firewall.

## E. Datos y almacenamiento

| Recurso | Evidencia |
|---|---|
| Sistema de archivos raíz | `df -h /` informó 9,8 G de tamaño, 5,3 G usados, 4,0 G disponibles y 58 % de uso |
| Datos de PostgreSQL | Volumen identificado en la ficha de origen como `n8n_postgres_data`. `du -sh /var/lib/postgresql/data` informó `67.0M` dentro del contenedor |
| Esquema n8n | 58 tablas según la auditoría de PostgreSQL |
| Definiciones de workflows | 11 filas en `workflow_entity` |
| Ejecuciones registradas | 0 filas en `execution_entity` al momento de la consulta. El historial anterior queda indeterminado |
| Redis en CT620 | 0 claves en la consulta reportada. La relación de Redis con el modo de ejecución de n8n queda por confirmar |

## F. Configuración

| Elemento | Ubicación o estado |
|---|---|
| Compose del servicio | `/opt/infra-pulpo/docker-compose.yml`, con n8n y PostgreSQL |
| Variables y secretos | `/opt/infra-pulpo/.env`. La auditoría dejó los valores, las credenciales y las variables internas de n8n fuera de la revisión |
| Compose de exporters | `/opt/exporter-phase4-pilot/integration-20261102T223431Z-619/` |
| Persistencia propia de n8n | Pendiente identificar el montaje efectivo de `/home/node/.n8n`, si existe, y dónde se conserva la clave de cifrado de credenciales |
| Zona horaria | Pendiente confirmar la zona efectiva de los triggers programados |

## G. Workflows n8n

Los **11 workflows** estaban inactivos. La columna de disparador recoge la configuración auditada. El horario efectivo del cron sigue pendiente de verificar.

| Workflow | ID | Nodos | Disparador configurado |
|---|---|---:|---|
| 1. LinkedIn Search & Invite - 3 PACKS | `1lbacmAUQ2Hne7Fc` | 42 | Cron `0 9 * * 1-5` |
| 1. LinkedIn Search & Invite - 3 PACKS | `b25FRkdahggQtnuW` | 38 | Cron `0 9 * * 1-5` |
| 1. LinkedIn Search & Invite - 3 PACKS | `wezH45QWFXjqC3ep` | 38 | Cron `0 9 * * 1-5` |
| 1. LinkedIn Search & Invite (OPTIMIZED) | `GdGq0Me9pqFPEqWk` | 32 | Cron `0 9 * * 1-5` |
| 1. LinkedIn Search & Import | `6LfQZcdmgGZlvMV9` | 12 | Cron `0 9 * * 1-5` |
| 1. LinkedIn Search & Import | `VUgMxma2MzEgHE6g` | 13 | Cron `0 9 * * 1-5` |
| 1. LinkedIn Search & Import (FIXED) | `6lleHw1NpjRyvSbY` | 10 | Cron `0 9 * * 1-5` |
| 2. Lead Enrichment | `4C4d7KFmUd5md3J5` | 10 | Cada 6 h |
| LinkedIn Sourcing - Health Check | `qAnooe37jJj73Bu0` | 9 | Cada 1 h |
| LinkedIn Sourcing - Health Check SIMPLE | `Nvt9mlRzuz33Ldu6` | 6 | Cada 1 h |
| EVA - Telegram Human Reminders | `I5ZFvl8PWNBxQorw` | 7 | Telegram Trigger |

`1lbacmAUQ2Hne7Fc` es el **candidato a workflow canónico** entre los tres «3 PACKS». Tiene 42 nodos y el export muestra la secuencia `Delay Invites → Consume Invite Budget → IF Can Send Invite`, con salidas hacia `Send Invite` y `Stop Invites (Cap Reached)`. La designación oficial y la equivalencia de las dos variantes de 38 nodos siguen pendientes. El estado de archivado de los workflows también queda por confirmar.

## H. Dependencias y compatibilidad

| Dependencia | Dirección | Uso |
|---|---|---|
| linkedin-worker (CT620) | `192.168.1.120:3000` | Rutas de búsqueda y envío referenciadas en los workflows |
| signals-worker (CT620) | `192.168.1.120:3001` | Enriquecimiento de señales |
| CRM/API | `infra-svc01.mailerblend.com` | Límites, plantillas, importación, actualización de leads y registro de actividad según los exports. Disponibilidad pendiente de verificar |
| PostgreSQL local | Red Docker de CT619 | Persistencia de n8n |
| Telegram | Integración del workflow EVA | Recepción y envío de recordatorios según su definición. Credenciales y funcionamiento pendientes de verificar |

| Ruta configurada en n8n | Uso en los exports | Resultado HTTP reportado |
|---|---|---|
| `POST /search/people` | Los tres workflows «3 PACKS» | `405` |
| `POST /job/search` | Tres variantes «Search & Import» y «Search & Invite (OPTIMIZED)» | `404` |
| `POST /job/invite` | Nodo `Send Invite` del candidato canónico y otros flujos de invitación | `404` |
| `POST /enrich/places` | «Lead Enrichment» | `405` |

**Hallazgo pendiente de confirmación.** El `404` de `/job/invite` podría bloquear el paso `Send Invite`. El resumen de auditoría no indica el método HTTP empleado para obtener cada respuesta. Los `404` y `405` se conservan como resultados reportados, con los métodos registrados en CT620 pendientes de contrastar en el código desplegado. También queda pendiente una prueba funcional del flujo completo.

## I. Monitorización

| Señal | Fuente | Estado de verificación |
|---|---|---|
| Métricas del LXC | node_exporter en `192.168.1.119:9100` | Contenedor y puerto observados |
| Métricas de contenedores | cAdvisor en `192.168.1.119:8085` | Contenedor `healthy` y puerto observado |
| Scrape y alertas | Prometheus (CT610), Alertmanager y Telegram de infraestructura | Referenciados en la ficha de origen. Targets y entrega de alertas pendientes de verificación |
| Disponibilidad de n8n | UI/API en `192.168.1.119:15678` | Contenedor en ejecución. Healthcheck y resultado de la comprobación HTTP de la aplicación pendientes |

## J. Operación

- Ruta de acceso observada mediante `ssh pve` y `pct exec 619`. La ficha de origen registra un problema de validación de host key para el acceso SSH directo.
- La auditoría verificó el recuento de ejecuciones consultando PostgreSQL. La CLI de la instancia devolvió `Command "list:executions" not found`.
- La descripción de Proxmox indicada en la sección A corresponde al momento de la captura. La sincronización posterior de las Notes mediante Terraform queda sin verificar en el registro compartido.
- Las Notes operativas resumen esta ficha. El índice general del repositorio enlaza al inventario individual.

## K. Backup y recuperación

La evidencia revisada deja pendientes la política de backup de CT619, la fecha de la última copia, la retención y una prueba de restauración. Para preparar un procedimiento reproducible, confirmar que la copia cubre:

1. La configuración del LXC y su disco, mediante el mecanismo de backup de Proxmox que se utilice para este servicio.
2. Una copia consistente de PostgreSQL, por ejemplo un dump lógico, con una restauración probada en una instancia de recuperación.
3. El Compose, el `.env`, la clave de cifrado efectiva de n8n y el almacenamiento persistente adicional identificado en la sección F. Los secretos se recuperan desde su ubicación protegida.
4. Una validación en el entorno restaurado del acceso a n8n, la conexión a PostgreSQL y la presencia de las definiciones de workflows con sus estados esperados.

## L. Verificaciones pendientes

| Pendiente | Evidencia para cerrarlo |
|---|---|
| Responsable, entorno formal y repo de aplicación | Identificación del owner, clasificación y repositorio que gobierna Compose y versiones |
| Diferencia de disco | Confirmación de la capacidad deseada y conciliación entre YAML y Proxmox |
| Rutas de CT620 y CRM | Registro de rutas y métodos del código desplegado, y resultado de verificación de disponibilidad de las dependencias |
| Versión oficial de «3 PACKS» | Referencia de proyecto que confirme el ID canónico y revisión de las dos variantes del mismo nombre |
| Monitorización de n8n y CT619 | Respuesta de la sonda de aplicación y estado de los targets de Prometheus |
| Backups y recuperación | Última copia, retención, cobertura de claves y volúmenes, y prueba de restauración |
| Contenedores residuales | Determinar si los tres contenedores detenidos se conservan para rollback |
| Notes de Proxmox | Evidencia de la descripción efectiva después de la sincronización |
