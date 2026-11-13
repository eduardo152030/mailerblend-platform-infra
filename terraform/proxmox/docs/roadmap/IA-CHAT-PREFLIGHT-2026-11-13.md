# IA local para chat — Fase A: preflight y plan parcial

13 de noviembre de 2026 (Europe/Madrid). Roadmap: **Fase 7. IaC Reliability, Security & Disaster Recovery**, tarea IA-CHAT-A. La «Fase 1» del encargo es el subproyecto de chat; no sustituye las siete fases centrales.

Estado: **BLOCKED**. Lecturas completadas parcialmente; despliegue y aceptación TODO.

## Bloqueo y parada

En PVE, los dos ficheros indicados no existen en `/srv/models/qwen3.6-35b-a3b/`:
`Qwen3.6-35B-A3B-UD-IQ4_XS.gguf` y `mmproj-F16.gguf`.
No se ha podido calcular su SHA256 ni acreditar tamaños locales. No se han buscado
copias alternativas ni descargado pesos como sustitución. La regla del encargo
«Si algo falla, para e informa» obliga a detener aquí el trabajo dependiente.
La consulta pública y las otras lecturas ya estaban en curso cuando se conoció el fallo.

## Plan parcial propuesto; sin autorización de creación

| CT | Nombre | IP propuesta | CPU | RAM / swap | Discos SSD local-lvm |
|---|---|---|---|---|---|
| 630 | infra-llm | 192.168.1.230/24 | 4 | 22528 / 1024 MiB | rootfs16 + modelos60 GiB |
| 631 | infra-webui | 192.168.1.231/24 | 2 | 3072 / 1024 MiB | rootfs20 GiB |

IDs630/631 ausentes del inventario de recursos del clúster. Las IP no aparecen en
las configuraciones de los25CT leídas; ambas sin respuesta a3pings, sin MAC resuelta
(.230 FAILED, .231 INCOMPLETE). **Esto no demuestra que estén libres**: DHCP del router
no verificado, reserva/exclusión y confirmación del propietario pendientes.
Gateway192.168.1.254, vmbr0; unprivileged y Europe/Madrid en ambos.
Modelos backup=0 y RO después de copia/descarga verificada; WebUI nesting/keyctl.

Plantilla propuesta: `debian-12-standard_12.12-1_amd64.tar.zst`, presente en catálogo
`pveam available`; `pveam list local` sin plantillas. Descarga pendiente de autorización.
Total volúmenes96GiB frente a178,64GiB libres de pool; margen aproximado82,64GiB,
sin contar crecimiento de otrosCT ni snapshots.

## Modelos: metadatos públicos consultados

Elección propuesta: Gemma Unsloth UD-Q4_K_XL,14,249GB decimales, cumple <=17,5GB.
Se propone su proyector F16 del mismo repositorio. No se han descargado ni probado.
Todos los SHA de esta tabla son `lfs.oid` remoto; **ninguno es hash local validado**.

| Repositorio | Fichero | Bytes | SHA256 remoto |
|---|---|---:|---|
| `unsloth/gemma-4-26B-A4B-it-qat-GGUF` | `gemma-4-26B-A4B-it-qat-UD-Q4_K_XL.gguf` | 14249047104 | `a7c5bc715f5ff8e99a3e8901ce7d2b42b402c669bf24f7c5250747633d0f5891` |
| `unsloth/gemma-4-26B-A4B-it-qat-GGUF` | `mmproj-F16.gguf` | 1193058784 | `d00f211a7d4f7fb19bd9b75d8e9342eccffb5920b08fd9562167560fdfcc5dd1` |
| `google/gemma-4-26B-A4B-it-qat-q4_0-gguf` | `gemma-4-26B_q4_0-it.gguf` | 14439363584 | `3eca3b8f6d7baf218a7dd6bba5fb59a56ee25fe2d567b6f5f589b4f697eca51d` |
| `google/gemma-4-26B-A4B-it-qat-q4_0-gguf` | `gemma-4-26B-it-mmproj.gguf` | 1194828160 | `a359953a076b877db30c31dbbb4c6d93b4a6e017ee5db5784247e4d4c0dd4f3b` |
| `unsloth/Qwen3.6-35B-A3B-GGUF` | `Qwen3.6-35B-A3B-UD-IQ4_XS.gguf` | 17730509792 | `649d7508507b84638732c4f52c24c8b15843c6dca2f3ff793ae07c14a67ebbb3` |
| `unsloth/Qwen3.6-35B-A3B-GGUF` | `mmproj-F16.gguf` | 899283680 | `8971ee4f331ff0a4c609374f32984b3d4e6dc086c0aa35f1d637fad1829e887f` |

Listado completo de ambos repos Gemma, del Qwen y revisiones consultadas en
[metadatos públicos](evidence/ia-chat-a-2026-11-13/public.json).
Fuentes: [Unsloth Gemma](https://huggingface.co/unsloth/gemma-4-26B-A4B-it-qat-GGUF),
[Google Gemma](https://huggingface.co/google/gemma-4-26B-A4B-it-qat-q4_0-gguf),
[Unsloth Qwen](https://huggingface.co/unsloth/Qwen3.6-35B-A3B-GGUF).
Los cuatro ficheros elegidos sumarían34071899360bytes (~31,73GiB) en60GiB.

## Versiones: selección todavía incompleta

API oficial de releases: llama.cpp `v1.0.0`, commit indicado por release
`2d8a32502909ca065c41c4cf5f2fb1c427c047fc`, publicado13nov2026;
Open WebUI `v0.13.3`, publicado8nov2026, imagen propuesta
`ghcr.io/open-webui/open-webui:v0.13.3` (digest aún no resuelto).
[Release llama.cpp](https://github.com/ggml-org/llama.cpp/releases/tag/v1.0.0),
[release Open WebUI](https://github.com/open-webui/open-webui/releases/tag/v0.13.3).
SearXNG no ofrece `/releases/latest` (404); versión/digest de imagen pendiente.
No usar `latest` como fijación. Compatibilidad router, parámetros, thinking,
variables WebUI, embeddings/STT y dependencias aún no verificadas: Fase A incompleta.
No se ha instalado ni compilado nada.

## RAM y operación

Lectura tras preflight:31,23GiB físicos utilizables, MemAvailable22,42GiB,
swap host2,47GiB/16GiB. Supera21GiB solo en ese instante: repetir antes de cada
carga grande y parar si baja. Los nuevos límites suman25GiB; frente a~8,81GiB
usados actualmente no hay garantía de concurrencia segura al alcanzar límites.
CT627 sigue running/onboot1; no se ha detenido ni modificado. La exclusión de uso
Voicebox/LLM declarada por propietario aún necesita un mecanismo operativo aprobado
que no modifique627. Dos CT nuevos onboot1 no resuelven esa exclusión.
KV cache/contextos, proyectores, RAG y Whisper requieren medición; no prometer que
los contextos solicitados caben. Reducir según guarda90% en fase autorizada.

Enlace real eno1 **100Mb/s**, no1Gb/s; ver
[diagnóstico existente](NETWORK-ENO1-DIAGNOSTIC-2026-11-13.md). Sin cambios de red.

## Evidencia, alcance y siguiente paso

[Lecturas PVE filtradas](evidence/ia-chat-a-2026-11-13/host.json), marca UTC conservada,
SSH con known_hosts del propietario, StrictHostKeyChecking=yes y BatchMode=yes.
Se leyeron configuraciones LXC directamente; no se ejecutó `pct config` individual.
Script público reproducible: [preflight-public.py](../../scripts/ia-chat/preflight-public.py).
No cambios remotos persistentes, creación, instalación, inferencia, borrado,
reinicio, backups nuevos, commit ni push. CT existentes y627 intactos.

Siguiente: propietario aclara ubicación/ausencia de Qwen. Tras resolver el bloqueo,
completar Fase A (hashes, versión SearXNG y compatibilidad), confirmar exclusión DHCP
y presentar plan definitivo. **Esperar confirmación explícita antes de B–F**, según
punto de parada del encargo. La copia del encargo termina truncada en F11 «Reinicio»;
su criterio completo deberá aclararse antes de ejecutar esa validación.
