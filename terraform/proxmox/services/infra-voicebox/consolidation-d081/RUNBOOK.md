# Fase 7.4 — operación Voicebox/Qwen funcional D080–D081

**D082: D081 ACCEPTED / PRODUCTION.** Voz ycontenido delWAV57,36s aceptados
el12nov2026. [Cierre, reconstrucción ytroubleshooting](../release-d082/README.md).
Las advertencias sobre aceptar muestras futuras se conservan; no anulan estaaceptación.

## Uso normal

Abrir http://192.168.1.127:17493 desdeLAN. Seleccionar **Eduardo — Mi Voz**,
idioma **Spanish**, modelo **Qwen3-TTS0.6B** (no1.7B niCustomVoice), sin personalidad
ni efectos. El selector deUI puede iniciar en1.7B: comprobarlo siempre. La ruta
personal aislada fija semilla42. Introducir eltexto completo, máximo1200caracteres;
una sola pulsación enGenerar. No dividir texto ni reenviar al demorarse.

Un único job mantiene TalkerA→checkpoint privado persistente→liberaciónA→DecoderB.
Presupuesto900s total, sin reintentos automáticos. El historial muestra estado y,
alcompletar, permite reproducir ydescargar unWAV. EOS/WAVválido no prueban contenido
ni parecido: escuchar antes deusarlo. No añadir silencio para cumplir una duración.
D080573caracteres generó28,56s en362,18s, no unRTF garantizado para textosdistintos.

## Recursos y comprobación

CT62715GiB RAM/3CPU/2GiBswap/50GiB disco. Guardas agregada14GiB, workerhard9GiB,
parada8,2GiB; swapdelta128MiB/techo1920MiB, PSIlocal5%sostenido10s. Preflight:
CTactual+4,5GiB+0,5GiB≤14GiB, hostdisponible≥12GiB, sinmodelos/inferencias activos.
Mantener las demás condiciones implementadas enpilot-d077/guards.py ysupervise.py.
Appno cargaQwen; worker usa imagenD069 fijada,FP32/SDPA,3hilos,decoder300/context25.
NoR/A/B ni preparación reutilizable dereferencia implementados.

Leer `/health` y `/qwen-worker/health`, estadoDockerhealth devoicebox yheartbeat.
PVE `voicebox-qwen-627.service` es unagente stdlib exclusivo627 sinlistener; fuentes
en `/opt/voicebox-qwen-627`. App no recibe socketDocker. `/opt/voicebox/deploy.sh`
reconcilia soloapp conimagenfijada, sinbuild/pull ni preparación de modelos para
integracionesD077/D079. Ejecutarlo solo sinjobs activos; no es despliegueglobal.
IaC recursos: inventarioVoicebox +receta maintenance-d080/resize-live.py yreconciliación
Terraform dirigida; consultarD080 antes decualquiercambio, no ejecutarapplygeneral.

## Cancelación y recuperación

La cancelación deUI/API escribe cancel.flag; agente termina elgrupo supervisor,
este mata/verifica contenedor propio ycgroup vacío antes de regresar. No reiniciar
CT627 ni matar procesos ajenos. Para una intervención manual, identificarUUID yfase
exactos; conservar logs yestado. No probar cancelación sobre untrabajo útil como
comprobación rutinaria. La ruta ya fue validada sintéticamente enD077.

Jobs en `/srv/voicebox/qwen-worker/jobs/<UUIDhex>` privados0700/0600. Uncheckpoint
válido exige COMMITTED+manifest+codesNPYint64+hashes+EOS+identidad correctos. Si existe,
no repetirTalker: recuperaciónB requiere revisión yautorización; laUI no reanudaB
por sísola. Sincheckpoint hace falta unnuevo intento explícito; error no afirma
que se han conservado códigos inexistentes. No borrar carpetas para sortear la
protección. Referencia original ytranscripción confirmada no se editan ni publican.

## Backup y retorno a la referencia funcional

Antes de cambios: sininferencias; SQLitebackup coordinado conarchivos de data,
private-originals,jobs ysrc. Receta backup.py deeste directorio crea captura nueva
sin sobrescribir. Copiar fueraCT, verificar SHA, cada archivo delmanifest, SQLite y
CP/WAV. ImagenappD079 yworkerD069 están enarchivoDockerOCI privado externo conblobs
verificados. Restaurar imagenexacta archivada, no reconstruir dependencias flotantes.
modelosHF permanecen fijados yprotegidos enCT; estebackup no es DRintegral delhost.

Rollback configuración: detener/esperar workers, restaurar archivos exactos de
supervisor+unidad ytargetsrc registrados, Compose/image-lock/deploy.sh ytag/Digest
aceptados, iniciar exclusivamente agente627 yreconciliar exclusivamenteVoicebox.
Verificar identidad deimagen, health, heartbeat ydatos. No revertirBD para deshacer
un cambio decódigo. Una restauración dedatos exige snapshotSQLite+archivos coordinados
yun destino aislado validado previamente; no sobrescribir generacionesposteriores.
D080checkpointUUID7f348e9777214f4e827dcf7e1458c045 yWAV28,56s son referencia técnica.

No reinstalar recursos antiguos10GiB/guarda9,5 desdeunrunbookhistórico. No bajarRAM
bajo carga. No prune,down-v,drop_caches global ni borrados deperfiles/modelos/audios.
No modificar otrosLXC, Prometheus/Grafana opipeline porun fallo deeste servicio.
