# Fase 4 — cierre del rollout CRITICAL D-039

2026-11-06 19:46 CET. **13/17 aceptados;4BLOCKED;0PENDING sin intentar. Ejecución cerrada.**

|CT|Servicio|Resultado|Tiempo intervención|Observación|Métricas|Aplicación|Backups|
|---|---|---|---|---|---|---|---|
|618|CRM|BLOCKED / ROLLED BACK|8,3min + diagnóstico acotado|9muestras válidas/240s; fallo siguiente|RAMcAdvisor volátil;CPU7/7|Originales/appsinregresión|2previos conservados|
|622|EVA|DONE|13.3min|21/600.5s|9contenedores|HTTP200;sinregresión|4verificados|
|611|Grafana|DONE|13.1min|21/600.5s|3contenedores|HTTP200;sinregresión|4verificados|
|616|Blackbox|DONE|13.3min|21/600.5s|3contenedores|HTTP200;sinregresión|4verificados|
|610|Prometheus|DONE|12.7min|21/600.4s|5contenedores|HTTP200;sinregresión|4verificados|

617/615/614 no se intervinieron. Continúan bloqueados junto con618. Los nueve
aceptados anteriores no se reaplicaron. Fase4 sigueINPROGRESS:17/17 y cierre global
pendientes; aceptar exporters e integración porCT no activa jobsGrafana/sondas
adicionales ni suponeUAT de negocio.

## Controles y alcance

- Node/cAdvisor activos por digest; EVA Node1.11.1, otros tres1.10.2; cAdvisor0.60.6.
  CPU/RAM alineadas por identidad/generación/namespace, Docker/cgroup ytimestamps.
  84muestras aceptadas en cuatroCT; márgenes y frescura sin cambios.
- Backup externo yPVE, configuración/reglas validadas conpromtool antes de recarga;
  integración incremental, idempotencia sin recreación/recarga innecesaria.
- Sin nuevosOOM, reinicios inesperados ni regresión de apps; recursos/config/montajes
  ycontenedores de aplicación originales preservados, incluidos los detenidos.
- Mecanismo de recuperación comparado conD037 realmente probado; no ensayo repetido
  en cuatroCT aceptados.618 sí requirió rollback real coordinado verificado.
- Prom/AM disponibles,17Node/17cAdvisor/11BlackboxUP y13cadenas correctas.
  Histórico previo alrollout:17seriesNode accesibles. Sin eliminación de volúmenes.
  ConfigAM ysecretoTelegram idénticos en backups antes/después, sin publicarcontenido.
- EntregaTelegram porloteR6 en622 yR7 en610: FIRING/RESOLVEDAPI +2cadauno,
  0errores nuevos (acumulado56, histórico); sin recepción humana confirmada.
- Antes de610 ydurante suintervención: observador externo local víaSSH estrictoPVE
  yHTTPdirecto, sin API dePrometheus;23muestras correctas,12otrosCT supervisados,
  procesosProm/AM sin reinicio. [Prueba](evidence/2026-11-06-d039-final.json).

## CT618 aislado yseguro

Fallo devalidación RAM del propio cAdvisor:20.582.400B entrebracketsDocker/cgroup
aprox14y30MB; superómax(4MiB,30%) enextremos. CPU7/7 yRAMrestantes6/6 correctos.
Hay volatilidad delgauge; no se demuestra contabilidaderrónea del exporter ni fallo
común deparser/unidades/identidad. No se aceptólamuestra ni se ampliaron márgenes.
Originales/checkpoint/cobertura restaurados; Budibase3.27.4 yduplicados detenidos,
DB/datos/volúmenes/RAM intactos. Revisión final confirmaIDs/config/apps/recursos.
El primerdriveremitióHALT conservador sinclasificar; se conservó su evidenciaHALT.
Tras prueba positiva deaislamiento yretornoseguro,SKIPcontinuó enrun nuevo desde622,
sin reintentar618. [Aislamiento](evidence/2026-11-06-d039-618-isolation.json).

## IaC y recuperación

Adaptación mínima [driverCRITICAL](../../scripts/run-critical-exporter-wave.py)
sobreRunner/Transaction existentes; [audit](../../scripts/audit-critical-exporters.py)
y [diagnóstico acotado](../../scripts/diagnose-critical-ram.py). Factoría común
admite618/622 con apps detenidas preservadas; contratoCPU/RAM sin cambio.
Pruebas pertinentes25PASS (5adaptación,13clasificación,7runner); no repetir80tests
comunes. Autorización618/622 enRunner solo bajo políticaD039 explícita, no--all.

Backupsprivados porrun/CT:
`~/.local/share/mailerblend-recovery/phase4/<run>/<CT>/` y
`/mnt/storage/mailerblend-recovery/phase4/<run>/<CT>/` enPVE.
Antes/después: `exporters-before.tar`, `exporters-after.tar.gz`,
`monitoring/integration-before.tar`, `monitoring/integration-after.tar.gz`.
16archivos de cuatroDONE revalidados porSHA/lectura;618 conserva dosprevios y
originales/candidatos detenidos. No borrarimágenes,volúmenes,HALTs ni evidencias.
Rollback existente: checkpointProm coordinado antesdeexporters originales,
readiness/identidades/apps/cobertura. No ejecutar sobreestado13 con checkpoints
anteriores sin plan/autorización: podrían retirar integraciones posteriores.

[Primer intento618](evidence/2026-11-06-d039-wave.json),
[continuación622→610](evidence/2026-11-06-d039-continuation.json),
[auditoría final](evidence/2026-11-06-d039-final.json),
[tiempo](evidence/2026-11-06-d039-time.json).
Tiempo total:81.3min, incluyepreparación,observaciones,rollback/diagnóstico ydocumentación.
Siguientegrupo recomendado: recuperación individual617→618; después615/614 con
baseline503,sin exigir reparación deaplicaciones para aceptar monitorización si
no hay regresión ylosotrosgates pasan. **Sin autorización deesosCT enesta sesión.**
SinTerraformapply,commit,push ni cambios deapps/DB/recursosPVE.
