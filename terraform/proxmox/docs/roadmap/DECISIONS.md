# Registro de decisiones

Registro: 2026-11-02, Europe/Madrid. “Aprobada” refleja instrucciones del propietario
o mecanismos ya utilizados; “propuesta” no autoriza producción. Las aprobaciones
anteriores no se extienden automáticamente a otros despliegues.

## Aprobadas

| ID | Decisión | Evidencia / límites |
|---|---|---|
| D-001 | Mantener Terraform + inventario YAML, scripts existentes y Docker Compose como mecanismos actuales | [README](../../README.md), `main.tf`, runbooks de recuperación. No introducir otra plataforma en esta intervención |
| D-002 | IaC transversal: correcciones y documentación deben quedar declaradas y reproducibles | Requisitos del propietario; [reglas de trabajo](../../AGENTS.md). No usar un cambio manual remoto como entrega definitiva |
| D-003 | Telegram es el receptor principal actual, con FIRING y RESOLVED | [TELEGRAM](../../services/infra-prom/TELEGRAM.md), confirmación del propietario y pruebas de entrega. No se ha aprobado separación por severidad |
| D-004 | Secretos fuera de Git y de las salidas de diagnóstico | Token mediante archivo, .env/.runtime ignorados. Es un requisito; NO una afirmación de cumplimiento global: existen credenciales y estado heredados rastreados, pendientes en F7 |
| D-005 | Despliegues idempotentes; no recrear/recargar si no cambia el contenido efectivo | [deploy-prom](../../services/infra-prom/deploy-prom.sh), [ejecución F3](../../services/infra-prom/PHASE2-EXECUTION.md); probado para Prom/CRM/EVA, no demostrado para todos los scripts |
| D-006 | Preservar datos, volúmenes, imágenes y originales necesarios para rollback | [RECOVERY](../../services/infra-composable-crm/recovery/RECOVERY.md), [STORAGE-PLAN](../../services/infra-eva-assistant-bot/recovery/STORAGE-PLAN.md). No implica prohibir la limpieza de caché/journal expresamente aprobada |
| D-007 | Backups verificados, copia externa y restauración aislada antes de los pasos de recuperación dependientes | Evidencias y resultados en [PHASE2-EXECUTION](../../services/infra-prom/PHASE2-EXECUTION.md). Checksum de transporte no sustituye restauración funcional |
| D-008 | Validación previa y posterior por APIs/servicios reales, más pruebas locales | Readiness no demuestra Telegram, `up=1` no demuestra métricas individuales ni salud de aplicación |
| D-009 | Recuperación CRM: una instancia Budibase 3.27.4, dependencias y /data originales; 6 GiB temporales | F3 ejecutada. Worker y app anteriores conservados detenidos. No reducir RAM, actualizar imágenes ni arrancar el duplicado automáticamente |
| D-010 | Centralizar seguimiento en estas siete fases y actualizarlo tras cada intervención | Petición actual; [ROADMAP](ROADMAP.md). Mantener correspondencia histórica Fase 2 antigua → Fase 3 central |
| **D-011** | **Aceptar formalmente F3 con dispensa de UAT** | **Instrucción expresa del propietario del 2026-11-02**; detalle siguiente |
| D-012 | Auditoría/preparación inicial F4 autorizada | Restricción inicial de producción ampliada únicamente por D-014 para CT 624; resto del rollout sigue sin aprobar |
| D-014 | Ejecutar piloto exclusivamente CT 624 | Aprobación expresa del propietario; helper, backups, rollback y diez minutos de validación; sin otros CT ni discovery global |
| D-015 | Acceso directo containerd para CT 624 | Socket exacto ro aprobado expresamente; ro no limita RPC; no otros sockets/privilegios |
| D-016 | Implementación CPU cgroup dentro del piloto | Mismo Node/UID nobody, fuente ya montada; nuevo contrato lxc_cpu_*, sujeto a compatibilidad/revisión antes de rollout |
| D-013 | Excepciones anteriores de parada forzada limitadas a mantenimiento/cron EVA inactivos | Fueron aprobadas individualmente durante F3, con guardas y originales conservados. No constituyen permiso general para SIGKILL ni para F4 |
| D-017 | Aceptación técnica del piloto CT 624 por el propietario | Ocho criterios aceptados; no autoriza rollout ni otros sockets |
| D-018 | Preparar compatibilidad CPU y lote CT 625/626 | Diagnóstico de solo lectura y pruebas locales autorizados; sin despliegue ni discovery global |
| D-019 | Ejecutar lote CT 626→625 y aceptar contrato CPU local | Autorizados digests, exporters, socket containerd exacto ro/sin crear ruta, backups, rollback, 10 min y segunda aplicación. CT 625 solo tras PASS de 626; sin apps/DB, recursos ni discovery |
| D-020 | Aceptación técnica Journal API 626 y DB 625 | Propietario acepta JOURNAL-EXECUTION; exporters DONE/Accepted, no implica cadena CPU integrada |
| D-021 | Integración por CT y orden R1–R7 como plan | Preparar estrategia incremental y R1; no desplegar todavía. Cadena Exporter→Prometheus→Reglas→AM→Telegram obligatoria por CT |

### D-014 — Piloto autorizado exclusivamente CT 624

El propietario aprueba preparar, validar y ejecutar el piloto de Node Exporter y
cAdvisor 0.60.6 por digest en Journal Web, incluyendo imágenes, snapshots, rollback,
contraste Proxmox/LXCFS/cgroups e idempotencia. Requiere diez minutos estables, sin OOM
ni presión significativa y web operativa. Se limitan los exporters a 48 MiB/0,20 CPU
(Node) y 128 MiB/0,50 CPU (cAdvisor) dentro de los recursos existentes, para proteger
los servicios; no se amplían recursos Proxmox. No autoriza otros LXC, discovery global,
apps/DB, kernel, Docker daemon ni privilegios adicionales no contemplados.
Si aparece esa necesidad o riesgo para aplicaciones, detenerse y consultar.

### D-011 — DONE — Accepted with UAT Waiver

El propietario revisó los resultados técnicos y **acepta formalmente la recuperación
de CRM y EVA**. Las verificaciones técnicas y automatizadas pasaron, las restauraciones
reales aisladas se verificaron y ambos servicios están operativos según las comprobaciones
realizadas. Se conserva [PHASE2-EXECUTION.md](../../services/infra-prom/PHASE2-EXECUTION.md)
como evidencia histórica, junto con la revalidación de solo lectura de F4.

**La prueba manual adicional de login y flujos de negocio no se ejecutó y fue dispensada
por el propietario. Esta dispensa no equivale a demostrar que todos los flujos funcionales
fueron probados.** No generar retroactivamente resultados de UAT ni extender la dispensa
a la aceptación de F4. Los pendientes heredados permanecen abiertos, sin reabrir la
recuperación aceptada ni declararlos resueltos.

## Propuestas / decisiones pendientes

| ID | Propuesta | Estado y puerta |
|---|---|---|
| P-001 | Piloto F4: Node Exporter leyendo /host/proc y /host/sys, con la imagen instalada por servicio | Tres Journal validados; CPU cgroup tras detectar tiempo físico procfs. Otros 14 pendientes |
| P-002 | cAdvisor 0.60.6 por digest, API moderna y visibilidad cgroup del LXC | Imagen probada CT 624/626/625 con sockets aprobados. Otros 14 pendientes |
| P-003 | Activar targets 17+17, Grafana y tres sondas Journal nuevas | Local; tres Journal ya instalados. Activación global pendiente de completar otros 14 y validación independiente |
| P-004 | Monitorizar separadamente el nodo PVE y exportar recursos/estado LXC desde su fuente de gestión | Sin implementación ni despliegue aprobados. No usar las métricas globales de Docker como sustituto de las del LXC |
| P-005 | Severidades, inhibiciones, rutas Telegram, duración RESOLVED | F5 pendiente. No modificarlo para ocultar métricas incorrectas o un incidente real |
| P-006 | Corregir los tres healthchecks heredados y el digest diario EVA | Pendientes. Cambios que reinicien aplicaciones o alteren sus comandos necesitan revisión y aprobación de su alcance |
| P-007 | Herramientas fijadas sin dependencia /tmp, CI, hardening y política sostenida de DR | F7. Credenciales heredadas, TLS/SSH, estados Terraform y backups requieren un trabajo específico; no se modifican ahora |
| P-008 | Cierre mediante commits curados del trabajo acumulado | Revisar el árbol con cambios ajenos, runbooks y servicios nuevos. No hacer commit indiscriminado ni incluir secretos/estado. El despliegue real se verifica independientemente de Git |
| P-009 | Ideas históricas del README: edge/TLS, otros receivers y cloud | Backlog sin priorizar ni aprobar nuevas funcionalidades; CI/CD y DR se encuadran en F7. No se ejecutan como parte de F4 |


### D-015 — Socket containerd autorizado solo CT 624

Durante el piloto, el propietario autorizó expresamente el bind ro de
`/run/containerd/containerd.sock` en cAdvisor 0.60.6, con create_host_path=false.
Se explicó que ro no restringe los métodos RPC. No autoriza otros sockets, otros CT,
privilegios adicionales, kernel, Docker daemon o Proxmox. El primer candidato se
revirtió y se conserva detenido antes de aplicar la revisión explícita.


### D-016 — Implementación de CPU real dentro del piloto CT 624

El contraste mostró que /host/proc/stat conserva tiempo del núcleo físico aunque
CPU count/RAM estén virtualizados. Dentro de la autorización D-014 se aplicó una
variante del mismo Node Exporter, sin privilegios adicionales ni cambios PVE/LXCFS:
collector textfile ejecutado como nobody, leyendo el cgroup del LXC ya expuesto por
/host/sys. Se desactiva collector.cpu y se publican contadores explícitos lxc_cpu_*,
no tiempos idle inventados ni series node_cpu_seconds_total con otra semántica.
La imagen, cuotas y aplicación permanecen iguales; solo se monta código del collector
como ro. Superó una nueva ventana de 600,943 s y queda limitado al piloto. Su contrato
de métricas y compatibilidad con alertas se revisarán antes de cualquier rollout o
discovery global; no es una autorización de cambios sobre el nodo físico.


### P-010 — Compatibilidad CPU y próximo lote

Compatibilidad CPU ya preparada y probada localmente (D-018); promoción/discovery
y dashboards siguen pendientes. El piloto aceptado no autoriza rollout. Lote
concreto Journal API/DB presentado en P-011, sujeto a aprobación y preflight.


### D-017 — Aceptación técnica del piloto Journal Web

El propietario revisó PILOT-624 y acepta expresamente recursos LXC/cgroup, visibilidad
Docker, estabilidad, consumo, rollback, idempotencia y continuidad de Journal Web.
F4-07 queda DONE con aceptación técnica. No amplía la dispensa UAT de F3 ni afirma
haber probado todos los flujos de usuario. Fase 4 global permanece IN PROGRESS.

### D-018 / P-011 — Preparación aprobada y siguiente ejecución pendiente

Se autorizan reglas/validadores compatibles con lxc_cpu_*, diagnóstico y preparación
local de CT 625/626. Se implementan sin recargar Prometheus. Fórmula normalizada por
capacidad asignada, sin mezclar Docker; calidad inválida no equivale a cero. Se
mantienen umbral/for y rutas. Frescura directa 15 s; Prometheus 45 s por scrape de
30 s y writer de 5 s. Ver CPU-CONTRACT.

**P-011 aprobada por D-019 y ejecutada:** exporters solo Journal API 626 y DB 625, por ese orden,
con descargas por digest y bind ro del socket /run/containerd/containerd.sock en
ambos (ro no restringe RPC), backups externos verificados y rollback. D-015 no se
extiende a estos CT. Sin apps/DB, nuevos privilegios, CRM/EVA, otros LXC ni discovery.
Plan concreto en [JOURNAL-625-626](JOURNAL-625-626.md). Ambos CT desplegados y validados técnicamente; ver JOURNAL-EXECUTION.


### D-019 — Ejecución Journal y objetivo obligatorio 17/17

El propietario acepta el contrato CPU y sus pruebas locales y autoriza expresamente
626→625 con los controles documentados, incluido socket exacto en ambos. La ejecución
se completó en orden CT 626→625 con PASS técnico en ambos. Detener expansión ante regresión importante o privilegios nuevos.
La Fase 4 exige desplegar Node/cAdvisor corregidos en los **17 LXC, incluyendo CRM y
EVA**, y validar integración global, Grafana, Journal, reglas y Telegram. CRM/EVA
serán el último lote de aplicaciones por su recuperación reciente. Se autoriza
preparar el rollout progresivo restante, no ejecutarlo. La integración global no
forma parte del lote actual; requiere validación independiente y no cierra F4 aún.


### Resultado de D-019

626: 21 muestras/600,960 s. 625: 21 muestras/601,019 s, después del PASS de API.
Backups/carga de imagen/rollback/reanudación/segunda aplicación y configuración
posterior externa verificados. Aplicaciones conservadas, cero OOM nuevos. No se
registra aceptación formal del propietario posterior aún; ver [JOURNAL-EXECUTION](JOURNAL-EXECUTION.md).
F4 sigue IN PROGRESS con tres CT validados. R1–R7 únicamente diseñados/preparados;
no autorizar por inferencia sus sockets/recursos/despliegues. Integración global
condicionada a 17/17 y validación independiente, fuera del lote actual.


### D-020 — Journal aceptado por propietario

El propietario acepta técnicamente CT 626 y CT 625 tras revisar JOURNAL-EXECUTION.
F4-11 queda DONE — Accepted. No se realizaron nuevas pruebas de negocio/UAT, ni se
extiende la dispensa F3. Sus exporters están aceptados; su CPU todavía no entra en
Prometheus y no se declaran cadenas completas por esa aceptación técnica.

### D-021 / P-012 — Integración incremental y R1 preparados

Orden R1–R7 aprobado como plan, incluidos finalmente CRM/EVA. Se sustituye la espera
hasta 17 por integración y validación de cadena **en cada CT**, antes de avanzar.
Preflight, backups/rollback, pins, exporters, Prometheus/reglas, Telegram, observación,
idempotencia y roadmap son gates de cada lote. Las reglas legacy deben identificarse
como no verificadas, sin falso cero ni fallback para corregidos.

P-012 preparado, pendiente de aprobación de ejecución: P0 integra solo los tres
Journal sobre snapshot real preservando 14 legacy y once Blackbox, después R1 CT 613.
No activar Grafana/sondas globales ni R2–R7 desde este alcance. El permiso de sockets
D-015/D-019 no cubre CT 613. Contrato fuente verificada, exporters aceptados,
integración y cadena recibida son estados distintos en exporter-migration.yml.
Ver [INCREMENTAL-INTEGRATION](INCREMENTAL-INTEGRATION.md) y [R1-613](R1-613.md).
La cobertura F4 exige 17/17 fiables con cadena operativa, más aceptación global;
solo instalar exporters no cumple. No se ha desplegado/recargado nada en esta preparación.


### D-022 — P0 y R1 autorizados, con gate de aceptación

El propietario autoriza ejecutar P0 para Journal 624/626/625 y solo después de todos
sus criterios R1 CT 613, incluidos socket exacto y cgroupns=host dentro del LXC.
Antes de R1 demostrar límite namespace LXC vs PVE. Incluye backups externos,
rollback/reanudación, pins, observación y segunda aplicación. No apps inesperadas,
recursos/kernel/daemon/Proxmox ni privilegios nuevos; detenerse si falla condición.
R2 se prepara después del PASS de ambas etapas, R2–R7 no se despliegan. La recepción
Telegram y sus evidencias forman parte del gate, no se hereda una dispensa previa.


### Incidencia de archivo posterior durante D-022

Tras validar R1, el archivo posterior de mecanismos falló por asumir una carpeta
compose; la ruta real es /opt/infra-prom/docker-compose.yml. Backups previos y
originales siguen verificados/intactos; exporters, reglas, namespace y Telegram
funcionan. Se detuvo el avance a R2 y se consultó al propietario por su condición
explícita ante fallos de backup. Corrección local probada: conservar parcial,
seleccionar mecanismo existente y crear integration-after-v2.tar.gz, verificar
hash/copia externa sin modificar configuración ni reiniciar servicios.

### D-023 — Cierre P0/R1 y reparación exclusiva del archivo posterior

P0 y R1 pasan rollback, idempotencia, observación600s y cadena real. Propietario
confirma seis mensajes Journal y dos613. V2 verificado completo/legible con hash
externo coincidente, parcial conservado. Primer reintento falló localmente al encontrar
copia existente, antes de crearV2; se volvió a detener. Propietario autorizó una sola
operación --monitoring-only, exitosa sin reinicios/cambios activos. La ruta Compose
real queda seleccionada automáticamente en código; archivos existentes no se sobrescriben.
Ver [ejecución](P0-R1-EXECUTION.md). Esto no autoriza R2.

### D-024 — Observación inicial escalonada desde R2 (aprobada)

R2–R5:180s y7 muestras cada30s. R6/R7 CRM/EVA/observabilidad:600s/21.
P0/R1 mantienen600s ya realizados. Mantener backups/rollback/idempotencia/Prom/AM,
vigilancia automática externa900s y continuaProm/AM. Anomalía: halt, diagnóstico,
ventana extendida mínima600s conservando baseline original OOM/restarts. Nunca dar
por validada una alerta cuyo for/predicado no se haya cumplido; no acortar for ni
intervalos Telegram. Socket/namespace de R2 requiere autorización específica del lote.

### D-025 — Rollout autónomo autorizado R2–R5 y R7

Propietario autoriza ejecución secuencial621→620→619→623→617→615→614→61211→611→616→610.
R6 CRM618/EVA622 excluido: conservar contenedores/recursos/config y cobertura existente.
Reutilizar configuración de seguridad ya revisada; detener ante privilegios nuevos.
Preflight, backups externos/restauración, rollback, integración porCT, Telegram,
idempotencia y observación son gates. R2–R5:180s;R7:600s; muestreo30s y vigilancia
posterior. Anomalías: detener secuencia y extender>=600s. R7 depende de demostrar
independencia de R6. No requiere confirmación humana entreCT; no confundir pruebas
automatizadas de entrega con recepción humana. No commits ni pushes automáticos.

#### Bloqueo D-025 — identidad SSH de Proxmox

Antes del primer despliegue se comprobó SSH explícito con BatchMode=yes,
StrictHostKeyChecking=yes y UserKnownHostsFile=$HOME/.ssh/known_hosts: fallo por
clave ED25519 desconocida para192.168.1.100. ssh -G confirma que aliaspve hereda
StrictHostKeyChecking=false/UserKnownHostsFile=/dev/null. Tampoco hay entrada en
known_hosts.old ni por aliaspve; consulta ainfra-prom mediante clave conocida no
proporcionó entrada alternativa. Las primeras consultas usaron configuración del
alias y son preliminares, no evidencia de identidad autenticada. Secuencia detenida
antes de CT621; cero cambios de producción. Se pide clave/huella verificada por
consola, sin modificarSSH ni aceptar keyscan como prueba. Borradores IaC locales
pendientes de validación completa; conservar autorizaciónD-025 al reanudar.

#### Reanudación D-025 — clave PVE verificada por propietario

El propietario confirma verificación/registro ED25519. Conexión explícita
BatchMode=yes/StrictHostKeyChecking=yes/UserKnownHostsFile=$HOME/.ssh/known_hosts
correcta, hostnamepve. Bloqueo SSH resuelto. Revalidar preflight autenticado y continuar
621, sin repetir Journal/P0/R1 y sin ampliar alcance a618/622. No cambiar SSH global.

### D-026 — Incidencia del vigilante durante D-025 y recuperación acotada

Seguimiento2026-11-03 Europe/Madrid; run iniciado2026-11-02UTC. Tras PASS inicial621,
watcher falló a60s coincidiendo con recarga620 (a42s), volvió correcto a90s. Se detuvo
620 automáticamente. Rollback previsto restauró sus dos exporters originales y
checkpointProm con cinco fuentes corregidas; apps/datos intactos. Segundo fallo
coincidió con rollback. HALT y trazas iniciales se conservan.

El primer sampler no conservó la excepción interna completa: causa puntual no
atribuible con certeza. Diagnóstico: reload sin cambios no reprodujo unknown;
regla temporal nueva desactivada sí reprodujo healthunknown, sin fallos de evaluación
ni notificaciones, y se retiró. Esta transición hace fallar el predicado global del
sampler. La sincronización corregida coordina únicamente lectores del seguimiento
posterior con transacción de recarga+readiness medianteflock compartido/exclusivo.
No pausa scrapes, apps ni relaja verificaciones. Pruebas reales entre procesos y
preservación de diagnóstico privado incluidas. Muestras mantienen su hora real.

Reanudación dentroD-025 limitada a620: exige nueva observaciónPASS>=600s/21 muestras,
backups vigentes revalidados, fuentes aceptadas correctas y diagnóstico sin errores.
Preserva marcador original archivado; no admite nuevoHALT distinto ni ventana fallida.
No repetir backups/candidatos ya verificados. CT620 tendrá600s tras la incidencia.
Si falla esa condición, no se libera el bloqueo. R6 sigue excluido. Las aplicaciones
Edge615 con salud503/unhealthy deben superar preflight: no están autorizadas sus
reparaciones funcionales ni un despliegue de exporters si no hay disponibilidad.

### D-027 — Compatibilidad de predicción RAM con cambios de fuente (F4)

Se detecta HostMemoryFillingFast para621 con92%RAM disponible: durante ensayo de
rollback, Node original publicó brevemente memoria física bajo etiquetas corregidas.
El rango1h conserva el salto; predict_linear genera un pronóstico inválido. No hay
OOM/PSI significativo. Las alertas de rango también pueden persistir para etiquetas
retiradas. Corrección necesaria dentroD025/F4 (calidad de fuente), sin optimizarF5:
misma predicción1h→4h y for15m, pero solo para targetactualup y capacidadRAM estable
en su rango. UmbralesCPU/RAM y severidades no cambian; alertaRAMbaja inmediata sigue.
Ensayos futuros retiran contratoProm antes de reanudar exporteroriginal, evitando
contaminar la serie corregida. PruebasPromQL/gates/backup previos a aplicación. Registro
operativo bajo autorizaciónD025, no aceptación global de F4/F5 por el propietario.

<!-- D025 CT621 completed -->

Resultado operativo D025 CT621: PASS technique, 14 muestras/395.661s, backup externo/rollback/idempotencia verificados. Telegram API: +2.0 envíos, 0.0 errores nuevos; no se atribuye recepción humana. [Prueba](evidence/2026-11-02-rollout-621.json). F4 sigue IN PROGRESS.

<!-- D025 CT620 completed -->

Resultado operativo D025 CT620: PASS technique, 21 muestras/606.138s, backup externo/rollback/idempotencia verificados. Telegram API: +2.0 envíos, 0.0 errores nuevos; no se atribuye recepción humana. [Prueba](evidence/2026-11-02-rollout-620.json). F4 sigue IN PROGRESS.


### P-012 — propuesta pendiente: cAdvisor CT619 a 256 MiB

2026-11-03 08:38 CET. Preparada localmente, dos pruebas PASS; no aprobada ni
desplegada. Cambio exclusivo de límite Docker 128→256 MiB; LXC/apps intactos.
Requiere aprobación expresa por cambio de recursos y revalidación previa;
observación >=600s/21 muestras y gates D-025 completos. Secuencia detenida.
Ver [seguimiento](evidence/2026-11-03-619-resume-readonly.json) y
[propuesta](evidence/2026-11-03-619-recovery-proposed.json).


### D-028 — P-012 aprobada: recuperación cAdvisor CT619

2026-11-03T08:41:46.043145+01:00. El propietario responde «si, autorizo» al ajuste exclusivo
de cAdvisor CT619 de128 a256MiB, con rollback y observación mínima600s/21 muestras
antes de continuar. P-012 aprobada; D-025 conserva orden y exclusiones. Preservar
candidato128 detenido, originales, backups, baseline y HALT histórico. Revalidar
fuentes previas y gates; no ampliar recursos LXC ni aplicaciones. F4 IN PROGRESS.


Incidencia D-028: primer apply reactivó candidato128 renombrado por identidad
Compose compartida. Gate falló antes de integrar Prometheus; rollback ejecutado
y originales restaurados. Se conserva candidato rechazado y HALT. Corrección
reproducible: proyecto Compose exclusivo cadvisor-containerd-m256, sin modificar
Node; mantiene reconocimiento de ambos proyectos para rollback. Tres pruebas PASS,
incluida identidad revisada y gestión de candidatos históricos. Reintento dentro
de D-028 tras revalidación completa; ningún CT posterior iniciado.


Incidencia de observación D-028 (2026-11-03T08:56:50.034576+01:00): candidato256 pasó fuente puntual,
integración, rollback y segunda aplicación. La observación detectó fallos CPU
cAdvisor/Docker; no PASS ni avance. Diagnóstico adicional reproduce la aserción
con datos privados completos. API cAdvisor muestra caché de estadísticas con
timestamps distintos de Docker; posible desfase temporal, causalidad pendiente.
No se relajan tolerancias. Se conserva baseline y ventana extendida>=600s desde
el primer fallo. Corrección local del registrador conserva muestra/mensaje/traza
privados ante fallos futuros; no altera gates. Se prevé rollback coordinado tras
recoger la ventana extendida, conservar candidato256 detenido y mantener seis
fuentes integradas. No autoriza nuevos cambios de recursos ni aplicaciones.


### Estado vigente D-028 — 2026-11-03 09:02 CET

**Fase 4 IN PROGRESS; CT619 BLOCKED_ROLLED_BACK; cobertura validada6/17.**
P-012 aprobada y ejecutada localmente/en producción con candidato256MiB; no aceptada
como recuperación completa. Fuente puntual, integración, ensayo de rollback y segunda
aplicación pasaron; observación FAIL:27 muestras/780,579s,10 fallidas, primera a180,125s
y extensión600,454s conservando baseline. Diagnóstico independiente:14 discrepancias
CPU cAdvisor/Docker en36 muestras; pico cgroup cAdvisor24,2MiB, sin OOM/reinicios
ni eventos max en esas muestras. Hipótesis de desfase de caché pendiente de demostrar.

Regla temporal retirada y checkpoint coordinado restaurado; originales activos,
candidatos128/256 y Node conservados detenidos. n8n/PostgreSQL disponibles. Seis
cadenas previas revalidadas por API tras rollback;17Node/17cAdvisor/11Blackbox.
CT623 y posteriores sin iniciar; R6 excluido. No hubo commits/push. La prueba
Telegram de619 no se declara aceptada por fallar la ventana; ninguna recepción
humana nueva atribuida. D-025/D-028 conservan alcance, sin aprobar otros recursos.

Siguiente paso: contrastar CPU cAdvisor/Docker con timestamps equivalentes y preparar
una validación reproducible, manteniendo tolerancias y HALT hasta resolver el gate.
No avanzar ni repetir despliegue por el solo hecho de tener256MiB. Los registros
anteriores de aprobación pendiente y bloqueo SSH son históricos y quedan sustituidos.
[Evidencia D-028](evidence/2026-11-03-619-d028-recovery.json).


### D-029 — investigación CPU619 y reanudación condicionada autorizadas

2026-11-03 (Europe/Madrid). Propietario ordena identificar causa raíz antes de
otro despliegue, comparar identidad/timestamps/ventanas/fórmulas/normalización
y cgroup; corregir validador con regresiones si procede, sin relajar umbrales.
Tras causa identificada/corregida, reintentar únicamente619 con gates completos;
PASS permite continuar automáticamente623 y secuencia D025. Causa indeterminada
o discrepancia significativa recurrente exige detener e informar. Registrar tiempo.
D028256MiB conserva autorización; no otros recursos ni apps, R6 excluido.


D-029 diagnóstico previo cerrado: causa en muestreador/validador (timestamp
explícito descartado; comparación de contador cacheado con actual). Mismo ID
cAdvisor en14 fallos reproducibles; Docker/cgroup coinciden. Contraste de solo
lectura en620 con misma versión: dos timestamps, ventana54,747s y tasas coinciden
sin normalización CPU. Corrección solo instrumentación/validador; tolerancia
originalmax(1s,3%) intacta, extremos acotados<=2s y comparación adicional de
incrementos sobre ventanas comunes. 19 pruebas locales PASS. Exporters/imágenes,
recursosLXC/apps y ocho inputs624 intactos. Habilitado reintento exclusivo619
con mismo candidato256, backups/gates y600s/21; no se autoriza avance hasta PASS.
Ver evidence/2026-11-03-619-cpu-root-cause.json y cronometraje asociado.


D-029 incidencia de instrumentación durante rollback: lector CPU terminó al
consultar /proc/0 tras transición running→stopped entre list/inspect. No es una
nueva discrepancia significativa de CPU. Sin relajar controles: refresh ignora
solo proceso detenido/desaparecido, rechaza identidad cgroup incorrecta; diez
regresiones de alineación PASS. Reanudar checkpoint ya integrado/idempotente
sin reiniciar exporters/apps, conservar historial/fallo/HALT original y esperar
historia nueva acotada. Ningún paso posterior hasta600s/21 y cadena PASS.

<!-- D025 CT619 completed -->

Resultado operativo D025 CT619: PASS technique, 21 muestras/600.442s, backup externo/rollback/idempotencia verificados. Telegram API: +2.0 envíos, 0.0 errores nuevos; no se atribuye recepción humana. [Prueba](evidence/2026-11-02-rollout-619.json). F4 sigue IN PROGRESS.


Cierre operativo D-029 (2026-11-03 10:03 CET):619 PASS técnico21/600,442s y vigilancia31/901,725s,
CPU alineada de cuatro contenedores y cadenaAPI verificada sin errores nuevos.
Continuación623 falló por dato CPU>90s (una de33 muestras/960,793s); extensión
600,511s completada, rollback coordinado y originales/apps/checkpoint7 verificados.
No avanzar617 ni posteriores. Atribución a test-nginx solo hipótesis (timestamps
separados113,635s); no hay edad/identidad exacta original conservada. Diagnóstico
posterior41 muestras sin reproducción no dispensa gate. Registro íntegro de fallos
de probe mejorado y probado solo localmente; no desplegado tras HALT.
21 pruebas de alineación/rollout/recuperación más piloto histórico conservado.
Tiempo medido en evidence/2026-11-03-619-cpu-investigation-time.json, incluye esperas.
No cambios apps/recursos fueraD028 ni commits/push. F4 IN PROGRESS;7/17.
Siguiente paso: presentar diagnóstico623 y resolver frescura antes de otro intento.


### D-030 — cierre controlado, continuación automática suspendida

2026-11-03 (Europe/Madrid). Propietario limita esta sesión a CT623: investigar
frescura de forma acotada y corregir por IaC si es seguro, o conservar rollback
verificado y declarar BLOCKED. Suspende autorización automática D025/D029 para
R4/R5/R7 y excluye cualquier modificación de617/615/614/61211/611/616/610/618/622.
Auditoría final de solo lectura y handoff obligatorios, sin commits/push ni
borrado de backups, originales o evidencias. Tras documentar, detener la sesión.


#### Resultado D-030 — 2026-11-03 11:24 CET

Sin nuevas mutaciones de producción. CT623 continúa BLOCKED/ROLLED BACK;
originales, apps y backups verificados. Contrato de cadencia confirmado: fuente
v0.60.6 permite max dinámico60s +jitter1 hasta120s, superando frescura90s. Se
prepara propuesta fija30s exclusiva623 sin modificar umbrales/recursos/imágenes;
no desplegada. Aplicar/aceptar completamente requiere configurar Prom610, fuera
del alcance «no modificar otros LXC» de D030. No desplegar parcialmente ni asumir
permiso por D025/D029. No atribución única a test-nginx sin muestra faltante.

Auditoría de lectura:7 DONE técnicos,1 BLOCKED/ROLLED BACK,9 PENDING; ochoCT
intervenidos, versiones en PHASE4-HANDOFF.27 backups con hash externo/PVE,49 inputs
exporters y24 archivos Prom reproducibles; siete cadenas sanas,17/17/11 targetsup,
reglas sanas. Sin envíosTelegram nuevos ni pruebasUAT/reaplicaciones nuevas.
Política local SUSPENDED y guardas impiden ejecución del rollout; sin commits/push.
Handoff obligatorio creado; terminar sesión y esperar otra solicitud del propietario.

### P-013 — propuesta local pendiente (no aprobación de despliegue)

623: --allow_dynamic_housekeeping=false, --max_housekeeping_interval=30s,
--jitter_factor=0, --initial_splay_factor=0 y proyecto Compose propio cadence30.
Generador prepare-623-cadence.py; aprobación nueva debe incluir623 y configuración
coordinada Prom610, sin ningún lote posterior. Reentrada y observación600s/21+
vigilancia900s deben validarse; no hay apply preparado que se presente como probado.


### D-031 — reanudación P0 CT623 y objetivo R4/R5

2026-11-05 (Europe/Madrid). Propietario autoriza corregir623 con cambios mínimos
de configuración de Prom610, sin migrar sus exporters ni arquitectura general.
Revalidar producción/backups, cadencia, métricas/namespace, apps, OOM/reinicios,
Prom/AM/Telegram, rollback e idempotencia;623 requiere600s/21 tras incidencia.
Tras PASS pide617→615→614→61211, secuenciales, observación180s/7 y anomalías>=600s.
El adjunto también limita cambios610 exclusivamente a623: se solicita aclaración
del alcance de integración R4/R5, pendiente; no bloquea preparación/ejecución623.
Excluidos618/622/611/616;610 solo configuración autorizada, sin exporters. No
recursosPVE, apps/DB/volúmenes, verificaciónSSH desactivada, secretos ni commits/push.
No repetir sieteCT aceptados. Fallo exige conservar/restaurar estado seguro y parar.


#### Ampliación explícita D-031 — configuración Prom610 para R4/R5

Propietario autoriza targets/reglas/recording rules mínimos en610 para623,617,615,
614,61211, sin migrar/modificar exporters610.17 fuentes y11Blackbox conservados;
legacyCRM/EVA y otros pendientes intactos; promtool y backup verificado antes
de cambios, recargas controladas, Telegram y rollback; fallo detiene. No aprobación
porCT adicional dentro del alcance. Sustituye la duda de alcance anterior.


D-031 preparaciónR4/R5: candidatos nuevos617/615/614/61211 usan cadencia fija30s
sin dinámica/jitter para no reproducir defecto conocido. Solo generador local,
sin tocar siete CT aceptados niR7; mismos recursos/privilegios/digests.623 mantiene
su builder de revisión/proyecto exclusivo. Ningún target nuevo antes de PASS623.

<!-- D025 CT623 completed -->

Resultado operativo D025 CT623: PASS technique, 21 muestras/600.804s, backup externo/rollback/idempotencia verificados. Telegram API: +2.0 envíos, 0.0 errores nuevos; no se atribuye recepción humana. [Prueba](evidence/2026-11-02-rollout-623.json). F4 sigue IN PROGRESS.

<!-- D025 CT617 completed -->

Resultado operativo D025 CT617: PASS technique, 13 muestras/360.537s, backup externo/rollback/idempotencia verificados. Telegram API: +2.0 envíos, 0.0 errores nuevos; no se atribuye recepción humana. [Prueba](evidence/2026-11-02-rollout-617.json). F4 sigue IN PROGRESS.


Resultado parcial D-031:623 PASS21/600,804s;617 PASS13/360,537s (mínimo180s,
ventana ampliada por entregaTelegram), ambos API+2/0errores. Backups frescos,
rollback coordinado y segunda aplicación PASS; vigilancia posterior activa.
615 falla preflight HTTP503 /healthy antes de backups o cambios activos: estado
BLOCKED_NO_CHANGES, originales preservados.614/61211 no iniciados. Política
BLOCKED impide nuevas ejecuciones. No ampliar a reparación apps: fuera de alcance.
Finalizar vigilancia de lectura y documentar; no declarar12/17.


D-031 veto posterior617: a120,026s delwatch falla RAM analytics-ingest-gateway,
47.448.064B cAdvisor (timestamp anterior) vs61.263.872B Docker y60.858.368B
cgroup actual; diferencia13.815.808B supera12.252.774,4B(20%). No relajar ni
atribuir causa definitiva sin mediciones RAM del mismo instante. PASS inicial
provisional no satisface aceptación final. Completar vigilancia/anomalía, retirar
617 del registro tras rollback a checkpoint8 (623 conservado). Política BLOCKED
permite exclusivamente recovery617 por condición de rollback ya autorizada.
615 sigue sin cambios;614/R5 no iniciados. No nuevas investigaciones/despliegues.


#### Cierre D-031 — 2026-11-05 22:01 CET

623 DONE técnico21/600,804s+watch31/901,544s.617 inicial13/360,537s y entregaAPI
correctos, pero watcher31/901,797s FAIL por RAM: se revoca el marcador histórico
D025 CT617 completed como aceptación final, conserva resultado inicial como
provisional y se restaura originales/checkpoint8. Registro validado8, no9 ni12.
615 no desplegado:preflight503, no cambios activos.614/R5 no iniciados.
Política BLOCKED, recovery617 terminado y retirado de permiso de recuperación;
HALTs y candidatos preservados. No apps/DB/recursos ni exporters610/excluidos.
35 backups revalidados,56 inputs exporters+24Prom reproducibles; ocho cadenas
sanas,17/17/11 targetsup. Sin nuevos erroresTelegram, recepción humana nueva no
atribuida. CausaRAM pendiente; no afirmar causalidad única por snapshotsdistintos.
Siguiente sesión617 RAM temporal, salud615 requiere alcance separado. Sincommit/push.


### D-032 — diagnóstico CT617 y procedimiento común (sin despliegue)

2026-11-06 (Europe/Madrid). Propietario autoriza lectura de producción, diagnóstico
RAM617, comparación de ocho aceptados y revisión619/623/617. Correcciones IaC y
regresiones locales/preparación autorizadas; despliegue pendiente de presentación
y autorización posterior. No615 ni otros lotes, no modificar ocho aceptados,
HALTs/política permanecen BLOCKED; sin reinicios, recursos, commits/push.


#### Resultado D-032 — diagnóstico/preparación, no despliegue

2026-11-06 10:35 CET. Defecto confirmado: RAM cacheada contra actual; no se puede
demostrar la causa única histórica sin historial RAM. Docker/cgroup coinciden en
480 lecturas617; control623 cinco contenedores alineados y44 regresiones PASS.
Preparado opt-in RAM617 con mismos márgenes, identidad/generación/timestamps,
doble extremo sin interpolación, logger acotado y proyectoCompose propio.
Ocho aceptados sin cambios,56 inputs iguales,17/17/11 up. Sin envíosTelegram.
623 Node real1.11.1: se corrige errata1.10.2, no cambio de imagen.
Producción8/2/7, política BLOCKED; nueva aprobación617 previa a ejecución.
Propuestas comunes (contrato declarativo/validadores importados/promoción tras
watcher) no autorizan despliegue global ni modificar ocho aceptados.
[Diagnóstico](CT617-RAM-RCA.md). Sin commits/push.


### D-033 — reentrada controlada CT617 autorizada

2026-11-06 (Europe/Madrid). Propietario autoriza exclusivamente617 conforme
a CT617-RAM-RCA: backups/checkpoint nuevos y verificados, IaC RAM alineada sin
ampliar tolerancias, fuentes/apps/OOM/reinicios, rollback/idempotencia,600s/21
y900s de vigilancia, cadenaProm/AM/Telegram. Permite configuraciónProm610 mínima
y recuperación coordinada; no exporters610 ni615/otros LXC. Fallo exige rollback
y detención; DONE solo tras todas las comprobaciones. Sin commits/push.


#### Cierre D-033 — 2026-11-06 11:15 CET

Primer apply617 rechazado por `Held candidate differs`, candidatoheld histórico
consultado con records de runnuevo vacíos. Error de aislamientoheld en preparación,
no fallo RAM nuevo. Rollback coordinado y originales/apps verificados, checkpoint8
y24 archivosProm exactos, ocho aceptados sin cambios,17/17/11UP;OOMdelta0.
600s/900s, idempotencia real y pruebaTelegram no ejecutadas. Correcciónheld propia
ram-v1 y simulación apply/rollback/reapply/idempotencia localPASS,27 pruebasPASS.
No se reintentó ni avanzó615. PolíticaBLOCKED, permisos vacíos, HALTs/backups
preservados. Nueva reentrada requiere aprobación; [cierre](CT617-D033-EXECUTION.md).


### D-034 — SKIP AND CONTINUE exclusivo614→61211

2026-11-06 (Europe/Madrid). Propietario cambia estrategia:617/615 aplazados;
autoriza614 después61211, configuraciónProm610 mínima con backup/promtool,
observación180s/7 y extensión si anomalía, CPU/RAM alineadas sin relajar márgenes,
rollback/idempotencia/apps/OOM/Prom/AM/Telegram. Skip solo si fallo aislado
demostrado, originales/app funcionando y cobertura anterior íntegra. Backups,
IaC común, SSH/identidad, Promglobal/cobertura, AM/Telegram, incertidumbre, rollback
incompleto o datos en riesgo exigen HALT GLOBAL. Sin reintentos indefinidos.
No618/622/611/616/exporters610 ni617/615; finalizar al tratar los dos o HALTglobal.
Sin commits/push. Sustituye orden estricto histórico solo en este alcance.


#### Resultado D-034 — 2026-11-06 11:35 CET

PolíticaSKIP versionada, driver secuencial con guardas/pruebas positivas y sin
promoción antes dewatcher. RAMalineada extendida solo a candidatos614/61211,
180s/7 ywatch900s conservados,36 regresionesPASS. Preflight614salud503 heredada
en ambasapps:originales/config y cobertura verificados, pero aplicación sigue
sin funcionar según contrato. HALT GLOBAL por application_working=False;
61211noiniciado. No mutacionesremotas/backupnuevo/apply/recarga/reinicios.
8DONE/3BLOCKED/6PENDING; cola617/615/614, políticaBLOCKED y permisosvacíos.
NoCRM/EVA/Grafana/Blackbox/exporters610, ni commits/push.
[Procedimiento/cierre](SKIP-AND-CONTINUE.md).


### D-035 — incidencias previas frente a regresiones; solo61211

2026-11-06 (Europe/Madrid). Propietario sustituye vetoD034: aplicaciónunhealthy
antes de cualquier mutación, originalsin cambios, legacy/alertas conservados y
ninguna dependencia crítica no verificada permiten BLOCKED / PRE-EXISTING ISSUE
y continuar haciaCT independiente. Regresión local exige rollback y contención;
fallos compartidos/backups/datos/rollback/estado incierto/dependencias desconocidas
conservanHALT GLOBAL. Autoriza exclusivamente61211 y configProm610 mínima,
tras verificar614preexistente/aislado e independencia. No reparar614 niapps,
no ocho aceptados niR6/R7, no commits/push. GatesCPU/RAM/Docker/cgroups, backups,
rollback/idempotencia,180s/7 convencional ywatch900s conservados. DONEsoloPASSfinal.


#### Cierre D-035 — 2026-11-06 12:24 CET

614CaseBpreexistente/aislado/fingerprintsintactos e independencia61211verificada;
no reparación. Solo61211ejecutado: backups/checkpoint/promtool/fuentes/rollback/
idempotenciaPASS; inicial13/360,225s yTelegramAPI+2/0errores. Watch31/903.637s
FAIL por lectorRAMcomún: Python3.10rechaza fracciónRFC3339Nano5dígitos sinpadding.
CPUlector sigueválido; no seafirmafalloexporter. CaseD/HALT GLOBAL, recuperación
coordinada yoriginales/apps/checkpoint8/24archivosverificados, backupslegibles
externoPVE,OOMdelta0,ochoaceptadosintactos,17/17/11UP. Correcciónparser+regresión
fracciones0–9 solo local.52pruebasPASS.8DONE/4BLOCKED/5PENDING; ningúnR6/R7,
políticaBLOCKEDpermisosvacíos,HALTs/candidatos/backupsretenidos,sincommit/push.
[Informe](CT61211-D035-EXECUTION.md). El vetoD034 de reparar614 queda sustituido,
pero HALTcomún deD035 impide otrointentoautomático en estaejecución.


### D-036 — estabilizar framework común sin despliegue

2026-11-06 (Europe/Madrid). Propietario autoriza auditoría/corrección localCPU/RAM,
regresiones saneadas de619/623/617/61211 ycompatibilidad de lectura en ochoaceptados.
Sin cambiosproducción/exporters/reinicios/apps/Terraformapply/otrosCT/commit/push.
No ampliar tolerancias ni suprimir gates. Preparar procedimiento61211 sin ejecutarlo.
F4 sigue8DONE/4BLOCKED/5PENDING;políticaBLOCKED/HALTs conservados.


#### Resultado D-036 — 2026-11-06 13:29 CET

Framework común local cerrado: parser únicoCPU/RAM, captura/unidades/identidad con
scopeLXC, rawproof, historia acotada/ordenada y lectores vivos; revisioneshash en
Compose/held y auditoría fresca61211.80 pruebasPASS con fixtures reales saneados.
Compatibilidad final8/8,147frames/31contenedores,56inputs e identidades intactos,
recursosPVE y17/17/11UP/cadenas8verificados. Rechazo inicial625frescura/futuro
conservado comoantecedente sin muestra completa; no asignar causa ni relajar90s.
No cambiosproducción/exporters/reinicios/apps/recargas/Telegramtest/Terraformapply.
Política sigueBLOCKED/HALTs preservados;8DONE/4BLOCKED/5PENDING. Preparación61211
local `framework-347ef93c2fca`,sin ejecución; [informe](VALIDATION-FRAMEWORK.md).
Sin commits/push. No se acepta ningún CT por esta validación local/de lectura.


### D-037 — reintento exclusivo61211 con frameworkD036 autorizado

2026-11-06 (Europe/Madrid). Propietario autoriza61211 con pruebas/originales/
backups/checkpoint/IaC verificados, fuentesCPU/RAM/identidad/timestamps/Docker,
integraciónProm mínima, apps/OOM/reinicios, rollback/idempotencia, observaciones
yAM/Telegram. No otrosLXC salvo configuraciónProm610 estrictamente necesaria
del procedimiento; noR6/R7. Fallo local exige retorno seguro ydocumentación;
nuevo defecto común exige detener ypresentar diagnóstico, sin reintento automático.
Sin commits/push. Mantener originales/backups/HALTs históricos.

<!-- D025 CT61211 completed -->

Resultado operativo D025 CT61211: PASS technique, 13 muestras/360.188s, backup externo/rollback/idempotencia verificados. Telegram API: +2.0 envíos, 0.0 errores nuevos; no se atribuye recepción humana. [Prueba](evidence/2026-11-02-rollout-61211.json). F4 sigue IN PROGRESS.

**Resultado D037 — 2026-11-06 16:38 CET:** CT61211 DONE;9DONE/3BLOCKED/5PENDING.
FrameworkD036 desplegado solo61211,80tests y lectura8/8PASS; rollback real,
idempotencia, inicial13/360,188s ywatch31/901,755sPASS. Auditoría final44muestras,
4backups y12inputsverificados; apps200/PGready,OOMdelta0,sin reinicios inesperados.
Prom17/17/11 y9cadenas, AMsano,TelegramAPI+2/0errores(sinconfirmaciónhumana).
614sin cambios503preexistente; ocho aceptados yProm/AMintactos. PolíticaCOMPLETED,
permisosvacíos,sincontinuación. NoR6/R7,Terraformapply,commits/push.
[Informe](CT61211-D037-EXECUTION.md); tiempo 38.0min excluyendo pausa
registrada145.9min. Propuesta no autorizada:
revisión/preflightCRM→EVA;617/615/614continúanpara recuperaciónindividualal final.

### D-038 — perfiles STANDARD/CRITICAL y alcance convencional

2026-11-06 (Europe/Madrid). Propietario aprueba STANDARD180s, sinwatch900s
ni ensayo rollback porCT si existe prueba compatible del procedimiento sin cambios;
CRITICAL600s y continuidad/recuperación específicas. No repetir pruebas comunes
sin cambio de código/dependencias; Telegram real porlote o cambio de configuración,
AMdisponible/erroresTelegram estables porCT. Aplicación previamenteunhealthy no
impide aceptar monitorización si no empeora y conserva alertas/dependencias seguras.
MárgenesCPU/RAM/frescura eidentidad intactos; ausentes nunca cero.
Autoriza convencionalesPENDING del plan, excluye617/615/614,CRM/EVA/observabilidad.
Inventario documental: cincoPENDING618/622/611/616/610, todosCRITICAL; cero
STANDARDautorizados. Verificación real porlectura y preparaciónIaC, sin despliegue
ni ampliación aCRITICAL. Sin apps/DB/recursosPVE,Terraformapply,commit/push.

Resultado D038 — 2026-11-06 17:32 CET: perfiles y evaluación local preparados,25testsPASS,
producción9cadenas/17Node/17cAdvisor/11BlackboxUP,Prom/AM200;sin nuevos errores
Telegram. CeroSTANDARDpendientes,ningúnCTdesplegado.9DONE/3BLOCKED/5PENDING.
Driverhistórico no recertificado como ejecutor deperfiles nuevos; próximo alcance
CRITICAL requiere autorización específica ycontinuidad/recuperación porservicio.
Tiempo:3.4min; [política](VALIDATION-PROFILES.md). Sincommit/push.

### D-039 — ejecuciónCRITICAL618→622→611→616→610 autorizada

Propietario autoriza cincoCT secuenciales,600s/21 porCT,backup recuperable,
fuentesCPU/RAM/Docker,baselineappsinregresión,idempotencia,AM/Telegram sin errores.
Sin ensayo rollback repetido si mecanismo aplicable ya probado; entregaTelegram
porloteR6/R7. Soloexporters yconfigPrommínima conbackup/promtool. CRMconservar
Budibase3.27.4/duplicadodetenido/DB/volúmenes/RAM;EVAsinlimpiezas/datos/retención;
observabilidadsinpérdida históricos/volúmenes/config/secretosAM.610último con
observaciónexterna independiente. SKIPsoloconretornoseguro/legacy/dependencias;
HALTporfallocompartido/backup/rollback/datos/estadoincierto.617/615/614excluidos.
SinTerraformapply,commit/push. Adaptaciónmínima deldriver, noframeworknuevo.

D039618: primerdriver emitióHALTporerror deprobe sinclasificación; recuperóoriginales
/checkpoint/cobertura/appsinregresión. Diagnósticopositivoaislado: RAMcAdvisor
20.582.400B entre brackets14–30MB; CPU7/7 yRAMrestantes6/6 correctos. No se
acepta ni relaja eseFAIL. Evidenciareplaycon reloj de muestra explícito, nofrescura
actual. Se conservaHALThistórico; continuaciónautorizadaD039ennuevorun622→611→616→610,
sinreintentar618. [Aislamiento](evidence/2026-11-06-d039-618-isolation.json).

<!-- D025 CT611 completed -->

Resultado operativo D025 CT611: PASS technique, 21 muestras/600.485s, backup externo/rollback/idempotencia verificados. Telegram API: +0 envíos, 0 errores nuevos; no se atribuye recepción humana. [Prueba](evidence/2026-11-02-rollout-611.json). F4 sigue IN PROGRESS.

<!-- D025 CT616 completed -->

Resultado operativo D025 CT616: PASS technique, 21 muestras/600.485s, backup externo/rollback/idempotencia verificados. Telegram API: +0 envíos, 0 errores nuevos; no se atribuye recepción humana. [Prueba](evidence/2026-11-02-rollout-616.json). F4 sigue IN PROGRESS.

<!-- D025 CT610 completed -->

Resultado operativo D025 CT610: PASS technique, 21 muestras/600.372s, backup externo/rollback/idempotencia verificados. Telegram API: +2.0 envíos, 0.0 errores nuevos; no se atribuye recepción humana. [Prueba](evidence/2026-11-02-rollout-610.json). F4 sigue IN PROGRESS.

Resultado D039 — 2026-11-06 19:46 CET:622/611/616/610DONE,13/17;618BLOCKED/ROLLED BACK
seguro porRAMvolátil.617/615/614sinintervención;4BLOCKED/0PENDINGsinintentar.
600s/21cadaDONE,84muestras;16backups verificados;idempotencia;AM/Telegram/históricos
conservados.Observadorexterno61023/23PASS. TelegramporloteR6/R7API+4/0fallosnuevos.
Métricas/thresholds sin cambios;25testspertinentesPASS. Tiempo:12.4min.
PolíticaCOMPLETED/permisosvacíos. Sinapp/DB/recursosPVE/volúmenes,Tfapply,commit/push.
[Consolidado](CRITICAL-D039-EXECUTION.md). Recuperación617→618 espropuesta,noautorización.

### D-040 — ventanas porservicio, solo nuevas observaciones

Propietario aprueba convencionales/Grafana/Blackbox180s(7muestras),CRM/EVA300s(11),
Prometheus/Alertmanager600s(21),cadencia30s. No alterar observaciones iniciadas ni
repetir aceptados. Mantener CPU/RAM/Docker,exporters,baselineapps sinregresión,
OOM/reinicios,Promrecogiendo,AM/erroresTelegram,backups/rollback. Vigilancia posterior
continua enProm/AM y registro de anomalías; no añade espera bloqueante900s. No
atribuir evaluación de reglasfor aún no transcurrida. Regresión/fallocompartido
exige parada/recuperación. Política de duración no reabre bloqueados: D039cerrado,
13DONE/4BLOCKED/0PENDINGsinintentar,sin procesos activos ni nuevas mutaciones.

ResultadoD040 — 2026-11-06 20:01 CET: configuración/generador/driver actualizados, ventana congelada al inicio;17testsPASS. Sin ejecución deproducción ni cambios deaceptación (13/17). Vigilancia existenteProm/AM mantenida; sin repetir aceptados ni reabrir bloqueados.

### D-041 — recuperación secuencial617→618→615→614 autorizada

Propietario autoriza loscuatroCT,13aceptados sinreaplicar. STANDARD180s/7;
CRM300s/11. Backupverificado,CPU/RAM/Docker reales,Prom/AM/Telegram,idempotencia,
apps sinregresión.615/614HTTP503preexistente permitido,conservaralertas,sinrepararapps;
CRMsinBudibase/DB/volúmenes/recursos yduplicadosdetenidos.617usarcorrecciónheld y
frameworktemporalcomún. SKIP trasretornoseguro/dependenciasaisladas; diagnóstico
máximo15–20min,HALTpara recuperación/backups/datos/servicioscompartidos/estadoincierto.
No vigilancia bloqueante adicional,ni pruebas completas deframework sin cambios.
Soloexporters yconfigPrommínima medianteIaC,promtool/backup/recargacontrolada.
SinTerraformapply,commit/push.17/17coberturaexporters no equivale aalertas/dashboards/
seguridadglobalcompletadas. Ventanas/reglasfor reportadas según evidencia real.

PreparaciónD041: candidato/held determinista porrun,conservandoanteriores;
CRM mejora precisión decapturaRAM0,5→0,1s,sin cambiar fórmula/tolerancias,brackets,
identidad ni límites2s/0,5s.24pruebasafectadasPASS;13cadenas y17/17/11UP porlectura.
CanalAM/Telegramidéntico porhash alD039; sereutiliza entregaD039 sin nuevoFIRING
porCT, controlandoAM/errores durantecadaobservación.615/614 reportanHTTP503 y
PRE_EXISTING_HTTP_503 explícitos aunqueelgate denoregresión pase.

<!-- D025 CT615 completed -->

Resultado operativo D025 CT615: PASS technique, 7 muestras/180.122s, backup externo/rollback/idempotencia verificados. Telegram API: +0 envíos, 0 errores nuevos; no se atribuye recepción humana. [Prueba](evidence/2026-11-02-rollout-615.json). F4 sigue IN PROGRESS.

<!-- D025 CT614 completed -->

Resultado operativo D025 CT614: PASS technique, 7 muestras/180.129s, backup externo/rollback/idempotencia verificados. Telegram API: +0 envíos, 0 errores nuevos; no se atribuye recepción humana. [Prueba](evidence/2026-11-02-rollout-614.json). F4 sigue IN PROGRESS.

ResultadoD041 — 2026-11-06 21:08 CET:617/618/615/614DONE,17/17coberturaexporterscompletada,
32muestrasválidas/ventanas180-300-180-180,0OOM/reiniciosnuevos,16backupsverificados.
615/614siguen503,sinregresión;noapphealthy.617heldcorregido conidentidadporrun;
CRMcapturaRAM0,1s/bracketmáximo0,123s,sin ampliar tolerancias.13previos yProm/AM
intactos;17/17/11UP,17cadenas. CanalD039sin cambios/erroresnuevos,sin entrega nueva.
24testsafectadosPASS. Tiempo:12.4min. [Cierre](EXPORTERS-D041-CLOSURE.md).
Cierre especifico decoberturaexporters;no certificaalertasfor/dashboards/seguridad
ni complementosheredados aúnnoejecutados. PolíticaCOMPLETED/permisosvacíos,sinotroCT,
sinTerraformapply/commit/push. RevisiónF5espropuesta,noautorizacióndeproducción.


### D-042 — consolidación Git autorizada, sin producción

2026-11-06 (Europe/Madrid). El propietario autoriza diagnóstico, auditoría de
secretos, commits locales curados y push normal por SSH a la rama correspondiente
si revisión, pruebas y seguridad pasan; sin force push ni reescritura de historia.
Alcance F7-01 y prevención local F7-04: excluir credenciales/estado/artefactos
privados conservando sus archivos y respaldos. No despliegues ni reinicios.
Secretos históricos requieren rotación separada; no se consideran revocados.
Los cambios de aplicaciones ajenos a monitorización se conservan sin incluir.

Resultado D042: consolidación curada publicada por SSH normal, sin force ni
reescritura. Auditoría saliente sin secretos nuevos; credenciales/estado locales
preservados fuera de seguimiento. Secretos históricos requieren rotación; no
revocados por eliminación de archivos. F7-01 DONE solo monitorización, F7 global
IN PROGRESS; aplicaciones ajenas pendientes. Sin producción.
[Informe](GIT-CONSOLIDATION-D042.md), [evidencia](evidence/2026-11-06-git-consolidation.json).

### D-043 — diagnóstico614sGTM/Preview yBlackbox, sololectura

Propietario autoriza inspecciónCompose/envsaneado/comunicación/proxy/EdgeRouter/
rutaspúblicas ymétodosHTTP, sin enviar eventosGA4válidos. PrepararIaCmínima,noaplicar.
Sinproducción/reinicios/imágenes/GoogleCloud/DNS/router/commit/push. Configs ylogs
se filtran antes de cualquier salida; nuncaCONTAINER_CONFIG,auth ni datosdeeventos.
F4cobertura17/17conservada; investigación deapp/sondaINC005 yF5, no nuevo rollout.

ResultadoD043 — 2026-11-06 22:05 CET:diagnóstico ypreparaciónDONE,remediación NOaplicada.
503real dehealthbootstrapcaducado,configmainfuncional/refresco<5min,Previewenred
alcanzable;curlDockerinexistente essegundodefecto. Mismoid/env/auth válido,sinvalores
publicados enartefactos. Blackboxactual200,alertahistóricaHTTP0el2nov;HEADnoescausa
acreditada. Overlayhealthcheckvalidado,nuevasprobes opcionalesdeferred,noactivas.
SiguientepasorequiereautorizarrecreaciónPreview→mainmismaimagen/env,sincambios
proxy/EdgeRouter/DNS/GCloud. GA4endtoendnocertificado;noeventosválidosdeprueba.
[Informe](CT614-SGTM-D043.md).Sincommit/push/nuevosreinicios.

### D-044 — recuperacióncontrolada614Preview→sGTMautorizada

Propietario autoriza backupverificadodelComposeACTIVO eimágenes/config/secretos,
healthcheckNode nativo enIaC,recrear SOLOPreview,exigir/healthz200antes derecrear
SOLOprincipal. Mismasimágenes/env/secretos/puertos/recursos. NoComposehistóricorepo,
Nginx/EdgeRouter/DNS/GCloud/sondasBlackbox/pull/build ni otrosCT. Fallo detienesecuencia
yrecuperaconfiguración/imagen previstas; conservabackups. Validar saludarranque,
dominiopúblico/Blackbox/Prom/AM e idempotencia. Investigar/documentar prevención de
caducidad,sin implementarcron/timers/reiniciosautomáticos. Sincommit/push.


### D-044 — cierre de recuperación CT 614

## D-044 — CT 614 recuperado — DONE

Preview y sGTM healthy; `/healthz` local y público HTTP 200. Healthcheck Node
aplicado mediante overlay sobre Compose activo; misma imagen, variables, puertos
y recursos. Backups privados verificados en CT/PVE/fuera del host, idempotencia
PASS y sin nuevos OOM. Prom/AM disponibles: 17 Node/17 cAdvisor/11 Blackbox UP;
sondas collect nuevas HTTP 200 y sin incremento de errores Telegram.
Hubo reintentos por defectos del script: 7 recreaciones Preview y 4 principal,
incluidos rollbacks; corregidos y registrados. No cambios de proxy/DNS/Cloud/sondas.
F4 exporters conserva 17/17. Prevención de caducidad semanal solo propuesta;
no timers ni reinicios automáticos instalados. Sin commit/push.
[Resultado, riesgos y recuperación](CT614-SGTM-D044-RECOVERY.md).
Siguiente paso: revisar mantenimiento periódico; no ejecución automática adicional.

### D-045 — Issue sGTM e inventario operativo IaC (autorizado)

Alcance: buscar/crear/actualizar Issue de recurrencia CT 614; descubrir por lectura
los 17 LXC, generar fichas Notes y Markdown desde inventario versionado. Aplicación
Terraform autorizada únicamente si el plan completo cambia descripciones; cualquier
cambio adicional exige detener apply y consultar. No reinicios, recursos, apps,
contenedores, DNS/proxy, secretos, commits ni pushes. Preservar cambios EVA/Journal/
Gestoría y notas útiles. F4 cobertura 17/17 conservada; documentación transversal F7.

### D-045 — resultado y propuesta pendiente

## D-045 — inventario IaC preparado; Notes BLOCKED por tags

Issue sGTM creada: [#1](https://github.com/eduardo152030/mailerblend-platform-infra/issues/1),
sin automatizar reinicios. Inventario de 17 LXC generado desde recursos declarados,
metadatos funcionales y observaciones PVE/Docker/Nginx fechadas. Campos no
confirmados explícitos; fichas Markdown y Notes comparten fuente y plantilla.
9 pruebas PASS, schema/referencias/secretos y Terraform fmt/validate PASS.
Plan completo: 17 updates de **description y tags**, sin creación/destrucción;
**NO apply**, conforme al límite autorizado. Todas las Notes de producción siguen
originales. 17/17 boot IDs, configuración PVE comprobada e identidades/arranques/
reinicios de todos los contenedores sin cambios. Trabajo previo preservado.
F4 exporters conserva cierre 17/17; documentación transversal F7 en curso.
[Inventario](../inventory/LXC-INVENTORY.md), [operación y bloqueo](../inventory/README.md),
[evidencia](evidence/2026-11-06-d045-result.json). Sin commit/push.
Siguiente paso requiere autorización: conservar tags reales mediante override
propuesto existente y generar nuevo plan estrictamente de Notes antes de aplicar.

La propuesta `inventory/notes-preserve-tags.proposed.tfvars.json` NO está autorizada
ni aplicada todavía. Usa el override de tags existente, no ignore_changes ni -target.
No aceptar ni aplicar el plan actual que incluye cambios de etiquetas.

### D-046 — Notes exclusivamente CT 614 (autorizado)

El propietario sustituye el alcance global D045: consultar solo CT614 y el bloque
Nginx de su dominio; preparar/aplicar únicamente description de CT614 si el plan
lo confirma. Preservar tags actuales, recursos, aplicaciones y contenedores. Se usa
plan dirigido al recurso CT614 para no refrescar/investigar otros LXC; no supone
permiso para aplicar otros recursos ni para el plan global anterior. Sin commits/push.

### D-046 — cierre

## D-046 — Notes CT 614 aplicadas — DONE

Trabajo limitado a infra-nucleoedge y lectura de su ruta Nginx. Serving/Preview
healthy y healthz local/público 200. Notes específicas en formato Purpose,
Environment, Network, Applications, Dependencies, Monitoring, IaC y Known Issues;
fuente versionada `services/infra-nucleoedge/NOTES.md`, integrada en generador y
plantilla Terraform. Production confirmado por propietario. Sin secretos.
Plan dirigido: 1 update de description de CT614; tags conservados por var-file
acotado. Apply PASS, Notes exactas verificadas y segundo plan sin cambios.
Configuración PVE salvo description, boot ID, contenedores y Compose intactos;
estado de otros recursos Terraform idéntico, sin investigar otros LXC.
11 tests, generación, fmt/validate y diff-check PASS. Sin commit/push.
[Fuente y procedimiento](../../services/infra-nucleoedge/NOTES-IAC.md),
[evidencia](evidence/2026-11-06-d046-result.json).
D045 global sigue sin aplicar: solo CT614 tiene Notes nuevas. F4 exporters17/17
no reabierto; F7 documental en curso. Siguiente: revisión por propietario, sin
continuación automática ni nuevos cambios autorizados.

### D-047 — ficha individual de CT614

Autorizado inventario técnico exclusivo CT614, consultas de lectura a sus
dependencias directas Nginx/Prometheus/Blackbox y resumen Notes mediante IaC.
Sin cambios de apps, tags, recursos, DNS/Nginx ni reinicios; cualquier aplicación
de Notes exige plan exclusivo description CT614. No eventos GA4 ni secretos.
Documentar discrepancias, backups verificables y límites funcionales; sin commit/push.

### D-047 — cierre

## D-047 — ficha individual CT614 y Notes — DONE

[Inventario técnico principal](../inventory/614-LXC-INVENTORY.md): secciones A–L,
diagrama Mermaid, arquitectura/rutas, versiones por métricas/digest, operaciones,
backups y límites. El inventario general solo enlaza su ficha; no duplica CT614.
Lectura limitada a CT614 y sus dependencias directas Nginx/Prometheus/Blackbox.
Confirmado: 2 CPU, 2048 MiB, Ubuntu22.04.5, rootfs10G; Serving/Preview healthy,
healthz local/público200. Node1.10.2:9100, cAdvisorv0.60.6:8085, targets UP y dos
probes collect200. `/orbit/healthz` y `/orbit/ingest` son rutas exactas a CT617;
no se consultó ese CT. DNS/TLS actuales documentados, sin cambios.
Discrepancias documentadas: disco16GiB declarado/10Greal, Compose histórico distinto,
labels monitorización diferentes; no corregidas. GA4 y prevención automática pendientes.
Notes resumidas aplicadas por plan exclusivo description614, tags conservados;
verificación exacta y segundo plan cero cambios. Boot/contenedores/Compose/Nginx y
estado Terraform de otros recursos intactos.12tests y validaciones locales PASS.
Sin eventosGA4, reinicios, recreaciones, secretos, commits ni pushes.
[Evidencia](evidence/2026-11-06-d047-result.json). F4exporters17/17 conservado;
F7 documental en curso. Siguiente: revisión del propietario; ejecución detenida,
sin avance automático a otro LXC.

### D-048 — recuperación CT615 autorizada

Propietario autoriza reutilizar D044 en CT615 si el preflight confirma misma causa
y ausencia de diferencias materiales: Compose ACTIVO, backup verificado antes de
modificar, misma imagen/config/env/secretos/puertos/montajes/recursos; checker Node,
Preview antes de Serving, salud200, cobertura y OOM/idempotencia. No otros LXC,
Nginx/DNS/Cloud ni reinicios automáticos, eventosGA4, commits o pushes. Issue#1
revisada; prevenir sus errores de orquestación y contar todas las recreaciones.

### D-048 — cierre de recuperación CT615

## D-048 — CT615 sGTM recuperado — DONE

Preview y Serving healthy; healthz18092/18091 y público200. Caducidad del bootstrap
con alta confianza:50días, configuración válida/igual y diagnóstico de edad coherente.
Checker Node sobre Compose ACTIVO; mismo digest/env/secretos/puertos/montajes/recursos.
**1 recreación Preview + 1 Serving**, cero adicionales; segunda aplicación sin
recreaciones, OOMdeltas0 y sin errores graves de arranque detectados.
Recuperador D044 reutilizado con perfil615; Nginx Preview usa `/gtm/` con cabecera
de selección, no `/preview/`. Ruta y parámetros conservados, sin cambiar Nginx.
Backups CT/PVE/externo verificados antes de intervenir.17Node/17cAdvisor/11BlackboxUP,
Prom/AM ready, sonda Mailerblend frescaHTTP200; Telegram132/56 sin errores nuevos.
21tests pertinentesPASS. Ejecución productiva68.444s; sin vigilancia redundante.
[Procedimiento/evidencias](CT615-SGTM-D048-RECOVERY.md). No otrosLXC modificados,
Terraformapply, reiniciosautomáticos, eventosGA4, commits ni pushes.
F4exporters17/17 conservado; el503 preexistente de615 queda resuelto (sustituye
estado de salud histórico D041). GA4endtoend/prevención Issue#1 pendientes.
Inventario local actualizado; Notes615 generadas NOaplicadas a Proxmox.
Siguiente: revisión del propietario; ejecución detenida, sin otroLXC autorizado.

### D-049 — inventario individual y Notes CT615 autorizados

Propietario autoriza ficha técnica específica, consultas breves de lectura a CT615
y dependencias directas (Nginx/DNS/monitorización), diagrama y Notes IaC. Aplicar
solo si plan dirigido cambia exclusivamente description CT615; preservar tags y
todos los otros atributos. Evaluar ampliación necesaria de Issue#1 sin duplicados.
No apps/contenedores/recursos/Nginx/DNS/certificados, reinicios, commits ni pushes.

### D-049 — cierre

## D-049 — ficha individual y Notes CT615 — DONE

[Ficha técnica principal](../inventory/615-LXC-INVENTORY.md) A–L y Mermaid de rutas
reales. Sitio Mailerblend HTTPS200 verificado; envío navegador/GA4 pendiente.
Nginx: collect/healthy/fallback Serving, `/gtm/` selecciona Preview por cabeceras;
no se copió `/preview/` de CT614. Serving/Preview healthy, salud local/pública200;
Node1.10.2:9100/cAdvisorv0.60.6:8085 up1, sonda collect1/HTTP200, Prom/AM ready.
Clasificación prod por tags; 2CPU/2048MiB/Ubuntu22.04.5, disco10G real/16GiB declarado.
Compose local conserva curl histórico; activo usa overlay Node. Discrepancias
solo documentadas. Backups D048 presentes; no nueva restauración ni eventosGA4.
[Notes IaC](../../services/infra-mailerblend-edge/NOTES.md) aplicadas: plan dirigido
solo description615, tags intactos; lectura exacta y segundo plan cero cambios.
Boot/contenedores/Compose/Nginx y estado Terraform de otros recursos sin cambios.
14tests locales y controles de generación/fmt/validate/enlaces PASS. Issue#1 ampliada
con segundo caso615/perfil Preview, sin duplicados ni automatizar reinicios.
[Evidencia](evidence/2026-11-06-d049-result.json),
[operación Notes](../../services/infra-mailerblend-edge/NOTES-IAC.md).
F4 exporters17/17 conservado; F7 documental en curso. Sin commit/push.
Siguiente: revisión del propietario; ejecución detenida, no avanzar a otroLXC.

### D-050 — Fase 5 autorizada

2026-11-06 (Europe/Madrid). Solicitud vigente autoriza optimizar reglas, rutas,
inhibiciones y Telegram mediante IaC; aplicar exclusivamente configuración de
Prometheus/Alertmanager tras validación, backup y revisión de diff. Ensayo
FIRING/RESOLVED autorizado sin incidencia real ni eventos Analytics. Regresión de
monitorización/notificaciones exige restaurar. No apps/recursos/LXC/commit/push.
Sustituye la prohibición histórica de ensayos F5 en este alcance.

### D-050 — ejecución y aceptación de Fase 5

2026-11-07 (Europe/Madrid). Solicitud vigente ejecutada exclusivamente sobre
configuración Prometheus/Alertmanager. Umbrales y rutas concretos en
[PHASE5-D050-EXECUTION](PHASE5-D050-EXECUTION.md), evidencia
[resultado](evidence/2026-11-07-d050-result.json). CPU física retirada de alerting;
CPU aceptada F4 no modificada. Nuevos pares RAM/disco/TLS e inhibición por recurso;
no inhibición de apps independientes por CT. Recargas con backup y rollback;
primera aplicación revertida por gate prematuro unknown, sin errores de evaluación
ni notificación, después corregido. Segunda aplicación idéntica sin recargas.
Ensayo real exporter→Prometheus→reglas→AM→Telegram, API132→134 sin errores nuevos.
El propietario confirma explícitamente «Recibidos ambos y claros» para FIRING y
RESOLVED y lectura móvil. F5 DONE — Accepted; no dispensa UAT. Ensayo retirado.
Tres unhealthy CRM/EVA preexistentes se monitorizan, no se reparan ni aceptan como
saludables. Sin aplicaciones/exporters/recursos/volúmenes/reiniciosLXC/commit/push.

Propuestas separadas, NO aprobadas por este cierre: nuevas sondas HTTP específicas
Grafana/CRM, corrección de healthchecks CRM/EVA y revisión del AM extra heredado.
Fase 6 requiere alcance/autorización; no la habilita automáticamente este cierre.

### D-051 — corrección acotada CRM/EVA autorizada

2026-11-07 (Europe/Madrid). Solicitud explícita: «revisa y soluciona estas 3 alarmas».
Alcance: focalboard CT622, budibase-app y crm-api CT618. Diagnosticar checks y salud
real; corregir mediante IaC con backup, rollback y validación. Recreación mínima
solo si es necesaria para aplicar sus healthchecks; preservar imágenes, variables,
datos/volúmenes, recursos y otros contenedores. No cambios de reglas para ocultar
los fallos, upgrades, DB/esquemas, recursos PVE, commits/push ni avance F6.

### D-051 — cierre técnico

2026-11-07 16:08 CET. Los tres checks corregidos mediante IaC y aplicados con las
imágenes/env/datos/recursos/redes originales. Backups/restauración staging y
idempotencia verificadas. Tres health1 y cero alarmas objetivo FIRING, Prom/AM
READY y17/17/11 conservados; sin modificar reglas ni ocultar series antiguas.
API1/Focalboard2/Budibase1 candidatos; rollback Focalboard y rechazos preservados.
Incidencia API SIGTERM durante arranque y comparaciones de serialización corregidas
en validador documentadas en [informe](HEALTHCHECKS-D051-EXECUTION.md).
DONE técnico sin nueva UAT funcional ni dispensa extendida; no se certifica parada
SIGTERM bajo cualquier carga. No commits/push ni intervención F6. Propuestas de
revisión de parada API y UAT permanecen separadas, sin ejecución automática.

### D-052 — dashboard principal F6 autorizado

2026-11-07 16:22 CET. Solicitud del propietario autoriza implementar, validar y desplegar por
IaC exclusivamente «Proxmox · LXC Fleet Overview» en CT611, con datos reales de
Prometheus. Preservar dashboards/datasource/usuarios/volumen existentes. Sin apps,
reglas/umbrales F5, Telegram, recursos, reinicios LXC ni commits/push. F6 global
no se declara completada. F6-01/03/05 en curso; F6-02 solo correcciones necesarias
confirmadas por runtime. Validación visual y persistencia se reportarán separadas.
Acceso SSH estricto y Prometheus comprobados; Grafana12.3.1 operativo en3010,
autenticación inicial401. Pendiente acceso existente para API/UI; no resetear claves.
Siguiente: construir consultas/JSON, validar, backup y despliegue acotado.

### D-052 — cierre técnico

2026-11-07 16:36 CET (Europe/Madrid). Dashboard principal provisionado en CT611 con datasource
Prometheus existente: tabla17CT, KPIs17/17Node,17/17cAdvisor,11/11Blackbox,
CPU/RAM/discoLXC, filtros Service/LXC, alertas y diagnóstico Docker.26consultas
reales/9porproxyGrafana PASS;12casos sintéticos y navegador/filtros/rango/enlace
PASS;segunda aplicación cero escrituras/recargas/reinicios.7dashboards/2datasources
conservados, backup CT/fueraPVE y restore-check SQLite/config PASS. Tres retornos
preventivos por metadatos versión/ordenMounts; comparadores corregidos, contenido
ajeno intacto. Cero restarts/recreaciones; providers antiguos duplicados pendientes.
11CT sinsondaasociada siguenUNKNOWN, Dockerhealthy no acredita disponibilidad.
Descripción/tiempoactivo enlazados aPrometheus; sinhistorialRESOLVED. Grafanadinámico,
file_sd requierealtaIaC explícita; no discoveryPVE afirmado. F6 globalINPROGRESS;
aceptaciónvisual propietario y recreaciónreal no realizadas. Sinapps/reglasF5/
Telegram/CT610/recursos/commits/push. Tiempo: 17.4min desde primera lecturaProm.
[Informe](PHASE6-D052-EXECUTION.md), [resultado](evidence/2026-11-07-d052-result.json),
[dashboard](http://192.168.1.111:3010/d/proxmox-lxc-fleet/proxmox-c2b7-lxc-fleet-overview?theme=dark).
Siguiente: revisiónvisual propietario y alcance del próximo dashboard, sinavanceautomático.

### D-053 — auditoría Application Health, solo lectura

2026-11-07 16:56 CET (Europe/Madrid). Solicitud del propietario autoriza auditar los11UNKNOWN
de Fleet Overview: runtime Docker/systemd, endpoints seguros de lectura, métricas
y sondas existentes. Sin cambios de Prometheus/Grafana/Docker/apps ni reinicios,
recreaciones, commits o push. GET de salud y pg_isready diagnóstico, sin ingesta,
login de negocio ni consultas SQL. Solo script/evidencias/documentación locales.
F6-03 auditoría en curso; propuestas requieren revisión, no autorización de aplicación.

### D-053 — resultado y propuestas pendientes

2026-11-07 17:00 CET (Europe/Madrid). Fase 6 IN PROGRESS. Consulta desplegada y runtime
confirman UNKNOWN en CT611/613/616/617/618/620/621/623/624/625/626: ninguno tiene
probe Blackbox asociada. Propuesta: 618 reutiliza readiness D051 por consultas;
617/620/624/626 necesitan 5 targets HTTP en total; 621/623/625 requieren contrato
específico; 611/616 se proponen N/A de monitorización y 613 requiere decisión de
ciclo de vida (demo ausente, no declarar N/A automáticamente). Categorías y totales
son propuestas, no cambios aceptados. Orbit público healthz200 desde CT616; directo
403. Focalboard621 ping devuelve el mismo HTML que raíz; no prueba API healthy.
Odoo623 loopback200, 8080 solo Nginx de prueba; PostgreSQL625 pg_isready0 sin métrica
periódica. Salud Docker de CRM es readiness, no disponibilidad externa certificada.
Auditoría de lectura, sin configuración/recargas/reinicios/recreaciones/commits/push;
solo script, evidencia y documentación locales. Los 11 UNKNOWN se conservan.
[Informe](PHASE6-D053-APPLICATION-HEALTH-AUDIT.md),
[evidencia](evidence/2026-11-07-d053-audit.json),
[conservación](evidence/2026-11-07-d053-final.json).
Siguiente: revisión del propietario; ninguna implementación autorizada.

### D-054 — autorización vigente

2026-11-07 17:04 CET. Petición autoriza señales de monitorización611/616, readinessCRM618,
sondasOrbit617/dosworkers620/Journal624+626 y columnaUptime dinámica; soloIaC de
monitorización, sin apps/exporters/recursos/reinicios/umbralesF5/commits/push.
Preparación incluye módulosBlackbox mínimos en616 con validación de respuesta y
recarga controlada sin reinicio, necesarios para identidad funcional de sondas.
Se preservan11sondas existentes. Backup/rollback coordinado610/611/616 antes de
aplicar. node_boot_time_seconds observado común alhost, rechazado; no fuentePVE
publicada. UptimeUNKNOWN hasta fuenteLXC fiable, sin collector nuevo ni fallback.
F6INPROGRESS; otrasetapas excluidas. Siguiente: validar candidatos y aplicar alcance.

### D-054 — cierre técnico y límite de Uptime

2026-11-07 17:15 CET (Europe/Madrid). Application Health UNKNOWN11→4:613/621/623/625
conservados.611/616 NOT APPLICABLE como negocio con Monitoring Health real;618
HEALTHY(readiness), sin disponibilidad pública certificada.617/620/624/626 con
sondas funcionales verificadas. Seis sondas nuevas incluida Grafana:11anteriores
preservadas,17BlackboxUP/success1;17Node/17cAdvisor conservados. Regla/umbralesF5,
apps, imágenes, identidades y siete dashboards ajenos intactos. Backups CT/fueraPVE,
restore-check, promtool/parserBlackbox,26casos sintéticos,28consultas y navegador
PASS. Segunda aplicación0escrituras/recargas/reinicios. Sin commits/push.
Columna Uptime dinámica añadida,17filas UNKNOWN: node_boot_time_seconds refleja
arranqueHOST, rechazado por comparación con API PVE17CT. node_time es reloj;
no métrica LXC/PVE publicada. No se afirma uptime real completado; requiere fuente
fiable y alcance separado. No Docker/exporter como sustituto. F6INPROGRESS;
EtapaA DONE técnico, aceptación visual propietario pendiente. Tiempo:12.4min.
[Informe](PHASE6-D054-STAGE-A-EXECUTION.md), [resultado](evidence/2026-11-07-d054-result.json).
Siguiente: revisión visual y autorización de fuente uptime; no EtapaB ni otrosCT.

### D-055 — diagnóstico autorizado y propuesta sin aprobar

2026-11-07 17:24 CET (Europe/Madrid). Diagnóstico/preparación DONE, ejecución BLOCKED por
aprobación según petición: no exporter/métricasPVE ni identidadAPI de sololectura.
TokenTerraform heredaPVEAdmin, no reutilizado. Propuesta concreta: exporterupstream
3.11.0fijadopordigest, único contenedor no-root en610/redProm existente; resources/
status y métricasuptime/info/up porCT, sin listasVMID. Requiere usuario/token nuevos
PVEAuditor en/, privsep=1 y archivo secreto privado. TLS/CA desde610PASS; Compose,
promtool y8casos sintéticosPASS. Soloartefactos locales, nada aplicado:17uptimes
siguenUNKNOWN. Fuente admin puntual previa no equivale a monitorización desplegada.
Sin permisos nuevos, recargas/reinicios/apps/recursos/reglasF5/commits/push.
[Propuesta](PHASE6-D055-UPTIME-PROPOSAL.md),
[evidencia](evidence/2026-11-07-d055-preparation.json).
F6INPROGRESS. Siguiente: aprobación explícita de identidad de lectura y despliegue
acotado; no usar SSHroot periódico ni credencialTerraform para evitarla.

### D-056 — D055 aprobado para ejecución

2026-11-07 17:29 CET. Propietario aprueba D055: usuario prometheus-uptime@pve y tokenexclusivo
uptime, privsep=1, exclusivamentePVEAuditor usuario/token en/, verificaciónefectiva,
secreto privado fueraGit y TLSactivo. ExporterúnicoIaC en610, Prometheus/Grafana
porrecarga/polling sinreiniciarLXC/apps/servicios existentes ni recursos/F5/commit/push.
Validar17uptimes frentePVE, descubrimiento y segundaaplicación. Detener si permisos
adicionales. D055 deja deestar pendiente en estealcance; no habilitaotrasetapas.
Siguiente: backup, creaciónacotada/validaciónpermisos yTLS, arranque soloexporternuevo.

D056 ajuste de implementación: imagenupstream3.11.0 usaPython3.14 y rechazaCA PVE
por extensiónkeyUsage ausente. No se cambiaCA, flagsTLS ni permisos. Mismo paquete
3.11.0 sobrePython3.12 soportado, basefijadapordigest, Dockerfileversionado. Solo se
sustituye el nuevoexporter nointegrado, preservando imagen/contenedor fallido para
diagnóstico. Sin reiniciarservicios preexistentes ni tocarrecursosPVE/apps.

### D-056 — cierre técnico Uptime

2026-11-07 17:43 CET (Europe/Madrid). 17/17uptimes reales enGrafana desdeAPI Proxmox;26LXC
API descubiertos sin listasVMID, filtrados a17monitorizados porinventario dinámico.
Exportercentral3.11.0 en610 no-root, capacidadesvacías/rootfsRO/redProm privada.
Usuario/tokenpropios exclusivamentePVEAuditor, privsep=1; seis privilegiosAudit
verificados, secreto0400fueraGit, TLS/CA activo, sin credencialTerraform.
Comparación17CT conPVE y611/618/624status/current: máximo11.0s (<45s).
Prometheus/GrafanaIaC, previos17Node/17cAdvisor/17Blackbox, reglasF5/umbrales/apps/
identidades/sietedashboards conservados; sin reinicios deLXC/apps/serviciosprevios.
Segundaaplicación0escrituras/recargas/recreaciones. Inicial upstreamPython3.14 rechazó
CA porkeyUsage; mismoexporter sobrePython3.12soportado, base+depsfijadas, TLSsinbypass.
Soloexporternuevo sustituido; candidatoimagen/contenedorretenidos. No rollbackProm.
UptimeDONE técnico; F6INPROGRESS y aceptaciónvisual propietario pendiente. Tiempo:17.1min.
[Informe](PHASE6-D056-UPTIME-EXECUTION.md), [resultado](evidence/2026-11-07-d056-result.json).
Sin recursosPVE, reglasF5, apps, commits/push. Siguiente: revisiónvisual; noEtapaB.

### D-057 — alcance autorizado

2026-11-07 18:08 CET. Solicitud autoriza monitorización IaC613/621/623/625 y consolidación
Infrastructure/Application/Monitoring/Overall para17CT, STOPPED solo desdePVE.
613DEMO confirmado, verificar appausente antes deN/A.621/ping real JSON7.10;
623Odoo local+PG y625pg_isready mediante checks de lectura y textfileNodeexistente.
Timers locales root usan accesoDocker yaadministrado, sin nuevo usuario/rol/ACL;
pg_isready como usuario postgres existente y escritura métricas como nobody.
Sin cambiar apps/DB/passwords/healthchecks/recursos/F5 ni reinicios/commit/push.
Backup/rollback acotado y validación/idempotencia; no otras etapas. F6INPROGRESS.
Siguiente: comprobar checks, preparar candidatos y desplegar monitorización.

### D-057 — reanudación y cierre técnico 2026-11-09

La petición vigente confirma el mismo alcance de salud de17CT; no amplía a apps,
DB, recursos ni otras fases. Nueva línea base privada, backups y evidencias
separadas del07nov; collectors existentes verificados sin cambios. Desplegados
sonda621 y dashboard consolidado con STOPPED exclusivamente PVE;17filas/ceroUNKNOWN,
18Blackbox/17Node/17cAdvisor y F5 conservados, idempotenciaPASS.
[Informe](PHASE6-D057-COMPLETE-HEALTH.md). DONE técnico del alcance, no aceptación
visual ni cierre globalF6. Propuestas/pendientes de otras vistas/providers/UAT
no se autorizan por este cierre. Ejecución detenida, sin commit/push.

### D-058 — simplificación visual autorizada

2026-11-09. Petición explícita autoriza quitar Environment y el panel Componentes
Docker del Fleet desplegado y de IaC. Solo presentación en611, sin otras fases,
reinicios ni commits/push.

### D-058 — cierre técnico

Environment y panel Componentes Docker retirados del generador y dashboard
provisionado611. Solo presentación, backup verificado, API e idempotenciaPASS;
cero recargas/reinicios, otras siete vistas y datasources conservados. Sin commit/
push. F6 global IN PROGRESS, pendiente revisión visual del propietario.

### D-059 — revisión documental autorizada

2026-11-09 (Europe/Madrid). El propietario solicita contrastar y actualizar la
documentación al estado real. Alcance: lecturas de APIs/archivos, consolidación
del roadmap/estado/fichas y manual Fleet, conservación del historial/evidencias.
Sin despliegues, reinicios, recursos, cambios de aplicaciones, commits ni push.
Tarea documental transversal F7-09, con actualización de F1–F6 según evidencias.

### D-059 — cierre de revisión documental

2026-11-09 (Europe/Madrid). Roadmap/estado consolidados, fichas F1–F7 y manualFleet
alineados con evidencias D041–D058 y lectura actual de APIs. Historial íntegro
conservado en archivos separados; no se reescriben pruebas originales ni se
extiende dispensa UAT. F6/F7 IN PROGRESS; jobGrafana y demás pendientes explícitos.
[Informe](DOCUMENTATION-D059-REVIEW.md),
[evidencia](evidence/2026-11-09-d059-documentation-audit.json).
Solo documentación y consultas, sin producción/commits/push. Propuestas futuras
siguen sin autorizar; siguiente paso revisión visual y alcance F6 específico.

### D-060 — implementación final y cierre F6 autorizados

2026-11-09 (Europe/Madrid). Solicitud autoriza completar Fleet y LXC Details,
navegación bidireccional, provisioning IaC, comprobación visual/consultas/
idempotencia/persistencia y cierre F6 si cumple los once criterios nuevos.
Cambios productivos limitados a provisioning Grafana y sondas necesarias/seguras;
sin recursosLXC, apps/DB/secretos/reglas/Telegram, commits/push. Aplicaciones y
pendientes F7 quedan separados. Se permite continuar tareas independientes ante
bloqueo funcional. No exige nueva UAT de negocio ni perfección cosmética para cerrar.

### D-060 — cierre Fase 6 DONE

2026-11-10 (Europe/Madrid). Implementación/navegador09nov y revisión/ensayoaislado
final10nov acreditan los once criterios autorizados. Fleet y LXC Details enlazados,
17CT, uptimePVE real, salud coherente, nueve dashboards IaC y siete modelos/carpetas
anteriores conservados. Providers únicos y mounts efectivos en recetaCompose;
mismaimagen fijada, sin recreación deGrafana activo. Idempotencia0escrituras/recargas/
reinicios. Producción17Node/17cAdvisor/18BlackboxUP, sin FIRING/PENDING; F5intacta.
[Informe](PHASE6-D060-CLOSURE.md), [resultado](evidence/2026-11-10-d060-result.json).
DONE por criteriosD060; no se afirma UAT ni aceptaciónvisual humana no registrada.
La dispensaF3 no se amplía. Límites de señales y documentaciónlocal explícitos.
F7 y complementosF4/aplicaciones pendientes, propuestas no autorizadas por cierre.
Ejecución detenida; sin commits/push, apps/DB/recursos/secretos/F5/Telegram alterados.

### D-061 — F7.1 y F7.4 autorizados

2026-11-10 (Europe/Madrid). Petición autoriza auditar, seleccionar, validar,
crear commits coherentes y push normal SSH de infraestructura/monitorización F4–F6,
documentación y nuevo flujo IaC. Conservar cambios funcionales EVA/Gestoría/Journal
fuera del commit, salvo artefactos de monitorización inequívocos. No force/historial.
F7.4 prepara alta reutilizable sobre Terraform/inventario actuales, Notes, ficha,
exporters/targets/alertas y Grafana, con fixture/mocks y plan revisable. Sin crear CT,
apply productivo, cambios de recursos/apps/DNS/credenciales ni reservas IP.
7.2 Security Hardening y7.3 Disaster Recovery OUT OF SCOPE por decisión, no DONE.
Numeración del propietario7.4 no es la tarea histórica F7-04(secretos). Fase7 global
no se declara desplegada:7.4 solo READY FOR FIRST REAL PROVISIONING TEST tras pruebas.
