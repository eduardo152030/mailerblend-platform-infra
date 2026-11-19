# 03 — Flujo Git por tarea

Aplica esta regla al recibir cada tarea, incluidas las tareas pequeñas,
documentales, de solo planificación y las que disparan un workflow específico.
La trazabilidad une **plan o issue → worktree dedicado y rama propia → PR**.
Si el encargo limita una acción, registra el estado real y el siguiente paso
en el plan o issue. La preparación y publicación del PR tienen su propio alcance,
igual que la integración y cualquier operación en producción.

## 1. Identificar la tarea y abrir o retomar su worktree

Empieza con estas comprobaciones de lectura:

```bash
git rev-parse --show-toplevel
git rev-parse --show-prefix
git worktree list
git status --short --branch
```

1. Identifica el plan o issue existente. Si falta, define la ruta del plan
   breve según la [regla 14](14-implementation-plans.md).
2. Para una tarea nueva, ejecuta `git fetch origin main` y crea la rama y el
   worktree desde `origin/main` actualizado, salvo que exista otra base acordada.
   El worktree se crea fuera del checkout actual. Desde la raíz Git:

   ```bash
   git worktree add -b ops/ct618-swap ../mailerblend-platform-infra-ct618-swap origin/main
   ```

3. Para una tarea en curso, reutiliza su worktree y rama. Revisa el estado
   local, la referencia de seguimiento y el PR existente antes de actuar.
   Un PR integrado cierra esa rama de trabajo. Si queda trabajo con otro alcance,
   abre una tarea desde la base actualizada.
4. **Antes de escribir, mover, borrar, preparar artefactos, hacer staging o
   ejecutar un paso del workflow que cambie el entorno**, comprueba la ruta con
   `git rev-parse --show-toplevel` y la rama con `git branch --show-current`.
   Si no coinciden con la tarea, corrige el directorio de trabajo primero.
   En Proxmox, continúa desde `terraform/proxmox/` dentro del worktree dedicado.
   Copia allí los archivos de entrada que el usuario dejó en otro checkout y
   conserva el origen. Si existe una dependencia de otra rama, regístrala y
   acuerda la base antes de incorporarla.

## 2. Registrar alcance, evidencia y estado

Antes de implementar, usa un plan versionado o un issue que identifique la tarea
y contenga el alcance, los criterios y verificaciones, la rama, la ubicación
relativa del worktree, la referencia base y el siguiente paso. Un plan breve
basta para tareas pequeñas. Si el issue ya contiene estos datos, úsalo como
referencia principal. Registra las ampliaciones antes de ejecutarlas.

En un encargo de solo planificación, el cambio del PR es el plan y, cuando
corresponda, el seguimiento asociado. Marca el plan como propuesto hasta
que el propietario apruebe su ejecución.

## 3. Validar, publicar y enlazar

Aplica el [cierre de la regla 15](15-task-commit-closeout.md). Comprueba
que el diff contra la base contiene solo cambios de la tarea. Publica la rama
y abre su PR hacia la base acordada cuando el encargo lo autorice. Si la rama
ya tiene PR, actualiza el mismo PR. Si el alcance termina en un commit local,
registra el PR como pendiente y conserva el worktree para publicarlo más tarde.

En el PR, enlaza el issue o el plan con su ruta y revisión, e incluye el
resumen y las verificaciones. Registra también la URL del PR en el issue o
plan correspondiente. Para un plan versionado, incorpora el enlace en la
misma rama antes de solicitar la revisión.

## 4. Revisar e integrar

Consulta el estado con:

```bash
gh pr view <número-o-rama> --json state,reviewDecision,isDraft,mergeStateStatus,headRefOid,url
gh pr checks <número-o-rama> --required
```

- **Abierto o en borrador**. Conserva el estado pendiente hasta tener una
  aprobación válida para el cambio actual.
- **Cambios solicitados**. Revisa el feedback, registra las correcciones en la
  referencia de la tarea y actualiza la misma rama y PR según el alcance.
- **Aprobado**. La integración requiere autorización para la tarea, que el PR
  sea integrable y que pasen las comprobaciones requeridas. La IA que
  implementa no aprueba su propio PR.
- **Integrado**. Registra el cierre con el PR y el commit de integración.
  Si se solicita actualizar `main`, inspecciona primero su estado, preserva
  cambios ajenos y verifica el resultado contra `origin/main`.

Conserva el worktree mientras haya cambios pendientes o trabajo por retomar.
Comprueba su estado y el de la rama antes de retirarlo.
