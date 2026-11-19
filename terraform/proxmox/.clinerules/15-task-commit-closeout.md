# 15 — Cierre de tarea: commits, PR y revisión

## Implementación

1. Confirma el worktree y la rama con la [regla 03](03-git-workflow.md).
2. Compara el alcance del plan o issue con el diff contra la base. Verifica
   los criterios y registra resultados, desviaciones aprobadas y pendientes
   en la referencia de la tarea.
3. Prepara solo los archivos de la tarea. Revisa `git diff --cached` y ejecuta
   `git diff --cached --check`. Comprueba también el diff completo contra la
   base para detectar cambios ajenos introducidos por la historia de la rama.
4. Si el encargo lo permite, crea commits descriptivos y verifica el estado
   del worktree. Conserva cualquier cambio ajeno.
5. Publica la rama y abre o actualiza el PR según el alcance. Incluye el enlace
   al plan o issue, la base, la rama, el resumen del diff, los resultados
   de validación y las desviaciones aprobadas. Registra la URL del PR en
   la referencia de la tarea antes de entregarlo para revisión.
6. Entrega el enlace de trazabilidad junto con la rama, el worktree, los
   commits, el PR y el estado de las comprobaciones. Para un cierre local
   autorizado, registra la publicación como pendiente.

## Revisión independiente

1. Abre el PR y su plan o issue. Identifica el commit revisado y comprueba
   que la rama y la base coinciden con la tarea.
2. Contrasta el diff real con el alcance y comprueba las pruebas o evidencias
   de cada criterio. Verifica los enlaces entre la referencia de la tarea
   y su PR.
3. Aprueba si se cumplen los criterios. Si faltan cambios o evidencias,
   solicítalos en el PR con el criterio concreto y la referencia al archivo
   o validación. Registra el resultado de la revisión y el siguiente paso.
4. Deja la integración sujeta a las condiciones de la
   [regla 03](03-git-workflow.md).
