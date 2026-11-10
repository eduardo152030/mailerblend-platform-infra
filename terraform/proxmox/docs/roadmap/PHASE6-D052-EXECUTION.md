# Fase 6. Grafana & Dashboards — D-052

Dashboard principal **DONE técnico**, Fase 6 **IN PROGRESS**. 2026-11-07
(Europe/Madrid). Aceptación visual del propietario pendiente; no se extiende UAT
ni se declara cerrada toda la fase.

[Acceso directo](http://192.168.1.111:3010/d/proxmox-lxc-fleet/proxmox-c2b7-lxc-fleet-overview?theme=dark) ·
[Manual IaC, consultas, altas y recuperación](../../services/infra-grafana/FLEET-OVERVIEW.md).

## Resultado

Dashboard real Grafana12.3.1 en CT611, UID `proxmox-lxc-fleet`, carpeta Proxmox,
provisioning exclusivo. Cinco tarjetas con descubierto/inventariado, disponibilidad
porcentaje y UP/configurados, tabla de diez columnas con17CT, CPU/RAM/disco LXC,
alertas activas y componentes Docker para diagnóstico. Filtros dinámicos Service/LXC,
rango y enlaces desde CT a la vista filtrada. Tema oscuro, estados coloreados,
priorización de problemas y UNKNOWN explícito. Sin listas CT fijas en el JSON.

Fuente CPU aceptada F4 y RAM LXCFS; Node `vmid` se normaliza a `ct_id`, cAdvisor
se une por servicio. Tres alias de sondas se normalizan semánticamente para salud
y alertas; no se inventa la identidad de `infra-doc` ni de Internet. Probes asociadas
ofrecen cobertura de disponibilidad parcial:11CT con Application Health UNKNOWN,
6con sondas asociadas. Docker healthy separado. 17exporters UP no implica17apps
certificadas. No nuevas sondas ni modificación de reglas/umbrales F5.

## Validaciones y evidencias

| Control | Resultado |
|---|---|
| JSON/generación | Parse correcto, UID estable, generación determinista |
| PromQL directo |26consultas reales PASS;17CT únicos por tabla/recurso, sin NaN/Inf |
| Datasource Grafana | Salud OK;9consultas de salud por proxy autenticado devuelven17CT |
| Contrato de estados |12casos sintéticos promtool PASS: nuevo999, datos ausentes, exporter/sonda caídos, RAM por severidad, fallo+ausencia, Docker unhealthy, alerta crítica y alias |
| Navegador real | Login, KPIs/tabla/gráficas, filtros CT/servicio, rango1h, navegación CT y componentes; sin errores JS/consulta detectados |
| Alertas actuales | Cero FIRING/PENDING; mensaje explícito «Sin alertas activas». No se fuerza incidencia real |
| Provisioning API | `meta.provisioned=true`; modelo desplegado coincide con JSON |
| Conservación | Contenido de7dashboards anteriores y2datasources intactos; contenedor/StartedAt/restartCount/mounts conservados |
| Backup/restauración | SQLite consistente y configuración enCT/fueraPVE, SHA256 idéntico, restore-check staging/integrity_check PASS |
| Segunda aplicación | Cero escrituras de configuración, recargas o reinicios; hashes/identidad idénticos |

- [PromQL](evidence/2026-11-07-d052-promql.json).
- [Datasource](evidence/2026-11-07-d052-datasource.json).
- [Despliegue](evidence/2026-11-07-d052-deployment.json).
- [Idempotencia](evidence/2026-11-07-d052-idempotence.json).
- [Navegador](evidence/2026-11-07-d052-browser.json), [captura real](evidence/2026-11-07-d052-fleet.png).
- [Estado final](evidence/2026-11-07-d052-result.json).

Las marcas `timestamp_utc` de JSON permanecen enUTC; seguimiento enEurope/Madrid.
La captura es del sistema real, no una maqueta ni un ensayo con datos inventados.

## Incidencias controladas

Autenticación inicial401; propietario indicó archivo local ignorado y se utilizó
sin mostrar/copiar credenciales. No reset de contraseñas.

Tres retornos preventivos: primero por incremento de versión de NodeSlim durante
recarga del provisioning legado; otros dos por orden variable del array Mounts de
Docker. En todos se conservaron originales/backups; inspección confirmó contenido
idéntico de dashboards y mismos mounts por destino. Comparadores corregidos:
excluir solo `version` al comparar contenido de dashboards, ordenar mounts por
Destination conservando todos sus atributos. NodeSlim pasó deversión20a31 por
recargas, con contenido idéntico. No se oculta como ausencia de incidente.

Provider aislado evita el bloqueo por duplicados de los dos `default` antiguos.
Solo se recargó configuración de dashboards; cero restarts/recreaciones/pull.
Actualizaciones posteriores del JSON se cargaron por polling. Transacciones
protegidas con flock local; no ejecutar generador/cambiar fuente durante apply.

## Límites y siguiente paso

- `ALERTS` no proporciona descripciones/activeAt: disponibles en el enlace a
  Prometheus, no en columnas inventadas. No historial RESOLVED. Sin fuente
  adicional instalada ni cambios de Telegram/reglas.
- Disponibilidad de aplicaciones parcial: UNKNOWN conserva11CTsinsonda. La salud
  Docker no la reemplaza. Los casos con incidencias se prueban sintéticamente,
  sin provocar alertas productivas ni certificar entrega Telegram en esta fase.
- El dashboard es dinámico; targets file_sd explícitos requieren alta IaC y
  publicación aprobada. No discovery automático de infraestructura afirmado.
- LXC Details pendiente, sin enlaces rotos. Environment ausente, sin variable falsa.
- F6-02 conserva duplicados heredados de Compose/providers e imagen latest. No se
  hace saneamiento global ni se sobrescriben dashboards ajenos.
- Persistencia por archivos/mounts acreditada; recreación real de Grafana y UAT
  visual del propietario no realizadas. No se afirma F6-04 global DONE.

Siguiente paso: revisión visual del propietario y elección del próximo dashboard
F6. No avance automático ni nuevos cambios productivos autorizados por el cierre.
Sin apps/DB/exporters/recursos/LXC, cambios enCT610, commits ni push.
