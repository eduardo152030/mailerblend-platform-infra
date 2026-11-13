# Fase 7.4 — Chatterbox: entrada de 1.200 caracteres, solo código

13 de noviembre de 2026, Europe/Madrid. Implementación local preparada para publicar.
**Pruebas no ejecutadas por instrucción expresa. Despliegue no ejecutado.**

## Alcance

El código de Chatterbox Multilingual admite entre1y1.200caracteres de entrada,
igual que el límite de Qwen. Esto es admisión de entrada: **la generación completa
de textos de esa longitud sigue sin validar**. No se han ejecutado inferencias,
procesado audio, compilado imágenes, desplegado ni reiniciado servicios.
La producción aceptada D089 conserva240caracteres hasta un despliegue separado.

## Cambios de código

- `candidate-d085/engine_policy.py`, `maintenance-d087/engine_policy.py` y
  `validation-d089/engine_policy.py`: CHATTERBOX_MAX_CHARS=1200, consumida por
  CB.max_chars, mensajes de error y capabilities.max_chars. La API recibe esta
  política en el contexto de imagen; controlador y worker reciben sus copias
  verificadas. El worker ya invoca validate antes de cargar ML, sin un límite
  numérico adicional que cambiar.
- UI: constante equivalente en ct627Policy.ts para textLimit y selector. El mensaje
  de validación existente usa textLimit; el selector muestra entrada1200 y que la
  generación completa no está validada. No se cambian Qwen ni los efectos.
- Comprobaciones de capacidades en recetas usan el límite de política/manifest.
  La receta D089 incluye engine_policy en los archivos objetivo del controlador y
  worker; copia/verifica y respalda/restaura los archivos declarados, sin ejecutar
  esas operaciones. Se conserva fallback de restauración de backups anteriores.
- Expectativas de tests Python/UI y fixture API actualizadas a1200/1201. El fixture
  usa CB.max_chars+1 para su caso de rechazo. **No se ejecutaron esos tests**.

## Límites conservados

| Parámetro | Valor sin cambios |
|---|---:|
| Tokens de salida | 400 |
| EOS | Obligatorio antes del decoder |
| WAV | Máximo20s |
| Timeout | 300s |
| Worker: parada / hard | 7 /8GiB |
| Guarda CT627 | 19GiB |
| Qwen | 1200caracteres; resto del contrato intacto |

El mayor límite de entrada no amplía salida, tiempo o memoria. Puede no bastar
para completar un texto largo: no se declara capacidad acústica de1200caracteres
ni se relajan las guardas para conseguirla.

## Hashes, imágenes e historial

Se recalculan hashes de engine_policy en los release propuestos D085/D087 y el
source-lock objetivo D089, el hash del release y archivos afectados en el lock D087,
y los hashes objetivo del controlador/worker D089. Se añade max_chars de destino
al manifest para que la comprobación de capacidades no conserve240hardcodeado.
Manifiesto de fuentes de este cambio:
`services/infra-voicebox/release-d089/input-1200-source-manifest.json`.

Las claves original_source_hashes/original_worker_hashes y production_controls
siguen describiendo el baseline/rollback D089 desplegado, no el nuevo destino.
Los execution-manifest históricos registran ejecuciones anteriores: se conservan
sin reescribir la evidencia. Su procedencia está en el commit D089
`ec9cb311443ea0c3291c6b708302e47bbb0cf8e1`; el nuevo manifiesto cubre las fuentes actuales.
No se cambian digests de imágenes, pesos, entorno o referencia ya publicados.
El audit.py de release-d089 sigue siendo la auditoría histórica de la imagen
publicada de240caracteres; no se ejecuta ni se utiliza como prueba de esta ampliación.

Los digests publicados describen imágenes anteriores: no contienen el cambio
nuevo de UI/API. Habilitarlo en producción requeriría un build y despliegue
coordinado posteriores, autorizados por separado. Las recetas históricas no se
reaplican automáticamente ni se etiquetan las imágenes existentes como si fueran
un nuevo build de1200caracteres.

## Revisión y estado

Revisión de diff y generación de hashes únicamente. No se ejecutaron tests,
comprobaciones funcionales de API, builds, inferencias, despliegues o reinicios.
Publicación solicitada por push normal aorigin/main del repositorio
eduardo152030/mailerblend-platform-infra, sinforce y sin cambios ajenos.

Implementación local/publicación: alcance de este cambio. Validación y despliegue:
TODO, fuera del alcance. La aceptación acústica D089 queda intacta para lo probado.
[Historial D089](PHASE7-D089-CHATTERBOX-PRODUCTION-VALIDATION.md).
