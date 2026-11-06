# Fase 4 — Exporters & Monitoring Coverage: framework de validación

2026-11-06 13:29 CET. D-036 terminado: **implementación local y lectura**, sin despliegue.
Producción sigue8DONE/4BLOCKED/5PENDING. No promete ausencia permanente de defectos:
recertificar un despliegue exige sus gates, rollback e idempotencia reales.

## Defectos y correcciones

|Hallazgo|Corrección reutilizable|Límite que se conserva|
|---|---|---|
|619: acumulativo cacheado contra actual, timestamp descartado|Mismo ID/generación/ámbito, timestamp y extremos; delta sobre ventanas comunes|CPU max(1s,3%); no división por núcleos del acumulativo|
|623: dinámica/jitter puede superar90s|Frescura explícita y cadencia30s sin dinámica/jitter en candidatos futuros de la factoría|90s; no modificar perfiles de ocho instalados|
|617: gauge RAM comparado en instantes distintos|Brackets medidos para usage, ambos extremos; sin interpolar RAM|Apps max512KiB/20%; exporters4MiB/30%|
|61211: parserRAM divergente rechazó5decimales|Parser único RFC3339 con timezone,0–9 decimales; truncado/padding a6|No asumir zona local ni inferir timestamps ausentes|
|CPU aceptaba coincidencia parcial de ID/cgroup|ID64hex exacto en hoja, nombre, StartedAt y ámbitoLXC/namespace|Sin mezclar motores ni arranques|
|IDs Docker clonados en distintos LXC|Ámbito obligatorio en las APIs de validación; frames/historia con mismo scope|Datos históricos solo por replay con procedencia explícita|
|NaN/Inf/bool/valores negativos o duplicados no uniformes|Contrato tipado, parsingProm común, rechazo de muestras/identidades duplicadas y de orden temporal inverso|Sin sustituciones por0 ni último valor conocido|
|Historial crecía en memoria y pruebaCPU no ligada al raw|Lectura en streaming acotada, raw metric↔proof, gaps/monotoníaCPU; parciales finales ignorados, JSON completo malformado rechazado|Gap<=2s, request<=0,5s|
|Lector muerto parecía solo ausencia de historia|PID/cmdline exacto antes de esperar historia; fallo explícito del framework|No reiniciar lectores para esconder fallos|
|Reentrada podía colisionar con candidatos retenidos|ProyectoCompose y nombresheld con revisión hash de inputs; auditoría fresca incluyendo held|Originales/candidatos/backups/HALTs conservados|

La incertidumbre de un límite inferior de deltaCPU puede ser negativa cuando
se solapan brackets; no es un acumulativoCPU negativo. Se conserva la tolerancia
original con valor absoluto para ese intervalo, rechazando contadores reales
negativos. RAM puede subir o bajar y nunca se interpola como un contador.
No ejecutar validaciones con `python -O`: el contrato rechaza optimización que
suprima los asserts. El renderer embebe la misma fuente en ambos lectores/observer;
no requiere instalar módulos ni copiar librerías a producción durante esta sesión.

No reconstruir RAM histórica617 que no se guardó. La diferencia conservada fue
47.448.064B vs61.263.872B, margen12.252.774,4B, con tiempos distintos. Se demuestra
el defecto de comparabilidad, no una causa contable única. La muestra original623
tampoco permite atribuir el fallo exclusivamente a un contenedor.

## Código IaC

- [Contrato único](../../scripts/exporter_metric_contract.py): timestamps, tipado,
  identidad/ámbito, unidades, parsingProm, memoria, captura y estado del lector.
- [CPU](../../scripts/exporter-cpu-alignment.py) y [RAM](../../scripts/exporter-memory-alignment.py)
  usan ese contrato. Capturan Docker/cgroup en la misma petición acotada, con
  ID/nombre y raw antes/después; guardan generación y namespace. CPU total no se
  confunde con series por núcleo. InterpolaciónCPU solo estimativa, ambos extremos
  y ventanas siguen siendo obligatorios.
- [Factoría común](../../scripts/prepare-aligned-exporters.py) y
  [base](../../scripts/prepare-approved-exporters.py): parsing y librerías compartidos,
  hash/schema, scope y gates presentes antes de staging. El adaptador617 conserva
  la API anterior; sus nombres históricos no son la implementación autoritativa.
- [Runner](../../scripts/rollout-approved-exporters.py) requiere contratoCPU/RAM
  antes de cualquier staging y auditoría fresca para reentradas617/61211.
- [Auditoría de reentrada61211](../../scripts/audit-exporter-reentry.py), preparada
  y no ejecutada aquí: originales/apps/D035held exactos, recursos e inventario.
  [Driver de política](../../scripts/run-skip-exporter-wave.py) recibe ese audit.

La factoría conserva ventanas de la política: convencional180s/7, observabilidad
600s/21;617600s/21 por incidente. Autorizar un modelo o un renderer **no** autoriza
su despliegue. Los templates históricos del piloto permanecen como entradas congeladas;
no usar directamente el validador antiguo para nuevos candidatos. La nueva guardia
rechaza bundles sin RAMalineada antes de mutar. La factorización no revisa por sí
sola límites especiales (p.ej.256MiB619), sockets ni modelosR6: no reaplicar aceptados.

## Unidades y diferencias legítimas

CPU Docker ns/1e9, cgroup usage_usec/1e6 y cAdvisor segundos. La cantidad acumulada
no se multiplica/divide porCPU. Rate en cores=deltaCPU/deltaT; porcentajeLXC=100×rate/
capacidad asignada. Es diferente del porcentajeCLI calculado con system_cpu_usage.
[DockerCLI29.1.3](https://github.com/docker/cli/blob/v29.1.3/cli/command/container/stats_helpers.go).

En cgroupv2 se contrasta **usage bruto** entre API/cAdvisor/memory.current. cAdvisor
working_set=max(0,usage-inactive_file); DockerCLI descuenta inactive_file si es menor
queusage y, en su límite defensivo, devuelveusage. Proxmox instalado informa
memory.current-file. Son vistas distintas; shmem forma parte de file, no se suma
otra vez. Estas fórmulas explican semántica, nunca rellenan métricas ausentes ni
transforman un fallo de gauge enPASS.
[cAdvisor0.60.6](https://github.com/google/cadvisor/blob/v0.60.6/lib/container/libcontainer/handler.go),
[fuentePVE conservada](evidence/2026-11-06-proxmox-memory-accounting-source.json).

## Regresiones y comprobación de lectura

**80 tests PASS**:21 contrato común+11CPU+15RAM+13política+7rollout+6reentrada+
4aplicaciónincremental+3cierre. [Fixture real saneado](../../tests/monitoring/fixtures/phase4-actual-incidents.json)
y [procedencia/límites](../../tests/monitoring/fixtures/README.md). Se verifican los
valores reales619/623/617/61211, controlRAM623, corruptelas sintéticas separadas,
IDs clonados, muerto/PIDreutilizado, timestamps, conversiones, scopeausente, proof
adulterada, parser embebido, nombresheld y preservación de ventanasR7.

[Auditor de compatibilidad](../../scripts/check-framework-compatibility.py) ejecutó
Python efímero porSSH estricto/stdin, sin archivos remotos ni instalaciones. API GET,
/proc/cgroups y métricasHTTP;130s porCT, máximo4 lecturas concurrentes. Resultado
final8/8PASS,147frames válidos sobre31 contenedores con scope; historia CPU común
con ventanas medidas y RAM sin interpolación. Se observaron fracciones6/7/8/9 en
8060 lecturas y se prueban0–9 offline. CapacidadPVE verificada y NodeLXC real, sin
CPU física nativa.56 inputs y IDs/imágenes/StartedAt/restarts intactos. No Telegramtest.

|CT|Resultado final de lectura|
|---|---|
|624/626/625/613/621/620/619/623|PASS todos; fuente, identidad y CPU/RAM alineadas|

Primera pasada625 rechazó frescura/futuro; la muestra completa/edad/ID no quedaron
capturados en ese error inicial. No atribuir causa única. El auditor ya conserva
esos datos en diagnósticos posteriores. La segunda pasada completa PASS **no borra**
el antecedente ni demuestra frescura permanente. Los perfiles antiguos con dinámica/
jitter siguen instalados salvo623; no se tocaron. Una futura violación90s exige
parada y diagnóstico, no ampliar límite ni corregir ocho fuentes sin alcance.

[Evidencia inicial](evidence/2026-11-06-d036-compatibility.json),
[final8/8](evidence/2026-11-06-d036-compatibility-final.json),
[resumen/hashes/recursosPVE](evidence/2026-11-06-d036-compatibility-summary.json),
[Prom/AM](evidence/2026-11-06-d036-global-readonly.json).
No es aceptación nueva ni reobservación completa de cada aplicación y deTelegram.

## Reintento61211 preparado, NO ejecutado ni autorizado en D036

Revisión local `framework-347ef93c2fca`,12 archivos, pins originales,
[manifiesto](evidence/2026-11-06-d036-61211-prepared-manifest.json). Usa entrada
histórica para revisión local, no un preflight actual de61211. Ningún CT bloqueado
se volvió a intervenir. Nuevos nombres con hash evitan los heldram-v1 delD035.

1. Revisar este informe y alcance exclusivo61211/configProm610 mínima/rollback.
   D036 no habilita política: hoyBLOCKED, listas de ejecución yrecuperaciónvacías.
2. Tras autorización de nueva intervención: ejecutar tests, revalidar ocho fuentes
   de lectura y requisitos614preexistente/independencia. No borrar HALTs ni backups.
3. Auditoría fresca61211 incluye sus dos heldD035 detenidos y originales exactos.
   Preparar bundle nuevo a partir de esa auditoría, revisar pins/revisión/diff.
4. Mantener política/ejecución orden[61211] ysin--all; audit<=300s alpreflight.
   Backups externos/PVE nuevos verificados, checkpointactual8 ypromtool antes de
   mutar; fuenteLXC/DockerCPU/RAM, app/DB, rollbackreal e idempotencia,180s/7 más
   watcher900s/31 ycadenaTelegram. Anteanomalía>=600s sinreset yparadaCaseD si común.
5. DONE exige todos los gates; fallo exige retorno seguro ydocumentación. No614,
   nootrosaceptados niR6/R7. No usar elrunD035 ni sucheckpoint comoactual por edad.

Comandos para la sesión autorizada posterior, desde terraform/proxmox:

```bash
python3 -m unittest discover -s tests/monitoring -p 'test_metric_contract.py'
python3 scripts/check-framework-compatibility.py --seconds 130 --workers 4 --output /tmp/framework-preflight-new.json
python3 scripts/verify-614-61211-isolation.py --output /tmp/61211-prerequisite-new.json
python3 scripts/audit-exporter-reentry.py --ct 61211 --output /tmp/61211-audit-new.json
python3 scripts/prepare-aligned-exporters.py --ct 61211 --audit /tmp/61211-audit-new.json --output /tmp/61211-review-new
```

Esos scripts rechazan salidas existentes: conservarlas y usar rutas nuevas. Regenerar
los dos audits si tienen>300s antes de ejecución. Solo con política habilitada y
alcance aprobado, usando unrun nuevo:

```bash
run_id="integration-$(date -u +%Y%m%dT%H%M%SZ)"
python3 scripts/run-skip-exporter-wave.py --run "$run_id" \
  --preflight-audit /tmp/61211-audit-new.json \
  --prerequisite-evidence /tmp/61211-prerequisite-new.json \
  --output docs/roadmap/evidence/61211-new-wave.json --execute
```

El driver espera alwatcher, no promueve por PASS inicial; recupera automáticamente
ante fallo, verificaoriginales/aplicación/cobertura y para ante cualquier incertidumbre.
No hacer commits/push ni eliminar archivosprivados de recuperación. Estado actual
8/4/5; intervenciónD036terminada. Tiempo:44.0min, incluyendo lecturas acotadas.
