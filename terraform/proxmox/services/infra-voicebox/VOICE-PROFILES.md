# Voz personal de Eduardo — Fase 7.4, D069

## D081 — ACCEPTED / PRODUCTION (cierre D082)

El propietario aceptó voz y contenido el **12 de noviembre de 2026**: narración
continua de 1.059 caracteres, WAV de 57,36s generado en676,18s, EOS ycheckpoint
íntegros, picoCT9,625GiB, sin nuevosOOM. Alcance: aproximadamente unminuto;
no acredita narraciones de5–10min. ElWAV es privado yno se publica enGitHub.

CT627:15GiB RAM,3vCPU,2GiBswap,50GiB. Qwen Base0.6B FP32/SDPA,3hilos,
semilla42, español, Eduardo — Mi Voz, A→checkpoint→B300/context25. GuardaCT14GiB,
workerhard9GiB/stop8,2GiB,1200caracteres y900s. No nuevas optimizaciones niR/A/B.

[Operación, recuperación yrollback](consolidation-d081/RUNBOOK.md) ·
[Cierre y reconstrucción IaC](release-d082/README.md) ·
[Informe final](../../docs/roadmap/PHASE7-D082-VOICEBOX-FINAL-ACCEPTANCE.md).
Elegir **Qwen3-TTS0.6B** expresamente enUI; el selector puede iniciar en1.7B.
Los apartados siguientes son históricos; no ejecutar recetas antiguas para reconciliar
la producción aceptada.


El único perfil de usuario vigente es **Eduardo — Mi Voz**,
`1fd00418-2a79-4178-883f-af6c3f5e07ee`, tipo `cloned`. Las voces adicionales quedan
fuera del alcance actual; podrán incorporarse en una intervención futura.
[Estado y mediciones](../../docs/roadmap/PHASE7-D069-PERSONAL.md).

## D070 — límite vigente de narraciones largas

La muestra corta D069 sigue aceptada. El intento largo de~55s no terminó yse canceló;
no repetir Qwen largo por ahora. La APIcancel puede marcar fallido sin parar elhilo
nativo de inferencia: verificar CPU yactividad real. No reiterar `POST/generate` ni
cargar otro modelo sobre el hilo activo. D070 requirió permiso expreso para reiniciar
soloVoicebox, conservando el CT ylosdatos; ese permiso no autoriza nuevos motores.
[Diagnóstico y comparaciónCPU](../../docs/roadmap/PHASE7-D070-CPU-ALTERNATIVES.md).
Kokoro/Piper conservados, sin convertirlos en sustitutos de la voz personal.

## Grabación real y privacidad

La grabación aportada es WAV PCM16,48kHz,estéreo,27,86s. Se conservaron sus bytes
originales en almacenamiento privado local fuera del repositorio y en
`/srv/voicebox/private-originals` del CT, directorio0700/archivos0600, verificando
la copia antes de retirarla de documentación. `.gitignore` protege ambas grafías
de la antigua carpeta; ni audio, transcripción, SQLite ni ZIP deben ir a Git.

La referencia ya asociada tiene ID `8840f5e1-990b-463e-b94e-e72beef61917`,
PCM16 mono24kHz,24,88s. La transcripción de425caracteres fue confirmada exacta por
el propietario. El original se conserva separado de la referencia preprocesada.
El propietario aceptó expresamente el parecido, acento y lectura de la primera
muestra generada (925f8b71-6ad7-46f0-a48a-ffa3881004ef). Esta aceptación no valida
narraciones largas ni voces adicionales.

Para futuras tomas:2–3grabaciones de10–20s, voz habitual, habitación silenciosa,
sin música ni saturación y distancia constante al micrófono. Preferir WAV PCM16
mono24/44,1/48kHz con transcripción literal. No es necesario volver a crear el perfil
existente. Incorporar por API `POST /profiles/{id}/samples` multipart `file` y
`reference_text`, después de preservar el original privado y validar la copia.
El script `prepare-voicebox-personal.py` exige3–25s, RMS suficiente y poco clipping;
no se aplica retroactivamente para rechazar el original estéreo ya procesado.

## Motor y prueba controlada

[Qwen Base0.6B](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-0.6B-Base) admite clonación
con audio y texto. EngineAPI `qwen`; CustomVoice usa presets y no es el motor para
esta identidad. BaseCPU preparado con BF16/SDPA, codecFP32 y dos hilos; snapshot
fijado a `5d83992436eae1d760afd27aff78a71d676296fc`. No usar1.7B en este CT.
La descarga persistente es independiente de carga e inferencia y se verifica por
hash antes de generar. Solo un modeloTTS enRAM. El guard exige el UUID real,
perfil clonado, referencias, archivos presentes y transcripción, sin sustituir voz.
La candidata añade una habilitación explícita `VOICEBOX_BASE_CPU_ENABLED=1` para
el piloto; deshabilitarla tras una parada de seguridad, sin borrar las referencias.

La prueba autorizada usa exactamente:

> Ningún trader opera sin perder, ni siquiera los mejores. La diferencia no está en evitar las pérdidas, sino en cómo las gestionas.

`scripts/validate-voicebox-personal.py --owner-reference-confirmed --output
/ruta/privada/prueba.wav` registra el ID una sola vez y vigila180s máximo, cgroup
6,5GiB, swap+64MiB,OOM,hostdisponible1,5GiB,PSIfull2% y45s sinCPU. Un fallo detiene
la inferencia mediante reinicio soloVoicebox y recupera un motor estable, sin borrar
datos. No repetir cargas después de un veto bajo el mismo ensayo. Consultar el
informe para resultado real; no inferir viabilidad por esta receta preparada.

## Contrato API, sin modificar el pipeline

La única identidad del catálogo `voice-identities.yml` es `personal`. El cliente
`scripts/voicebox-narrate.py personal --text-file /privado/texto.txt --output
/privado/audio.wav` exige muestra técnica completa; `personal` ya cumple esta condición. Nunca
sustituye la voz personal por Kokoro/Piper. No se ha integrado el pipeline.

- `GET /profiles/{id}/samples`: referencias asociadas.
- `GET /models/status`: estado de modelos; `POST /models/{name}/unload` liberaRAM,
  conservando pesos. `POST /models/load` selecciona modelo; no hacerlo fuera de
  una prueba controlada si Base no está validado.
- `POST /generate`: JSON `profile_id`, `engine:qwen`, `model_size:0.6B`,
  `language:es`, `text`, `personality:false`; devuelve ID asíncrono.
- `GET /history/{id}` hasta `completed` o `failed`. Ante error/timeout conservarID,
  reconciliar y devolver causa; nunca repetir automáticamente POST/generate.
- `GET /audio/{id}` recuperaWAV solo si terminó. Datos y UUID persisten enbind.

El servidor serializa TTS y devuelve409 para mutaciones de modelos mientras está
ocupado. La API no tiene autenticación porusuario: ACLLAN192.168.1.0/24 restringe
red, no distingue usuarios LAN. Los originales privados están fuera del volumen
servido por API. No exponer WAN ni publicar referencias o backups.

## Backup, retirada y recuperación

D069 retiró ocho perfiles de usuario, sin desinstalar motores ni alterar catálogos
integrados. Sus25audios y registros están en el backup privado `d069-before.tar.gz`
con restauración aislada verificada. Existen además ochoZIP porperfil con registros,
referencias y generaciones; el exportAPI de presets no se admite en este fork.
El propietario no depende de esos presets ni tiene enlaces de historias/canales.

El [runbook](README.md) describe snapshot coherenteSQLite/archivos y copia fueraPVE.
`backup.py` incluye originales privados y configuración; comprobar manifiesto,
SQLite y referencias en restauración aislada. El verificador no exige generaciones
completadas si el servicio solo tiene intentos personales fallidos, pero valida
todos los WAV completados que existan y todas las referencias reales.

Recrear soloVoicebox con los mismosbinds conserva perfil y referencia. Rollback
solo de código restauraCompose+lock+imagen, sin revertirSQLite. Restaurar datos exige
coordinación de snapshotSQLite y archivos correspondientes; nunca `down -v` ni
`prune`. Los backups e imágenes anteriores permanecen privados y conservados.

## Diccionario de pronunciación — alcance aceptado

- `trader → tréider`: corrección comprobada.
- `hola`: incidencia de pronunciación registrada, corrección pendiente. No aplicar
  sustituciones automáticas ni afirmar que se ha corregido.

Una futura transformación fonética pertenece exclusivamente a la entrada TTS.
Conservar el texto original destinado a subtítulos sin sustituciones fonéticas.
D082 documenta esta separación; no modifica código, texto ni pipeline de vídeos.
