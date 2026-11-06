# Fase 4 — causa raíz de CPU en CT 619

Seguimiento: 2026-11-03 (Europe/Madrid). Las evidencias numéricas conservan UTC.
Autorización: D-029, con candidato cAdvisor256MiB aprobado D-028.

## Causa y alcance demostrado

El muestreador descartaba el timestamp explícito en milisegundos que acompaña a
`container_cpu_usage_seconds_total`, así como `read` de Docker. El validador
comparaba el acumulativo cacheado de cAdvisor con el acumulativo actual de Docker.
`container_last_seen` representa la exposición de la métrica, no la fecha de la
muestra CPU: usarlo como frescura CPU no corrige el desfase.

Los14 fallos reproducibles conservados del diagnóstico afectan exclusivamente al
ID `f1b11c591622d87e404c996ebb4eb06207776f236e52320a2512ab23f2230f85`,
contenedor `cadvisor`. No se compararon por accidente originales ni otros CT.

| Muestra diagnóstica | cAdvisor (s CPU) | Docker (s CPU) | cgroup (s CPU) | Diferencia cAdvisor/Docker (s) | Tolerancia (s) |
|---|---:|---:|---:|---:|---:|
| 3 | 10.665283 | 11.972806 | 11.976798 | 1.307523 | 1 |
| 4 | 10.665283 | 11.991161 | 11.997478 | 1.325878 | 1 |
| 9 | 12.064623 | 13.504951 | 13.509448 | 1.440328 | 1 |
| 35 | 18.174179 | 19.612720 | 19.617517 | 1.438541 | 1 |

[Los14 valores exactos, identidades y timestamps](evidence/2026-11-03-619-cpu-root-cause.json).
La ventana original fallida descartaba las muestras completas al capturar la
excepción; no es posible reconstruir sus diez valores faltantes. El registro exterior conserva muestra, mensaje y traza cuando el probe devuelve
datos; el diagnóstico independiente sí preservó sus36 muestras completas.
Tras el bloqueo623 se preparó/probó una mejora local para conservar también el
probe completo y edad/ID/valor exactos cuando falla dentro de la alineación;
esta mejora adicional no está desplegada.

Docker y cgroup coinciden en los valores guardados. La comprobación de solo lectura
en620, misma versión y digest de cAdvisor, demuestra el efecto al comparar un
mismo timestamp:202.542049s de cAdvisor frente a202.541956647s de Docker/cgroup.
Sobre54.747332s de ventana común:0.006619665 y0.006628653 núcleos, respectivamente.
[Prueba temporal](evidence/2026-11-03-619-cpu-alignment-live-proof.json).
El reintento en619 reproduce el falso fallo con los mismos contenedores:7.543747s
cacheados frente a8.962150s actuales, pero7.544305s/7.544219s en Docker/cgroup
al timestamp correcto. [Confirmación directa619](evidence/2026-11-03-619-aligned-versus-unaligned.json).
CT619 completó21 muestras/600,442s, backups/rollback/idempotencia y TelegramAPI;
sus cuatro contenedores pasan CPU alineada. Ver [resultado](evidence/2026-11-02-rollout-619.json).
La vigilancia posterior sigue activa y no equivale a aceptación global. Es un defecto del muestreador/validador; no hay evidencia de error contable de Docker
ni del LXC. La validación propia de619 debe cerrar producción: la prueba620 no
sustituye sus gates.

## Fórmulas y normalización

- cAdvisor: `cpu.usage.total / 1e9`, segundos CPU acumulados de todos los núcleos.
- Docker API: `cpu_stats.cpu_usage.total_usage / 1e9`, misma unidad y ámbito.
- cgroupv2 del ID concreto: `cpu.stat usage_usec / 1e6`.
- Consumo en núcleos: `delta segundos CPU / delta segundos reloj`, mismos extremos.
- Porcentaje respecto a un núcleo: `100 * consumo en núcleos`.
- Porcentaje LXC: el anterior dividido entre capacidad asignada (2 en619).
  Docker online_cpus=2 y LXCFS=2, cpuset1-2; cAdvisor cuota0,5CPU
  (cpu.max50000/100000, NanoCpus500000000). Ninguno de estos factores
  escala el acumulativo. [Verificación](evidence/2026-11-03-619-cpu-normalization.json).
- Docker CLI usa `delta total_usage / delta system_cpu_usage * online_cpus *100`;
  ese porcentaje no interviene en este validador. No multiplicar/dividir los
  acumulativos porCPU. Prometheus LXC usa `100*rate(lxc_cpu_usage_seconds_total[5m]) /
  lxc_cpu_capacity_cores`, conservado sin cambios.

Referencias primarias: [cAdvisor v0.60.6](https://github.com/google/cadvisor/blob/v0.60.6/lib/metrics/prometheus.go),
[Docker API](https://github.com/moby/moby/blob/master/api/types/container/stats.go),
[Docker CLI](https://github.com/docker/cli/blob/master/cli/command/container/stats_helpers.go).

## Corrección reproducible y límites

[Instrumentación](../../scripts/exporter-cpu-alignment.py),
[generador D-025](../../scripts/prepare-approved-exporters.py),
[regresiones](../../tests/monitoring/test_cpu_alignment.py).

Se conserva el timestamp explícito; un lector de solo lectura registra Docker y
el cgroup exacto, con ID completo y StartedAt. Para cada muestra cAdvisor se exigen
lecturas anterior/posterior del mismo arranque, separadas<=2s, y frescura<=90s.
La estimación interpolada se conserva como evidencia; el gate exige que **ambos
extremos medidos** cumplan la tolerancia original `max(1s CPU,3% referencia)`, y
compara también incrementos sobre ventanas idénticas. No amplía tolerancias por
edad de caché, número de CPU ni huecos. No permite fallback ni CPU cero por ausencia.
Las comprobaciones de RAM, identidad, frescura, OOM, aplicaciones e integración
permanecen. El lector tiene duración acotada y se detiene tras vigilancia posterior.

Durante el reintento, el lector inicial encontró PID0 al detenerse un exporter en
el ensayo de rollback. Se detuvo el gate antes de observación; la regresión nueva
cubre list/inspect/proc cuando un proceso desaparece y mantiene rechazo de cgroup
incorrecto. Se reanuda el mismo checkpoint idempotente con historial nuevo, sin
reiniciar exporters/apps ni repetir despliegue. Originales, candidatos, backups,
historial anterior y HALT quedan conservados.

## Ejecución y tiempo

Consultar [estado vigente](CURRENT-STATUS.md), [ejecución autónoma](AUTONOMOUS-EXECUTION.md)
y [cronometraje](evidence/2026-11-03-619-cpu-investigation-time.json).
Backups/rollback y gates siguen el [rollout existente](PROGRESSIVE-ROLLOUT.md), sin
duplicarlo aquí. Solo PASS completo de619 permite623 y secuencia D-025; una nueva
discrepancia significativa exige detener e informar. R6 continúa excluido.


## Resultado de la continuación autorizada

619 PASS estable; la secuencia alcanzó623 y se detuvo por frescura CPU>90s.
33 muestras/960,793s con un fallo y extensión600,511s; rollback coordinado
verificado, checkpoint7 y aplicaciones originales conservados. No se iniciaron
617 ni posteriores. La muestra íntegra del fallo623 no se conservó;
atribución a test-nginx es hipótesis (hueco de timestamp113,635s), no RCA cerrada.
Diagnóstico posterior41 muestras sin reproducción no dispensa el fallo.
[Resultado623](evidence/2026-11-03-623-halt-rollback.json).
