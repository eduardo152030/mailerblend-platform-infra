# Fase 4 — CT61211: ejecución D-035

**Cerrado:HALT GLOBAL,61211 BLOCKED / ROLLED BACK. Originales y checkpoint restaurados/verificados.**

## Cambio de política y prerrequisitos

D035 sustituye el vetoD034:614 pasa aBLOCKED / PRE-EXISTING ISSUE, sin reparación.
Sus503 preceden cualquier modificación; fingerprints originales iguales aD034.
NocoDB61211 usaDBhostdb en su propia redDocker, alias verificado, PostgreSQLready,
health200 y sin endpoints614 en dependencias. No se alteraron614 ni sus alertas.
CasosA/B/C/D implementados sin cambiar tolerancias, fuentes o umbrales.

## Ejecución real

61211 pasó preflight, backups externos/PVE de imágenes/config y checkpointProm,
promtool, Node1.10.2/cAdvisor0.60.6 por digest, fuenteLXC3CPU/6656MiB yDockerindividual,
ensayo de rollback coordinado, reanudación e idempotencia. AplicaciónHTTP200/PGready.
Observación inicial13muestras/360,225sPASS (mínimo180s/7), cuatro identidades con
CPU/RAM alineadas,TelegramFIRING/RESOLVED aceptados porAPI+2/0errores; sin recepción
humana nueva atribuida. Registro sigue8 aceptados: no promoción previa alwatcher.

## Fallo común confirmado

A60,025s delwatch comienza `RAM timeline does not bracket metric timestamp`.
El lectorRAM había terminado después del último dato1793963196.241173 por:

```text
ValueError: Invalid isoformat string: '2026-11-06T11:06:36.74017+00:00'
```

RFC3339Nano omite ceros finales. El parserRAM truncaba fracciones a6 pero no
completaba las de5 decimales; Python3.10 las rechaza. El parserCPU ya completaba
correctamente a6. No es evidencia de un contador erróneo de cAdvisor/Docker ni
una regresión de la aplicación. El validador hizo lo correcto al rechazar datos
sin historial; el defecto está en el lector común preparado enIaC.

Lectura independiente duranteanomalía:app200,CPUalineada4, contenedores activos
sin reinicios/OOMKilled, OOMcgroupdelta0. El lectorCPU sigueactivo; RAMinactivo.
Se conserva watcher900s y>=600s desde la primera anomalía; no se repite despliegue
ni se sustituye historial ausente. Después se ejecuta rollback coordinado.

## Corrección local, sin despliegue

`exporter-memory-alignment.py` normaliza fracción a6 microsegundos, igual al
parserCPU: `.ljust(6,'0')`. Conserva IDs/generación/timestamps/gaps/frescura y
20%/30%/25% con sus mínimos; no amplía tolerancias. Regresión reproduce el valor
exacto y precisiones0–9 conZ/+00:00/+01:00, además de rechazar texto inválido.
La corrección NO se copió alrun activo ni se reinició el lector; nuevo intento
no autorizado dentro delHALT de este run. Hay que revalidar producción tras fallo.

## Evidencias

- [Independencia y614 intacto](evidence/2026-11-06-d035-isolation-apply.json).
- [Prerrequisitos de lectura](evidence/2026-11-06-d035-prerequisite-readonly.json).
- [Salida exacta del lector](evidence/2026-11-06-d035-memory-collector-exit.json).
- [Historial ausente yCPUactivo](evidence/2026-11-06-d035-memory-collector-failure.json).
- [Aplicación/OOM durante anomalía](evidence/2026-11-06-d035-anomaly-runtime.json).
- [Decisión del lote](evidence/2026-11-06-d035-wave.json).
- [Tiempo](evidence/2026-11-06-d035-time.json).


## Cierre verificado — 2026-11-06 12:24 CET

Watcher31/903.637sFAIL,29muestrasfallidas,
primera a60.025s; extensiónconservada
843.612s desdeprimera. No se borróbaseline
ni se aceptaron muestras sin historial. El driver devuelveCaseD/HALT GLOBAL por
validador/lectorcomún, noCaseB ni falloaislado delLXC.

Rollbackcoordinado finalPASS: originalesnode/cAdv IDs/imágenes/restars/config,
aplicaciones/configsin cambios,HTTP200/PGready; checkpoint8con24/24archivosbyteexactos,
dosarchivosbackup legibles/hash externoPVE coincidente. LoggersCPU/RAMdetenidos.
Ochoaceptados yProm/AM mantienenIDs/StartedAt/restarts;17Node/17cAdvisor/11BlackboxUP
yochocadenasPASS;OOM/oom_kill/oom_group_killdelta0. Detenciones/reanudaciones de
exporters duranteensayo/rollback previstas; no reinicios deaplicaciones.
CT614 vuelvea verificarseexactamenteigual aD034 ycontinúa503preexistente,
alertas/targetslegacyintactos; no recurso/app/contendor suyo modificado.

ResultadoF4:8DONE/4BLOCKED/5PENDING. PolíticaBLOCKEDsinpermisos ni nuevosprocesos
deavance.52regresionesPASS(13política+15RAM+11CPU+7rollout+6reentrada),incluido
parserfraccionalexacto. Correcciónlocal NO aplicada alrunrechazado ni prod.
Tiempo:36.8min, incluyeobservación/vigilancia/rollback; sincommit/push.

Evidenciafinal:[rollback](evidence/2026-11-06-d035-final-audit.json),
[614/independencia trasrollback](evidence/2026-11-06-d035-isolation-final.json).
Siguientepaso: revisar/revalidar correccióncomún antesdeotrareentrada61211,
conrun/checkpointnuevos, sinreactivarelrunfallido. No reparar614ni iniciarR6/R7.
Backups/HALTs/archivosprivados bajo `$HOME/.local/share/mailerblend-recovery/phase4/`
y `/mnt/storage/mailerblend-recovery/phase4/`con elrun delintento en auditoría.
No borrar originales/imágenes/candidatos/volúmenes; no publicarconfiguraciónprivada.
