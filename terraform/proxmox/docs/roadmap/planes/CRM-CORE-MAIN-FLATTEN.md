# CRM Core Main — Flattening and Cleanup

## Estado: Propuesto

## Rama
`feat/crm-core-main-flatten`

## Base
`origin/main` (commit 5420968a)

## Alcance
- Aplanar la estructura de directorios de `crm-core-main` eliminando la carpeta
  anidada `crm-core-main/crm-core-main/`.
- Eliminar todos los archivos `:Zone.Identifier` (artefactos de Windows ADS
  copiados a ext4).

## Lo que NO incluye
- Modificaciones de código.
- Commits ni pushes (solo preparación del worktree y verificación).
- Cambios en `.gitignore` (ya contiene `*Zone.Identifier`).

## Criterios de aceptación verificables
1. No existe el directorio `services/infra-composable-crm/compose/budibase/crm-core-main/crm-core-main/`.
2. No existen archivos `:Zone.Identifier` dentro de `crm-core-main/`.
3. El directorio `crm-core-main/` contiene 129 archivos y ~21 directorios.
4. `git diff --cached --check` no reporta errores.

## Pruebas requeridas
- `find ... -type f | wc -l` == 129
- `find ... -name ':Zone.Identifier' | wc -l` == 0
- `find ... -type d | wc -l` == ~21
- `git diff --cached --check` limpio

## Archivos afectados
- `services/infra-composable-crm/compose/budibase/crm-core-main/` (directorio completo, nuevo en git)

## Pasos
1. Crear worktree dedicado `feat/crm-core-main-flatten`.
2. Copiar la estructura aplanada desde el worktree principal.
3. Verificar estructura y limpieza.
4. Staging y commit.
5. Publicar rama y abrir PR.

## Pendiente
- Validar que la aplicación funciona con la nueva estructura.
- Revisar referencias de rutas internas en el código.
