# Documentación de un LXC (ficha + Notes) mediante IaC

Estado: **proceso estandarizado** derivado del alta documental real de
CT619 (infra-pulpo) y CT620 (infra-excraper), 2026-11-15.

Este runbook convierte el flujo manual de "documentar un CT" en un
procedimiento reproducible. **La fuente de verdad de cada paso son los
scripts y el inventario declarativo**, no este documento: si un comando de
aquí no coincide con `scripts/` o `inventory/`, gana el código.

Dos modos:

- **MODO CREAR** — el CT ya existe en producción pero no tiene ficha
  (`docs/inventory/<CT>-LXC-INVENTORY.md`) ni `NOTES.md`. Se crea la
  documentación y se sincronizan las Notes de Proxmox.
- **MODO ACTUALIZAR** — el CT ya está documentado; cambió su estado,
  recursos, apps o decisiones. Se regeneran los artefactos y se re-sincronizan
  las Notes.

El workflow de Cline (`.clinerules/workflows/lxc-docs.md`) orquesta este
runbook. **No duplica sus pasos**: los referencia.

---

## 1. Modelo de datos (qué es la "fuente de verdad")

Un CT se documenta con **tres artefactos por servicio**, todos versionados:

| Artefacto | Ruta | Rol |
|---|---|---|
| Declaración | `inventory/services/<service>.yml` | Identidad, recursos, tags y el bloque `documentation:` que enlaza los dos archivos de abajo. |
| Notes (fuente) | `services/<service>/NOTES.md` | Texto libre de las Notes de Proxmox. El **primer título** (`# ...`) es el título de la nota; el resto es el cuerpo. |
| Ficha (fuente) | `docs/inventory/<CT>-LXC-INVENTORY.md` | Ficha larga del CT (estado, decisiones, operación, backup/rollback). |

El bloque `documentation:` de la declaración es el único cableado por
servicio (patrón real de 619/620):

```yaml
documentation:
  notes_file: services/infra-pulpo/NOTES.md
  inventory_file: docs/inventory/619-LXC-INVENTORY.md
```

A partir de ahí, **todo lo demás es generado** por
`scripts/generate-lxc-inventory.py` y **no se edita a mano**:

- `inventory/generated/lxc-notes.json` — mapa `service → {title, sections}`.
- `inventory/generated/lxc-notes-manifest.json` — sha256 de todas las fuentes.
- `docs/inventory/LXC-INVENTORY.md` — tabla resumen + detalle por CT.

Cadena de datos (ver `inventory.tf` y `main.tf`):

```
NOTES.md ─┐
ficha ────┤  generate-lxc-inventory.py
*.yml ────┤  ─────────────────────────────► lxc-notes.json ─► lxc_descriptions
observed ─┘                                     (templatefile lxc-notes.tftpl)
                                                 └► resource svc.description
```

`main.tf` fija `description = local.lxc_descriptions[each.key]` y tiene un
**precondition** que bloquea cualquier `plan`/`apply` si las Notes están
stale o incompletas:

```
"LXC notes are stale or incomplete. Run python3 scripts/generate-lxc-inventory.py
 and review all service records."
```

Por eso **regenerar antes de planear es obligatorio**, no opcional.

> Nota: los CT "legacy" (sin bloque `documentation:`, p. ej. infra-blackbox,
> infra-grafana) obtienen sus Notes de `inventory/documentation.yml`
> (metadatos `META_FIELDS`). Este runbook cubre el flujo **con** `documentation:`
> (619/620 y nuevos). No mezclar ambos para el mismo CT.

---

## 2. Reglas de seguridad (aplican a AMBOS modos)

1. **Acceso al CT solo lectura.** SSH a `infra-pulpo` / `infra-excraper`
   (o el alias del CT) **solo** para leer estado: `pct status`, `pct config`,
   `docker ps`, `docker inspect`, `cat` de compose, `df`, `free`. **Nunca**
   `pct start/stop/restart/destroy`, `docker down -v`, `prune`, `rm`, ni
   escritura de configuración.
2. **SSH estricto.** Usar siempre `UserKnownHostsFile=$HOME/.ssh/known_hosts`,
   `StrictHostKeyChecking=yes`, `BatchMode=yes`. No aceptar `keyscan` como
   verificación de identidad. (Ver D-025 reanudado.)
3. **Nunca `terraform apply` general ni `make apply`/`make deploy-all`.**
   Aplicar únicamente el binario acotado y validado según §6, tras
   confirmación explícita del usuario.
4. **Regla de parada del plan.** Si el plan muestra **cualquier** cambio que
   no sea `description` del CT objetivo (tags, memory, cpu, disk, start_on_boot,
   otro recurso, otro CT) → **PARAR**. No aplicar. Reportar el diff y pedir
   autorización. `validate-lxc-notes-plan.py` automatiza esta comprobación.
5. **No editar artefactos generados a mano.** `lxc-notes.json`,
   `lxc-notes-manifest.json` y `LXC-INVENTORY.md` se regeneran. Editar la
   fuente (`NOTES.md`, ficha, `.yml`) y volver a generar.
6. **Sin secretos.** El inventario y las Notes no llevan contraseñas, tokens,
   URLs con autenticación ni claves. `generate-lxc-inventory.py` falla en
   cerrado (`assert_public`) si detecta patrones de secreto.
7. **Preservar datos.** Este flujo no toca volúmenes, imágenes ni backups.
   Si una condición de seguridad falla, detener el paso dependiente y
   explicar el bloqueo.

---

## 3. MODO CREAR (ficha nueva para un CT ya desplegado)

Precondición: el CT existe en producción y ya está declarado en
`inventory/services/<service>.yml` (identidad, recursos, tags). Si no está
declarado, primero hacer el alta de IaC (`docs/runbooks/NEW-LXC-PROVISIONING.md`);
este runbook solo documenta.

### Paso 1 — Confirmar identidad y alcance
- `inventory/services/<service>.yml`: `service.vmid`, `service.name`, `service.ip`.
- Confirmar el CTID en el inventario y elegir **CREAR** si falta
  `docs/inventory/<CT>-LXC-INVENTORY.md`.

### Paso 2 — Lectura de estado real (SSH solo lectura)
Con el alias del CT (p. ej. `infra-pulpo`), comandos **solo lectura**:

```sh
ssh -o UserKnownHostsFile="$HOME/.ssh/known_hosts" -o StrictHostKeyChecking=yes -o BatchMode=yes pve \
  'pct status 619; pct config 619 | grep -E "^(hostname|cores|memory|rootfs|net0|tags):"'
ssh -o UserKnownHostsFile="$HOME/.ssh/known_hosts" -o StrictHostKeyChecking=yes -o BatchMode=yes infra-pulpo 'docker ps --format "{{.Names}}\t{{.Status}}\t{{.Ports}}"'
ssh -o UserKnownHostsFile="$HOME/.ssh/known_hosts" -o StrictHostKeyChecking=yes -o BatchMode=yes infra-pulpo 'docker inspect --format "{{.Config.Image}}" <container>'
ssh -o UserKnownHostsFile="$HOME/.ssh/known_hosts" -o StrictHostKeyChecking=yes -o BatchMode=yes infra-pulpo 'df -h; free -h'
```

Registrar: estado RUNNING, hostname, CPU/RAM/rootfs reales, contenedores
activos, puertos, imágenes, compose activo. **No ejecutar nada mutante.**

### Paso 3 — Crear la ficha
Crear `docs/inventory/<CT>-LXC-INVENTORY.md` con el estado observado,
función, operación, backup/rollback y enlaces a informes. Estilo y secciones
de referencia: `docs/inventory/627-LXC-INVENTORY.md`.

### Paso 4 — Crear las Notes
Crear `services/<service>/NOTES.md`. **Formato obligatorio** (lo exige el
generador):

- Primera línea: `# CT <CT> — <service>` (título de la nota).
- Una línea en blanco.
- Cuerpo: secciones en Markdown. El generador toma el primer `\n\n` como
  separador título/cuerpo y el resto como una sola sección.

Referencia de estilo: `services/infra-voicebox/NOTES.md` (secciones
`**D0xx — ...:**` fechadas, más densas que la ficha).

### Paso 5 — Cablear el bloque `documentation:`
Añadir al `inventory/services/<service>.yml`:

```yaml
documentation:
  notes_file: services/<service>/NOTES.md
  inventory_file: docs/inventory/<CT>-LXC-INVENTORY.md
```

### Pasos 6–9 — Regenerar, probar y validar el plan

Ejecutar §6.1. Si el informe devuelve `BLOCKED`, detener la aplicación y
registrar los campos que bloquean el plan. Si devuelve `PASS` sin cambios,
pasar directamente a la verificación en producción.

### Pasos 10–11 — Confirmar y aplicar

Seguir §6.2 con el plan binario validado.

### Paso 12 — Verificar en producción

Leer `/nodes/<node>/lxc/<CT>/config` con `pvesh get` en el nodo PVE vía SSH
estricto y `--output-format json`. Comparar el campo `description` completo
con la salida del generador (título, cuerpo y salto final). Antes de aplicar,
guardar una copia privada de la configuración PVE. Después, comparar el resto
de campos excluyendo `description` y `digest`. Comunicar los resultados de las
comparaciones sin mostrar la configuración completa. Volver a planear con el
mismo alcance y exigir cero cambios. Si hay diferencias, registrar el bloqueo.

### Paso 13 — Cerrar
- `git diff --check` y revisar el diff (solo los 4 artefactos + fuentes).
- Actualizar el documento de fase, `ROADMAP.md` y `CURRENT-STATUS.md`
  (estado, evidencia, fecha Europe/Madrid y siguiente paso).
- Registrar decisión en `docs/roadmap/DECISIONS.md` si aplica.
- **No** commit/push salvo autorización explícita.


---

## 4. MODO ACTUALIZAR (CT ya documentado)

### Paso 1 — Detectar el cambio
- ¿Qué cambió? (estado, recursos, apps, decisión, dominio, backup.)
- Identificar la fuente a editar: `NOTES.md` (Notes), ficha (detalle largo)
  o `.yml` (recursos/tags/identidad).

### Paso 2 — Editar SOLO la fuente
- Notas/decisiones → `services/<service>/NOTES.md` (añadir sección `**D0xx — ...:**`
  al inicio, conservar el histórico).
- Ficha → `docs/inventory/<CT>-LXC-INVENTORY.md`.
- Recursos/identidad → `inventory/services/<service>.yml`.

> Si cambian **recursos** (cpu/memory/disk) o **tags**, el plan ya NO será
> solo `description`. En ese caso el flujo de Notes no cubre el cambio:
> requiere autorización de recursos aparte y `validate-lxc-notes-plan.py`
> marcará `BLOCKED`. Separar la actualización documental del cambio de
> recursos.

### Pasos 3–4 — Regenerar, probar y validar el plan

Ejecutar §6.1.

### Pasos 5–6 — Confirmar, aplicar y verificar

Seguir §6.2 y verificar según §3 paso 12. Con un plan sin cambios, verificar
directamente la descripción real y cerrar solamente si coincide.

### Paso 7 — Cerrar
Igual que MODO CREAR paso 13.

---

## 5. Troubleshooting

### 5.1 Drift de `tags` (caso real 619/620)
**Síntoma:** el plan muestra un cambio en `tags` además de `description`, y
`validate-lxc-notes-plan.py` devuelve `BLOCKED` ("Change is not
description-only").

**Causa:** `main.tf` añade la IP al array de tags y devuelve los tags
**ordenados** (`sort(distinct(concat(tags, [ip])))`) para CTs con
`provisioning.ssh.enabled`. Si el `.yml` declara los tags sin la IP o en otro
orden, Terraform ve un cambio de `tags` aunque el contenido sea equivalente.

**Solución:** alinear el array `tags` del `.yml` con el orden que PVE
devolverá (orden alfabético, IP incluida). Ejemplo real de 619:

```yaml
tags:
  - 192.168.1.119
  - automation
  - internal
  - n8n
  - parte_linkedin_stealth_sourcing
  - server
```

Tras alinear, regenerar y re-planear: el plan debe quedar **solo**
`description`. No forzar el apply con `tags` en el diff.

### 5.2 Precondition "LXC notes are stale or incomplete"
**Causa:** `lxc-notes-manifest.json` no coincide con los hashes de las
fuentes (se editó una fuente sin regenerar, o se editó un artefacto
generado a mano).

**Solución:** `python3 scripts/generate-lxc-inventory.py` y luego `--check`.
Nunca editar `lxc-notes.json` / `lxc-notes-manifest.json` a mano.

### 5.3 "Invalid Notes source" / "Notes must start with a Markdown title"
**Causa:** `NOTES.md` no empieza por `# ` o no tiene un `\n\n` separando
título y cuerpo, o la ruta de `notes_file` apunta fuera del repo.

**Solución:** primera línea `# CT <CT> — <service>`, línea en blanco, cuerpo.
Comprobar que `notes_file` es relativa al repo y existe.

### 5.4 "Potential secret detected (value withheld)"
**Causa:** una fuente contiene un patrón de secreto (password=, token, URL
con `user:pass@`, private key, `ghp_...`).

**Solución:** eliminar el valor de la fuente. El error no revela el valor;
buscar el patrón en `NOTES.md`, ficha y `.yml`.

### 5.5 "Identity mismatch"
**Causa:** `service.ip`/`service.name` del `.yml` no coinciden con
`lxc-observed.json` (net0/hostname).

**Solución:** verificar el estado real por SSH (solo lectura) y alinear la
declaración con la realidad. No forzar.

---

## 6. Plan y aplicación de Notes

### 6.1 — Generar, guardar y validar

Ejecutar desde `terraform/proxmox`. Usar las credenciales existentes y una CA
PVE confiable. Mantener el plan binario y su JSON en un directorio privado:
ambos pueden contener credenciales. Compartir únicamente el informe del
validador y el resumen de los cambios de la nota.

```sh
set -eu
service=infra-prom  # Sustituir por la clave exacta del inventario
target="proxmox_virtual_environment_container.svc[\"$service\"]"
umask 077
notes_dir=$(mktemp -d)

python3 scripts/generate-lxc-inventory.py
python3 scripts/generate-lxc-inventory.py --check
python3 -m unittest discover -s tests/inventory -q
terraform validate
terraform plan -input=false -parallelism=1 -var=proxmox_tls_insecure=false \
  -target="$target" -out="$notes_dir/notes.tfplan" > "$notes_dir/plan.log" 2>&1
terraform show -json "$notes_dir/notes.tfplan" > "$notes_dir/plan.json"
python3 scripts/validate-lxc-notes-plan.py "$notes_dir/plan.json" \
  --report "$notes_dir/report.json" --service "$service"
```

Ante un fallo, consultar los archivos privados y comunicar solo la causa y los
campos seguros. `PASS` con `changes: []` exige verificar la nota real antes de
cerrar. `PASS` con un cambio en `description` habilita el paso de confirmación.

### 6.2 — Confirmar y aplicar el plan guardado

Mostrar el CT, el resumen de la nota y los campos validados. Esperar confirmación
explícita para aplicar ese plan. Si cambian el plan o las fuentes, repetir §6.1
y mostrar el nuevo resultado. Con la confirmación y la copia previa privada
del paso 12, usar el mismo binario, con el mismo acceso TLS.

```sh
terraform apply -input=false -parallelism=1 "$notes_dir/notes.tfplan"
```

Verificar según §3 paso 12. Registrar por separado ficha generada, plan validado,
aplicación y verificación en PVE.

## 7. Ejemplo ejecutado — CT610, 19/11/2026

`documentar CT610` resolvió la clave `infra-prom`. La ficha ya existía, por lo
que se siguió **ACTUALIZAR**. Se comprobó el disco de 25 GiB y los componentes
activos en PVE y Docker. Se corrigieron la ficha, las Notes y sus referencias
en el YAML. La regeneración modificó únicamente las Notes de ese servicio.

El primer plan propuso quitar la etiqueta IP existente y devolvió `BLOCKED`.
Se declaró la etiqueta observada en el YAML. El nuevo plan conservó las
etiquetas y devolvió `PASS` con una sola actualización en `description`.
Tras autorización del propietario, se aplicó ese binario guardado. La API
PVE devolvió la misma nota byte por byte y el resto de la configuración
coincidió con la copia previa (excluido `digest`). Un segundo plan acotado
confirmó cero cambios.

La misma secuencia sirve para otro VMID o clave del inventario. Si la ficha
falta, usar CREAR. Si ya existe y las fuentes están vigentes, «sincronizar
Notes» puede empezar en §6.1. Cada aplicación usa el plan validado para el CT
solicitado y la autorización correspondiente.

- [Ficha CT610](../inventory/610-LXC-INVENTORY.md)
- [Notes de infra-prom](../../services/infra-prom/NOTES.md)
- [Estado y evidencia de cierre](../roadmap/CURRENT-STATUS.md)
