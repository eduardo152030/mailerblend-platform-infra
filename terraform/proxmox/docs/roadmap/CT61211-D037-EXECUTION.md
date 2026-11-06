# Fase 4 — CT61211 svc01: cierre D-037

2026-11-06 16:38 CET. **DONE técnico;9/17 aceptados. Sesión detenida.**
Run `integration-20261106T12344561211Z`; solo exporters61211 y configuraciónProm610
mínima. No otros exporters/apps/recursos ni Terraformapply. Sin commits/push.

## Resultado verificado

|Control|Resultado|
|---|---|
|FrameworkD036|80testsPASS; compatibilidad fresca8/8 por lectura; tolerancias intactas|
|Originales/dependencias|NocoDB200/PGready;614503 previo, intacto e independiente|
|Backups|4archivos legibles ySHA256 local/PVE; imágenesoriginales cargadas/verificadas|
|IaC|12inputs aplicados coinciden conmanifest; dos renders idénticos; contratoCPU/RAM común|
|Node Exporter|1.10.2,CPUtextfile cgroupv2 yRAMLXCFS; CPUfísica nativa desactivada|
|cAdvisor|0.60.6; cadencia30s,dinámica/jitter desactivados;128MiB/0,5CPU|
|Identidad/CPU/RAM|4contenedoresactivos;44muestrasPASS; identidad/generación/namespace exactos ybrackets temporales|
|Rollback/idempotencia|Rollback coordinado real deProm+exporters; originales restaurados; mismos candidatos reaplicados; segunda aplicación sin recreación/recarga|
|Inicial|13muestras/360,188s (mínimo180s/7), sin anomalías|
|Vigilancia|31muestras/901,755s (última muestra900s), sin anomalías|
|Aplicación/recursos|NocoDB200 yPostgreSQLready antes/después; sin nuevosOOM ni reinicios inesperados|
|Prometheus/AM|Ready,sanos;17Node/17cAdvisor/11BlackboxUP;9cadenas fiables;8aceptados yProm/AMsin reinicios|
|Telegram|FIRING/RESOLVED medianteexporter→Prom→AM→API;2envíos,0erroresnuevos; sin recepción humana confirmada|

No se demuestra el predicado realCPU>90% durante10min al probar una regla temporal.
No pruebaUATfuncional de negocio. El antiguo falloRFC3339RAM no reapareció en esta
ventana; no garantiza ausencia futura de defectos. Legacy y alertas de bloqueados
conservados. La integración fiable de9CT no equivale a aceptación global17/17.

## Producción y recuperación

Revisión `framework-347ef93c2fca`; digests:

- Node: `sha256:3ac34ce007accad95afed72149e0d2b927b7e42fd1c866149b945b84737c62c3`.
- cAdvisor: `sha256:b8e7d1093144fd088f425ff003d75a4aa405de075db78dae3bc563730b1bd07a`.

Bundleactivo61211: `/opt/exporter-phase4-pilot/integration-20261106T12344561211Z-61211`.
Backupsprivadoslocales: `~/.local/share/mailerblend-recovery/phase4/integration-20261106T12344561211Z/61211/`;
PVE: `/mnt/storage/mailerblend-recovery/phase4/integration-20261106T12344561211Z/61211/`.
Archivos: `exporters-before.tar`, `exporters-after.tar.gz`,
`monitoring/integration-before.tar`, `monitoring/integration-after.tar.gz`.
Imágenes/originales/candidatosretenidos yHALTsD033/D035 no borrados. El rollback
del procedimiento [runner](../../scripts/rollout-approved-exporters.py) y
[recuperación](../../scripts/recover-approved-wave.py) restaura primerocheckpointProm,
despuésexportersoriginales, readiness eidentidad/cobertura. No ejecutarlo trasDONE
sin diagnóstico/alcance aprobado. Configuraciones sensibles solo enbackupsprivados.

## Evidencias y siguiente paso

- [Aceptaciónfinal](evidence/2026-11-06-d037-completion.json).
- [Wave](evidence/2026-11-06-d037-wave.json).
- [Lecturafresca8/8](evidence/2026-11-06-d037-framework-preflight-refresh.json).
- [Reproducibilidad](evidence/2026-11-06-d037-reproducibility-refresh.json).
- [Aislamiento final614/61211](evidence/2026-11-06-d037-final-isolation.json).
- [Tiempo](evidence/2026-11-06-d037-time.json).

Tiempo: procedimiento25,3min; totaldocumental38.0min excluyendo pausa
sin acciones145.9min (wall183.9min).
9DONE:624/626/625/613/621/620/619/623/61211.
3BLOCKED:617/615/614;5PENDING:618/622/611/616/610. Permisosvacíos,
automatic_rolloutfalse. Revisar yautorizar siguientegrupo; no ejecutarotroCT.
