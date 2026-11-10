# Fase 6. Grafana & Dashboards — implementación y cierre D-060

Estado: **DONE**, criterios autorizados D-060 cumplidos. Cierre documental:
**2026-11-10 (Europe/Madrid)**. Implementación y navegador: 09 nov; revisión final,
idempotencia y ensayo aislado del candidato definitivo: 10 nov. Se conservan las
marcas UTC originales de los JSON; no se atribuyen pruebas antiguas a una fecha nueva.

## Resultado entregado

- [Proxmox · LXC Fleet Overview](http://192.168.1.111:3010/d/proxmox-lxc-fleet/proxmox-lxc-fleet-overview?theme=dark).
- [Proxmox · LXC Details, ejemplo CT 614](http://192.168.1.111:3010/d/proxmox-lxc-details/proxmox-lxc-details?var-lxc=614&theme=dark).

Fleet muestra los17 CT con identidad, exporters, recursos, estado PVE, uptime real y
cuatro capas de salud. CT ID abre Details conservando el rango; el enlace de vuelta
conserva CT/rango. Details incorpora asignación CPU/RAM, IP, capacidad raíz, red,
históricos, Docker por identidad completa, endpoints/latencia/disponibilidad,
readiness, targets/frescura, alertas/severidad/descripción de contrato y fichas locales.
Environment y la tabla Docker retirada de Fleet no se reintroducen en esa vista.
Docker sí se presenta en Details, conforme a la nueva solicitud.

Los nueve dashboards son ahora archivos IaC provisionados. Los siete anteriores
conservan UID, contenido y carpeta; tres que solo estaban enSQLite se exportaron
y adoptaron sin cambiar su modelo. No se certifican de nuevo todas sus consultas
heredadas, pero se comprueba conservación, carga y recuperación. Dos providers
con nombre/ruta únicos; la receta Compose conserva los tres mounts efectivos y
fija la misma imagen por digest. No se recreó Grafana activo para estos ajustes.

## Criterios de cierre

| # | Criterio autorizado | Evidencia / resultado |
|---|---|---|
| 1 | Fleet funciona | 17 filas únicas, métricas reales y estados coherentes; API y navegador PASS |
| 2 | LXC Details desplegado | UIDproxmox-lxc-details provisionado y renderizado; vistas614/615/618/613 PASS |
| 3 | Ambos gestionados por IaC | Generadores/JSON/provider y hashes; nueve dashboards provisionados |
| 4 | Navegación bidireccional | Links reales pulsados Fleet→Details→Fleet, CT/rango transmitidos |
| 5 | Uptime real y fiable | Comparación17 CT con API PVE, tres status/current independientes; máximo20 s, límite45 s |
| 6 | Salud coherente | 34 escenarios sintéticos; STOPPED solo PVE, ausencia≠HEALTHY; sin UNKNOWN en salud consolidada actual |
| 7 | Los17 LXC aparecen | Inventario publicado y filas/consultas verificadas, incluidos613/618/622 |
| 8 | Altas por IaC documentadas | Variables por inventario CPU publicado; CT 9999 sintético sin editar JSON; file_sd requiere altaIaC explícita |
| 9 | Sin dashboards perdidos | Siete modelos/carpetas anteriores intactos, nueve cargados/provisionados; snapshot SQLite y ensayo aislado |
| 10 | Sin regresiones de monitorización | Targets y reglas idénticos;17 Node/17cAdvisor/18 Blackbox UP, sondas success1, sin FIRING/PENDING |
| 11 | Límites documentados | Sección de límites y manual operativo; no se inventan señales ni UAT |

Estos criterios sustituyen la puerta anterior de F6 definida antes de esta
solicitud. DONE no implica UAT de aplicaciones ni una aceptación visual humana
no registrada: el navegador automatizado sí fue ejecutado. No se amplía la dispensa F3.

## Implementación IaC y consultas

- [Generador Fleet](../../scripts/generate-fleet-dashboard.py): enlaces y filtro
  final por inventario seleccionado en todas las ramas, incluida readiness.
- [Generador Details](../../scripts/generate-lxc-details.py),
  [JSON Details](../../services/infra-grafana/config/provisioning/fleet-assets/proxmox-lxc-details.json),
  [JSON Fleet](../../services/infra-grafana/config/provisioning/fleet-assets/proxmox-lxc-fleet.json).
- [Provider Fleet/Details](../../services/infra-grafana/config/provisioning/dashboards/fleet.yml),
  [provider legado único](../../services/infra-grafana/config/provisioning/dashboards/default.yml),
  [duplicado retirado](../../services/infra-grafana/config/provisioning/dashboards/provider.yml).
- Siete modelos en `services/infra-grafana/config/provisioning/legacy-assets/`;
  subdirectorio Infra conserva esa carpeta. Datasources existentes conservados.
- [Compose](../../services/infra-grafana/compose/docker-compose.yml): digest de la
  imagen ya instalada y mounts sin duplicados; actualización de receta, sinup/restart.
- [Transacción](../../scripts/phase6-grafana-final.py): baseline privado nuevo,
  config/Compose/SQLite consistentes, backups CT/fuera PVE, extracción/hash/integrity_check,
  recarga controlada de provisioning y rollback con protección de eliminación.

Variables Details: CT ID single-select desde `lxc:cpu_inventory:expected`; Service
se resuelve para ese CT. No lista estática17 CT. Identidades y datos se unen porservice
al inventario seleccionado; Docker incluye service+instance+cgroup ID+name para no
mezclar IDs clonados. Solo cgroups vistos≤45 s con cAdvisorUP. Capacidad CPU delcgroup,
RAMLXCFS y raíz Node; red sin loopback en bits/s. No métricas del host como fallback.

Application: probe_success y probe_duration, medias históricas observadas; Odoo/PG
por textfile existente y CRM por checks ya validados. Monitoring distingue edad
delscrape y edad de fuente CPU/cAdvisor/probe/PVE. Alertas reales desde ALERTS con
severidad y descripción del contrato IaC; evaluación interpolada enlazada a Prometheus.
Fichas se descubren desde archivos existentes; se muestran rutas locales verificadas,
no URLs falsas a archivos aún sin publicar.

## Correcciones y validación

Se corrigió una fuga de readiness de CT 623/625 al seleccionarotro CT y se añadieron
pruebas de regresión. La inspección visual detectó columnas repetidas trasjoins;
se proyectan etiquetas una sola vez preservando las columnas numéricas. Las
primeras pasadas del validador UI se adaptaron a paneles virtualizados y etiquetas
almacenadas en fields; las pasadas finales comprobaron datos y cabeceras reales.
Ningún gate fallido se presenta como una prueba pasada.

- 4 casos nuevos de aislamiento/nuevo CT/IDclonado/cgroupantiguo y30 regresiones de
  salud (16+14):PASS, sin suites largas F4/F5.
- 663 consultasinstantáneas en17 CT y28 históricas:sinNaN/Inf, sin datos cruzados,
  una fila por CT en general/capacidades. JSON/YAML y generación determinista PASS.
- Navegador: ambos dashboards, CT 614/615/618/613, rango1 h, enlaces ida/vuelta,
  cabeceras Docker/frescura y654 frames de datos reales; cero errores JS/consulta.
-17 comparacionesuptime con PVE y tres lecturas independientes, diferencia≤20 s.
- Reaplicación final10 nov:0 escrituras/0 recargas/0 reinicios. Grafana activo conserva
  ID/Started At/restart Count/mounts; reglas F5 y targets exactos. No apps/DB/recursos,
  secretos ni Telegram modificados por esta intervención. Sin commits/push.

## Persistencia, backup y recuperación

Ensayo final10 nov con el candidato exacto, misma imagen que producción, copia
consistente deSQLite y provisioningIaC, en contenedor nuevo aislado con red none y
sin puertos publicados. Nueve dashboards, modelos/carpetas originales yprovisioning
verificados tras arranque en frío; prueba detenida y conservada. Hubo candidatos
intermedios09 nov, también conservados. No se presenta como recreación de Grafana
productivo ni prueba deconectividad de datasource dentro de la redaislada.
Datasource y consultas reales se verificaron en Grafana activo.

Backuporiginal y snapshots privados bajo `/opt/infra-grafana/.runtime/d060/` y
`~/.local/share/mailerblend-recovery/grafana/d060/`; no Git. Conservar imágenes,
contenedores de ensayo detenidos y originales. Elrollback solo toca archivos de esta
transacción; primero protege contra eliminación para conservar los modelos
adoptados, después repone config/Composeprevios yverifica. Nuevo UIDDetails se
retiene si se revierte; no elimina automáticamente dashboards ni restaura DBsobre
volumenactivo. RestoreSQLite completo solo enensayo o recuperación explícita.
[Manual deoperación](../../services/infra-grafana/FLEET-OVERVIEW.md).

## Límites reales y pendientes externos

No quedan UNKNOWN en Application/Monitoring/Overall de los17 CT en la instantánea.
N/A solo Application613/611/616, sin exención de infraestructura. Sin señal local
readiness enotrosservicios se indica consultar endpoints, no se inventa éxito.
Docker SINHEALTHCHECK no equivale ahealthy. No existe contador fiable dereinicios:
no se transforma start_time en un contador ficticio. Estado Docker mostrado es
observación fresca de cgroup, no el estado exacto de la API Docker ni inventario de
originales detenidos. CPU Docker=%deun core, CPU LXC=%decapacidadasignada.

Disco mostrado es capacidad real del filesystem, no cuotavirtualmaxdisk ni valor
Terraform; divergencia de inventario sigue F7. Disponibilidadhistórica es media de
muestras, sin garantía durante huecos. Descripción dealerta es contrato IaC; valores
interpolados/activeAt en Prometheus. Fichaslocales no están hospedadas en Grafana.
Altasrequieren inventario/targetsIaC; no hay descubrimientoydespliegue automáticos
deexporters por aparecer un CT en PVE.

Scrape propio Grafana, observabilidad completa del host, seguridad/rotaciónhistórica,
CI/herramientas, DRcontinuo, digest EVA, prevenciónsGTM y UAT/GA4 quedan fuera de F6.
No se ejecutan ni se consideran aceptados por este cierre.

## Evidencias y tiempos

- [Resultado inicial09 nov](evidence/2026-11-09-d060-result.json),
  [resultado final10 nov](evidence/2026-11-10-d060-result.json).
- [Consultas](evidence/2026-11-09-d060-promql.json),
  [uptime PVE](evidence/2026-11-09-d060-uptime.json).
- [Navegador](evidence/2026-11-09-d060-browser.json),
  [Fleet](evidence/2026-11-09-d060-fleet.png),
  [Details614](evidence/2026-11-09-d060-details-614.png),
  [Details618](evidence/2026-11-09-d060-details-618.png).
- [Recreaciónaislada final](evidence/2026-11-10-d060-recreation-replay-final-20261110.json).

13,7 min desdebaseline hasta verificación inicial09 nov. Cierre/revisión10 nov medido
separadamente en [tiempos](evidence/2026-11-10-d060-closure-validation.json);
la pausa entre sesiones no se cuenta como trabajo. Lectura/preparación previa al
baseline no quedó cronometrada. El campo elapsed_minutes_from_baseline del snapshot
final es tiempo de calendario, incluye la pausa y no es esfuerzo de ejecución.

Siguiente: revisión del resultado por propietario yselección deun pendiente F7 o
complemento F4 con alcance explícito. F6 DONE; ejecución detenida, sin avance a F7.
