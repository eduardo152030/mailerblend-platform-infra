# CT 615 — recuperación sGTM D-048

## Resultado: DONE — 06/11/2026 (Europe/Madrid)

`mailerblend-sgtm-preview` y `mailerblend-sgtm-serving` healthy. GET `/healthz`
local en **18092/18091** y público devuelve HTTP200. **Una recreación Preview y
una Serving**, cero recreaciones adicionales y ningún rollback necesario.
Segunda aplicación idempotente sin cambios de IDs/arranque. Ejecución productiva:
**68,444 segundos**, aparte de preparación y documentación.

[Evidencia de ejecución](evidence/2026-11-06-d048-execution.json),
[auditoría independiente de comandos/estado](evidence/2026-11-06-d048-final-audit.json).
F4 exporters conserva 17/17 aceptados; esta intervención recupera la aplicación,
no vuelve a desplegar exporters ni da por terminadas F5/F6/F7.

## Diagnóstico breve y diferencias parametrizadas

[Preflight](evidence/2026-11-06-d048-preflight.json): ambos llevaban 50,06 días
activos; checker curl contra `/healthy`, salud nativa503 y checker Node exit1.
Configuración GTM estructuralmente válida e igual, Preview en modo de depuración;
sin publicar valores. Diagnóstico nativo de edad: límite30d falla500,60d pasa200,
con salud normal503. Junto al mismo digest/bootstrap de D043, atribuye el fallo con
alta confianza a caducidad del bootstrap, además del checker Docker incompatible.
Un 200 con cabecera diagnóstica de edad NO se acepta como salud.

Se revisaron [D044](CT614-SGTM-D044-RECOVERY.md) y
[Issue #1](https://github.com/eduardo152030/mailerblend-platform-infra/issues/1).
Las diferencias no exigen cambiar la configuración de aplicación: nombres de
servicio/proyecto, puertos **18091/18092**, una sonda collect en vez de dos y
**enrutamiento Preview por cabecera bajo `/gtm/`**.

`PREVIEW_SERVER_URL` ya era `https://edge.mailerblend.com` y se conserva exactamente.
Nginx selecciona Preview cuando `X-Gtm-Server-Preview` o `X-Gtm-Preview` no están
vacías; `/preview/healthz` sin esa selección no demuestra salud de Preview.
La comprobación pública correcta usada fue GET
`https://edge.mailerblend.com/gtm/healthz` con `X-Gtm-Server-Preview: 1`, después
de exigir salud local y checker Node200/exit0. Es una cabecera de **enrutamiento**,
no `X-Sgtm-Healthz` de diagnóstico ni un bypass de salud.

La petición `/gtm/healthz` sin cabecera devolvía502 antes de intervenir; no es un
endpoint público de salud incondicional. Su comportamiento sin selección de Preview
no se corrigió ni se usa como aceptación. No confundirlo con fallo de Serving
`/healthz`. [Ruta verificada](evidence/2026-11-06-d048-preview-route.json).
No se envió ningún evento GA4 ni se cambió Nginx/DNS/EdgeRouter/Google Cloud.

## Cambio IaC aplicado

Se reutilizó el mismo [recuperador](../../scripts/recover-sgtm-614.py), ahora con
perfil explícito `--ct 615`; el comportamiento614 por defecto se conserva y **no
se ejecutó CT614**. Perfil fija host, proyecto, base activa, nombres, puertos y
selector de sonda. La misma receta
[healthcheck nativo](../../services/infra-nucleoedge/proposals/d043/healthcheck.native.yml)
se aplica en `/opt/infra-mailerblend-edge/healthcheck.native.yml` sobre la base
ACTIVA `/opt/infra-mailerblend-edge/docker-compose.yml`, no una copia histórica.

Única diferencia efectiva de configuración: healthcheck
`CMD /nodejs/bin/node /app/health_checker_bin.js`, intervalo30s, timeout10s,
3 intentos, start_period30s. Se recreó solo Preview, se aceptó su salud local y
pública, después solo Serving. No pull/build ni actualización de imagen.

Imagen conservada: `gcr.io/cloud-tagging-10302018/gtm-cloud-image:stable`, digest/ID
`sha256:16c407168e2089ef6ed6a43253be1294a2bf693dbdef98e05283ef1299dff8ba`.
Se verificaron igualdad de variables/secretos, configuración, puertos, redes,
montajes y recursos Docker; archivos originales intactos. No había montajes de
aplicación que migrar. CPU2/RAM2048MiB/swap512MiB/red PVE iguales; no cambios PVE.
Los otros contenedores de CT615 conservan IDs/arranque/restarts y estado de ejecución.
No se modificó ningún otro LXC ni configuración de monitorización.

## Validaciones y orquestación

- 21 pruebas locales: 9 contratos D044 y 12 del perfil615, incluidas mismas
  regresiones de DNS vacío, aceptación Preview del intento actual, protección de
  identidad principal y rollback limitado a servicios del intento.
- Diff estructural de Compose: únicamente healthcheck; backup externo obligatorio.
- Preview validado antes del principal. Salud local sin cabeceras especiales y
  checker Node exit0; salud pública de cada backend correctamente enrutada.
- Sin errores graves de arranque detectados, sin nuevos OOM/oom_kill/oom_group_kill.
- Contenedores finales RestartCount0; recuento de recreaciones proviene del log de
  comandos, no de RestartCount. **Preview1 / Serving1**.
- Idempotencia con `compose up` sin force: sin nuevas identidades ni arranques.
- Prometheus/Alertmanager ready; **17 Node / 17 cAdvisor / 11 Blackbox UP**.
- Sonda Mailerblend: muestra nueva posterior al arranque, success1 y HTTP200.
  Espera acotada por frescura, sin repetir vigilancia larga. Ningún reintento de
  transición por probe fallida. No se aceptan muestras fallidas/ausentes como cero.
- Telegram: notificaciones132 y errores históricos56, sin incremento; no se
  envió nueva prueba FIRING/RESOLVED ni se certificó recepción humana.

## Backups y recuperación

Run: `sgtm-615-d048-20261106T221856Z`. Backup privado119859200bytes:

- CT: `/opt/infra-mailerblend-edge/.runtime/sgtm-615-d048-20261106T221856Z/backup.tar`.
- PVE: `/mnt/storage/mailerblend-recovery/sgtm-615-d048-20261106T221856Z/backup.tar`.
- Externo: `~/.local/share/mailerblend-recovery/sgtm615/sgtm-615-d048-20261106T221856Z/backup.tar`.

SHA256: `ccaa003cc5cdb3191e4b200424722f3bb6c075c6ec2d6ec7dede6a97ca7fd8d3`.
Contiene Compose/env existentes, modelo/inspecciones privados e imagen original.
Antes de cambiar servicios se verificaron archivo/miembros, contenido de imagen y
hash idéntico en CT/PVE/copia externa. No es un snapshot completo del LXC ni se
ensayó una restauración funcional nueva en CT615. El mecanismo D044 se conservó;
no ejecutar un rollback real adicional si la intervención ha pasado.

En fallo, parar la secuencia; el helper recupera solo servicios ya intentados,
con base e imagen originales, verifica configuración y conserva cobertura.
Esa base incluye el curl defectuoso y no restaura el bootstrap antiguo en memoria:
restaurar configuración no implica restaurar un proceso previo ni garantizar salud.
Si la recuperación falla, HALT global; no reintentar indefinidamente.

## Operación posterior y límites

Conservar base activa + overlay al mantener este servicio. La validación de
configuración, **sin desplegar**, es:

```bash
docker compose --project-name infra-mailerblend-edge --project-directory /opt/infra-mailerblend-edge -f /opt/infra-mailerblend-edge/docker-compose.yml -f /opt/infra-mailerblend-edge/healthcheck.native.yml config --quiet
```

Procedimiento reproducible de intervención autorizada (no repetir ahora):

```bash
python3 scripts/recover-sgtm-614.py --ct 615 --run sgtm-615-d048-AAAAMMDDTHHMMSSZ --output docs/roadmap/evidence/NUEVA-EVIDENCIA.json --execute
```

Sustituir la marca por UTC real y crear un run nuevo; no reutilizar/reescribir los
backups existentes. El modo execute fuerza recreaciones: no es diagnóstico rutinario.
Usar siempre SSH estricto existente. No mostrar Compose resuelto, env ni logs crudos.

Salud200 confirma runtime, **no procesamiento GA4 extremo a extremo**. No se ha
cuantificado pérdida de solicitudes durante las dos recreaciones inevitables.
La caducidad puede repetirse; prevención pendiente en Issue#1. No se instalaron
timers, cron, autoheal ni reinicios automáticos. Sin Terraform apply, commit o push.
Intervención terminada; no avanzar a otro LXC.
