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
  documentación.
- **MODO ACTUALIZAR** — el CT ya está documentado; cambió su estado,
  recursos, apps o decisiones. Se regeneran los artefactos documentales.

El workflow de Cline (`.clinerules/workflows/lxc-docs.md`) orquesta este
runbook. **No duplica sus pasos**: los referencia.

## Cierre documental

Si el encargo indica «solo documentación», recoge los datos en
modo lectura, actualiza las fuentes según CREAR o ACTUALIZAR y documenta las
etiquetas observadas. Al alinear el YAML con las etiquetas verificadas,
conserva las existentes, incluida la etiqueta IP de CT611.

```bash
python3 scripts/generate-lxc-inventory.py
python3 scripts/generate-lxc-inventory.py --check
python3 -m unittest discover -s tests/inventory -q
git diff --check
```

Revisa el diff y las referencias de ficha, Notes e inventario. Registra el
resultado documental según §3 paso 13 y entrega el resumen sin pedir
confirmación. Este cierre se completa sin Terraform ni cambios en Proxmox.
Para el workflow completo, continúa con la sincronización de §6.

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

1. **Lecturas por SSH.** En el nodo PVE se ejecutan `pvesh`, `pct status`
   y `pct config`. Dentro del CT se ejecutan `hostname`, `df`, `free`
   y consultas de Docker. Usar la ruta de §3 paso 2 también en ACTUALIZAR.
2. **SSH estricto desde el primer intento.** Usar
   `UserKnownHostsFile=$HOME/.ssh/known_hosts`, `StrictHostKeyChecking=yes`
   y `BatchMode=yes`. Si falla la clave del alias del CT, usar un nodo PVE
   ya verificado y `pct exec` para las consultas internas. Si PVE tampoco
   se puede verificar, detener las lecturas remotas y reportar el bloqueo.
   Mantener la verificación activa, sin `keyscan` como prueba de identidad
   ni cambios en la configuración SSH del propietario.
3. **Nunca `terraform apply` general ni `make apply`/`make deploy-all`.**
   Aplicar únicamente el binario guardado, acotado y validado según §6.
4. **Regla de parada del plan.** Para el CT objetivo se admite la descripción
   generada y la reordenación de las mismas etiquetas. Las altas y bajas
   de etiquetas, cambios de recursos y cambios de otros CT bloquean la
   aplicación. `validate-lxc-notes-plan.py` verifica el alcance.
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

**Primero, PVE.** El alias habitual del nodo es `pve`. Confirma el nodo
propietario del VMID en el clúster si hay varios nodos. Ejecuta `pct` solo
en ese nodo. Ejemplo para CT611:

```bash
ssh -o UserKnownHostsFile="$HOME/.ssh/known_hosts" -o StrictHostKeyChecking=yes -o BatchMode=yes pve \
  'pct status 611 && pct config 611 | grep -E "^(hostname|cores|memory|swap|rootfs|net0|tags):"'
```

**Después, dentro del CT.** El propietario suele conectarse con
`ssh infra-grafana`. Para automatizar la lectura, prueba el alias con SSH
estricto. El alias del CT abre el sistema invitado, donde `pct` no existe.

```bash
ssh -o UserKnownHostsFile="$HOME/.ssh/known_hosts" -o StrictHostKeyChecking=yes -o BatchMode=yes infra-grafana hostname
```

Si el hostname coincide, usa ese acceso para las lecturas internas. Si la
clave del alias no está verificada, usa el nodo PVE ya verificado para esas
mismas lecturas. Este ejemplo se probó con CT611:

```bash
ssh -o UserKnownHostsFile="$HOME/.ssh/known_hosts" -o StrictHostKeyChecking=yes -o BatchMode=yes pve \
  'pct exec 611 -- sh -c '"'"'hostname; df -h /; free -m; sed -n "/^PRETTY_NAME=/p" /etc/os-release; if command -v docker >/dev/null 2>&1; then docker ps -a --format "{{.Names}} | {{.Image}} | {{.Status}} | {{.Ports}}"; else printf "Docker CLI no encontrada\n"; fi'"'"''
```

Sustituye VMID y alias por los del CT solicitado. Si el CT está parado,
registra ese estado y omite las lecturas internas. Registra por separado
un fallo de SSH, un error de Docker y la ausencia de la CLI. Evita agrupar
todo bajo `|| echo "no docker"`. Documenta valores observados y conserva
como pendientes los datos que falten. Para inspeccionar Docker, limita
la salida a los campos necesarios, sin volcar el entorno.

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

### Pasos 10–11 — Aplicar

Seguir §6.2 con el plan binario validado.

### Paso 12 — Verificar en producción

Leer `/nodes/<node>/lxc/<CT>/config` con `pvesh get` en el nodo PVE vía SSH
estricto y `--output-format json`. Comparar el campo `description` completo
con la salida del generador (título, cuerpo y salto final). Antes de aplicar,
guardar una copia privada de la configuración PVE. Después, comparar el resto
de campos excluyendo `description`, `tags` y `digest`. Comprobar que las
etiquetas coinciden con las anteriores al aplicar, independientemente del orden. Comunicar los resultados de las
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

> Si cambian recursos o se añaden o quitan etiquetas, el validador marca
> `BLOCKED`. Una reordenación de las mismas etiquetas puede acompañar a
> las Notes del CT en un plan acotado.

### Pasos 3–4 — Regenerar, probar y validar el plan

Ejecutar §6.1.

### Pasos 5–6 — Aplicar y verificar

Seguir §6.2 y verificar según §3 paso 12. Con un plan sin cambios, verificar
directamente la descripción real y cerrar solamente si coincide.

### Paso 7 — Cerrar
Igual que MODO CREAR paso 13.

---

## 5. Troubleshooting

### 5.1 Diferencias en `tags`

El plan acotado admite cambiar el orden cuando las etiquetas coinciden antes
y después, incluida su multiplicidad. Si el plan modifica el contenido,
revisa el inventario observado y corrige la fuente dentro del encargo. El
plan histórico de CT611 proponía eliminar `192.168.1.111`. La etiqueta
existente se declaró en su YAML para conservarla.

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

Desde `terraform/proxmox`, ejecuta este comando en una llamada y sustituye
`infra-grafana` por la clave exacta del servicio.

```bash
bash scripts/prepare-lxc-notes-plan.sh infra-grafana
```

El script regenera, prueba y valida. Obtiene la CA desde `pve` por SSH
estricto y crea el plan acotado con TLS verificado. Requiere el Terraform
inicializado y las credenciales locales vigentes. Conserva CA, binario,
JSON, informe y registros en un directorio privado cuya ruta imprime.

Comparte únicamente el informe seguro y un resumen de la nota. Ante un
fallo, comunica la etapa indicada y detente. Si necesitas revisar un
registro privado, extrae solo la causa sin credenciales. El comando no
aplica cambios. `PASS` con `changes: []` exige verificar la nota real
antes de cerrar. Con cambios permitidos, continúa en §6.2.

### 6.2 — Aplicar el plan guardado

El workflow completo autoriza sincronizar el CT identificado con un informe
`PASS`. Continúa automáticamente cuando haya cambios validados y se haya
guardado la copia previa privada del paso 12. Si el plan o sus fuentes
cambian, genera y valida uno nuevo según §6.1. Aplica el mismo binario
guardado con la CA privada, usando como `notes_dir` el directorio indicado
por el script.

```sh
SSL_CERT_FILE="$notes_dir/pve-ca.pem" terraform apply -input=false -parallelism=1 "$notes_dir/notes.tfplan"
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
