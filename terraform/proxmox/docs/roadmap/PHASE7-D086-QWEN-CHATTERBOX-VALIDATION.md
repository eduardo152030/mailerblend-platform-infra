# Fase 7.4 — D086: despliegue y validación Qwen/Chatterbox

**Actualización posterior:** el propietario descartó la propuesta USERroot.
Se corrigió el candidato manteniendo UID999 y se validó el arranque real aislado;
no hubo otro despliegue. Ver [corrección UID999](PHASE7-D086-UID999-STARTUP-FIX.md).

12 de noviembre de 2026, Europe/Madrid. **BLOCKED / ROLLED BACK.**
Restauración de producción: **DONE técnico**. D081 sigue ACCEPTED / PRODUCTION.
No se ejecutó ninguno de los tres ensayos reales ni la prueba de efectos.
No commit ni push.

## Resultado

El despliegue coordinado llegó a instalar el controlador, worker y app candidata,
pero la app no superó el arranque ni el control de salud. Se detuvo la intervención
por fallo crítico y se activó el rollback coordinado. **Voicebox vuelve a estar
healthy con la imagen y fuentes D081 originales; Chatterbox está deshabilitado.**
El problema ocurre antes de levantar la API, no durante inferencia ni por RAM.

## Preflight y protección previa

- Voicebox D081 healthy, agente activo, sin jobs queued/running ni workers residuales.
- CT627 conserva3CPU/15360MiBRAM/2048MiBswap/rootfs100GiB local-lvm.
- Memoria CT≈2,22GiB, swap0, PSIlocal0; host MemAvailable≈20,45GiB.
- Thin pool libre124,154GiB/31,03%, por encima del20% mínimo (80,017GiB).
- Candidato exacto19af4754… y sus fuentes/receipts/modelos comprobados por hash;
  no descargas, cambios de modelos, límites o recursos.
- Backups D081(imagen), D082(datos), D084(CT completo HDD) y D085(datos) revalidados
  por SHA. D084 releído íntegramente:3fa4107c… coincide.
- Backup nuevo `/opt/voicebox/backups/d086-before-deploy.tar.gz`:
  **118archivos**, SQLiteok,6WAV y1referencia, restaurados fueraPVE yverificados.
  SHA256 `86ffe1d26259b1af044daa3f5fb2e2cfc33efe70f190ff01637c4a81c4016843`.
  Copia HDD `/mnt/storage/d086-before-deploy/application.tar.gz`.
- Configuración operativa original, imagen/ID/inicio, controller, target de src y
  hashes de27configuraciones PVE guardados antes de pausar el agente.
  Backup de controller/config también enHDD. No se reemplazó ningún backup previo.

La captura de referencia/profiles/SQLite se hizo sin modificar el original ni
cargar modelos. Se preservaron las imágenes D081/D069 y sus locks.

## Despliegue realizado

Receta versionada [transaction.py](../../services/infra-voicebox/deploy-d086/transaction.py),
exclusiva CT627, sin enviar inferencias:

1. Preparó nuevo árbol src con runtime/checkpoint originales más overlay D083/D085;
   conservó el árbol anterior y el target para rollback.
2. Comparó Compose normalizado: únicamente cambiaban imagen/build. CPU, RAM,
   swapDocker, mounts, puertos, entorno y límites permanecían iguales.
3. Pausó el agente dedicado, instaló controller/worker coordinados y habilitó el
   receiptCB con hashes. El heartbeat superó la comprobación es/en y CBready.
4. Recreó únicamente DockerVoicebox con imagen candidata. No reinició CT627.
5. El contenedor no alcanzó healthy: falló el entrypoint repetidamente. No se
   llegó a la verificación funcional API/UI y no se envió POST /generate.

Compose advirtió un contenedor OpenVoice huérfano preexistente: no se eliminó,
no se usó remove-orphans ni limpieza Docker. No se tocó ningún otro LXC.

## Causa demostrada

Ambas imágenes heredan `/usr/local/bin/entrypoint.sh`:

| Imagen | Config.User | Contrato de arranque |
| --- | --- | --- |
| D08109774c5b… |root|EntryPoint adapta directorios y usa gosu para ejecutar app como UID999|
| D08519af4754… |999:999|Mismo EntryPoint, pero sin privilegios para cambiar de usuario/grupos|

El Dockerfile candidato acaba en `USER 999:999`. Los logs mostraron:

```text
error: failed switching to "voicebox": operation not permitted
error: /app/data is not writable by the voicebox user (uid 999)
```

La segunda línea no demuestra permisos incorrectos de los datos: el propio
`gosu voicebox test -w` no puede ejecutarse desde ese contexto. El script termina
en `exec gosu voicebox "$@"`. No se corrigió chmod/chown de las grabaciones.
Se observaron al menos10reinicios del candidato en la captura19:18:14UTC.

**Fallo de cobertura D085:** sus fixtures de API/imports usaban `--entrypoint python`
y omitían el arranque heredado. Validaban backend y DSP, pero no el contrato real
de inicio. La compilación y las pruebas sin voz no acreditaban ese arranque.
No se atribuye el error a Qwen, Chatterbox, BF16, longitud del texto ni memoria.

## Parada y rollback ejecutados

Al detectar unhealthy se interrumpió la espera de la transacción con SIGINT dirigido
solo a su PID; su manejador de BaseException ejecutó el rollback previsto. El
KeyboardInterrupt del log corresponde a esta parada controlada, no a la causa raíz.

Se restauraron Compose, image-lock, image-id, deploy.sh, fuentes PVE originales y
el enlace al árbol src previo. Se deshabilitó CB antes de arrancar el agente original
y se recreó solo Voicebox con la imagen D081. No se restauró ni sobrescribió SQLite,
no se borraron jobs, checkpoints, WAV, modelos ni grabaciones.

Imagen restaurada:
`sha256:09774c5b7c535185c901557ddb6c69a4f8bb38ceff2c6998e19bab403b8e94ea`.
App restaurada iniciada19:18:39UTC (20:18:39Europe/Madrid), posteriormente healthy.
El ID de Docker cambia como corresponde a una recreación; el PID de CT627 sigue31843.
El servidor vuelve a ejecutarse como **UID999**, aunque el entrypoint inicia como root.

Reconciliación adicional del deploy.sh original: **no-op**, mismoID/inicio yhealthy,
sin preparación de modelos. No se repitió el despliegue candidato.

## Validación después de recuperar

- Voiceboxhealthy, API200, agente originalactivo/heartbeat válido.
- Mismas imágenes app/worker y hashes originales de controller, runtime ycheckpoint.
-111archivos protegidos coincidentes; perfilEduardo, referencia yoriginales intactos.
- Tablas perfiles/referencias/generaciones con las mismas huellas lógicas:1/1/6.
- Historial existente accesible y WAV D081 descargable con los mismos bytes/SHA.
- Checkpoints D080/D081 íntegros yEOS históricos conservados; ningún checkpoint nuevo.
- Ningún contenedor de inferencia residual; activos solo Voicebox,cAdvisor,test-nginx.
-27configuracionesCT PVE idénticas alpreflight, incluidos losotros17LXC de servicios.
- Sin OOM, errores kernel I/O/ext4 ni incremento de memory.events respecto albaseline:
  high251/max367 heredados; oom/oom_kill0.
- MemoriaCT2,422GiB, swap0, PSIlocal0; disco libre59,852GiB.
  Thin pool libre124,152GiB/31,03%; reserva20% respetada.

No se generó una nueva prueba española después del rollback: se verifica la
restauración del runtime aceptado y el audio previo, sin exceder la parada ordenada.
El entorno y la imagen candidata permanecen conservados, pero no activos.

## Ensayos y efectos

| Ensayo | Resultado | WAV/tokens/EOS/tiempo/RSS/inferencia |
| --- | --- | --- |
| A — QwenEnglish |NO EJECUTADO|No aplica: falló el control de despliegue previo|
| B — ChatterboxSpanish |NO EJECUTADO|No aplica: secuencia detenida antes deA|
| C — ChatterboxEnglish |NO EJECUTADO|No aplica: secuencia detenida antes deA|
| Robotic/Radio/EchoChamber/DeepVoice |NO EJECUTADOS enD086|No se continuó probando tras el fallo crítico|

No existen nuevos audios para aceptar o comparar. Se conservan los resultados DSP
sintéticos D085 como antecedentes, sin presentarlos como prueba con Eduardo.
La solicitud de efectos se había separado en copias de salida para respetar los tres
ensayos sin efectos; tampoco se procesaron WAV históricos después de la parada.

## Corrección concreta y siguiente autorización

**Propuesta, no aplicada:** conservar el contrato de inicio D081: entrypoint inicia
como root y hace gosu; la app termina ejecutándose como UID999. En el Dockerfile
candidato, retirar/reemplazar el USER999 final por USERroot. No cambiar permisos de
datos ni flexibilizar guardas. Alternativa de reescribir entrypoint es más amplia y
no es la corrección mínima preferida.

Antes de otro despliegue es obligatorio probar el **entrypoint real** en un
contenedor aislado, sin puertos, sin datos productivos, con volúmenes temporales
controlados y capacidades equivalentes a producción. Comprobar startup, salud y
UID999 del proceso. Después repetir la verificación de API/UI/contratos, construir
un tag nuevo y conservar el candidato fallido como evidencia. El test no debe
sustituir el entrypoint por Python ni imponer capacidades incompatibles con gosu.

Se propone además que wait_health aborte en cuanto el contenedor se declare
unhealthy y registre el tipo de excepción, sin esperar el timeout completo.
No se ha ejecutado ninguna de estas correcciones ni un segundo despliegue.

Se requiere nueva autorización para corregir/validar el candidato y repetir el
intento de despliegue y A→B→C. La autorización D086 se detuvo ante el fallo crítico.
La aceptación acústica de los motores nuevos sigue pendiente; no hay versión final
bilingüe ni Chatterbox declarada aceptada.

## Evidencias

[Preflight](evidence/2026-11-12-d086-preflight.json),
[backup restaurado](evidence/2026-11-12-d086-backup.json),
[fallo de startup](evidence/2026-11-12-d086-startup-failure.json),
[restauración verificada](evidence/2026-11-12-d086-restored.json),
[estado final e imágenes](evidence/2026-11-12-d086-final.json),
[reconciliación no-op](evidence/2026-11-12-d086-rollback-idempotence.json).

**Estado final: D086 BLOCKED / ROLLED BACK; D081 productivo healthy.**
Sin inferencias, efectos con voz real, cambios enotrosLXC/pipeline, commit ni push.
