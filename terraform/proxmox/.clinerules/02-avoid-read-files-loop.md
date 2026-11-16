# 02 — Evitar bucles de lecturas con `read_files`

## Regla principal

**Al trabajar en este repositorio, evitar `read_files` y `read_file`.**
Para inspeccionar archivos, usar `run_commands` con `sed`, `rg`, `cat` o
`git diff` y leer solo lo necesario.

## Problema

Las sesiones anteriores entraron en bucles de llamadas idénticas a
`read_files` que impedían avanzar en la tarea. La tarea avanzó al cambiar
a `run_commands` con `cat` para leer el inventario.

La causa raíz del fallo de `read_files` sigue sin confirmarse (posible
problema de permisos, ruta relativa vs absoluta o límite de tamaño).

## Comportamiento obligatorio

### Antes de leer

- Usar `run_commands` con `cat <ruta>`, `sed -n 'N,Mp' <ruta>`,
  `rg 'patrón' <ruta>` o `git diff` para inspeccionar archivos.
- Nunca emitir `read_files` salvo que el usuario lo solicite explícitamente
  para un archivo concreto.

### Si la lectura funciona

- Usar el resultado inmediatamente para pasar al siguiente paso.
- No releer el mismo archivo salvo que haya cambiado.

### Si la lectura falla

- Revisar el mensaje de error.
- Cambiar la ruta, el rango de líneas o el método de lectura.
- Máximo tres intentos con estrategias diferentes.
- Si el bloqueo persiste, mostrar el error y detenerse.

## Comandos recomendados

| Necesidad | Comando |
|---|---|
| Leer archivo completo | `cat <ruta>` |
| Leer líneas N–M | `sed -n 'N,Mp' <ruta>` |
| Buscar patrón | `rg 'patrón' <ruta>` |
| Ver diff | `git diff <ruta>` |
| Listar directorio | `ls -la <ruta>` |
| Contar líneas | `wc -l <ruta>` |

## Excepciones

`read_files` está permitido cuando:
- El usuario lo solicita explícitamente.
- Se necesita leer múltiples archivos pequeños de forma concurrente
  y se conoce que las rutas son absolutas y accesibles.
