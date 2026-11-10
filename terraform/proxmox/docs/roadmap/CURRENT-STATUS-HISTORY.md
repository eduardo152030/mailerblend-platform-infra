# Historial documental anterior a la consolidación D-059

Copia conservada el 2026-11-09 (Europe/Madrid). Los estados y permisos siguientes
son históricos; consultar [estado vigente](CURRENT-STATUS.md) y [roadmap](ROADMAP.md).
Las fechas UTC de evidencias se conservan.

# Estado actual del proyecto

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

## Estado real

17DONE:624/626/625/613/621/620/619/623/61211/622/611/616/610/617/618/615/614.
0BLOCKED deexporters,0PENDING derollout.615/614 mantienen503 yalertas;noapphealthy.
Losproblemas deaplicación no reabren retrospectivamente laaceptación de métricas.

## Hitos conservados

F1 y F2 DONE. Journal624/626/625 aceptados técnicamente por propietario.
**F3 DONE — Accepted with UAT Waiver:** verificaciones técnicas y restauraciones
pasaron; CRM/EVA operativos según comprobaciones. UAT manual no ejecutada y dispensada
por propietario; no demuestra todos los flujos funcionales. Ver
[PHASE2-EXECUTION](../../services/infra-prom/PHASE2-EXECUTION.md).
CRM/EVA no fueron modificados durante este lote.

## Pendientes heredados

| ID | Pendiente | Seguimiento |
|---|---|---|
| INC-001 | Healthcheck Budibase y Redis externo | F4-08 TODO |
| INC-002 | Healthcheck API CRM usa wget ausente | F4-08 TODO |
| INC-003 | Healthcheck Focalboard usa curl ausente | F4-08 TODO |
| INC-004 | Digest diario EVA, crontab/apk heredados | F7-07 TODO |
| INC-005 | Nucleotecnológico / CollectEndpointDown, RCA pendiente | Conservar sus dos sondas; no dar por reparado |
| R-001 | CoberturaLXC17/17cerrada; fuentePVE explícita aún pendiente | ComplementoF4 |
| R-002 | Promoción global del contrato CPU y compatibilidad dashboards | F4-10/13 pendiente, F6 |
| R-003 | Secretos/estado/hardening heredados | F7 TODO, no corregidos por Journal |
| R-004 | Árbol Git amplio pendiente de commits curados | F7-01, [WORK-AUDIT](WORK-AUDIT.md) |

Roadmap y decisiones siguen como fuente central; secretos y backups privados fuera de Git.

Cierre final: 2026-11-05 22:04 CET. Tiempo transcurrido registrado: 58.9 minutos (incluye observaciones y recuperación). 31 pruebas de regresión PASS; enlaces locales y `git diff --check` PASS; Prometheus/Alertmanager ready HTTP200; sin procesos activos de rollout. Sin commit/push.

CierreD032: 2026-11-06 10:56 CET. Tiempo registrado: 39.1min. Enlaces locales, secreto-signaturas y `git diff --check` PASS; sin commit/push/staging. [Validación local](evidence/2026-11-06-617-local-validation.json).
