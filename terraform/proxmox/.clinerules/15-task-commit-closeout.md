# 15 — Cierre de tarea: commits, PR y revisión

## Implementación

1. Confirma el worktree y la rama con la [regla 03](03-git-workflow.md).
2. Compara el alcance del plan o issue con el diff contra la base. Verifica
   los criterios y registra resultados, desviaciones aprobadas y pendientes
   en la referencia de la tarea.
3. Prepara solo los archivos de la tarea. Revisa `git diff --cached` y ejecuta
   `git diff --cached --check`. Comprueba también el diff completo contra la
   base para detectar cambios ajenos introducidos por la historia de la rama.
4. Crea commits descriptivos con los archivos concretos. Si el alcance
   tiene un límite explícito, registra el paso pendiente.
5. Publica la rama del worktree con `git push -u origin HEAD`. Si ya tiene
   un PR abierto, actualízalo. Si falta, créalo indicando explícitamente
   base y rama con `gh pr create --base <base> --head <rama>`. Incluye
   el enlace al plan o issue, el resumen, las pruebas y las desviaciones
   aprobadas. Registra la URL del PR en la referencia de la tarea.
6. Verifica el resultado final después del último push:

   ```bash
   git status --short --branch
   git log -1 --format=%H
   gh pr view <rama> --json url,state,isDraft,headRefName,headRefOid,baseRefName,mergeable,mergeStateStatus
   gh pr checks <rama>
   ```

   Confirma que el PR está abierto y listo para revisión, que corresponde
   a la rama y base esperadas, que `headRefOid` coincide con `HEAD` y que
   GitHub indica `MERGEABLE`. Si GitHub todavía calcula la integrabilidad,
   indica que está pendiente. Revisa el estado local y cualquier cambio
   propio que falte subir. Reporta los checks como aprobados, pendientes,
   fallidos o ausentes según GitHub. Registra la ausencia de checks como
   tal. Usa las etiquetas del repositorio que correspondan a la tarea.
7. Empieza el mensaje final con **PR: [#número](URL)**. A continuación
   indica rama, ruta del worktree, plan o issue, SHA y estado de los checks.
   Si falta el PR, el SHA no coincide o existe un bloqueo de entrega,
   indica **entrega pendiente** con la causa. Cline termina su intervención
   al entregar el PR para revisión. El propietario decide cuándo aprobarlo
   y fusionarlo.

## Revisión independiente

1. Abre el PR y su plan o issue. Identifica el commit revisado y comprueba
   que la rama y la base coinciden con la tarea.
2. Contrasta el diff real con el alcance y comprueba las pruebas o evidencias
   de cada criterio. Verifica los enlaces entre la referencia de la tarea
   y su PR.
3. Registra los criterios satisfechos y los cambios o evidencias pendientes.
   El propietario emite su aprobación desde GitHub.
4. Deja la integración sujeta a las condiciones de la
   [regla 03](03-git-workflow.md).
