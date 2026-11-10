# Matriz de cobertura — estadoD041

ActualizaciónD059,2026-11-09:17/17exportersaceptadosD041 yactualmenteUP,
18 Blackbox UP; Journal funcional periódicoD054/D057 yhealthchecks D051resueltos.
Estado/uptimeCT desdePVE D056. ScrapeGrafanaausente; hostcompleto pendiente.
[Estado vigente](../CURRENT-STATUS.md), [evidencia](../evidence/2026-11-09-d059-documentation-audit.json).
Las tablas inferiores fechadasD025/D021sonhistóricas; sus pendientes fueron
sustituidos porD041yD051–D058. La coberturaexportersno certificaUATdenegocio.

Registro validado:17/17. CoberturaexportersDONE; complementosabiertos. [Ejecución](../AUTONOMOUS-EXECUTION.md).

| CT | Estado | Evidencia |
|---|---|---|
| 624 | PASS — fuente y cadena verificadas | [prueba](../evidence/2026-11-02-pilot624-summary.json) |
| 626 | PASS — fuente y cadena verificadas | [prueba](../evidence/2026-11-02-journal626-execution.json) |
| 625 | PASS — fuente y cadena verificadas | [prueba](../evidence/2026-11-02-journal625-execution.json) |
| 613 | PASS — fuente y cadena verificadas | [prueba](../evidence/2026-11-02-r1-execution.json) |
| 621 | PASS — fuente y cadena verificadas | [prueba](../evidence/2026-11-02-rollout-621.json) |
| 620 | PASS — fuente y cadena verificadas | [prueba](../evidence/2026-11-02-rollout-620.json) |
| 619 | PASS — fuente y cadena verificadas | [prueba](../evidence/2026-11-02-rollout-619.json) |
| 623 | PASS — fuente y cadena verificadas | [prueba](../evidence/2026-11-02-rollout-623.json) |
| 617 | DONE D041 — fuente/cadena; appsinregresión,503preexistente615/614conservado | [prueba](../evidence/2026-11-06-d041-final.json) |
| 615 | DONE D041 — fuente/cadena; appsinregresión,503preexistente615/614conservado | [prueba](../evidence/2026-11-06-d041-final.json) |
| 614 | DONE D041 — fuente/cadena; appsinregresión,503preexistente615/614conservado | [prueba](../evidence/2026-11-06-d041-final.json) |
| 61211 | PASS — fuente y cadena verificadas | [prueba](../evidence/2026-11-02-rollout-61211.json) |
| 618 | DONE D041 — fuente/cadena; appsinregresión,503preexistente615/614conservado | [prueba](../evidence/2026-11-06-d041-final.json) |
| 622 | PASS — fuente y cadena verificadas | [prueba](../evidence/2026-11-02-rollout-622.json) |
| 611 | PASS — fuente y cadena verificadas | [prueba](../evidence/2026-11-02-rollout-611.json) |
| 616 | PASS — fuente y cadena verificadas | [prueba](../evidence/2026-11-02-rollout-616.json) |
| 610 | PASS — fuente y cadena verificadas | [prueba](../evidence/2026-11-02-rollout-610.json) |

<!-- D025 historical snapshot below -->

La tabla siguiente es histórica (auditoría inicial), no el estado actual.

# Matriz de cobertura — Fase 4

Snapshot de solo lectura del 2026-11-02 (Europe/Madrid). Fuentes:
[runtime](../evidence/2026-11-02-runtime-final-readonly.json),
[Prometheus](../evidence/2026-11-02-monitoring-audit.json) y
[HTTP/API](../evidence/2026-11-02-supplementary-audit.json).
Los valores de CPU/RAM de la tabla proceden de Proxmox real, no de Node Exporter.
Actualizaciones posteriores: CT 624 [piloto aceptado](../PILOT-624.md) y CT 626/625
[lote validado](../JOURNAL-EXECUTION.md).
Las demás filas conservan el snapshot inicial; no implican una nueva auditoría.

| Servicio | CT | IP | CPU / RAM MiB reales | Node instalado / scrape | cAdvisor instalado / scrape y calidad | Aplicación / contrato |
|---|---|---|---|---|---|---|
| infra-blackbox | 616 | 192.168.1.116 | 1 / 512 | sí / sí; CPU/RAM del PVE | sí / sí; sin series Docker individuales | Exporter scrape disponible; probe_success es otro contrato |
| infra-composable-crm | 618 | 192.168.1.118 | 2 / 6144 | sí / sí; CPU/RAM del PVE | sí / sí; sin series Docker individuales | Verificaciones F3 aceptadas; 2 healthchecks heredados abiertos |
| infra-eva-assistant-bot | 622 | 192.168.1.122 | 2 / 2048 | sí / sí; CPU/RAM del PVE | sí / sí; sin series Docker individuales | Verificaciones F3 aceptadas; Focalboard/digest pendientes |
| infra-excraper | 620 | 192.168.1.120 | 2 / 2048 | sí / sí; CPU/RAM del PVE | sí / sí; sin series Docker individuales | Contrato funcional a completar; no inferirlo de up |
| infra-gestoria | 623 | 192.168.1.123 | 2 / 4096 | sí / sí; CPU/RAM del PVE | sí / sí; sin series Docker individuales | Contrato funcional a completar; no inferirlo de up |
| infra-grafana | 611 | 192.168.1.111 | 1 / 1048 | sí / sí; CPU/RAM del PVE | sí / sí; sin series Docker individuales | /api/health y /metrics = 200; sin job Grafana |
| infra-hola | 613 | 192.168.1.113 | 1 / 512 | sí / sí; CPU/RAM del PVE | sí / sí; sin series Docker individuales | Contrato funcional a completar; no inferirlo de up |
| infra-journal-api | 626 | 192.168.1.126 | 2 / 2048 | sí / no; RAM LXCFS, CPU cgroup validada | sí / no; 4 Docker individuales, 0.60.6 validado | GET :3000/health = 200; identidad/config intactas |
| infra-journal-db | 625 | 192.168.1.125 | 2 / 2048 | sí / no; RAM LXCFS, CPU cgroup validada | sí / no; 4 Docker individuales, 0.60.6 validado | pg_isready=0; no acredita integridad SQL |
| infra-journal-web | 624 | 192.168.1.124 | 1 / 512 | sí / no; RAM LXCFS, CPU cgroup validada | sí / no; 4 contenedores individuales validados, v0.60.6 | GET :8090/ = 200 sin cambios; piloto técnico validado |
| infra-mailerblend-edge | 615 | 192.168.1.115 | 2 / 2048 | sí / sí; CPU/RAM del PVE | sí / sí; sin series Docker individuales | Contrato funcional a completar; no inferirlo de up |
| infra-nucleoedge | 614 | 192.168.1.114 | 2 / 2048 | sí / sí; CPU/RAM del PVE | sí / sí; sin series Docker individuales | Contrato funcional a completar; no inferirlo de up |
| infra-orbit | 617 | 192.168.1.117 | 1 / 512 | sí / sí; CPU/RAM del PVE | sí / sí; sin series Docker individuales | Contrato funcional a completar; no inferirlo de up |
| infra-project-gestion | 621 | 192.168.1.121 | 2 / 2048 | sí / sí; CPU/RAM del PVE | sí / sí; sin series Docker individuales | Contrato funcional a completar; no inferirlo de up |
| infra-prom | 610 | 192.168.1.110 | 2 / 2048 | sí / sí; CPU/RAM del PVE | sí / sí; sin series Docker individuales | Prom/AM readiness 200; self-scrapes presentes |
| infra-pulpo | 619 | 192.168.1.119 | 2 / 2048 | sí / sí; CPU/RAM del PVE | sí / sí; sin series Docker individuales | Contrato funcional a completar; no inferirlo de up |
| svc01 | 61211 | 192.168.1.112 | 3 / 6656 | sí / sí; CPU/RAM del PVE | sí / sí; sin series Docker individuales | Sonda pública base existente; no equivale a todas sus aplicaciones |

## Capas y significado

| Capa | Fuente/indicador | Qué acredita | Qué no acredita |
|---|---|---|---|
| Nodo físico PVE | Proxmox y /proc del nodo consultados por SSH | 4 CPU, memoria física y lxcfs 6.0.0-pve2 en esta auditoría | No existe aún un job dedicado PVE que permita alertar su disponibilidad |
| LXC | Configuración Proxmox/cgroup y /proc virtualizado LXCFS | Asignación y presión de recursos del CT | up del exporter no diferencia red/collector/CT apagado |
| Collector | up y scrape health | Prometheus pudo recoger /metrics | No demuestra que CPU/RAM sean del CT ni que se vean sus contenedores |
| Docker | API + CPU/RAM por identidad de contenedor cAdvisor | Visibilidad individual cuando esté validada | Una serie raíz, HTTP 200 o cAdvisor healthy no la acreditan |
| Aplicación | HTTP /health o raíz; TCP PostgreSQL según contrato | Respuesta concreta o conexión de transporte | No demuestra login, todos los flujos ni integridad SQL |

La UAT dispensada de F3 no se presenta como evidencia adicional para esta matriz.
Los originales de recuperación detenidos se mantienen para rollback: no exigir que
aparezcan como aplicaciones activas ni volver a arrancarlos para mejorar cobertura.

## Preparado frente a real

| Catálogo | Real cargado | Candidato local | Condición pendiente |
|---|---|---|---|
| Node Exporter | 14 scrapes; 3 Journal instalados/validados fuera del discovery | 17 | Migrar otros 14; contrato CPU local aceptado, activar después de validación global |
| cAdvisor | 17 scrapes; cuatro corregidos, trece legacy | 17 | Validar imagen moderna y CPU/RAM en los otros 14 CT |
| Grafana | 0 | 1 | Aprobar y recargar job; /metrics ya responde |
| Blackbox | 11 | 14 = 11 base + 3 Journal | Aprobar contratos y verificar tcp_connect efectivo; no se altera el catálogo aceptado |

La incorporación de vmid/collector_scope en los catálogos es local y puede cambiar
identidades de alertas tras el despliegue. No usar collector_scope=lxc para etiquetar
una métrica como garantía de exclusividad si proviene de un subsistema compartido.


## Integración real de CPU — D-021

Fuente fiable integrada y cadena recibida:624/626/625/613, **4/17**.
Los otros13 conservan CPUlegacy no verificada. Prometheus17 Node/17CAD/11Blackbox;
Grafana0/1 y sondasJournal pendientes. Ver [ejecución](../P0-R1-EXECUTION.md).
