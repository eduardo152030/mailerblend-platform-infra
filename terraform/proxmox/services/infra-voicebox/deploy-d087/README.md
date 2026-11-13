# D087 — despliegue coordinado exclusivoCT627

**Estado vigenteD087b:** imagen21270364… desplegada/healthy, Qwenes/en listo y
ensayoEnglish aceptado por propietario. Chatterbox deshabilitado tras parada
preventiva worker7GiB; Cnoejecutado. No repetir inferencias automáticamente.
[Informe](../../../docs/roadmap/PHASE7-D087-QWEN-CHATTERBOX-PRODUCTION-VALIDATION.md).

transaction.py recibe --attempt d087b para aislarbackup/context/src. ElBACK ya
existe: nunca borrarlo para repetir. Otrointento requiere alcanceautorizado y
nombre nuevo, backup/preflight actualizados ypreservación deestaintentona.
copy_locked valida nombres, hashes yarchivosregulares, omitiendo cachés;
readinessmaintenance-d087 exige los7archivoscontroller y7worker reales.
Imagen,USER999/entrypoint/CMD yprivilegios se comprueban antes/después; no construir
otraimagen ni ejecutar unapplygeneral/deploy-all. --rollback restauraD081 coordinado
sindatosSQLite, conservandoRAM20/guarda19aprobadas.

backup.py --attempt d087b crea unsnapshotnuevo sinreemplazos; verify-data.py
--baseline valida perfiles/referencias/historial ylos7audiosoriginales.
postdeploy.py es la comprobación sin inferencias yverify-control.py valida cancelación
conhold/hijo sintéticos ysharedlock, sinpesos/audio. No reejecutar susnombresexistentes.

submit-trial.py incluye sololos3textosautorizados. ExigegatePASS, O_EXCL antes
dePOST y resultadoanteriorválido; no reenvía anteHTTPincierto. observe-trial.py
soloGET/descarga; collect-trial.py leeevidencia/checkpoint/métricas. La ausencia de
trial-B-validated.json impide enviarC. disable-failed-chatterbox.py deshabilitó
elrelease deB conprecondiciónexacta; final-check.py verificaQwen ydatosintactos.
Scripts de intentoespecífico no sonrunbooks para reinferir sin autorización.

No originales, WAV, planesTF, basesSQLite niarchivosprivados enGit.
