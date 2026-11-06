# Trabajo en terraform/proxmox

## Gestión del proyecto

Antes de iniciar una tarea, leer `docs/roadmap/ROADMAP.md`,
`docs/roadmap/CURRENT-STATUS.md` y las decisiones aplicables en
`docs/roadmap/DECISIONS.md`. Identificar fase y tarea; registrar cualquier ampliación
antes de ejecutarla. El roadmap central prevalece sobre la numeración histórica de
los runbooks (su correspondencia está documentada).

Distinguir implementación local, pruebas, despliegue real y aceptación. Estados de
tarea: TODO, IN PROGRESS, BLOCKED, DONE. DONE exige criterios verificables y evidencia;
un archivo preparado o un test local no prueba un despliegue. Las dispensas de UAT
se registran como dispensas, nunca como pruebas realizadas. No extender una dispensa
a otros servicios o fases.

Al terminar cada intervención actualizar la fase, ROADMAP y CURRENT-STATUS con
resultados, evidencias, riesgos, bloqueos, autorización disponible y siguiente paso.
Registrar decisiones aprobadas y propuestas por separado. En el resumen al usuario
indicar fase actual y siguiente paso. Mantener estos archivos dentro del control de
versiones; revisar el diff y no incluir secretos ni cambios ajenos en un commit.

## Operación

Terraform + inventario YAML, scripts versionados y Docker Compose son los mecanismos
actuales. Toda corrección debe ser reproducible mediante IaC. No confundir el estado
Git con el estado de producción: consultar APIs/servidores y fechar las evidencias.
No ejecutar `make deploy-all` para una intervención acotada: incluye Terraform y otros
servicios. El script heredado `deploy-cadvisor-all.sh` elimina contenedores; no es el
procedimiento de piloto de la Fase 4.

Los despliegues, reinicios, limpiezas y cambios de recursos requieren autorización
para ese alcance. Una aprobación de recuperación anterior no autoriza desplegar la
siguiente fase. Para Fase 4 están autorizados diagnóstico, preparación y el piloto de exporters
en CT 624 según D-014 y el lote 626→625 completado bajo D-019. No está autorizado el rollout restante ni
el discovery global. Consultar CURRENT-STATUS antes de cualquier ejecución.

Preservar datos, volúmenes e imágenes de rollback. Verificar backups y restauración
cuando la intervención lo requiera; si falla una condición de seguridad, detener el
paso dependiente y explicar el bloqueo. Validar antes y después; comprobar que una
segunda aplicación sin cambios no recrea ni recarga servicios innecesariamente.
No desactivar verificación SSH/TLS ni modificar la configuración SSH del propietario
para eludir un bloqueo. Usar los accesos existentes y no mostrar entornos, tokens,
contraseñas, estados Terraform o logs sensibles completos.

## Documentación y pruebas

Documentación operativa en español, títulos de las siete fases según ROADMAP.
Enlazar los runbooks existentes, sin duplicar sus instrucciones. Fechas de seguimiento
en Europe/Madrid; conservar las marcas UTC de evidencias históricas identificándolas.
Ejecutar pruebas apropiadas al cambio y comprobar enlaces locales y `git diff --check`.
No modificar cambios previos ajenos ni declarar aceptados los pendientes heredados.


## Contrato del piloto F4

CT 624 ya tiene el piloto validado: CPU real por lxc_cpu_* (textfile, fuente cgroup),
collector.cpu desactivado y RAM desde LXCFS. /host/proc/stat solo daba capacidad,
pero sus tiempos seguían siendo del núcleo físico. No revertir esa corrección ni
reutilizar la regla CPU antigua sin revisión de compatibilidad. cAdvisor requiere
el socket containerd aprobado solo para CT 624. Revisar PILOT-624 antes de otro lote;
no hay aprobación para otros CT ni discovery global.

## Preparación del lote Journal

CT 624 aceptado técnicamente (D-017). CPU-CONTRACT y JOURNAL-625-626 describen
reglas CPU aceptadas/probadas pero sin recarga global; bundles Journal aplicados y
validados bajo D-019. P-011 ya aprobado para 625/626; no extenderlo a otros CT ni
activar discovery durante este lote.
Frescura Prometheus 45 s (scrape 30 s); validación directa 15 s. No alterar los
ocho inputs desplegados de CT 624 al preparar otros CT.

## Autorización Journal D-019

El propietario aceptó el contrato CPU y autorizó ejecutar CT 626→625, incluidos
sockets exactos, digests, backups, rollback, 10 min y segunda aplicación. El permiso
previo P-011 ya está concedido para esos dos CT. CT 625 exige PASS de CT 626.
Fuera de este lote solo preparar: R1–R7 requieren aprobación; 17/17 incluyendo
CRM/EVA es obligatorio para F4. CRM/EVA último lote de aplicaciones, observabilidad
al final. No activar discovery global durante Journal.

D-019 completado: tres Journal corregidos, 626/625 PASS técnico. Próximo paso R1
CT 613 para revisión/aprobación; consultar JOURNAL-EXECUTION y PROGRESSIVE-ROLLOUT.


## D-020 / D-021 — CPU incremental y cadena completa

Journal 626/625 técnicamente aceptados: F4-11 DONE — Accepted. Exporters aceptados
no implican cadena completa: hoy 3 fuentes fiables y 0 cadenas CPU corregidas
integradas. INCREMENTAL-INTEGRATION y R1-613 son la preparación vigente, pendiente
de aprobación de ejecución. No desplegar P0/R1/R2–R7 desde esa preparación.

El orden R1–R7 está aceptado como plan, con integración Prometheus/reglas/Telegram
por CT antes de avanzar, no al final de 17. Mantener estados/exporter-migration.yml,
backups/rollback coordinados y fuente legacy unverified. Ningún fallback físico ni
CPU cero por ausencia. Pruebas Telegram deben recorrer exporter→Prometheus→reglas→AM
→Telegram con FIRING/RESOLVED recibidos; POST directo AM no satisface cadena.
La fuente puntual puede verificarse antes de observación; DONE requiere estabilidad,
idempotencia y cadena. No marcar integrado por tener archivos locales preparados.

## Estado vigente D-023/D-024 (sustituye estados históricos anteriores)

P0/R1 ejecutados, verificados; cuatro cadenas fiables624/626/625/613. R2 preparado,
no autorizado; no ejecutar R2–R7. Consultar CURRENT-STATUS y P0-R1-EXECUTION.
Desde R2: política services/common/rollout-observation.yml: R2–R5 inicial180s/7;
R6/R7 600s/21, cada30s. Anomalía detiene avance y extiende>=600s sin resetear baseline.
Mantener vigilancia posterior y no declarar validado for no cumplido.

## D-025 — autorización vigente y bloqueo

R2–R5 y R7 autorizados secuenciales, R6 excluido. Detenido antes de CT621 por falta
de clave PVE verificada: aliaspve usa UserKnownHostsFile=/dev/null y checkingno.
No usar esos defaults para despliegue ni aceptar keyscan como verificación. Resolver
identidad y revalidar antes de continuar. Nuevos scripts approved-exporters y
progressive-monitoring-transaction son borradores no validados en producción.

### D-025 reanudado

Propietario verificó/registró clavePVE; SSH estricto explícito comprobado. Reanudación
solo621 y siguientes autorizados, sin repetir4CT yaaceptados. Usar siempre
UserKnownHostsFile=$HOME/.ssh/known_hosts, StrictHostKeyChecking=yes, BatchMode=yes.
La prueba automática actual acredita aceptaciónAPI del envío, no recepción humana.
Ante HALT de watcher no avanzar. CURRENT-STATUS e informe autónomo tienen el estado
vigente y sustituyen el bloqueoSSH histórico anterior.


## D-030 — cierre de sesión, sustituye continuación D-025/D-029

Rollout suspendido por propietario. Leer docs/roadmap/PHASE4-HANDOFF.md antes de
retomar.7 CT DONE técnicos;623 BLOCKED/ROLLED BACK, originales verificados;
nueve PENDING. No modificar617/615/614/61211/611/616/610/618/622 ni continuar--all.
Cadencia623 solo propuesta local; nueva aceptación requiere permiso explícito
623 más configuración coordinada de Prom610. No quitar HALT ni habilitar política
services/common/phase4-execution-policy.yml sin nueva autorización. Cierre D030
es auditoría de lectura; no commits/push ni borrado de backups/originales/evidencias.


## D-031 — reanudación 2026-11-05 (sustituye suspensión D-030 en este alcance)

Propietario autoriza623, después617→615→614, después61211; modificaciones mínimas
de configuración Prom610 para integrar esos cinco CT, con promtool, backup,
rollback, recarga controlada,17 fuentes/11Blackbox y legacy restante conservados.
No migrar exporters610 ni intervenir618/622/611/616. No apps/DB/recursosPVE ni
volúmenes ni commits/push.623 tras incidencia exige600s/21;R4/R5 inicial180s/7,
anomalías veto y extensión>=600s. Consultar CURRENT-STATUS; no repetir siete PASS.
