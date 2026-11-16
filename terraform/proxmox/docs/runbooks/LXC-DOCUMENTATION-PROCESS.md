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
   Solo `terraform apply -parallelism=1 -target=proxmox_virtual_environment_container.svc["<service>"]`
   y **solo** tras el paso de validación del plan (§4 paso 6) y confirmación
   explícita del usuario.
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
- Confirmar con el usuario el CTID y que el modo es **CREAR** (no existe
  `docs/inventory/<CT>-LXC-INVENTORY.md`).

### Paso 2 — Lectura de estado real (SSH solo lectura)
Con el alias del CT (p. ej. `infra-pulpo`), comandos **solo lectura**:

```sh
ssh infra-pulpo 'pct status 619; pct config 619 | grep -E "hostname|cores|memory|rootfs|net0|tags"'
ssh infra-pulpo 'docker ps --format "{{.Names}}\t{{.Status}}\t{{.Ports}}"'
ssh infra-pulpo 'docker inspect --format "{{.Config.Image}}" <container>'
ssh infra-pulpo 'cat /opt/<app>/docker-compose.yml'   # o la ruta real del compose
ssh infra-pulpo 'df -h; free -h'
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

### Paso 6 — Regenerar artefactos
```sh
python3 scripts/generate-lxc-inventory.py
```
Escribe `lxc-notes.json`, `lxc-notes-manifest.json` y `LXC-INVENTORY.md`.
Si falla, es un error de esquema/identidad/secreto: corregir la fuente y
repetir. No se "arregla" editando la salida.

### Paso 7 — Verificar frescura
```sh
python3 scripts/generate-lxc-inventory.py --check
```
Debe imprimir `PASS: ... freshness`. Si dice `Stale generated file`, hay
fuentes que cambiaron tras el paso 6: regenerar de nuevo.

### Paso 8 — Plan Terraform (target)
```sh
terraform plan -parallelism=1 \
  -target=proxmox_virtual_environment_container.svc["<service>"] \
  -out=/tmp/lxc-docs-<service>.plan.json
```
El precondition de Notes-fresh debe pasar (si no, volver al paso 6).

### Paso 9 — Validar que el plan es SOLO `description`
```sh
python3 scripts/validate-lxc-notes-plan.py /tmp/lxc-docs-<service>.plan.json \
  --report /tmp/lxc-docs-<service>.report.json --service <service>
```
- `result: PASS` / `apply_permitted: true` → continuar.
- `result: BLOCKED` → **PARAR** (regla de seguridad §2.4). Revisar
  `report.json`, corregir y repetir desde el paso 8.

### Paso 10 — Confirmación del usuario (STOP)
Mostrar el diff del plan (solo `description` del CT) y **pedir confirmación
explícita** antes de aplicar. Sin confirmación, no aplicar.

### Paso 11 — Aplicar (target)
```sh
terraform apply -parallelism=1 \
  -target=proxmox_virtual_environment_container.svc["<service>"] \
  /tmp/lxc-docs-<service>.plan.json
```

### Paso 12 — Verificar en producción (SSH solo lectura)
```sh
ssh infra-pulpo 'pct config 619 | grep -A2 description'   # o pct list / API
```
Confirmar que la `description` del CT coincide con el título/cuerpo de
`NOTES.md`. Confirmar que **no** cambió nada más (tags, recursos).

### Paso 13 — Cerrar
- `git diff --check` y revisar el diff (solo los 4 artefactos + fuentes).
- Actualizar `docs/roadmap/CURRENT-STATUS.md` (estado, evidencia, fecha
  Europe/Madrid).
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

### Paso 3 — Regenerar
```sh
python3 scripts/generate-lxc-inventory.py
python3 scripts/generate-lxc-inventory.py --check
```

### Paso 4 — Plan + validar (solo `description`)
```sh
terraform plan -parallelism=1 \
  -target=proxmox_virtual_environment_container.svc["<service>"] \
  -out=/tmp/lxc-docs-<service>.plan.json
python3 scripts/validate-lxc-notes-plan.py /tmp/lxc-docs-<service>.plan.json \
  --report /tmp/lxc-docs-<service>.report.json --service <service>
```
`PASS` obligatorio. `BLOCKED` → parar y diagnosticar.

### Paso 5 — Confirmación del usuario (STOP)
Mostrar diff del plan y pedir confirmación explícita.

### Paso 6 — Aplicar (target) + verificar
Igual que MODO CREAR pasos 11–12.

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

## 6. Comandos de referencia (resumen)

```sh
# Regenerar artefactos generados
python3 scripts/generate-lxc-inventory.py
# Verificar frescura (no escribe)
python3 scripts/generate-lxc-inventory.py --check
# Plan acotado al CT
terraform plan -parallelism=1 \
  -target=proxmox_virtual_environment_container.svc["<service>"] \
  -out=/tmp/lxc-docs-<service>.plan.json
# Validar que el plan es solo description
python3 scripts/validate-lxc-notes-plan.py /tmp/lxc-docs-<service>.plan.json \
  --report /tmp/lxc-docs-<service>.report.json --service <service>
# Aplicar (tras confirmación del usuario)
terraform apply -parallelism=1 \
  -target=proxmox_virtual_environment_container.svc["<service>"] \
  /tmp/lxc-docs-<service>.plan.json
```

`<service>` es el nombre del archivo del inventario sin extensión
(`infra-pulpo`, `infra-excraper`). `<CT>` es el `vmid` (619, 620).
