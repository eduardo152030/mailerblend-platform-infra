# CT 614 — recuperación sGTM D-044

## Resultado: DONE

Intervención autorizada sobre la configuración Compose activa. Preview y sGTM
están **healthy**; `/healthz` local (8092/8091) y público (`/preview/healthz`,
`/healthz`) devuelve HTTP 200 sin cabeceras especiales. Sin errores graves de
arranque detectados. La renovación del proceso resolvió el 503 del bootstrap
caducado documentado en [D-043](CT614-SGTM-D043.md).

Se conserva la misma imagen `gcr.io/cloud-tagging-10302018/gtm-cloud-image:stable`,
ID `sha256:16c407168e2089ef6ed6a43253be1294a2bf693dbdef98e05283ef1299dff8ba`.
Variables y secretos, puertos, recursos, volúmenes y configuración de aplicación
sin cambios. Compose base conserva su hash original. Otros contenedores intactos.

El único cambio efectivo de configuración es el healthcheck:
`CMD /nodejs/bin/node /app/health_checker_bin.js`, intervalo 30s, timeout 10s,
reintentos 3, inicio 30s. Está declarado en
[overlay versionado](../../services/infra-nucleoedge/proposals/d043/healthcheck.native.yml)
y aplicado en `/opt/infra-nucleoedge/healthcheck.native.yml` junto a la base activa.
No se utilizó el Compose histórico del repositorio.

## Validación y limitaciones

- Preview validado antes de recrear el principal en la ejecución aceptada.
- Segunda aplicación idempotente, sin cambios de ID ni fecha de arranque.
- Sin nuevos OOM; contenedores finales con RestartCount 0. Esto no cuenta recreaciones.
- Prometheus y Alertmanager disponibles: 17 Node, 17 cAdvisor y 11 Blackbox UP.
- Dos sondas collect: muestras posteriores al arranque con éxito y HTTP 200.
- Contadores Telegram conservados: 132 notificaciones, 56 errores históricos;
  ningún incremento observado. No se realizó una nueva prueba de recepción humana.
- No cambios de Nginx, EdgeRouter, DNS, Google Cloud, sondas ni imágenes.
- No eventos GA4 de prueba enviados. Salud HTTP no certifica entrega GA4 extremo
  a extremo. No se ha cuantificado posible pérdida de solicitudes durante recreaciones.

[Evidencia final](evidence/2026-11-06-d044-live-final.json),
[ejecución aceptada](evidence/2026-11-06-d044-accepted.json).
La marca `recovered_original_configuration` en el historial del helper describe
recuperaciones intermedias; la configuración final activa usa el overlay nativo.

## Incidencias de ejecución, recuperadas

Hubo errores del script de validación que causaron recreaciones adicionales:

1. Preflight local: import de urllib sombreado; fallo antes de modificar producción.
2. Comparación de DNS vacío `null` frente a `[]`: falso cambio; se restauró Preview.
3. Una muestra Blackbox fallida retenida durante la transición disparó recuperación.
   La ventana de evaluación de unos 26s no demuestra 26s de indisponibilidad real.
   Se exige ahora una muestra nueva posterior al arranque, con espera acotada de 90s;
   no se acepta una muestra fallida ni se ocultan fallos compartidos.
4. Reentrada comparaba el ID principal con el primer baseline, anterior a una
   recuperación. Se corrigieron referencias por intento y el alcance del rollback.

Conteo auditado de comandos force-recreate: **7 Preview y 4 sGTM** incluidos
rollbacks; no solamente las dos recreaciones previstas inicialmente. Se verificó
configuración original antes de cada reentrada. Resultado final aceptado, sin más
recreaciones pendientes. Los errores anteriores permanecen en las evidencias
`d044-recovery`, `d044-completion`, `d044-final` y los diagnósticos asociados.

[Orquestador IaC](../../scripts/recover-sgtm-614.py): backup externo obligatorio,
comparaciones estrictas, secuencia por servicio, recuperación y evidencia filtrada.
Pruebas de regresión: 9 del recuperador y 3 de la propuesta, todas PASS.

## Backups y recuperación

Run productivo: `sgtm-614-d044-20261106T211738Z`.
Backup privado de Compose activo, configuración efectiva, inspecciones e imagen:

- CT: `/opt/infra-nucleoedge/.runtime/sgtm-614-d044-20261106T211738Z/backup.tar`.
- PVE: `/mnt/storage/mailerblend-recovery/sgtm-614-d044-20261106T211738Z/backup.tar`.
- Externo: `~/.local/share/mailerblend-recovery/sgtm614/sgtm-614-d044-20261106T211738Z/backup.tar`.

119859200 bytes; SHA256
`776a8c4a69506d0f4e190dd08ee44c283568e30ffc073f9b13293f8fb39ffcb9`.
Archivo y miembros legibles, imagen validada y copias PVE/externa con mismo hash
antes de intervenir. Mantener permisos privados: contienen secretos. No borrarlos.

El mecanismo de recuperación fue ejecutado: Compose base original, imagen local
sin pull, servicios afectados únicamente. No puede recuperar el bootstrap antiguo
en memoria; cualquier nuevo arranque depende del bootstrap servido por Google.
La base sola restaura también el healthcheck curl defectuoso; no es el estado
final deseado. Mantenimiento futuro debe conservar **ambos** archivos activos:

```bash
docker compose --project-name infra-nucleoedge --project-directory /opt/infra-nucleoedge -f /opt/infra-nucleoedge/docker-compose.yml -f /opt/infra-nucleoedge/healthcheck.native.yml config --quiet
```

Este comando valida sin desplegar. No ejecutar nuevamente el recuperador como
comprobación: su modo de ejecución fuerza recreaciones y requiere una intervención
explícitamente autorizada. No aplicar el Compose histórico del repositorio.

## Evitar una nueva caducidad — propuesta, NO implementada

[Google documenta](https://developers.google.com/tag-platform/tag-manager/server-side/manual-setup-guide)
la necesidad de reiniciar periódicamente para obtener código reciente y recomienda
la comprobación nativa. El bootstrap inspeccionado establece un temporizador base
de 12–14 días con ajustes de calendario. La imagen fija no fija el JavaScript que
Google entrega al arranque. `unless-stopped` no renueva un proceso que continúa
vivo aunque esté unhealthy: las [políticas Docker](https://docs.docker.com/engine/containers/start-containers-automatically/)
se activan por salida del proceso o reinicio del daemon.

Propuesta para revisión: mantenimiento semanal, primero Preview, validar salud
nativa y después principal, con backup, exclusión mutua, comprobación de acceso a
Google, muestras nuevas de Blackbox, límite de intentos y parada ante fallo.
Empezar con recordatorio y ejecución supervisada; automatizar solo tras revisar
riesgos y autorización. No se instalaron timers, cron ni autoheal.

Riesgos: un único servidor principal tiene una interrupción breve al recrearse y
puede perder solicitudes; Preview pierde sesiones de depuración; dependencia de
red/config/bootstrap de Google, cambios de código remoto pese a imagen fija,
y bucles o recreaciones simultáneas si se automatiza mal. Si se exige continuidad
sin pérdida, estudiar redundancia separadamente. No se modificaron recursos ahora.

## Cierre

Fase 4 mantiene 17/17 exporters aceptados; esta intervención recupera la aplicación
CT 614. CT 615 y tareas F5/F6/F7 siguen separadas. Sin commit ni push. No hay nueva
autorización para ejecutar otros servicios. Tiempo en la evidencia de cierre.
