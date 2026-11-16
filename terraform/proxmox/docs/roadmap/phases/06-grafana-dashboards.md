# Fase 6. Grafana & Dashboards

## IA-CHAT — integración desplegada y estabilidad PASS (2026-11-13, Europe/Madrid)

Fase 7. IaC Reliability, Security & Disaster Recovery; complementos de Fases 4 y 6.
Implementación y pruebas técnicas DONE: CT 630/631 adoptados en Terraform sin
recreación, plan acotado no-op y 18 entradas anteriores del estado intactas.
YAML y configuración canónica por servicio, inventario individual/global y Notes
actualizados. CPU cgroup y RAM LXCFS verificadas; Node Exporter nativo en ambos,
cAdvisor solo en 631 y cinco targets nuevos. Prometheus/Blackbox integrados de
forma aditiva; Grafana Fleet/Details contempla cAdvisor N/A en 630.

PASS: 600 segundos / 21 muestras sin anomalías, 136 consultas reales de Grafana,
reinicio de ambos CT, autenticación, chat, visión, thinking, búsqueda, RAG e historial.
Segunda aplicación sin escrituras de configuración, recargas ni reinicios.
Backup final de 631 verificado por SHA256/zstd/tar; README operativo en PVE.
27 hashes de configuración PVE protegidos iguales; CT 627 no intervenido.
Sin commits ni push.

Voz funcional con calidad limitada: small/int8, 4 de 5 palabras correctas en el WAV
sintético (WER 20 %). Con RAG/STT y exporters, 631 alcanza 2,69 GiB residentes /
2,85 GiB de working set; propuesta de 4096 MiB sin aplicar, límite de 3072 MiB
conservado. Cuenta y Knowledge técnicos retirados; primer administrador disponible.

Aceptación completa IN PROGRESS: reservas DHCP, administrador y UAT móvil/voz del
propietario. Restauración funcional y recepción Telegram FIRING/RESOLVED de las
nuevas cadenas no realizadas. No declararlas aceptadas bajo el contrato F4 ni cerrar
la Fase 7 global. Siguiente paso: propietario reserva DHCP, crea su administrador,
prueba voz/móvil y valora el margen de RAM; coordinar después la aceptación de
alertas de 630/631. [Informe vigente](../IA-CHAT-EXECUTION-2026-11-13.md).


Estado: **DONE**. Cierre: **2026-11-10 (Europe/Madrid)**, D-060.
[Roadmap](../ROADMAP.md) · [Estado actual](../CURRENT-STATUS.md) · [Decisiones](../DECISIONS.md)

## Objetivo y alcance aprobado

Fleet Overview y LXC Details útiles, con métricas reales, navegación bidireccional,
provisioning reproducible y preservación de los siete dashboards anteriores.
La solicitud D-060 establece once criterios verificables de cierre; no exige
nueva UAT de aplicaciones ni aceptación visual humana separada para cerrar.
El navegador automatizado sí se ejecutó. La dispensa de F3 no se amplía.

## Tareas

| ID | Tarea | Estado | Resultado |
|---|---|---|---|
| F6-01 | Datasource, UID y variables de las vistas entregadas | DONE | Datasource existente, selectores dinámicos, consultas de17 CT y navegador; modelos heredados conservados |
| F6-02 | Resolver mounts y providers duplicados | DONE | Dos providers únicos; receta Compose con tres mounts efectivos e imagen fijada, sin reiniciar Grafana activo |
| F6-03 | Entregar Fleet y LXC Details | DONE | Salud/uptime/recursos, Docker por LXC, aplicaciones, monitoring y alertas; navegación ida/vuelta |
| F6-04 | Validar rango, navegación y persistencia | DONE | Navegador, CT 614/615/618/613; arranque aislado del candidato final desde snapshot consistente, sin recrear producción |
| F6-05 | Documentar provisioning y recuperación | DONE | Manual, transacción acotada, backup CT/fuera PVE, restore-check, idempotencia y rollback con protección de eliminación |

## Implementación, pruebas, despliegue y cierre

Dos dashboards entregados en CT 611; nueve modelos provisionados por archivos IaC.
Los siete anteriores conservan UID, carpeta y contenido, incluidos tres exportados
antes presentes solo en SQLite. No se afirma que todas sus consultas heredadas
hayan sido auditadas de nuevo.

34 casos sintéticos relevantes, 663 consultas instantáneas en17 CT, 28 históricas,
navegador sin errores con654 frames y navegación real PASS. Comparación uptime PVE
para17 CT y tres endpoints independientes: diferencia máxima20 s, límite45 s.
Ensayo aislado final10 nov: nueve dashboards cargados, sin red ni puertos publicados,
misma imagen, candidato exacto y SQLite consistente. Grafana activo no se reinició.
Idempotencia final:0 escrituras/0 recargas/0 reinicios.

Revisión10 nov08:08 CET:17 Node/17cAdvisor/18 Blackbox y exporter PVE UP; reglas F5 y targets
conservados; sin FIRING/PENDING ni UNKNOWN en salud consolidada de los17 CT.
[Resultado final](../evidence/2026-11-10-d060-result.json).

DONE según los once criterios D060, no UAT de negocio ni afirmación de recreación
productiva. Implementado, probado y desplegado; sin commit/push por restricción
expresa. Siguiente fase: F7, sin ejecución autorizada por este cierre.

## Límites documentados

No contador fiable de reinicios Docker; estado Docker representa cgroup observado
fresco. Disco es capacidad real del filesystem, no cuota Terraform. Descripciones
de alertas muestran contrato IaC y enlazan evaluación/activeAt a Prometheus. Rutas de
inventarios locales solo si existen, sin URLs web inexistentes. Readiness y medias
de sondas no certifican UAT ni disponibilidad durante huecos. Altas necesitan
publicar inventario/targets medianteIaC; no hay despliegue automático deexporters.
Scrape propio Grafana, observabilidad completa del host y seguridad/DR/aplicaciones
siguen como complementos F4/F7; no bloquean los criterios autorizados de esta fase.

## Evidencias y operación

- [Cierre D060 y once criterios](../PHASE6-D060-CLOSURE.md).
- [Manual Fleet/Details](../../../services/infra-grafana/FLEET-OVERVIEW.md).
- [Navegador](../evidence/2026-11-09-d060-browser.json), [consultas](../evidence/2026-11-09-d060-promql.json), [uptime](../evidence/2026-11-09-d060-uptime.json).
- [Persistencia aislada](../evidence/2026-11-10-d060-recreation-replay-final-20261110.json).
- [Tiempos y revisión documental](../evidence/2026-11-10-d060-closure-validation.json).

Historial: [D052](../PHASE6-D052-EXECUTION.md),
[D053](../PHASE6-D053-APPLICATION-HEALTH-AUDIT.md),
[D054](../PHASE6-D054-STAGE-A-EXECUTION.md),
[D056](../PHASE6-D056-UPTIME-EXECUTION.md),
[D057](../PHASE6-D057-COMPLETE-HEALTH.md). Bloqueos de esas etapas resueltos según
informes posteriores; no reejecutarlos ni reutilizar permisos históricos.

## Incidencia operativa D083 — 12 de noviembre de 2026

Monitorización central recuperada tras reiniciar PVE. FIRING/RESOLVED recibidos y
confirmados; datasource Grafana OK, 18 hosts/CPU y 19 sondas. Políticas de arranque
corregidas en IaC/runtime sin recrear contenedores. cAdvisor 618/623 con latencia
intermitente, estabilidad global pendiente; CRM API 618 parada y alertada.
Aceptación histórica conservada. [Informe y pruebas](../PHASES-D083-MONITORING-RECOVERY.md).

## D088 — incidencia cAdvisor623/618 y CRM

13 de noviembre de 2026 (Europe/Madrid), DONE técnico. Recuperación autorizada
por el propietario, acotada a623/618: límite cAdvisor128→384MiB en caliente,
CPU y RAM PVE intactas; CRMAPI618 arrancado sin recreación y restartalways.
Backups/restauración aislada e idempotenciaPASS. Dashboarddesplegado indica
HEALTHY/0alertas para ambos. Observación600s/21 PASS: cero timeouts/alertas, sin OOM ni reinicios nuevos.
Siguiente: vigilancia existente; recepción humana Telegram no verificada.
[Informe y evidencias](../PHASES-D088-CADVISOR-CRM-RECOVERY.md).
No modificar aceptación previa ni dar por aceptados pendientes heredados.


## IA-CHAT — ampliación de alcance aprobada: patrón del repositorio y observabilidad

13nov2026 Europe/Madrid. El propietario solicita integración reproducible completa de
630/631 en Terraform/inventario YAML, docs/inventory, monitorización y Grafana como
el resto del pool; autoriza los cambios necesarios para ello. Aprobación limitada
a los dos CT nuevos y modificaciones aditivas de observabilidad que los incorporen,
con backup/rollback, validación e idempotencia. No rollout global de exporters,
no cambios de aplicaciones/recursos de otros CT y **627 excluido por completo**.
Sin commit/push ni aumento automático de RAM631. Mantener DHCP y reservas pendientes,
unprivileged, volúmenes/modelos y contratos CPU/RAM del repositorio.

Estado IN PROGRESS: la receta pct aislada anterior no basta como cierre del patrón
solicitado; preparar adopción Terraform sin recreación, SSH verificado si procede,
exporters apropiados para630sinDocker y631conDocker, integración aditiva enPrometheus/
Blackbox/Grafana e inventario. Conservar cambios previos ajenos. La validación devoz
sigue pendiente tras corregir WHISPER_MODEL persistido; no declararla aprobada.
