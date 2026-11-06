# Consolidación Git D-042

Fecha: 2026-11-06 21:18 CET. Alcance F7-01 y prevención local F7-04; sin producción.

## Diagnóstico y respaldo

Rama `main`, upstream `origin/main`, remoto SSH de GitHub existente. Tras fetch
con BatchMode, StrictHostKeyChecking y known_hosts del propietario: cuatro commits
locales pendientes y cero remotos pendientes. HEAD inicial `ceb2e79b6163b79b33dbf2b62cf157a7ea2126a0`;
origin/main inicial `9cf3bb76f7a2617f5cc51eb7c0c19f2761467f5a`.
Estado inicial: 425 entradas (156 rastreadas con cambios, 269 nuevas; algunas son
directorios), con 130 archivos staged. Respaldo privado completo de refs mediante
bundle verificado, índice, patches binarios y archivos nuevos en
`$HOME/.local/share/mailerblend-recovery/git/20261106T201522Z/`.
El respaldo contiene material sensible: permanece privado, fuera de Git.

## Auditoría de seguridad

Gitleaks 8.30.1: cuatro commits salientes previos sin hallazgos. Auditoría de
historial y árbol local complementada con patrones y revisión de archivos
sensibles; los resultados brutos no son una lista de credenciales confirmadas.
Se confirmó token Telegram histórico en origin/main en el backup EVA
`backups/infra-eva-assistant-bot/2026-04-07-115353/compose-backup/.env.example`
y su historial de `services/infra-eva-assistant-bot/compose/.env.example`.
La configuración histórica de Alertmanager incluye una credencial SMTP que debe
rotarse; su eliminación actual no la revoca ni borra del historial. Un diff de
revisión la mostró accidentalmente; no se reproduce aquí. Otros hallazgos
históricos de claves/API requieren revisión y rotación por su propietario.
No se ha probado su vigencia ni se han usado para autenticar servicios.
No se reescribe historia ni se fuerza push.

Nuevos archivos locales sensibles excluidos: claves/certificados privados de
Gestoría, odoo.conf y perm.env de Journal. Estados Terraform, terraform.tfvars
y perm.env de Prometheus se retiran del índice preservando archivos locales.
Se ignoran también .terraform, cachés Python, .runtime/.rollback y plan de
recuperación renderizado. Los .env existentes siguen excluidos. Los backups y
evidencias seleccionados se revisan con escáner; no se publica el respaldo privado.

## Revisión y pruebas

230 pruebas unittest de monitorización PASS; sintaxis Python y shell y JSON de
selección PASS; enlaces locales Markdown PASS; git diff --check PASS.
validate-monitoring.sh PASS con promtool 3.12.0 y amtool 0.33.0: reglas, tres
suites PromQL, configuración Prometheus/Alertmanager y plantillas Telegram.
Solo renderizado y pruebas locales: sin despliegue, SSH a PVE ni notificaciones.

Se conservan contrato cgroup CPU, collector.cpu desactivado, RAM LXCFS, digests,
política de ejecución COMPLETED/permisos vacíos y evidencia17/17 D041. Los
catálogos/configuración base locales no certifican equivalencia con snapshots
incrementales de producción ni autorizan desplegarlos. No se ejecuta Terraform
plan/apply; overrides de recuperación no aceptan automáticamente nueva deriva.

## Selección y pendientes

Commits separados para exclusiones, IaC/exporters/recuperación, Prometheus/AM/Telegram,
framework/pruebas y documentación. Se mantiene fuera de los commits el cambio
funcional sync_service.py de EVA, Compose y artefactos de aplicaciones Journal,
Gestoría y repositorios de addons anidados: trabajo conservado, requiere revisión
separada; no se considera perdido ni aceptado por F4. Inventarios de identidad
Journal/Gestoría sí son necesarios para la cobertura17 y forman parte de IaC.

F4 cobertura exporters DONE según evidencia D041, no nueva verificación viva.
F7-01 completado para monitorización en el resultado inferior. F7-04 sigue pendiente
de rotación/gestión global; F5/F6 y otros complementos no se aceptan aquí.
Selección final escaneada por Gitleaks: cero hallazgos. Siguiente paso: verificar
el historial saliente y realizar push normal autorizado.


## Resultado D-042

Push normal SSH confirmado a main: cinco commits nuevos y cuatro previos,425
rutas cambiadas; HEAD/origin `44c0e8b`,0ahead/0behind en verificación del primer
push. Se añade cierre documental con esta evidencia en un commit separado, que
también requiere auditoría y push normal; su hash final se entrega en la sesión.
F7-01 DONE en alcance monitorización curada; F7 global IN PROGRESS. No árbol
limpio: un archivo funcional EVA modificado y19entradas nuevas de apps/repositorios
Gestoría/Journal conservadas. No hay cambios staged tras los commits principales.
F7-04/rotación histórica y revisión de esas aplicaciones pendientes.
[Evidencia fechada](evidence/2026-11-06-git-consolidation.json).
