# Fase 4 — integración incremental del contrato CPU

**PREPARED / LOCALLY VALIDATED / NOT DEPLOYED.** 2026-11-02.
Preparación autorizada; presentar P0 y R1 antes de desplegar. D-020 acepta Journal;
D-021 establece la cadena completa como criterio. No hay permiso nuevo para desplegar
P0/R1 ni R2–R7 desde esta intervención.

## Estado real y decisión propuesta

Tres exporters corregidos y aceptados no equivalen a tres LXC monitorizados de extremo
a extremo. Actualmente: **3/17 fuentes CPU fiables; 0/17 cadenas CPU corregidas completas**.
Prometheus real recoge 14 Node legacy y 14 cAdvisor; Journal está fuera del discovery.
La entrega Telegram genérica se validó en F2; no demuestra la nueva cadena CPU por CT.
[Comprobación API previa](evidence/2026-11-02-incremental-live-chain-before.json):
falla como se esperaba para CT 626, sin interpretar ausencia como CPU cero.

**P0 propuesto:** integrar 624/626/625 primero, antes de migrar R1. Se genera un
candidato desde un snapshot real de /opt/infra-prom/config, no desde la configuración
global preparada que incluye otras novedades. Conserva prometheus.yml byte a byte,
los 14 targets legacy con sus etiquetas/endpoints y todos los archivos no relacionados.
Añade solo los tres Journal Node/cAdvisor y las reglas CPU/inventario necesarias.
Quedan **17 targets mixtos**, con 3 CPU corregidas y 14 pendientes; eso no completa F4.
Grafana, sondas Journal, rutas Telegram, AM, otras reglas, apps y recursos no cambian.
[Capacidad CT 610](evidence/2026-11-02-incremental-capacity.json): snapshot de solo
lectura; revalidar margen y vigilar crecimiento de series/TSDB/RAM tras añadir los
12 contenedores Docker Journal. Promtool no mide ese coste de ingestión en producción.
Las once Blackbox y sus dos contratos Nucleotecnológico se preservan.

## Registro IaC y estados separados

[exporter-migration.yml](../../services/common/exporter-migration.yml) es el registro compartido por el generador general y el incremental; no hay lista
de CT corregidos hardcoded separada:


- cpu_contract_verified: fuente/identidad/capacidad verificadas; permite promoción
  controlada. Puede ser una comprobación puntual anterior a la observación final.
- exporters_validated: estabilidad/rollback/idempotencia superados; hoy 624/626/625.
- prometheus_integrated: target, series y reglas verificados por API; hoy vacío.
- telegram_chain_verified: prueba real completa y recibida, FIRING y RESOLVED; hoy vacío.
- remaining_order: los otros 14 CT, una sola vez, manteniendo orden R1–R7.

La preparación rechaza pruebas de otro CT, manifest de solo preparación, inventario
incompleto/duplicado y estados imposibles (Telegram sin integración). No se añade
613 a fuente verificada por tener un bundle local. La evidencia puntual de R1 solo
se registrará tras Node listo, identidad/contador contrastados con el padre PVE,
capacidad 1/RAM 512 MiB y modelo/digest correctos. Su observación y aceptación final
seguirán pendientes hasta cerrar la cadena; no usar result=PASS sin esas mediciones.

| Servicio / CT | Fuente CPU actual | Prometheus CPU corregida | Cadena completa |
|---|---|---|---|
| Journal Web 624, API 626, DB 625 | cgroup verificado, exporters DONE/aceptados | TODO: P0 | TODO |
| infra-hola 613 | Legacy compartida, sin validar; R1 solo preparado | TODO | TODO |
| infra-project-gestion 621, infra-excraper 620 | Legacy compartida, pendientes | TODO | TODO |
| infra-pulpo 619, infra-gestoria 623 | Legacy compartida, pendientes | TODO | TODO |
| infra-orbit 617, infra-mailerblend-edge 615, infra-nucleoedge 614 | Legacy compartida, pendientes | TODO | TODO |
| svc01 61211 | Legacy compartida, pendiente | TODO | TODO |
| CRM 618, EVA 622 | Legacy compartida, pendientes; último lote de apps | TODO | TODO |
| Grafana 611, Blackbox 616, Prometheus 610 | Legacy compartida, pendientes | TODO | TODO |

## Reglas, ausencia y exclusión mutua

Se mantiene **HostHighCpuUsage >90%, for 10m, warning** y rate de 5m.
Fuente corregida: lxc:cpu_usage:percent = 100 × rate(consumo CPU) / cores asignados,
con las máscaras de [CPU-CONTRACT](CPU-CONTRACT.md): identidad, finitud, capacidad,
success, textfile y frescura. 1 CPU ocupada de 2 representa 50%, no 100%.
No se suma cAdvisor ni se usa machine_* para capacidad LXC.

La rama legacy conserva su cálculo/umbral/etiquetas actuales para los pendientes.
Su descripción indica **fuente compartida sin validar**. El record
lxc:cpu_migration:pending añade esa semántica sin cambiar etiquetas de los scrapes
legacy. Se excluye por job/instance/service cuando existe contrato corregido **o**
inventario esperado corregido: no hay fallback al contador físico si se pierde un label.
También se excluye el estado pending cuando quedan series legacy antiguas durante el cambio.

Las reglas generadas lxc:cpu_inventory:expected son independientes de up:

| Situación | Resultado |
|---|---|
| CPU válida y >90% sostenida | Una HostHighCpuUsage tras 10m |
| CPU válida con valor 0 | Cero real, se conserva; no alerta de CPU alta |
| Counters ausentes, viejos, NaN, infinitos, duplicados o identidad incorrecta | Sin porcentaje fabricado; LxcCpuCollectorInvalid tras 2m si up=1 |
| Target corregido desaparecido o sin label de contrato | LxcCpuTargetMissing tras 2m; rama legacy excluida |
| Exporter up=0 con contrato | HostOutOfService existente; sin alertas duplicadas de calidad |
| Pending legacy | Estado unverified explícito; no se presenta como CPU LXC fiable |

Missing-target se empareja por identidad de endpoint, no ct_id del target erróneo,
para no duplicar el error de identidad que ya detecta CollectorInvalid.
Frescura directa <=15s; en Prometheus <=45s por scrape 30s + writer 5s + margen 10s.
Sin datos no hay vector percent, nunca una sustitución por cero. La falta de tasa
más de 2m también alerta; el calentamiento inicial no inventa historial.

## Herramientas preparadas y pruebas locales

- [Snapshot](../../scripts/snapshot-incremental-monitoring.py): solo lectura, CT 610
  vía alias pve; archivo local privado 0600, sin imprimir configuración. **No es por
  sí mismo un backup de rollback restaurado/verificado.**
- [Candidato incremental](../../scripts/prepare-incremental-monitoring.py): merge
  determinista y fail-closed. Copia solo infra-hosts y reglas CPU; rechaza cambios de
  RAM/disco ajenos. Config/otros targets/reglas se preservan. Hashes antes/después.
- [Validación](../../scripts/test-incremental-monitoring.sh): 106 tests Python,
  28 escenarios CPU previos y 6 incrementales, suite anterior, promtool config/rules
  y **check service-discovery real**, no solo lectura JSON. Node/CAD sin identidades
  duplicadas; Blackbox distingue module/probe_type para no borrar sondas diferentes.
- [Chequeo API / regla de prueba](../../scripts/check-incremental-chain.py): lectura
  real de targets, percent, contrato, CPU nativa y rules health; no declara éxito
  Telegram. Genera una regla de prueba local sin instalar ni enviar nada.

Desde terraform/proxmox, sin desplegar:

```bash
python3 scripts/snapshot-incremental-monitoring.py --output services/infra-prom/.runtime/incremental/NEW-baseline.json
python3 scripts/prepare-incremental-monitoring.py --baseline services/infra-prom/.runtime/incremental/NEW-baseline.json --output services/infra-prom/.runtime/incremental/NEW-candidate --report services/infra-prom/.runtime/incremental/NEW-report.json
PROMTOOL=/ruta/a/promtool-3.12.0 bash scripts/test-incremental-monitoring.sh services/infra-prom/.runtime/incremental/NEW-baseline.json
```

No usar deploy-prom/deploy-all: activarían además el candidato global previo.
No copiar check-prometheus.yml: contiene rutas locales solo para validar. La ruta
prometheus.yml del candidato conserva las rutas reales y el contenido original.

## P0 tras aprobación: operación mínima y verificación

1. Revalidar snapshot/hashes contra servidor; abortar ante drift. Capturar IDs/StartedAt
   de Prom/AM, targets/alerts y counters Telegram. Crear backup privado de configuración
   y mecanismos actuales, copia externa y prueba de lectura/restauración en staging.
   No borrar históricos ni volúmenes. Se guarda estado de los tres Journal y sus
   rollback originales existentes; no se modifican sus exporters en P0.
2. Validar candidato con versiones fijadas y paths de contenedor en staging. Revisar
   diff permitido: dos catálogos, CPU en infra-hosts, tres archivos CPU/inventario.
   No cambiar prometheus.yml, Compose, Alertmanager, receptores o secretos.
3. Instalar primero reglas CPU/inventario verificadas con reemplazo atómico,
   preservando owner/mode legibles por el UID real de Prometheus; backups siguen
   privados. Validar lectura con promtool del contenedor antes de recargar. Recargar
   **solo Prometheus ya running/ready** mediante SIGHUP; sin compose up ni señales a
   contenedores recién iniciados. Esperar reload_successful, aumento de timestamp,
   readiness y rules health=ok por API. No dar por exitoso un kill con código cero. Solo tras esa verificación publicar
   los dos JSON de targets mediante reemplazo atómico: file_sd los recoge sin
   recreaciones. Así ningún target nuevo se publica antes de que existan reglas.
   Comparar hashes antes de cada escritura; si son iguales, no escribir ni recargar.
4. file_sd debe mostrar 17 Node/17 cAdvisor, 3 contratos correctos, 14 pendientes,
   ninguna duplicación, once Blackbox sin cambios y cero job Grafana nuevo. Verificar
   percent/valid/capacidad/RAM y Docker individual de cada Journal con API.
5. Prueba real Telegram por cada CT como se describe abajo, >=10m de observación
   integrada y segunda aplicación sin cambios: mismos IDs/StartedAt, hashes iguales,
   **sin recarga** si no cambió nada. Solo entonces actualizar integración/cadena.
6. Fallo detiene R1. Conservar backups, estado, errores saneados y presentar la
   corrección/rollback; no ampliar el alcance a aplicaciones ni recursos.

## Handoff por CT sin esperar al final de los 17

P0 debe estar validado antes de R1. En cada R1–R7:

1. Backup de exporters, configuración Prometheus vigente/registro e imágenes; estado
   correcto del resto de contratos ya integrados como precondición.
2. Preparar reglas/targets y rollback con el nuevo CT, y validar off-host antes del
   corte. No añadirlo a pruebas verificadas ni registry definitivo por intención.
3. Aplicar exporters; inmediatamente medir fuente CPU/capacidad/identidad y registrar
   evidencia puntual. Promover solo ese CT al contrato. Aplicar target/inventario
   atómicos, recarga controlada si cambian reglas y verificar APIs. No esperar diez
   minutos de observación aislada ni al final de 17 para integrar el nuevo CT.
4. Completar prueba de cadena, observación integrada, idempotencia y actualización
   del roadmap **antes de avanzar al CT siguiente**.

El handoff tiene el intervalo normal de parada/arranque, descubrimiento, scrape y
calentamiento de rate; no se promete continuidad de cero segundos. Se exige timeout
acotado (120s para readiness y 180s para discovery/series), avisos de calidad y no
fallback. El for de CPU se inicia sobre datos correctos y no hereda tiempo de la
fuente física. Si no converge, detener el lote y conservar alerta de calidad; nunca
sustituir falta de CPU por cero. Ajustar relojes de trabajo/precondiciones, no umbrales.

## Rollback coordinado

Guardar un checkpoint por CT: IDs/imágenes/archivos exporter, catálogo previo,
inventario esperado, reglas y registry, hashes y estado del resto de CT ya integrados.

- R1 falla: mantener contrato corregido y su alerta de calidad mientras se restaura
  el exporter original. Verificar ambos originales running/IDs/métricas; después
  revertir **solo CT 613** al catálogo/inventario anterior. La CPU vuelve a unverified,
  no a fiable. No quitar reglas compartidas ni los tres Journal ya integrados.
- Si la regresión es de reglas comunes: conservar una versión compatible conocida
  que siga cubriendo todos los CT migrados; validar antes de recargar. **Rechazar**
  restaurar reglas legacy mientras siguen targets corregidos esperando lxc_cpu_*.
- Una reversión completa de P0 recupera la línea base de 14 scrapes, pero elimina
  cobertura Journal: solo es una salida documentada ante regresión, no una aceptación
  ni un avance a R1. No ejecutarla automáticamente ni afirmar que preserva la cadena.
- Validar tras rollback counts/identidades/reglas/alertas y receptor; conservar
  evidencia del incidente. No restaurar datos ni eliminar volúmenes/contenedores.

## Prueba Telegram que recorre la cadena completa

Generar regla temporal solo para un CT y run único:

```bash
python3 scripts/check-incremental-chain.py --ct 624 --prepare-test-run P0_624_fecha --output services/infra-prom/.runtime/incremental/verification.yml
```

La expresión `lxc:cpu_usage:percent{ct_id="624"} >= 0` depende del dato real válido;
for=30s, severity=info, etiqueta integration_test_run única. No se eleva carga ni se
modifican umbrales. Tras la aprobación de integración, instalar/validar/recargar solo
esa regla, observar FIRING en Prometheus, el mismo incidente/fingerprint en AM y
recepción en Telegram. Registrar contadores antes/después: intentos aumentan,
fallos no; el destinatario confirma el mensaje en el chat correcto.

Para resolver generar la misma regla con --resolved-rule (`<0`), manteniendo nombre
y labels. Verificar que deja de FIRING, AM procesa resolución y llega RESOLVED; puede
esperar group_interval=5m. Conservar evidencia/confirmación de ambos mensajes, después
retirar archivo temporal y validar/recargar. Nada se envió durante esta preparación.

Un POST directo a Alertmanager **no** satisface este criterio: omite exporter,
Prometheus y reglas. Readiness o counters sin confirmación de recepción tampoco
certifican toda la entrega. Solo actualizar telegram_chain_verified con evidencia
real y aceptación de recepción; no fabricar recibos ni extender la dispensa UAT F3.

## Riesgos y aceptación

Cambio de fuente/etiquetas puede resolver fingerprints viejos y crear nuevos; comprobar
que no coexisten alertas equivalentes, no silenciarlas para ocultar un problema.
Scrape/rate/for introducen el handoff descrito; fallos producen calidad/availability.
Los 14 pendientes siguen sin CPU LXC fiable aunque su alerta legacy se conserve.
Dashboards antiguos siguen pendientes de adaptar al contrato; no presentarlos como
vista fiable. Socket containerd ro permite RPC; R1 requiere aprobación específica, incluyendo
el cambio cAdvisor cgroupns private→host dentro del LXC detectado en su baseline.

P0/R1 se presentan para aprobación, con candidatos y pruebas locales. **No se ha
recargado ni desplegado ninguna configuración, reiniciado exporters o enviado alertas**
en esta intervención. La cobertura completa F4 exige 17 cadenas fiables verificadas,
Grafana/sondas y validación global independiente; el rollout ya integra por CT.

[Pruebas y estado real](evidence/2026-11-02-incremental-validation.json),
[discovery promtool](evidence/2026-11-02-incremental-discovery.json),
[candidato por hashes](evidence/2026-11-02-incremental-candidate.json).
