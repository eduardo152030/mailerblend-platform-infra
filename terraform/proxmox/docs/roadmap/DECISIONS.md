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
Métricas/thresholds sin cambios;25testspertinentesPASS. Tiempo:81.3min.
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
24testsafectadosPASS. Tiempo:58.1min. [Cierre](EXPORTERS-D041-CLOSURE.md).
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
