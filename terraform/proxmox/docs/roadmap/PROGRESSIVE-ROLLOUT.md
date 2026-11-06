# Fase 4 — rollout progresivo de los 17 LXC

2026-11-02. **R1 completado bajo D-022. R2–R7 preparados como plan, no autorizados.**
Decisión D-019: los 17 LXC, **incluidos CRM y EVA**, son cobertura obligatoria.
Tres Journal aceptados por propietario (D-017/D-020); P0 integrado y verificado.
D-021 sustituye la espera hasta 17 por integración por CT: ver INCREMENTAL-INTEGRATION. Cada CT debe
superar sus gates antes del siguiente. No hay despliegue simultáneo ni cambios de apps.

## Orden exacto y justificación

Fuente de identidad: inventory/services y auditoría runtime existente, no nombres/IP
inventados. Recursos de la auditoría son históricos y deben revalidarse en Proxmox;
no se modifican para acomodar exporters. [Manifiesto generado](evidence/2026-11-02-progressive-rollout-plan.json).

| Lote | Orden CT — servicio | Criticidad / motivo / comprobación específica |
|---|---|---|
| R1 | **613 — infra-hola** | Canario de migración de Node ya instalado, sin aplicación Docker en la auditoría. Confirmar que no haya nuevas apps; validar OS/exporters y retener ambos originales |
| R2 | **621 — infra-project-gestion → 620 — infra-excraper** | Gestión interna antes de workers. Preservar Focalboard; después workers LinkedIn/signals y Redis, comprobar identidades y disponibilidad/colas sin disparar trabajos |
| R3 | **619 — infra-pulpo → 623 — infra-gestoria** | n8n/PostgreSQL y Odoo/PostgreSQL: mayores dependencias de datos. Readiness y consultas inocuas previamente revisadas; no ejecutar workflows ni migraciones |
| R4 | **617 — infra-orbit → 615 — infra-mailerblend-edge → 614 — infra-nucleoedge** | Gateway/proxy antes de entrada y analítica pública; verificar serving y preview por separado. Nucleotecnológico conserva su incidente conocido y sus dos contratos; no silenciar ni dar por reparado |
| R5 | **61211 — svc01** | CT real 61211 (no inferir 612). NocoDB y DB, plataforma multiusuario; preflight/backup propio y observación dedicada |
| R6 | **618 — infra-composable-crm → 622 — infra-eva-assistant-bot** | **Último lote de aplicaciones** por recuperación reciente. Preservar originales/volúmenes de F3, RAM actual de CRM sin nuevos cambios, cron/scheduler/DB de EVA. No extender permisos de paradas forzadas F3 a exporters |
| R7 | **611 — infra-grafana → 616 — infra-blackbox → 610 — infra-prom** | Plano de observabilidad después de aplicaciones; Prometheus/Alertmanager al final. Verificar Grafana /api/health y métricas, Blackbox y sus sondas existentes, Prom/AM readiness y reglas; no reiniciar esas aplicaciones |

Son **14 CT restantes + 3 Journal = 17**. R6 es el último lote de aplicaciones;
R7 solo migra los exporters del plano de monitorización. Toda aplicación nueva,
recurso diferente o dependencia no identificada obliga a revisar el manifiesto
antes de aprobar el lote. Las comprobaciones específicas son contratos a confirmar
en su preflight; no se presentan como pruebas ya realizadas de todos esos servicios.

## Automatización y límites de ejecución

[plan-exporter-rollout.py](../../scripts/plan-exporter-rollout.py) genera de forma
determinista el manifiesto, verifica 17 identidades únicas y cobertura exacta,
congela orden, pasos, digests y recursos históricos; no usa red ni ejecuta comandos.

```bash
python3 scripts/plan-exporter-rollout.py --output /tmp/exporter-rollout-plan.json
```

[rollout-journal-exporters.py](../../scripts/rollout-journal-exporters.py) implementa
el flujo real secuencial autorizado de 626/625: staging por hashes, preflight, backup
con carga de imagen, copia externa, pulls por digest, apply, rollback, reanudación,
segunda aplicación y observación. CT 625 exige PASS registrado de CT 626 en el mismo
run. Rechaza otros CT y la repetición ciega de un run existente; no dispone de opción
all ni de fallback a SIGKILL. Conserva checkpoints privados para diagnóstico. Un error
interrumpe el flujo, sin continuar ni intentar un rollback destructivo automático.

**No se afirma que este ejecutor acepte ya R1–R7.** Antes de aprobar cada lote se
preparará el adaptador CT-específico con el mismo helper probado, hostname/IP, límites
reales, imagen Node instalada por digest y probe de aplicación revisado. Esta puerta
impide sustituir validación por interpolaciones de nombres. No cambiar el helper ya
aplicado sobre Journal. El manifiesto futuro mantiene execution=NOT_AUTHORIZED y
socket approval pendiente; no basta editar un JSON para obtener autorización.

Por cada CT, sin paralelismo:

1. Aprobación de lote y socket exacto por CT; validar aplicaciones/dependencias,
   recursos/PSI/OOM/swap, puertos, versión Docker, backend y cgroup padre real.
2. Render local determinista, tests del collector para capacidad asignada y simulación
   de idempotencia/drift; revisar modelo Compose en servidor sin up.
3. Snapshot privado de **ambos exporters existentes**, configuraciones, imágenes/IDs,
   hashes de apps y estado/healthchecks. Archivado de imágenes originales con blob/SHA
   y carga verificada; copia PVE y externa y hashes completos/nested. No tocar datos.
4. Descargar solo digests aprobados si faltan. Mantener Node instalado por digest,
   salvo actualización explícita revisada; las distintas versiones deben probar shell,
   textfile y flags. cAdvisor candidato fijo 0.60.6; no latest/build/update implícito.
5. Parada ordenada únicamente de exporters; conservar nombres/IDs originales. Aplicar
   modelos inmutables exporter-only. Si requiere otros privilegios, detenerse.
6. Contrastar RAM/capacidad LXCFS y CPU cgroup contra PVE; por Docker activo contrastar
   CPU/RAM/identidad/frescura y labels contra API/cgroups. No confundir machine_*, el
   host físico ni límites Docker sin cuota con los límites heredados del CT.
7. Integrar controladamente el CT en Prometheus/reglas tras verificar su fuente.
   Ensayo real coordinado de rollback, verificar running/IDs/imagen/métricas del original y apps;
   reanudar mismos candidatos y segunda aplicación sin cambios de ID/StartedAt.
8. Prueba de regla real/Telegram FIRING/RESOLVED recibidos y ventana inicial según lote (R2–R5:180s/7; R6/R7:600s/21), cada30s, con gates de recursos/aplicación, sin nuevos OOM desde
   preflight, presión significativa ni reinicios; registrar y conservar swap/high.
9. Archivar configuración posterior/evidencias fuera del nodo, actualizar cobertura y
   aceptar técnicamente ese CT antes de pasar al siguiente. Fallo detiene el lote.

No limpiar candidatos, datos, imágenes o volúmenes. No ampliar RAM/disco/CPU ni
cambiar daemon, kernel, LXCFS o Proxmox. Si falla backup, restauración, margen o parada,
conservar estados/evidencias y consultar. Los originales recuperan cobertura anterior,
no garantizan las métricas corregidas. La disponibilidad HTTP/TCP no equivale a probar
login, integridad SQL o flujos completos; la dispensa UAT de F3 no se extiende aquí.

## Integración incremental obligatoria, sin esperar a 17

[INCREMENTAL-INTEGRATION](INCREMENTAL-INTEGRATION.md) sustituye el esquema anterior
que dejaba CPU sin reglas hasta el final. P0 integra primero tres Journal, con
config/targets legacy preservados. En cada R1–R7, medir la fuente al arrancar el
nuevo exporter, promover solo ese CT, verificar Prometheus/reglas y completar
Exporter→Prometheus→Reglas→AM→Telegram antes de avanzar. Un CT no queda completo
por tener exporters; el registro IaC separa fuente, estabilidad, integración y cadena.

Cada lote incluye: preflight; backup/rollback de exporters y checkpoint Prometheus;
pins; despliegue; fuente/identidad; integración controlada; rollback/resume coordinado;
prueba Telegram real desde regla sobre el exporter; observación integrada según política de lote;
idempotencia sin recreación/recarga y actualización roadmap. No ejecutar R2–R7.
R1 CT 613 está [completado técnicamente](P0-R1-EXECUTION.md). R2 preparado, no desplegado.

No hay fallback a CPU física para corregidos; pendientes conservan configuración y
estado unverified explícito. Se mantiene >90%/10m. Handoff tiene tiempos normales de
scrape/rate/for, con timeouts y alertas de calidad; no se promete cero segundos.
Rollback de un CT conserva contratos/reglas de los CT ya integrados. No restaurar
reglas legacy que dejen CPU corregida sin cobertura. Prueba directa a AM no basta.

512 MiB de algunos CT requieren margen específico; no ampliar automáticamente.
Socket ro permite RPC y necesita permiso por CT. Recursos/CPU físicos compartidos,
incidentes previos, swaps y machine_* no se interpretan como límites exclusivos.
Los fingerprints pueden cambiar al promover solo el CT: auditar exclusión de alertas
viejas/nuevas, sin silencios para ocultar fallos. No afirmar integración ya desplegada:
actualmente cuatro fuentes fiables y cuatro cadenas CPU corregidas verificadas.

## Puerta final de integración independiente

Después de cerrar los 17 CT con integración incremental y comprobar las
precondiciones finales de D-019/D-021:

- Backups privados de Prometheus/Alertmanager/discovery y rollback verificados.
- Confirmar los 17 Node y 17 cAdvisor ya integrados progresivamente, sin extras/duplicados, con contrato CPU
  y vmid/ct_id coherentes; activar Grafana y tres sondas Journal conservando las once
  Blackbox existentes. Revisar targets remotos antiguos antes de retirar equivalentes.
- Extender el selector cpu_contract del generador desde los tres Journal a los
  **17 CT realmente validados**, con tests de cobertura exacta; la promoción se alimenta del registro incremental verificado. No olvidar esta
  puerta ni dejar 14 en la rama nativa.
- Desplegar las reglas lxc_cpu_* aceptadas; promtool/amtool/config/templates válidos.
  No ampliar umbrales/for/rutas como parte de compatibilidad.
- APIs reales: targets up, series/capacidades correctas, cuatro capas diferenciadas,
  evaluación de reglas health=ok, >=10 min de muestras por los 17 y ninguna duplicación.
- Verificación independiente FIRING/RESOLVED Telegram y contadores de fallo sin nuevos
  errores durante la prueba; readiness solo no demuestra entrega.
- Comprobar dashboards compatibles con el nuevo contrato y documentar cualquier
  limitación; el diseño completo de dashboards sigue en F6.
- Segunda aplicación sin recargas/recreaciones innecesarias, evidencia y revisión del
  propietario. **F4 no es DONE antes de esta aceptación global 17/17.**

Esta documentación diseña la integración; no autoriza ejecutarla dentro de 626/625.

## Política vigente desde R2 — D-024

[Fuente única](../../services/common/rollout-observation.yml): R2–R5 inicial180s/7,
R6/R7 600s/21, cada30s. Watch externo900s y vigilanciaProm/AM continua. Anomalía
detiene avance y extiende>=600s preservando baselineOOM/restarts. No declarar
validado for no cumplido. P0/R1 completaron600s. [R2 concreto](R2-621-620.md).


## D-034 — SKIP AND CONTINUE (sustituye orden estricto en alcance autorizado)

[Contrato y procedimiento](SKIP-AND-CONTINUE.md).614→61211;617/615 aplazados.
Solo fallo aislado con apporiginal funcionando y todas las pruebas positivas
permite avanzar; validador/IaC/backups/SSH/Prom/cobertura/AM/Telegram/datos o falta
de prueba implicaHALT GLOBAL. En ejecuciónD034:614health503, sin cambios;
vetoapplication_working impide61211. PolíticaBLOCKED al cierre; no repetirrun.


## D-035 — baseline preexistente yregresión (sustituye vetoD034)

[PolíticaA/B/C/D](SKIP-AND-CONTINUE.md). CaseB permite aplazar aplicaciónyaunhealthy
si originalintacto/legacy/alertas/dependenciasverificados. CaseC exigecontención
yrollback;CaseDglobal/lectorcomún/backup/incertidumbredetiene. D03561211revertido
porparsertimestamp;correcciónsolo local. No reparar614paraaceptarotroCTindependiente.
