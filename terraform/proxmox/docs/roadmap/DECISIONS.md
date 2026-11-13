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

### D-061 — cierre y publicación del alcance solicitado

2026-11-10 (Europe/Madrid).7.1 DONE: cinco commits curados publicados porSSHnormal,
main/origin0ahead/0behind en4bd0fec; cierre documental adicional. Índice vacío y
cambios funcionalesEVA/Gestoría/Journal intactos fuera delcommit.0credenciales nuevas
según escaneo y revisión; único falso positivo SHA256 cotejado con fuente.
7.4 READY FOR FIRST REAL PROVISIONING TEST: flujo reutiliza módulo/inventario,
Notes/ficha conPENDINGVERIFICATION, exporters nativos/cAdvisoropcional y targets/
reglas/variables preparados; dos planes mock1create/0update/0destroy efectivos.
7.2/7.3 OUT OF SCOPE por decisión, noDONE; numeración distinta deF7-04histórica.
No nuevosCT, applyreal, reservasIP, DNS, recursos, apps ni credenciales modificados.
Compatibilidad nodocker solo preparada/versionada, no aplicada al despliegueF5/F6.
[Informe](PHASE7-D061-EXECUTION.md), [publicación](evidence/2026-11-10-d061-git-published.json).
Ejecución detenida. Próximo: permiso específico del primerCTreal ysu integración,
no concedido por este cierre. No force, reescritura, borrado de ramas/tags/backups.

### D-062 — bootstrap SSH futuro autorizado, solo implementación local

2026-11-10 (Europe/Madrid). Solicitud permite inyectar clave pública durante alta,
bootstrap inicial porpctexec si necesario, openssh-server y SSHsolo por clave tras
probar acceso. No tocar17CTexistentes, crearCT, cambiarpasswords/SSHlocal del dueño,
modificar producción ni commit/push. Fuente pública ~/.ssh/id_ed25519.pub; nunca
leer/copiar/imprimir privada. Prioridadprovider: initialization.user_account.keys
verificado en esquema bpg/proxmox0.94.0; revisar efecto enclone y conservar claves
existentes con fase porconsola. Pruebas offline/nativas/mock sin afirmar acceso real.
7.4 sigue pendiente de primer alta autorizada; 7.2 global continúa OUT OF SCOPE.


D062 — resultado de implementación local: provider admite claves, pero su inyección
en clone sustituye el bloque PVE heredado. Se implementa fusión aditiva por pct exec
como ruta estándar; inyección opt-in exige conjunto completo revisado. No es permiso
para modificar plantillas ni claves de los17. Acceso por clave antes y después de
endurecer, SSH estricto con host keys obtenidas por consola confiable y rollback.
Provisioner de creación mantiene plan dirigido1CT; fallo puede taintar ese CT:
recuperación y revisión de estado obligatorias antes de reintentar, sin destroy.
[Informe](PHASE7-D062-SSH.md). Implementación/pruebas locales DONE; primer ensayo
real pendiente de autorización, no dispensa ni prueba realizada. No commit/push.
Propuesto y pendiente: seleccionar CT/plantilla/red para ese ensayo; no aprobado.

### D-063 — primer provisioning Voicebox autorizado y detenido

2026-11-10 (Europe/Madrid). 7.4 **BLOCKED** antes de provisioning: CT627 libre,
8,55GiB MemAvailable y4,18GiB swap ocupados; asignar mínimo8GiB deja0,55GiB
de margen. Sin apply ni cambios productivos. Autorizado únicoCT con plan
1create/0change/0destroy, SSHD062, Voicebox e integración aditiva de monitorización;
sin tocar apps existentes/pipeline, exposición pública, commit/push.
[Diagnóstico, revisión del fork y alternativas](PHASE7-D063-VOICEBOX.md).
Siguiente: decidir capacidad (ampliación/otro nodo/liberación aprobada), revalidar
y preparar plan real. No se declara desplegado ni aceptado.

Las alternativas son propuestas, no permisos para modificar recursos existentes.

### D-063 — recursos iniciales de plantilla aprobados

2026-11-10 (Europe/Madrid). El propietario sustituye el mínimo inicial8GiB:
autoriza comenzar con los recursos de la plantilla y valorar aumentos graduales
según consumo real. CT106 comprobado:3vCPU,1080MiB RAM,512MiB swap,50GiB
local-lvm. 7.4 **IN PROGRESS**; bloqueo previo de capacidad levantado para este
presupuesto, sin afirmar viabilidad TTS hasta probarla. Se conserva alcance único
CT627 y plan1create/0change/0destroy, sin cambios en los17CT existentes.
Siguiente: preparar bundle, validar plan real y ejecutar alta autorizada.

### D-063 — cierre técnico del primer provisioning real

2026-11-10 (Europe/Madrid). Alcance627 completado: plantilla1080MiB, aumentos
medidos1536→2048MiB conforme permiso expreso;3CPU/512swap/50GiB. Solo627 creado,
memoria yNotes de627 actualizadas, sinreemplazos. BootstrapDSA recuperado antes de
untaint delCTnuevo. Voicebox CPU/Kokoro español real,12,94s paraWAV6,46s.
600s/21muestrasPASS,18Node/18cAdvisor/19Blackbox, ceroFIRING/PENDING;17configPVE
y56targets previos idénticos. Reaplicaciones sin cambios/recreaciones/recargas.
Backup restaurado aisladamente eimagen exacta archivada/verificada; no restore
completo enotroLXC ni buildlimpio bit-a-bit afirmados. Notes/inventario/contratoAPI
completos, pipeline intacto.7.4DONE técnico delprimeralta;F7globalINPROGRESS.
SinUAT/escucha humana ni nuevoTelegram; sinextenderdispensas.7.2/7.3 OUTOFSCOPE.
Sin commit/push. Propuestas no aprobadas por estecierre: otrospresets/motores,
concurrencia, exposición con autenticación, integraciónpipeline yDRcontinuo.
[Informe](PHASE7-D063-VOICEBOX.md), [resultado](evidence/2026-11-10-d063-result.json).

### D-064 — mejora acotada Voicebox autorizada

2026-11-10 (Europe/Madrid). Autorizado soloCT627: auditar perfiles/modelos, conservar
Kokoro y sus perfiles, generar muestras comparables y evaluar Qwen dentro del límite
máximo4GiB. Ampliaciones3/4GiB solo justificadas por medición/capacidad, con backup,
rollback y reinicios documentados; no crear/reemplazar CT, tocar otrosLXC, reglas
Prometheus, pipeline, exposiciónWAN ni commit/push. No aceptar acento/edad/calidad
sin revisión auditiva del propietario. D063 conserva su cierre técnico previo.
Primero distinguir error deperfil de disponibilidad/modelo y presupuestar tensores
CPU antes de descargas/cargas. [Informe](PHASE7-D064-VOICES-QWEN.md).


### D-064 — resultado de catálogo y ajuste medido a3GiB

Cuatro candidatas generadas sin editar originalD063.18,4%RAMlibre yHostMemoryPressure
PENDING justificaron escalón3072MiB permitido. Solo627memory/Notes, backup/restore
previo, reinicio documentado ypersistencia/audio posteriorPASS. Reaplicación0/0/0,
catálogo0perfiles/0generaciones,180s/7muestras,18/18/19UP ysinOOM. SinotrosCT/reglas/
pipeline/commit/push. Alex aceptado porelpropietario; tres nuevascandidatas descartadas.

### D-065 — diagnóstico previo obligatorio paraQwen optimizado

Elpropietario pide separar descarga/carga/inferencia e investigarFP16/BF16/CPUquant
con uso~60s. Exige presentar diagnóstico/recomendación antes de más cambios
productivos. Por ello no se ejecutan limpieza, descarga/cargaQwen, nuevaimagen ni
aumento4GiB. Localmente: diagnóstico deversión, operadores pequeños (no modelo),
parche yplanBF16 preparados. low_cpu_mem_usage esignorado por4.57.3; pesosFP32 no
descartan una rutaBF16 viable, todavía sin medir carga/inferencia real. Propuesta
primerCustomVoice0.6B ydespuésBase0.6B, secuenciales; techo4GiB no ampliado.
[Informe](PHASE7-D065-QWEN-OPTIMIZATION.md). AceptaciónAlex no implica edad/acento
certificados, aceptaciónQwen ni dispensa extendida. Retirada solo3perfiles nuevos
rechazados pendiente tras revisión, preservando originalD063,Alex ymuestras/backup.

### D-066 — autorización explícita delpiloto CustomVoice0.6B

2026-11-10 (Europe/Madrid). El propietario autoriza ejecutar únicamente elpiloto
QwenCustomVoice0.6B BF16/SDPA deD065, backup antes de cambios, imagenoriginal
conservada, unmodelo residente, máximo4096MiB deRAM627. Frasecorta primero y~60s
solo si estable. MedirRSS/cgroup/swap/OOM/tiempo yconsumo máximo; parada yrollback
automáticos si falla, memoria peligrosa oinestabilidad. ComprobarKokoro/Alex después.
No QwenBase, no otrosLXC/pipeline/reglas generales, no commit/push. No borrar ningún
perfil o muestra: presentarIDs exactos de las3rechazadas para retirada futura.
[Informe](PHASE7-D066-QWEN-PILOT.md).

#### Resultado de D-066 y propuesta pendiente

Piloto autorizado ejecutado, sin ampliación por encima de 4096 MiB. Descarga y
carga BF16/SDPA reales PASS; frase corta detenida por umbral preventivo de cgroup
3,5 GiB, sin OOM y sin WAV Qwen completo; 60 s no ejecutados. Rollback automático
y Kokoro/Alex posteriores PASS; CT627 vuelve a 3072 MiB. Dos intentos previos
fallaron en preflight del supervisor antes de cargar Qwen y se corrigieron con
rollback; no son fallos del modelo. Tres ciclos 3072→4096→3072 solo en CT627.

**Propuesta, no aprobada ni ejecutada:** reducir procesos residentes y estudiar la
memoria de inferencia/codec y páginas de archivo antes de otro piloto. La carga
BF16 está demostrada; un minuto de narración en este hardware sigue sin demostrar.
No promover la candidata, relajar el umbral, reintentar ni borrar perfiles bajo
esta ejecución. [Informe y evidencias](PHASE7-D066-QWEN-PILOT.md).

### D-067 — Qwen con 6 GiB y preparación de identidades — IN PROGRESS

2026-11-10 (Europe/Madrid). Autorizado solo CT627: comprobar capacidad del host,
backup/rollback, plan Terraform exclusivo y ampliación 3072→6144 MiB; 3 CPU,
512 MiB swap y disco 50 GiB conservados. Piloto con candidata BF16/SDPA D066,
corta→30 s→60 s; detener a 5,5 GiB, OOM, swap excesivo, inestabilidad o afección
externa. Un modelo residente; imagen original y todos los datos conservados.
Preparar candidatos masculino/femenino sin aceptación auditiva, clonación personal
pendiente de grabaciones reales, contrato API sin integrar el pipeline. Qwen Base
se evalúa separadamente, sin asumir memoria ni crear voz ficticia del propietario.
No otros LXC, borrados, pipeline, commit ni push. [Informe](PHASE7-D067-QWEN-6G.md).

#### Resultado de D-067 — medición y aceptación separadas

Ensayo6 GiB ejecutado; cargaBF16/SDPA PASS, corta TIMEOUT600s sinWAV,30/60s no
ejecutados. SinOOM ni corte de5,5 GiB; pico4,22 GiB incluida parada. Original
restaurada automáticamente; retornoRAM exigió regenerar/revisar plan por cambios
al manifiesto durante el ensayo. Final3072MiB; no afirmar rollback totalmente
automático ni probar el fallback corregido por una recuperación manual.
Kokoro/Alex/muestra masculina PASS tras recreaciónDocker;7IDs persistentes.
FemeninaSerena solo registro experimental bloqueado, sinmuestra ni aceptación de
acento/edad. Personal no creado; Base0.6B clonación investigada y parche preparado,
no desplegado. Propuesta pendiente: diagnosticar terminación/rendimientoCPU antes
de más pruebas; no ampliarRAM ni promover candidata por este cierre.
Alcance no ejecutado permanece pendiente: audioQwen/30/60s, muestrafemenina y
clonación real con grabaciones. [Informe](PHASE7-D067-QWEN-6G.md).

Cierre D067:180s/7muestrasPASS, sinalertas; aplicaciónNotes solo627description,
segundaTerraform0/0/0, mismoIDDocker, clienteAPIKokoro realPASS. Backupfinal
restaurado fueraPVE39archivos/13audios. Ensayo/recuperación DONE conincidencias;
aceptaciónQwen/femenina BLOCKED ypersonal pendiente, sin nuevaautorización inferida.

### D-068 — 7 GiB, diagnóstico instrumentado y voces — IN PROGRESS

2026-11-10 (Europe/Madrid). Autorizado solo CT627: comprobar capacidad/presión del
host, backup/rollback y plan exclusivo para RAM3072→7168 MiB; CPU3,swap512 ydisco50
sin cambios. Diagnosticar por etapas/progreso el timeout Qwen antes de repetir;
comparar alternativas CPU seguras y validar mínima→15–30s→120–150palabras/~60s,
solo si cada anterior termina. Un modelo TTS residente, umbral6,5GiB, OOM/swap/
presiónhost/inestabilidad/sinprogreso vetan avance. Conservar imagenestable/datos,
Kokoro/Alex y muestras. Preparar candidata femenina real yclonación personal sin
vozficticia, terceros ni aceptación sin grabaciones delpropietario. No pipeline,
otrosLXC, CPU/disco/swap, borrados, commit nipush. [Informe](PHASE7-D068-VOICEBOX.md).

#### Resultado D-068 — implementación y aceptación separadas

Ampliación autorizada3072→7168MiB solo627; CPU3/swap512/disco50 conservados.
Un reinicio delCT, sin recreación. ProbesQwen con progreso real, parados porPSI/swap
conOOM0; no se declara audioQwen validado ni causa completa de600s identificada.
Se conserva7GiB por normalización de presión yobjetivo aprobado, conguard IaC;
retornoRAM para inseguridad persistente. No se ampliaron umbrales niRAM para forzarQwen.

Piper CPU es_ES añadido como motorAPI soportado, perfil femenino real ydosmuestras
masculina/femenina. Base0.6B guardado contra ausencia dereferencias reales; código,
privacidad,backup yprocedimiento preparados, sinmodelo/vozpersonal ni terceros.
DockerCPU3/RAM6200/RAM+swap6600 conserva400MiBswap anterior, dentro de7GiB/512CT.
OriginalD063 retenida; nuevaimagenR2 archivada/verificada yreceta reproducible.
Serialización y409 reales, dobledeploysinreinicio; aceptacionesauditivas pendientes.
Se detectó unoriginalD063 ausente yse restituyó debackup, UUID+metadatos+WAV,
sinrollback totalDB ni pérdida de nuevosdatos; causa no determinada ysinDELETEemitido.
[Informe](PHASE7-D068-VOICEBOX.md).

**Propuesta pendiente, no ejecutada:** otro diagnósticoQwen aislando codec/atribución
presión con presupuesto explícito. No aumentarRAM ni integrarPipeline por estecierre.
La primera clonación requiere grabaciones reales yvalidación; noDONE ni dispensaUAT.

Cierre técnico D068: Notes solo627description, segundaTerraform0/0/0, dobledeploy
sinreinicio,31tests yobservación180s/7PASS. Backup definitivo trasrecuperación:
72archivos/25audios;13originalesidénticos y12nuevoscompletos. OriginalausenteD063
5385d04b recuperado selectivamente sinrollbackDB total; origen abierto yno ocultado.
PiperR2 quedaoperativo, modelosTTSmáximo1 y409comprobado. Qwen sigueBLOCKED por
seguridad, sinRTF/60s; clonaciónpersonal noDONE ysinperfil ficticio. No commits/push.


### D-069 — Voicebox exclusivamente personal — IN PROGRESS

El propietario autoriza conservar únicamente `Eduardo — Mi Voz`, inventariar y
respaldar perfiles/muestras antes de retirar los ocho perfiles de usuario sobrantes.
Catálogos integrados y motores se conservan. Grabación real autorizada: comprobar,
copiar y verificar en almacenamiento privado persistente antes de retirar del árbol
de documentación; nunca Git ni evidencias públicas. Transcripción existente confirmada
exacta por el propietario. Prioridad Base0.6B, piloto controlado con límites D068 y
texto solicitado; no validar semejanza sin escucha humana. Máximo7GiB, CPU3/swap512/
disco50 sin cambios; solo627, backups/rollback y persistencia. No pipeline, commit/push.
Nombre histórico del guard Base no reconoce el perfil real: corregir sin quitar
validación de referencias. Modelos pesados alternativos: presentar antes de añadir.


#### Resultado D-069 — primera clonación técnica, aceptación pendiente

Se conserva únicamente Eduardo — Mi Voz (`1fd00418-2a79-4178-883f-af6c3f5e07ee`).
Ocho perfiles retirados tras inventario presentado y backup restaurado; motores y
catálogos integrados conservados. Grabación real preservada fuera Git y en volumen
privado persistente, transcripción confirmada. Guard corregido por UUID, no eliminado;
fallos previos0.6B por nombre antiguo y1.7B por tamaño rechazado, antes de inferencia.

Base0.6B BF16/SDPA con codecFP32 produce WAV6,40s en106,86s; cgroup observado
5,18GiB, HWM4,68GiB, swap+5,32MiB, OOM0. Texto solicitado y referencia real,
sin nuevas cargas tras éxito. Imagen personal fijada, backup de imagen con29blobs
verificados; rollbackR2 conservado. Reinicio preserva perfil/referencia/WAV y dos
deploy sin recreación/reinicio. Notes solo627description, segundaTerraform0/0/0.
No RAM/CPU/swap/disco, otrosLXC,pipeline,commit ni push.

Clonación NO DONE: pendiente escuchar parecido, contenido pronunciado y acento.
Una muestra6,4s no valida un minuto; no se extrapola rendimiento. Voces adicionales
fuera del objetivo vigente; alternativas pesadas no instaladas ni autorizadas por
este cierre. [Informe D069](PHASE7-D069-PERSONAL.md).


D069 — aceptación humana posterior: el propietario escuchó la muestra925f8b71 y
respondió «Sí, acepto la muestra» a la comprobación de parecido, acento y lectura
íntegra. Perfil personal y primera clonación **DONE — Accepted**. Se sustituye la
aceptación pendiente anterior únicamente para esta muestra; no para narración60s.
El catálogo persistente yrecibo deaceptación se conservan además en backup privado
suplementario, porque esta decisión llegó después del snapshot completo.


### D-070 — cancelar generación larga y comparar alternativas CPU — IN PROGRESS

El propietario autoriza diagnosticar y cancelar exclusivamente la generación activa
de Eduardo — Mi Voz, sin reiniciar CT627 ni perder perfiles/grabaciones. No repetir
pruebas largas Qwen. Conservar Kokoro/Piper y verificar CPU/RAM/swap/Voicebox después.
Investigar clonación española CPU dentro de7GiB y presentar comparación antes de
desplegar otro motor. No otrosLXC,pipeline,commit ni push. La aceptación D069 de
la muestra corta no acredita narración larga; esta queda bloqueada según resultado.

D070 — autorización adicional expresa: ante cancelaciónAPI que deja el hilo nativo
consumiendoCPU, el propietario autoriza reiniciar únicamente el contenedorDocker
Voicebox conservando imagen/perfiles/grabaciones/volúmenes. CT627 no se reinicia.
No extender a nuevos motores ni otras generacionesQwen.


#### Resultado D070 — recuperación y comparación DONE, narración larga BLOCKED

Trabajo d7ce3d31 cancelado porAPI, pero asyncio.cancel no paraba el hilo inferente;
CPU1,97núcleos ysinOOM. Con autorización adicional se reinició soloDockerVoicebox
el10nov21:52:36UTC, mismoID eimagen, sinreiniciarCT. Verificado11nov: perfil y
referencias/originales idénticos,healthy,cero trabajos activos,CPUenreposo,swapestable
en ventana observada. Kokoro2,58s/8,09s yPiper2,11s/2,16s en helperssinred; sin
perfiles nuevos ni otrosLXC. SnapshotSQLite+referencias restaurado fueraPVE; D069
completo conservado. No nuevoQwen largo, motor, pipeline,commit ni push.

Propuesta pendiente: piloto aislado OpenVoiceV2+MeloES conworker cancelable ytecho
inicial3GiB, sin subirCT de7GiB; después evaluarXTTS si fidelidad insuficiente.
Pesos verificados por metadata, RAM/tiempoCPU alternativos no medidos. No se
considera esta comparación autorización de descarga/despliegue.
[Informe yfuentes](PHASE7-D070-CPU-ALTERNATIVES.md).


### D-071 — implementación OpenVoice V2 + MeloES autorizada — IN PROGRESS

11nov2026,Europe/Madrid. SoloCT627,3CPU/7GiB/512MiBswap/50GiB sin ampliación.
Autorizados revisión de código/licencias, implementaciónIaC y despliegue candidato,
backup/rollback y pruebas progresivas de voz real del perfil existente. Máximo una
inferencia, cola limitada, cancelación efectiva y timeout con liberación de recursos.
Evaluar worker3GiB; QwenCPU no se utiliza. Integración mínimaVoicebox/UI ycontratoAPI,
texto original separado de adaptación trader→tréider. No cambiar arquitectura del
fork sustancialmente sin presentar plan, no pipeline,otrosLXC,commit nipush.
Aceptación técnica exige minuto real ycancelación; fidelidad reservada al dueño.
Si el candidato falla, rollback ypropuesta justificada, sin forzar recursos.


### D-072 — Qwen C/BLAS aislado autorizado — IN PROGRESS

11nov2026, Europe/Madrid. El propietario rechaza la voz OpenVoice D071
(«no esa no es mi voz») y prioriza Qwen Base0.6B. Autoriza investigar y probar
el repositorio gabriele-mastrapasqua/qwen3-tts, INT8 primero, referencia personal
real e invariable; comparación INT4/BF16 solo viable y útil. Pruebas corta→15→30→60s
solo tras WAV correcto previo, una generación, límites de tiempo/cancelación real,
monitorización y comprobación de capacidad del host. CT627 permanece3vCPU/7GiB/
512MiBswap. No CustomVoice para identidad, otrosLXC, pipeline, ampliación, commit
ni push. No sustituir producción ni integrar definitivamente antes de aceptación
auditiva. La prohibición histórica de QwenCPU se levanta solo para este piloto
aislado. OpenVoice deja de ser la solución principal.

D071: muestra369ebd31 rechazada; candidata restaurada a imagenD069, worker parado.
Cancelación nativa probada0,423s, pero ensayo de minuto detenido por presiónPSI
del host, sin WAV. No aceptación técnica de minuto ni aceptación de voz. Backups,
perfiles, referencias y muestras conservados.


#### Resultado D072 — piloto concluido por seguridad, sin WAV

Base0.6B C/BLASAVX2 INT8 cargado5,738s, ICL referencia real24,883s. Corte123s
porPSIfullhost sostenida (pico9,10%), no OOM ni umbralRAM:RSS3,697GiB,
worker3,712GiB,CT5,094GiB. SinWAV: no comparaciónINT4/BF16 ni15/30/60s.
Dockerpiloto parado3,406s/PID0; producciónD069healthy sin reinicios, perfiles y
referencias/originales verificados. Kokoro/Piper generan después,59targetsUP.
DiscoCT6277,1GiB libres,HostDiskFillingpending; no borrar ni limpiar sin alcance
autorizado. ConfiguracionesPVE intactas, sin otrosLXC/pipeline/recursos/commit/push.

Diagnóstico/piloto acotado DONE; objetivoQwen/narración BLOCKED sinaceptación.
Propuesta no aprobada como producción: optimizar y atribuirPSI/espacio antes de
otra carga, workerAPI cancelable si futuroWAV aceptado. No descartar porRAM ni
promover por documentación. [Informe y evidencias](PHASE7-D072-QWEN-C.md).


### D-073 — auditoría de capacidad de solo lectura autorizada — IN PROGRESS

11nov2026, Europe/Madrid. Auditar memoria física/disponible/caché/swap/PSI/OOM
del host, consumo porLXC yfueraLXC, almacenamientoCT627 y candidatos de limpieza
con tamaños reales ydependencias de restauración. La intención inicial de recuperar
disco queda concretada por la prohibición explícita posterior: **no eliminar nada,
no limpieza automática ni cambios productivos**. No nuevas inferenciasQwen, otros
LXC,pipeline,recursos,commit/push. Verificar producción/perfil/grabaciones y motores
existentes sin modificarla. Crear PHASE7-D073-CAPACITY-AUDIT.md y detenerse para
revisión; toda retirada/archivo/limpieza queda propuesta y pendiente de autorización.


#### Resultado D073 — auditoría DONE; cambios no autorizados

SinQwen ni limpieza. Host15,504GiB físicos,9,070disponibles; CT6273,556GiBcurrent
incluye2,615GiBfilecache y0,539anon. Durante60s sininferencia: presiónhost5,67%
con≥8,832GiB disponibles, stall1,189s/cAdvisor6181,190s yCT6270,000029s;
cAdvisor618 límite128MiB,+4918max,0OOM nuevos. Identificadafuenteactual independiente
deQwen; no atribución retrospectiva concluyenteD072. No modificarCT618 porD073.

Disco7,056GiBlibres; A4,748GiB temporales/cache, B7,198GiB backups expandidos
con tarhomónimo, condicionados a verificación/restore/retención. No son permiso
de eliminación:0bytes borrados, sin archivar ni cambiar producción. K/Preadiness
yWAVsD072verificados, no nueva inferencia; perfil/originales intactos.59UP,warning
disco627FIRING;27configsPVE intactas, otros17CTgestionados sin cambios.

Propuestas separadas no aprobadas: remediar límitecAdvisor618 y limpiezaacotadaA/B,
optimizar memoriaQwen con palancasexperimentales solo en eventualpiloto autorizado;
no ampliarRAM ni compraGPU sin evidencia. Detenido para revisión.
[Informe y evidenciasD073](PHASE7-D073-CAPACITY-AUDIT.md).


### D-074 — preparación de mantenimiento controlado — IN PROGRESS

11nov2026, Europe/Madrid. El propietario quiere continuar Qwen y retirar lo
innecesario de CT627, pero limita esta intervención a auditoría/preparación y exige
aprobar la lista exacta antes de cualquier eliminación material. Verificar duplicados
y copias externas, preservar voz/datos/modelos funcionales/rollback/volúmenes; nada
de limpieza globalDocker. El apartadoCT618 autoriza inspeccionar cAdvisor y proponer
límite porIaC, sin tocar recursos ni Budibase/CRM/API/otros contenedores. No se usa
su presión como bloqueo automático del objetivoQwen, pero tampoco se omite la
comprobación específica pedida. La parada final exige no ejecutar eliminación ni
cambio de memoria; nuevas inferencias no se ejecutan en esta preparación. Validar
Voicebox/Kokoro/Piper,perfil/originales,18LXC,OOM/alertas; sin commit/push.


#### Resultado D074 — preparación DONE, ejecución BLOCKED a aprobación expresa

Lista exacta105entradas/11,946GiB;44cacheIDs Sharedfalse/InUsefalse,47rutas
APT/buildpúblico,14expansionesbackup. Manifiesto SHA256
`d2396813e51c98e171052f0bc8765c69476467db53b098d89727954474fc8b00`.
14parejas idénticasarchivo/permisos/symlink,14manifiestosválidos/SQLiteok y14copias
externasSHAidéntico. Conservar ambas copiascomprimidas. Selectorcacheallowlist
probado solo lectura, sinprune. Imágenes/contenedores/modelos/livevoice/audio/
referencias/originales/volúmenes/rollback excluidos. 0eliminaciones/0cambiosmemoria.

cAdvisor618healthy,reinicios0,OOMnuevo0,2880scrapes24hUP; +63eventosmax/10s.
PropuestaIaC opcional local256MiBRAM/384MiBRAM+swap/CPU0,50; no aprobada ni aplicada.
No requisito aQwen ni autorización de modificarBudibase/CRM/API o realizar rollout.
Voicebox/perfil/originales preservados,K/PreadinessPASS,18LXC/59targetsUP,0alertas
niOOMnuevos; aviso627discoFIRINGprevio. No reinicios,recursos,pipeline,commit/push.

El propietario quiere continuar pruebasQwen; se conserva ese objetivo tras resolver
la aprobación concreta de mantenimiento. No nueva inferencia durante preparación.
Detenido antes de eliminación/memoria para revisar lista; aprobación de limpieza
no se extendería aCT618 ni aotrosrecursos.
[Informe](PHASE7-D074-CONTROLLED-MAINTENANCE.md) y[lista](PHASE7-D074-CLEANUP-LIST.md).


### D-074 ejecución aprobada + segunda opinión Qwen Fase A — IN PROGRESS

11nov2026,Europe/Madrid. El propietario autoriza eliminar únicamente105elementos
del manifiesto SHA256d2396813e51c98e171052f0bc8765c69476467db53b098d89727954474fc8b00,
tras revalidación, con espacioantes/después ypreservaciónVoicebox/Eduardo/originales,
Prometheus/Grafana yalertas. ProhibidoCT618/cAdvisor/otrosLXC. Aprobación no incluye
ningunaimagen/modelo/volumen/backupcomprimido ni recurso fueraallowlist.

Autoriza además FaseA de diagnóstico hardware/PyTorch/C/memoria/referencia y
microbenchmarkFP32/BF16 sin cargarQwen. La frase final «ejecutar generación Qwen
todavía» se interpreta según el encabezado «Solo diagnóstico» y parada antesFaseB
como no ejecutar generación todavía. No cambio de recursos/servicios, no alterar
ni recortar original. Tabla dehipótesis/evidencias yprueba mínima propuesta, sin
FaseB,commit/push. Se registra como D075-FaseA para seguimiento, sin ampliar alcance.


#### Resultado D074 ejecutado / D075 Fase A — DONE; Fase B no iniciada

Limpieza105/105 autorizados:61rutas+44cacheIDs; libre7,056→18,997GiB,+11,941GiB.
No eliminaciones deimágenes/modelos/contenedores/backupscomprimidos/livevoice/volúmenes,
niotrosIDs. 14tars externos SHA revalidados. Preflight paró antes de borrar por dos
auxiliaresSQLite deauditoríaD074 (WAL0/SHM32KiB; soloextras derivados; DB/tars intactos);
verificador corregido immutable. GuardAPT distinguió helperdeapagado inactivo ylocks
libres; filtrosbooleanospresencia seleccionaban0cache, se terminó conallowlist44
exacta yprevalidaciónShared/InUse/Size. No limpieza global ni ampliación de alcance.

FaseA: microbenchmark PyTorch2.8+CPU real sinQwen, hilos2/interop1 solo enproceso
diagnóstico225MiBRSS: BF16matrices10,48–146,33×/conv44,19× máslento. i5-6500AVX2
sinBF16nativo; generaciónoficial hereda8192tokens, no overrideVoicebox; EOSpendiente.
CINT8ambosTalker/CP por código/capsD072; mismoSHAupstream actual; D072312frames
yúltimo50no runawaydemostrado. DecoderconcurrenteWAValfinal; referencia24,883s/
425caracteres/formato/condicionamientoaudio+texto correctos, originalnoalterado.

SwapCT413MiB traslecturabackups, cache3,192GiB/anon0,225/kernel0,365; noOOM ni
swapoff/cacheclean/restart. 59UP/GrafanaPromPASS,0alertas/erroresproductivos nuevos,
Voiceboximagen/ID/inicio/Eduardo/grabaciones preservados;27configsPVE intactas.
NoCT618/cAdvisor/otrosLXC/recursos/pipeline/commit/push. ObjetivoQwen sigue vigente,
pero esta FaseA termina antes deFaseB como pide propietario; no carga/generaciónQwen.
Prueba mínima futura propuesta, no ejecutada. [Informe](PHASE7-D075-QWEN-HYPOTHESES-PHASE-A.md).


### D075 Fase B — una inferencia oficial Base0.6B FP32 autorizada — IN PROGRESS

Propietario autoriza una única prueba CPU/FP32/SDPA si compatible, texto «Hola, soy
Eduardo.», referencia real/transcripción exacta, hilos basados enFaseA. Preflight
memoria/swap/PSI/servicio/disco/exporters; presión significativa o swap activa creciente
impide cargar. Modelo/proceso aislado cancelable, timeoutmáximo300s, tokenslimitados
explícitos ycausaEOS/límite/timeout/error instrumentada; sin asumir token=frame.
CT6273CPU/7GiB/512MiBswap sin cambios; no reinicio para liberar swap, no Voicebox
productivo/otrosLXC/modelos/perfiles/grabaciones/pipeline/commit/push. No30/60s ni
segunda prueba; informe ydetenerse. Seguridad de capacidad prevalece sobre cargar.


#### Resultado D075B — F por preparación, único intento concluido sin carga

Preflight60sPASS:hostmín9,345GiB,CTPSI0/swapestable412MiB;59UP/0jobs/disco19GiB.
Un worker oficialCPUFP32/SDPA configurado64pasosnuevosTalker,2hilos/interop1,
max300s, límitesguardados/RO/offline. Falló importación librosa/Numba por caché sin
localizador: rootFSRO yNUMBA_CACHE_DIR no redirigido altmpfs. Error de preparación
delpiloto reconocido, no QwenFP32 inviable. 0cargas depesos/generaciones/tokens/WAV;
8,205sworker/14,326ssupervisor,RSSHWM483MiB,CTpico4,410GiB,swapnuevagua0,0OOM.

ExitCode1/PID0/Runningfalse, sin hilosresiduales ni reinicio. Voicebox/Eduardo/
referencia/originales/modelos conservados,27configsPVEintactas,otrosLXC/CT618sin
cambios;59UP/GrafanaPromPASS/0alertas, sin recursos/pipeline/commit/push.
No segunda prueba porlímite solicitado. Correccióncache delworker propuesta, no
ejecutada; validarFP32 sigueBLOCKED, intentoacotadoDONEF. Detenido para revisión;
no usar esta autorización ya consumida para repetir.
[Informe](PHASE7-D075-QWEN-FP32-PHASE-B.md).


### D075B — repetición02 FP32 ycorrecciónNumba autorizadas — IN PROGRESS

Propietario autoriza una única repetición, exclusivamente NUMBA_CACHE_DIR=/tmp/numba
enworkeraislado, conmkdir/escritura/espacio/importsNumba+librosa+backend comprobados
antes decargar. Fallo de cualquierpreflight detiene sincarga. MantenerBase0.6B CPU
FP32/SDPA, j2/interop1, texto «Hola, soy Eduardo.», referenciaexacta, cap64 ytimeout
≤300s/guardas; no cambiar límitesCT6277GiB niVoicebox/CT618/otrosLXC/pipeline.
No borrar datos/modelos ni30/60s, no segundo reintentoautomático/commit/push.
Medir yclasificar etapa/progreso/tiempos/EOS/cap/recursos, proporcionarWAVsi existe,
actualizarinforme ydetenerse alfinal. Autorización anterior no se reutiliza.


#### Resultado repetición02 y autorización de umbrales graduales

02: cachéNumba/tmpfs/importsPASS, cargaFP32 completada9,052s; referencia iniciada,
sin tokens/WAV. CorteE por crecimiento swapCT observado32,445MiB frenteaguarda16,
0OOM/PID0. Datos completos en evidenciaD075-b02; cierre documental interrumpido
por nueva instrucción, se retoma antes de otraspruebas.

Propietario confirma expresamente pruebas cortas ajustando solo umbrales de parada
(swap,PSI,margenmemoria), manteniendo CT6273CPU/7GiB/512MiBswap, Voicebox yotros
LXC sin cambios. No límites de recursos ni servicios productivos, ni pipeline,
commit/push. Nuevoalcance sustituye parada de una prueba solo para estos ensayos
graduales. Primer escalón: swapcrecimiento16→32MiB, techo absoluto480MiB para
reservar32MiB; resto guardas idénticas. Si no queda margen previo oaparece OOM/
inestabilidad, no iniciar/avanzar. Un trabajo simultáneo, máximo300s, texto corto
original, Base0.6BFP32/SDPA,64pasos,j2/interop1,misma referencia. Máximo tres nuevos
ensayos enesta intervención; no ejecutar más si basta el primero o si lo impide la
seguridad. No30/60s. Cada escalón se documenta por separado, sin elevar límites
para ocultar un fallo ni promover producción sin voz aceptada.


Escalón03 completadoE: corteCTPSI≥1%/5s; acumuló solo0,245s destall en una
ráfaga decarga yprácticamente0enlos5s siguientes, aunqueavg10 persistía1,36%.
Swap+18,98MiB bajo32, sinOOM/PID0. Se permite escalón04 conPSICT2%/5s y
PSIhost3%/10s, memoriaigual; techoabsolutoswap496MiB, reserva16MiB ycancelación
inmediata solo delcgroupworker al cortar, sinCTswapoff/recursos/producción.
Justificación: diferencias cortasmedidas, no presión continua; techofijo496 no se
aumentará más enesta intervención. Preflight exige swap<480MiB sincrecimiento.
Si se agota ese margen o apareceOOM/inestabilidad se detiene, sin forzar máspruebas.


04: EOSreal14tokensTalker/13frames acústicos,8,950sTalker,decoderiniciado; Eal
superarworker5,75GiB (pico5,841;anon4,269/file1,557GiB), CT6,451<6,6,0OOM.
Último escalón05 cambia solo umbralworker5,75→5,85GiB, sin cambiarhardlimit6GiB,
CT6,6/RSS5,6/PSICT2%/host3%/swap32MiB y496absoluto. Mantener≥153MiB hastalímite
duro delworker; no suponer filecache instantáneamentelibre. Si superaeste margen
o preflight no pasa, parar sin elevarotra vez. No nuevosensayos tras05enestecierre.


05:EporPSIhost3%/10s; CTPSI2,1% transitorio2s ydesciende0,77%, sinpresiónlocal
sostenida niOOM. Tokensnoalcanzados en05;04síEOS. Revisión justificada delmáximo
autoimpuesto3: laautorización deldueño cubre umbralesgraduales/pruebascortas, nofija
tres. Se amplía solo aunescalón06, PSIhost3→5%/10s; todasguardaslocales yrecursos
idénticos05, capswap496/reserva16 ypreflight<480 no se elevan. No insistir si
preflightfalla ni elevarmemoria/localPSI tras06. Se registra antes deejecutar; no
cambia elalcancefuncional yse informaalpropietario.


### D076 — nuevos recursos y narración55–60s autorizados — IN PROGRESS

El propietario informa ampliaciónRAMfísica; autoriza CT6273CPU/10240MiBRAM/2048MiB
swap yworkeraislado umbral8,2GiB/hard9GiB,swapcrecimiento128MiB/PSICT5%10s,
OMP/MKL/TORCH_NUM_THREADS3. ObjetivoWAVcompleto55–60s trading conEduardo, Base0.6B
FP32/SDPA aislado, sin reemplazarVoicebox/otrosLXC/pipeline,commit/push. Sustituye
los máximos anteriores7GiB/512MiB yprohibición deensayo largo solo en este alcance.
Laobservación06previa no lanzóworker06; se cancela eseescalón corto por nuevoalcance.

Verificaciónhost:MemTotal33533042688B(~31,23GiB),disponible~21,9GiB; PSIglobalalto
se registra, no se equipara a agotamiento físico sin atribución. CT627sigue7168/512.
ProveedorBPG0.94 marca memorycomo rebootRequired; aplicar recursos en caliente
mediante scriptversionado exclusivo627, conservarconfigprevia yreconciliarstateTF
conrefresh-only. Planprevio revisado solo627memory/description; no applymutante que
reinicie. CPU/disco conservados. Timeout previo300s: se pide autorización de900s
para ellargo; hastarespuesta no exceder300. No reiniciarCT niVoicebox.

### D076 — resultado del único ensayo y cierre condicionado

Recursos10GiB/2GiB aplicados en caliente solo627,CPU3 conservada, Voicebox sin
reinicio y datos privados intactos. Ensayo FP32/SDPA3hilos detenido por deadline300s
con368 llamadas forward ysin WAV; no alcanzó decoder. Pico worker6,50GiB,CT7,78GiB,
RSSHWM5,59GiB,swap0/PSICT0/OOMnuevo0. No se considera fallo por memoria ni bloqueo
demostrado. Timeout900s propuesto, no aprobado todavía: no repetir automáticamente.
Prometheus9090 inaccesible antes del piloto;36exporters directos responden, Grafana
DB sana ydatasource falla. No modificar otrosLXC para repararlo. Fase7.4 IN PROGRESS,
WAV BLOCKED por límite temporal pendiente de nueva autorización. InformeD076 enlazado
en roadmap; sin commit/push.

### D076 — autorización explícita de un nuevo ensayo hasta900s

El propietario responde «Sí, máximo15minutos» a la ampliación temporal. Se autoriza
un único intento02, conservando01 y sus evidencias, mismos recursos/guardas/texto/
referencia/FP32/SDPA/3hilos. Registrar preflight actualizado antes de cargar pesos.
No nuevos reintentos automáticos ni cambios productivos. Estado IN PROGRESS.

### D076 — intento02 finalizado E; optimización del decoder solo propuesta

La autorización máxima de900s se consumió en un único intento02, terminado a701,542s
por RESOURCE_MEMORY_GUARD delCT (9,533GiB>9,5GiB), no por timeout ni OOM. Talker
emitió EOS:813tokens/634,226s,812×16códigos; decoder inició pero no escribióWAV.
Worker cgroup5,984GiB/RSS6,406GiB,CTanon5,906/file3,298GiB,swap0/PSIlocal0/OOM0.
Cancelación cgroup.kill completa,PID0; Voicebox y originales intactos, configsPVE
sin cambios. No repetición. El objetivo deaudio55–60s sigue BLOCKED.

Código real ya usa chunked_decode300/context25; pública decode no expone chunk_size.
Propuesta pendiente, no ejecutada: checkpoint privado de códigos yrecorte, liberar
Talker antes delcodec ybloques120/context25. Sin ampliar recursos ni guardas.
Kokoro/Piper descargados sin nueva síntesis;36endpoints responden (uno alreintentar
lectura); Prometheus inaccesible desde antes, sin modificarlo. No otrosLXC/CT618/
pipeline ni commit/push. Fase7.4 INPROGRESS, detenerse para revisión.

### D077 — preparación autorizada de Talker y decoder separados

11nov2026, Europe/Madrid. Propietario autoriza implementación, inspección de posibles
checkpoints D076 y validación estática/imports/datos sintéticos, sin cargar Qwen ni
generar audio. Dos procesos exclusivos, checkpoint privado persistente y atómico,
checksum y metadatos de referencia/recorte/versiones. Primero preparar decoder300
con separación de procesos; soporte120 experimental, no activar simultáneamente.
Mantener CT6273CPU/10GiB/2GiBswap, workerhard9GiB, guardaCT9,5GiB y FP32/Base0.6B.
No Voicebox productivo/otrosLXC/CT618/pipeline/borrados ni commit/push. Generación
real posterior pendiente de autorización. Fase7.4/D077 IN PROGRESS.

### D077 — preparación terminada; generación real pendiente

Dos procesos implementados en pilot-d077: A intercepta antes de decodificar,
persiste códigos completos y metadatos en NPY/JSON privados con commit atómico;
B carga únicamente271 entradas decoder.*, sin Talker/encoder. Guardas y recursos
conservados. Default300/context25;120 solo experimental, sin cambio automático.

17 tests locales PASS; imports/versiones/cabeceras/layout meta y cargador con un
peso ficticio PASS sin pesos Qwen; checkpoint sintético recuperado desde contenedor
nuevo; cancelación padre+hijo con cgroup.kill, PID0/cgroup vacío y retirada del
worker propio PASS. Primer import falló por symlinks HF aislados; montaje individual
config/safetensors corregido y validado. Preparación idempotente y jobnarracion01
listo; no checkpoint real recuperable D076, no carga de pesos ni WAV D077.

Producción intacta: Voicebox misma imagen/ID/inicio/health, originales ytranscripción
conservados;27 configsPVE sin cambios,0OOM nuevos, Kokoro/Piper descargados.
CT627 sigue3CPU/10GiB/2GiBswap; no otrosLXC/CT618/pipeline ni commit/push.
D077 preparación DONE; Fase7.4 INPROGRESS. Propuesta pendiente: ensayo A→B300 con
presupuesto900s y guardas actuales; no afirmar memoria/calidad acústica sin medir.
No ejecutarlo hasta autorización específica. Informe PHASE7-D077-CHECKPOINT-DECODER.

### D077 — ensayo único autorizado con texto nuevo e integración productiva solicitada

El propietario autoriza un único A→B300/context25, misma referencia Eduardo/Base0.6B
FP32, checkpoint persistente y guardas actuales, sin reintentos ni repetir Talker
si falla B. Nuevo texto literal de bienvenida/análisis trading sustituye únicamente
el texto de generación en un job nuevo; no sobrescribir narracion01 previo.
También solicita modificar Voicebox para dejar este flujo listo en producción.
Registrar ampliación antes de ejecutarla: integración productiva autorizada solo
CT627/Voicebox, con backup/rollback y validación técnica; preservar perfil/datos,
Kokoro/Piper y límites3CPU/10GiB/2GiB. No otrosLXC/CT618/pipeline/commit/push.
Primero probar motor aislado; si no produce WAV válido, detener despliegue dependiente.
Aceptación auditiva del WAV sigue pendiente de escucha, no presumirla. IN PROGRESS.

### D077 — integración productiva: supervisor externo dedicado a CT627

Ensayo único A→B300 PASS técnico: EOS y checkpoint válido; WAV10,8s/24kHz/PCM16,
183,04s total. UAT voz/texto pendiente de escucha. Para conservar las guardas físicas
del host, la integración autorizada Voicebox requiere un agente systemd ligero en
PVE, limitado en código a CT627: cola de archivos privada, sin puertos nuevos,
sin Docker socket en Voicebox. El agente lanza supervisores A yB secuenciales con
las guardas D077 existentes; cambiosPVE exclusivamente control de Voicebox/627,
sin recursos ni intervención enotrosLXC. Registrar antes del despliegue.
Adaptador Voicebox sin modelos residentes, conserva UI/API/historial/perfil;
checkpoint ysalida privados, cancelación real, sin retry ni división automática
del texto. Backup verificable, imagenoriginal yrollback antes de reemplazarapp.

### D077 — resultado, aceptación y despliegue productivo

Ensayo único bienvenida01 PASS: texto literal216caracteres; EOS136tokens/95,547s,
checkpoint447×16, A finaliza antes B300/context25; WAV10,8s, total183,041s. Propietario
confirma «Sí, voz y texto correctos». No120 ni Talker adicional. WAV publicado en
historial Eduardo, URLaudio225c8772-6b09-52b0-9580-c0001fff4bcb, SHAidéntico.

Voicebox productivo7c747589… conadaptador sin modelos, cola privada y agentePVE
exclusivo627; guardas y recursos sin ampliar. Backup68archivos/restoreSQLitePASS,
copia externa yambas imágenes conservadas. Primera sustitución pese asmokefallido
porpermisos600/root se revirtió aimagenoriginal;COPYchown999 ygateruntimeUID999
antes demutaciones corregidos. WAVimportado nuevo también pasó propietario999;
no permisos deoriginales alterados. Finalhealthy,23tests runtimePASS, idempotente
sin recreación y180s/7muestrasPASS;0OOM/swap/errores nuevos enventana final.

Perfil/samples idénticos porhash de filas; historias3→4 solo porimportar elWAV
aceptado, sinsegunda inferencia paraAPI. Pipeline/otrosLXC/CT618 intactos.
D077 ejecución yproducción DONE técnico; Fase7.4 INPROGRESS. Calidad10,8s aceptada;
55–60s yprimer recorrido real de nueva generación porUI/API aún sin repetir.
Prometheus previo inaccesible no se intervino. Sin commit/push. InformeD077-PRODUCTION.

### D078 — diagnóstico autorizado del primer fallo Qwen desde Voicebox

Propietario limita el alcance a diagnóstico remoto de lectura y preparación local.
Localizar job cuyo texto comienza por «El mercado cambia cada sesión…pre-market.»,
verificar checkpoint real/EOS/tokens y métricas de memoria, y contrastar con D077.
No inferencias, cambios de producción/recursos/guardas, borrados, otrosLXC ni pipeline.
No commit/push. No reanudar ni repetir ningún trabajo; informe D078 y detenerse.
Fase7.4 INPROGRESS; éxito aislado D077 no acredita recorrido UI/API real.

### D078 — causa demostrada y corrección mínima propuesta, sin ejecutar

12nov2026 Europe/Madrid. Prioridad aprobada: pico durante preparación de referencia,
antes de investigar duración. Jobs86dde73b…/73a3755f… fallan26–27s de supervisión,
sinreference_ready, generación ni checkpoint. Baselinefile D0773,311GiB→4,69–4,85;
anon inicial≈0,35. CTalparar9,70–9,78,workerRSSmuestreado4,52–4,64;0swap/OOM,
pero193+58high/reclaim. CódigoML igual, texto aún no usado; no es limitación de573
caracteres. Observación delarchivadoD077 muestra subidafile4,319→4,846, baseline
que reaparece enfallos. mincore actual:containerd1,409GiB, cinco blobs concretos
1,051GiB candidatos a consejo DONTNEED. No se envió ningún consejo ni se purgó.

Propuesta pendiente: reclamación selectiva y medición antes del siguiente ensayo
continuo60s, conrecursos/guardas iguales, sin segmentar. Promptcache yloaderselectivo
son mejoras posteriores separadas. No afirmar cuál fue elúltimobuffer encoder/spk
sin nueva instrumentación. Cuantificación perfile esactual, nohistórica.

Ningún jobtieneCP; B imposible. UIretry bloquea elpath existente ysobrescribe error
original, mensajecheckpoint falso. Política local6testsPASS propone attempts nuevos
explícitos oBsoloconCPverificado, nunca autorepetirA ni borrar originales. Diagnóstico
DONE, corrección/inferencia no autorizadas. Fase7.4 INPROGRESS/narraciónBLOCKED.
Informe PHASE7-D078-QWEN-DIAGNOSIS; no producción/otrosLXC/pipeline/commit/push.

### D079 — corrección mínima y un único ensayo UI/API autorizados

12nov2026, Europe/Madrid. Propietario acepta D078 y autoriza POSIX_FADV_DONTNEED
solo sobre los cinco blobs del manifiesto, sin operaciones incompatibles; medir
antes/después sin prometer recuperar1,05GiB. Autoriza desplegar preflight predictivo
y corregir mensaje de checkpoint inexistente, conservando ambos intentos fallidos.
Después de comprobaciones y margen suficiente, un único ensayo desde Voicebox con
texto original573caracteres, Base0.6B/FP32/Eduardo/es/300-context25, A→checkpoint→B,
presupuesto900s y guardas actuales. Si falla preflight o guarda: detener, sinretry.
No recursos/otrosLXC/pipeline/borrados/commit/push. No caché reutilizable de referencia
ni otro cambio estructural simultáneo. Fase7.4/D079 IN PROGRESS.

### D079 — cierre técnico 12nov2026

Corrección desplegada; reclamados1,051445GiB de file reales. Preflight rechaza
inicial4,533GiB: proyección9,533>9,5GiB. Parada antes de cargar Qwen, cero
inferencias nuevas. No ampliar autorización ni relajar reserva. Recursos intactos.
Resultado y siguiente propuesta separados en [D079](PHASE7-D079-QWEN-CONTINUOUS.md).

### D080 — recursos y ensayo continuo autorizados, IN PROGRESS

12nov2026 Europe/Madrid. Propietario autoriza exclusivamente CT62715360MiB RAM,
3CPU/2048MiBswap/disco50 sin cambios, guarda CT14GiB, workerhard9GiB y resto
de parámetros intactos. Preflight físico, plan Terraform exclusivo627, backup y
rollback, validación. Última instrucción autoriza continuar con un ensayo continuo
del texto completo573caracteres, un WAV, A→checkpoint→B300/context25, sin R/A/B.
Presupuesto900s y ausencia de retries automáticos conservados. No otrosLXC,
pipeline, borrados ni commit/push. Procedimiento existente: resize en caliente
versionado para evitar reboot del proveedor, reconciliación Terraform dirigida.

### D080 — resultado y cierre de intervención

12nov2026 Europe/Madrid. CT627 ampliado a15360MiB en caliente mediante receta
versionada, tras plan exclusivo627 memory/description revisado; refresh-only
reconciliado yplan final0cambios. CPU3/swap2048/disco50 intactos, sinrebootCT/app.
GuardaCT14GiB, workerhard9GiB/stop8,2 ycontroles de swap/PSI/cancelación conservados.
Un único POST573caracteres completó A→checkpoint→B: EOS358, códigos669×16,
WAV28,56s,total362,182s. PicoCT8,612GiB, swap4KiB, OOM0; CPcopiado fueraCT y
recuperado sinmodelo. No se afirman60s ni aceptación acústica. Otros17configPVE
idénticos; Voiceboxhealthy, agenteactivo, workersfinalizados, datos protegidos
intactos. Prometheus sigueinaccesible previamente; no intervenciónajena.
Fase7.4 INPROGRESS: recursos ycaso573caracteres DONE técnicos, duración60s/UAT
pendientes. Siguiente propuesto: escuchar ydespués ensayo contexto60s separado,
sinretries automáticos ni cambios silenciosos. SinR/A/B,commit,push,borrados.
[Informe D080](PHASE7-D080-QWEN-15G.md).

### D081 — consolidación y ensayo único autorizados, IN PROGRESS

12nov2026 Europe/Madrid. Propietario acepta D080 como referencia técnica funcional.
Autoriza consolidar fuentes locales/IaC/docs/Notes/runbook, backups verificados
y UI deVoicebox sin cambiar runtime ni reiniciar innecesariamente. Después de
preflight, un único ensayo con texto literal adjunto, Base0.6B FP32/Eduardo/es/42,
A→checkpoint→B300/context25, continuo, límite900s yguardasD080. Si excede1200
caracteres: detener sin truncar. CT15GiB/3CPU/2GiBswap, guardaCT14GiB, worker9GiB
yparada8,2 conservados. NoR/A/B, otrasLXC, Prometheus/Grafana/pipeline, borrados,
commit ni push. No declarar calidad aceptada antes deescucha. Detener tras elensayo.

### D081 — cierre de consolidación yensayo único

12nov2026 Europe/Madrid. RuntimeD080 preservado, sinrestarts nirecreaciones.
Backup externo103archivos/SQLite ydosimágenesOCI39blobs verificados; fuentes
locales archivadas, deploy.sh reconoceD079 ydosreconciliaciones sinrecreación.
UnclickUI1059caracteres exactos, jobbaa61a95…: EOS718,checkpoint1029×16,
WAV57,36s,total676,180s, picoCT9,625GiB,swapmáx4KiB/PSI0/OOM0. No silencio
ni cambio develocidad para forzar50–55. ASRlocal señala4variantespequeñas; voz
ylectura literal pendientes deescucha. CPcopiado yrecuperado externamente.
91archivosprotegidos,perfiles ymuestras intactos; no workersresiduales, apphealthy.
PeticiónDELETEseparada delfallido73a3755f… antes delPOSTnuevo,autor noestablecido;
carpeta/filarespaldada conservadas, no reinsertar automáticamente. Otros17config
PVEidénticos; no Prometheus/Grafana/pipeline, R/A/B, recursos/modelos,commit/push.
Fase7.4 INPROGRESS, consolidación yensayo DONE técnicos, UATpendiente. Detenido.
[Informe D081](PHASE7-D081-QWEN-CONSOLIDATION.md).

### D082 — aceptación definitiva y publicación autorizadas

12 de noviembre de2026, Europe/Madrid. El propietario escuchó y aceptó voz y
contenido del WAV D08157,36s: D081 ACCEPTED / PRODUCTION. Autoriza cierre
formal, comprobación real sin inferencias/restarts, Notes627 ydocs finales,
commits curados ypush normal aGitHub. Misma configuración D081, sin optimizaciones
ni R/A/B. No datos privados/modelos/audios/backups/estados/secretos enGit.
Preservar cambios ajenos; detener publicación si rama/remoto o diff no son seguros.
Alcance aceptado≈unminuto, no5–10min; pronunciación hola pendiente, trader→tréider
comprobado; texto fonéticoTTS separado del original destinado a subtítulos.
Fase7.4 cierre IN PROGRESS hasta validaciones ypublicación; otrasfases intactas.

### D082 — cierre aceptado ypublicación confirmada

12nov2026 Europe/Madrid. D081 ACCEPTED / PRODUCTION por voz ycontenido escuchados.
Fase7.4 DONE / ACCEPTED:≈1min, no5–10min. Runtime yrecursos conservados; noaudio
nuevo, no reinicios. 68testsPASS,backup final117archivos/6WAV/1referencia ySQLite
aceptado restaurados fueraPVE; dosimágenesOCI y39blobs verificados. Datos privados
fueraGit. Notes627 sincronizadas; Terraformdirigido final0cambios.

Commits b55a7f99480017fffcbeff4a3106115d65ee10ea y4dab6d505f4c7628cf8ebaecfdb44177bbbf3e5d
publicados enorigin/main mediantepushnormal ySHA remoto comprobado. Recibo final
solo documental; SHA exacto enentregafinal. Post-push: mismoVoiceboxhealthy/ID/inicio,
agenteactivo,checkpoints/perfil/originales intactos,otros17configsin cambios,OOM0.
No cambios ajenos publicados; noforcepush ni reescritura. Pronunciaciónhola pendiente,
trader→tréider comprobado ysubtítulos originales separados deltexto fonéticoTTS.
F7global y7.2/7.3 fueraalcance permanecen; no funcionalidades nuevas tras elcierre.
[Informe final D082](PHASE7-D082-VOICEBOX-FINAL-ACCEPTANCE.md).

### D083 Voicebox — preparación bilingüe y evaluación Chatterbox autorizadas

Nueva intervención Fase7.4, distinta deD083 de recuperación de monitorización
registrada arriba. No renumerar ni alterar esa intervención ajena. El propietario
autoriza diagnóstico, implementación candidata local ytests sininferencias para
es/en enQwen0.6B; investigar Chatterbox antes deinstalar/descargar modelos. Mantener
D081 ACCEPTED / PRODUCTION, referencia/transcripción,semilla42,FP32,A/B,guardas
yrecursos intactos. No despliegue, inferencias, nuevasdependencias productivas,
servicios,otrosLXC,pipeline,commit/push. Chatterbox requiere diagnóstico deCPU,
RAM/disco/licencias/versiones yplan antes deactivación. Candidatos yensayos
preparados se distinguen delruntime productivo. Detenerse alpresentar informe.

### D083 Voicebox — pausa Chatterbox y auditoría de almacenamiento

El propietario pausa descargas/instalación/despliegue de Chatterbox. Prioridad:
auditoría de solo lectura delstorage mostrado comoStorage(pve), rootfs627 y
alternativas de volumen gestionado100GiB frente amigrarrootfs. No crear/mover/borrar,
no reiniciar, cambiar recursos/guardas, inferencias, commit/push ni otrosLXC.
Conservar candidatoQwenbilingüe ytests locales. Esta ampliación documental F7.4
se distingue deD083monitorización ajeno; producciónD081 aceptada permanece intacta.
Entrega propuesta antes de cualquier cambio dealmacenamiento.

### D083 Voicebox — prioridad SSD: auditoría rootfs50→100GiB

El propietario sustituye la preferencia de mp0/HDD por ampliar rootfs627 enSSD
local-lvm de50 a100GiB. Solo auditoría: thinpool/datos/metadatos/sobreasignación,
hotresize yprocedimientoIaC compatibleD080, validación yrollback. No pctresize,
volúmenesHDD, movimientos, descargas, reinicios, inferencias,commit/push ni otrosLXC.
Conservar todos los avances/candidato bilingüe yproducciónD081. La auditoríaHDD
queda como antecedente, no se ejecuta ninguna de sus propuestas.

### D083 Voicebox — resultado auditoría SSD, sin ejecución

Poolpve/data400,086GiB,275,051usados y125,035libres; metadatos2,794%,VGfree0,
autoextendthreshold100 desactivado. Thinvirtual808GiB→858trasresize100. Con50GiB
nuevos escritos quedarían75,035GiB; con627todoasignado100≈73,70. Snapshots yotros
LXC comparten margen; no prometer reserva absoluta. Crecimientoext4online soportado
porAPIinstalada; no ejecutado. Políticaactual50 eignore_changes[disk] requieren
actualización coordinada futura yverificaciónLV+FS, recetaD080 yrefresh-only.
Planes privadossinapply:100rechazado porpolítica; permitiendo100diskignoradocero
cambios; quitandoignore soloensimulación update627 sinrecreación. No modificar
ignore global de17CT. Rollbacknoesshrink: backupcompleto/restauraciónaislada si
seexige50. SSD100 es opciónpreferida parausoprevisto conreservaoperativa propuesta.

CandidatoD083 ytests preservados; app/recursos/configsPVE intactos, rootfsreal50.
Fase7.4productivaDONE/ACCEPTED permanece; ampliación NOAUTORIZADA aún. No inferencias,
descargas,limpieza,HDD,volúmenes,reinicios,commit/push. [Auditoría](PHASE7-D083-CT627-SSD-CAPACITY-AUDIT.md).

### D084 — ampliación SSD CT627 autorizada

Fase 7.4, 12nov2026 Europe/Madrid. Autorizados preflight, backup completo verificable
en HDD storage, resize online absoluto rootfs62750→100GiB local-lvm, actualización
IaC/Notes y reconciliación refresh-only dirigida627. Reserva operativa pool20%;
no capacidad física exclusiva. Backup obligatorio antes de resize. Sin reinicios,
inferencias, descargas, otros LXC, cambios Qwen, commit/push. D081 y candidatoD083
protegidos. Estado IN PROGRESS; detener ante condición de seguridad fallida.

### D084 — resultado: DONE técnico

CT627 rootfs50→100GiB local-lvm yext4 verificadosonline, mismoUUID/PID/app;
backupHDDcompleto17,651GiB íntegro, extracción completa aislada,SQLite/modelos/
111archivos ypermisosPASS. BackupD082/imagen externa revalidados. Disponibles
65,494GiB; poollibre124,605GiB/31,14%, reserva20%respetada. Notes/IaCactualizados,
ignore_changes conservado; refresh-onlytarget627 aplicado, serial278→279,
planfinaldirigido0cambios yotrosestadosTerraformidénticos. Configsotros17servicios
y26CTajenosidénticas. Perfil/referencia/6WAV/historial/checkpoints intactos;
OOM0 ysin erroreskernel nuevos. D081 ACCEPTED / PRODUCTION sin cambioML;
candidatoD08316archivos intacto. No inferencias,descargas,Chatterbox,reinicios,
commit/push. Restauraciónporarchivos comprobada, no ensayoDRdearranque.
No shrink; backup50 ycontroladorPVE separados conservados. VGfree0 yPSIheredado
continúan; reserva20%noesunaalerta desplegada. Detenida alcompletarD084; próximo
trabajoinglés/Chatterbox separado. [Informe](PHASE7-D084-CT627-SSD-RESIZE.md).

### D085 — preparación bilingüe y Chatterbox autorizada

Fase 7.4, 12nov2026 Europe/Madrid. Recuperar candidato D083 porhash, completar
código y pruebas sin audio, preparar dependencias/entorno aislado Chatterbox
Multilingual oficial fijado tras preflights. Se autorizan descargas selectivas
con hashes ypresupuesto vigilado, conservando20%delthinpool libre. Sin cambio
de recursos/guardas, referencia/transcripción, D081 niotrosLXC. No despliegue
productivo, inferencia real, commit/push. Estado IN PROGRESS. Entregar informe
D085 y detener antes de despliegue yensayos A/B/C.

### D085 — ampliación autorizada: cuatro efectos de salida

El propietario confirma referenciaoriginal mediante procesamiento propioChatterbox,
perfil/checkpointsQwen intactos, límite240 exclusivoCB/Qwen1200 ydependencias
porversiones/hashes sinmaster. Autoriza preparar Robotic,Radio,EchoChamber y
DeepVoice reutilizando presets/DSP existentes, solo candidato ypruebas sintéticas.
Se conserva punto deparada: sinproducción, inferencia real, commit/push.

### D085 — preparación completada; despliegue y ensayos pendientes

Fase7.4: implementación/pruebas/entorno aislado DONE, producción nueva TODO.
16hashesD083 intactos; política Qwen1200 yChatterbox240 independiente. Referencia
original RO yprocesamiento acústicoCB propio, sincheckpointQwen; perfil intacto.
113paquetes instalados conlock/hashes,Perthcommitff1c8ac… sinmaster;5archivosV3
verificados3208844550bytes. UI/imagen candidata19af4754… construidas sin despliegue;
11Python+5UI nuevos y10Python+4UI heredadosPASS,14API/8efectos/4DSP sintéticosPASS.
Efectos4 nativos porgeneración; no defaultperfil alterado. Backupdatos117archivos
restaurado externamente yD084completo revalidadoSHA. Entorno4,796GiB;rootlibre
60,025GiB,pool124,155GiB/31,03%,20%respetado. ImportsRSS601MiB medido, carga/inferencia
CB no medida; propuesta hard8/stop7 y300s basada encomponentesFP32, sin cambiarQwen.
ProducciónD081 mismoID/inicio/imagen/fuentes,111archivos+DB/WAV intactos;27configs
PVE idénticas/OOM0;max367 soloen hijosauxiliares,localCTmax0. Sininferenciasreales,
deploy, recursos/guardas originales modificados, otrosLXC,pipeline,commit/push.
Detenida para revisión del[InformeD085](PHASE7-D085-QWEN-BILINGUAL-CHATTERBOX.md).
Siguienteautorizable: desplieguecoordinado,validaciónsinvoz y AEnglishQwen→BSpanishCB
→CEnglishCB secuenciales,sinefectos alcompararidentidad. No ejecutar ahora.

### D086 — despliegue y tres ensayos autorizados

Fase7.4. Autoriza desplegar D085 coordinadamente enCT627 conbackupnuevo yrollback
app/controller/worker; recursos/guardas intactos. Solo A QwenEnglish→B CBSpanish
→C CBEnglish, secuenciales, textos exactos, sin efectos ni normalización adicional.
Fallo detiene secuencia, sin reintentos; fallo crítico de despliegue exige rollback.
Solicitud adicional deefectos se probará en copias separadas delWAV obtenido, sin
otra inferencia ni alterar las muestras de comparación/referencia. SinotrosLXC,
pipeline,commit/push. Aceptaciónacústica pendiente. IN PROGRESS.

### D086 — fallo crítico de startup; rollback completado

Candidato19af4754… cambió USER a999 pero heredóentrypoint congosu; erroroperation
notpermitted antesAPI. FixturesD085 omitíanentrypoint real. Se abortótransacción
conSIGINTcontrolado ysuBaseExceptionejecutórollbackcoordinado. D08109774c5b…
healthy, procesoservidorUID999,agente/src/controlador originales,CBdeshabilitado;
CTsinreinicio. NuevoDockerID esperado, reconciliación posterior no-op.
A/B/C yefectos noejecutados;0POSTgenerate/0inferencias,ningúncheckpointnuevo.
Backup118archivos restaurado externamente yD081/82/84/85revalidados. Datos6WAV/
1perfil/1referencia/111archivos y27configsPVE idénticos. OOM0,eventosmemoriaigual,
swap0/PSIlocal0;pool31,03%libre. SinotrosLXC/pipeline/recursos/guardas/commit/push.
EstadoD086 BLOCKED/ROLLED BACK; recuperaciónDONE técnica;D081 ACCEPTED vigente.
Propuesta NOaplicada: USERroot soloalarranque heredado,gosu aUID999,smokeaislado
conentrypoint real ydespuésnuevo tag/revisión. Nuevaautorización antesdereintentar.
[Informe](PHASE7-D086-QWEN-CHATTERBOX-VALIDATION.md).

### D086 — corrección de arranque sin privilegios autorizada

Confirmar rollback D081 healthy; corregir solo entrypoint candidato manteniendo
USER999, sinroot ni capacidades añadidas. InspeccionarDockerfile/Compose/mounts
ypermisos reales; probarentrypoint yCMD reales en aislamiento, más accesoUID999
a módulos/config/DB/directorios. No despliegue productivo ni inferencia A/B/C.
Pruebas dearranque usan copias privadas equivalentes a losbinds para conservar
SQLite/perfiles/WAV originales; auditoría deacceso real sin escrituras separada.
SinotrosLXC,recursos,guardas,commit/push. IN PROGRESS.

### D086 — resultado corrección sinprivilegios: DONE técnico aislado

Se descarta propuesta previa deUSERroot segúninstrucción expresa delpropietario.
Imagen21270364… mantieneUSER999:999 yentrypointdirectexec sin gosu/chown/usermod
ni fallbackroot. Cacheparent imagenowned999 medianteCOPYbuild, sin tocarvolúmenes;
CMDUvicorn original explícito porqueENTRYPOINTreiniciaCMDheredado enDocker.
Fullstartup realenaislamiento healthy, mismosENV/límites/mounts internos/modos,
fuentesbindprivadas conowners/modes ySQLitebackup coherentes; auditoría realbind
UID999sin escrituras. PID1UID/GID999,CapEff/Prm0,DBlectura/escritura rollbackPASS,
modelo no cargado. TestparadoPID0, producción mismoID/inicio/imagenhealthy yagent.
30testsPython/UI y14API+8efectos/4DSP sintéticosPASS;111archivos/DB/WAV y27configs
PVE idénticos, permisosreales intactos, sinOOMnuevo. SinA/B/C,inferencias,deployment
productivo, recursos/guardas/otrosLXC,pipeline,commit/push. Intervencióndetenida
para revisión antes de continuar. [Informe](PHASE7-D086-UID999-STARTUP-FIX.md).

### D087 — despliegue corregido y tres ensayos autorizados

Fase 7.4, 12 de noviembre de 2026 (Europe/Madrid), IN PROGRESS. El propietario
autoriza exclusivamente la imagen 21270364… manteniendo USER999:999, entrypoint
corregido, CMD Uvicorn y cero privilegios adicionales. Preflight, backup actualizado
y rollback coordinado obligatorios; ante fallo crítico de despliegue, restaurar D081.
Solo A Qwen English → B Chatterbox Spanish → C Chatterbox English, una ejecución
por ensayo, textos exactos, sin efectos ni reintentos; detenerse al primer fallo.
Recursos/guardas intactos; no otros LXC, pipeline, narraciones largas, commit/push.
Calidad acústica pendiente del propietario aun si los tres WAV resultan válidos.

### D087 — resultado: BLOCKED en preflight, producción intacta

La imagen21270364… UID999 se verificó; receta/locks actualizados solo localmente.
CT7,745GiB + presupuestoCB7GiB + reserva0,5GiB =15,245GiB > guarda14GiB.
Política realD085 rechaza admisión; no se descuenta file6,893GiB como ya liberado.
QwenPASS, pero no se inicia secuencia parcial. Host dispone20,6GiB; swapglobal
activo, PSIlocal0/swapCTestable/OOM0. D081healthy/mismoID/inicio, DB/WAV y27configs
PVE intactos;30tests PASS. No despliegue, backupnuevo ni A/B/C; rollback innecesario.
Backups existentes conservados, revalidación completa pendiente antes de desplegar.
No recursos/guardas/otrosLXC/pipeline/commit/push. Detenido según condición del
propietario. Siguiente: diagnosticar file/swap, resolver margen y repetir preflight;
no ejecutar limpieza/reclamación ni inferencias automáticamente.
[InformeD087](PHASE7-D087-QWEN-CHATTERBOX-PRODUCTION-VALIDATION.md).

### D087 — reanudación autorizada: CT627 con20GiB y guarda19GiB

El propietario autoriza ampliar exclusivamente CT627 a20480MiB mediante el
procedimiento IaC existente y elevar la guarda agregada a19GiB. Conservar CPU3,
swap2048MiB, disco100GiB y workers Qwen hard9GiB/stop8,2GiB y Chatterbox
hard8GiB/stop7GiB. Autoriza reanudar despliegue coordinado imagen21270364… y
A→B→C secuenciales sin efectos ni reintentos, condicionado a preflight/backup.
No otros LXC, pipeline, narraciones largas, commit/push. IN PROGRESS.

### D087 —20GiB aplicados; despliegue fallido y rollbackPASS

RAM20480MiB/guarda19GiB DONE mediante IaC+PVEhotchange yrefresh-onlytarget627;
planfinal0cambios/restoestadoidéntico. CPU3/swap2GiB/disco100GiB yworkerstope sin
cambios. BackupsD081/82/84/85 revalidados; nuevo117archivos restaurado fueraPVE.
Presupuesto físico usa techooperativo19GiB yreserva6GiB; primerchequeo20GiB/6GiB
se detuvo sin cambios. Posterior despliegue coordinado falló al copiar__pycache__
creado porpreflight. Rollback automáticoPASS, D081 mismoID/iniciohealthy, agente
activo, CBdeshabilitado; conserva20GiB/19GiB aprobados.0inferenciasA/B/C; parada
alprimerfallo, sinreintentos. Datos/perfil/referencia/WAV/checkpoints intactos,
26configsajenasidénticas/OOM0. Receta copy_locked corregida solo localmente;37tests
PASS, nodéploy de corrección. Próximo intento necesita revisión/autorización y
backup/nombre nuevos, sin borrar el fallido. SinotrosLXC/pipeline/commit/push.
[InformeD087](PHASE7-D087-QWEN-CHATTERBOX-PRODUCTION-VALIDATION.md).

### D087b — corrección y continuación autorizadas

El propietario indica «solucionalo y continua» después del rollbackD087. Autoriza
corregir la receta, preparar nuevo intento sin sobrescribir respaldos y continuar
el despliegue y A→B→C condicionado a validaciones. Mantener imagen21270364…,
UID999,20GiB/guarda19GiB, resto de recursos/guardas/parámetros y referencias.
Sin efectos, narraciones largas, reintentos de inferencia, otrosLXC, commit/push.
IN PROGRESS; preservar evidenciasD087 y detener secuencia al primer fallo real.

### D087b — despliegueDONE; inglésaceptado; paradaB y Chatterboxdeshabilitado

13nov2026 Europe/Madrid. Imagen21270364… USER999/entrypointrealhealthy. Nuevo
backup117archivos restaurado ychecksumD081/82/84/85PASS; sin borrar elintentoD087.
Readiness corregido a7archivoscontroller/7worker conguardas19/RAM20;39testsPASS.
Cancelaciónhold sintética ysharedslotPASS,0pesos/0audio. AEnglishcompleted33tokens
EOS/checkpoint344×16;2,56sWAV,124,38sagente. Propietario confirmó «Sí, voz y texto
correctos»: aceptado soloesteensayoinglés; noingléslargo niotrasvoces/motores.
BSpanishCB fallóenguarda7GiB, pico7,6957GiBcgroup/RSS6,516GiB/CT12,04GiB,OOM0;
subetapaexactanoinstrumentada. SinWAV; Cnoejecutado ysinreintentos. Se deshabilitó
releaseCB sinreinicioapp, preservandoQwenbilingüe ytodoslosdatos/evidencias.
Efectos4disponibles enUI/API, noprocesadosconvozreal. Recursos/guardas intactos;
Notes/TFrefresh-only627/planfinal0 yotrosestados/configsajenasintactos.105archivos,
7audiosoriginales ycheckpointsPASS; historial6previos+Acompleted+Bfailed.
Sinresiduales/otrosLXC/pipeline/commit/push. Detenidoalprimerfallodeinferencia.
Propuesta pendiente: eventosdurablesporfase y optimizarcopias/mapeosdelcargador
CB; no másRAMCT niajustesdeguardas automáticos.
[InformeD087](PHASE7-D087-QWEN-CHATTERBOX-PRODUCTION-VALIDATION.md).

### D088 Voicebox — diagnóstico y dos cargas comparativas autorizadas

Fase7.4,13nov2026 Europe/Madrid. Esta D088 es independiente de la recuperación
cAdvisor/CRM D088 anterior. Preservar Qwen es/en aceptado, producción y susdatos.
Preparar candidato e instrumentación persistente de memoria porfase paraChatterbox.
El propietario autoriza expresamente dos cargas reales: original y candidata,
secuenciales, sinreferencia personal niTTS, hard8GiB/stop7GiB/CT19GiB/300s cadauna.
Sin más intentos automáticos. MantenerFP32/modelo/paquetes/hashes originales, CPU3,
RAM20GiB,swap2GiB,disco100GiB; CBsigue deshabilitado. No deploy, inferencia, otrosLXC,
Terraformglobal,pipeline,borrados,commit/push. IN PROGRESS.

## D-088 Voicebox y autorización condicional D-089

13nov2026 Europe/Madrid. Dos cargas autorizadas consumidas; candidata FP32 carga
en38,88s, RSS máximo4,557GiB frente a6,556GiB original. Reducción por assign=True
verificada sin cambiar pesos. Producción Qwen es/en intacta y Chatterbox deshabilitado.
D089 BLOCKED: no hay mediciones de activaciones/generación/decoder que acrediten
margen. No despliegue ni audio. Propuesta pendiente de autorización: ensayo aislado
instrumentado bajo guardas originales. Informe: [D088](PHASE7-D088-CHATTERBOX-MEMORY-OPTIMIZATION.md). Sin commit/push.

## D-089 sustituida — validación aislada y despliegue condicional autorizados

13nov2026 Europe/Madrid, Fase7.4 IN PROGRESS. La última instrucción sustituye
íntegramente D089 anterior. Autoriza resolver/reproducir suite completa estable
y candidata en entorno fijado con soundfile; exigir PASS antes de una única
inferencia aislada española, referencia original RO, sin efectos ni reintentos.
Solo con WAV íntegro, sin guardas/OOM/swap y margen medido autoriza backup y
despliegue mínimo exactamente probado; después una prueba UI es y, si pasa, en.
CT20GiB/3CPU/2GiBswap/100GiB; CB FP32 stop7/hard8/CT19/300s/240 caracteres.
Ante fallo detenerse; si desplegado deshabilitar CB y rollback si afecta Qwen/app.
Qwen aceptado, datos, otrosLXC y pipeline intactos; sin commit/push.

### D089 — ejecución condicional y parada

13nov2026 Europe/Madrid. Suite73/73, UI9/9; inferencia aislada FP32es aprobó
criterios medidos y permitió despliegue mínimo con backup D089141archivos
restaurado/verificado, D084/D085/D087 revalidados. App/Qwen sin cambios. Una
generación Voiceboxes completa:139tokens/EOS, WAV5,48s, pico kernel3,187GiB,
margen3,813GiB; sin OOM/swap. Observador local falló por No route to host;
STOP aplicado, inglés no ejecutado, ninguna inferencia repetida. Observación
recuperada desde PVE, Chatterbox deshabilitado sin reinicios. Qwen es/en sigue
operativo; generación ajena activa conservada. Overlay instalado pero no habilitado;
rollback preparado sin restaurar SQLite. Cierre BLOCKED, calidad acústica pendiente.
Siguiente propuesto, no ejecutado: revisión de conectividad y reanudación autorizada
para inglés después de valorar español. Sin recursos/otrosLXC/pipeline/commit/push.
[Informe](PHASE7-D089-CHATTERBOX-PRODUCTION-VALIDATION.md).

### D089 — reanudación autorizada tras conectividad

13nov2026 Europe/Madrid, Fase7.4. El propietario confirma que inició Qwen inglés
728caracteres. No cancelar ni reiniciar app/agente mientras activo; comprobar
estado terminal y WAV o conservar fallo. Autoriza diagnóstico/corrección del
observador, reutilizar WAVes sin inferencia adicional, verificar API/checksum
desde ruta comprobada o PVE. Tras salud/sin trabajos activos, reactivar CB y una
única generación inglesa exacta, sin efectos/reintentos, stop7/hard8/CT19GiB/300s.
Si falla o no verificable API: STOP/CBdeshabilitado/Qwen operativo. Si pasa, dejar
CBes/en disponible, aceptación acústica pendiente. Sin recursos/otrosLXC/pipeline
ni commit/push. Trabajo Qwen ya comprobado terminal completed antes de cambios.

### D089 — reanudación completada, disponibilidad autorizada

13nov2026 Europe/Madrid. Propietario Qwen: completed45,04s/EOS, checkpoint875×16
íntegro, descarga API verificada; ninguna interrupción. Español existente
revalidado directo/PVE mismo SHA, cero inferencias nuevas. Observer GET-only
fallback/estados separados, 4regresiones y suite77/77 PASS. Error histórico
EHOSTUNREACH demostrado, causa precisa de red no recuperable con evidencia actual.
Receipt reactivado y una sola inferencia inglesa:127tokens/EOS, WAV5,00s,
API=worker SHA, pico kernel2,518GiB, margen4,482GiB; sin OOM/swap/guardas.
Chatterbox disponible es/en conforme autorización. Voicebox/Qwen healthy, cero
trabajos activos/residuales, misma imagen/ID/StartedAt, cero reinicios/recursos.
Implementación/despliegue/validación DONE técnico; aceptación acústica TODO.
No elevar a aceptación final por WAV válido. Sin otrosLXC/pipeline/commit/push.
[Informe D089](PHASE7-D089-CHATTERBOX-PRODUCTION-VALIDATION.md).

### D089 — aceptación acústica y publicación autorizadas

13nov2026 Europe/Madrid. El propietario confirma escucha y aceptación de
Chatterbox español5,48s e inglés5,00s y Qwen inglés45,04s. Cerrar solo alcance
validado Voicebox F7.4; no extender a CB1200caracteres, efectos acústicos ni
narraciones no probadas. Autoriza auditoría solo lectura de límites/efectos y
commit/push normal del código, IaC y documentación Voicebox pendientes, con
selección explícita de rutas/hunks y exclusión de datos privados/estados/backups.
Sin inferencias, DSP, despliegues, reinicios o cambios de límites/recursos.
Rama actualmain, upstreamorigin/main, remotoeduardo152030/mailerblend-platform-infra;
fetch confirmado0/0 antes de preparar. Cambios de otros servicios/monitorización
se conservan fuera del índice.

### D089 — publicación funcional verificada

13nov2026 Europe/Madrid. Commit `402501e0279389e607c44950be9b3423e4d5bb4c` enmain verificado
enorigin/main conpushnormal,197archivos Voicebox/CT627. Índice exacto validado
y escaneado sin secretos ni fragmentos de transcripción; efectosdisponibles/default
none yCB240/Qwen1200confirmados enproducción sinaudio. Voicebox/Qwen/CBhealthy
post-push, misma app/configPVE/datos protegidos. Se publica recibo documental
posterior; SHAfinal se verifica ycomunica, sinforce. Cambiosajenos conservados
fuera delcommit. F7.4Voicebox ACCEPTED, otrosalcances no se cierran.

### Voicebox — entrada Chatterbox1200 autorizada, solo código

13nov2026 Europe/Madrid, Fase7.4. Propietario autoriza entrada1200caracteres
coherente UI/API/controlador/worker, selector/capabilities/mensajes, expectativas
de tests y hashes/manifiestos. Conservar400tokens/EOS/20sWAV/300s/guardas, Qwen,
efectos, evidenciasD089 y digests publicados. Autoriza commit/pushnormalmain
solo de este cambio. Prohíbe ejecutar pruebas/inferencias, desplegar o reiniciar.
Generación completa de1200caracteres no validada; producción aceptada240 intacta.
Preparación IN PROGRESS; registro previo a implementación.

### Voicebox — entrada1200 implementada localmente

UI/API/controlador/worker ycapabilities/mensajes/selector actualizados en código.
Política reutilizada; contratos de salida/tiempo/memoria, Qwen y efectos intactos.
Hashes objetivo recalculados; baselines y evidenciasD089/digests preservados.
Tests solo actualizados, NO ejecutados; sin inferencia/build/despliegue/reinicio.
Generación completa1200no validada; producción permanece240hasta otra intervención.
Implementación local DONE; publicación autorizada aorigin/main; validación y
despliegue TODO. [Detalle](VOICEBOX-CHATTERBOX-INPUT-1200.md).

### Voicebox — despliegue de entrada1200 autorizado

13nov2026 Europe/Madrid, Fase7.4. Propietario solicita desplegar el cambio
3987cab a producción enCT627; probará él después las narraciones largas.
Autoriza build/backup y sustitución acotada de app/política/controlador/worker
necesarias para coherencia, con rollback y comprobaciones de salud. No ejecutar
inferencias ni suite de pruebas; conservar400tokens/EOS/20sWAV/300s/guardas,
Qwen, efectos, datos, imágenes previas y recursos. No intervenir otrosLXC/pipeline.
Comprobación inicial: app21270364 healthy, Qwen/CBready, cero trabajos activos;
producción aúnCB240. Despliegue IN PROGRESS antes de aplicar.

### Voicebox — entrada1200 desplegada, validación larga pendiente

13nov2026 Europe/Madrid. Backup180archivos HDD/restauraciónaisladaPASS; UI
compilada y nuevaimagen218dc413 sobre21270364, mismaUID999/entrypoint/CMD.
Primer intento revertido automáticamente por comprobación UI sobre descripción
eliminada delbundle; sin fallo de arranque/datos. Observador corregido, segundo
intentoPASS, mismo artefacto; UI/API/controlador/worker1200. IdempotenciaPASS
sin recargas. SQLite/perfil/ref/12filas y11audios originales conservados;
Qwen/CBes/en/Kokoro/Piper saludables, sinOOM/activos/CTrestart/otrosLXC/pipeline.
400tokens/EOS/20sWAV/300s/guardas intactos. Sin suite ni inferencias. Despliegue
DONE; narración completa1200TODO por propietario, sin atribuir aceptación acústica
a esta ampliación. [Informe](VOICEBOX-CHATTERBOX-INPUT-1200.md).
## IA-CHAT-A — autorización del encargo, 2026-11-13

Aprobado: preflight de solo lectura y plan para infra-llm/infra-webui nuevos, bajo Fase 7; ningún CT existente se modifica. Punto de parada obligatorio antes de crear nada. Propuestas B–F aún no aprobadas. Guardas: MemAvailable host >=21 GiB antes de modelo grande, secretos600, SSH estricto, versiones fijas; no cambios red/storage.cfg/627 ni commit/push.

### IA-CHAT-A — parada por ausencia de modelos

Hecho: ambos ficheros Qwen declarados ausentes, FaseA BLOCKED. No hash local ni despliegue. Propuestos, no aprobados:630/631, IP230/231 sujetas DHCP, Gemma UnslothUD-Q4_K_XL y plan de96GiBSSD. Versiones todavía incompletas. Aclarar ruta y completar preflight antes de solicitar confirmación de creación. Ver [informe](IA-CHAT-PREFLIGHT-2026-11-13.md).


## IA-CHAT A–F — reanudación autorizada — IN PROGRESS

13nov2026 Europe/Madrid. El propietario sustituye bloqueo por ausencia de pesos:
autoriza descarga en630, altas630/631 DHCP, volúmenes96GiBSSD, instalación,
compilación, benchmarks/validaciones, reinicios solo nuevosCT, backups/jobs propios,
README /root/ia-local y reservas MikroTik exclusivamente si acceso existente.
627 excluido por completo; exclusión de uso manual/riesgo aceptado, sin mecanismos.
Sin cambios otrosCT/storage.cfg/redhost ni commit/push. Guardas: parar SHA tras
dos intentos, MemAvailable<21GiB antes de cargas, afectación fuera alcance o
aceptación sin solución interna. No pedir permiso entre fases. IPs antiguas propuestas
230/231 descartadas: usar DHCP y reserva si acceso existente; si no, comandos al dueño.
Siguiente: completar A y ejecutar B–F condicionado a guardas; no repetir otros trabajos.

### IA-CHAT — compatibilidad Docker en631

Runtime runc actual rechaza sysctl dentro deLXC conAppArmor antiguo (lxc-pve6.0.0-1). Se prepara OCI crun1.31 oficial/SHAfijo y registro exclusivoDocker631; elección de implementación dentro delCTnuevo. No actualización delhost, no cambiosAppArmor/seccomp ni CTexistentes, no downgrade. Validación pendiente; no afirmar resuelto.

### IA-CHAT — excepción AppArmor631 aprobada

13nov2026 Europe/Madrid. Tras falla real tanto runc como crun1.31, propietario
autoriza expresamente `lxc.apparmor.profile: unconfined` SOLO631 y reinicio deeseCT.
Mantener unprivileged/namespaces/seccomp; pérdida deAppArmor exterior aceptada
solo631, sin extender aotrosCT ni modificar perfiles/paquetes globales. Volver
a runtimeoficialrunc. Crun queda evidencia deintento/no configuración activa.
B–F siguen autorizadas conguardas originales; implementación/validación pendientes.

### IA-CHAT — ajuste interno de memoria de llama.cpp

Primer benchmarkGemma interrumpido(SIGINT/rc130), no válido: repacking por defecto
duplica pesos, RSS≈21,2GiB ymemory.high en630; sinOOM, swap630≈0,76GiB yhost
≈7,12GiB frentea2,47previos. No modificar otrosCT ni swapglobal. Se desactiva
repacking (`--repack 0` enbench, `no-repack=true` enpreset), mmap ybatch512/ubatch128.
Repetir solo benchmarks incompletos conguarda21GiB, sin ampliar recursos.

### IA-CHAT — contexto Qwen reducido según guarda90%

Chat inicial correcto, pero RSSrouter+hijoQwen19,8195GiB supera90% de22GiB
(19,8GiB), aunqueworkingset17,10GiB. Se reduce contexto total131072→65536,
dos slots32768, sin modificarRAM ni otrosCT. Evidencia inicial conservada y
revalidación pendiente. Watcher vigila tantoRSS como workingset. Gemma65536 intacto.

### IA-CHAT — validación y ajustes dentro de los CT nuevos

Qwen con65536total: RSS18,96GiB, chatPASS. FalsoHALT alvolver aGemma: workingset
incluía caché no mapeada delmodelo descargado; RSS6,53GiB/anon0,15GiB aldetenerse.
Observador corregido: máximoderesident_tasks(anon+file_mapped+kernel) yRSS,
conserva current/working_set porseparado; Gemma65536 revalidado. SinOOM.
Visión: primera imagen pixelada falló enQwen; PNG DejaVuSans normal pasó4821
enambos. Sin cambio deversión/modelo/proyector. Thinkingoff0chars/on1040chars
yrespuestaCarlaPASS. STTsmallint8>1GiB incremental ytranscripción errónea; se
usa baseint8. FP32 descartado por2,97GiBworking/1GiBswap en631 sinOOM ysinmejorar.
RAM631 permanece3072MiB. Propuesta noaprobada:4096MiB solo si se quisiera investigar
FP32; no necesaria paraelperfilint8 elegido. STTaproximado4/5palabras: sustituye
prueba→nueva; exactitud limitada se conserva comoresultado, no transcripción exacta.
Criterio operativo de«parecerse»: WER<=20%, registrando errores; noUAT humana.
RAG/STT concurrentes yreboots/limpieza/idempotencia todavía pendientes.

### IA-CHAT — corrección de configuración persistida de audio

Auditoría de SQLite detecta `audio.stt.whisper_model="small"` pese al cambio de
entorno a base. Los ensayos etiquetados base anteriores siguieron usando small;
se conserva su evidencia y se corrige esa clasificación. El pico FP32 de2,97GiB
corresponde a small/FP32. Se precarga base en caché local y se fija mediante API
admin `/api/v1/audio/config/update`, verificando respuesta y valor persistido.
Repetir STT y concurrencia/RAM antes del cierre; no reutilizar sus cifras como
evidencia de base. El backup13:41 se conserva como anterior a esta corrección.
Sin cambios de RAM/otrosCT/627 ni commit/push.


## IA-CHAT — ampliación de alcance aprobada: patrón del repositorio y observabilidad

13nov2026 Europe/Madrid. El propietario solicita integración reproducible completa de
630/631 en Terraform/inventario YAML, docs/inventory, monitorización y Grafana como
el resto del pool; autoriza los cambios necesarios para ello. Aprobación limitada
a los dos CT nuevos y modificaciones aditivas de observabilidad que los incorporen,
con backup/rollback, validación e idempotencia. No rollout global de exporters,
no cambios de aplicaciones/recursos de otros CT y **627 excluido por completo**.
Sin commit/push ni aumento automático de RAM631. Mantener DHCP y reservas pendientes,
unprivileged, volúmenes/modelos y contratos CPU/RAM del repositorio.

Estado IN PROGRESS: la receta pct aislada anterior no basta como cierre del patrón
solicitado; preparar adopción Terraform sin recreación, SSH verificado si procede,
exporters apropiados para630sinDocker y631conDocker, integración aditiva enPrometheus/
Blackbox/Grafana e inventario. Conservar cambios previos ajenos. La validación devoz
sigue pendiente tras corregir WHISPER_MODEL persistido; no declararla aprobada.


## IA-CHAT — decisiones aprobadas y propuestas separadas,13nov2026

Aprobado por el propietario: A–F, excepciónAppArmor exclusivamente631 y ampliación
posterior para que630/631 sigan IaC/inventario/monitorización/Grafana delrepositorio.
Se concreta en adopciónTerraform sinrecrear, soporte opcional plantillaDebian/DHCP/
unprivileged, configuración canónica porservicio, NodeExporternativoambos,
cAdvisor concontainerdRO solo631, targets/reglasBlackbox aditivos yN/AnoDocker630
para alertas/Fleet/Details. Backups/rollback coordinados yTLS/SSH verificados;
no perfilglobal ni rolloutajeno,627excluido, no commits/push. La decisiónN/A solo
se activa conlxc:cadvisor:required=0; serviciossincontrato mantienenexigenciaDocker.

Selección técnica small/int8 trasmedición equivalenteincremental0,853GiB<1GB;
la SQLite persistida manda sobreenv y se verifica modelo efectivo. Se conservan
pruebasmaletiquetadas anteriores yse corrige su atribución. STT4/5palabras es
aproximado, no UAT ni calidad exacta. Sin dispensa de otrasfases/servicios.

Propuesta NO aprobada/aplicada:6314096MiB por pico working2,85GiB>2,7 durante
RAG/STT conexporters. Actual3072MiB. ReservasDHCP aejecutarporpropietario porfalta
deaccesoRouterOSexistente. Restauraciónfuncional yTelegramFIRING/RESOLVED recibidos
para630/631 no realizados; no ampliar aceptaciones/dispensas heredadas.


## IA-CHAT-NOTES — alcance aprobado por el propietario,13nov2026

Ampliar Notes y fichas de los CT nuevos usando627 como referencia de estructura.
Identificación inequívoca por despliegue previo y consulta actual:630/631.
Se autoriza exclusivamente description/Notes de esos dos CT en Proxmox, conservando
la información anterior útil y excluyendo secretos. Sin reinicio, redespliegue ni
Terraform apply general, sin commit/push. Ejecución: API PVE bajo SSH estricto,
control de digest, backup privado y comparación de configuraciones/identidades.
Fuentes canónicas y generador existentes conservados; no se extiende autorización
a CT627 ni a los seis servicios activos ajenos al inventario. No se proponen ni
aplican cambios de recursos, red, backups o aplicaciones en esta intervención.


## IA-CHAT-LATENCY — AUTORIZADO (13/11/2026, Europe/Madrid)

Fase 7. Optimización autorizada exclusivamente en630/631, sin627 ni otros CT.
Medir primero Open WebUI /api/chat/completions en stream con Gemma cargado y logs
filtrados por petición. Después: desactivar herramientas nativas por defecto y tareas
competidoras (títulos/consultas), idle3600, caché/prefijo/slots, benchmark3repeticiones
por modelo pp512/pp2048/tg128 con b512/2048 y ub128/256/512, generación3h/prompt4h.
Repacking soloGemma si margen medido y sin duplicar pesos. Objetivo<=10s en caliente,
además<=15s tras5minidle. Sistema con fecha/weekday exactos deWebUIv0.13.3.
RAM6314096MiB expresamente aprobada; verificar RAG/STT y memory.events.
Swaphost porCT solo lectura, sin consulta de aplicaciones ni ejecución en627.
Preservar secretos, datos, backups/rollback e idempotencia. Sin commit/push.



IA-CHAT-LATENCY: prueba de caché SWA completa Gemma con contexto16384total/
8192por slot, frente a65536total anterior. Modelo declara25capasSWA,8cabezasKV,
256dim,K/Vf16: SWAfull64k requeriría~12,5GiB extra deKV y excede margen90%22GiB.
Se prueba16k total bajo guardaRSS/residente<90%; Qwen conserva65536total.
Cambio de contexto comunicado al propietario durante ejecución; no aumento deRAM630.
TemplateJinja derivado delGGUF conserva prefijo vacío de reasoning-off en historial;
primera petición y thinking-on comprobados idénticos. Aceptación pendiente de prueba.

### IA-CHAT-LATENCY — resultado de la ejecución autorizada

13/11/2026 Europe/Madrid. Perfil técnico probado: Gemma b2048/ub512 yQwen
b512/ub512, 3h generación/4h prompt. Defaults sin herramientas implícitas ni tareas
competidoras, fecha dinámica, idle3600, cache_prompttrue. GemmaSWAcompleta ytemplate
versionado quedan aplicados con16384total/8192por slot; Qwen conserva65536total y
preserve_thinkingtrue. El cambio de contexto es una elección técnica comunicada
dentro del ajuste de caché, no una aceptación humana de contexto lleno oUAT.
4096MiB631 expresamente aprobados y verificados. Repack descartado por margen.
PruebasUI, idle300s, matrizr3, RAG/STT, idempotencia ylimpiezaPASS; JWT401 ydatos
del propietario preservados. Se conserva el fallo inicial de búsqueda sin resultados
yla variación desfavorable deQwen3000. Fase7 global permanece IN PROGRESS.
No nuevas propuestas de ejecución sobre otrosCT. [Informe](IA-CHAT-LATENCY-2026-11-13.md).

## IA-CHAT — publicación autorizada y contexto futuro

13/11/2026. Aprobado por el propietario: documentar y hacer commit/push de IA-CHAT.
La restricción anterior sin commit/push queda sustituida para este alcance; no
incorporar cambios ajenos ni secretos. Sin nuevos despliegues o cambios de CT.
Propuestas TODO, no aprobadas para ejecución: resumen automático, recuperación de
notas, otro presupuesto de slots o capacidad/modelo. No prometer memoria automática
por usar carpetas o búsqueda. [Plan y criterios](IA-CHAT-CONTEXT-PLAN.md).

### IA-CHAT — publicación verificada

Commit principal2d945b0 publicado y comprobado en origin/main. Documentación DONE;
plan de ampliación de contexto TODO, sin nueva autorización de despliegue.
[Recibo de publicación](evidence/ia-chat-latency-2026-11-13/publication-verified.json).
## IA-CHAT-SWAP-631 — autorizado

El propietario autoriza swap631 de1024 a1741MiB (~1,7GiB), IaC, commit ypush.
Sin cambio de RAM, reinicios ni otrosCT. El aumento amplía cuota de swap del CT,
no crea swap física en el host ni garantiza mayor velocidad.

Resultado técnico:1741MiB aplicados, segunda aplicación0escrituras, PVE/cgroup/
Node/Prometheus PASS, sin reinicios ni cambios aotrosCT. [Informe](IA-CHAT-SWAP-631.md).
