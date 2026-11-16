# 16 — Ruteo de workflows: keywords de swap de LXC

## Regla principal

Cuando la petición del usuario coincida con los disparadores de un workflow
de `.clinerules/workflows/`, **leer ese workflow y seguirlo** en lugar de
improvisar. El workflow referencia el runbook correspondiente; no duplicar
pasos.

## Mapa keyword → workflow

| Disparador (español) | Workflow | Runbook |
|---|---|---|
| "aumentar swap de <service>", "subir swap CT<id>" | `.clinerules/workflows/lxc-swap.md` | `docs/runbooks/LXC-SWAP-INCREASE.md` |
| "swap alert <service>", "alerta de swap <service>" | `.clinerules/workflows/lxc-swap.md` | `docs/runbooks/LXC-SWAP-INCREASE.md` |
| "aumentar swap", "swap increase" | `.clinerules/workflows/lxc-swap.md` | `docs/runbooks/LXC-SWAP-INCREASE.md` |

## Reglas

1. Antes de ejecutar, leer el workflow y las secciones 1–4 del runbook.
2. **STOP obligatorio** antes de `terraform apply`: confirmación explícita del
   usuario. Nunca aplicar sin ella.
3. **STOP** si `next-swap-step.py` devuelve `AT_MAX` o `BLOCKED`, o si el plan
   muestra cualquier cambio que no sea el `swap` del CT objetivo.
4. SSH al CT **solo lectura**; SSH estricto
   (`UserKnownHostsFile=$HOME/.ssh/known_hosts`, `StrictHostKeyChecking=yes`,
   `BatchMode=yes`).
5. Solo `terraform apply -parallelism=1 -target=proxmox_virtual_environment_container.svc["<service>"]`.
   Nunca `apply` general ni `make deploy-all`.
6. El swap se aplica en caliente; no reiniciar el CT.
7. Si falta `<service>`/`<CT>` o el objetivo es ambiguo, preguntar antes de
   ejecutar.
8. No hacer commit/push salvo autorización explícita.

### Ejemplos de invocación

- "aumentar swap de infra-webui" → dispara `lxc-swap.md` → CT 631.
- "swap alert CT627" → `lxc-swap.md` → resolver servicio por vmid 627.
- "subir swap CT631" → `lxc-swap.md` → diagnóstico + cálculo + plan + STOP.
