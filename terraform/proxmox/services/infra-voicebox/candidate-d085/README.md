# D085 — candidato preparado, no desplegado

La corrección posterior UID999 tiene imagen separada y prueba real deentrypoint;
ver [startup D086](../startup-d086/README.md). Este tagD085 se conserva como antecedente.

**Actualización D086:** candidato bloqueado por incompatibilidad USER/entrypoint;
rollback D081 verificado. No volver a desplegar este tag sin corregir y probar
el arranque real bajo nueva autorización. [Diagnóstico D086](../../../docs/roadmap/PHASE7-D086-QWEN-CHATTERBOX-VALIDATION.md).

Producción sigue en D081 español. Se autorizaron preparación aislada, dependencias,
pesos selectivos y pruebas sin inferencia. **No arrancar agent.py ni pasar
--execute-real sin aprobación de despliegue y ensayos.**
[Informe D085](../../../docs/roadmap/PHASE7-D085-QWEN-BILINGUAL-CHATTERBOX.md).

## Arquitectura y archivos

Se reutilizan sin alterar los16 archivos del candidato D083. `engine_policy.py`
conserva su validación Qwen y añade admisión Chatterbox exclusiva: Eduardo,
es/en, semilla42,240caracteres. Qwen conserva1200caracteres y900s.
`isolated_chatterbox_backend.py` hereda la comprobación original de referencia y
transcripción, y usa la misma cola persistente con artefactos propios.
`chatterbox_worker.py` emplea MultilingualV3/CPU/FP32, referencia original RO y
procesamiento acústico nativo; no códigos/checkpoints Qwen ni voces predeterminadas.

`agent.py` mantiene A/B Qwen y despacha CB a `supervise_chatterbox.py`, con el mismo
flock ya usado por Qwen. CB propone parada7GiB, hard8GiB,300s,400tokens con EOS
obligatorio y máximo20s de audio para el piloto. Son controles propios preparados,
no guardas Qwen modificadas. El slot no se libera hasta PID0/cgroup vacío.
`readiness.py` requiere un release coherente y explícitamente habilitado; el JSON
propuesto tiene enabled=false. Una instalación o un paquete no habilitan el motor.

`patch.py` amplía el backend D083: factory aislada, contextos por trabajo, admisión,
capabilities, status de modelos y errores de retry antes de modificar historial.
Retry/Regenerate sobre un ID conservado devuelve409; una nueva pulsación Generar
crea un ID nuevo. No se repite Talker ni se reanuda Decoder automáticamente.
La descarga/borrado nativos de Chatterbox quedan fuera de su almacenamiento aislado.

Los cuatro efectos son los presets/DSP existentes. `effects_ui_patch.py` y
`ui/lib/constants/generationEffects.ts` los priorizan sin quitar los personalizados.
El efecto elegido se envía por generación; no cambia los valores del perfil.
La salida limpia se conserva como versión y solo hay un WAV final predeterminado.

## Reproducción, fuera de producción

1. Descargar los archivos fuente de los commits exactos de `sources.lock.json` y
   `ui-source.lock.json`; verificar sus SHA antes de extraer. No seguir master.
2. `prepare_inputs.py --source-archive ARCHIVO_CB --uv UV_FIJADO --out DIR_PRIVADO`:
   valida hashes y cambia únicamente la referencia VCS de Perth por su commit fijo.
3. Transferir entradas a un directorio nuevo CT627 y usar `prepare-env.sh` solo tras
   preflight. Usa imagen base verificada,1CPU/2GiB auxiliares y uv sync require-hashes.
   No ejecutar sobre un venv existente. `requirements.lock` fija todos los paquetes;
   `build-constraints.txt` fija la construcción. No instalar desde requirements.in.
4. `download-models.py` se ejecuta en PVE con el manifiesto seleccionado por stdin:
   solo5 archivos fijados, comprobación cada64MiB de thinpool≥20% y rootfs>20GiB,
   presupuesto12GiB; checksum y escritura atómica. Ante fallo conservar parcial y
   detener, sin reintentos ni borrados. `models.lock.json` recoge los hashes finales.
5. `prepare_cache.py MODELS` prepara el lookup Cangjie offline con hardlink, sin
   duplicar pesos. El watermarker Perth ya contiene su recurso fijado en el paquete.
6. `build_ui.py --archive FORK_FIJADO --bun BUN_FIJADO --out DIR_NUEVO`: extrae el
   fork exacto, aplica D083+D085, frozen-lockfile sin scripts de instalación ybuild.
7. `stage.py --dist DIST_VERIFICADO --out CONTEXTO_NUEVO`: backend/UI/controller/worker
   con manifiesto de hashes. Construir Dockerfile solo comprobando primero la
   imagen baseD081 por ID, networknone y un tag candidato separado. No deploy/pull.

Se preparó `/srv/voicebox/chatterbox-d085` en el SSD. No contiene grabaciones
personales. El worker futuro monta el fichero existente de referencia como RO.
Las imágenes, modelos y backups anteriores no se borraron. Los tar/contextos
privados y los pesos no deben incorporarse a Git.

## Pruebas

```sh
python3 -m unittest discover -s tests/voicebox -p test_d083.py
python3 -m unittest discover -s tests/voicebox -p test_d085.py
node --experimental-strip-types --test tests/voicebox/test_d085_ui.mjs
```

`api-fixture.py` corre dentro de la imagen candidata sin red, sin puertos ni binds
productivos; bloquea loaders y usa DB temporal/dobles. Verifica rutas/historial,
14casos API,8envíos de efectos y4procesamientos DSP sintéticos. No usa tu voz.
`imports.py` verifica dependencias e impide cargar pesos/descargas implícitas.

## Despliegue y rollback pendientes de autorización

Revalidar recursos, cola vacía, salud y backups. `backup-predeploy.py` es exclusivo
CT627, nunca sobrescribe backups y hace SQLitebackup coherente; su copia D085 se
verificó por restauración externa y se conservó también en HDD. Refrescar antes de
un despliegue futuro si ha cambiado algún dato. D084 completo sigue verificado.

Solo tras aprobación: coordinar app+UI, PVEcontroller y srcCT, conservar supervisor
Qwen/guardas, habilitar receipt CB con hashes exactos y comprobar metadata sin audio.
No instalar otra unidad ni abrir puertos. A→B→C, secuenciales, requieren autorización.
No se admite ejecutar las pruebas desde CLI con el agente productivo anterior.

Rollback: drenar/cancelar y verificar ausencia total de workers; restaurar imagen
appD081 y fuentes PVE/CT originales delbackup, deshabilitar CB, mantener datos,
historial y nuevos trabajos. No revertir SQLite ni reducir rootfs100GiB. El entorno
CB puede quedar inactivo; no es necesario borrar sus modelos ni imágenes.
