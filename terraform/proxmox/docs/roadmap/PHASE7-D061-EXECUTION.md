# Fase 7 — consolidación Git y preparación de nuevas altas D061

2026-11-10 (Europe/Madrid). Alcance aprobado: **7.1 Git Consolidation** y
**7.4 Automated LXC Provisioning**. 7.2 Security Hardening y 7.3 Disaster Recovery
**OUT OF SCOPE**, no DONE. Fases1–6 conservan sus cierres. Numeración operativa del
propietario distinta de las tareas históricasF7-04(secretos)/F7-06(DR).

## 7.1 — consolidación

Estado: **IN PROGRESS**, pendiente de publicar la selección validada.
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

Siguiente: publicar commits normales de la selección y verificar origin/main;
después, alta real de unCT específico solo tras nueva autorización.
