# Fase 6. Grafana & Dashboards — D-055 Uptime centralizado

**Actualización D-056:** propuesta autorizada y ejecutada; [informe](PHASE6-D056-UPTIME-EXECUTION.md).
El bloqueo de aprobación siguiente es histórico.

**Diagnóstico/preparación DONE. Ejecución BLOCKED por aprobación de identidad de
lectura nueva. Fase 6 IN PROGRESS.** No despliegue, nuevo usuario/token/ACL, recarga,
restart, Terraformapply, modificación de aplicaciones, commit ni push.

La petición autoriza una solución centralizada y exige presentar la alternativa
antes de aplicar cuando necesite privilegios nuevos o cambios significativos.
La auditoría confirma que no existe una identidad API de lectura reutilizable;
por ello ese paso se detiene, sin reutilizar permisos administrativos.

## Hallazgos actuales

- No métricas `pve_*`/`proxmox_*` ni scrape PVE en Prometheus.
- No exporter PVE en CT610 ni servicio exporter en el host PVE inspeccionado.
- Solo root y la identidad Terraform; el único token hereda PVEAdmin, sin separación
  de privilegios. Es inadecuado para un daemon de monitorización.
- Red Docker Prometheus existente `infra-prom_default`; no requiere reiniciarlo.
- API `192.168.1.100:8006` accesible desde610 con TLS/CA PVE verificados. Sin
  credencial devuelve401, esperado; no se ha probado todavía una credencial nueva.
- Fuente real ya acreditada por lectura administrativa puntual: API PVE con uptime
  por VMID, incluido618 distinto delhost. Es diagnóstico, no un collector desplegado.

## Alternativa mínima preparada

Reutilizar exporter estándar **prometheus-pve-exporter3.11.0**, imagen upstream
fijada por digest `sha256:290756c34fd13e1d9972b8e64344d49a15ab99dd0053b29d9716f1ca4ae4c069`.
Un contenedor nuevo en610, no root, sin capacidades/puertos públicos/Docker socket.
Colectores resources/status, sin configuración porCT, backup o suscripción.
No software en los17CT, comandos root periódicos ni desarrollo de exporter propio.

Permisos propuestos: usuario `prometheus-uptime@pve`, token `uptime` conprivsep=1,
PVEAuditor propagado en `/` para ambos. Rol estándar sololectura delclúster, más
amplio en lecturas que uptime pero sin escritura. No tocar usuario/tokenTerraform.
Secreto por archivo privado montado, no valor enCompose/env/logs/versionado.
CA conocida por SSHestricto, TLSactivo; sin omitir validación.

Fuente: `pve_uptime_seconds` para `lxc/VMID`, `pve_guest_info` para nombre/nodo/tipo,
`pve_up` para estado. Scrape30s, retención solo deesasfamiliasLXC; ct_id se deriva
porrelabeling. No inventar nodeboot ni derivar uptime deDocker/exporter. Fuente
caída, antigua, duplicada o CTparado conservaUNKNOWN; reinicio real actualiza el
contador desdePVE. Reinicios Docker no intervienen en la consulta.

Descubrimiento API sin listaVMID. Dashboard conserva alcance dinámico de los17
monitorizados medianteNode/inventario; futuros CTmonitorizados obtienen uptime
sin editarJSON. TodoslosLXC delAPI se descubren en el exporter; incorporarlos como
monitorizados enCPU/RAM/etc sigue el altaIaC existente. No se afirma que PVEsolo
cree toda la observabilidad. No añadir filas deCTajenos por un outerjoin accidental:
patch completo filtra contra inventario vigente y conserva fallbackUNKNOWN.

## Archivos concretos, sin aplicar

- [Compose](../../services/infra-prom/proposals/pve-uptime/compose.yml).
- [Job Prometheus](../../services/infra-prom/proposals/pve-uptime/scrape.yml).
- [Consulta base](../../services/infra-prom/proposals/pve-uptime/grafana-query.promql).
- [Patch Grafana J](../../services/infra-prom/proposals/pve-uptime/grafana-uptime-patch.json).
- [Procedimiento y permisos](../../services/infra-prom/proposals/pve-uptime/README.md).
- [Pruebas locales](../../tests/monitoring/test_pve_uptime_proposal.py).
- [Evidencia preparación](evidence/2026-11-07-d055-preparation.json).
- [Conservación](evidence/2026-11-07-d055-final.json).

## Validación y límites

Compose validado mediante `docker compose config -q` en610, sin crearcontenedores.
promtool valida eljob aislado y8casos deconsulta sintéticos: antes/después de un
reinicioLXC, caída scrape, CTparado, antigüedad, duplicado, solo bootHOST y ausencia
deestado. Un futuroCT9999 sirve como dato deensayo, no lista productiva.
TLS desde610 verificado con CA/PVE y SANIP coincidente;401sincredenciales.

**No probado todavía:** arranque del contenedor con imagen fijada, permisos reales
del token nuevo, scrape con credencial,17seriesuptime, comparación postdespliegue,
render devalores enGrafana o idempotencia productiva. Esas pruebas dependen de
aprobación. No se declara resuelto Uptime ni desplegados losartefactos.

Siguiente tras aprobación: crear solo identidad de lectura/tokenprivsep, backup
coordinado610/611 y restorecheck; iniciar soloexporternuevo, validar API/métricas/
permisos sin escribir recursos; incorporarjob y JSON porrecarga/polling sin reiniciar
servicios existentes, comparar almenos3CT, verificar17valores y filtros, segunda
aplicación sin cambios y rollback acotado. No reglas/umbrales F5 ni recursosLXC.

Referencia primaria: [repositorio upstream](https://github.com/prometheus-pve/prometheus-pve-exporter).
