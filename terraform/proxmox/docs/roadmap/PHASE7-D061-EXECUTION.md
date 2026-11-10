# Fase 7 — consolidación Git y preparación de nuevas altas D061

2026-11-10 (Europe/Madrid). Alcance aprobado: **7.1 Git Consolidation** y
**7.4 Automated LXC Provisioning**. 7.2 Security Hardening y 7.3 Disaster Recovery
**OUT OF SCOPE**, no DONE. Fases1–6 conservan sus cierres. Numeración operativa del
propietario distinta de las tareas históricasF7-04(secretos)/F7-06(DR).

## 7.1 — consolidación

Estado: **DONE**. Cinco commits principales publicados por SSH normal; main y
origin/main sincronizados0/0 en checkpoint `4bd0feceaec1d60e5d2759857ba97d4c820c8e3b`.
El registro de cierre se publica en un commit documental separado, sin reescrituras.
Rama main, upstream origin/main y remoto SSH
`git@github.com:eduardo152030/mailerblend-platform-infra.git` verificados por fetch
con BatchMode, known_hosts del propietario y StrictHostKeyChecking=yes.
HEAD/origin inicial: `7deba1cc8cfa7740ba8f8bd1d99e3fc2887d7ca9`;0ahead/0behind.
Un único worktree, índice inicialmente vacío; ningún archivo eliminado al auditar.

Backup privado fuera de Git: refs.bundle verificado, patches binarios staged/
unstaged, índice, status y242 archivos nuevos. La primera resolución del índice se
corrigió por ser relativa al subdirectorio; el respaldo final se verificó antes de
seleccionar archivos. Rutas bajo `~/.local/share/mailerblend-recovery/git/d061/`.
No reset, stash, limpieza ni reescritura de historial.

Selección explícita por grupos: IaC/Notes/inventario; Prometheus/Alertmanager/Blackbox/
exporterPVE; Grafana; scripts/tests de monitorización; documentación/evidencias.
Excluidos los cambios funcionales de
`services/infra-eva-assistant-bot/compose/api/sync_service.py` y los directorios
`services/infra-gestoria`, `services/infra-journal-api`, `services/infra-journal-db`,
`services/infra-journal-web`. Las correcciones de healthchecks D051 y overlayssGTM
D044/D048 sí son monitorización autorizada, con apps/imágenes/datos conservados.
Secretos reales, .env/perm.env, tfstate/tfvars y backups privados no se seleccionan.
.gitignore amplía únicamente la exclusión de .env reales; no rota credenciales ni
reescribe el historial. No se ejecuta hardening ni DR global.

Gitleaks8.30.1 sobre copia privada curada, redacción activada. Un hallazgo de
`generic-api-key` corresponde al SHA256 del archivo
`inventory/services/infra-journal-api.yml` dentro del manifiesto de Notes: hash
calculado y cotejado con su fuente, no token. Cualquier hallazgo diferente detiene
publicación. Se registra el falso positivo, no se desactiva el detector global.
La ausencia de secretos nuevos no afirma que las credenciales históricas estén rotadas.

## 7.4 — READY FOR FIRST REAL PROVISIONING TEST

Preparación implementada, sin infraestructura creada ni servicio productivo modificado.
[Runbook completo](../runbooks/NEW-LXC-PROVISIONING.md).

- [Preparador](../../scripts/new-lxc.py): copia aislada del mismo módulo Terraform,
  sin state/backend/credenciales reales; inventario existente más nueva declaración.
- [Lógica compartida](../../scripts/lxc_provisioning.py): validación, Notes/ficha,
  systemdCPU/Node, cAdvisor opcional, targets/módulos/reglas esperadas aditivas.
- [Verificador futuro](../../scripts/verify-new-lxc.py): solo lectura real y recibo
  local; no se ejecutó contra Proxmox enD061. EtiquetaCPU solo trasgatePVE/cgroup.
- [Bootstrap futuro](../../templates/provisioning/install-monitoring.py): únicamente
  exporters del nuevoCT autorizado. Node nativo1.10.2 con SHA256oficial; cAdvisor
  0.60.6 por digest siDocker, socket/namespace exactos requieren aprobación nueva.
- [Fixture nativa](../../examples/new-lxc/service.yml),
  [fixtureDocker](../../examples/new-lxc/docker-service.yml): TEST-NET-2, no aplicar.
- [Tests](../../tests/provisioning/test_new_lxc.py) y generación Notes/inventario
  existente extendida sin cambiar recursos de los17CT actuales.

Dos planes mock revisables:1create/0update/0destroy, sin backend ni llamadasPVE,
Terraform1.14.3 y bpg/proxmox0.94.0. Se detectó y corrigió la selección recursiva de
pruebas (0tests no vale) y la salidaTerraform que indexaba recursos no presentes en
un plan dirigido. Se conserva el lock original; init normaliza solo la copia de
prueba y comprueba que no cambie la versión del provider.

Declaración completa:CTID/hostname/entorno/IP/CPU/RAM/disco/plantilla/SO/red/storage/
tags/propósito/apps/puertos/dependencias/monitorización. Notes con las nueve secciones;
ficha individual detallada yestado `PENDING VERIFICATION`. No se afirma despliegue,
funcionalidad, backup o aceptación del ejemplo. Observaciones posteriores solo desde
recibo real cotejado; estabilidad/aceptación continúan pendientes hasta probarlas.

Sin Docker: Node nativo, CPUcgrouptextfile (collector.cpu deshabilitado), LXCFS y
filesystem real; ningún cAdvisor ni instalaciónDocker. `lxc:cadvisor:required=0`
permite cAdvisorN/A y Monitoring real, sin alertas falsas de ausenciaDocker. Ese
ajuste de regla/dashboard se publica **preparado y no aplicado a producción**;
requiere autorización de primera integración y backup/rollback coordinado.
Los17actuales sin esa marca conservan su estándar. Nuevos CT aparecen porinventario/
labels publicados, sin editarJSON porCT; targetsfile_sd requieren altaIaC explícita.

## Validación y límites

Terraformfmt/validate y mockplan; JSON/YAML/Python; Compose con parser oficial
2.39.4 (checksum verificado), fixtures de reglas y promtool/amtool oficiales,
tests relevantes de inventario, salud/exporters/Notas/Grafana, enlaces/diff.
Sin repetir ensayos productivosF4/F5/F6 ni enviar Telegram.
[Resultados](evidence/2026-11-10-d061-validation.json).

Primer ensayo real sigue pendiente: acceso/plantilla/LXCFS/namespaces, instalación,
idempotencia delbootstrap, integración, estabilidad y cadena real. El mock no acredita
nada de eso. Los endpoints de ejemplo son contratos declarados, no servicios vivos.
No se desplegaron apps ni se reservóIP, cambióDNS, aplicóTerraform o modificórecursos.

Publicación principal completada y verificada. Siguiente: alta real de un CT
específico solo tras nueva autorización.

## Commits principales publicados

| Commit | Grupo |
|---|---|
| `5dfcce346f1b` | feat(iac): prepare reproducible LXC provisioning and generated notes |
| `31308da1c915` | feat(monitoring): finalize alerting, functional checks and PVE uptime |
| `1c09bd301dd5` | feat(grafana): provision Fleet and LXC Details with preserved legacy dashboards |
| `b765b6ad357d` | feat(tooling): add guarded monitoring recovery and provisioning validation |
| `4bd0feceaec1` | docs: consolidate phase evidence and new LXC provisioning runbook |

[Evidencia Git publicada](evidence/2026-11-10-d061-git-published.json).
El HEAD final incluye el commit de cierre posterior; consultar `git log`/`rev-parse`
y la confirmación final de sincronización. No hay autorreferencia del hash del
propio documento.20rutas ajenas conservadas, algunas directorios; ninguna borrada.
Índice vacío tras la entrega principal. El árbol no se declara limpio: contiene
los cambios funcionales excluidos y sus archivosignorados originales.

Validación:28grupos PASS,7modelosCompose,14testsInventario y6testsProvisioning,
fixturesPrometheus y regresiones relevantes de cambios publicados. Dos pruebas
Terraform efectivamente ejecutadas con mocks, cada una1alta/0cambios/0destrucciones.
651enlaces comprobados contra el checkout final disponible; sin referencias a
archivos de aplicaciones excluidos. Único hallazgoGitleaks:SHA256 verificado,0credenciales
nuevas. Fuentes/planes/artefactos de prueba no son despliegues ni aceptación real.

7.1 DONE;7.4 READY FOR FIRST REAL PROVISIONING TEST;7.2/7.3 OUT OF SCOPE.
Siguiente: autorización deun CTreal específico y alcance de integración para probar
creación/plantilla/instalación/observación/idempotencia/cadena. No ejecutar nada
productivo por este cierre. No se reservóIP, modificóDNS ni alterórecursos/credenciales.
Ejecución detenida tras sincronización y comprobación final.

Tiempo registrado desde el respaldo verificado: **36.8min**. Lectura inicial
previa fuera de ese cronómetro. [Cierre/tiempos](evidence/2026-11-10-d061-closure.json).
