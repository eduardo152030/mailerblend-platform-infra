# IA-CHAT — latencia de chat

13 de noviembre de 2026, Europe/Madrid. Fase 7; **DONE técnico del alcance IA-CHAT-LATENCY**.

## Resultado de la ruta real de Open WebUI

Usuario técnico, chat persistido, `POST /api/chat/completions` con stream y Socket.IO.
TTFT desde primer delta visible; incluye procesamiento de WebUI y la llamada al modelo.
Gemma cargado previamente. Sin llamadas ocultas de título/consultas en el perfil final.

| Estado / mensaje | Peticiones | Tokens de prompt | Reutilizados | TTFT s | Generación tokens/s |
|---|---:|---:|---:|---:|---:|
| Antes: saludo + título | 2 | 5324 + 314 | 0 + 1 | 344.401 | 4.637 |
| Después, turno 1 | 1 | 60 | 0 | 3.571 | 6.061 |
| Después, turno 2 | 1 | 96 | 77 | 1.410 | 8.272 |
| Después, turno 3 | 1 | 134 | 112 | 1.477 | 8.265 |

Qwen, tres turnos UI: 4.193s / 4.039s / 2.634s. Una petición por mensaje, caché0/75/120tokens, mismo slot.
Tras 300 s sin inferencias: mismo PID/pesos de Gemma; primer token **1.609s**.
Fecha: **Hoy es viernes.**; coincide con viernes 2026-11-13.

Causa principal: 5281 tokens adicionales de herramientas nativas implícitas para un saludo.
El prompt principal tardaba 344,265s en leerse. El título añadía 314 tokens totales,
313 procesados / 1 reutilizado,19,550s de lectura y1,224s de generación. No era un problema
resuelto únicamente manteniendo el modelo cargado.

## Configuración y coste de contexto

[Uso de chats largos y plan futuro](IA-CHAT-CONTEXT-PLAN.md). Carpetas y búsqueda organizan el historial; no amplían el contexto del modelo.

- Herramientas internas nativas desactivadas por defecto en ambos modelos; function_calling=legacy.
- Títulos, etiquetas, seguimiento, autocompletado y consultas web/RAG en segundo plano OFF.
- Botón de búsqueda conservado; consulta explícita breve validada por la ruta UI.
- Búsqueda explícita: 49.434s hasta primer token, 785tokens; recuperación y lectura de documentos añaden latencia.
- Sin generador de consultas se busca el texto literal. Una frase larga inicial devolvió cero resultados;
  se conserva el fallo y se valida la consulta breve Open WebUI documentation.
- Idle 3600 s. System prompt de una línea con {{CURRENT_WEEKDAY}} y{{CURRENT_DATE}}, verificados en v0.13.3.
- cache_prompt=true explícito; selección de slot por prefijo, sin fijar todos los chats al slot0.
- Gemma: template derivado del GGUF conserva prefijo vacío de pensamiento desactivado, ySWA completa.
- **Gemma 16384 tokens totales/8192 por conversación**, antes 65536/32768. Es una reducción de capacidad
  necesaria para alojar SWA completa dentro del margen de RAM. Qwen conserva 65536/32768 y usa
  preserve_thinking=true, opción nativa de su template. No se aumentó RAM de CT 630.
- CPU: generación con 3 hilos y prompt con 4 hilos. Se fija image-max-tokens128, equivalente al límite previo por ub128,
  para que aumentarubatch no amplíe implícitamente el presupuesto de imagen.

El mismo slot sirve los tres turnos finales. Reutilizar prefijo requiere texto estable:
se preservan los marcadores vacíos que la plantilla de generación emitía y el historial omitía.
La cachéSWAparcial de Gemma restauraba checkpoints anteriores incluso con prefijo coincidente.
No se cambia el binario/pesos; se usan opciones nativas y un template Jinja versionado/proveniente.

## Batch, ubatch y prompt de 3000 tokens

llama-bench: r3 por prueba; pp512/pp2048 a 4 hilos y tg128 a 3 hilos, en invocaciones separadas
porque esta versión no acepta --threads-batch. Modelo y pesos idénticos, mmap y repack0.
Selección por mayor pp2048 entre candidatos bajo guarda; validación adicional en servicio real.

| Modelo | b/ub | pp512 base→final | pp2048 base→final | tg128 base→final | TTFT3000 base→final s |
|---|---|---:|---:|---:|---:|
| gemma-4-26b | 2048/512 | 17.747→18.950 | 16.480→17.810 | 8.127→8.215 | 185.868→177.204 |
| qwen3.6-35b | 512/512 | 21.512→27.148 | 20.402→26.473 | 5.063→5.258 | 133.432→139.371 |

TTFT3000 medido con exactamente 3000 tokens sintéticos en `/completion`, stream,cache_prompt=false,
sin envolverlos con un prompt UI adicional. Es una prueba distinta del saludo UI:
un prompt largo nuevo sigue limitado por la CPU; el objetivo<=10s corresponde al chat corto en caliente.
El resultado runtime de 3000 tokens de Qwen empeora ligeramente pese a mejorar llama-bench; se conserva esa limitación.
Repacking no repetido: el ensayo previo con estos pesos duplicó memoria; el margen medido restante
no permite ese incremento. Se conserva no-repack y la evidencia del intento histórico.

## RAM de CT 631, datos, limpieza e idempotencia

4096 MiB aprobados/aplicados sin reiniciar el CT. RAG 7731 y STT concurrentes PASS; pico residente 2.510GiB.
memory.events delta: {'low': 0, 'high': 0, 'max': 90, 'oom': 0, 'oom_kill': 0, 'oom_group_kill': 0}. El contador local del límite del CT=0; max jerárquico corresponde
al cAdvisor de 256 MiB, sin OOM. No se reinician contadores ni se elimina swap.
Se preservan usuarios, chats, Knowledge y archivos originales; cuenta/token técnicos retirados, JWT 401.
SQLite quick_check=ok. Configuración, archivos, PID/StartedAt y segunda aplicación verificados.
Sin operaciones sobre CT 627 uotros CT, salvo lectura de sus contadores de swap desde el host.
Sin commit/push. Fase 7 global y aceptaciones heredadas no se cierran por este resultado.

## Anexo: matriz completa

| Modelo | b | ub | pp512 | pp2048 | tg128 | Pico benchmark GiB |
|---|---:|---:|---:|---:|---:|---:|
| gemma-4-26b | 512 | 128 | 17.747 | 16.480 | 8.127 | 13.820 |
| gemma-4-26b | 512 | 256 | 18.303 | 17.323 | 8.071 | 13.847 |
| gemma-4-26b | 512 | 512 | 18.613 | 17.729 | 8.044 | 13.946 |
| gemma-4-26b | 2048 | 128 | 17.291 | 16.749 | 8.154 | 13.823 |
| gemma-4-26b | 2048 | 256 | 16.451 | 17.104 | 8.170 | 13.850 |
| gemma-4-26b | 2048 | 512 | 18.950 | 17.810 | 8.215 | 13.949 |
| qwen3.6-35b | 512 | 128 | 21.512 | 20.402 | 5.063 | 16.859 |
| qwen3.6-35b | 512 | 256 | 24.488 | 23.743 | 5.069 | 16.880 |
| qwen3.6-35b | 512 | 512 | 27.148 | 26.473 | 5.258 | 16.914 |
| qwen3.6-35b | 2048 | 128 | 20.700 | 20.187 | 5.231 | 16.861 |
| qwen3.6-35b | 2048 | 256 | 24.830 | 23.621 | 5.239 | 16.882 |
| qwen3.6-35b | 2048 | 512 | 27.131 | 25.630 | 5.196 | 16.917 |

## Anexo: swap por CT, solo lectura

Capturas UTC:Gemma2026-11-13T21:24:24.930293+00:00;Qwen2026-11-13T21:20:09.796517+00:00.
Bytes de memory.swap.current convertidos aMiB; indica páginas alojadas, no tasa de swapping.
No se ejecuta nada dentro de los CT ajenos; no swapoff ni limpieza de cachés.

| CT | Hostname | Con Gemma MiB | Con Qwen MiB |
|---|---|---:|---:|
| 101 | docmost | 536.89 | 538.63 |
| 103 | aws-workshop | 803.77 | 803.78 |
| 104 | nucleo | 56.20 | 56.17 |
| 105 | n8n-server | 74.83 | 75.27 |
| 107 | drawio | 470.03 | 471.17 |
| 109 | edge-router | 89.79 | 89.56 |
| 610 | infra-prom | 203.09 | 203.68 |
| 611 | infra-grafana | 100.81 | 100.32 |
| 613 | infra-hola | 77.04 | 76.93 |
| 614 | infra-nucleoedge | 130.75 | 125.67 |
| 615 | infra-mailerblend-edge | 123.39 | 123.30 |
| 616 | infra-blackbox | 82.21 | 82.46 |
| 617 | infra-orbit | 118.28 | 117.05 |
| 618 | infra-composable-crm | 512.00 | 512.00 |
| 619 | infra-pulpo | 254.22 | 258.94 |
| 620 | infra-excraper | 153.89 | 154.71 |
| 621 | infra-project-gestion | 84.16 | 83.85 |
| 622 | infra-eva-assistant-bot | 280.61 | 281.23 |
| 623 | infra-gestoria | 211.34 | 216.48 |
| 624 | infra-journal-web | 91.10 | 91.20 |
| 625 | infra-journal-db | 106.35 | 106.53 |
| 626 | infra-journal-api | 139.00 | 138.32 |
| 627 | infra-voicebox | 418.75 | 418.69 |
| 630 | infra-llm | 41.75 | 104.78 |
| 631 | infra-webui | 272.88 | 102.43 |
| 61211 | svc01 | 253.73 | 252.73 |

## Evidencia y reproducción

[Recetas](../../scripts/ia-chat/latency/README.md),
[por petición](evidence/ia-chat-latency-2026-11-13/ui-request-summary.json),
[selección runtime](evidence/ia-chat-latency-2026-11-13/runtime-selection.json),
[idle](evidence/ia-chat-latency-2026-11-13/idle-residency.json),
[limpieza](evidence/ia-chat-latency-2026-11-13/cleanup-final.json).

Fuentes canónicas por servicio; YAML4096 MiB, Compose/perfilAPI, INI/template Jinja yselecciónr3.
Notas/inventario yREADME operativo actualizados. Tras cambiar hardware/release, revalidar el perfil.
No se certifica contexto lleno ni múltiples usuarios simultáneos a partir de estas pruebas.

Variables de fecha: [documentación oficial](https://docs.openwebui.com/features/chat-conversations/chat-features/temporal-awareness/),
contrastadas con el código instalado v0.13.3.
