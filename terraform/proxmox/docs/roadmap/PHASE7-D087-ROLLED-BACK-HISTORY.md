# Fase 7.4 — D-087: CT627 con20GiB, despliegue corregido y rollback

12 de noviembre de 2026, Europe/Madrid. **Recursos DONE técnico; despliegue
ROLLED BACK / BLOCKED. D081 continúa healthy en producción.** A/B/C no ejecutados.

## Resultado de la reanudación

El propietario autorizó RAM20GiB y confirmó expresamente guardaCT19GiB, conservando
los límites individuales de workers, CPU y swap. La ampliación y reconciliación IaC
se completaron en caliente. El intento coordinado posterior falló antes de recrear
la app: la receta intentó copiar el directorio `controller/__pycache__` como archivo.
Su manejador ejecutó rollback coordinado correctamente. **No se reintentó** ni se
inició ninguna inferencia. El problema es de la receta de copia, no del entrypoint
UID999, Qwen, Chatterbox ni del presupuesto RAM.

## Recursos efectivamente aplicados

| Elemento | Inicial | Final |
| --- | --- | --- |
| CT627 RAM |15360MiB|**20480MiB /20GiB**|
| Guarda agregada CT |14GiB|**19GiB**|
| CPU |3vCPU|3vCPU|
| Swap LXC |2048MiB|2048MiB|
| Rootfs SSD local-lvm |100GiB|100GiB|
| Qwen worker |hard9GiB /stop8,2GiB|Sin cambios|
| Chatterbox worker candidato |hard8GiB /stop7GiB /300s|Sin cambios; no ejecutado|

`memory.max=21474836480`, `memory.swap.max=2147483648`. Ni CT627 ni la app
se reiniciaron por la ampliación. Solo el agente dedicado se reinició para adoptar
las constantes autorizadas y durante despliegue/rollback. Al final mantiene las
guardas19GiB y comprobación explícita de RAM20GiB para Qwen.
No se cambiaron presión/swap, semilla, FP32, modelo, referencia, arquitecturaA/B,
bloques300/contexto25, presupuestos, hilos ni parámetros acústicos.

### Capacidad y chequeo físico

Host físico33533042688bytes (~31,23GiB). Al final dispone de
21.856GiB MemAvailable; thin pool conserva
124.143GiB /31.029% libre (>20%).
La RAM configurada es un límite, no una reserva física inmediata.

La lectura completa del backup alteró el reparto de caché: CT bajó aproximadamente
7,7→3,9GiB; no se ejecutó reclamación, borrado ni `drop_caches`. El primer intento
de la receta de recursos se detuvo **antes de cambios** al proyectar llenado hasta
20GiB y exigir reserva física6GiB. Se revisó la estimación para usar el techo
operativo autorizado19GiB, manteniendo esa reserva6GiB (>piso runtime4GiB), y se
revalidó antes de aplicar. No se relajaron las guardas para pasar un ensayo.
Una invocación dependiente de instalación de guardas también abortó en su primera
aserción de RAM20GiB durante ese intento previo, sin modificar archivos.

PSI/swap globales previos siguen registrados y no se atribuyen a627. CT PSI full
avg10 final0%; swapCT14.168.064bytes, muy por debajo de2GiB. La lectura delbackup
produjo crecimiento respecto albaseline de311.296bytes, inferior a128MiB;
no hubo generación. No se aumentaron otrosLXC para compensarlo.

## Terraform e IaC

Se actualizaron inventario YAML, precondición máxima20480MiB, Notes y generados.
La observación anterior15GiB se conservó en historial; la verificación actual20GiB
se añadió solo después de comprobar PVE/cgroup. Protecciones `ignore_changes`
intactas; no apply general ni deploy-all.

1. Plan guardado dirigido únicamente `svc["infra-voicebox"]`: update de memoria
   15360→20480, swap2048; sin creación, destrucción ni otros recursos.
2. BPG0.94 reiniciaría elCT al aplicar memoria: se mantuvo el procedimientoD080,
   receta versionada `pct set627 --memory20480 --swap2048` en caliente.
3. Notes sincronizadas exclusivamente627 mediante la descripción generada.
4. Plan refresh-only dirigido revisado: deriva de memoria/description de627,
   cero mutaciones remotas; se aplicó únicamente ese plan de estado.
5. Plan normal dirigido final: **0cambios**; resto de instancias del estado idénticas.
   Serial 279→280.

[Recetas de recursos](../../services/infra-voicebox/maintenance-d087/README.md).
No se ejecutó un segundo despliegue como prueba de idempotencia después del fallo.
El planfinal sin cambios acredita reconciliación de recursos; no valida la app candidata.

## Backups verificados y recuperación preparada

- D081 imagen externa: SHA `b6fe07c1…9b43` revalidado.
- D082 datos aceptados: SHA `3b1bd7ed…170a` revalidado.
- D085 datos: SHA `9ac082cf…90d1` revalidado.
- D084 CT completo enHDD: SHA completo `3fa4107c…afcb` releído y coincidente.
  La extracción completa histórica D084 se conserva; no se repitió ni se afirma
  restauración de arranque de unCT enD087.
- Backup actualizadoD087: **117archivos**, SQLiteok,1perfil/1referencia/6WAV,
  extraído y verificado fueraPVE. SHA:
  `466deaa31ef647b277d3559198b577b364754d0fae9c02979936b76db2b005ab`.
- Archivo original `/opt/voicebox/backups/d087-before-deploy.tar.gz`, copia externa
  alPVE y copiasHDD en `/mnt/storage/d087-resource-before/application.tar.gz` y
  `/mnt/storage/d087-before-deploy/application.tar.gz`.
- Config627/controlador previo a recursos enPVE `backups/d087-resource-before`
  yHDD; configuración operativa/controlador/src previos aldespliegue en
  `backups/d087-before` y `/mnt/storage/d087-before-deploy/controller`.
- Imágenes D08109774c5b…, workerbcc5c14f… y candidata21270364… conservadas.

No se restauró SQLite sobre producción ni se eliminaron datos. El rollback de app
restaura Compose/locks/deploy.sh, controlador y enlace src, y deshabilita Chatterbox;
**conserva los20GiB/guarda19GiB aprobados**. Volver a15GiB requeriría comprobar uso,
restaurar constantes coherentes y reconciliar IaC; no se hizo automáticamente.

## Despliegue intentado y causa demostrada

Imagen obligatoria verificada antes del cambio:
`sha256:212703647c03d428adc30f8bf4b864af82690eb41f4fe8ca052ff10dbaa45386`.
Config.USER999:999, entrypointcorregido, CMDUvicorn original, sin privilegios añadidos.
La imagen no se reconstruyó y no se usó19af4754… como app de destino.

El bundle de recursos actualiza únicamente controller/worker19GiB y comprobaciones
20GiB, conservando el runtimeML. La imagen21270364… queda intacta. Las funciones
predictivas de recursos del controlador son las activas; el adaptador de la app
conserva validaciones de identidad/idioma/semilla y no carga modelos.
Preflight de ambos motores pasó antes del intento, frente a19GiB. Hashes de release,
fuentes, modelos y receipt fueron verificados. Se guardó el rollback y se pausó
el agente dedicado para copiar el controlador.

La comprobación previa importó `engine_policy` desde el bundle. Python creó
`bundle/controller/__pycache__`. La copia posterior recorría `iterdir()` y llamaba
`shutil.copy2` sobre todas las entradas, incluidos directorios. Error exacto:

```text
IsADirectoryError: [Errno 21] Is a directory: '.../bundle/controller/__pycache__'
```

El fallo quedó dentro del manejador de rollback. Se restauraron controlador,
enlace src, Compose y locks originales; el agente volvió a activo y Chatterbox
quedó deshabilitado. Compose reconoció Voicebox ya en ejecución: **mismo DockerID,
mismo inicio19:18:39UTC y cero reinicios**. No llegó a sustituirse la imagen de app.
El contenedor OpenVoice huérfano previo se conservó; no se ejecutó remove-orphans.

## Corrección local posterior, sin nuevo despliegue

[transaction.py](../../services/infra-voicebox/deploy-d087/transaction.py) usa ahora
`copy_locked`: valida nombres, archivos regulares sin symlinks y SHA de todas las
entradas declaradas; después copia exclusivamente esas entradas del release,
tanto en controller como worker. Ignora cachés y archivos no declarados, sin borrarlos.
El lock se regeneró con los hashes de la receta corregida. No cambia la imagen,
los privilegios ni las guardas.

Pruebas: **37PASS sin inferencia**: D08310Python+4UI, D08511Python+5UI yD0877.
Las siete nuevas cubren guardas19GiB, presupuestos predictivos, límites individuales,
identidad/idiomas/caracteres y copia con caché, hash incorrecto y symlink.
Estas pruebas no equivalen a un segundo despliegue. La copia defectuosa y sus logs
privados siguen conservados en stagingHDD; no se modificaron para ocultar el intento.
La receta rechaza reutilizar `backups/d087-before`; otro intento debe preparar un
identificador y backup nuevos, conservando el fallido, antes de ejecutarse.

## Ensayos y aceptación

| Ensayo | Resultado | Carga / generación / WAV / EOS / picoRAM / CPU |
| --- | --- | --- |
| A — Qwen English |NO EJECUTADO|No aplica: parada por fallo de despliegue|
| B — Chatterbox Spanish |NO EJECUTADO|No aplica|
| C — Chatterbox English |NO EJECUTADO|No aplica|

No hay audios nuevos para escuchar. No efectos convoz real, narraciones largas ni
reintentos. Aceptación acústica bilingüe/Chatterbox pendiente del propietario.

## Estado final

- D08109774c5b… healthy, mismo contenedor/inicio; agente original activo.
- CT62720GiB/3CPU/2GiBswap/100GiB; Qwen guardaCT19GiB y worker9/8,2GiB activos.
- Chatterbox deshabilitado tras rollback, sin modelos precargados ni workers activos.
- PerfilEduardo, referencia/transcripción, SQLite1/1/6, WAV e historial intactos;
  mismo WAVD0812.753.324bytes y SHA6da5f689….
- Checkpoints históricos íntegros yEOS conservados; ningún checkpoint nuevo.
- OOM0; memory.events high251/max367 heredados sin incremento.
- Otras26configuracionesPVE idénticas, incluidos losotros17LXC de servicios.
- Exporters627 HTTP200. Sin cambios de otrosLXC/pipeline, borrados, commit ni push.

**Punto de parada cumplido:** recursos completados, despliegue fallido recuperado;
corrección de copia solo local. Siguiente: revisar esta corrección y autorizar un
nuevo intento coordinado con nombre propio y preflight/backup actualizados,
antes de A→B→C. No ejecutar automáticamente.

## Evidencias

- [Reanudación20GiB, Terraform, backup y estado final](evidence/2026-11-12-d087-20g-resume-result.json).
- [Primer preflight con15GiB](evidence/2026-11-12-d087-preflight-result.json).
- [Observación anterior de presión](evidence/2026-11-12-d087-pressure-observation.json).

## Antecedente: auditoría inicial con15GiB antes de la ampliación

Estas cifras son históricas y quedan sustituidas por la sección de reanudación.

## Preflight real

Captura final UTC: `2026-11-12T20:18:13.599408+00:00`; fecha de seguimiento Europe/Madrid.

| Componente | Medición | Resultado |
| --- | --- | --- |
| Host físico | 31.230 GiB | Sin ampliación |
| Host MemAvailable | 20.585 GiB | Supera mínimos existentes |
| CT627 recursos | 3 vCPU, 15 GiB RAM, 2 GiB swap, rootfs100 GiB SSD | Sin cambios |
| CT memory.current | 7.745 GiB | Se contabiliza íntegro |
| CT anon | 0.366 GiB | Memoria anónima |
| CT file | 6.893 GiB | No se descuenta como memoria ya liberada |
| CT kernel | 0.485 GiB | Incluido en memory.current |
| CT swap | 311296 bytes | Estable durante observación |
| CT PSI full avg10 | 0,00 % | Sin presión local observada |
| Thin pool libre | 124.145 GiB / 31.030 % | Supera reserva20 % |
| Qwen proyección inicial +4,5 GiB +0,5 GiB | 12.745 GiB | PASS frente a14 GiB |
| Chatterbox proyección inicial +7 GiB +0,5 GiB | 15.245 GiB | FAIL frente a14 GiB |

El cálculo de Chatterbox es el de `engine_policy.preflight` preparado en D-085,
no una guarda nueva. Se evaluó su función real, sin importar modelos ML. Con ese
presupuesto, el CT debe empezar como máximo en **6,5 GiB**; faltan
**1.245 GiB** de margen en la captura final. No se redujeron
la estimación de7 GiB, la reserva ni las guardas para hacer pasar el ensayo.
El consumo inicial es mayoritariamente `file`; eso no demuestra su recuperación
inmediata ni autoriza descontarlo. No se reclamó caché ni se alteraron archivos.

### Presión y swap del host

Observación independiente de20 segundos, antes de cualquier despliegue:

- PSI full avg10 del host: 15,86 →13,26 %; CT full avg10 permanece0 %.
- Swap-in: +149213 páginas; swap-out: +89362 páginas.
- Con páginas4 KiB, equivalen a582,863 MiB de entrada y349,070 MiB de salida en20s.
- MemAvailable permanece aproximadamente20,6 GiB; CT swap no crece.
- Sin nuevos OOM: CT oom/oom_kill0 y host oom_kill0.

La actividad de swap no se atribuye a CT627 ni a un LXC concreto: no se realizó
una investigación de los demás servicios. Los controles existentes de Qwen no
clasifican solo la PSI global como parada cuando MemAvailable es suficiente;
**el bloqueo demostrado aquí es el preflight de Chatterbox**, acompañado de esta
actividad global que conviene aclarar antes de otro piloto. No se cambiaron umbrales.
