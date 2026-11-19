# 18 — Ruteo de workflows: keywords de documentación de LXC

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
2. **STOP obligatorio** antes de `terraform apply`: confirmación explícita del
   usuario. Nunca aplicar sin ella.
3. **STOP** ante `BLOCKED` de `validate-lxc-notes-plan.py` o ante un plan que
   no sea solo `description`.
4. SSH al CT **solo lectura**; SSH estricto
   (`UserKnownHostsFile=$HOME/.ssh/known_hosts`, `StrictHostKeyChecking=yes`,
   `BatchMode=yes`).
5. Aplicar únicamente el binario acotado, validado y autorizado según §6 del runbook.
6. Deducir CREAR/ACTUALIZAR de la existencia de la ficha. Preguntar si
   falta la identidad o hay más de una coincidencia.

### Ejemplos de invocación

- "documentar CT621" → dispara `lxc-docs.md` → elegir modo según existencia de la ficha.
- "actualizar la ficha de infra-pulpo" → MODO ACTUALIZAR.
- "sincronizar Notes de infra-excraper" → regenerar + plan + validar + STOP.
