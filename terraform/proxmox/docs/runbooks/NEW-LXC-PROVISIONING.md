# Alta de un LXC mediante IaC

Estado: **primer provisioning real CT627 PASS**, D063, 2026-11-10.
Los apartados D061/D062 conservan su contexto histórico; el alcance vigente de cada
intervención se consulta siempre en CURRENT-STATUS.
D063 probó un único CT real:627 Voicebox, con creación, SSH, aplicación ymonitorización.
Cada futura alta requiere autorización específica de identidad, IP/recursos/plantilla,
exporters y acceso exacto a sockets si usa Docker. No reutilizar el permiso627.

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

La preparación lee por defecto únicamente `~/.ssh/id_ed25519.pub`; otra fuente
pública se selecciona con `--ssh-public-key /ruta/propietario.pub`. Rechaza entradas
privadas y symlinks. La identidad privada permanece local y solo OpenSSH la utiliza
para firmar; una identidad cifrada debe estar disponible en el agente, sin prompts.

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
ni tocar DNS sin ese alcance. Verificar previamente la clave SSH de PVE en `~/.ssh/known_hosts`. El bootstrap
obtiene las claves públicas del host nuevo mediante ese canal confiable y `pct exec`,
y crea su propio `bundle/ssh/known_hosts`; nunca keyscan como prueba, checking=no
ni known_hosts=/dev/null. Requiere acceso root/pct ya autorizado en PVE y Python3
en la plantilla Debian/Ubuntu con systemd. No modifica la configuración SSH local.

Copiar únicamente la nueva declaración y su ficha del bundle al inventario real,
con revisión del diff. Conservar su bloque `provisioning.ssh.enabled: true`.
El `-var-file` privado vincula exclusivamente el servicio nuevo con su bootstrap.
No copiar su `.terraform`, estado ni todo el módulo sobre
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
  -var-file="$PLAN_DIR/terraform/ssh-bootstrap.auto.tfvars.json" \
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

El provisioner de creación ejecuta automáticamente el bootstrap SSH siguiente;
Terraform solo continúa tras su PASS. No ejecuta este paso en los CT existentes.
Después, verificar el nuevo CT por API/servidor: identidad, RUNNING, IP, recursos y rootfs.
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

## SSH automático del nuevo CT (D062)

El provider bpg/proxmox0.94.0 permite `initialization.user_account.keys`, incluso
al clonar. Estos campos son ForceNew. Proxmox sustituye el bloque PVE de claves
heredadas al recibir un conjunto nuevo; por eso el flujo de clones usa por defecto
una fusión aditiva mediante `pct exec`, antes de necesitar SSH en el contenedor.
La opción `lxc_ssh_public_keys` exige `provisioning.ssh.provider_key_set_complete: true`
y el conjunto completo revisado de claves legítimas de la plantilla; no activarla
sobre un CT ya creado ni suministrar solo una clave sin revisar las heredadas.

El controlador comprueba identidad/IP/RUNNING del CT elegido y excluye los17 IDs
actuales. Dentro del CT instala `openssh-server` si falta, genera sus host keys
localmente y añade la clave pública: `/root/.ssh`0700, `authorized_keys`0600,
propietario root. Conserva claves/opciones legítimas y elimina duplicados de la
misma clave con iguales opciones. Si una clave existente tiene restricciones que
impiden el acceso, bloquea el alta en lugar de eliminarlas.

Primero habilita clave pública manteniendo los métodos de contraseña efectivos
existentes. Valida `sshd -t`, recarga/inicia `ssh.service` y comprueba por SSH estricto:
`ssh -o BatchMode=yes -o PreferredAuthentications=publickey root@<IP> true`
(el controlador también fija identidad, host key, puerto22 y prohíbe fallback).
Solo tras ese PASS aplica la política final gestionada:

```text
PermitRootLogin prohibit-password
PasswordAuthentication no
KbdInteractiveAuthentication no
PubkeyAuthentication yes
```

Anteponer un Include exacto al archivo principal garantiza la precedencia global
de `/etc/ssh/sshd_config.d/00-lxc-bootstrap.conf`; no sustituye líneas mediante sed.
El resto de configuración se conserva. Comprueba sintaxis y valores efectivos con
`sshd -T -C` para la conexión root y repite la conexión por clave tras recargar.
Los Match incompatibles bloquean y restauran, no se reescriben indiscriminadamente.
`without-password` es el nombre normalizado equivalente de OpenSSH.

La configuración anterior y el estado quedan en `/var/lib/lxc-ssh-bootstrap/`0700
dentro del CT. Ante fallo de los gates restaura los archivos anteriores, valida y
recarga, conservando la clave añadida. Nunca toca contraseña ni consola Proxmox.
Si falla la propia restauración, detenerse y recuperar por consola; no destruir.
El recibo privado `bundle/ssh/verified.json` solo aparece después del acceso real.
Segunda aplicación DONE comprueba configuración/acceso, sin reescrituras ni recarga.
Docker no interviene en este bootstrap.

**Fallo del provisioner:** Terraform puede dejar el nuevo CT tainted. No repetir
apply automáticamente: un reemplazo destruiría el CT. Inspeccionar por consola/API,
conservarlo y sus datos, corregir la causa y reejecutar únicamente:

```sh
python3 scripts/bootstrap-new-lxc-ssh.py --execute --node pve \
  --config "$PLAN_DIR/ssh/bootstrap.json"
```

Tras PASS, revisar el estado Terraform y retirar la marca tainted exclusivamente
del CT recién creado (`terraform untaint` de su dirección exacta), con autorización
de recuperación y comprobación posterior del plan sin reemplazos. No ejecutar
destroy/recreate para resolver SSH. Una aplicación normal sin cambios no vuelve a
ejecutar el provisioner; la comprobación anterior permite revisar idempotencia.

Fuentes: [provider0.94.0](https://github.com/bpg/terraform-provider-proxmox/blob/v0.94.0/docs/resources/virtual_environment_container.md),
[implementación del provider](https://github.com/bpg/terraform-provider-proxmox/blob/v0.94.0/proxmoxtf/resource/container/container.go),
[gestión de claves Proxmox](https://github.com/proxmox/pve-container/blob/master/src/PVE/LXC/Setup/Base.pm),
[precedencia OpenSSH](https://man.openbsd.org/sshd_config).

## 10. Rollback si falla el alta

Antes de publicar monitorización, conservar backup y catálogos/modelos previos.
Revertir solo los fragmentos del CT nuevo y comprobar targets antiguos, reglas,
Prometheus/AM/Grafana; recarga controlada tras validar. Restaurar el provisioning
previo sin eliminar dashboards ni volumen. Detener solo sus exporters nuevos si
necesario. Conservar CT/volúmenes/apps/datos, imágenes y evidencias; no destroy ni
borrar discos automáticamente. Eliminación o cambio de recursos requiere aprobación
separada y verificación de datos/backups. Sin autorización, dejar el alta BLOCKED y
explicar qué gate falló. RPO/RTO/retención global quedan fuera del alcanceD061.

## 11. Estado de la entrega D061/D062 — histórico

7.4 READY FOR FIRST REAL PROVISIONING TEST: flujo, artifacts, mocks, plan revisable,
Notes/fichas y compatibilidad preparados. Ningún nuevoCT ni servicio desplegado.
Primer ensayo real, acceso/plantilla/cgroups, idempotencia delbootstrap y aceptación
end-to-end siguen pendientes hasta que el propietario autorice un CT concreto.
[Estado y decisiones](../roadmap/CURRENT-STATUS.md).

Referencia primaria: [mocks de Terraform](https://developer.hashicorp.com/terraform/language/tests/mocking).
El mock sustituye al proveedor y no acredita una creación real ni las propiedades
de una plantilla concreta.

## 12. Gate de capacidad observado en D063

Antes de reservar identidad o aplicar, contrastar API PVE con MemAvailable, swap,
presión de memoria y espacio del almacenamiento destino. MemFree o la suma de
límites LXC no bastan para acreditar margen. Un límite de8GiB no reserva RAM física;
no usar sobreasignación para eludir los requisitos del propietario.
[D063](../roadmap/PHASE7-D063-VOICEBOX.md): primer alta detenida por riesgo de
capacidad, sin creación real ni prueba de bootstrap.

## 13. Lecciones del primer alta real D063

[CT627 Voicebox](../roadmap/PHASE7-D063-VOICEBOX.md) creó1recurso sin alterar otros.
Comenzó con recursos reales de plantilla por instrucción del propietario; los
aumentos1080→1536→2048MiB se justificaron con saturación y margenRAM medidos.
Elprovider0.94 reinicia elCT al cambiar memoria; registrar esa interrupción del
servicio nuevo. Descripción/Notes solas no requieren reboot según código yensayo.

- Plantillas antiguas pueden contener hostkeysDSA. El selector ahora conserva los
  archivos y solo confía en tipos admitidos. Fallo deprovisioner no justifica destruir:
  se recuperó bootstrap porconsola, se verificó acceso ydespués se retiró taint solo627.
- La automatizaciónPVE añadeIP como tag ydevuelve orden estable. Solo las nuevas
  altasSSH normalizan esos tags enIaC; las expresiones legadas siguen intactas.
- Servicios nuevos observados necesitan Notes propias y estadoRUNNING enlazado a
  recibo; no mantener «no desplegado» después de una verificación real.
- Adoptar elcatálogo vivo antes de añadir targets: conservar etiquetas reales de los
  anteriores. El diffGit puede reflejar deriva anterior sin modificar targets vivos.
- Contenedores auxiliares sin servidor no deben heredar healthcheckHTTP de una
  imagen de aplicación. No confundir series antiguas con fallo permanente ni cambiar
  umbrales para esconderlas. Esperar/verificar su desaparición antes de aceptación.
- ReglasDockerLAN basadas en conntrack deben distinguir direcciónORIGINAL para
  no bloquear respuestas. Probar desde elcliente real además de loopback.
- BackupsHF contienen enlaces relativos internos. Restaurar con destinos confinados
  y hashes; nunca resolver errores delparser mediante extracción permisiva.
- Imagen exacta archivada ybloqueada porID/hash permite reproducir runtime aun
  cuando elDockerfileupstream conserva rangos de dependencias. No afirmar rebuild
  idéntico sin un lock completo y un ensayo independiente.

D063:16testsprovisioning/15inventarioPASS, segundaaplicación0/0/0, estabilidad600s/21,
web/API/TTS/persistencia/restoreaislado yGrafanadinámicoPASS. Las autorizaciones de
627 no seextienden aotrosCT, exposiciónWAN, pipeline ni fases7.2/7.3.
