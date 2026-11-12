# Fase 7.4 — piloto Qwen CustomVoice 0.6B — D066

Fecha de cierre: 2026-11-10 (Europe/Madrid). Ensayo real iniciado a las
14:41:17,730 CET (13:41:17,730 UTC). **DONE: ejecución del piloto y recuperación**.
Resultado del modelo: **FAIL por parada preventiva; no aceptado para producción**.
Fase 7.4 global **IN PROGRESS**.

## Alcance autorizado y resultado

El propietario autorizó CustomVoice 0.6B BF16/SDPA con un máximo de 4 GiB,
backup, imagen original conservada, un único modelo residente, frase corta y
60 segundos solo si era estable. También autorizó la parada y recuperación
automáticas. No autorizó eliminar los tres perfiles rechazados. No se intervino
Qwen Base, otros LXC ni el pipeline de vídeos; no se hizo commit ni push.

La descarga y la carga en CPU se completaron. La primera generación en español
superó el umbral conservador de cgroup de 3,5 GiB y se detuvo automáticamente.
**No hay WAV Qwen terminado, aceptación de calidad, medición de un minuto ni
factor de tiempo real de Qwen**. No se relajó el umbral ni se reintentó tras HALT.

## Preparación reproducible y conservación

[Diagnóstico y propuesta D065](PHASE7-D065-QWEN-OPTIMIZATION.md). Fork fijado en
`8af7efe62fab8d33e2a5dfbedabaa45f68a5184f`. La receta y el parche están en
[Dockerfile](../../services/infra-voicebox/pilot-d066/Dockerfile),
[backend.patch](../../services/infra-voicebox/pilot-d066/backend.patch) y
[source-lock](../../services/infra-voicebox/pilot-d066/source-lock.json).
Solo cambia el backend CustomVoice CPU 0.6B a BF16/SDPA; Base permanece intacto.

- Original conservada: `sha256:7f2e6f7e6a2d09c77ebd35424a7641249e51b8ff0374bc9c4acb1f7393cfcd4c`.
- Candidata conservada: `sha256:4de8a649d267fb9f4fa9d7049f264a1e6896718c7892f70706abb4a46d75430d`.
- Backup previo: `/opt/voicebox/backups/d066-before-qwen.tar.gz`, SHA256
  `5a4f2f9d7c49ea1f45772cacb86a4a3611b710bf564a6581355ba2d410d00441`.
  Copia fuera de PVE en `~/.local/share/mailerblend-recovery/voicebox-d066/`;
  restauración local comprobada: 35 archivos, 6 symlinks confinados, SQLite íntegro,
  9 audios completados. Archivo de imagen original D063 también conservado.

Datos y caché aislados en `/srv/voicebox/pilot-d066/`; copia de la base de datos,
sin sustituir el volumen productivo. [Compose](../../services/infra-voicebox/pilot-d066/compose.yml)
limita la candidata a 3300 MiB sin swap adicional, 2 CPU y API loopback 17494.
El servicio original permanece vivo con Kokoro descargado de RAM durante el piloto
(RSS base 316,10 MiB), sin cargar dos modelos. El perfil Ryan de prueba solo existe
en la copia aislada. Imagen, contenedor detenido, caché y datos de prueba se conservan.

Terraform permite únicamente el override temporal 4096 MiB para CT627; el
inventario y el valor predeterminado siguen en 3072 MiB. Cada plan comprobado
cambió solo memoria de CT627, sin recreaciones ni cambios en otros recursos.
El wrapper [run-d066-pilot.py](../../scripts/run-d066-pilot.py) aplica en `finally`
el plan de retorno a 3072 MiB. No usarlo como autorización para repetir el ensayo.

Dos intentos iniciales detectaron errores del supervisor **antes de cargar Qwen**:
`pct pid` no soportado y acceso a la API original por localhost en vez de su IP
publicada. Se corrigieron y se ejecutó rollback en ambos. El tercer intento fue
el único que cargó Qwen. En total: tres ciclos 3072→4096→3072 y seis reinicios de
CT627 por el provider. Estos errores operativos no se atribuyen al modelo.

## Mediciones reales

Modelo `Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice`, revisión
`85e237c12c027371202489a0ec509ded67b5e4b5`, archivos fijados en
[model-lock](../../services/infra-voicebox/pilot-d066/model-lock.json).
Descarga directa a caché persistente: 12 archivos, 2.498.386.873 bytes, 231,67 s,
RSS máximo del descargador 75,09 MiB. Sin instanciar el modelo.
Se verificaron hashes y se liberaron páginas de esos archivos mediante
`posix_fadvise`; no se ejecutó limpieza global de caché del nodo.

| Etapa | Tiempo | RSS máximo candidata | Cgroup CT627 máximo observado |
| --- | --- | --- | --- |
| Carga | 3,81 s interna / 9,83 s API | 1,71 GiB | 2,90 GiB |
| Generación corta, interrumpida | unos 5,03 s hasta corte | 2,50 GiB | 3,54 GiB |

La instrumentación del backend confirmó CPU, atención SDPA, 402 tensores de
parámetros principales y 400 del codec en `torch.bfloat16`. El pico kernel
`memory.peak` leído antes de la parada fue 3.803.488.256 bytes (3,542 GiB);
el máximo muestreado `memory.current` fue 3.800.338.432 bytes. El RSS máximo
observado fue 2.682.695.680 bytes. El aumento de RSS de carga a inferencia fue
aproximadamente 0,79 GiB antes de completar siquiera la frase.

En el instante de máximo cgroup había 1,093 GiB de `inactive_file`; el working set
calculado `current-inactive_file` fue 2,446 GiB. Su máximo en todo el ensayo fue
2,616 GiB. Estas páginas pueden ser reclamables, pero no se puede restar toda
la caché y concluir que un minuto cabe: el presupuesto de inferencia queda sin medir.

Swap máximo del CT: 4096 bytes; `VmSwap` de la candidata: 0. Eventos `oom`,
`oom_kill` y `oom_group_kill`: 0. Journal del kernel sin OOM y Docker
`OOMKilled=false`. La salida 137 corresponde a la terminación del contenedor tras
la orden preventiva de parada y su plazo de 5 s, no a un OOM acreditado.

[Supervisor](../../services/infra-voicebox/pilot-d066/run_on_pve.py) ejecutado en
PVE fuera del CT; 89 muestras, cadencia nominal 200 ms y separación máxima
observada 2,594 s. Las cifras máximas corresponden **hasta el corte preventivo**;
no se capturó otro pico final durante los 5 s de parada antes del reinicio de
retorno. No se presentan como máximo exacto de ese intervalo no muestreado.
Tres comprobaciones de los demás targets durante el ensayo fueron satisfactorias.

La petición corta fue: «Hola, esta es una prueba controlada de narración en
español. Vamos a comprobar la estabilidad y la claridad de esta voz.»
Generación aislada `7ad72f4f-9263-40a0-b07e-649dde62a3b4`, estado final `failed`,
`Generation cancelled`, sin ruta de audio. El ensayo duró 28,76 s hasta recuperación.

## Recuperación y verificación posterior

Unidad systemd con restauración `ExecStopPost` y wrapper con retorno Terraform:
candidata detenida, original conservada y activa, Kokoro cargado. Recursos finales
verificados en PVE: 3072 MiB, swap 512 MiB, 3 CPU, disco 50 GiB. Segunda aplicación
Terraform acotada: **0 añadidos, 0 cambios, 0 destruidos**, sin otro reinicio.

Alex generó un WAV nuevo tras el rollback: 8,88 s de audio en 14,23 s observados,
24 kHz mono. [Escuchar verificación Alex](http://192.168.1.127:17493/audio/951cb9d1-af4f-4b27-afec-d16cb15d7a17).
SHA256 `29b727abe8f8929c5c5dee528110ef72b932d5917a736078cc1660ce352f051f`,
coincidente con la muestra aceptada. Cinco perfiles originales conservados.
Observación 180,06 s/7 muestras PASS, sin alertas, 49,80–49,88 % de RAM disponible,
18 Node/18 cAdvisor/19 Blackbox UP. Los hashes de configuración de los otros
17 CT y los 59 targets de Prometheus son idénticos a sus baselines. Esto acredita
las comprobaciones realizadas, sin prometer ausencia de efectos no observados.

## Retirada preparada, sin borrar datos

| Perfil rechazado D064 | ID exacto de perfil | Muestra que se conserva |
| --- | --- | --- |
| Dora (`ef_dora`) | `7b6c34d0-861a-4001-ba37-aa6cb379b6e9` | `604dd48d-93f7-4ea8-8447-404a44908edf` |
| Santa (`em_santa`) | `6be85095-8500-44cb-8f62-bab88f475d95` | `c98308bf-db33-4008-b14f-79ee5477c176` |
| Emma (`bf_emma`) | `5850a2d6-7349-4235-9e85-c3d92819281b` | `ee2fe00b-62c7-4cf3-a4e5-e74393e96736` |

No se ejecutó DELETE ni limpieza. Alex `250f2938-c396-47e8-8b75-0bf9179d0252`
y el perfil original D063 `285b5291-74b8-406d-b7fe-56c31c4e21cd` quedan protegidos.
La retirada futura debe volver a verificar estos IDs, conservar el backup y
esperar autorización de eliminación; este informe solo presenta los identificadores.

## Recomendación propuesta y siguiente paso

**Optimizar más; no mantener Qwen activo en producción todavía.** BF16/SDPA permite
cargarlo realmente dentro de 4 GiB, por lo que descartarlo solo por pesos FP32
sería incorrecto. La inferencia no superó el criterio de seguridad de este piloto.
Antes de otro ensayo, estudiar un único proceso servidor (el original vacío aún
ocupaba unos 316 MiB), atribución de caché/codec y memoria de inferencia. No se
propone cuantización como solución ya compatible ni se promete ahorrar toda la
caché. Medir una generación corta completa sigue siendo requisito antes de 60 s.

No se ejecutan más cambios productivos bajo esta intervención. La candidata
queda parada; Kokoro/Alex siguen en servicio. Próximo paso de Fase 7.4: revisar
este resultado y, si procede, aprobar una nueva propuesta concreta de optimización
con el mismo techo de 4 GiB. Qwen Base queda fuera del ensayo y sin validar.

## Evidencias

- [Resultado del piloto](evidence/2026-11-10-d066-pilot-result.json),
  [resumen de mediciones](evidence/2026-11-10-d066-measurement-summary.json),
  [muestras](evidence/2026-11-10-d066-samples.jsonl),
  [descarga](evidence/2026-11-10-d066-download.json).
- [Rollback RAM](evidence/2026-11-10-d066-ram-rollback.json),
  [auditoría de recuperación](evidence/2026-11-10-d066-recovery-audit.json),
  [Alex](evidence/2026-11-10-d066-alex-recovery.json),
  [preservación](evidence/2026-11-10-d066-preservation.json),
  [observación](evidence/2026-11-10-d066-observation.json).

Validación local: `terraform fmt -check` y `terraform validate` PASS, 31 tests
(inventario y provisioning) PASS, compilación Python, sintaxis shell, enlaces locales
y `git diff --check` PASS. [Registro](evidence/2026-11-10-d066-validation.json).
[Restauración del backup](evidence/2026-11-10-d066-restore.json) y
[manifiesto de retirada sin ejecutar](evidence/2026-11-10-d066-retirement-plan.json).

Planes Terraform, backups, bases de datos y logs completos se mantienen privados;
no se publican estados ni secretos. Los cambios previos ajenos se conservan.
