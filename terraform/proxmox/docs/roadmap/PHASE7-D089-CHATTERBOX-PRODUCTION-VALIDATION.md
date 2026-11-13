# Fase 7.4 — D-089: validación aislada y despliegue condicional de Chatterbox

## Cierre aceptado y auditoría final de publicación

**D089 y alcance validado de Voicebox Fase7.4: DONE / ACCEPTED.**
13 de noviembre de 2026, Europe/Madrid. El propietario confirma haber escuchado y
aceptado Chatterbox español5,48s, Chatterbox inglés5,00s y su narración Qwen en inglés
45,04s. Es aceptación humana explícita, no dispensa ni inferencia por archivo válido.
Se conservan Qwen español D081 y todos los datos/configuración productivos.
La sección de reanudación inferior refleja el estado previo a esta aceptación.

### Límite efectivo de Chatterbox

**No se pueden enviar hoy1.200caracteres a Chatterbox en una sola solicitud.**
El límite es240; Qwen conserva1.200. Auditoría fechada:
[evidencia efectiva](evidence/2026-11-13-d089-acceptance-audit.json).

| Capa | Dónde se aplica |
|---|---|
| UI servida | `index-CzM_gv4b.js`, función compilada textLimit: chatterbox240/qwen1200; useGenerationForm rechaza exceso antes de envío |
| API | `/app/backend/routes/generations.py` llama admission; `/app/backend/backends/engine_policy.py` valida CB.max_chars240 antes de crear trabajo/cargar modelos |
| Controlador | `/opt/voicebox-qwen-627/engine_policy.py`: validate y capabilities max_chars240 |
| Worker | `/srv/voicebox/qwen-worker/src/chatterbox_worker.py` valida request con engine_policy antes de imports ML |
| Salida y presupuesto | max_new_tokens400 con EOS obligatorio, WAV≤20s, timeout300s, stop7/hard8/CT19GiB |

Se comprobó mediante validación pura que240pasa y241/1200se rechazan. No se envió
ninguna generación ni se procesó audio. JS descargado desde Voicebox coincide con
el hash del archivo de imagen inspeccionado; no se deduce del candidato local.

La versión fijada upstream `ab55923c27757c90cfcc407baa57dc25a7d25217` no documenta
un tope universal240caracteres. Su [README fijado](https://github.com/resemble-ai/chatterbox/blob/ab55923c27757c90cfcc407baa57dc25a7d25217/README.md)
no acredita una narración completa de1.200caracteres en este hardware.
El [T3Config fijado](https://github.com/resemble-ai/chatterbox/blob/ab55923c27757c90cfcc407baa57dc25a7d25217/src/chatterbox/models/t3/modules/t3_config.py)
define max_text_tokens2048 y max_speech_tokens4096. Son capacidades de tokens,
no equivalencias de caracteres ni prueba de generación larga.
El [generate nativo](https://github.com/resemble-ai/chatterbox/blob/ab55923c27757c90cfcc407baa57dc25a7d25217/src/chatterbox/mtl_tts.py)
fija1000tokens de salida internamente; no expone ese argumento en su firma pública.
Nuestra envoltura lo acota a400, y exige EOS antes del decoder. Con25tokens acústicos/s,
400tokens representan aproximadamente16s antes de EOS/recorte, no minutos.

La configuración local puede editarse y el código de inferencia admite ajustar
max_new_tokens, pero elevar solamente max_chars no demuestra que se complete el
texto ni resuelve presupuestos de salida, contexto, RAM y tiempo. No hay prueba
ni autorización para subir límites aquí. Chatterbox1200caracteres y narraciones
largas quedan fuera del cierre; el límite documentado no bloquea lo aceptado.

### Efectos disponibles y valor predeterminado

| Preset | UI | API | Qwen / Chatterbox |
|---|---|---|---|
| Robotic | Disponible | GET /effects/presets | Ambos |
| Radio | Disponible | GET /effects/presets | Ambos |
| Echo Chamber | Disponible | GET /effects/presets | Ambos |
| Deep Voice | Disponible | GET /effects/presets | Ambos |

Se inspeccionaron el selector compilado servido, los cuatro presets efectivos,
el encaminamiento effects_chain de la API y el postprocesamiento compartido en
`/app/backend/services/generation.py`. La selección no está restringida por motor:
se aplica a la salida generada y no a la referencia de voz. No se ejecutó DSP.

**Predeterminado para Eduardo: sin efectos / None.** El selector comienza en null
mostrado como none; la API usa effects_chain=None y puede heredar defaults del
perfil. Se verificó que Eduardo no tiene cadena de efectos configurada, por lo
que no hereda ningún preset. Este matiz impide extrapolar ese default a perfiles
futuros con efectos propios. La normalización de volumen es una opción distinta.
Los cuatro presets no han recibido aceptación acústica con voz real en este cierre;
se acredita disponibilidad/configuración, no una nueva prueba sonora.

### Publicación y límites del cierre

Se autoriza publicar los cambios pendientes Voicebox D083–D089, su infraestructura
CT627 y evidencias documentales filtradas en la rama main del repositorio IaC,
conforme al flujo D082. La aplicación se reproduce con fuentes/overlays y locks
de este repositorio; no se altera producción para publicar Git. Se excluyen los
cambios ajenos de monitorización/CRM/EVA, grabaciones, WAV, pesos, checkpoints,
SQLite, backups, credenciales y estados Terraform. Los documentos compartidos se
preparan por secciones, conservando el resto en el árbol de trabajo.

Cierre F7.4 limitado a Voicebox validado; F7 global,7.2/7.3 y otros servicios siguen
con sus estados previos. Siguiente: operación habitual y vigilancia; cualquier
ampliación de Chatterbox o nuevos ensayos requiere alcance propio. Sin inferencias,
procesado de audio, reinicios, despliegues ni cambio de configuración en esta revisión.

## Publicación verificada en GitHub

Commit funcional **`402501e0279389e607c44950be9b3423e4d5bb4c`**, rama **main**, remoto
`git@github.com:eduardo152030/mailerblend-platform-infra.git`. Push normal y consulta
independiente de refs/heads/main confirmaron ese SHA.197archivos de Voicebox/CT627,
sin datos privados ni cambios ajenos. Instantánea exacta del índice validada:
inventario fresco, Terraformvalidate,9testsUI, sintaxisPython/Bash y enlaces locales.
Suite77/77 previa D089 conservada; no se generó ni procesó audio en esta revisión.

Post-push: Voiceboxhealthy, Qwen/Chatterboxes/en ready; mismo ID/StartedAt/imagen,
configuraciones PVE y105archivos protegidos intactos, sin trabajos residuales.
[Recibo de publicación](evidence/2026-11-13-d089-publication.json).
El recibo y esta sección se publican en un commit documental posterior normal;
suSHA final se comprueba en el remoto y se comunica al propietario sin intentar
incluir autorreferencia circular. Otros cambios locales permanecen sin publicar.
No se aplicaron ProxmoxNotes/Terraform, reinicios o despliegues al publicar Git.

## Historial de reanudación previo a la aceptación

## Estado vigente — reanudación completada técnicamente

13 de noviembre de 2026, Europe/Madrid. **DONE técnico; aceptación acústica pendiente**.
Chatterbox queda disponible en español e inglés; Qwen es/en aceptado se conserva.
La autorización de reanudación sustituye la parada operativa inferior exclusivamente
en el alcance de verificar el español existente y ejecutar un único inglés.
[Evidencia de cierre](evidence/2026-11-13-d089-resume-validation.json).

### Generación Qwen del propietario

El trabajo `27af4ddc-c17a-4e10-9dc2-b3fe2d569329`, inglés/728caracteres, se comprobó
**completed antes de cambiar el receipt**. Talker415,96s, EOS y checkpoint íntegro;
Decoder69,13s, WAV45,04s,1.080.960frames/24kHz. Su estado y artefactos permanecen
conservados. No se canceló, no se reinició app/agente/CT y no se volvió a generar.
[WAV del propietario](http://192.168.1.127:17493/audio/27af4ddc-c17a-4e10-9dc2-b3fe2d569329)
verificado por API desde PVE y descargado privadamente.

El checksum de descarga `71f8587b…d7118f` difiere del WAV crudo del decoder
`7e3879d3…a2ca3`: Voicebox aplica su normalización nativa por defecto. Se contrastaron
los1.080.960samples: ganancia7,92109 hacia RMS−20dB, residuo máximo0,99985LSB,
sin cambio de duración. Esto explica la diferencia sin modificar ningún audio ni
ajuste del propietario. La primera comprobación auxiliar que exigía SHA idéntico
entre ambos archivos era demasiado estricta para esa salida normalizada; no fue
un fallo del worker ni de la descarga. No se afirma aceptación acústica de esa voz.

### Diagnóstico y corrección del observador

El error anterior se produjo durante `connect()` con EHOSTUNREACH/Errno113 sobre
una IP literal, antes de obtener respuesta HTTP. Por tanto no fue resolución DNS,
respuesta de error del modelo ni prueba de que el trabajo hubiera fallado. El
observador antiguo dejaba escapar URLError y no tenía transporte alternativo;
se interrumpía su comprobación local aunque el worker terminase. Ya era de solo
lectura: su excepción tampoco cambió el estado API ni disparó otra inferencia.

Ruta actual desde el puesto: eth0, origen172.17.21.167, gateway172.17.16.1 hacia
192.168.1.127. Desde PVE: vmbr0, origen192.168.1.100, acceso directo a esa IP.
En esta reanudación ambas rutas devolvieron HTTP200 y el mismo WAV español.
**No se ha demostrado qué provocó exactamente la pérdida histórica de ruta**:
no se guardó captura de rutas/ICMP del instante. No se atribuye a VPN, firewall,
ARP ni reinicio de red sin evidencia. No se cambiaron rutas, firewall, DNS o SSH.

La corrección es un observador GET-only en
[resume/observer.py](../../services/infra-voicebox/validation-d089/resume/observer.py):
allowlist health/capabilities/history/audio con UUID; SSH estricto existente para
el transporte PVE, y fallback directo→PVE exclusivamente para lecturas. Distingue
`observer-error.json` de estado del worker, conserva completed leído, valida bytes
reales WAV y SHA, y no escribe en cola ni API. No tiene capacidad de POST/generar,
cancelar o marcar un trabajo failed. Solo el submitter separado, con marcador
exclusivo, envía la única inferencia autorizada.

Cuatro regresiones nuevas PASS: fallback lee el mismo ID, rechaza endpoints
mutantes, pérdida de conexión tras completed conserva el estado y no genera,
y WAV truncado se rechaza. Suite completa reproducible **77/77 PASS** en el mismo
venv/imagen sin modelos ni grabación montados. Suite UI9/9 previa conservada,
sin cambios UI. La prueba sintética de fallback no se presenta como un nuevo corte
real de red. En el ensayo inglés se usó directamente PVE y no hizo falta fallback.

### Español reutilizado y activación

Se consultó el trabajo español existente por API directa y por PVE, se descargó
su WAV por ambas rutas y se contrastó SHA256:
`358aacba678d13acd3e203e517cbb53f54f5ea62fd261869b9c5a12ac6b4cd45`.
Sigue completed/5,48s. **Cero nuevas inferencias españolas**; ningún perfil,
referencia, checkpoint o resultado previo se modificó.

Con Qwen propietario terminal, cola vacía y host/CT saludables, se verificaron de
nuevo hashes de controlador, worker, dependencias, manifiesto y todos los pesos.
Se conservan modelo/FP32/semilla42, stop7/hard8/CT19GiB,300s,240caracteres y
sharedlock. Los archivos ML coinciden con el candidato probado D088/D089.
Backup/rollback D089 siguen disponibles. Se guardó receipt previo en HDD y se
cambió **solo enabled/reason** mediante toggle.py. Cero reinicios, despliegues de
imagen o modificaciones de código productivo en esta reanudación.

### Único ensayo inglés

Solicitud exacta por API desde PVE:

> Hello, my name is Eduardo. This is a test of my cloned voice using Chatterbox in English.

Job `bde1cb38-1cc7-4d37-a77e-6226bd0762b3`, una ejecución, sin efectos, normalize=false,
sin reintentos. Referencia personal original RO y cola exclusiva con Qwen.

| Medida | Resultado |
|---|---:|
| Estado worker / API / descarga | completed / completed / WAV íntegro HTTP200 |
| Tokens / EOS | 127 / sí |
| Duración WAV | 5,00s mono PCM16,24kHz |
| Carga | 22,99s |
| Preparación referencia, eventos | 15,85s |
| Generación T3 | 33,70s |
| Decoder, eventos | 33,12s |
| Tiempo interno ML / hasta evento final incluyendo imports y hashes | 106,27s /128,23s |
| Pico kernel cgroup | 2,518GiB |
| Margen real respecto a7GiB | 4,482GiB |
| RSS VmHWM | 4,583GiB |
| Swap worker / crecimiento swap CT | 0 /0 |
| OOM nuevos / guardas alcanzadas | 0 /ninguna |
| Procesos residuales | Ninguno |

API y worker comparten SHA256
`6f388a3ac00fa69e48d1e3d49e463ea878b6aa3b9469f7f666f6456abd2fb677`.
El kernel peak se usa para el margen; no se suman RSS y cgroup, ni file_mapped a
file. La caché compartida explica parte de la diferencia de contabilidad; no se
alteró ni se promete igual pico para cualquier longitud o condición de caché.
Snapshots y muestras anon/file/kernel/PSI/CPU en la evidencia enlazada.

- [Chatterbox español, WAV existente](http://192.168.1.127:17493/audio/9a8ba53a-6032-4ab0-bfa6-8521e4d1de77).
- [Chatterbox inglés, WAV nuevo](http://192.168.1.127:17493/audio/bde1cb38-1cc7-4d37-a77e-6226bd0762b3).

### Cierre

Lectura final2026-11-13 07:50:09 UTC (08:50:09 Europe/Madrid): Voicebox healthy,
Qwen es/en ready y Chatterbox es/en ready. UID/GID999, capacidades0, misma imagen,
ID y StartedAt que al inicio. No trabajos activos ni workers residuales. Configs
PVE comparadas sin cambios;20GiB/3CPU/2GiBswap/100GiB y todas las guardas intactas.
Perfil/referencia con los mismos fingerprints;105archivos protegidos, checkpoints
anteriores y datos del propietario conservados. SQLite íntegra, historial12filas,
una más por inglés;8audios originales del backup D089 verificados. WAV D081 HTTP200.

**No se declara aceptación acústica**: parecido, acento, naturalidad y pronunciación
quedan pendientes de escucha del propietario. Backend disponible conforme a su
instrucción, sin sustituir Qwen. Fase7.4 sigue IN PROGRESS; D089 DONE técnico con
UAT acústica pendiente. Siguiente: revisar ambos WAV y mantener vigilancia existente;
no se autorizan ni ejecutan otros ensayos automáticamente.

Evidencias privadas en `~/.local/share/mailerblend-recovery/voicebox-d089-resume`
y `/mnt/storage/d089-resume` (HDD); resultados originales intactos. Sin recursos,
otros LXC, pipeline, commit ni push.

## Historial — primera intervención y parada conservada

13 de noviembre de 2026, Europe/Madrid. Marcas de evidencia en UTC.
Estado histórico de la primera intervención: **BLOCKED**. Sustituido por la reanudación documentada arriba.
La última instrucción D-089 sustituye íntegramente la autorización anterior.

## Resultado

La optimización FP32 supera la carga y una inferencia española completa aislada.
Después de verificar backups, se desplegó el componente mínimo y se realizó una
única generación española desde la API utilizada por Voicebox. También terminó
con EOS y WAV íntegro, idéntico por checksum al aislado.

Durante la observación desde el puesto local ocurrió `URLError: [Errno 113]
No route to host`. El observador no llegó a guardar su validación final. Conforme
a la condición de parada, **no se ejecutó inglés ni se repitió ninguna inferencia**.
Se deshabilitó Chatterbox mediante su receipt, sin reiniciar app, CT ni agente.
Después se recuperó la observación del trabajo ya completado mediante lecturas
desde PVE: historial y descarga HTTP200. Esto no es otra generación ni borra el fallo
del observador. No se atribuye ese error a OOM, al decoder ni a un fallo de Qwen.

Qwen es/en permanece operativo y aceptado. El overlay optimizado queda instalado,
pero Chatterbox **no está disponible para nuevas generaciones**. No se restauró
código anterior porque app y Qwen no se vieron afectados; el rollback coordinado
sigue preparado. Nunca se restauró SQLite antiguo sobre datos nuevos.

[Evidencia filtrada](evidence/2026-11-13-d089-chatterbox-validation.json) ·
[Diagnóstico D-088](PHASE7-D088-CHATTERBOX-MEMORY-OPTIMIZATION.md).

## Suite y causa de readiness

La ejecución original conjunta en el entorno reproducible, ya con soundfile,
reprodujo 69 tests con un único fallo readiness y cero errores de dependencias.
El mismo test estable por separado pasó 2/2. La causa es `sys.modules`:
`test_d085` importa `readiness` de candidate-d085; el test D087 hacía después
`from readiness import chatterbox_ready`, reutilizando la función antigua.
D085 acepta una lista de archivos más corta y rechaza el manifiesto D087 que
incluye también `guards.py` y `supervise.py`. El código real desplegado coincide
con maintenance-d087, SHA `7cbac2aa…6024fd`, y no tenía esa regresión.

Se corrigió exclusivamente el fixture para importar por identidad de archivo y
para inyectar ese mismo módulo al cargar el agente sintético. Se conservaron las
pruebas de heartbeat, hashes, fuentes requeridas, guardas y rechazo de archivos
alterados. Se añadió una regresión que introduce deliberadamente el módulo D085
en la caché y verifica que el fixture sigue validando D087. Otro contrato comprueba
estable y candidato bajo igual configuración: el nuevo receipt exige los helpers
exactos y falla si falta o se altera telemetry. No se relajó readiness productivo.

Resultado final previo al despliegue: **73/73 tests Python y 9/9 tests UI PASS**.
Los doce contratos de carga de D088 se conservan; la inferencia verifica de nuevo
pesos completos y módulos CPU FP32. Los siete errores locales por soundfile no
se ocultaron con mocks: la suite se ejecutó con soundfile real en el venv fijado.

Entorno: Python3.12.16, PyTorch2.6.0+cpu; imagen inmutable
`sha256:bcc5c14f88064ffa76f813d788d183918b208deba45075d8118a2b07c60c248b`,
venv D085 RO y receipt SHA `2228e956…1b8dce`. Red ninguna, UID/GID999,
suite RO y sin montar modelos ni referencia durante los tests. Snapshots de suite
antes, corregida e integración conservados privadamente para reproducir el orden.
No hubo instalación ni actualización de dependencias.

## Ensayo aislado autorizado

Una sola ejecución, texto exacto:

> Hola, soy Eduardo. Esta es una prueba de mi voz utilizando Chatterbox en español.

Modelo Multilingual V3, FP32 CPU, seed42, referencia original montada RO y verificada
por SHA, sin transcripción nueva, efectos ni normalización adicional. El tokenizer
español se comprobó antes de cargar pesos. Se mantuvo el auxiliar chino diferido
validado en D088; no se descargó ningún recurso. Pesos y paquetes permanecieron
sin modificar. Contratos y hashes en source-lock; ninguna referencia flotante.

Mismo Docker/cgroup v2 que el worker productivo: `memory.max=8589934592`,
`memory.swap.max=0`, `cpu.max=300000 100000`. Exclusión mediante el lock compartido
con Qwen; funciones productivas de preflight y parada sin cambios. Parada7GiB,
hard8GiB, CT19GiB y timeout300s. Supervisor cancelable, hijo completamente terminado,
contenedor retenido parado; checkpoint Qwen nunca usado como entrada Chatterbox.

| Medida | Aislado es | Voicebox es |
|---|---:|---:|
| Intentos | 1 | 1 |
| Carga instrumentada | 22,71 s | 23,50 s |
| Generación T3 | 37,79 s | 32,31 s |
| Referencia, eventos antes/después | 17,32 s | 15,48 s |
| Decoder, eventos antes/después | 40,32 s | 39,06 s |
| Worker hasta evento final, incluye imports/verificación | 139,11 s | 137,30 s |
| Tiempo interno desde inicio de preparación ML | 118,71 s | 110,92 s |
| Tokens / EOS | 139 / sí | 139 / sí |
| WAV mono PCM16, 24 kHz | 5,48 s | 5,48 s |
| Pico cgroup kernel | 2,400 GiB | 3,187 GiB |
| Margen hasta guarda7GiB | 4,600 GiB | 3,813 GiB |
| RSS máximo VmHWM | 4,583 GiB | 4,583 GiB |
| Swap worker / crecimiento swap CT | 0 / 0 | 0 / 0 |
| OOM worker/CT/host nuevos | 0 | 0 |
| PSI CT full avg10 máximo | 0 % | 0 % |
| CPU worker | 250,94 CPU-s | aproximadamente243,29 CPU-s |

El pico kernel es superior al máximo de las muestras discretas, especialmente en
producción (3,042GiB muestreado frente a3,187GiB kernel); se usa el mayor para el
margen. RSS y cgroup no se suman. La observación aislada completa duró141,19s.
Tiempo por segundo de audio, incluyendo imports: aproximadamente25 veces tiempo
real; no acredita narraciones largas bajo el presupuesto300s.

Ambas salidas comparten SHA256:
`358aacba678d13acd3e203e517cbb53f54f5ea62fd261869b9c5a12ac6b4cd45`.
Esto confirma reproducibilidad de esos dos ensayos, no aceptación acústica.

### Memoria por fase en Voicebox

Snapshots posteriores a cada fase, GiB. Los picos transitorios globales están en
la tabla anterior; estos puntos no se presentan como máximos por fase.

| Fase | memory.current | RSS | anon | file |
|---|---:|---:|---:|---:|
| Carga | 2,910 | 4,272 | 2,077 | 0,822 |
| Referencia | 2,941 | 4,313 | 2,098 | 0,832 |
| Generación | 2,941 | 4,316 | 2,098 | 0,832 |
| Decoder | 2,948 | 4,327 | 2,105 | 0,832 |

La evidencia incluye los valores antes/después de cada fase y los samples aislados.
`file_mapped` sigue siendo parte de `file`. Hay páginas compartidas cuyo cargo no
coincide con RSS; no se forzó limpieza ni se movieron cargos. El cambio de caché
entre sesiones explica parte de las diferencias cgroup. El margen observado cubre
estos ensayos y su decoder, no garantiza cualquier longitud ni caché fría.

## Backup, despliegue y rollback

Antes de aplicar se verificaron salud, ausencia de inferencias, host y thin pool
con más del20% libre. Backup completo D084: lectura SHA de18.952.506.863bytes,
idéntica al archivo previamente descomprimido y restaurado fuera de producción;
SQLite de esa restauración sigue íntegra. No se declara un nuevo ensayo de arranque
DR. Backups D085 y D087b íntegros por SHA respecto a sus restauraciones verificadas.

Nuevo backup D089 de configuración, perfiles, referencias, SQLite e historial,
WAV, checkpoints y fuentes:141archivos verificados tras extracción aislada en HDD,
SQLite íntegra. SHA archivo `32006c99…72b4f0`. No se duplicaron modelos RO.
Ubicación HDD `/mnt/storage/d089`, copia actual y rollback de controlador/source link.
Los backups anteriores y datos nuevos permanecen intactos.

Despliegue mediante [deploy.py](../../services/infra-voicebox/validation-d089/deploy.py)
y deployment-lock: solo `chatterbox_worker.py`, `load_probe.py`, `telemetry.py`,
readiness y receipt con hashes ampliados. Los tres archivos ML son idénticos a los
del ensayo aislado. Nuevo árbol de fuentes privado y cambio atómico del enlace;
reinicio exclusivamente del agente para cargar readiness actualizado. No se recreó
ni reinició la app y no se cambió Compose, imagen ni código Qwen. Verificación
idempotente posterior PASS, sin escrituras ni recargas adicionales.

Shared lock y cancelación sintética PASS, sin modelos ni audio; cancelación API
sobre ID inexistente responde404. Health, historial, descargas antiguas y efectos
existentes verificados antes del ensayo. No se aplicaron efectos a voz real.

Ante el fallo del observador se aplicó [disable.py](../../services/infra-voicebox/validation-d089/disable.py):
receipt enabled=false, comprobación de capabilities, sin reinicio. Si app/Qwen
hubieran resultado afectados, el rollback preparado restaura readiness/receipt y
source link guardados, reiniciando solo el agente después de confirmar ausencia
de trabajo activo. **No restaura SQLite ni audios antiguos sobre producción.**
No ejecutar rollback mientras existe una generación Qwen ajena activa.

## Audio para revisión privada

[Chatterbox español desde Voicebox](http://192.168.1.127:17493/audio/9a8ba53a-6032-4ab0-bfa6-8521e4d1de77).
La descarga se comprobó desde PVE tras el fallo de ruta del observador local.
Copia privada fuera de Git: `~/.local/share/mailerblend-recovery/voicebox-d089/Eduardo-D089-Chatterbox-es.wav`.
El aislado tiene el mismo contenido binario. No hay WAV inglés de D089.
La fidelidad, naturalidad, acento, pronunciación y texto completo quedan pendientes
de escucha del propietario; EOS y WAV válido no los certifican.

## Estado final y siguiente paso

Lectura final 07:35:06 UTC, 08:35:06 Europe/Madrid: Voicebox healthy,
misma imagen21270364…, ID y StartedAt; UID/GID999 y capacidades0. Qwen es/en ready,
Kokoro/Piper disponibles. Chatterbox deshabilitado. Guarda19GiB, workers9/8GiB y
recursos20GiB/3CPU/2GiBswap/100GiB intactos. Configuraciones PVE comparadas sin cambios;
thin pool libre30,94%. 105archivos protegidos y tres checkpoints con EOS intactos.

SQLite íntegra, mismo perfil y referencia por fingerprint; ocho generaciones
preexistentes preservadas exactamente, ocho archivos de audio originales verificados,
WAV D081 HTTP200/hash intacto. Historial tiene11filas en esa lectura: el ensayo español
y otras solicitudes que no fueron iniciadas por esta intervención. Una generación
Qwen de728caracteres estaba activa en Talker; se dejó intacta. Por ello no se declara
el CT globalmente sin inferencias: **no quedan workers Chatterbox de estos ensayos**.

La validación final detectó además un defecto del helper heredado para verificar
backups: trataba audio_path vacío de una generación fallida como ruta con primer
componente. Se corrigió el helper local para distinguir ausencia de audio en fallidas
y exigir ruta en completadas, manteniendo la comparación de filas y checksums.
La comprobación se completó sin modificar SQLite ni datos productivos.

Fase7.4 sigue IN PROGRESS; D089 queda BLOCKED tras parada y deshabilitación preventiva.
Siguiente: revisar la muestra española y el fallo de conectividad del observador;
una reanudación para activar Chatterbox y ensayar inglés requiere nuevo alcance
tras esta parada. No se consume automáticamente el ensayo inglés pendiente.
No se aumentaron recursos, relajaron guardas, modificaron otrosLXC/pipeline ni se
hizo commit/push. Evidencias privadas en HDD y directorio local mencionado.
