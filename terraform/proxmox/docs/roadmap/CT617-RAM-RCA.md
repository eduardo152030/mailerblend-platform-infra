# Fase 4 — diagnóstico CT617 y procedimiento común

2026-11-06 10:35 CET. D-032: **diagnóstico/local; NO desplegado**. Producción sigue8 DONE,
2 BLOCKED,7 PENDING.617 conserva originales y candidatos detenidos;615 no tratado.

## Conclusión y alcance de la causa

**Defecto confirmado del validador RAM: comparar un gauge cacheado con una lectura
actual sin alinear tiempos. No está demostrada la causa única de la muestra histórica
ni un fallo contable de cAdvisor/Docker/LXC.** El diseño permitía falsos rechazos;
las pruebas reproducen ese mecanismo sin ampliar tolerancias. RAM puede subir o
bajar: la interpolación monótona usada para CPU no es válida aquí.

Fallo histórico de analytics-ingest-gateway, ID
`674fd7dbdff0972aa9b41d7d0d09160887cd03ab7f11a69ba31f1d8522bca09a`,
StartedAt2026-09-17T20:43:50.983839068Z:

| Fuente | Bytes | Tiempo/alcance |
|---|---:|---|
| cAdvisor usage y working_set |47.448.064|1793911210.764 UTC epoch|
| Docker API usage |61.263.872|Lectura posterior; read original descartado|
| Cgroup PVE memory.current |60.858.368|Lectura posterior|
| Inicio del sample |—|1793911217.9410284;7,177s posterior a cAdvisor|

Diferencia13.815.808B, superior al margen12.252.774,4B(max512KiB/20%).
El inicio del sample **no es** el timestamp exacto Docker: el desfase real de su
lectura puede ser mayor. No hay historial RAM a1793911210.764; el logger anterior
solo conservaba CPU. No reconstruir ni afirmar falso positivo histórico probado.
[Incidente](evidence/2026-11-05-617-post-watch-failure.json).

## Lectura real y diferencias de contabilización

CT617:1CPU/512MiB, swap512MiB. En una captura PVE:
`memory.current=516.857.856`, `file=256.905.216`, usoProxmox259.952.640B.
La fórmula instalada es `memory.current - memory.stat.file`, ver
[fuente PVE leída](evidence/2026-11-06-proxmox-memory-accounting-source.json).
El cgroup delegado dentro del CT muestra `memory.max=max`, pero el padrePVE limita
536.870.912B; no significa memoria ilimitada del LXC.

480 lecturas/60s,120 por contenedor: Docker API usage coincide exactamente con
memory.current posterior en las480; solicitudes<=11,1ms. Ingest-gateway conserva
el ID/StartedAt del incidente y varía61.091.840–61.739.008B. Primer memory.stat:
anon43.659.264, file14.024.704, kernel3.878.912, shmem0, inactive_file0.
Eso no prueba cuánto file tenía en el instante histórico. El shmem de LXC192.512B
forma parte de file: no sumarlo otra vez ni sumar RSS de procesos compartidos.

Docker CLI descuenta inactive_file en cgroupv2; API usage incluye caché.
Comparar usage con usage/memory.current y working_set con la semántica equivalente,
no Proxmox neto ni RSS. [Docker oficial](https://docs.docker.com/reference/cli/docker/container/stats/),
[cgroupv2](https://www.kernel.org/doc/html/latest/admin-guide/cgroup-v2.html).
No se usó Docker CLI para el gate histórico: la caché no demuestra su causa única.

Node legacy informa16.646.774.784B físicos frente a536.870.912B LXCFS.
cAdvisor legacy0.47.2 solo expone raíz, sin series Docker individuales (Docker29.1.3).
Son defectos conocidos de la cobertura legacy restaurada, no aceptación del candidato.
Apps originales/config/IDs verificados: proxy403 esperado, backend200.
Durante60s: OOM/max0 nuevos; high+18 en padrePVE, PSIavg60 máximo observado0,01.
Hay reclaim y swap(~83MB); no afirmar ausencia de presión por tenerOOM0.
[Lecturas completas](evidence/2026-11-06-617-memory-readonly.json).

## ¿Es el mismo template?

**Misma familia, distintas revisiones y parámetros; no es un artefacto idéntico.**
Se deriva624→Journal→R2→otros mediante sustituciones Python con asserts. Cambian
IDs/host/IP/capacidad/imagenNode/apps/puertos/labels, ventanas, proyectosCompose,
sockets/namespaces y revisiones de recursos/cadencia.

| CT | CPU / RAM MiB | Node / cAdvisor | Límite cAdvisor MiB | Cadencia fija |
|---|---|---|---|---|
| 624 | 1 / 512 | 1.10.2 / v0.60.6 | 128 | No |
| 626 | 2 / 2048 | 1.10.2 / v0.60.6 | 128 | No |
| 625 | 2 / 2048 | 1.10.2 / v0.60.6 | 128 | No |
| 613 | 1 / 512 | 1.10.2 / v0.60.6 | 128 | No |
| 621 | 2 / 2048 | 1.11.0 / v0.60.6 | 128 | No |
| 620 | 2 / 2048 | 1.10.2 / v0.60.6 | 128 | No |
| 619 | 2 / 2048 | 1.10.2 / v0.60.6 | 256 | No |
| 623 | 2 / 4096 | 1.11.1 / v0.60.6 | 128 | Sí |
| 617 | 1 / 512 | 1.10.2 / v0.47.2 | 0 | No |


617 de la tabla es el original restaurado: sin límites Docker propios y namespace
private; sigue sujeto a512MiB del padreLXC. El candidato preparado usa0.60.6,
128MiB/0,5CPU y cgroupns host **del LXC**, sockets Docker/containerd y montajes
revisados; no el namespacePVE. Los ocho aceptados usan ese modelo, salvo619256MiB.
Versiones Node distintas son pins deliberados;623 realmente1.11.1 (corrige texto
anterior que decía1.10.2; no se cambió producción).

619: presión con128MiB (entorno/ajuste de recursos), identidadCompose compartida
(defecto de revisión) y CPU cacheada vs actual (validador).623: dinámica/jitter
permiten hasta120s frente a frescura90s (defecto de contrato del template, no evidencia
de Docker mal); cadencia fija30s lo corrige.617: RAM aún no alineada (validador);
512MiB/caché/swap/carga y legacy son diferencias reales, no justificación para subir20%.
No hay evidencia de un fallo contable de cAdvisor en617.

## Corrección preparada, pruebas y límites

- [Librería común RAM](../../scripts/exporter-memory-alignment.py): ID completo,
  nombre/StartedAt, timestamp explícito, historial0,5s Docker/cgroup, memory.stat
  seleccionado y lectura acotada<=0,5s; huecos<=2s, frescura90s intactos.
- [Opt-in617](../../scripts/prepare-617-memory.py): compara ambos extremos que
  rodean el timestamp; sin interpolar, escoger extremo conveniente ni añadir margen
  por tiempo. Conserva20%/512KiB apps,30%/4MiB exporters y25%/8MiB Docker/cgroup.
  Si hay volatilidad o falta de evidencia, falla cerrado. También sustituye el
  contraste Docker/PVE posterior por la comprobación Docker/cgroup acotada del logger.
- Runner elige este builder solo617; arranca/para ambos loggers, conserva archivos,
  tolera únicamente desaparición de PID/404 en transiciones planificadas. Un hueco
  no pasa el validador. Memoria leída en streaming, sin cargar toda la historia.
- Proyecto617-ram-v1 evita reutilizar los candidatos detenidos por etiquetasCompose.
  No se modifican imágenes, recursos, privilegios, sockets, apps ni Compose de exporters.
- [Reentrada de lectura](../../scripts/audit-617-reentry.py): originales/held/apps,
  inventario y configuración verificados. Runner exige auditoría617<=300s mediante
  `--preflight-audit`; no reutiliza inventario anterior al rollback.
-13 regresiones RAM, más31 pertinentes existentes: **44 PASS**. Control de solo
  lectura en623:600 lecturas y cinco contenedores con RAM alineada PASS; replay
  registrado pasa. No sustituye la prueba de617 ni demuestra un instante histórico.
- Ocho cadenas sanas,17Node/17cAdvisor/11Blackbox UP, reglas y Prom/AM ready;
 56 hashes de inputs y16 identidades/StartedAt/restarts de exporters aceptados sin
 cambios respecto al cierre anterior. No pruebas nuevas de entregaTelegram enviadas.
 [Resumen](evidence/2026-11-06-617-diagnosis-summary.json),
 [control](evidence/2026-11-06-memory-alignment-live-control.json),
 [cadena](evidence/2026-11-06-617-diagnostic-chain.json).

Riesgos: no aceptar617 con una prueba en623; el gauge puede fluctuar entre lecturas
subsegundo, por eso ambos extremos deben pasar y una discrepancia vuelve a parar.
La reentrada completa y su recuperación con este bundle no se han ensayado aún en
producción. El runner publica PASS inicialmente: es provisional hasta watcherPASS;
no avanzar ni dar DONE antes. Política actual BLOCKED y HALTs históricos intactos.

## Mejoras comunes propuestas, no desplegadas globalmente

Un contrato versionado porLXC con capacidad, pins, recursos revisados, cadencia,
sockets/namespaces y probes; validadores importados en lugar de cadenas de replace;
preflight funcional antes de cualquier despliegue; historial CPU/RAM con identidad,
timestamps y fallo íntegro; identificadorCompose por revisión; aceptar/promover
solo tras vigilancia final. Fijar cadencia en futuros candidatos, sin reaplicar ocho
aceptados ni ampliar límites automáticamente. Extender RAM opt-in a otrosLXC requiere
revisión y pruebas: hoy se prepara únicamente617.

## Procedimiento exacto para finalizar617 (pendiente de autorización)

1. Revisar este diagnóstico y autorizar **solo617**, configuraciónProm610 mínima y
 recuperación617. Mantener ocho aceptados y615 intactos. Registrar aprobación antes
 de habilitar política IaC: allowed_mutation_cts=[617], allowed_recovery_cts=[617],
 automatic_rollout=false; no borrar HALTs ni usar--all. Ahora NO habilitada.
2. Preparación local reproducible (directorio nuevo):

```bash
python3 -m unittest discover -s tests/monitoring -p 'test_memory_alignment.py'
python3 scripts/prepare-617-memory.py --output /tmp/phase4-617-ram-v1-review
python3 scripts/audit-617-reentry.py --output /tmp/phase4-617-fresh-audit.json
```

3. Tras aprobación y revisión de diff/política, repetir auditoría fresca (nuevo
 archivo si ya existe), y usar un run nuevo, conservando el runD031 y sus backups:

```bash
run_id="integration-$(date -u +%Y%m%dT%H%M%SZ)"
python3 scripts/rollout-approved-exporters.py --run "$run_id" --ct 617   --preflight-audit /tmp/phase4-617-fresh-audit.json --execute
```

Ese comando está vetado hoy por política. Antes de mutar exige preflight,
backup imágenes/config verificable externo/PVE y checkpointProm **actual de ocho**,
promtool config/reglas/discovery17/17/11. Aplica candidato, comprueba fuente real,
integra solo617, ensaya rollback coordinado y segunda aplicación; observa>=600s/21
más cadena Telegram API FIRING/RESOLVED. Recepción humana sigue pendiente si no se
confirma. No migrar exporters610 ni eliminar legacyCRM/EVA.
4. Esperar `post-watch-result.json` del nuevo run:>=900s/31 sin anomalías, apps,
OOM/restarts/PSI, métricas reales y ocho fuentes intactos. Solo entonces617 DONE y
nueve aceptados; si el fallo exige extensión,>=600s desde primera anomalía sin reset.
5. Si falla observación inicial, recuperación de Runner restaura checkpoint previo
 antes de originales y bloquea. Si falla watcher, autorizar únicamente recovery ya
 previsto y ejecutar para **ese run nuevo**, conservando evidenciaD031:

```bash
python3 scripts/rollback-post-watch-617.py --run "$run_id"   --evidence-output docs/roadmap/evidence/617-ram-v1-rollback.json --execute
```

El helper exige watcherFAIL>=900s y>=600s desde anomalía, checkpoint8 correcto,
IDs de candidatos y permiso recovery. Revoca provisional y verifica ocho cadenas;
no restaurar checkpoint7 ni borrar originales/candidatos/volúmenes. Si cualquier
recuperación no verifica, detener y presentar estado sin declarar seguro.
6. Actualizar estado/evidencias y detenerse: **no615 ni otroLXC**.

CierreD032: 2026-11-06 10:56 CET. Tiempo registrado: 39.1min. Enlaces locales, secreto-signaturas y `git diff --check` PASS; sin commit/push/staging. [Validación local](evidence/2026-11-06-617-local-validation.json).


## Resultado posterior D-033 — 2026-11-06 11:15 CET

Reentrada autorizada pero primer apply FAIL por colisión de nombresheld heredados.
Rollback seguro verificado,8/17 sin cambios; no se llegó a validar RAM nueva ni
a600s/900s. Nombresheld por revisión corregidos solo localmente y regresión
completa de helperPASS. No reintento, políticaBLOCKED; [cierre](CT617-D033-EXECUTION.md).
