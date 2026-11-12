# Fase 7.4 — D082: aceptación final de Voicebox + Qwen

Fecha: **12 de noviembre de 2026, Europe/Madrid**. Evidencias operativas enUTC.

**D-081 — ACCEPTED / PRODUCTION.** El propietario escuchó y aceptó expresamente
voz y contenido. Implementación y aceptación de Fase7.4 **DONE / ACCEPTED**;
publicación Git del cierre en curso, pendiente del recibo final de esta intervención.
Fase7 global sigue IN PROGRESS; no se cierran7.2,7.3 ni tareas ajenas.

## Configuración final conservada

| Componente | Configuración aprobada |
| --- | --- |
| LXC | CT627 infra-voicebox, running |
| Recursos |15360MiB RAM,3vCPU,2048MiBswap,50GiB disco|
| Motor |Qwen3-TTS Base0.6B, FP32/SDPA,3hilos,semilla42,español|
| Perfil |Eduardo — Mi Voz; referencia real ytranscripción confirmadas|
| Arquitectura |TalkerA→checkpoint persistente→Afinalizado→DecoderB|
| Decoder |bloques300/contexto25; recorte original de referencia|
| Guardas |CT14GiB, workerhard9GiB/parada8,2GiB; swap/PSI/cancelación conservados|
| Entrada/plazo |1200caracteres;900s por generación; unjob serial, sinretry automático|

Imagenapp `sha256:09774c5b7c535185c901557ddb6c69a4f8bb38ceff2c6998e19bab403b8e94ea`.
Imagenworker `sha256:bcc5c14f88064ffa76f813d788d183918b208deba45075d8118a2b07c60c248b`.
Modelo fijado enrevisión `5d83992436eae1d760afd27aff78a71d676296fc`.
No se cambia runtime, modelo, recursos, parámetros ni arquitectura enD082.
NoR/A/B, optimizaciones nuevas, inferencias ni reinicios/recreaciones.

## Evidencia aceptada por el propietario

D081:1059caracteres completos, una narración continua y unWAV de **57,36s**,
generado en **676,18s**;EOS718tokens de secuencia, checkpoint1029×16int64 íntegro,
picoCT9,625GiB, sin nuevosOOM. A terminó antes de B, sin mantenerTalker cargado.
La aceptación de voz ycontenido es humana yexplícita del12nov2026. Las cuatro
variantes deASR registradas enD081 son observaciones históricas, no un rechazo ni
una corrección de pronunciación implementada enD082.

[WAV aceptado, disponible solo en la red privada](http://192.168.1.127:17493/audio/baa61a95-c7b4-4524-8229-aa697b941710).
El archivo, la referencia biométrica ylos checkpoints no se publican enGitHub.
Alcance aceptado: generación continua de **aproximadamente un minuto**.
No se considera validada una narración de5–10min ni se promete unRTF constante.

## Estado real de producción

Verificador de lectura `release-d082/verify-production.py`: LXC running,
Voiceboxhealthy, agenteactivo, imágenes exactas, recursos yfuentes aprobados.
Historialcompleted ydescargaWAV conSHA comprobada. Checkpoints D080 yD081:
COMMITTED,manifest,codesNPY yEOS verificados sin importar ni cargarQwen.
Modelo disponible por archivos/revisión fijados; no se vuelve a generar audio.

La comprobación de datos frente albackupD081 acredita perfil/muestras y91archivos
protegidos intactos, originales yWAV anteriores preservados. Exporters627 responden
HTTP200; no inferencias residuales. Se compara identidadDocker yOOM antes/después
del procesoGit para comprobar que publicar no modificó producción.

La presión global delhost yla memoria disponible se registran separadas. PSIglobal
previo puede ser distinto decero; no afirmar que caché equivale amemoria anónima ni
que toda ella es recuperable. Sin presión crítica según guardas vigentes en la
comprobación local; incidencia centralPrometheus anterior fuera deeste alcance.
No se interviene enotrosLXC, Prometheus, Grafana o pipeline de vídeos.

## Documentación y reproducibilidad

- [OperaciónUI, jobs, checkpoints ycancelación](../../services/infra-voicebox/consolidation-d081/RUNBOOK.md).
- [ReconstrucciónIaC, despliegue, rollback ytroubleshooting](../../services/infra-voicebox/release-d082/README.md).
- [InventarioCT627](../inventory/627-LXC-INVENTORY.md), inventarioYAML, main.tf,
  Compose,image-lock yfuentes supervisor/worker versionados.
- NotesPVE627 actualizadas para reflejar aceptación yconfiguración final; plan
  dirigido exclusivo description627 yreconciliaciónTerraform sin cambios derecursos.
- Informes D062–D081 conservados como antecedentes; sus enlaces a capturas privadas
  se identifican como tales yno publican los píxeles. Guías activas apuntan aD082.

Pronunciación: **trader→tréider comprobado**; **hola: incidencia pendiente**.
No se aplica automáticamente una corrección. Cualquier transformación fonética
futura corresponde solo alTTS; eltexto original destinado asubtítulos debe conservarse
sin sustituciones. D082 no implementa esa transformación ni toca elpipeline.

## Backups y recuperación

BackupD081 externo:103archivos,SQLiteintegrityok,5WAV completados y1referencia
verificados enrestauración aislada D082. Incluye originales privados,jobs yfuentes.
ArchivoDockerOCI externo de1279369082bytes,ambas imágenes fijadas y39blobs conSHA
verificados. Locks de versión yreferencias de modelo encheckout; pesosHF protegidos
persistentes enCT. SnapshotD081 deljob nuevo ycheckpoint legibles fuera deCT.
No se borran backups históricos ni se restaura sobre producción para probarlo.

Elcheckout no contiene laidentidad vocal: una recuperación exige además elbackup
privado coordinado ymodelos fijados. No confundir larecuperación de aplicación con
unensayoDR completo delhost. Elrunbook distingue restaurar imagen/configuración de
restaurar datos; nunca revertirBD para deshacer un cambio decódigo.

La captura final D082 incluye además el estado aceptado completo: **117archivos,
6WAV y1referencia**, conSQLite restaurado yla filaD081 completed/57,36s
comprobada. Copia privada fueraPVE; [recibo](evidence/2026-11-12-d082-accepted-backup.json).
Receta versionada `release-d082/backup-accepted.py`; no se publican susdatos.

## Git, privacidad y validaciones

Rama `main`, upstream `origin/main`, remotoGitHub configurado
`git@github.com:eduardo152030/mailerblend-platform-infra.git`.
Fetch inicial seguro:HEAD yorigin/main sincronizados0/0, sin reescritura ni forcepush.
Se revisan ystagingan rutas explícitas. Cambios ajenos conservados, especialmente
CRM/EVA, servicios noVoicebox ylas modificaciones deotrosCT en targets.
En targetsnode/cAdvisor se prepara solo la adición627 para elíndice Git,
sin sustituir elarchivo de trabajo ni publicar cambios ajenos.

Se excluyen credenciales,.env,tfvars,estadosTerraform,claves privadas, audios,
referencias biométricas,pesos,NPY,SQLite,backups,OCI ycapturas privadas. Los patrones
que detectaron fixtures negativos de tests (cabeceraPEM sin clave yURL ficticia)
fueron revisados como datos sintéticos; no son credenciales. Se compara además
contra fragmentos de latranscripción privada real sin publicar sucontenido.

Validaciones: pruebasVoicebox en runtimeCPU aprobado sin modelos ni red,
provisioning/inventario, sintaxisPython/Bash, Terraformvalidate, plan exclusivo627,
enlaces locales ygitdiffcheck. Recibo yconteos exactos al cierre. No se instalan
librerías enproducción para satisfacer tests de la estación local.

## Commits y publicación

Commit funcional local: `b55a7f99480017fffcbeff4a3106115d65ee10ea`.
Pendiente de completar con el reciboGitHub ylos commits documentales. No se declara
publicado por haber preparado uncommit local. La entrega requiere push normal,
confirmación deSHA remoto ysin commits locales deeste cierre pendientes.

## Limitaciones conocidas y estado de Fase7.4

- Alcance aceptado≈1min, no5–10min;1200caracteres y900s permanecen.
- UI puede iniciar en1.7B: elegir0.6B expresamente. No reconstruir frontend aquí.
- RecuperaciónB requiere checkpoint validado yrevisión; no retry automático.
- Pronunciación dehola pendiente; trader→tréider no altera subtítulos originales.
- API soloLAN; hardening/DR global yla incidencia centralPrometheus no se cierran.

Fase7.4: implementación **DONE / ACCEPTED**, conD081 enproducción. La finalización
de publicación D082 se registra separada hasta comprobar elpush. Sinfuncionalidades
nuevas después deeste cierre.
