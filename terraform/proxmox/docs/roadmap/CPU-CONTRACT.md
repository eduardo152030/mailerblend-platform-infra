# Contrato CPU LXC — compatibilidad preparada

F4-10. Local validado; **no desplegado en Prometheus**. Fecha 2026-11-02.

## Consulta y semántica

Fuente exclusiva: counters `lxc_cpu_*` del cgroup del LXC, incluidos descendientes.
Capacidad asignada contrastada con Proxmox, cpuset y cuota efectiva; si cambia la
asignación se aborta/revisa el bundle. No inferir capacidad desde machine_* de cAdvisor.

```promql
100 * rate(lxc_cpu_usage_seconds_total[5m]) / lxc_cpu_capacity_cores
```

La fórmula muestra la semántica; la implementación con máscaras e identidades está
en [lxc-cpu.yml](../../services/infra-prom/config/rules/lxc-cpu.yml).
`rate` aporta segundos CPU/segundo; dividir por cores asignados da la fracción del
LXC completo. En 2 CPU: 1 s/s=50%, 2 s/s=100%. La ventana de 5 min suaviza; necesita
al menos dos muestras y no se inventa un cero durante calentamiento. Los resets del
counter los trata rate. No se limita el resultado a 100: una ráfaga/cuota cambiante
puede superarlo y merece investigación, no ocultación.

`lxc:cpu_usage:percent` conserva job/instance/service/ct_id y añade
resource_scope=lxc,cpu_source=cgroup_v2. Nunca suma métricas cAdvisor: un contenedor
Docker es descendiente y mezclar ambos produciría doble contabilización. El uso por
contenedor sigue siendo container_cpu_usage_seconds_total, con identidad Docker.

## Selección y calidad

El generador de targets, **solo local**, añade cpu_contract=lxc_cgroup_v1 a Node de
CT 624/625/626. vmid del target se transforma en ct_id para exigir coincidencia con
el exporter; no se confía solo en el label enviado por este. En otros targets se
conserva la rama antigua de CPU sin alterar su comportamiento; eso no certifica su
calidad pendiente. No hay fallback al contador físico en un target con contrato LXC.

Recording rules ordenadas: expected → valid → percent. La máscara exige:

- up=1, job node_exporter, scope LXC y fuente cgroup_v2;
- ct_id coincidente con vmid, capacidad positiva/finita y una serie por identidad;
- total/user/system presentes, finitos y no negativos; sin duplicados;
- success=1, textfile_scrape_error=0 y ausencia del collector CPU nativo;
- timestamp del writer entre -2 y **45 segundos** de antigüedad. Exige relojes
  sincronizados. El límite Prometheus cubre scrape 30 s + writer 5 s + margen 10 s;
  no usar aquí el gate directo de 15 s, pues Prometheus conserva el timestamp del
  último scrape entre recogidas. Hay tests de edad 30 s aceptada y 46 s rechazada.

El validador y observer consultan el exporter directamente, por lo que mantienen
el límite estricto de 15 s. Ambas ventanas responden al mismo writer pero a rutas
con distinta caché. No es necesario cambiar ahora el scrape global de 30 s.

Ausencia, NaN, infinito, capacidad cero/negativa, duplicados, identidad distinta,
error textfile o antigüedad excluyen percent. `LxcCpuCollectorInvalid` warning tras
2 min indica calidad inválida sobre targets esperados y up=1. up=0 se mantiene en
HostOutOfService (no doble alerta de calidad). Si desaparece el target del discovery,
no hay up esperado: requiere validación del catálogo, no convertir ausencia en éxito.
Una tasa ausente por falta de historial inicial no significa CPU cero; la alerta
de calidad compara expected con percent y espera 2 min. Si la ausencia persiste
aunque los counters parezcan frescos, alerta para investigar continuidad/historial
de scrapes; no se crea una tasa artificial. Docker, LXC y disponibilidad de aplicación mantienen contratos
separados.

HostHighCpuUsage acepta percent del contrato y mantiene **>90%, for 10m, warning**;
la rama nativa se excluye explícitamente para ese contrato. No se modifican umbrales,
rutas Telegram, inhibiciones ni métricas RAM/disco. Reglas y cambios locales de
infra-hosts no se han recargado en producción.

## Validadores y pruebas

validate-phase4-evidence rechaza procfs no verificado, fuente desconocida, contador
nativo, CT incorrecto, edad inválida, counters/capacidad ausentes o no finitos y
capacidad distinta de Proxmox. audit-monitoring-runtime recoge esos valores sin Env.
La validación global seguirá fallando hasta corregir los otros CT: es deliberado.

promtool 3.12.0 prueba porcentajes, umbral/for, resets, idle, calentamiento, pérdida,
identidad, valores inválidos, duplicados, datos futuros/antiguos y exporter caído.
Los tests Python prueban los guards, collector 2 CPU, generación y segunda aplicación
con mocks. Los mocks **no** prueban idempotencia real en CT 625/626, pendiente del
lote aprobado. Ejecutar sin SSH ni secretos:

```bash
PROMTOOL=/ruta/a/promtool-3.12.0 bash scripts/test-journal-exporters.sh
```

La dependencia heredada de binarios /tmp sigue en F7; esta intervención no instala
herramientas ni cambia su versión. Ver [plan del lote](JOURNAL-625-626.md).


## Actualización D-021 — integración por CT

[INCREMENTAL-INTEGRATION](INCREMENTAL-INTEGRATION.md) sustituye esperar al rollout
completo: tres Journal primero y cada CT siguiente antes de avanzar. El cálculo y
>90%/10m se conservan. Se añade inventario esperado independiente de up, alarma
MissingTarget y estado legacy unverified, sin fallback físico aun si se pierde label.
P0/R1 preparados y validados localmente; no desplegados. Legacy y corregido se
excluyen también mediante inventario y se identifican explícitamente.
