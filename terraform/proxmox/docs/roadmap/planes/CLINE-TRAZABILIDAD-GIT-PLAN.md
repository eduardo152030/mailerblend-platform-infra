# Trazabilidad Git por tarea en Cline

- Fase 7. Estado IN PROGRESS. 19/11/2026, Europe/Madrid.
- Rama `docs/cline-trazabilidad-por-tarea`, worktree `../mailerblend-platform-infra-cline-trazabilidad` desde la raíz del checkout principal.
- Base `origin/main` en `1cf05a1b`.
- Alcance: regla 03 como entrada obligatoria, plan o issue enlazado al PR,
  revisión de las demás reglas y corrección de numeración y referencias.
- Validación: comprobar prefijos únicos, títulos, enlaces, referencias y
  `git diff --check`. Revisar escenarios de inicio, reanudación y cierre.
- Evidencia local: nueve prefijos únicos con sus títulos, enlaces revisados,
  referencia antigua retirada y `git diff --check` limpio.
- PR de revisión: [#20](https://github.com/eduardo152030/mailerblend-platform-infra/pull/20).
- Siguiente paso: revisión del PR por el propietario.

## Ampliación aprobada del cierre

- Una tarea con cambios solo se declara terminada tras publicar y verificar
  el PR de su worktree. El informe final empieza con su enlace.
- Una petición breve de commit, push o PR ejecuta el flujo de cierre para
  la tarea activa. Un límite explícito o un bloqueo deja la entrega pendiente.
- Verificar rama, base, SHA publicado, conflictos y checks en GitHub. La
  aprobación e integración corresponden al propietario.

## Ronda 01 — artefacto diferencial de revisión

- Baseline `59a3dd6387e63b979d6ba98b7e090f2bbcb6ef8c`, capturado antes de editar.
- Alcance: añadir la regla 19 para guardar el diff de cada ronda en el worktree,
  enlazarla al cierre con PR y generar el artefacto de esta ronda.
- Verificación: numeración, enlaces, diff de la ronda, comprobación inversa
  del parche y ausencia del artefacto en los commits.

## Ronda 02 — numeración consecutiva

- Baseline `d75f0a9d369497cd0c9160f2e24922fddf9cc5db`, capturado antes de editar.
- Alcance: numerar las diez reglas activas del 01 al 10, conservando Git
  como 03. Actualizar referencias y conservar el historial de las rondas.
- Verificación: secuencia, títulos, enlaces locales, diff y parche de la ronda.
