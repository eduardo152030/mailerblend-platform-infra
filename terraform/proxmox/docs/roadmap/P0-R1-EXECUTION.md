# P0 y R1 — Ejecución verificada

2026-11-02, Europe/Madrid. Run `integration-20261102T204936Z`.
Fase4 IN PROGRESS; P0 y R1 DONE técnico bajo D-022/D-023.

## Resultados

| Gate | P0 Journal624/626/625 | R1 infra-hola613 |
|---|---|---|
| Integración | 14 legacy preservados +3 Journal | Promoción exclusiva613:4 corregidos/13 legacy |
| Observación | 21 muestras/600,563s | 21 muestras/600,967s |
| Backup externo | SHA y restauración staging verificados | Imágenes/configuración y hashes anidados verificados |
| Rollback | Regreso real14/14/11 y reaplicación17/17/11 | Ambos originales reanudados; checkpoint P0 restaurado; candidatos reanudados |
| Idempotencia | Segunda aplicación sin reload ni cambio ID/StartedAt | Segunda aplicación exporters e integración sin recreación/recarga |
| Telegram real | +6 intentos;0 fallos nuevos | +2 intentos;0 fallos nuevos |
| Recepción | FIRING/RESOLVED tres Journal confirmados | FIRING/RESOLVED613 confirmados |

Pruebas desde reglas sobre métricas reales lxc:cpu_usage:percent, for30s temporal;
retiradas al finalizar. No fueron POST directos a Alertmanager ni pruebas de carga.
Se conserva umbral operativo >90% durante10m. Esa condición de CPU alta no se
provocó: no se declara probada por observar diez minutos un CT sin CPU alta.
Ausencia/antigüedad/invalidez, exclusión legacy/corregidos y capacidad tienen pruebas
PromQL locales; ausencia nunca se sustituye por cero.

## Exporters613 y recursos

Node1.10.2: `prom/node-exporter@sha256:3ac34ce007accad95afed72149e0d2b927b7e42fd1c866149b945b84737c62c3`.
cAdvisor0.60.6: `ghcr.io/google/cadvisor@sha256:b8e7d1093144fd088f425ff003d75a4aa405de075db78dae3bc563730b1bd07a`.
1CPU/512MiB contrastados; CPU cgroups textfile y RAM LXCFS, dos Docker individuales.
Namespace candidato coincide con init LXC y difiere de PVE; socket exacto autorizado
bind ro, sin crear ruta. RO no limita RPC. Originales detenidos conservados.
Sin aplicación empresarial inventariada613; comprobar inventario fue el contrato.
Journal mantuvo aplicaciones/IDs. CRM/EVA no se modificaron.

Cero OOM nuevos y reinicios inesperados. PSI memoria0 durante observación;
MemAvailable mínimo aproximadamente360MiB. memory.high0→399 durante preparación,
399 estable durante21 muestras. Snapshot memory.stat mostró caché predominante;
no confundir memoria.current que incluye caché con RSS exclusivo ni afirmar que no
hubo presión durante toda la preparación. No se ampliaron recursos.

## Archivo posterior y corrección definitiva

El primer archivo posterior asumió carpeta compose; producción tiene
`/opt/infra-prom/docker-compose.yml`. Se detuvo avance. Primer reintento aprobado
falló localmente por copia exporter ya existente, antes de crearV2; nueva detención.
El propietario autorizó exclusivamenteV2 con --monitoring-only. Resultado: archivo
completo/legible, todos los miembros leídos, hashes externos coincidentes; parcial
anterior y copia exporter preservados. Ningún reinicio ni cambio activo en el reintento.
Código IaC selecciona ruta efectiva y rechaza layouts ambiguos/ausentes; pruebas
cubren staging/restauración, aislamientoV2 y preservación de archivos existentes.

Backups privados contienen secretos y permanecen fuera deGit. Directorio operador:
`~/.local/share/mailerblend-recovery/phase4/integration-20261102T204936Z/`.
Backup P0 final histórico: `613/monitoring/integration-before.tar` (checkpoint tres
Journal); archivo final cuatroCT: `613/integration-after-v2.tar.gz`. No confundirlos.
Los backups iniciales conservaban configuración modificada/runtime; el archivoV2
incluye también el mecanismo Compose de raíz que la ruta opcional anterior omitía.

## Evidencias y siguiente gate

- [P0](evidence/2026-11-02-p0-execution.json), [R1](evidence/2026-11-02-r1-execution.json).
- [Porcentajes y capacidad](evidence/2026-11-02-p0-live-percentages.json).
- [Namespace preapply](evidence/2026-11-02-r1-namespace-preapply.json).
- [APIs finales](evidence/2026-11-02-p0-r1-final.json):17Node/17CAD/11Blackbox,
  ready200 ambos, reglashealthok, cuatroCPU fiables, contador histórico fallos56.

R2 preparado para revisión, no desplegado. F4 exige17/17 y validación global independiente.

## Validación local final

124 pruebas Python correctas; promtool3.12.0 valida reglas y tres suites, configuración
y discovery/relabeling sobre snapshot nuevo del runtime:17/17/11, cuatro CPU
corregidas, identidades únicas. Sintaxis Bash y bundlesPython, enlaces y diff correctos.
[Registro](evidence/2026-11-02-p0-r1-local-validation.json). Ningún despliegue adicional.
