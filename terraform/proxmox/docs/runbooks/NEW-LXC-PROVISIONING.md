# Alta de un LXC mediante IaC

Estado: **READY FOR FIRST REAL PROVISIONING TEST**, D061, 2026-11-10.
Preparación local probada con mocks; ninguna creación real ni despliegue autorizado
en esta intervención. El primer CT requiere autorización explícita de identidad,
IP/recursos/plantilla, exporters y acceso exacto a sockets si usa Docker.

## 1. Declaración y preparación

Reutiliza `inventory/services/<service>.yml` y el recurso Terraform existente
`proxmox_virtual_environment_container.svc["<service>"]`; no hay otro módulo IaC.
Ejemplos no aplicables: [nativo](../../examples/new-lxc/service.yml) y
[Docker](../../examples/new-lxc/docker-service.yml), direcciones TEST-NET-2.
No reservar esas IP ni copiar ejemplos al inventario productivo.

La declaración exige CT ID/hostname/IP, CPU/RAM/disco, plantilla/SO, bridge/gateway/
DNS/storage/tags, entorno, propósito, propietario, apps/runtime/puertos, dependencias,
dominios, backup/limitaciones y requisitos de monitorización. Valores no conocidos:
`PENDING VERIFICATION`. Las aplicaciones se declaran; este flujo no las despliega.
No contraseñas, tokens ni URLs con autenticación en el inventario.

Preparar fuera del repositorio, sin sobrescribir un bundle anterior:

```sh
python3 scripts/generate-lxc-inventory.py --check
python3 scripts/new-lxc.py prepare \
  --spec examples/new-lxc/service.yml \
  --output "$HOME/.local/share/mailerblend-recovery/new-lxc/example-01"
python3 scripts/new-lxc.py validate \
  --bundle "$HOME/.local/share/mailerblend-recovery/new-lxc/example-01"
```

El bundle contiene copia de los mismos `.tf`, inventario existente más el candidato,
Notes/manifiesto/ficha, configuración systemd/CPU, cAdvisor si Docker, targets y reglas
esperadas aditivas, módulos Blackbox y plan mock revisable. Nunca copia tfstate,
credenciales o un backend productivo. Rechaza identidad/IP duplicadas y salidas dentro
del módulo operativo. Terraform>=1.7 para mocks; probado con1.14.3 y bpg/proxmox0.94.0.

## 2. Validación sin infraestructura

`validate` ejecuta fmt, init de providers sin backend (sin upgrade), validate y
`terraform test` con `mock_provider` y `command=plan`. El directorio de pruebas se
selecciona explícitamente y se exige que haya pasado una prueba; “0 tests” no sirve.
Exige exactamente **1 add / 0 change / 0 destroy** y misma versión del provider.
`plan.mock.txt` y `validation.log` son privados. No son un plan real aplicable.
La eliminación en la copia de una entrada de lock de provider no usado no modifica
el lock del repositorio ni actualiza el provider Proxmox.

```sh
python3 -m unittest discover -s tests/provisioning -v
terraform fmt -check
terraform validate
```

Comprobar contenido de los artifacts, CPU sin fallback físico, Docker opcional,
Notes con sus nueve secciones y estado no desplegado. Gate de primera ejecución:
plantilla real compatible, LXCFS/cgroup v2, arquitectura amd64, Python3/systemd,
TLS/SSH/acceso existentes y disco pedido>=raíz de plantilla (no reducir discos).
El ejemplo no acredita esas propiedades del CT106. No hay llamadas PVE en mocks.

## 3. Plan real: solo después de autorizar un CT concreto

Usar una declaración real fuera de `inventory/services` y preparar otro bundle.
Comprobar disponibilidad de CTID/IP mediante lecturas de Proxmox y red; no reservar
ni tocar DNS sin ese alcance. Verificar previamente la claveSSH de PVE y del nuevo
acceso; nunca keyscan como prueba, checking=no ni known_hosts=/dev/null.

Copiar únicamente la nueva declaración y su ficha del bundle al inventario real,
con revisión del diff. No copiar su `.terraform`, estado ni todo el módulo sobre
producción. Regenerar Notes con el generador existente: conserva los registros
observados anteriores y añade el nuevo como PENDING VERIFICATION.

```sh
# Sustituir los valores; no usar IDs/IP de los ejemplos.
SERVICE=new-approved-service
PLAN_DIR="$HOME/.local/share/mailerblend-recovery/new-lxc/$SERVICE"
python3 scripts/generate-lxc-inventory.py
terraform fmt -check
terraform validate
terraform plan -input=false -parallelism=1 \
  -target="proxmox_virtual_environment_container.svc[\"$SERVICE\"]" \
  -out="$PLAN_DIR/create.tfplan"
terraform show -no-color "$PLAN_DIR/create.tfplan" > "$PLAN_DIR/create.review.txt"
terraform show -json "$PLAN_DIR/create.tfplan" > "$PLAN_DIR/create.private.json"
```

Usar los accesos existentes, fuera de Git; plan/JSON pueden contener datos sensibles:
permisos0700/0600. Verificar que el único recurso con acción es el nuevo CT y que
es `create`: ningún update/replace/delete/import de los17 actuales. Revisar template,
red, privilegios heredados, capacidad y Notes. No `make deploy-all`, ni plan/apply
sin target para evitar discrepancias heredadas. Un plan mock no autoriza apply.
El TLS legacy del provider es deuda fuera del alcance de esta preparación, no una
certificación de hardening; no se desactiva SSH/TLS para superar bloqueos nuevos.

## 4. Creación y exporters: autorización necesaria

```sh
# SOLO después de aprobar el plan real exacto anterior:
terraform apply -parallelism=1 "$PLAN_DIR/create.tfplan"
```

Verificar el nuevo CT por API/servidor: identidad, RUNNING, IP, recursos y rootfs.
No reiniciar otros CT/apps. El bootstrap preparado instala únicamente Node Exporter
nativo1.10.2 con SHA256 oficial, productor CPU cgroup textfile y unidades systemd.
Si Docker está declarado, requiere Docker/containerd ya disponibles en la plantilla;
no instala/reconfigura el motor ni las apps. cAdvisor0.60.6 está fijado por digest.
Socket/namespace/cgroup y privilegios se aprueban para este nuevo CT; no se heredan
los permisos históricos del piloto624 ni Journal. Sin Docker no hay cAdvisor,
Docker sockets, contenedor Node ni necesidad de instalar Docker.

Transferir `bundle/monitoring/` exclusivamente al nuevo CT por el acceso aprobado.
Si se usa PVE, empaquetar, copiar porSSH estricto y `pct push` al CT; nunca ejecutar
el instalador enPVE ni en un CT existente diferente. Extraer, por ejemplo, en
`/opt/lxc-bootstrap/`. Después ejecutar DENTRO del CT autorizado:

```sh
python3 /opt/lxc-bootstrap/install-monitoring.py --confirm-new-ct CTID
# Solo Docker y con aprobación explícita del socket exacto:
python3 /opt/lxc-bootstrap/install-monitoring.py \
  --confirm-new-ct CTID --approve-containerd-socket
```

La identidad y memoria deben coincidir. Archivos idénticos no se reescriben; Node
no se reinicia si su configuración coincide. TimerCPU escribe métricas periódicas,
lo cual no es una recreación. cAdvisor Compose usa reconciliación normal, sin rm,
force-recreate ni aplicaciones. Validar la segunda aplicación en el primer ensayo
real: esa idempotencia productiva todavía no se acredita mediante mocks.

## 5. Verificar exporters y generar candidatos de activación

```sh
python3 scripts/verify-new-lxc.py --bundle "$PLAN_DIR" --node pve --pve-host pve
```

Solo lecturasPVE/cgroup/Node/cAdvisor/endpoints y escritura local de recibo. Rechaza
fixturesTEST-NET. Compara identidad/IP/CPU/RAM conPVE, tiempoCPU frente al cgroup,
MemTotalLXCFS, capacidad y timestamps directos<=15s; no acepta CPU nativa compartida.
Docker exige métricas individuales y namespace init/Docker/cAdvisor coincidente.
Los endpoints deben cumplir HTTP200 y regex funcional declarada cuando exista;
no fabricar disponibilidad desde Docker/Node ni aceptar HTML para un contratoJSON.

Solo tras PASS genera `activation/` con `cpu_contract=lxc_cgroup_v1`. Los targets
iniciales carecen de esa etiqueta: YAML preparado no prueba una fuente verificada.
El recibo es puntual; estabilidad/idempotencia/cadena de alertas siguen pendientes.
Ante FAIL no activar discovery; preservar el CT/datos/backups y diagnosticar.

## 6. Integración Prometheus/Blackbox: transacción acotada

El bundle prepara fragmentos, NO los publica automáticamente. Unir targets del
candidato al catálogo cargado correspondiente en los jobs existentes (Node, cAdvisor
si procede y Blackbox), conservando todos los anteriores. Añadir su expected-inventory
como archivo de reglas, con service/ct_id/instance correctos. No reemplazar globalmente
los catálogos usando un generador histórico. Antes de aplicar, tomar baseline vivo,
backupCT/fueraPVE y verificar restauración; exigir diff exclusivamente aditivo.

Módulos Blackbox nuevos: fusionar `blackbox-modules.yml` sin sobrescribir otros,
parser oficial, recarga controlada y prueba del endpoint antes de incluir la sonda.
No añadir scrapes con módulo ausente. Promtool debe validar la configuración completa
y las reglas; después una recarga controlada y consultas de comprobación.

La compatibilidad sin Docker se prepara una vez en IaC mediante
`lxc:cadvisor:required=0`: cAdvisorN/A, Monitoring sigue siendo una comprobación real.
La regla de ausenciaDocker y dashboards tienen ajuste compatible preparado enD061,
**no desplegado en esta sesión**. Su primera aplicación requiere autorización y
backup/rollback coordinado de Prometheus/Grafana antes de activar el primer CT nativo.
Para los17 heredados, ausencia de esa marca conserva el comportamiento requerido.

## 7. Prometheus y Grafana

Consultar `up` del servicio nuevo; CPU LXC válida, MemTotal/Available, raíz,
timestamps, cAdvisor individual siDocker y probe_success de cada endpoint. Uptime
viene del exporterPVE existente porCTID y no necesita un agente nuevo ni listaVMID.

Fleet y Details usan inventario publicado y etiquetas; no editar JSON por cadaCT.
CTID/Service nuevos aparecen cuando se integran targets y expected-inventory.
Verificar una fila, sin duplicados, sin datos de otroCT, CTIDtransmitido entre vistas,
RAM/CPU/disco/unidades reales y UNKNOWN honestos si falta un contrato de aplicación.

## 8. Alertas y aceptación de la nueva fuente

Confirmar reglas aplicables, ausencia de alertas falsas y las severidades actuales.
Sin Docker no debe activarse LxcDockerMetricsMissing por diseño; no silenciar fallos
reales ni crear healthchecks ficticios. Mantener el perfil de observación aprobado
para el CT y detener avance ante anomalías. La integración Exporter→Prometheus→reglas
→Alertmanager→Telegram requiere ensayo/recepción según alcance aprobado para el alta,
no un POST directo ni contadoresAPI como recepción humana. No repetir el rollout17/17.

## 9. Notes, inventario y observación posterior

```sh
python3 scripts/new-lxc.py refresh-docs \
  --bundle "$PLAN_DIR" --receipt "$PLAN_DIR/verification.json"
```

Añade la observación fechada al candidato sin inventar aceptación continua. Copiar
solo la nueva declaración/ficha al repositorio, regenerar Notes y plan dirigido al
mismoCT. Para actualizar Notes de un CT ya creado, exigir que el plan cambie solo
su `description`, sin recursos/tags/apps; conservar el plan y lectura posterior.
Marcar aceptación/estado en `exporter-migration.yml` únicamente después de estabilidad,
segunda aplicación y cadena requeridas. No “DONE” por tener archivos locales.

## 10. Rollback si falla el alta

Antes de publicar monitorización, conservar backup y catálogos/modelos previos.
Revertir solo los fragmentos del CT nuevo y comprobar targets antiguos, reglas,
Prometheus/AM/Grafana; recarga controlada tras validar. Restaurar el provisioning
previo sin eliminar dashboards ni volumen. Detener solo sus exporters nuevos si
necesario. Conservar CT/volúmenes/apps/datos, imágenes y evidencias; no destroy ni
borrar discos automáticamente. Eliminación o cambio de recursos requiere aprobación
separada y verificación de datos/backups. Sin autorización, dejar el alta BLOCKED y
explicar qué gate falló. RPO/RTO/retención global quedan fuera del alcanceD061.

## 11. Estado de esta entrega

7.4 READY FOR FIRST REAL PROVISIONING TEST: flujo, artifacts, mocks, plan revisable,
Notes/fichas y compatibilidad preparados. Ningún nuevoCT ni servicio desplegado.
Primer ensayo real, acceso/plantilla/cgroups, idempotencia delbootstrap y aceptación
end-to-end siguen pendientes hasta que el propietario autorice un CT concreto.
[Estado y decisiones](../roadmap/CURRENT-STATUS.md).

Referencia primaria: [mocks de Terraform](https://developer.hashicorp.com/terraform/language/tests/mocking).
El mock sustituye al proveedor y no acredita una creación real ni las propiedades
de una plantilla concreta.
