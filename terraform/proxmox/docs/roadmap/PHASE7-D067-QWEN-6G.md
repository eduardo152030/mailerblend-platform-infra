# Fase 7.4 — Qwen con 6 GiB y preparación de tres identidades

Estado de cierre: ensayo y recuperación **DONE con incidencias documentadas**;
aceptación Qwen/femenina **BLOCKED**, voz personal pendiente de grabaciones y
validación Base. No se declara completado el objetivo de tres voces operativas.

## D067 — ensayo cerrado; aceptación Qwen y femenina pendientes

2026-11-10 (Europe/Madrid). Autorizado solo CT627: comprobar capacidad del host,
backup/rollback, plan Terraform exclusivo y ampliación 3072→6144 MiB; 3 CPU,
512 MiB swap y disco 50 GiB conservados. Piloto con candidata BF16/SDPA D066,
corta→30 s→60 s; detener a 5,5 GiB, OOM, swap excesivo, inestabilidad o afección
externa. Un modelo residente; imagen original y todos los datos conservados.
Preparar candidatos masculino/femenino sin aceptación auditiva, clonación personal
pendiente de grabaciones reales, contrato API sin integrar el pipeline. Qwen Base
se evalúa separadamente, sin asumir memoria ni crear voz ficticia del propietario.
No otros LXC, borrados, pipeline, commit ni push. [Informe](PHASE7-D067-QWEN-6G.md).


## Preparación comprobada

Host Proxmox:7,82 GiB MemAvailable antes de ampliar; host total15,50 GiB. Se exige
más de6 GiB disponibles antes de aplicar; durante el ensayo se detiene por debajo
de1,5 GiB disponible. Solo CT627 cambia3072→6144 MiB;3 CPU,swap512,disco50.
Plan exclusivo revisado y rollback3072 preparado. Backup previo SHA256
`918456a7bf1016c85bd4572d26be2418386221f5501d483c3da274c14a985460`,
`/opt/voicebox/backups/d067-before.tar.gz`, copia privada fuera dePVE y restauración
comprobada:36 archivos,6 symlinks confinados,SQLiteok,10 audios completados.
No incluye caché Qwen aislada, conservada con su model-lock y reutilizada sin descarga.

La imagen candidata es la de D066, exactamente
`sha256:4de8a649d267fb9f4fa9d7049f264a1e6896718c7892f70706abb4a46d75430d`.
La original se conserva, sin sustituir datos productivos; candidata con5200 MiB,
2 CPU y sin swap adicional. Un único modelo cargado. El supervisor corre en PVE,
con restore independiente systemd y wrapper de retorno RAM en fallo.

Incidencias de preparación: un primer intento cargó correctamente, pero buscó
`d067-load-facts.json`; la candidata escribe `d066-load-facts.json`. Se detuvo antes
de generar, restaurando3 GiB. Se corrigió esa referencia. En la siguiente preparación,
el wrapper reutilizó el nombre `args` para una lista Terraform y falló antes de
iniciar la unidad; no ejecutó su finally de rollback. Se corrigió la colisión,
se comprobó el estado real6144 y el plan de retorno, y se reanudó sin otro reboot
ni repetir una generación. Son errores de automatización, no fallos de memoria
ni del modelo. Evidencia de ambos se conserva; no se ocultan como preflights PASS.

## Base0.6B para clonación: evaluación separada

La [tarjeta oficial](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-0.6B-Base)
confirma clonación desde grabaciones de referencia. CustomVoice usa presets; no
se utiliza como clonación personal. En el fork real `pytorch_backend.py`, Base
CPU usa FP32 y llama `create_voice_clone_prompt` con audio, transcripción y
`x_vector_only_mode=False`. La subida de muestras valida y persiste audio sin
cargar Base. La generación del prompt y la síntesis sí necesitan el modelo.

Cabeceras safetensors leídas sin descargar pesos: revisión
`5d83992436eae1d760afd27aff78a71d676296fc`,914.643.008 parámetros principales
más170.557.441 del codec. Pesos FP32:4.340.801.796 bytes (4,043 GiB); BF16
hipotético de ambos:2.170.400.898 bytes (2,021 GiB). No son medidas de RAM.
Los prompts de referencia, cachés y generación tienen necesidades distintas a
CustomVoice. Carga e inferencia Base **NO MEDIDAS**; no se afirma que quepan en6 GiB.
Parche Base BF16/SDPA preparado localmente, **no construido ni desplegado**; no se
carga Base FP32 ni se usa un audio inventado. Falta validar ese backend con
muestras reales y presupuesto propio.

[Procedimiento de grabación, almacenamiento privado, clonación y contrato API](../../services/infra-voicebox/VOICE-PROFILES.md).
`personal` sigue con IDnull. Originales fuera del volumen API,0700/0600,
y backup actualizado para preservarlos cuando existan. No se han recibido ni
guardado grabaciones personales. La ACL LAN no proporciona autenticación por usuario.

## Perfiles candidatos

- `male_es`: `916ce396-1b15-4621-b63c-5eaf49f03b74`, **ES Male — Narrator**,
  Kokoro `em_alex`; Alex original aceptable, nueva candidatura narrativa pendiente
  de muestra y revisión. No se altera el perfil Alex original.
- `female_es`: `7e127dfb-8e46-42c4-8b26-c88d0c7c65ae`, **ES Female — Narrator**,
  CustomVoice `Serena`; nativa china, candidata experimental en español, sin
  acreditación de acento peninsular/edad ni operatividad hasta validar el motor.
- `personal`: IDnull, pendiente de grabaciones reales y validación Base.

Los tres roles pueden guardarse simultáneamente sin mantener tres modelos en RAM.
[Catálogo con IDs reales](../../services/infra-voicebox/voice-identities.yml).
Dora/Santa/Emma rechazados conservados; no se eliminó ningún perfil ni muestra.

## Resultado medido del piloto

Ensayo efectivo iniciado15:06:37 CET (14:06:37 UTC), duración624,02 s hasta
recuperación. Carga interna3,874 s / API9,843 s. Se confirmaron402 tensores de
parámetros principales y400 del codec en BF16, atenciónSDPA yCPU. La petición
corta fue la misma deD066,21 palabras; tras600,47 s de fasecorta no había WAV.
Se detuvo por **plazo operativo configurado**, no por memoria ni pérdida deAPI.
No es prueba de que no pudiera terminar con otro plazo, ni validación de su texto,
acento o calidad. No se ejecutaron los pasos de30/60 s.

| Medición | Resultado |
| --- | --- |
| Pico `memory.current` muestreado | 4.527.128.576 bytes =4,216 GiB |
| `memory.peak` antes de parada | 4.529.487.872 bytes =4,219 GiB |
| `memory.peak` tras parada | 4.532.015.104 bytes =4,221 GiB |
| RSS/HWM máximo observado | 3.250.225.152 bytes =3,027 GiB |
| Swap máximo CT / proceso candidato | 4096 bytes /0 |
| OOM /oom_kill /oom_group_kill | 0 /0 /0 |
| CPU consumida durante muestras | 680,14 CPU-s; media1,096 núcleos |
| CPU media sobre3 vCPU CT | 36,53 %; candidata limitada a2 CPU |
| Muestras | 3347; nominal200 ms, mayor separación2,401 s |
| Comprobaciones de otros targets durante piloto | 62 PASS |
| Audio corto /30 s /60 s | Sin WAV /NO EJECUTADO /NO EJECUTADO |

El cgroup incluye páginas de archivos y otros procesos del CT; no equivale al
RSS ni a memoria irreclamable del modelo. El máximo working set calculado fue
3.761.270.784 bytes. La diferencia RSS entre máximo de carga1.831.112.704 y máximo
de la corta3.250.225.152 fue1.419.112.448 bytes (1,322 GiB), sin síntesis completa.
No se presenta esa diferencia como presupuesto cerrado de inferencia.
La candidata tenía5200 MiB sin swap adicional y2 CPU; no se ensayó otro número
de hilos. El CT conservó3 vCPU. No se atribuye el timeout a un cuello concreto sin
perfilado: CPU BF16 emulado, decodificación/terminación u otros costes son hipótesis.

Advertencia observada: `flash-attn is not installed`. No se instaló FlashAttention
CUDA; la instrumentación confirmó la rutaCPU/SDPA prevista. No hubo traceback de
inferencia antes del timeout. Generación`36e9000a-f876-48ca-a935-02b04ea459e4`,
estado final`failed`, error`Generation cancelled`, ruta vacía. La salida137 del
contenedor corresponde a la parada controlada con plazo5s, `OOMKilled=false`;
no hay OOM en el journal del kernel durante toda la intervención.

## Recuperación: alcance real y limitaciones de automatización

La unidad restauró automáticamente la imagen original y Kokoro, deteniendo antes
la candidata. El plan guardado de vuelta a3072MiB falló: durante el ensayo se
actualizó el manifiesto de inventario y Terraform detectó `file()` inconsistente.
Se generó y revisó otro plan, **solo memoria627 6144→3072, swap512**, aplicado con
éxito. No fue un rollbackRAM totalmente automático: precisó intervención del
agente. Se corrigió localmente el wrapper para renovar y volver a revisar un plan
RAM exclusivo si falla el guardado; esa rama nueva no se reprobó de extremo a
extremo con otro piloto. No se oculta este fallo de automatización.

D067 hizo **dos ciclos3072→6144→3072**, cuatro reinicios de
CT627 por cambios de RAM. El segundo ciclo se reanudó tras corregir el wrapper,
sin repetir ampliación ni reinicio. Hubo además una recreaciónDocker deVoicebox,
con backup fresco y restore-check previo. No se sustituyó la imagen original.
Se conservaron7 perfiles con UUID,25 hashes dearchivos ySQLite íntegra. La segunda
aplicaciónCompose conservó ID/StartedAt/RestartCount: sin recreación ni reinicio.

Backup previo a recreación: SHA256
`f8c5c5766527763f2c03fdc5da864a066c1e527c91f2ba1a1e890ecd053e47df`, también
restaurado fueraPVE,36 archivos,6 enlaces confinados,10 audiosprevios completos.
Tras generar las muestras finales, siguen persistentes en el volumen productivo;
las copias WAV de revisión están en el directorio privado de recuperación.

Alex original:8,88 s deaudio,14,17 s de generación observada.
[Escuchar Alex](http://192.168.1.127:17493/audio/912e1490-43d1-4ef6-9907-7005587e1c3e).
Candidato masculino:8,88 s,6,05 s observados conKokoro ya caliente.
[Escuchar ES Male — Narrator](http://192.168.1.127:17493/audio/597aaabb-5688-4df1-bd1c-18d9c6144afd).
Ambos SHA256`29b727abe8f8929c5c5dee528110ef72b932d5917a736078cc1660ce352f051f`:
es la misma vozAlex, no una voz nueva presentada engañosamente como distinta.
La nueva candidatura narrativa, acento exacto y edad aparente siguen pendientes
 deescucha. Serena queda solo como registro experimental bloqueado sinmuestra;
no se sustituye porDora/Emma ya rechazadas ni se marca como voz deEspaña aceptada.

## Validaciones y pendientes

Recursos finales: **3CPU,3072 MiB,swap512,50 GiB**. El estado de6 GiB se comprobó
en el piloto, pero no se mantiene tras su fallo conforme rollback autorizado.
Otros17LXC gestionados intactos; los26 archivosPVE ajenos, incluidas plantillas,
conservan sus hashes. Los59 targets dePrometheus conservan labels/scrapeURLs yUP.
GrafanaFleet/Details yUIVoicebox renderizan; consultas sinerrores. No hay cambios
en el pipeline ni aceptación humana de nueva voz. No se hizo commit ni push.

| Criterio | Estado |
| --- | --- |
| CT6276 GiB | Ensayado; final3 GiB porrollback |
| AudioQwen real | FAIL timeout600s; no validado |
| Narración30/60s ytiempo por minuto | No ejecutadas; no medido |
| Kokoro/Alex | PASS con audio real tras rollback/recreación |
| Masculino | Perfil+muestra PASS técnico; escucha pendiente |
| Femenina deEspaña | BLOCKED: candidataSerena sinmuestra ysinacento validado |
| Personal | Procedimiento/almacenamiento preparados; grabación/ID/motor pendientes |
| Persistencia tras reinicio/recreación | PASS para7 perfiles,25hashes ySQLite |
| OOM/nuevos cambios enotrosCT | SinOOM; hashesotrosCT idénticos |
| CoberturaPrometheus/Grafana | PASS, evidencia independiente |

## Recomendación y siguiente paso de Fase7.4

**Mantener Kokoro/Alex y no promover esta candidata Qwen.** Aumentar RAM no resolvió
la falta de audio en el plazo del ensayo. No recomendar másRAM a partir de estos
datos. Antes de otro piloto, diagnosticar por qué no termina la frase y perfilar
CPU/decodificación con un presupuesto explícito; cualquier alternativa deprecisión
debe revisar memoria propia. Los pesosBase yCustomVoice similares no acreditan
el mismo consumo en clonación. El hardware no se declara incapaz por un cálculo
FP32 ni por este timeout; la configuración ensayada sí queda sinvalidar.

Siguiente paso: revisión de la muestra masculina por el propietario y decisión
sobre una nueva propuesta de diagnóstico Qwen. La vozfemenina y la clonación real
quedan pendientes, no aceptadas ni dispensadas. No hay nueva prueba automática
trasHALT, ni eliminación de voces, ni integración delpipeline.

## Evidencias y recetas

[Resultado](evidence/2026-11-10-d067-pilot-result.json),
[mediciones yhash de muestras crudas privadas](evidence/2026-11-10-d067-measurement-summary.json),
[Base presupuesto separado](evidence/2026-11-10-d067-base-budget.json),
[incidencias deautomatización](evidence/2026-11-10-d067-automation-incidents.json),
[retornoRAM](evidence/2026-11-10-d067-ram-result.json),
[recuperación ypersistencia](evidence/2026-11-10-d067-recovery.json),
[auditoría](evidence/2026-11-10-d067-audit.json),
[identidades](evidence/2026-11-10-d067-identities-final.json),
[restoreprevio](evidence/2026-11-10-d067-restore-before.json),
[restorepre-recreación](evidence/2026-11-10-d067-restore-before-recreate.json),
[Grafana/UI](evidence/2026-11-10-d067-browser.json).
[Compose/supervisor](../../services/infra-voicebox/pilot-d067/README.md),
[clienteAPIsin integración](../../scripts/voicebox-narrate.py),
[procedimiento privado](../../services/infra-voicebox/VOICE-PROFILES.md).
Planes, bases dedatos, transcripciones ybackups completos se conservan privados.

## Cierre de validación

Observación posterior **180,06 s/7 muestras PASS**, sin alertas FIRING/PENDING,
18 Node/18 cAdvisor/19 Blackbox UP. Aplicación Terraform de Notes modificó solo
`description` de627, sin memoria ni otrosCT; segunda aplicación **0/0/0**.
Contenedor original conserva su ID después de Notes. Cliente independiente API
probado realmente con `male_es`: generación
`17d88dce-315f-48ae-8078-13793f4747bd`, WAV recuperado sin usar el pipeline.
Esto prueba selección/perfil/generación/descarga del cliente paraKokoro, no para
motores bloqueados ni concurrencia global. 31 tests locales PASS, formato y
validaciónTerraform, Python, shell, enlaces ydiff-check PASS.

Backup final después de los13 audios completados: SHA256
`1835532db90e731b434a8edd4115ab0fad362562110b854d0719ce3c36f9683f`,
`/opt/voicebox/backups/d067-final.tar.gz`, copia fueraPVE y restore aislado PASS:
39 archivos,6 symlinks confinados,SQLiteok,13WAV. Originales personales aúnvacíos;
no se afirma restauración de grabaciones que no se han proporcionado.

[Observación](evidence/2026-11-10-d067-observation.json),
[idempotenciaTerraform](evidence/2026-11-10-d067-terraform-final.json),
[permisos privados](evidence/2026-11-10-d067-private-storage.json),
[cliente API](evidence/2026-11-10-d067-api-client.json),
[backupfinal](evidence/2026-11-10-d067-backup-final.json),
[restorefinal](evidence/2026-11-10-d067-restore-final.json),
[validación](evidence/2026-11-10-d067-validation.json).
