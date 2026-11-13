# Voicebox + Qwen — versión final D081 aceptada en D082

**ACCEPTED / PRODUCTION**, 12 de noviembre de 2026. El propietario aceptó voz y
contenido del WAV privado de57,36s. No se prueba aquí un nuevo audio ni se amplía
el alcance a5–10min. [Informe final](../../../docs/roadmap/PHASE7-D082-VOICEBOX-FINAL-ACCEPTANCE.md).

**Actualización D084:** rootfs ampliado online a100GiB SSD; runtimeD081 intacto.
Para verificar la configuración actual usar [verificador D084](../resize-d084/verify-production.py)
y[runbook](../resize-d084/README.md); el verificador D082 original exige50GiB
como evidencia histórica yno debe usarse tras estaampliación.

## Configuración que debe conservarse

CT627 infra-voicebox:15360MiB RAM,3vCPU,2048MiBswap,100GiB (D084). ImagenappD079
`sha256:09774c5b7c535185c901557ddb6c69a4f8bb38ceff2c6998e19bab403b8e94ea`;
workerD069 `sha256:bcc5c14f88064ffa76f813d788d183918b208deba45075d8118a2b07c60c248b`.
Locks yCompose fijan las imágenes; `pilot-d077/runtime.py` fija modelo ybackend.
Base0.6B FP32/SDPA,3hilos,semilla42,español,referencia real confirmada.

[Runbook vigente](../consolidation-d081/RUNBOOK.md): usoUI, cancelación, estados,
checkpoints yrecuperación. GuardaCT14GiB, workerhard9GiB/stop8,2GiB; swap/PSI,
1200caracteres y900s. A termina antes de B; decoder300/context25. SinR/A/B.
Seleccionar0.6B enUI aunque elselector inicial muestre1.7B. Historial yExport Audio
probados enD081; no pulsar Regenerate para un simple fallo de descarga.

## Verificación sin efectos productivos

Desde el workspace, ejecutar `verify-production.py` enPVE mediante el SSH estricto
existente, ycomprobar `/health`, `/qwen-worker/health` yexporters627. Elverificador
solo lee: no importa modelos, no crea contenedores ni reinicia. Contrastarlo con
los hashes locales aprobados y las evidenciasD082. La memoria disponible se mide
separada de caché,anon yPSI; no interpretar la abundancia de RAM como ausencia dePSI.

## Reconstrucción ydespliegue coordinados mediante IaC

Este procedimiento es para una recuperación futura autorizada, no una acción deD082.

1. Recuperar el checkout publicado ylos locks. Leer inventarioVoicebox, main.tf,
   variables.tf yelrunbook deprovisioning. Preparar elbootstrapSSH privado existente,
   sin copiar claves privadas aGit. Generar inventario/Notes yrevisar unplan dirigido
   a `proxmox_virtual_environment_container.svc["infra-voicebox"]`; ninguna sustitución
   nidiferencia enotroCT es admisible. No ejecutar `deploy-all` ni unapplygeneral.
2. Para unCT existente, conservar susdatos y suidentidad; no clonarlo de nuevo.
   Elprocedimiento D080 usa `maintenance-d080/resize-live.py` yrefresh-only revisado
   porque BPG0.94 reiniciaría elLXC alactualizarRAM. No reducir memoria bajo carga.
   Enuna recuperación desdecero, validar primero elplan ylos accesos deconsola.
3. Restaurar fuera deproducción elbackupSQLite ylos archivos coordinados; verificar
   todos loshashes, integridadSQLite, WAV ycheckpoints. Conservar UID999 ypermisos
   privados0700/0600 de jobs/referencias; la captura incluye originales privados,
   datos, jobs yfuentes. No sobrescribir trabajo posterior albackup.
4. Transferir elarchivoDockerOCI privado verificado ycomprobar SHA contra elrecibo
   externoD081 yimage-lock. `docker image load --input ARCHIVO_VERIFICADO` recupera
   app yworker exactos; confirmar susIDs antes de continuar. No usar unbuild con
   dependencias flotantes como sustituto silencioso delruntime aceptado.
5. Recuperar `/srv/voicebox/huggingface` conservado ylos modelosPiper persistentes.
   QwenBase debe ser revisión `5d83992436eae1d760afd27aff78a71d676296fc`, conarchivos
   verificados por `pilot-d068/base-model-lock.json`; Kokoro usa model-lock.json,
   Piper su lock. Si faltan pesos, recuperarlos delrepositorio yrevisión fijados y
   validar tamaños/SHA, sin cargarQwen como parte de la descarga. No cambiar revisiones.
6. Restaurar Compose,image-lock,overlayD079 yfuentes worker aprobadas. Fuentes activas
   CT en `/srv/voicebox/qwen-worker/src` yjobs privados persistentes. Recuperar la
   versión D080 delsupervisorPVE ysuunit desde fuentes/backupD081; elprefijo ROOT
   productivo es `/srv/voicebox/qwen-worker`. `maintenance-d080/install-guards.py`
   muestra la adaptación exacta yno debe ejecutarse sobrejobs activos.
7. Verificar launit dedicada con systemd-analyze, arrancar solo elagente627 si
   estaba detenido ycomprobarheartbeat. Reconciliar soloVoicebox condeploy.sh,
   sinbuild/pull. Si imagen/Compose no cambian, debe conservar ID/StartedAt.
   No montar socketDocker enlaapp. No reiniciar exporters uotrosLXC.
8. Comprobarperfil, originales,BD,checkpoint,hashes ydescarga. Repetir reconciliación
   sinrecreación. Una inferencia deaceptación trasrecuperación requiere alcance
   específico; no forma parte delverificador ni delcierreD082.

ElbackupD081 ylos archivos deimágenes están fueraGit. Elcheckout por sísolo no
contiene ni debe contener laidentidad vocal; hace falta restaurar losdatos privados.
No se presenta este cierre como ensayoDR completo delhost.

## Rollback ytroubleshooting

- Fallo de despliegue: conservar evidencias, recuperar Compose/lock/fuentes exactos
  delbackup funcional D081 yreconciliar únicamenteVoicebox. No revertir BD para
  deshacer un cambio de código. Nunca `down -v`,prune o borrados globales.
- Trabajo fallido concheckpoint: validarCOMMITTED,manifest,codesNPY,EOS yhashes;
  conservartodo yrevisar recuperaciónB. La UI no reanudaB automáticamente.
- Sincheckpoint: elerror debe indicarlo; hace falta un nuevo intento explícito,
  no borrar lacarpeta ni repetición automática deTalker.
- Preflight insuficiente: no cargar modelo, medir anon/file/kernel/swap/PSI y
  detenerse. No bajarreserva ni liberar cachés globalmente para forzar entrada.
- Fallo de referencia/modelo: comprobar permisos ylocks, sin editar eloriginal.
- Incidencia de pronunciación: `trader → tréider` comprobado; `hola` pendiente.
  No implementar sustituciones enD082. Eltexto fonéticoTTS futuro debe mantenerse
  separado deloriginal destinado asubtítulos; elpipeline no se modifica.
- Disponibilidad deexporters locales no prueba por sísola lacadena central;
  incidencias previas Prometheus permanecen fuera deeste cierre.

Los pilotosD066–D079, antiguos README yrecetas son antecedentes; no autorizan
volver aBF16/CustomVoice, reducirrecursos, ejecutar limpiadores oexportar datos.
