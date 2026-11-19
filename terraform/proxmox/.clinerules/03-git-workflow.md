# 03 — Flujo Git por tarea

Cada tarea del repositorio empieza en un **worktree dedicado y una rama propia**.
Esto aplica aunque solo haya una IA trabajando y aunque la tarea consista
únicamente en preparar un plan. Aplica esta regla al recibir la tarea, antes
de editar, mover o borrar archivos, incluso si el usuario dejó los archivos
de entrada en el worktree principal. Identifica esas entradas y cópialas al
worktree dedicado para trabajar allí.

## 1. Abrir o retomar el worktree

Antes de editar, ejecuta:

```bash
git rev-parse --show-toplevel
git rev-parse --show-prefix
git worktree list
git status --short --branch --untracked-files=all
```

### 1.1. Sincronizar con el remoto

Antes de cualquier otra acción, ejecuta:

```bash
git fetch origin main
```

Usa la referencia actualizada para la base de una tarea nueva.

### 1.2. Tarea nueva

Crea una rama y un worktree para la tarea desde `origin/main`,
salvo que el usuario indique otra base o que el plan dependa de otra rama
confirmada. Usa una ruta fuera del árbol de trabajo existente.

### 1.3. Tarea en curso

Reutiliza el worktree y la rama ya asignados. Revisa
el estado de Git y el último paso registrado en el plan antes de seguir.

### 1.4. Dependencias entre tareas

Conserva los cambios que encuentres en otros worktrees. Si la tarea depende
de cambios pendientes de otra rama, identifica la dependencia y acuerda
cómo integrarla antes de incorporarla. Los PRs abiertos de otros trabajos
no bloquean una tarea independiente.

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

## 1.5. Consultar estado de PRs al iniciar o retomar una tarea

Antes de crear el plan (sección 2), consulta el PR asociado a la tarea.
Si la tarea no tiene un PR abierto, omite esta sección.

Para una **tarea nueva**, verifica que `origin/main` está actualizado (sección 1.1)
y crea la rama desde él. Si la tarea depende de un PR anterior, consulta ese PR
por número o URL:

```bash
gh pr view <número-o-rama> --json state,reviewDecision,isDraft,mergeStateStatus,headRefOid,url
```

- **`MERGED`**. El PR ya está integrado en `main`. Continúa desde
  `origin/main` actualizado. Registra el cierre en el plan.
- **Abierto**. Indica la dependencia en el plan. Los PRs abiertos de otras
  tareas no bloquean una tarea independiente.

Para una **tarea en curso**, reutiliza su worktree y consulta el PR asociado,
incluso si ya está cerrado o integrado:

```bash
gh pr view <número-o-rama> --json state,reviewDecision,isDraft,mergeStateStatus,headRefOid,url
```

- **`MERGED`**. Registra el cierre y refresca `origin/main` para el siguiente
  trabajo:
  ```bash
  git fetch origin main && git merge origin/main
  ```
- **`CHANGES_REQUESTED`**. Lee la revisión en GitHub, corrige lo que corresponda
  en la misma rama. Si la publicación está autorizada, haz `git push` para
  solicitar otra revisión.
  Actualiza el plan con los cambios realizados.
- **Pendiente o decisión vacía**. Deja el PR en revisión. Una decisión vacía
  (`reviewDecision == ""`) no cuenta como aprobación.
- **`APPROVED` y abierto**. Comprueba que la aprobación sigue vigente para el
  cambio actual y que GitHub permite integrarlo. Consulta los checks requeridos:
  ```bash
  gh pr checks <número> --required --json name,state,bucket
  ```
  Si los checks están en `SUCCESS` y no hay conflictos (`mergeStateStatus != "BEHIND"`),
  ejecuta el merge si está autorizado. Si el merge corresponde a otra persona,
  informa que el PR está listo para integrar. En ambos casos, toma la aprobación de GitHub como
  autoridad.

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

## 3. Implementar y abrir PR

La IA implementadora trabaja en la rama y el worktree de la tarea.
Una vez completados los cambios y validados contra el plan aprobado:

1. **Validar.** Ejecuta las pruebas y verificaciones que exige el plan.
   Registra los resultados. Si hay desviaciones, documentalas y obtén
   aprobación antes de continuar.
2. **Commitear.** Si el alcance permite commits, créalos siguiendo
   `15-task-commit-closeout.md`.
3. **Publicar rama.** Si el alcance autoriza publicación, sube la rama al remoto:
   ```bash
   git push -u origin <rama-de-la-tarea>
   ```
4. **Abrir PR.** Si el alcance autoriza abrir el PR, créalo hacia `main`.
   El PR debe referenciar el plan aprobado (ruta y versión) e incluir un
   resumen del diff, las pruebas ejecutadas con sus resultados y cualquier
   desviación aprobada.
5. **Entregar para revisión.** Deja la integración pendiente de la revisión
   independiente y de las comprobaciones requeridas. Si el alcance termina
   en el commit local, entrega el cierre de la sección 4. En el resumen final,
   indica la **rama**, el **enlace al PR**, la **ruta del plan**, los
   **hashes de los commits** y el **estado de las comprobaciones**.

La revisión la realiza **otra IA**, en una sesión separada. La IA
implementadora no aprueba su propio PR.

## 4. Cerrar la tarea

Desde el mismo worktree, aplica `15-task-commit-closeout.md`. Actualiza el
plan con los cambios realizados, las validaciones ejecutadas y los pendientes.
Si el alcance permite commits, crea los commits locales de la tarea con sus
cambios y su documentación.

En el resumen final, indica la **rama**, la **ruta del plan**, los **hashes de
los commits** y cualquier **cambio pendiente**. Conserva el worktree mientras
la tarea tenga cambios pendientes o deba retomarse. El push y la integración
en `main` requieren autorización para esa tarea.

## 6. Integración tras aprobación

Cuando la integración está autorizada para la tarea, la revisión está aprobada
(`reviewDecision == "APPROVED"`) y los checks requeridos están en `SUCCESS`:

1. Verificar que no hay conflictos:
     ```bash
     gh pr view <número> --json mergeStateStatus --jq '.mergeStateStatus'
     ```
   Si `mergeStateStatus` es `CLEAN` o `HAS_HOOKS`, procede. Si es `BEHIND`,
   actualiza la rama con `main` primero.

2. Hacer merge del PR:
     ```bash
     gh pr merge <número> --squash --delete-branch
     ```

3. Actualizar `main` local:
     ```bash
     git fetch origin main && git merge origin/main
     ```

4. Limpiar el worktree de la tarea si ya no es necesario:
     ```bash
     git branch -d <rama>
     git worktree remove <ruta-del-worktree>
     git remote prune origin
     ```

5. Actualizar el plan con el resultado de la integración.

Si el merge corresponde a otra persona (por política del repositorio o
autorización del usuario), informa que el PR está listo para integrar y
proporciona el enlace al PR. No ejecutes el merge en ese caso.
