# CRM Core Main — estructura y cierre Git

## Estado

DONE local, 19/11/2026 Europe/Madrid. Rama `feat/crm-core-main-flatten`,
base local original `main` en `5420968a`. Para publicar, el propietario
autorizó abrir un PR desde `feat/crm-core-main-review` sobre
`origin/main` (`95687975`).

## Alcance y validación

- El commit `adecd384` incorporó la estructura aplanada y el plan en el worktree
  dedicado. La copia original del propietario se conserva.
- Se incluyen los tres archivos que omitió el ignore general:
  `eslint.config.js`, `postcss.config.js` y `src/vite-env.d.ts`.
- Se corrigen espacios finales en tres archivos para cumplir `git diff --check`.
- La regla 03 se aplica al abrir la tarea. El cierre local y la publicación
  quedan sujetos al alcance autorizado, también en la regla 15.
- Criterios verificados: 129 archivos rastreados, sin carpeta duplicada ni
  archivos `:Zone.Identifier`, y diff de la tarea limpio.

## Siguiente paso

Revisión y aprobación del PR por el propietario. Validación funcional del CRM pendiente.
