# Fase 7.4 — D-068: Voicebox, 7 GiB, Qwen y perfiles de narración

2026-11-10, Europe/Madrid. Las evidencias conservan sus marcas UTC de PVE.
**Fase 7.4 IN PROGRESS.** Ampliación y voces operativas: DONE técnico; Qwen:
BLOCKED sin audio validado; aceptación auditiva y clonación personal pendientes.
No se declara completada una clonación sin grabaciones reales.

## Resultado y recursos finales

CT627 operativo en http://192.168.1.127:17493, privado LAN. Recursos efectivos:
**3 vCPU, 7168 MiB RAM (7 GiB), 512 MiB swap y 50 GiB**. Solo CT627 cambió memoria
3072→7168 MiB mediante plan Terraform revisado: un update, sin sustitución ni otros
campos. El provider reinició este CT una vez; no se recreó el LXC.

Antes de ampliar: host15,50 GiB, MemAvailable8,25 GiB; PSI avg10 sin presión actual,
con presión reciente registrada en avg60/300 y swap histórico del host. `vmstat`
mostró swapout0 en los intervalos y CPU mayoritariamente disponible. Se monitorizó
la evolución; no se confundió swap histórico con crecimiento del piloto.

Se mantiene el objetivo7 GiB tras liberar los workers: la presión se normalizó,
el host conservó margen y los17 CT restantes permanecieron operativos. El retorno
a3 GiB queda para inseguridad persistente de recursos, no para forzar otro intento.
No se relajaron los umbrales de los ensayos Qwen tras sus paradas. La política
inicial de retorno automático a3 GiB ante cualquier veto se afinó con las medidas:
parada/restauración inmediata del software y retorno de recursos si persiste el
riesgo. La ampliación7 GiB estaba expresamente autorizada por el propietario.

En Docker se conserva CPU3 y el presupuesto de swap400 MiB: RAM6200 MiB y
RAM+swap6600 MiB, dentro del CT7 GiB/swap512. Elevar el techo de la aplicación evita
intentar la futura carga Base bajo el antiguo límite1600 MiB. No es una reserva de
RAM ni acredita viabilidad de inferencia Base. IaC bloquea >7168 MiB o cambios
CPU/disco de627 sin cambiar explícitamente la política autorizada.

## Qwen: diagnóstico finito y causa del timeout

Fuentes revisadas: informes D065/D066/D067, inventario, runbooks de provisioning y
recuperación, código real instalado de qwen-tts y del fork. Runtime observado:
Torch2.8.0+cpu, Transformers4.57.3, qwen-tts0.1.1, CPU AVX2. No se atribuye a la RAM
el timeout deD067: **los600 s eran el plazo del supervisor externo**, no un timeout
HTTP ni una excepción de backend observados.

Se instrumentaron importación/runtime, carga, dtype real, hilos, llamadas del
talker y predictor, logits finitos, rango deEOS, producción de códigos y entrada/
salida del codec. Snapshot CustomVoice0.6B fijado:
`85e237c12c027371202489a0ec509ded67b5e4b5`; caché persistente ya descargada, sin
red ni nueva descarga del modelo. No hubo otro modelo TTS residente durante cada
probe: Kokoro se descargó de RAM y se restauró al terminar.

Límites definidos antes de inferir: cgroup6,5 GiB, incremento swap64 MiB, OOM,
host con menos de1,5 GiB disponible o PSI `full avg10 >=2%`,45 s sin eventos de
progreso y plazo diagnóstico120 s. Supervisión fuera del CT y restauración systemd
independiente. Muestreo nominal200 ms; las separaciones reales están en las
muestras privadas y el resumen, sin prometer vigilancia instantánea.

El texto diagnóstico fue el solicitado para PruebaA:
«Hola, soy una voz generada mediante inteligencia artificial.» Los probes limitaron
la carga a16 tokens para comparar etapas; esa salida truncada **no equivale a
una PruebaA completa ni se entrega como narración válida**.

| Configuración | Carga interna | Progreso real | Motivo de parada |
| --- | --- | --- | --- |
| Generador y codec BF16, SDPA,2 hilos/interop1 | 1,42 s | 15 frames de códigos en9,67 s; entrada al codec a11,09 s; logits finitos | PSI full avg10=2,51%; worker detenido antes de terminar codec |
| Generador BF16, codec FP32, SDPA | 3,85 s, incluida conversión codec0,64 s | 12 llamadas talker y180 predictor en el último evento | Swap CT creció hasta80,94 MiB, sobre el umbral64 MiB |

En el primer recorrido no se observó deadlock del generador: produjo códigos y
llegó al decoder. SDPA ejecutó operaciones reales y los logits muestreados fueron
finitos. No se demuestra terminaciónEOS ni fidelidad acústica de una frase completa.
En el segundo no se terminó la generación de códigos; no se midió el codecFP32
completo. No se presenta el cambio de precisión como una optimización validada.

**La causa completa de los600 s no queda determinada.** El generador progresa en
la ventana observada y el codec se alcanzó; las protecciones interrumpieron antes
de reproducir o completar el recorrido largo. No se prueba incompatibilidad BF16,
fallo de SDPA, saturación de las3 CPU, fallo de API ni deadlock global. No se
repitieron diez minutos sin información diagnóstica adicional.

| Consumo de los probes Qwen | Máximo observado |
| --- | --- |
| Cgroup, incluida parada del segundo worker | 5.336.653.824 bytes =4,97 GiB |
| RSS/HWM máximo muestreado | 2.774.306.816 bytes =2,58 GiB |
| Swap CT | 84.869.120 bytes =80,94 MiB |
| VmSwap de los workers muestreados | 0 |
| OOM /oom_kill /oom_group_kill | 0 /0 /0 |

El cgroup incluye caché de archivos y procesos ajenos al worker dentro de627; no
es el RSS del modelo. El crecimiento de swap del CT no se atribuye sin prueba al
PID candidato, cuyo VmSwap era0. Había más de7 GiB disponibles en el host durante
la parada por PSI; presión de memoria no implica por sí sola agotar la RAM física.
La política conservadora detuvo el trabajo igualmente. Tras detenerlo, la presión
volvió por debajo del umbral. No se forzó FP32 completo ni una nueva ruta eager.

Un microbenchmark independiente, sin pesos, comparó FP32/BF16/FP16 con1/2/3 hilos
bajo cuota de2 CPU. Linear ySDPA devolvieron resultados finitos. FP32 fue más rápido
en el caso de48 filas; BF16 pudo ser más rápido en el caso de1 fila. Es evidencia
sintética limitada, no un benchmark del modelo ni una selección definitiva de hilos.
La configuración instrumentada real registró2 hilos e interop1.

| Prueba solicitada | Resultado |
| --- | --- |
| A: frase mínima completa | No validada: solo probes finitos, interrumpidos por seguridad; sin WAV completo |
| B:15–30 s | NO EJECUTADA, dependía deA |
| C:120–150 palabras/~60 s | NO EJECUTADA, dependía deB |
| Tiempo por minuto yRTF Qwen | NO MEDIDOS; no extrapolados |

CustomVoice CPU queda bloqueado con un error explícito en la imagen operativa.
La imagen candidata BF16 anterior y su caché se conservan. No se borraron datos,
no se aumentó por encima de7 GiB ni se dejó un worker de Qwen activo.

## Voces reales para revisión

Se conserva Alex original y la muestra protegida
[597aaabb-5688-4df1-bd1c-18d9c6144afd](http://192.168.1.127:17493/audio/597aaabb-5688-4df1-bd1c-18d9c6144afd),
con el mismo SHA256 `29b727abe8f8929c5c5dee528110ef72b932d5917a736078cc1660ce352f051f`.

| Rol | Perfil real | Motor y muestra final |
| --- | --- | --- |
| `male_es` | `916ce396-1b15-4621-b63c-5eaf49f03b74`, ES Male — Narrator | Kokoro `em_alex`:7,56 s de audio,11,15 s observados tras cambio de motor. [Escuchar](http://192.168.1.127:17493/audio/43cee380-e68a-45d7-9080-65dd708c4889) |
| `female_es` | `6ab4fe0a-5a4f-4dc0-9b84-71b5173edfeb`, ES Female — Narrator · Piper es_ES | Piper1.8.0 `es_ES-sharvard-medium:F`, hablante1:7,24 s,2,83 s observados. [Escuchar](http://192.168.1.127:17493/audio/6c6fa9a0-54f9-4182-ae9d-7d2efea7de71) |
| Alex original | `250f2938-c396-47e8-8b75-0bf9179d0252` | Kokoro:7,56 s,5,26 s con modelo caliente. [Escuchar](http://192.168.1.127:17493/audio/692e2efb-5813-4ba8-8f51-b3f7942c3318) |
| `personal` | `null`, todavía no creado | Código y procedimiento preparados; grabaciones reales y validación pendientes |

El preset femenino procede de un checkpoint etiquetado `es_ES` y hablante femenina
según su [tarjeta oficial](https://huggingface.co/rhasspy/piper-voices/raw/main/es/es_ES/sharvard/medium/MODEL_CARD).
No se deducen país, edad ni calidad a partir del nombre. La edad aparente25–45,
el acento percibido, la naturalidad y la aceptación siguen pendientes de escucha.
La voz masculina utiliza Alex; no se vende como una voz nueva distinta de Alex.

Piper se eligió tras revisar alternativas: Kokoro solo aporta una femenina
española en su [catálogo](https://huggingface.co/hexgrad/Kokoro-82M/blob/main/VOICES.md),
Dora, ya rechazada; no se rebautizó como nueva candidata. Serena depende de Qwen y
no se ensayó tras el veto anterior. Su perfil sigue conservado:
`7e127dfb-8e46-42c4-8b26-c88d0c7c65ae`. Tampoco se borraron Dora/Santa/Emma D064
ni el perfil original D063. La alternativa Piper es un motor real integrado,
no un preset ficticio ni un identificador inventado.

Se descargó exactamente el modeloPiper77MB, su configuración yMODEL_CARD por
revisión yhash; no el repositorio entero. Modelo/corpusCC-BY3.0 y runtimeGPL3,
fuentes y créditos conservados. Piper entregaWAVPCM16 mono22050Hz; Kokoro24000Hz.
La muestra femenina fue reproducible en pruebas aisladas y producción, SHA256
`2d7e689304d2af7ba42c069d524419adf1b6cf48d15890a6661e5c84edbf1c00`.

## Imagen, memoria, concurrencia y recuperación

Imagen operativa: `local/voicebox:8af7efe62fab-piper-d068-r2`, índiceOCI
`sha256:c86ea2658d6ab7c02acf2b0a39fd483f17ca70b35d1471fce7010cec47358543`.
Base original conservada:
`sha256:7f2e6f7e6a2d09c77ebd35424a7641249e51b8ff0374bc9c4acb1f7393cfcd4c`.
Código base8af7efe62fab8d33e2a5dfbedabaa45f68a5184f +overlayD068 explícita;
no se presenta la imagen parcheada como checkout sin cambios.

La overlay añade Piper, esquemas/presets API y disponibilidad de su caché local,
serialización de trabajos TTS, descarga del motor anterior y rechazo409 de
mutaciones de modelo durante inferencia. Solo dos wheels fijados y comprobados,
sin resolver/actualizar otras dependencias ni instalarCUDA. ONNXRuntime existente
1.31.1, Piper1.8.0, pathvalidate3.3.1. `deploy.sh` verifica imagen, fuentes,
wheels ypesos antes de reconciliar el único servicio.

Prueba real con dos generaciones enviadas seguidas: ambas completadas, máximo
**un modelo TTS cargado**, cambio de modelo concurrente rechazado con409.
El cliente independiente `voicebox-narrate.py female_es` generó yrecuperó elWAV
`9b945d8f-7ec4-454e-a6ec-17165ecdb0f6`. No se tocó el repositorio delpipeline.
Dos ejecuciones de `deploy.sh` conservaron ID,StartedAt yRestartCount delcontenedor.

El backup previo al cambio deimagen se restauró fueraPVE antes de promoverla.
La activación tuvo recuperación systemd independiente; una primera activación
se revirtió automáticamente cuando falló la comprobación adicional de Base.
Se conservaron el perfil nuevo y sus audios durante ese rollback. La corrección
posterior importó SessionLocal de su módulo de sesión ya inicializado; el guard
real de referencias quedó probado con el mensaje esperado antes de cargar Base.
La versiónr2 pasó de nuevo Piper,Kokoro yesa comprobación antes de quedar activa.

Se guardó la receta/imagen/fuentes exactas de la última versión estable para
rollback coordinado, sin borrar DB ni volúmenes. Una recuperación de SQLite exige
usar los datos/referencias/audio de la misma captura. No se hizo destroy/prune ni
se modificaron los otros17LXC. La validación técnica no sustituye la escucha humana.

## Clonación personal: preparado, no DONE

Motor previsto: [Qwen3-TTS Base0.6B](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-0.6B-Base),
engine `qwen`, tipo `cloned`; CustomVoice yPiper son presets y no clonan alpropietario.
Base no se descargó ni cargó. Su checkpoint y11 archivos están fijados para una
única descarga futura, después de comprobar que existen referencias reales.
El consumo de carga/inferencia, prompt de voz y fidelidad de Base **no se midieron**.

Implementado: validación WAV/duración/RMS/clipping, originales exactos privados
0700/0600 fuera del volumenAPI, subida multipart con transcripción, creación de
UUID real solo con grabaciones, actualización automática del catálogo persistente,
carga de Base0.6B BF16/codecFP32 desde ruta local fijada, prueba corta controlada,
recuperación deWAV, guard de recursos y retorno aKokoro. La ruta del monitor se
comprobó en lectura; las ramas con vozreal no se presentan como ejecutadas.

Guía: **2–3 WAV de10–20 s**, PCM16 mono24/44,1/48kHz, habitación silenciosa,
una persona, sin música ni saturación, transcripción literal por toma. Entregar
por ruta privada/SSH fueraGit. Procedimiento completo y comandos en
[VOICE-PROFILES](../../services/infra-voicebox/VOICE-PROFILES.md).
La clonación sigue IN PROGRESS hasta una prueba con grabaciones reales del dueño.
No se usaron grabaciones de terceros ni un preset en nombre de Eduardo.

Otros motores revisados, no descargados: [LuxTTS](https://huggingface.co/YatharthS/LuxTTS)
anuncia clonaciónCPU y licenciaApache2, pero el material revisado etiqueta inglés;
español y consumo en este fork no se validaron. [ChatterboxTurbo](https://huggingface.co/ResembleAI/chatterbox-turbo)
es inglés; la variante Multilingual es otro checkpoint y backend a evaluar, no
un reemplazo automático. No se asumió que todos los modelos de clonación comparten
memoria o compatibilidad ni se hicieron descargas indiscriminadas.

## ContratoAPI y persistencia

[Catálogo real](../../services/infra-voicebox/voice-identities.yml): `male_es`,
`female_es` y `personal`. Un IDnull bloquea la petición; no hay sustitución devoz.
`POST /generate`: UUID real, texto, idiomaes, engine ymodel_size0.6B paraBase.
Respuesta asíncrona conid; consultar `GET /history/{id}` y recuperar
`GET /audio/{id}` solo tras `completed`. Persistir id, perfil yhash delWAV.
Gestionar400/404/422,409 de modelo ocupado y`failed/error`; no repetirPOST tras
timeout sin reconciliar elID. Frecuencia real en cabeceraWAV; no suponer24kHz.

La integración con Pipeline_videos_modulares es únicamente arquitectura/contrato:
**el repositorio delpipeline no se modificó**. El APIclient vive eninfra y fue
probado paraPiper/Kokoro. La interfaz muestra el nuevo perfil; no se declara
probada una ampliación completa del selectorfrontend ni aceptación de suvoz.

La API sigue sin autenticación individual, limitada aLAN por la ACL existente;
CORS no autentica usuarios. Originales privados no se sirven porHTTP; referencias
yexportaciones requieren red confiable. No se promete aislamiento porusuario que
esta instalación no implementa. Nada de grabaciones personales/SQLite/backups va
 aGit ni aubicaciones públicas. Modelos dePiper ycatálogo se guardan en elvolumen
persistente; Base futuro usaHFpersistente, sin descargas repetidas.

## Backups y evidencias de restauración

- Previo aRAM: SHA256 `45cab1304be6dd838ebf18a8c65b177b41748c13ae73dae740f818be72bcf2ea`,
  restore aislado39 archivos,6 enlaces confinados,SQLiteok,13WAV.
- Previo aPiper: `f9c9311f2d879c9be6ac78751d4b150572bc035f2311acafe439ac0d7657febd`,
  restore42 archivos/13WAV.
- Captura anterior a recuperación: `/opt/voicebox/backups/d068-final.tar.gz`, SHA256
  `1ea4bdb55406a459df29302be81c07e8b605e9d7de657190e8eff8194550b84e`.
  Copia fueraPVE yrestore **71 archivos,6 enlaces confinados,SQLiteok,24WAV**,
  incluidos22050/24000Hz. Overlay, ruedas, guías y flujoowner incluidos.
- **Definitivo tras recuperación:** `/opt/voicebox/backups/d068-preserved-final.tar.gz`,
  SHA256 `3ea7e797dd74daa89f90cfd0e78adcd5bbd8be857c2015e46deedf3424da6b7f`.
  Copia fueraPVE yrestauración **72 archivos,6 enlaces confinados,SQLiteok,25WAV**
  a22050/24000Hz. Los13 audios originales coinciden porhash y los12 nuevosIDs
  registrados siguen completados. No se presenta la captura de24 como definitiva.

- Imagenr2 exportada fueraPVE:1279003039 bytes, SHA256
  `18cdf4a57413ab9b285685ae23f444935bdc4da4dd1fb70d86c5005f6098f5d1`,
  **27 blobsOCI verificados**. El IDDocker29 es el digest delíndiceOCI, no eldel
  blobconfig; elverificador usa elíndice ycomprueba todos losblobs.

Archivos privados del equipo administrador:
`~/.local/share/mailerblend-recovery/voicebox-d068/`, directorio0700.
La imagen original sigue exportada/verificada en elbundleD063 yconservada enDocker.
No hay grabaciones personales, por lo que no se afirma haberlas restaurado.

## Recuperación de una muestra original detectada ausente

La comparación final conel backup inicial detectó ausencia de la generación D063
`5385d04b-49fa-4b0f-a001-1cebaf55b854`, suWAV ymetadatos relacionados. El perfil
original seguía presente. No se emitió ningúnDELETE en esta intervención. No se
ha determinado la causa; la revisión no identificó una retención automática y
los logs de contenedores previos ya retirados no permiten atribuir elborrado.
No se culpa a una migración, aotrocliente ni alpropietario sin evidencia.

Se guardó otra copiaSQLite previa a la recuperación yse restituyeron exclusivamente
la fila original, sus versiones yelWAV verificado delbackup inicial. No se revirtió
laDB completa ni se sobrescribieron nuevos registros. FK/integridadSQLite PASS;
API/historial devolvieron elUUID original yelSHA256 esperado
`d53665d3932c4b96fe7497587f57215e70b0b2cf8a5c9a290896665961cf2cfe`.
Los24 registros existentes se conservaron yel total restaurado es25 audios.

[Procedimiento reproducible](../../scripts/restore-voicebox-d068-sample.py),
[resultado](evidence/2026-11-10-d068-sample-recovery.json),
[preservación completa](evidence/2026-11-10-d068-generation-preservation.json),
[backup definitivo](evidence/2026-11-10-d068-backup-preserved-final.json),
[restore definitivo](evidence/2026-11-10-d068-restore-preserved-final.json).
Una nueva observación180s/7muestras después de recuperar fuePASS. Elorigen de la
incidencia sigue abierto; la ausencia no se oculta como preservaciónininterrumpida.

## Incidencias y límites

Los primeros probes detectaron errores de preparación antes de inferir: permisos
por cambio deusuario delentrypoint, cachéNumba/HOME yconsulta remota deltokenizer
conHFoffline. Se resolvieron con usuario/caché explícitos ycheckpoint local fijado;
no se confundieron con fallos de TTS. Se conservaron resultados ylogs privados.
Los dos probes conprogreso pararon porseguridad; no se elevaron umbrales.

El parche deAPI inicial se detuvo por assertions al comprobar diferencias de
esquema entre checkout yarchivo real deimagen; se validó contra elsnapshot real.
Una prueba aislada deestado de modelos detectó una clave ausente yse corrigió
antes de promoción. El fallo de sesiónBase descubierto en activación sí provocó
rollback real; r2 lo corrige yel guard específico quedó probado. No se ocultan
estos incidentes como si todos los intentos hubieran pasado.

La espera `networkidle` del primer navegador expiró porpeticiones persistentes;
una inspecciónDOM posterior obtuvoHTTP200, perfiles visibles ysin erroresJavaScript.
La comprobación visual final deGrafana/Voicebox pasó: páginaVoicebox renderizada,
Fleet/Details seleccionan627 ysin errores de consulta. No se atribuyó ese timeout
de prueba a un bloqueo delbackendTTS.

## Recomendación y siguiente paso

**Mantener7 GiB, Kokoro yPiper; no activar CustomVoice enproducción ni ampliar másRAM.**
Las muestras masculina y femenina quedan disponibles para revisión. La causa
completa del timeout sigue abierta: un nuevo diagnóstico debería aislar el codec
yla atribución de presión/swap con presupuesto explícito, no alargar laespera ni
forzar nuevas cargas. Esa recomendación es propuesta, no otro piloto ejecutado.

Siguiente paso deFase7.4: escucha/aceptación de las dos muestras y, cuando el
propietario quiera, incorporar sus grabaciones mediante elprocedimiento preparado.
La primera clonación real ysu aceptación siguen pendientes. Sin commit ni push.

## Evidencias

[Plan](evidence/2026-11-10-d068-plan-review.json),
[diagnósticoQwen](evidence/2026-11-10-d068-qwen-diagnosis.json),
[microbenchmark](evidence/2026-11-10-d068-cpu-benchmark.json),
[versiones](evidence/2026-11-10-d068-runtime-versions.json),
[política recuperación](evidence/2026-11-10-d068-rollback-policy.json),
[producciónfinal](evidence/2026-11-10-d068-production-final.json),
[concurrencia](evidence/2026-11-10-d068-concurrency.json),
[idempotenciaCompose](evidence/2026-11-10-d068-compose-idempotence.json),
[guardsowner](evidence/2026-11-10-d068-owner-no-data-guards.json),
[monitorowner](evidence/2026-11-10-d068-owner-monitor-preflight.json),
[auditoría](evidence/2026-11-10-d068-audit.json),
[observación](evidence/2026-11-10-d068-observation.json),
[restorefinal](evidence/2026-11-10-d068-restore-final.json),
[regresiónrestore](evidence/2026-11-10-d068-restore-old-regression.json),
[imagen](evidence/2026-11-10-d068-piper-r2-image-backup.json),
[identidades](evidence/2026-11-10-d068-identities-final.json).
Logs completos, muestras de diagnóstico, planes ybases de datos se conservan
privados; no se publican estadosTerraform ni secretos. Cambios ajenos previos intactos.


## Cierre técnico verificado

- TerraformNotes actualizó solo `description` de627; segunda aplicación **0 añadidos,
  0 cambios,0 destruidos**. Memoria7GiB,CPU3/swap512/disco50 efectivos.
- Dos despliegues Compose/IaC conservaron ID,StartedAt yRestartCount; auditoría
  posterior aNotes conserva el mismo contenedor yOOMKilled=false.
- Observación180,05s/7muestras PASS ysegunda ventana tras recuperación tambiénPASS:
  18Node/18cAdvisor/19Blackbox,18 fuentesCPU válidas, sinFIRING/PENDING.
- Otros17CT gestionados ylos26 archivosPVE ajenos conservan hashes. Los59targets
  conservan labels/URLs yUP. Grafana/Voicebox comprobados en navegador.
- 31 tests locales PASS; terraformfmt/validate,Python,shell,enlaces locales y
  gitdiff-check PASS. Las pruebas API, concurrencia, backups yrestauraciones reales
  tienen evidencia separada de las comprobaciones locales.

[IdempotenciaTerraform](evidence/2026-11-10-d068-terraform-final.json),
[observación trasrecuperación](evidence/2026-11-10-d068-after-recovery-observation.json),
[navegador](evidence/2026-11-10-d068-browser.json).
