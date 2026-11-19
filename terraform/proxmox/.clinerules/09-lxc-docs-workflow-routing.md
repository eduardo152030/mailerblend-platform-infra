# 09 — Ruteo de workflows: keywords de documentación de LXC

## Regla principal

Cuando la petición del usuario coincida con los disparadores de un workflow
de `.clinerules/workflows/`, **leer ese workflow y seguirlo** en lugar de
improvisar. El workflow referencia el runbook correspondiente; no duplicar
pasos.

## Mapa keyword → workflow

| Disparador (español) | Workflow | Runbook |
|---|---|---|
| "documentar CT<id>", "documentar <service>" | `.clinerules/workflows/lxc-docs.md` | `docs/runbooks/LXC-DOCUMENTATION-PROCESS.md` |
| "crear ficha de <service>", "crear ficha CT<id>" | `.clinerules/workflows/lxc-docs.md` | `docs/runbooks/LXC-DOCUMENTATION-PROCESS.md` |
| "actualizar la ficha de <service>" | `.clinerules/workflows/lxc-docs.md` | `docs/runbooks/LXC-DOCUMENTATION-PROCESS.md` |
| "sincronizar Notes de <service>" | `.clinerules/workflows/lxc-docs.md` | `docs/runbooks/LXC-DOCUMENTATION-PROCESS.md` |

## Reglas

1. Antes de ejecutar, leer el workflow y las secciones 1–2 del runbook.
2. **Documentar, crear ficha y actualizar ficha** terminan con el cierre
   documental local. Completa las comprobaciones y entrega el resumen sin
   pedir confirmación ni ejecutar Terraform.
3. Para una solicitud de **sincronizar Notes en PVE**, sigue §6 del
   runbook. Si el validador devuelve `BLOCKED`, reporta el motivo y detén
   la sincronización.
4. SSH al CT **solo lectura**; SSH estricto
   (`UserKnownHostsFile=$HOME/.ssh/known_hosts`, `StrictHostKeyChecking=yes`,
   `BatchMode=yes`).
5. Aplicar únicamente el binario acotado, validado y autorizado según §6 del runbook.
6. Deducir CREAR/ACTUALIZAR de la existencia de la ficha. Preguntar si
   falta la identidad o hay más de una coincidencia.

### Ejemplos de invocación

- "documentar CT621" → dispara `lxc-docs.md` → elegir modo según existencia de la ficha.
- "actualizar la ficha de infra-pulpo" → MODO ACTUALIZAR.
- "sincronizar Notes de infra-excraper" → seguir §6 del runbook.
