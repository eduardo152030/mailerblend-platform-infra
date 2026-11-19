# 03 — Flujo Git por tarea

Aplica esta regla al recibir cada tarea, incluidas las tareas pequeñas,
documentales, de solo planificación y las que disparan un workflow específico.
La trazabilidad une **plan o issue → worktree dedicado y rama propia → PR**.
Si el encargo limita una acción, registra el estado real y el siguiente paso
en el plan o issue. Para tareas con cambios, el cierre normal incluye commit, push y PR.
La aprobación, la integración y las operaciones en producción son pasos
separados.

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
   local, la referencia de seguimiento y el PR existente antes de actuar:

   ```bash
   gh pr list --head <rama> --state all --json number,state,url
   ```

   Distingue una lista vacía de un fallo de consulta.
   Un PR integrado cierra esa rama de trabajo. Si queda trabajo con otro alcance,
   abre una tarea con rama y worktree nuevos desde la base actualizada.
   Conserva las ramas anteriores para trazabilidad y cualquier trabajo pendiente.
   La limpieza de ramas y la reescritura de historia requieren un encargo
   específico.
4. **Antes de escribir, mover, borrar, preparar artefactos, hacer staging o
   ejecutar un paso del workflow que cambie el entorno**, comprueba la ruta con
   `git rev-parse --show-toplevel` y la rama con `git branch --show-current`.
   Si no coinciden con la tarea, corrige el directorio de trabajo primero.
   En Proxmox, continúa desde `terraform/proxmox/` dentro del worktree dedicado.
   Copia allí los archivos de entrada que el usuario dejó en otro checkout y
   conserva el origen. Si existe una dependencia de otra rama, regístrala y
   acuerda la base antes de incorporarla. Identifica el PR previo y el orden
   de integración en el plan o issue y en el PR dependiente. Tras integrarse
   el PR previo, actualiza la base acordada y vuelve a validar el diff y el PR
   dependiente antes de entregarlo. Si avanza la base de cualquier PR que
   estés gestionando, vuelve a consultar su estado antes de declararlo listo.

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

Aplica el [cierre de la regla 15](15-task-commit-closeout.md) desde el
worktree dedicado. Peticiones breves como «haz commit», «haz push» o
«crea el PR» activan el cierre completo de la tarea. Un límite explícito,
como «solo commit local», deja la publicación pendiente.

El cierre de una tarea con cambios exige un PR abierto y listo para revisión
cuya rama de origen corresponda al worktree y cuyo último commit sea el que
se acaba de verificar. Reutiliza el PR abierto de la tarea. Enlaza el plan
o issue en el PR y registra la URL del PR en la referencia de la tarea. Si
el enlace se incorpora en un commit posterior, publícalo y comprueba de
nuevo el SHA del PR.

El primer dato del mensaje de cierre es el **enlace al PR**. Si falta el
PR, la publicación falla o queda un conflicto, comunica **entrega pendiente**
con el motivo y el siguiente paso. Las consultas de solo lectura se
reportan como diagnóstico. Un encargo de solo planificación que modifica
un documento versionado sí sigue el cierre con PR.

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
- **Aprobado**. Cline entrega el enlace y se detiene. El propietario decide
  la aprobación y la integración desde GitHub.
- **Integrado**. Registra el cierre con el PR y el commit de integración.
  Si se solicita actualizar `main`, inspecciona primero su estado, preserva
  cambios ajenos y verifica el resultado contra `origin/main`.

Conserva el worktree mientras haya cambios pendientes o trabajo por retomar.
Comprueba su estado y el de la rama antes de retirarlo.
