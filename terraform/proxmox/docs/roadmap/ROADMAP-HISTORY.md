# Historial documental anterior a la consolidación D-059

Copia conservada el 2026-11-09 (Europe/Madrid). Los estados y permisos siguientes
son históricos; consultar [estado vigente](CURRENT-STATUS.md) y [roadmap](ROADMAP.md).
Las fechas UTC de evidencias se conservan.

# Roadmap de infraestructura

## D-058 — simplificación visual Fleet — DONE técnico

2026-11-09 (Europe/Madrid). Eliminadas columna Environment y tabla Componentes
Docker del generador IaC/JSON y Grafana611. Cobertura y navegación ocupa su fila.
API provisionada verificada, otros siete dashboards/datasources e identidadGrafana
conservados; backup CT/fueraPVE idéntico y legible. Una escritura de JSON, cero
recargas/reinicios; segunda aplicación sin escrituras. No métricas/reglas/apps
modificadas, sin commits/push. F6 global IN PROGRESS; siguiente: revisión visual.
[Evidencia](evidence/2026-11-09-d058-presentation.json).

## D-058 — simplificación visual Fleet — IN PROGRESS

2026-11-09 (Europe/Madrid). Propietario solicita eliminar columna Environment y
panel Componentes Docker · diagnóstico. Alcance F6-03: generador/JSON y provisioning
exclusivo611, backup/rollback, verificación API/UI e idempotencia. Sin métricas,
reglas, apps, reinicios ni commits/push. Siguiente: aplicar y verificar.

## D-057 — salud completa17/17 — DONE técnico del alcance

2026-11-09 09:44 CET (Europe/Madrid). Fleet17/17 con Infrastructure/Monitoring/Overall HEALTHY,
cero UNKNOWN.613 ApplicationN/A verificada, DEMO sin exención;621 pingJSON7.10.0
sondeado;623Odoo+PG y625PG readiness con tres métricas periódicas ya instaladas.
17Node/17cAdvisor/18Blackbox UP/success1; uptimePVE real; sin FIRING. Config610/611/
616 aplicada con backupCT/fueraPVE y restore-check, promtool/parserBlackbox,
30casos sintéticos,30consultas reales y navegadorPASS. Segunda aplicación0escrituras/
recargas/reinicios. Apps/DB/recursos/F5/siete dashboards ajenos conservados.
Sin commits/push ni reiniciosLXC/apps.3,5min desde línea base hasta validación,
lectura/cierre aparte. F6globalINPROGRESS; aceptaciónvisual propietario pendiente.
[Informe](PHASE6-D057-COMPLETE-HEALTH.md), [resultado](evidence/2026-11-09-d057-result.json).
Siguiente: revisiónvisual; ejecución detenida, sin otraetapa.

## D-057 — reanudación de salud completa — IN PROGRESS

2026-11-09 (Europe/Madrid). Petición vigente autoriza completar el mismo alcance.
Lectura actual: collectors623/625 ya instalados y tres señales1;17Node/17cAdvisor/
17Blackbox, sin FIRING. Nueva línea base y backups separados del07nov; se preservan
los anteriores. Identidades/arranques intactos; hashes opacos de configuración de
cinco exporters difieren del07nov, sin atribuir causa ni sobrescribirlos.
613 solo exporters/serviciosSO, Postfix loopback-only; Application N/A fundamentado.
Siguiente: validar candidato, añadir sonda621 y dashboard, comprobar idempotencia.
Sin apps/DB/recursos/F5/commits/push ni reinicios.

## D-057 — salud LXC completa, cuatro pendientes — IN PROGRESS

2026-11-07 18:08 CET. Solicitud autoriza monitorización IaC613/621/623/625 y consolidación
Infrastructure/Application/Monitoring/Overall para17CT, STOPPED solo desdePVE.
613DEMO confirmado, verificar appausente antes deN/A.621/ping real JSON7.10;
623Odoo local+PG y625pg_isready mediante checks de lectura y textfileNodeexistente.
Timers locales root usan accesoDocker yaadministrado, sin nuevo usuario/rol/ACL;
pg_isready como usuario postgres existente y escritura métricas como nobody.
Sin cambiar apps/DB/passwords/healthchecks/recursos/F5 ni reinicios/commit/push.
Backup/rollback acotado y validación/idempotencia; no otras etapas. F6INPROGRESS.
Siguiente: comprobar checks, preparar candidatos y desplegar monitorización.

## D-056 — Uptime PVE desplegado — DONE técnico; F6 IN PROGRESS

2026-11-07 17:43 CET (Europe/Madrid). 17/17uptimes reales enGrafana desdeAPI Proxmox;26LXC
API descubiertos sin listasVMID, filtrados a17monitorizados porinventario dinámico.
Exportercentral3.11.0 en610 no-root, capacidadesvacías/rootfsRO/redProm privada.
Usuario/tokenpropios exclusivamentePVEAuditor, privsep=1; seis privilegiosAudit
verificados, secreto0400fueraGit, TLS/CA activo, sin credencialTerraform.
Comparación17CT conPVE y611/618/624status/current: máximo11.0s (<45s).
Prometheus/GrafanaIaC, previos17Node/17cAdvisor/17Blackbox, reglasF5/umbrales/apps/
identidades/sietedashboards conservados; sin reinicios deLXC/apps/serviciosprevios.
Segundaaplicación0escrituras/recargas/recreaciones. Inicial upstreamPython3.14 rechazó
CA porkeyUsage; mismoexporter sobrePython3.12soportado, base+depsfijadas, TLSsinbypass.
Soloexporternuevo sustituido; candidatoimagen/contenedorretenidos. No rollbackProm.
UptimeDONE técnico; F6INPROGRESS y aceptaciónvisual propietario pendiente. Tiempo:17.1min.
[Informe](PHASE6-D056-UPTIME-EXECUTION.md), [resultado](evidence/2026-11-07-d056-result.json).
Sin recursosPVE, reglasF5, apps, commits/push. Siguiente: revisiónvisual; noEtapaB.

## D-055 — Uptime centralizado preparado; pendiente permiso de lectura

2026-11-07 17:24 CET (Europe/Madrid). Diagnóstico/preparación DONE, ejecución BLOCKED por
aprobación según petición: no exporter/métricasPVE ni identidadAPI de sololectura.
TokenTerraform heredaPVEAdmin, no reutilizado. Propuesta concreta: exporterupstream
3.11.0fijadopordigest, único contenedor no-root en610/redProm existente; resources/
status y métricasuptime/info/up porCT, sin listasVMID. Requiere usuario/token nuevos
PVEAuditor en/, privsep=1 y archivo secreto privado. TLS/CA desde610PASS; Compose,
promtool y8casos sintéticosPASS. Soloartefactos locales, nada aplicado:17uptimes
siguenUNKNOWN. Fuente admin puntual previa no equivale a monitorización desplegada.
Sin permisos nuevos, recargas/reinicios/apps/recursos/reglasF5/commits/push.
[Propuesta](PHASE6-D055-UPTIME-PROPOSAL.md),
[evidencia](evidence/2026-11-07-d055-preparation.json).
F6INPROGRESS. Siguiente: aprobación explícita de identidad de lectura y despliegue
acotado; no usar SSHroot periódico ni credencialTerraform para evitarla.

## D-054 — Etapa A desplegada; Uptime sin fuente fiable — F6 IN PROGRESS

2026-11-07 17:15 CET (Europe/Madrid). Application Health UNKNOWN11→4:613/621/623/625
conservados.611/616 NOT APPLICABLE como negocio con Monitoring Health real;618
HEALTHY(readiness), sin disponibilidad pública certificada.617/620/624/626 con
sondas funcionales verificadas. Seis sondas nuevas incluida Grafana:11anteriores
preservadas,17BlackboxUP/success1;17Node/17cAdvisor conservados. Regla/umbralesF5,
apps, imágenes, identidades y siete dashboards ajenos intactos. Backups CT/fueraPVE,
restore-check, promtool/parserBlackbox,26casos sintéticos,28consultas y navegador
PASS. Segunda aplicación0escrituras/recargas/reinicios. Sin commits/push.
Columna Uptime dinámica añadida,17filas UNKNOWN: node_boot_time_seconds refleja
arranqueHOST, rechazado por comparación con API PVE17CT. node_time es reloj;
no métrica LXC/PVE publicada. No se afirma uptime real completado; requiere fuente
fiable y alcance separado. No Docker/exporter como sustituto. F6INPROGRESS;
EtapaA DONE técnico, aceptación visual propietario pendiente. Tiempo:12.4min.
[Informe](PHASE6-D054-STAGE-A-EXECUTION.md), [resultado](evidence/2026-11-07-d054-result.json).
Siguiente: revisión visual y autorización de fuente uptime; no EtapaB ni otrosCT.

## D-053 — auditoría de 11 Application Health UNKNOWN — DONE, sin implementar

2026-11-07 17:00 CET (Europe/Madrid). Fase 6 IN PROGRESS. Consulta desplegada y runtime
confirman UNKNOWN en CT611/613/616/617/618/620/621/623/624/625/626: ninguno tiene
probe Blackbox asociada. Propuesta: 618 reutiliza readiness D051 por consultas;
617/620/624/626 necesitan 5 targets HTTP en total; 621/623/625 requieren contrato
específico; 611/616 se proponen N/A de monitorización y 613 requiere decisión de
ciclo de vida (demo ausente, no declarar N/A automáticamente). Categorías y totales
son propuestas, no cambios aceptados. Orbit público healthz200 desde CT616; directo
403. Focalboard621 ping devuelve el mismo HTML que raíz; no prueba API healthy.
Odoo623 loopback200, 8080 solo Nginx de prueba; PostgreSQL625 pg_isready0 sin métrica
periódica. Salud Docker de CRM es readiness, no disponibilidad externa certificada.
Auditoría de lectura, sin configuración/recargas/reinicios/recreaciones/commits/push;
solo script, evidencia y documentación locales. Los 11 UNKNOWN se conservan.
[Informe](PHASE6-D053-APPLICATION-HEALTH-AUDIT.md),
[evidencia](evidence/2026-11-07-d053-audit.json),
[conservación](evidence/2026-11-07-d053-final.json).
Siguiente: revisión del propietario; ninguna implementación autorizada.

## D-052 — Fleet Overview desplegado — DONE técnico; F6 IN PROGRESS

2026-11-07 16:36 CET (Europe/Madrid). Dashboard principal provisionado en CT611 con datasource
Prometheus existente: tabla17CT, KPIs17/17Node,17/17cAdvisor,11/11Blackbox,
CPU/RAM/discoLXC, filtros Service/LXC, alertas y diagnóstico Docker.26consultas
reales/9porproxyGrafana PASS;12casos sintéticos y navegador/filtros/rango/enlace
PASS;segunda aplicación cero escrituras/recargas/reinicios.7dashboards/2datasources
conservados, backup CT/fueraPVE y restore-check SQLite/config PASS. Tres retornos
preventivos por metadatos versión/ordenMounts; comparadores corregidos, contenido
ajeno intacto. Cero restarts/recreaciones; providers antiguos duplicados pendientes.
11CT sinsondaasociada siguenUNKNOWN, Dockerhealthy no acredita disponibilidad.
Descripción/tiempoactivo enlazados aPrometheus; sinhistorialRESOLVED. Grafanadinámico,
file_sd requierealtaIaC explícita; no discoveryPVE afirmado. F6 globalINPROGRESS;
aceptaciónvisual propietario y recreaciónreal no realizadas. Sinapps/reglasF5/
Telegram/CT610/recursos/commits/push. Tiempo: 17.4min desde primera lecturaProm.
[Informe](PHASE6-D052-EXECUTION.md), [resultado](evidence/2026-11-07-d052-result.json),
[dashboard](http://192.168.1.111:3010/d/proxmox-lxc-fleet/proxmox-c2b7-lxc-fleet-overview?theme=dark).
Siguiente: revisiónvisual propietario y alcance del próximo dashboard, sinavanceautomático.

## D-051 — tres healthchecks CRM/EVA corregidos — DONE técnico

2026-11-07 16:08 CET (Europe/Madrid). focalboard622, budibase-app618 y crm-api618
healthy; tres series cAdvisor health1 y cero alarmas objetivo FIRING en Prometheus/AM.
API ready200/dbok, Focalboard ping/UI200, Budibase status200/passing y3.27.4 conservada.
Correcciones IaC: Python nativo para API y dependencias reales Budibase; Bash nativo
para Focalboard /api/v2/ping. Mismas imágenes/env/puertos/recursos/datos/redes;
originales detenidos, backups CT/fueraPVE restaurados en staging, segunda aplicación
sin recreación en los tres. Prom/AM READY y17Node/17cAdvisor/11Blackbox UP.
16pruebas PASS. Incidencias: comparación DNS null/[] en API con intento de parada
SIGTERM agotado durante arranque; mismo candidato saludable reconciliado. Focalboard
revertido por representación Binds/Mounts, reintento aislado d051b aceptado, rechazado
retenido. Observación SIGTERM y UAT de negocio quedan separados; no se ocultan.
Reglas/umbrales F5 intactos; serie antigua Budibase retirada antes del cierre.
Sin apps ajenas/DB/esquemas/exporters/PVE, commits/push ni eliminación de backups.
[Informe](HEALTHCHECKS-D051-EXECUTION.md), [evidencia](evidence/2026-11-07-d051-result.json).
F5 DONE conservada. Siguiente: revisión; F6 pendiente de alcance/autorización.

## D-050 — Fase 5. Alerting Optimization — DONE — Accepted

2026-11-07 (Europe/Madrid). IaC aplicada y recargas controladas en CT610:
26 alertas +34 entradas de grabación; 12 nuevas/14 conservadas con mejoras/1 retirada.
CPU LXC exclusiva, RAM/disco por severidad, salud Docker/sGTM, ausencia de métricas y
contenedores esenciales, autovigilancia. Telegram por severidad y cinco inhibiciones
probadas sin ocultar aplicaciones independientes. Prom/AM READY, reglas sanas,
17 Node/17 cAdvisor/11 Blackbox conservados; segunda aplicación sin escrituras/recargas.
FIRING/RESOLVED por cadena CPU real: API132→134 y errores56 constantes; propietario
confirma ambos recibidos y claros. Ensayo retirado. Backup CT/fueraPVE/restauración
staging verificados; rollback preventivo inicial por espera prematura de primera
evaluación, hashes restaurados y validador corregido antes de aplicación final.
CRM/EVA mantienen tres unhealthy preexistentes con cobertura WARNING; no reparación.
Grafana/CRM HTTP específico y Alertmanager adicional heredado son pendientes separados.
Sin apps/exporters/recursos/LXC, commit ni push. [Informe](PHASE5-D050-EXECUTION.md),
[evidencia](evidence/2026-11-07-d050-result.json). F4 17/17 conservada.
Siguiente: Fase 6. Grafana & Dashboards, pendiente de alcance/autorización; no avanzar automáticamente.

## D-049 — ficha individual y Notes CT615 — DONE

[Ficha técnica principal](../inventory/615-LXC-INVENTORY.md) A–L y Mermaid de rutas
reales. Sitio Mailerblend HTTPS200 verificado; envío navegador/GA4 pendiente.
Nginx: collect/healthy/fallback Serving, `/gtm/` selecciona Preview por cabeceras;
no se copió `/preview/` de CT614. Serving/Preview healthy, salud local/pública200;
Node1.10.2:9100/cAdvisorv0.60.6:8085 up1, sonda collect1/HTTP200, Prom/AM ready.
Clasificación prod por tags; 2CPU/2048MiB/Ubuntu22.04.5, disco10G real/16GiB declarado.
Compose local conserva curl histórico; activo usa overlay Node. Discrepancias
solo documentadas. Backups D048 presentes; no nueva restauración ni eventosGA4.
[Notes IaC](../../services/infra-mailerblend-edge/NOTES.md) aplicadas: plan dirigido
solo description615, tags intactos; lectura exacta y segundo plan cero cambios.
Boot/contenedores/Compose/Nginx y estado Terraform de otros recursos sin cambios.
14tests locales y controles de generación/fmt/validate/enlaces PASS. Issue#1 ampliada
con segundo caso615/perfil Preview, sin duplicados ni automatizar reinicios.
[Evidencia](evidence/2026-11-06-d049-result.json),
[operación Notes](../../services/infra-mailerblend-edge/NOTES-IAC.md).
F4 exporters17/17 conservado; F7 documental en curso. Sin commit/push.
Siguiente: revisión del propietario; ejecución detenida, no avanzar a otroLXC.

## D-048 — CT615 sGTM recuperado — DONE

Preview y Serving healthy; healthz18092/18091 y público200. Caducidad del bootstrap
con alta confianza:50días, configuración válida/igual y diagnóstico de edad coherente.
Checker Node sobre Compose ACTIVO; mismo digest/env/secretos/puertos/montajes/recursos.
**1 recreación Preview + 1 Serving**, cero adicionales; segunda aplicación sin
recreaciones, OOMdeltas0 y sin errores graves de arranque detectados.
Recuperador D044 reutilizado con perfil615; Nginx Preview usa `/gtm/` con cabecera
de selección, no `/preview/`. Ruta y parámetros conservados, sin cambiar Nginx.
Backups CT/PVE/externo verificados antes de intervenir.17Node/17cAdvisor/11BlackboxUP,
Prom/AM ready, sonda Mailerblend frescaHTTP200; Telegram132/56 sin errores nuevos.
21tests pertinentesPASS. Ejecución productiva68.444s; sin vigilancia redundante.
[Procedimiento/evidencias](CT615-SGTM-D048-RECOVERY.md). No otrosLXC modificados,
Terraformapply, reiniciosautomáticos, eventosGA4, commits ni pushes.
F4exporters17/17 conservado; el503 preexistente de615 queda resuelto (sustituye
estado de salud histórico D041). GA4endtoend/prevención Issue#1 pendientes.
Inventario local actualizado; Notes615 generadas NOaplicadas a Proxmox.
Siguiente: revisión del propietario; ejecución detenida, sin otroLXC autorizado.

## D-047 — ficha individual CT614 y Notes — DONE

[Inventario técnico principal](../inventory/614-LXC-INVENTORY.md): secciones A–L,
diagrama Mermaid, arquitectura/rutas, versiones por métricas/digest, operaciones,
backups y límites. El inventario general solo enlaza su ficha; no duplica CT614.
Lectura limitada a CT614 y sus dependencias directas Nginx/Prometheus/Blackbox.
Confirmado: 2 CPU, 2048 MiB, Ubuntu22.04.5, rootfs10G; Serving/Preview healthy,
healthz local/público200. Node1.10.2:9100, cAdvisorv0.60.6:8085, targets UP y dos
probes collect200. `/orbit/healthz` y `/orbit/ingest` son rutas exactas a CT617;
no se consultó ese CT. DNS/TLS actuales documentados, sin cambios.
Discrepancias documentadas: disco16GiB declarado/10Greal, Compose histórico distinto,
labels monitorización diferentes; no corregidas. GA4 y prevención automática pendientes.
Notes resumidas aplicadas por plan exclusivo description614, tags conservados;
verificación exacta y segundo plan cero cambios. Boot/contenedores/Compose/Nginx y
estado Terraform de otros recursos intactos.12tests y validaciones locales PASS.
Sin eventosGA4, reinicios, recreaciones, secretos, commits ni pushes.
[Evidencia](evidence/2026-11-06-d047-result.json). F4exporters17/17 conservado;
F7 documental en curso. Siguiente: revisión del propietario; ejecución detenida,
sin avance automático a otro LXC.

## D-046 — Notes CT 614 aplicadas — DONE

Trabajo limitado a infra-nucleoedge y lectura de su ruta Nginx. Serving/Preview
healthy y healthz local/público 200. Notes específicas en formato Purpose,
Environment, Network, Applications, Dependencies, Monitoring, IaC y Known Issues;
fuente versionada `services/infra-nucleoedge/NOTES.md`, integrada en generador y
plantilla Terraform. Production confirmado por propietario. Sin secretos.
Plan dirigido: 1 update de description de CT614; tags conservados por var-file
acotado. Apply PASS, Notes exactas verificadas y segundo plan sin cambios.
Configuración PVE salvo description, boot ID, contenedores y Compose intactos;
estado de otros recursos Terraform idéntico, sin investigar otros LXC.
11 tests, generación, fmt/validate y diff-check PASS. Sin commit/push.
[Fuente y procedimiento](../../services/infra-nucleoedge/NOTES-IAC.md),
[evidencia](evidence/2026-11-06-d046-result.json).
D045 global sigue sin aplicar: solo CT614 tiene Notes nuevas. F4 exporters17/17
no reabierto; F7 documental en curso. Siguiente: revisión por propietario, sin
continuación automática ni nuevos cambios autorizados.

## D-045 — inventario IaC preparado; Notes BLOCKED por tags

Issue sGTM creada: [#1](https://github.com/eduardo152030/mailerblend-platform-infra/issues/1),
sin automatizar reinicios. Inventario de 17 LXC generado desde recursos declarados,
metadatos funcionales y observaciones PVE/Docker/Nginx fechadas. Campos no
confirmados explícitos; fichas Markdown y Notes comparten fuente y plantilla.
9 pruebas PASS, schema/referencias/secretos y Terraform fmt/validate PASS.
Plan completo: 17 updates de **description y tags**, sin creación/destrucción;
**NO apply**, conforme al límite autorizado. Todas las Notes de producción siguen
originales. 17/17 boot IDs, configuración PVE comprobada e identidades/arranques/
reinicios de todos los contenedores sin cambios. Trabajo previo preservado.
F4 exporters conserva cierre 17/17; documentación transversal F7 en curso.
[Inventario](../inventory/LXC-INVENTORY.md), [operación y bloqueo](../inventory/README.md),
[evidencia](evidence/2026-11-06-d045-result.json). Sin commit/push.
Siguiente paso requiere autorización: conservar tags reales mediante override
propuesto existente y generar nuevo plan estrictamente de Notes antes de aplicar.

## D-044 — CT 614 recuperado — DONE

Preview y sGTM healthy; `/healthz` local y público HTTP 200. Healthcheck Node
aplicado mediante overlay sobre Compose activo; misma imagen, variables, puertos
y recursos. Backups privados verificados en CT/PVE/fuera del host, idempotencia
PASS y sin nuevos OOM. Prom/AM disponibles: 17 Node/17 cAdvisor/11 Blackbox UP;
sondas collect nuevas HTTP 200 y sin incremento de errores Telegram.
Hubo reintentos por defectos del script: 7 recreaciones Preview y 4 principal,
incluidos rollbacks; corregidos y registrados. No cambios de proxy/DNS/Cloud/sondas.
F4 exporters conserva 17/17. Prevención de caducidad semanal solo propuesta;
no timers ni reinicios automáticos instalados. Sin commit/push.
[Resultado, riesgos y recuperación](CT614-SGTM-D044-RECOVERY.md).
Siguiente paso: revisar mantenimiento periódico; no ejecución automática adicional.

## D-043 — CT614sGTM diagnosticado; NOcorrección aplicada — 2026-11-06 22:05 CET

Saludnativa503enmain/Preview,checkerpropioexit1;rutaspúblicas a614:8091/8092confirmadas.
Bootstrapcaducado fuertementecorroborado:50díasactivo,diagnósticonativo>30<60días,
Googlehealth503alvencertemporizador. Configestructuralválida/igual,mainrefresca<5min.
Además,healthcheckDockerusacurlinexistente y`/`incorrecta. OverlaynativoNodepreparado,
validaciónCompose:solohealthchecks; noimagen/env/puertos/recursos. Propuesta mínima:
recreacióncontroladaconmismaimagen/config,Previewprimero;requiereautorización.
Blackboxactual200/success1ambassondas,24hsinfallos;alertahistórica2novconHTTP0,
noatribuir aHEAD. Sondasactivasintactas;no aceptar503 comosaludable. EntregaGA4no
certificada;ningúneventoGA4válidoenviado. F4exporters17/17conservado,sinrepetir.
[Diagnóstico/procedimiento](CT614-SGTM-D043.md). Sinreinicios/producción/Cloud/DNS/router/
commit/push. Complementosdeprobesopcionalesdiferidos,NOaplicados.


## D-042 — consolidación Git — 2026-11-06T21:20:11+01:00

F7-01 DONE para IaC de monitorización curada: push normal SSH confirmado de cinco
commits nuevos y cuatro previos; origin/main y main iguales en `44c0e8b` tras ese
push (0ahead/0behind). Cierre documental separado, con verificación final en sesión.
425 rutas versionadas en el push principal,230 tests y validadores Prom/AM PASS;
cero hallazgos de secretos nuevos en selección/historial saliente. Respaldo privado
verificado. Árbol no limpio: EVA funcional y aplicaciones Gestoría/Journal
conservadas fuera del alcance; secretos/estado locales ignorados. F7 global
IN PROGRESS, F7-04 y rotación de secretos históricos pendientes; F4exporters17/17
conservado, no nueva validación productiva. Sin despliegues ni reinicios.
[Informe](GIT-CONSOLIDATION-D042.md), [evidencia](evidence/2026-11-06-git-consolidation.json).
Siguiente paso: rotación de secretos históricos y revisión separada de cambios
de aplicaciones; F5/F6 y complementos siguen pendientes.

## D-041 cerrado — 2026-11-06 21:08 CET

**Cobertura de exporters Fase4: DONE —17/17 LXC aceptados técnicamente.**
617/618/615/614DONE;180/300/180/180s,32muestrasCPU/RAM/Docker válidas,
backups/idempotencia yno nuevosOOM/reinicios.13aceptadosprevios intactos,sinrepetir.
615/614siguenHTTP503preexistente: monitorizaciónaceptada,aplicacionesNOsaludables.
CRM3.27.4/DB/datos/duplicadosdetenidos/recursosconservados. Sinrelajartolerancias.
17Node/17cAdvisor/11BlackboxUP;17cadenas;Prom/AM yconfig/secretoTelegramintactos;
0erroresnuevosTelegram,canalD039reutilizado,sin nuevaentrega niconfirmaciónhumana.
16backups y12inputs/CT verificados.24testspertinentesPASS. Tiempo:17.1min.
0BLOCKED/0PENDING deexporters; incidencias deapps ycomplementosheredados abiertos.
AlertasF5,dashboardsF6,seguridadF7 NOcompletados. VigilanciaProm/AMcontinúa;
sin atribuir `for` no probado. PolíticaCOMPLETED/permisosvacíos;ejecución detenida.
SinTerraformapply,commit/push niborrados. [Cierre](EXPORTERS-D041-CLOSURE.md),
[prueba17/17](evidence/2026-11-06-d041-final.json). Próximo: revisión/alcanceF5,
sin ejecución automática ni nuevoCT.

## Historial D-040 y anteriores

## D-040 — tiempos de próximas observaciones — 2026-11-06 20:01 CET

Convencionales/Grafana/Blackbox180s(7muestras),CRM/EVA300s(11),Prom/AM600s(21),
a30s. Ventana fijada al inicio; no modificar intervenciones iniciadas ni repetir
los13aceptados. Mantener todoslosgatesCPU/RAM/Docker/exporters/apps/OOM/reinicios,
Prom/AM/Telegram ybackup/rollback. Vigilancia posterior automática existente en
Prometheus/Alertmanager, con anomalías en estado/historial de alertas ynotificaciones;
sin espera900s adicional. No atribuir reglasfor cuyo período no haya transcurrido.
Generador ydriver conectados aconfiguración porCT;17pruebas afectadasPASS.
No procesos activos ni CT autorizado sin intentar:13DONE/4BLOCKED(617/615/614/618).
Sin cambiosproducción,observacionesrepetidas,commit/push. Reentrada de bloqueados
requiere alcance específico; no se deduce de este cambio detiempos.
[Perfiles](VALIDATION-PROFILES.md), [configuración](../../services/common/phase4-validation-profiles.yml).

## Historial D-039 y anteriores

## D-039 cerrado — 2026-11-06 19:46 CET

**Fase4 IN PROGRESS:13DONE/4BLOCKED/0PENDING sin intentar. Ejecución detenida.**
NuevosDONE:622EVA,611Grafana,616Blackbox,610Prometheus;600s/21muestras cadauno,
CPU/RAM/Docker válidas,backup/idempotencia,apps yrecursos sinregresión,nuevosOOM0.
618CRM BLOCKED/ROLLED BACK porbracketRAMvolátil del propio cAdvisor; originales,
Budibase3.27.4/duplicadosdetenidos/DB/volúmenes ycheckpoint restaurados. SKIPseguro
trasaislamiento; no reintento.617/615/614sinintervención. No relajarumbrales.
Prom/AM sanos,17Node/17cAdvisor/11BlackboxUP,13cadenas. TelegramR6/R7API+4,
0erroresnuevos; sinconfirmaciónhumana. AMconfig/secreto intactos,históricoprevio
accesible; observaciónexterna61023muestrascorrectas,independiente dePromAPI.
16backups deDONE revalidados;25tests pertinentesPASS. Tiempo:17.1min.
PolíticaCOMPLETED/permisosvacíos; sinotrosCT,Tfapply,commit/push ni borrados.
Siguientepropuesta:617→618 individualmente;615/614 aplazados,baseline503 permitido
si monitorizaciónválida/sinregresión. Noejecutar sin nuevoalcanceautorizado.
[Consolidado](CRITICAL-D039-EXECUTION.md), [prueba final](evidence/2026-11-06-d039-final.json).

## Historial D-038 y anteriores

## D-038 — perfiles simplificados; grupo STANDARD vacío — 2026-11-06 17:32 CET

**Fase4 IN PROGRESS:9DONE/3BLOCKED/5PENDING. Sin despliegues nuevos.**
STANDARD180s/7, sinwatch900s ni rollback real repetido cuando existe prueba
compatible; CRITICAL600s/21 con continuidad/recuperación específicas. Aplicación
contra baseline,sinregresión; unhealthy previo no veta aceptación de monitorización.
Telegram real porlote/cambio deconfiguración,AMready y errores estables porCT.
Tolerancias eidentidad/frescura intactas; no sustituir ausentes por0.
Perfiles y evaluación preparados localmente;25pruebas afectadasPASS. No se repiten
pruebas comunes ni compatibilidad larga deaceptados. No se certifica el ejecutor
histórico como nuevo ejecutorSTANDARD; su adaptación requiere un objetivo autorizado.
Verificación actual porlectura:9cadenas sanas,9runtimesaceptados intactos,
17Node/17cAdvisor/11BlackboxUP,Prom/AMready200;Telegram56fallos históricos sin aumento.
Pendientes:618CRM,622EVA,611Grafana,616Blackbox,610Prometheus: **todosCRITICAL**.
Cero convencionalesPENDING autorizados; no modificar617/615/614. Política cerrada,
permisosvacíos. No cambiosproducción/apps/DB/recursosPVE ni commit/push.
Siguiente grupo recomendado:618→622; después611→616→610. Requiere autorización
específica, no concedida aquí. Tiempo:17.1min.
[Perfiles](VALIDATION-PROFILES.md), [plan](evidence/2026-11-06-d038-plan.json),
[lectura producción](evidence/2026-11-06-d038-production-check.json).

## Historial D-037 y anteriores

## D-037 cerrado — 2026-11-06 16:38 CET

**Fase 4 IN PROGRESS: 9 DONE, 3 BLOCKED, 5 PENDING. CT 61211 DONE. Ejecución detenida.**
Reentrada exclusiva svc01 con framework D036 `framework-347ef93c2fca` aplicado
mediante IaC: Node Exporter 1.10.2 y cAdvisor 0.60.6 fijados por digest.
80 pruebas locales PASS y compatibilidad fresca de lectura 8/8 antes de intervenir.
Preflight, backups externos/PVE, promtool, rollback coordinado real y reaplicación
idempotente PASS. Inicial 13 muestras/360,188s; vigilancia 31/901,755s; 44 muestras
CPU/RAM válidas de cuatro contenedores, mismo ID/generación/ámbito y tiempos alineados.
NocoDB HTTP200 y PostgreSQL ready; sin nuevos OOM ni reinicios inesperados.
Prometheus/Alertmanager sanos; 17Node/17cAdvisor/11BlackboxUP y nueve cadenas correctas.
Telegram FIRING/RESOLVED aceptados porAPI (+2 envíos,0 errores); recepción humana
no confirmada. Ocho aceptados y procesosProm/AM sin cambios de identidad/reinicio;
CT614 sigue503 preexistente, originales/config intactos y dependencia independiente.
Cuatro backups legibles y hashes locales/PVE verificados; doce inputs coinciden conIaC.
No se ampliaron márgenes ni se desactivaron comprobaciones.
Política COMPLETED, permisos vacíos y avance automático deshabilitado. NoR6/R7 ni
otrosCT, sin Terraformapply/commits/push. Originales, candidatos, backups y HALTs conservados.
Tiempo al cierre documental: 38.0min excluyendo el intervalo sin actividad
registrado de 145.9min; procedimiento productivo25,3min.
[Informe](CT61211-D037-EXECUTION.md), [aceptación](evidence/2026-11-06-d037-completion.json),
[tiempo](evidence/2026-11-06-d037-time.json). Próximo paso: revisión y autorización
separada del siguiente grupo; no ejecutar automáticamente.617/615/614 quedan para recuperación.

## Historial D-036 y anteriores (no autoriza nuevos despliegues)

## D-036 cerrado — 2026-11-06 13:29 CET

**Fase 4 IN PROGRESS: 8 DONE, 4 BLOCKED, 5 PENDING; sin cambios de producción.**
Framework CPU/RAM común corregido y probado: parser único RFC3339Nano, identidad
completa con ámbito LXC/namespace (hay IDs clonados entre motores), unidades,
validación de valores/historial y lector vivo. RAM sin interpolación; CPU conserva
sus extremos y ventanas. Márgenes y frescura intactos; sin fallback ni ceros ficticios.
80 pruebas locales PASS. Compatibilidad final de lectura **8/8**, 147 muestras
válidas sobre31 contenedores,56 inputs y DockerIDs/StartedAt/restarts intactos;
recursos PVE verificados,17Node/17cAdvisor/11BlackboxUP y ocho cadenas sanas.
Se conserva rechazo inicial de frescura/futuro625 sin muestra completa; la segunda
pasadaPASS no elimina ese antecedente ni demuestra su causa. No cambiar su perfil.
Preparación61211 `framework-347ef93c2fca` solo local; auditoría fresca,
run/checkpoint nuevos y alcance autorizado requeridos antes de reentrada.
No exporters/reinicios/apps/recargas/Telegramtests/Terraformapply/commits/push.
PolíticaBLOCKED y HALTs/backups preservados. Tiempo:17.1min.
[Informe y procedimiento](VALIDATION-FRAMEWORK.md). Siguiente paso: revisar y
reintentar exclusivamente61211 en otra intervención; no otrosCT ni reparar614.

## Historial anterior a D036


## D-035 cerrado — 2026-11-06 12:24 CET

**Fase4 IN PROGRESS:8 DONE,4 BLOCKED,5 PENDING. HALT GLOBAL;61211 revertido.**
PolíticaA/B/C/D implementada:614 esBLOCKED / PRE-EXISTING ISSUE,503 previo,
originales/config intactos e independencia crítica verificada de61211 (DBlocal).
Se ejecutó solo61211: preflight/backups/promtool/fuentesLXC-Docker, rollback e
idempotenciaPASS; inicial13/360.225s yTelegramAPI+2/0errores.
Watcher31/903.637sFAIL desde60,025s: lectorRAMcomún terminó por
parseoRFC3339Nano con5decimales; no se demuestra error contable del exporter.
Rollback final verificado: originales/apps/config61211, checkpointProm8/24archivos,
backups externo/PVE, loggersdetenidos, ocho aceptados/Prom/AM intactos,17/17/11UP,
OOMdelta0. NoDONE ni9/17. Correcciónparser yregresión0–9decimales solo local,
NO desplegada ni reintentada.52 pruebas pertinentesPASS; sin commits/push.
PolíticaBLOCKED, permisosvacíos, HALTs/backups/candidatos conservados; noR6/R7.
Tiempo:17.1min. [Cierre61211](CT61211-D035-EXECUTION.md),
[política](SKIP-AND-CONTINUE.md), [cola](../../services/common/phase4-recovery-queue.yml).
Próximo objetivo: revalidar correccióncomún y reentrada exclusiva61211 tras revisar
HALT;614 no debe repararse para continuar un CT independiente. No617/615 ahora.

## Historial previo aD035


## D-034 cerrado — 2026-11-06 11:35 CET

**Fase4 IN PROGRESS:8 DONE,3 BLOCKED,6 PENDING. Lote: HALT GLOBAL.**
SKIP AND CONTINUE implementado mediante política/driver versionados, un intento por
CT y clasificación cerrada. Orden autorizado614→61211,617/615 aplazados.
CT614 falla preflight:sgtm ysgtm_preview originalesunhealthy, /healthy503 en8091/8092.
Originales/appIDs/config preservados y cobertura previa íntegra, pero no se puede
confirmar **aplicación original funcionando**. Ese requisito explícito de D034
veta el salto, incluso sin cambios activos. No se inició61211.
Sin staging remoto, backups nuevos, apply, recargaProm ni reinicios. Cobertura
17Node/17cAdvisor/11Blackbox y ocho cadenas sanas;24 archivosProm sin cambios,
identidades de ocho aceptados yProm/AM intactas. OOMdelta614=0; sin nuevos errores
Telegram en contraste de contadores; no prueba nueva de entrega.180s/900s,
idempotencia/rollback real y métricas de candidatos NO ejecutados por fallo previo.
Política BLOCKED, permisos vacíos, HALTs conservados, sin procesos de avance.
36 pruebas pertinentes PASS. Sin commits/push. Tiempo:17.1min.
[Cierre y evidencia](SKIP-AND-CONTINUE.md), [cola](../../services/common/phase4-recovery-queue.yml).
Siguiente objetivo recomendado:61211, tras resolver el veto de aplicación de614.
No investigar ni intervenir617/615 ahora, noCRM/EVA/Grafana/Blackbox/exporters610.

## Historial de cierres anteriores


## D-033 cerrado — 2026-11-06 11:15 CET

**Fase4 IN PROGRESS:8 DONE,2 BLOCKED,7 PENDING. CT617 BLOCKED / ROLLED BACK.**
Run `integration-20261106T100830Z`. Primer apply rechazado por guarda `Held candidate differs`:
el proyectoCompose nuevo seguía consultando el nombreheld histórico. Se detuvo
Node original transitoriamente; no se creó ningún exporter nuevo. Recuperación
coordinada verificada: originales/apps/config intactos, proxy403/backend200,
checkpointProm8 y24/24 archivos exactos, ocho aceptados sin cambios,17/17/11 UP.
Sin nuevosOOM ni reinicios de apps; loggers CPU/RAM detenidos, backups conservados.
**600s/900s, idempotencia y cadenaTelegram NO ejecutadas** por fallo previo; no DONE.
Prom/AM ready200; ningún testTelegram nuevo. Corrección de nombresheld por revisión
más regresión apply→rollback→reapply/idempotencia preparada **solo local**, no aplicada.
27 pruebas pertinentes PASS. Política BLOCKED sin permisos de apply/recovery ni
continuación automática; HALTs históricos y nuevo preservados. No615 ni otrosCT,
sin commits/push. Tiempo:8.0min; ver [cierre617](CT617-D033-EXECUTION.md).
Próximo paso: revisar corrección local de aislamientoheld y autorizar otra reentrada
exclusiva617 si procede; no reutilizar este run ni declarar RAM validada en617.


## Seguimiento D-032 — 2026-11-06 10:35 CET

Fase4 IN PROGRESS. **8 DONE,2 BLOCKED,7 PENDING sin cambios de producción.**
Diagnóstico617 y código local preparados; despliegue NO autorizado en esta tarea.
Defecto confirmado: RAM cacheada comparada con lectura actual. Causa única del
fallo histórico no demostrable sin RAM histórica equivalente; no atribuir error
a cAdvisor. 480 lecturas617 Docker/cgroup coincidentes; control623 cinco
contenedores alineados PASS;44 pruebas locales PASS. Ocho aceptados y56 inputs
intactos,17/17/11 up y cadenas sanas. CT623 Node real1.11.1 (errata textual anterior).
Política BLOCKED/HALTs conservados; no615 ni reinicios/despliegues/commits/push.
[Diagnóstico y procedimiento617](CT617-RAM-RCA.md). Próximo paso: revisión del
diagnóstico y autorización exclusiva617 antes de habilitar la ejecución.


Actualizado: 2026-11-03 (Europe/Madrid). Fuente central de seguimiento para Proxmox,
Terraform, Docker Compose, Prometheus, Alertmanager, Telegram, Grafana y aplicaciones.
Para retomar el trabajo, leer primero [CURRENT-STATUS](CURRENT-STATUS.md) y después
la fase activa. Las decisiones están en [DECISIONS](DECISIONS.md).

## Estado real

| Fase | Objetivo y alcance | Estado | Implementación / producción / aceptación |
|---|---|---|---|
| [1. Monitoring Foundation](phases/01-monitoring-foundation.md) | Base Prometheus/Alertmanager, persistencia y discovery | DONE | Base desplegada y verificada por API; cobertura completa y calidad quedan en F4 |
| [2. Telegram Alerting & Blackbox Deduplication](phases/02-telegram-blackbox.md) | Entrega FIRING/RESOLVED y evitar incidentes equivalentes | DONE | Desplegada, entrega confirmada por propietario, 11 sondas aceptadas |
| [3. Infrastructure Recovery — CRM & EVA](phases/03-infrastructure-recovery.md) | Recuperar capacidad/servicios preservando datos | **DONE — Accepted with UAT Waiver** | Ejecutada y técnicamente validada; aceptación formal del propietario el 2026-11-02 |
| [4. Exporters & Monitoring Coverage](phases/04-exporters-coverage.md) | Métricas correctas y cobertura de los17servicios | **DONE — coberturaexporters** | D04117/17; complementosheredados abiertos; alertas/dashboards/seguridad no incluidos |
| [5. Alerting Optimization](phases/05-alerting-optimization.md) | Umbrales, severidad, rutas, inhibición y mensajes | **DONE — Accepted** | D050: 26 alertas/34 grabación desplegadas; 17/17/11; cadena FIRING/RESOLVED recibida y clara, idempotencia y rollback verificados |
| [6. Grafana & Dashboards](phases/06-grafana-dashboards.md) | Dashboards útiles con datos y ámbitos correctos | IN PROGRESS | Fleet17/17 desplegado D057, uptime real y salud completa; aceptación visual y otras vistas/providers pendientes |
| [7. IaC Reliability, Security & Disaster Recovery](phases/07-iac-security-dr.md) | Despliegues seguros, herramientas reproducibles y DR sostenido | TODO | Hay mejoras parciales desplegadas; faltan seguridad global, CI, política DR y cierre Git |

Cada ficha contiene objetivo, alcance, dependencias, tareas, riesgos, entregables,
criterios de aceptación y evidencias. DONE se refiere al alcance definido, no implica
que hayan desaparecido todos los problemas heredados del proyecto.

## Numeración histórica

No renombrar evidencias ni perder sus referencias:

| Documentación anterior | Fase central actual |
|---|---|
| “Fase 1” de [DEDUPLICATION.md](../../services/infra-prom/DEDUPLICATION.md) | Fase 2 |
| “Fase 2” de [PHASE2-INCIDENTS.md](../../services/infra-prom/PHASE2-INCIDENTS.md) y [PHASE2-EXECUTION.md](../../services/infra-prom/PHASE2-EXECUTION.md) | Fase 3 |
| Investigación de aislamiento LXC y Docker | Fase 4 |
| Antiguas propuestas de optimización / documentación | Redistribuidas entre F5 y F7 |

## Cómo se actualiza

1. Identificar fase/tarea y autorización antes de actuar. Registrar ampliaciones.
2. Separar cuatro hitos: **local**, **validado**, **desplegado**, **aceptado**.
3. Usar TODO, IN PROGRESS, BLOCKED o DONE. Documentar causa y salida de un bloqueo.
4. Vincular resultados fechados y criterios, sin secretos. Los JSON de auditoría son
   instantáneas, no garantías permanentes de disponibilidad.
5. Al finalizar, actualizar ficha, este índice, CURRENT-STATUS y decisiones nuevas.
6. Revisar Git y enlaces. No confundir cambios sin commit con evidencia de producción.
   El [inventario de trabajo previo](WORK-AUDIT.md) distingue cambios locales y runtime.

La aceptación de F3 dispensa expresamente la UAT manual adicional; **no demuestra que
todos los flujos funcionales hayan sido probados**. Los tres healthchecks heredados,
el digest diario de EVA y Nucleotecnológico continúan registrados como pendientes.

## Próxima puerta — cobertura17/17 cerrada D-041

SinCTpendientes ni bloqueados demonitorización. RevisaralertasF5 ycomplementos
heredados antes deuna nuevaautorización.615/614503 ylosotrosINC siguen registrados,
no reparados por elrollout. No repetir aceptados ni continuar--all.
[Handoff](PHASE4-HANDOFF.md), [cierre](EXPORTERS-D041-CLOSURE.md).
