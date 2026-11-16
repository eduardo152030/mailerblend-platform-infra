# 03 — Flujo Git por tarea

Cada tarea del repositorio empieza en un **worktree dedicado y una rama propia**.
Esto aplica aunque solo haya una IA trabajando y aunque la tarea consista
únicamente en preparar un plan.

## 1. Abrir o retomar el worktree

Antes de editar, ejecuta:

```bash
git rev-parse --show-toplevel
git rev-parse --show-prefix
git worktree list
git status --short --branch --untracked-files=all
```

- **Tarea nueva.** Crea una rama y un worktree para la tarea desde `main` local,
  salvo que el usuario indique otra base o que el plan dependa de otra rama
  confirmada. Usa una ruta fuera del árbol de trabajo existente.
- **Tarea en curso.** Reutiliza el worktree y la rama ya asignados. Revisa
  el estado de Git y el último paso registrado en el plan antes de seguir.
- Conserva los cambios que encuentres en otros worktrees. Si la tarea depende
  de cambios pendientes de otra rama, identifica la dependencia y acuerda
  cómo integrarla antes de incorporarla.

Ejemplo para la tarea de swap del CT618, ejecutado desde la raíz Git:

```bash
git worktree add -b ops/ct618-swap \
  ../mailerblend-platform-infra-ct618-swap main
```

Confirma la ruta y la rama del nuevo worktree. Si el módulo Proxmox está en
`terraform/proxmox/` dentro de la raíz Git, continúa desde ese mismo subdirectorio
en el nuevo worktree. En VS Code, abre el worktree como carpeta de la sesión.
Si usas la terminal para ejecutar comandos, verifica su directorio de trabajo.
El plan, las ediciones, las validaciones, el staging y los commits de la tarea
se hacen desde ese worktree.

## 2. Crear o retomar el plan de implementación

Con el worktree asignado, crea o abre el plan según
`14-implementation-plans.md`. Para el módulo Proxmox, usa la ubicación
`docs/roadmap/planes/` relativa al módulo, siguiendo la convención de esa regla.

El plan se guarda en el worktree de la tarea, no en el worktree principal.
Esto permite que cada tarea tenga su propia línea de cambios independiente.

Al inicio, deja registrado en el plan:

- El objetivo y alcance de la tarea, con el servicio o CT si corresponde.
- La rama y la referencia base elegida.
- Los archivos previstos y las validaciones que se van a ejecutar.
- El estado actual y el siguiente paso.

En una tarea pequeña, basta un plan breve. En una tarea retomada, actualiza
el plan existente. Si el alcance cambia, actualízalo antes de seguir con el
nuevo trabajo.

Si el encargo es **solo planificación**, el archivo del plan es el entregable
y la implementación queda pendiente. Si Plan mode impide escribir el archivo,
prepara el contenido y deja indicada su ruta. Si el usuario cambia a Act
solo para guardarlo, el alcance de Act se limita a crear o actualizar ese plan.

## 3. Trabajar en paralelo

- Cada tarea activa usa una combinación distinta de rama y worktree. Esto
  también aplica cuando se trabaja con distintas IA o herramientas.
- Si dos tareas necesitan editar los mismos archivos, identifica el punto
  de solapamiento y coordina el orden de integración.
- El aislamiento Git separa los archivos y el staging. Coordina aparte las
  operaciones que compartan estado o infraestructura, como Terraform o Proxmox.

## 4. Cerrar la tarea

Desde el mismo worktree, aplica `15-task-commit-closeout.md`. Actualiza el
plan con los cambios realizados, las validaciones ejecutadas y los pendientes.
Si el alcance permite commits, crea los commits locales de la tarea con sus
cambios y su documentación.

En el resumen final, indica la **rama**, la **ruta del plan**, los **hashes de
los commits** y cualquier **cambio pendiente**. Conserva el worktree mientras
la tarea tenga cambios pendientes o deba retomarse. El push y la integración
en `main` requieren autorización para esa tarea.