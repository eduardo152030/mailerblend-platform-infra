# Fase 4 — cierre de cobertura de exporters D-041

2026-11-06 21:08 CET. **Cobertura de exporters LXC/Docker: DONE,17/17 aceptados técnicamente.**
0BLOCKED de monitorización,0PENDING de rollout. Ejecución detenida.

|CT|Resultado|Tiempo intervención|Observación|CPU/RAM/Docker|Aplicación|
|---|---|---|---|---|---|
|617|DONE|5.4min|7/180.1s|4contenedores|Proxy403 esperado/backend200,sinregresión|
|618|DONE|8.3min|11/300.1s|7contenedores|UI/health/ready200;Budibase3.27.4preservado|
|615|DONE|5.5min|7/180.1s|4contenedores|HTTP503preexistente,sinregresión;NOsaludable|
|614|DONE|6.3min|7/180.1s|4contenedores|HTTP503preexistente,sinregresión;NOsaludable|

Total de sesión:58.1min; suma de intervenciones25.5min.
Preparación,pruebasdirigidas ydocumentación incluidas enel total.13aceptados previos
sin reaplicar ni repetir observaciones; IDs/imágenes/StartedAt/restarts intactos.

## Resultado y correcciones mínimas

- Node1.10.2 y cAdvisor0.60.6 por digest enlos cuatroCT; fuentesCPUcgroup/LXCFS,
  RAMrealLXC,métricasDocker individuales ycomparación temporal/identidad/namespace.
  32muestras válidas; no nuevosOOM ni reinicios inesperados. Recursos/apps intactos.
- Reentradas con proyecto/nombresheld derivados determinísticamente delrun más
  losinputs; preserva candidatos previos yevita colisiones.617 aplica corrección
  preparada,temporal ydeheld,con backup/checkpointnuevos.
- CRM: capturaRAM0,1s envezde0,5s paraestrechar elbracket deun gauge volátil;
  máximoobservado cAdvisor0,123s. Seconservan ambos extremos,sin interpolar ni
  ampliar tolerancias/frescura/límites. No se demuestra error contable deDocker
  o cAdvisor. Budibase3.27.4,DB,volúmenes,recursos yduplicados detenidos preservados.
-615/614: gate de no regresión contraHTTP503 explícito enIaC; aplicación sigue
  con problema preexistente. No se reparó ni se declaróhealthy. Alertas conservadas.
- Preflight,backup externo/PVE,imagenoriginal recuperable,promtoolantesderecarga,
  integración e idempotenciaPASS. Ruta rollback existente verificada contraD037;
  noensayo real repetido ni rollback necesario enestelote.16archivoslegibles/hash
  verificados y12inputs porCTcoinciden conarchivo deconfiguración aplicado.
-17Node/17cAdvisor/11BlackboxUP y17cadenasCPU válidas. ProcesosProm/AM intactos,
  histórico previo accesible. ConfigAM ysecretoTelegramidénticos antes/después.
  CanalverificadoD039 reutilizado,0errores nuevos;132envíos/56falloshistóricos.
  No nuevoFIRING/RESOLVED nihumanreceiptenD041; no se prueba un `for` sinpredicado.
- Vigilancia posterior continuaPrometheus/Alertmanager,sinwatchbloqueanteextra.
  24pruebasdirigidasPASS (3reentrada/503,15RAMmodificada,6adaptador); no suitecompleta.

## Evidencias, IaC y recuperación

[Resultado porCT](evidence/2026-11-06-d041-wave.json),
[auditoría final](evidence/2026-11-06-d041-final.json),
[13runtimesprevios intactos](evidence/2026-11-06-d041-accepted-unchanged.json),
[canalTelegram](evidence/2026-11-06-d041-telegram-channel.json),
[tiempo](evidence/2026-11-06-d041-time.json).

Cambios: [factoría](../../scripts/prepare-aligned-exporters.py),
[contratosHTTP](../../services/common/approved-rollout.yml),
[adaptador](../../scripts/run-critical-exporter-wave.py),
[capturaRAM](../../scripts/exporter-memory-alignment.py) y
[runner](../../scripts/rollout-approved-exporters.py). Configuración persistente
representada enrepositorio; sin dependencia de editsmanuales enproducción.

Backupsprivadospor`<run>/<CT>` bajo
`~/.local/share/mailerblend-recovery/phase4/` y
`/mnt/storage/mailerblend-recovery/phase4/`enPVE. Runs exactos enJSONfinalporCT.
Archivos:exporters-before.tar/exporters-after.tar.gz y
monitoring/integration-before.tar/integration-after.tar.gz. Mantener imágenes,
originales,candidatos,configuraciones,HALTs y evidencias. Restaurar uncheckpoint
antiguo sobreestado17 podría retirar integraciones posteriores: exige plan
coordinado yalcance específico. Noejecutar nuevamente elrunD041.

## Qué queda fuera del cierre de cobertura

El17/17 acepta exporters e integración, **no** saludfuncional de todaslasapps,
UATni certificación de todaslasreglasfor/rutasTelegram.615/614503,healthchecks
heredadosBudibase/API/Focalboard,digestEVA yNucleotecnológico siguen abiertos.
AlertasF5,dashboardsF6 yseguridad/hardeningIaCF7 requieren sus propiosalcances.
Complementos heredadosF4 (jobpropioGrafana,sondasJournal/fuentePVE) conservan
suestado pendiente; no se declaran realizados por tener17exporters.
NoTerraformapply,apps/DB/recursosPVE,limpiezas,commit ni push. Política cerrada,
permisosvacíos,sin siguienteCT. Próximopaso: revisar pendientes yautorizar F5,
noiniciarla automáticamente.
