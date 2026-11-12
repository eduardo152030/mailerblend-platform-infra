# Fase 7.4 — D081: consolidación y narración continua

**Aceptación posterior D082, 12nov2026: D081 ACCEPTED / PRODUCTION.**
El propietario escuchó yaceptó voz ycontenido. Las observacionesASR ypendientes
inferiores describen elestado histórico deD081; no anulan la aceptación posterior.
[Cierre definitivo](PHASE7-D082-VOICEBOX-FINAL-ACCEPTANCE.md).

Seguimiento12noviembre2026 Europe/Madrid; marcas UTC de evidencias conservadas.
**Consolidación técnica DONE; único ensayo completado, WAV57,36s.** D08028,56s aceptado por
elpropietario como referencia técnica funcional, sin extender aceptación acústica
alnuevo audio. No commit/push, R/A/B ni cambios de modelos/recursos/guardas.

## Versión funcional preservada

Voicebox imagenD07909774c5b… yworkerD069bcc5c14f… fijadas sin sustitución;
Base0.6B snapshot5d83992436eae1d760afd27aff78a71d676296fc,FP32/SDPA,3hilos,
Eduardo/es/42, A→checkpoint→PID0→B300/context25. CT15GiB/3CPU/2GiBswap,
guardaCT14GiB, workerhard9GiB/stop8,2GiB,controles swap/PSI y900s intactos.

Backup previo103archivos: datos,SQLite,originales,jobs/checkpoints yfuente worker;
copia privada fueraPVE,manifestSHA ySQLiteintegrity verificados. Snapshot privado
delsupervisorPVE yfuentes locales; archivoDockerOCI externo contienelas dosimágenes
funcionales ytodoslosblobsSHA fueron verificados contra losIDs fijados. ModelosHF
permanecen fijados yconservados enCT; no se declara estacaptura DRintegral delhost.
Elbackup incluyecheckpoint yWAVD080 ylosintentosD078, sin borrarlos ni sobrescribirlos.

Consolidación de fuentes bajo services/infra-voicebox: source-lock.json ycaptura
privada42archivos antes delensayo; lockdeimágenes actualizado conarchivoOCI verificado.
Código/Terraform/inventario/Compose/Notes ydocumentación permanecen locales, sinstage,
commit nipush; loscambiosprevios ajenos de laárbol no se atribuyen aesta intervención.

Corrección mínima en deploy.sh: reconocer integraciónD079 además deD077 para evitar
ruta antigua depreparación/modelos. Copia previa conservada enCT. Dosaplicaciones
reales preservan ID/StartedAt/restartcount eimagen; no reinicios ni recreaciones.
No se modificó runtimeML niAPI/frontend. Notes627 sincronizadas mediante plan
revisado exclusivo description627 yreconciliación refresh-only, sin otrosLXC.

[Runbook](../../services/infra-voicebox/consolidation-d081/RUNBOOK.md) describe uso,
preflight,cancelación,checkpoints yrollback. UI puede iniciar selector1.7B: elegir
Qwen3-TTS0.6B expresamente. No se reconstruye frontend para cambiar esedefault.

## Texto y preflight

Texto literal adjunto1059caracteres/1074bytesUTF8, inferior allímite1200.
SHA256a29d9c360200ef3277ea5a6f7ccbeff03cf763deef9df32373fb7ee7b10c413c.
Paréntesis ypuntuación conservados; validación exacta delPOSTUI, sintruncar.
ElbackendQwen aislado evita elchunking deotrasrutas aunque UImax_chunk_chars800.
SemillaUI puede sernull; eladaptador personal yeljob fijan42, no aleatoria.

Preflight trasarchivarimágenes: CT5997715456bytes,proyección11366424576bytes<14GiB.
HostMemAvailable23047483392bytes,CTswap4096bytes,PSIlocal0,sininferencias.
91archivos protegidos idénticos yperfil/muestras sin cambios; D080checkpoint incluido.
Guardas probadas con22tests puros, cancelación comprobada enD077sintético; no se
interrumpeuntrabajo real para volveraprobarla. Exporters627 yVoicebox responden.
No se modifican ni seoperan Prometheus/Grafana, otrosLXC opipeline.

## Ensayo único

Una pulsaciónUI Generate, seleccionandoEduardo,Spanish,Qwen0.6B; POSTcapturado y
validado literalmente. Jobbaa61a95-c7b4-4524-8229-aa697b941710, directorio privado
/srv/voicebox/qwen-worker/jobs/baa61a95c7b445248229aa697b941710.
Sinreintentos automáticos ni fragmentación. Resultado técnico completado, sin nuevo intento.

## Resultado del único ensayo

[Escuchar/descargar WAV](http://192.168.1.127:17493/audio/baa61a95-c7b4-4524-8229-aa697b941710).
**Duración real57,36s**, ligeramente superior a50–55s. No se cambió texto, semilla,
velocidad ni se añadió silencio. Una sola petición desdeUI yuna sola narración,
no variosWAV concatenados. Historialcompleted, errornull; exportación UI coincide
porSHA conAPI. Calidad acústica ylectura literal pendientes deescucha delpropietario.

| Medida | Resultado |
| --- | --- |
| CargaTalker, intervaloentre eventos |2,724s|
| Referencia preparada desde inicio worker |22,914s|
| GeneraciónTalker |540,131s,718tokens de secuencia,EOS verdadero;1,329tokens/s|
| ProcesoA /supervisiónA |563,181s /575,456s|
| Checkpoint |1029×16int64;312pasos referencia+717generados; hashes verificados|
| LiberaciónA antesB |PID0,runningfalse,cgroupvacío,checkpointverificado|
| ProcesoB /supervisiónB |89,090s /99,221s; sinTalker niencoder|
| Totalagente |676,180s,11min16s, dentro de900s|
| WAV |1376640muestras,24kHz,mono,PCM16,57,36s|
| PicoCT A / B,muestreado |9,625GiB /7,292GiB|
| RSSHWM proceso A / B |5,592GiB /2,537GiB|
| PicoanónimoCT A / B |4,717GiB /2,302GiB|
| PicofileCT A / B |4,893GiB /4,595GiB|
| PicokernelCT A / B |0,403GiB /0,398GiB|
| SwapCT A / B máximo |4KiB /0; sincrecimiento sostenido|
| PSIlocal fullavg10 máximo A / B |0% /0%|
| CPUCTacumulada A / B |1319,157s /187,540s, incluye residentes|
| HostMemAvailable mínimo A / B |16,831GiB /18,862GiB|
| EventosCT |high251→251,max0→0,OOM0→0; hostOOM0→0|

Picos porcomponente no necesariamente simultáneos. RSSHWM puede superarRSSmuestreado
porcaptar picos entre lecturas. ArchivoOCI nuevo calentó caché durante consolidación;
por eso elbaseline≈5,59GiB supera alD080≈4,53. No confundir file conanon ni interpretar
eseincremento comootro modelo residente. Margen trasreclamaciónD079 másCT15GiB yguarda14
permitieron esteensayo sin tocar cachés/guardas niotrosLXC durante lageneración.

Checkpoint persistenteprivado en
`/srv/voicebox/qwen-worker/jobs/baa61a95c7b445248229aa697b941710/checkpoint`.
Copia privada externa deljob completo, validada desdeunproceso nuevo porNPYint64,
dimensiones,EOS yhashes sin cargarQwen. D080checkpoint yWAV conservados.
BrutoB SHA `ee715445de5c817200d9be19825e5a5d6e1934be8c051ee73b805a8c6e0e38c2`;
API/UI SHA `6da5f689b7c939ef069c8ede664888ed42fa31bd0d0f3f15e2f03ff9dccc014c`.
Diferencia pornormalización Voicebox; idénticosframes/duración. Elrecorte referencia
fue599040muestras; no se incluyó lagrabación original en elWAV final niGit.

## Contraste de contenido ysilencios

Whisper small ya disponible enla máquina local, CPU3hilos, archivo deweightsSHA
verificado, sin descargar modelos ni cargarlos enCT627. Se ejecutó después delTTS,
sin initial_prompt ni alimentar eltexto esperado alreconocedor. ASR19,30s;
163palabras esperadas frente164reconocidas trasnormalizar puntuación/caja.
No señala frases omitidas nirepeticiones extensas, pero existen estasdiferencias:

| Texto solicitado | ReconocimientoASR |
| --- | --- |
| cuesta |cueste|
| agotamiento |agotamientos|
| ininterrumpido |ininterrumpidos|
| separarlas |separar la|

**No se certifica reproducción literal**: pueden ser variantes pronunciadas oerrores
ASR yrequieren escucha. No se modifica audio para ocultarlas ni se repiteTalker.
Tampoco seacepta fidelidad/acento pornormalización textual. DetectorlocalFFmpeg
-40dB no encontró silencios≥0,8s; rms≈0,1,pico0,574. Framesfinales coinciden conB,
sinpadding niestiramiento: no hay silencio añadido para alcanzar duraciónobjetivo.
Los signos/paréntesis están íntegros eninput/job; ASR no valida signos no pronunciados.

## Estado final, cambioslocales yrollback

Voicebox healthy, agenteactivo, ningúnworker/inferenciaresidual; imagen,ID,StartedAt
 yrestartcount idénticos abaseline. 91archivos protegidos yfilas perfil/muestras
iguales albackup. Configuraciones deotros17LXC iguales. Exporters627respondenHTTP200.
No se tocaron Prometheus,Grafana nipipeline, ni recursos, guardas ocomponentesML.
La anterior incidencia centralPrometheus no se da porresuelta conestas comprobaciones.

La BD tenía6filas degeneraciones albackup y6al cierre: se añadióD081 yhubo una
petición separada `DELETE /history/73a3755f-5b19-4d33-aba3-79e43bf6d72b` a07:38:27UTC,
antes delPOSTD08107:38:43UTC. Los scriptsD081 no emiten eseDELETE; autor no establecido.
Se conserva carpeta fallida íntegra yfila enbackup, pero no se reinserta para no
revertir unaacciónseparada deUI. No se afirma historial idéntico ni se pierden sus
evidencias. Eloriginal86dde73b… permanece también privado comoantes.

CambiosD081 deconsolidación: deploy.sh (rutacorrectaD079), image-lock (archivoOCI
verificado), README/NOTES/runbook, recetas ysource-lockdeconsolidation-d081, informes,
inventario generado ydocumentación central. Main.tf,workerML,supervisor/guardasD080,
Compose,modelo,referencia ysemilla funcionales se conservan. PendientesGit heredados
D062–D080 yotros cambios ajenos no se stagean,revierten ni se atribuyen aD081.

Rollback deconfiguración documentado enrunbook; imágenes exactas ydatos restaurados
fueraPVE porhash/SQLite, no se simula undespliegue real derestauración. Captura de
fuentes locales permite revisar todo sincorrer unbuild. Fuente/runtime no equivalen
aDRcompleto dehost omodelosHF. No se ha restaurado sobre producción para probarlo.
22tests guardas/checkpoint y16inventarioPASS; bashsyntax,PythonAST,enlaceslocales,
frescura deinventario ygitdiffcheck revisados al cierre. Sincommit nipush.

## Evidencias y cierre

[Input](evidence/2026-11-12-d081-input.json),
[backup](evidence/2026-11-12-d081-backup-verified.json),
[imagenapp](evidence/2026-11-12-d081-app-image-verified.json),
[imagenworker](evidence/2026-11-12-d081-worker-image-verified.json),
[reconciliaciónidempotente](evidence/2026-11-12-d081-reconcile.json),
[preflight](evidence/2026-11-12-d081-preflight-final.json),
[envíoUI](evidence/2026-11-12-d081-ui-submission.json),
[resultado yrecursos](evidence/2026-11-12-d081-result.json),
[exportUI](evidence/2026-11-12-d081-ui-final.json),
[contrasteASR](evidence/2026-11-12-d081-content-validation.json),
[checkpointexterno](evidence/2026-11-12-d081-checkpoint-backup-verified.json),
[postflight](evidence/2026-11-12-d081-postflight.json),
[final](evidence/2026-11-12-d081-final.json).

Fase7.4 **IN PROGRESS**. Consolidación yúnicoensayo DONE técnicos; duración50–55
estricta no alcanzada (57,36s), voz/lectura pendientesdeaceptación. Detenido tras
únicoTTS; ASR esvalidaciónlocal,nounsegundoensayoQwen. Siguiente: escucha delpropietario,
conénfasis enloscuatro pasajes indicados. No másinferencias nioptimizaciones conesta
intervención; R/A/B ypreparación reutilizable dereferencia permanecen sin implementar.
