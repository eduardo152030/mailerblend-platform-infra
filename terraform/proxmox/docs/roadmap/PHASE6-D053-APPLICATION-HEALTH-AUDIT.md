# Fase 6. Grafana & Dashboards — auditoría Application Health D-053

2026-11-07 (Europe/Madrid). **Auditoría DONE; implementación NO autorizada ni
realizada. Fase 6 IN PROGRESS.** Fuentes: APIs actuales Grafana/Prometheus y SSH
estricto a los11CT afectados. No se infiere producción desde Git. Marcas de JSON
enUTC. Se conserva la consulta desplegada del panel, no una reconstrucción local.

La petición autoriza diagnóstico y propuestas exclusivamente. Se han ejecutado
GET de salud/lectura y `pg_isready -q`, sin POST de ingesta, login de aplicaciones,
consultas SQL, reinicios, recreaciones, recargas ni escrituras productivas. Solo
se añaden script, evidencia y documentación locales; sin commit/push.

## Identificación y causa común

La consulta D del panel devuelve **-1** exactamente para:
**611,613,616,617,618,620,621,623,624,625,626**. El mapping lo presenta como UNKNOWN.
La consulta utiliza únicamente `probe_success` Blackbox, con normalización de
servicio y control de `up`; al no encontrar una sonda asociada, usa el fallback
`inventario*0-1`. No se debe a fallo del join de CPU, datasource incorrecto ni a
que los17Node/cAdvisor estén caídos. No implica que esas11aplicaciones estén rotas.

Hay11sondas activas en Prometheus. Ninguna corresponde a esos11CT. En particular:
`infra-doc` no tiene identidad acreditada con CT613; `svc01` corresponde a61211;
las dos sondas de collect son de614, no de617. Las sondas Journal de
[journal-probes.yml](../../services/infra-prom/config/journal-probes.yml) son
**contratos locales preparados**, sin series activas para624/625/626. No confundir
archivo preparado con monitorización desplegada.

## Clasificación y propuesta — sin aplicar

A: métrica existente desaprovechada. B: healthcheck Docker aprovechable.
C: endpoint disponible para Blackbox. D: comprobación específica o definición
operativa pendiente. E: infraestructura/monitorización, Application Health N/A.
Las categorías pueden solaparse; los totales de actuación al final son excluyentes.

En todas las filas, «sin probe» significa sin `probe_success` asociado al servicio.
`container_health_state=-1` significa **sin healthcheck**, nunca healthy.

| CT ID | Servicio | Motivo UNKNOWN | Señal disponible / categoría | Solución propuesta | Cambios necesarios | Riesgo |
|---|---|---|---|---|---|---|
|611|infra-grafana|Sin probe; `up{job="grafana"}` tampoco existe actualmente|E; `/api/health`200/database=ok; Dockerhealth=-1|Application Health **N/A: monitorización**; mostrar salud de Grafana por separado|Solo semántica/consulta de la vista para N/A. HTTP interno sería mejora opcional, no necesaria para retirar esta clasificación incorrecta|Bajo; no usar NodeUP como salud de Grafana|
|613|infra-hola|Sin probe y **no hay aplicación ejecutándose**; solo exporters|D, ciclo de vida pendiente; Compose declara demo Nginx, runtime no la tiene|Mostrar **NO APP / pendiente de definición**, no HEALTHY ni N/A automáticamente|Decisión del propietario: demo retirada/intencionada o aplicación esperada ausente. Solo después definir contrato; sin desplegarla ahora|Medio: N/A a ciegas ocultaría una aplicación ausente|
|616|infra-blackbox|La consulta busca probes de aplicación, no salud del propio exporter|E; `up{job="blackbox_exporter",instance="192.168.1.116:9115"}=1`, métricas de recarga; HTTP9115/=200|Application Health **N/A: monitorización**; reutilizar el `up` en salud de monitorización|Solo consulta/clasificación Grafana; no crear una sonda de Blackbox a sí mismo|Bajo; scrapeUP no garantiza todos los endpoints remotos|
|617|infra-orbit|Sin probe; healthcheck Docker inexistente. Ruta LAN403 por allowlist|C; ruta pública `/orbit/healthz`200 desdeCT616; ruta directa18088/healthz403|Sondear la **ruta pública existente** a `/healthz`; agrega proxy y gateway sin enviar ingesta|1target Blackbox nuevo con `service=infra-orbit`, catálogo/validación/revisión IaC; no cambiar allowlist|Bajo-medio: liveness, no entrega Analytics ni dependencias externas|
|618|infra-composable-crm|Solo consume Blackbox e ignora healthchecks corregidos D051|A+B; `container_health_state` de `budibase-app` y `crm-api`=1; API `/ready`200/dbok; Budibase `/api/system/status`200|Reutilizar **readiness validada** de ambos componentes; distinguirla de disponibilidad HTTP externa|Solo consulta/semántica Grafana: fuente explícita `Docker readiness`, exigir cobertura completa de `app:container:expected`, frescura/cAdvisorUP y ausencia conocida→UNKNOWN|Bajo-medio: un min sin exigir componentes podría dar falso verde; no acredita acceso exterior|
|620|infra-excraper|Workers sin probe ni healthcheck Docker; Redishealthy no acredita workers|C; LinkedIn3000/health200 y Signals3001/health200 desdeCT616; Redishealth=1|Agregar ambas sondas y conservar diagnóstico Redis separado|2targets Blackbox; agregar por servicio conservando componente y falla prioritaria|Medio: endpoints declaran liveness; no prueban sesión LinkedIn, cuotas, scraping ni enriquecimiento real|
|621|infra-project-gestion|Sin probe y Focalboardhealth=-1; `/api/v2/ping` devuelve HTML de portada|D; Focalboard ejecutándose; raíz200, pero cinco rutas devuelven el mismoHTML/SHA256|Definir/verificar un contrato específico real de Focalboard antes de pintarlo saludable|Investigar ruta/API/version/config efectiva y validar contenido/readiness. Luego elegir check o probe; no activar simple2xx a ping como si fuera API|Medio-alto: falso positivo200/SPA; no se ha demostrado fallo de la API real|
|623|infra-gestoria|Sin probe ni checks Odoo/Postgres; Odoo solo loopback|D; `/web/health` y `/web/login`200 locales;8069 no accesible desdeCT616;8080 es **Welcome to nginx**|Readiness local Odoo y PostgreSQL; no usar test-nginx como salud de Odoo|Preparar checks locales/exportación de señal, o proxy privado específico con autorización posterior. Evitar publicar Odoo o reconfigurar Nginx sin aprobar|Medio: acceso y coberturaDB;200dehealth solo liveness, no UAT contable|
|624|infra-journal-web|Contrato preparado, target no activo; Nginx sin healthcheck|C;8090/=200 desdeCT616; test-nginx8080 es otra instancia|Publicar contrato HTTP existente a8090, no al contenedor test|1target Blackbox nuevo a8090/ con etiquetas correctas, sin duplicar catálogos activos|Bajo-medio: disponibilidad frontend, no flujo navegador/API completo|
|625|infra-journal-db|Sin probe ni PostgreSQLhealth; no hay aplicación HTTP equivalente|D;5432TCP abre, `pg_isready`local exit0; métrica de readiness inexistente|Salud tipada **Database readiness**; PostgreSQL forma parte de Journal y no se descarta como N/A automáticamente|Check PostgreSQL periódico/exportación de readiness; definir si basta pg_isready o lecturaSQL autenticada. TCPpreparado no lo reemplaza|Medio:TCP/pg_isready no prueban autenticación, consultas ni integridad|
|626|infra-journal-api|Contrato preparado, target no activo; APIhealth=-1|C;3000/health200/statusok desdeCT616|Publicar contrato HTTP existente; visibilizar su alcance de liveness|1target Blackbox nuevo a3000/health, sin recrear API|Bajo-medio: respuesta de health no demuestra todos los flujos ni SQL del Journal|

## Servicios y señales por CT

En todos ejecutan Docker/containerd como servicios systemd; Node Exporter y cAdvisor
son contenedores. También se observan cron, dbus, rsyslog, postfix y servicios base
systemd. **No se observó una unidad systemd de aplicación de negocio** en ninguno
de los11. Las listas completas de unidades, sockets TCP, imágenes, contenedores y
checks filtrados están en la evidencia, sin exportar env ni comandos sensibles.

| CT | Aplicación principal y Docker realmente activo (además de Node/cAdvisor) | Checks existentes | Endpoints / métricas de salud actuales |
|---|---|---|---|
|611|Grafana12.3.1: `grafana`|Grafana sin check|3010/api/health200. cAdvisorhealth(grafana)=-1. No targetgrafanaUP |
|613|Demo «hola» declarada; **ningún contenedor de app**, ni activo ni detenido|Solo cAdvisorhealthy|No listener de aplicación.9100/8085 son exporters. Sin serie de app |
|616|`infra-blackbox` (Blackbox Exporter0.25.0)|Exporter sin Dockercheck|9115/200, scrape propioUP y reload_successful. Las11probes son de otros servicios |
|617|`analytics-ingest-gateway`, `orbit-gateway-proxy`|Ambos sin check|18088/healthz403 desde616/loopback; Nginx permite192.168.1.71 y denyall. Ruta públicaHTTPS `/orbit/healthz`200 desde616. Ambas serieshealth=-1 |
|618|`budibase-app`, `crm-api`, `budibase-redis`, `budibase-couchdb`, `supabase-db`|Budibase/API/Redis/Postgreshealthy; CouchDBsincheck|BudibasecheckD051 valida UI,backend,worker,Redis/CouchDB efectivos; APIcheckD051 exige /ready/dbok. Cuatro serieshealth=1; CouchDB=-1. Expected existentes:budibase-app/crm-api |
|620|`infra-excraper-linkedin-worker-1`, `infra-excraper-signals-worker-1`, `infra-excraper-redis-1`|Redishealthy; workerssincheck|3000/health y3001/health200. Workershealth=-1; Redis=1; sin métrica funcional de jobs/sesión |
|621|`focalboard`, imagenmattermost/focalboard:7.10.0; PID1 `/opt/focalboard/bin/focalboard-server`|Sincheck|8081raíz/ping/config/version/health:200y mismapáginaHTML463bytes,títuloFocalboard. cAdvisorhealth=-1. No se asume que esos paths son endpointsAPIválidos |
|623|`infra-gestoria-odoo-1`, `infra-gestoria-db-1`, `test-nginx`|Todos sincheck|Odoo127.0.0.1:8069/web/health200 y/login200. Desde6168069noalcanzable.8080/=Nginxdefault. Treshealth=-1 |
|624|`infra-journal-web-web-1`, `test-nginx`|Ambos sincheck|192.168.1.124:8090/=200. Healthweb=-1;8080esotroNginx |
|625|`infra-journal-db-db-1`, `test-nginx`|Ambos sincheck|192.168.1.125:5432TCPconecta; pg_isready0enPostgreSQL. Healthdb=-1;8080esotroNginx |
|626|`infra-journal-api-api-1`, `test-nginx`|Ambos sincheck|192.168.1.126:3000/health200 JSON/statusok; API Node/server.js. Healthapi=-1;8080esotroNginx |

**Blackbox por CT:** ninguno de los11tiene hoy una probe asociada. No hay una
sonda que baste con renombrar en Grafana. Para Orbit se propone añadir el target de
su endpoint específico, conservando las sondas `/g/collect` de614: comprueban otra
función. Journal requiere publicar contratos preparados, no añadir copias múltiples
del mismoendpoint al catálogo. No se propone duplicar esos contratos por archivo.

## Reutilización y conteos para revisión

Propuesta preferida, sin sumar categorías solapadas:

- **1 LXC solo consultas Grafana:618**, reutilizando readiness ya verificada. Es
  viable si se aprueba mostrar fuente/tipo de señal. **0** pueden convertirse solo
  con consultas en nueva disponibilidad HTTPexterna medida: esa señal no existe.
  No proponer `min(container_health_state)` genérico ni equiparar Dockerhealthy con
  disponibilidad. Exigir ambos componentes esperados, frescura, exporterUP y
  propagación de ausencia; la métricaexpectedyaexiste y no necesita nuevas reglas.
- **4 LXC con nuevos targets Blackbox:617,620,624,626**, **5targetsHTTP** en total
  (dosworkersen620). Endpoints probados desdeCT616. Son contratos de liveness y
  frontend, no UAT. Requieren revisión y publicación IaC posterior; no aplicados.
- **3 LXC con contrato/check específico:621,623,625**. Para621 primero resolver
  cuál es la señal real; para623 el acceso local; para625 readiness dePostgreSQL.
  No basta con aceptar2xx/TCP y recolorear el dashboard.
- **3 LXC a clasificar de otra manera:611,616,613**. Los dos primeros son
  **E:monitorización/N/A** en Application Health, manteniendo su salud técnica
  aparte. **613noesE aprobado**: requiere decisión de ciclo de vida y estado
  explícito NOAPP/appesperadaausente, nunca un verde automático.

Total: **1+4+3+3=11**. CategoríasA–E:618A+B;617/620/624/626C;
613/621/623/625D;611/616E. Ninguna solución está implementada por esta auditoría.

## Evidencias, conservación y siguiente paso

- [Snapshot actual y consulta exacta](evidence/2026-11-07-d053-audit.json).
- [GET desdeCT616 y comprobaciones locales](evidence/2026-11-07-d053-endpoints.json).
- [Allowlist, respuestas idénticas deFocalboard y8069](evidence/2026-11-07-d053-followup.json).
- [Procesos y ruta públicaOrbit](evidence/2026-11-07-d053-executables.json).
- [pg_isready diagnóstico](evidence/2026-11-07-d053-db-readiness.json).
- [Conservación final](evidence/2026-11-07-d053-final.json).
- [Script de auditoría base](../../scripts/audit-fleet-application-health.py).

Contenedores activos/StartedAt/restartCount/bootIDs contrastados antes/después;
configuracionesProm610/Grafana611 porhash. No se modifican Compose, targets, reglas,
JSON desplegado, dashboards, usuarios, volúmenes ni imagen. El script no copia
entornos, logs dechecks ni comandos dehealthcheck completos. El resultado es
observación puntual, no ventana de estabilidad ni nueva aceptación de aplicaciones.

Siguiente: revisión del propietario del modelo **Availability / Readiness /
Infrastructure / No App** y aprobación de un alcance concreto. No implementar
sondas/checks ni reclasificar el dashboard hasta esa revisión.
