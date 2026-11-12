# Fase 7.4 — D-069: Voicebox exclusivamente personal

Fecha: 10 de noviembre de 2026, Europe/Madrid. **DONE — Accepted:** perfil único y primera muestra
personal, con parecido, contenido y acento aceptados por el propietario.
El propietario sustituye el objetivo de voces adicionales por su propia voz.

## Resultado

CT627 conserva **3 vCPU, 7 GiB RAM, 512 MiB swap y 50 GiB de disco**. Solo queda
el perfil **Eduardo — Mi Voz**, con una referencia real y transcripción confirmada.
Qwen Base 0.6B generó el primer WAV. No se instalaron motores alternativos ni se
modificaron otros LXC, el pipeline o los recursos. Sin commit ni push.

[Escuchar muestra personal](http://192.168.1.127:17493/audio/925f8b71-6ad7-46f0-a48a-ffa3881004ef).
El propietario escuchó la muestra y confirmó «Sí, acepto la muestra» a la pregunta
sobre parecido, acento y lectura íntegra. Esta aceptación se limita a esta muestra.

## Grabación y almacenamiento

La ruta real de entrada fue
`docs/roadmap/mi_voz/11-10-2026-21-51-46-vertical.wav`, no la carpeta `mi voz`.
Original: WAV PCM16 estéreo, 48 kHz, 27,8613 segundos, RMS 0,0126 y sin clipping.
La referencia ya incorporada a Voicebox es mono, PCM16, 24 kHz y 24,8827 segundos.
Su ID es `8840f5e1-990b-463e-b94e-e72beef61917`; los 425 caracteres de su
transcripción fueron confirmados exactos por el propietario. No se atribuye la
diferencia de duración a un defecto sin comprobarlo.

Antes de retirar el archivo de documentación se verificaron copias exactas tanto
en almacenamiento privado local como en `/srv/voicebox/private-originals` del CT.
Directorios privados 0700 y archivos 0600. El original y su transcripción se
conservan separados de la referencia procesada, fuera del volumen servido por API.
Las dos grafías de la carpeta están excluidas por `.gitignore`; no estaban
versionadas. No se publican grabaciones, transcripciones, SQLite ni backups.

## Inventario y retirada

Los ocho nombres e IDs se presentaron antes de eliminarlos. No había perfiles
con nombres duplicados ni filas identificadas como perfiles integrados automáticos:
los presets integrados se ofrecen mediante catálogos de motores y se conservan.
El perfil clonado del propietario tiene referencia propia y no depende de presets;
no había enlaces de historias o canales que impidieran la retirada.

| Perfil | ID | Resultado |
|---|---|---|
| Eduardo — Mi Voz | `1fd00418-2a79-4178-883f-af6c3f5e07ee` | Conservado |
| ES Female — Narrator · Piper es_ES | `6ab4fe0a-5a4f-4dc0-9b84-71b5173edfeb` | Retirado con backup |
| ES Female — Narrator | `7e127dfb-8e46-42c4-8b26-c88d0c7c65ae` | Retirado con backup |
| ES Male — Narrator | `916ce396-1b15-4621-b63c-5eaf49f03b74` | Retirado con backup |
| ES experimental · Emma británica · candidata D064 | `5850a2d6-7349-4235-9e85-c3d92819281b` | Retirado con backup |
| ES · Santa · candidato D064 | `6be85095-8500-44cb-8f62-bab88f475d95` | Retirado con backup |
| ES · Alex · candidato D064 | `250f2938-c396-47e8-8b75-0bf9179d0252` | Retirado con backup |
| ES · Dora · candidata D064 | `7b6c34d0-861a-4001-ba37-aa6cb379b6e9` | Retirado con backup |
| Prueba IaC español D063 | `285b5291-74b8-406d-b7fe-56c31c4e21cd` | Retirado con backup |

La retirada se ejecutó por API únicamente sobre esos ocho UUID. El código real
elimina también su historial y audio: los **25 WAV anteriores siguen recuperables
en el backup**, aunque ya no aparecen en la aplicación. No se borraron los tres
intentos personales fallidos, la referencia ni el perfil del propietario. No se
desinstalaron motores ni se borraron pesos compartidos.

Backup previo: `/opt/voicebox/backups/d069-before.tar.gz`, SHA256
`416cab39066757005a69318d9bf5976a1c0b8b50b0d526b82c208895f00d2fc7`.
Copia fuera de PVE en `~/.local/share/mailerblend-recovery/voicebox-d069/`;
restauración aislada PASS: 127 archivos, 6 symlinks confinados, SQLite íntegra y
25 audios. Incluye referencia y original personal privados. Además se prepararon
ocho ZIP por perfil con registros, referencias y generaciones, verificando CRC.
El export API rechazó presets con HTTP400 antes de cualquier borrado, por lo que
esos ZIP se construyeron a partir del snapshot restaurado.

## Causa de las generaciones fallidas

- **0.6B**, intento `b792d27a-b89f-4e68-88cd-5d6eb44bb0d2`: el guard buscaba el
  nombre antiguo `Eduardo — Personal Voice`. No reconocía `Eduardo — Mi Voz`, aunque
  su referencia ya existía. Falló antes de inferencia.
- **1.7B**, intentos `8726a1bf-cbed-4a3c-b890-83f5c19ecd87` y
  `b1f70e0a-6657-4e21-960c-2ca207282c7e`: rechazo explícito del tamaño no preparado
  para CPU, antes de cargarlo. No demuestra un problema de la grabación.

Se corrigió el guard para comprobar el UUID real del propietario, tipo clonado,
referencias asociadas, archivos presentes y transcripción no vacía. Las validaciones
se conservan. Su engine por defecto pasa a `qwen`, idioma `es`; debe seleccionarse
**0.6B**, ya que 1.7B continúa rechazado. CustomVoice no sirve para esta clonación
personal y permanece bloqueado en CPU tras los pilotos anteriores.

## Motor, descarga e inferencia

Se utilizó **Qwen3-TTS-12Hz-0.6B-Base**, distinto de CustomVoice. El modelo oficial
admite clonación con audio y transcripción. Snapshot fijado a
`5d83992436eae1d760afd27aff78a71d676296fc`, 11 archivos, 2.516.100.892 bytes.
Descarga y hashes verificados en el volumen persistente: 233,41 segundos, RSS
máximo del helper 66.617.344 bytes, con límite de 512 MiB y sin instanciar TTS.
[Tarjeta oficial Base](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-0.6B-Base).

Candidata: generador BF16/SDPA, codec FP32, dos hilos, una operación TTS/modelo
residente, sin cambios de dependencias. Las etapas se instrumentaron sin registrar
texto o audio personal. El supervisor se ejecutó en PVE, fuera del cgroup del CT.
Límites: 180 segundos; 6,5 GiB de cgroup; swap adicional de 64 MiB; OOM;
host disponible menor de 1,5 GiB; PSI full avg10 del 2%; 45 segundos sin CPU.
Ninguno se activó. Se mantuvo rollback de imagen sin revertir la base de datos.

Texto exacto enviado:

> Ningún trader opera sin perder, ni siquiera los mejores. La diferencia no está en evitar las pérdidas, sino en cómo las gestionas.

| Medición | Resultado |
|---|---|
| Generación | `925f8b71-6ad7-46f0-a48a-ffa3881004ef` |
| WAV | 6,40 s, PCM16 mono, 24 kHz |
| Tiempo observado de generación | 106,86 s |
| Prompt de referencia | 23,852 s; incluye encode de 2,866 s |
| Generación de tokens | 41,268 s |
| Decodificación del codec | 33,369 s |
| Supervisor total | 126,54 s, incluye activación y readiness |
| Pico observado de cgroup | 5.561.266.176 bytes, 5,18 GiB |
| HWM de RSS | 5.026.299.904 bytes, 4,68 GiB |
| Crecimiento de swap observado | 5.574.656 bytes, 5,32 MiB; VmSwap del proceso 0 |
| CPU media del proceso en la ventana medida | 1,59 núcleos |
| PSI full avg10 máximo | 1,72% |
| OOM / OOM kill | 0 / 0 |

Muestreo cada aproximadamente 2 segundos: el pico de cgroup es el máximo observado,
no un máximo instantáneo exacto. Los eventos `memory.max` llegaron a 113728 por
límites/reclamación; no son OOM ni permiten afirmar que no hubo presión. El archivo
tiene señal válida, RMS 0,10 y clipping 0. No se comprobó su contenido mediante ASR
ni se acepta automáticamente la semejanza. RTF observado 16,70 para esta muestra;
**no se probó una narración de un minuto ni se extrapola su rendimiento**.

## IaC, imagen y persistencia

Imagen `local/voicebox:8af7efe62fab-personal-d069`, ID
`sha256:bcc5c14f88064ffa76f813d788d183918b208deba45075d8118a2b07c60c248b`.
Archivo de imagen fuera de PVE: 1.279.021.236 bytes, SHA256
`bfea29a8e30e006022575d27fdc4d19188ea0fde79295b72eb81caf6abbef628`;
29 blobs OCI verificados. Imagen R2 anterior y archivo conservados para rollback.
No se afirma una restauración Docker en otro CT ni un rollback automático ejecutado:
el piloto terminó con éxito y conservó preparado ese camino de recuperación.

Compose e image-lock fijan la candidata y habilitación Base tras la prueba técnica.
`personal-config.py` reconcilia el perfil existente, engine, idioma, fragmentos de
200 caracteres y catálogo persistente; no crea perfiles ni carga modelos.
`voice-identities.yml` solo contiene `personal`. El catálogo D064 queda archivado y
los flujos históricos de altas están bloqueados para evitar recrear perfiles.
Docker conserva CPU3, RAM6200 MiB y RAM+swap6600 MiB.

Reinicio real únicamente de Voicebox: mismo UUID, referencia idéntica por hash y
WAV generado idéntico por hash después. Ningún modelo quedó cargado tras reiniciar;
los pesos permanecen descargados. Dos deploy posteriores conservaron ID, StartedAt
y RestartCount. La UI muestra el perfil sin errores JavaScript; no se publican
capturas de referencias personales. El cliente API independiente solo admite la
identidad personal y no modifica el pipeline.

Notes se aplicó mediante Terraform: solo `description` de CT627; segunda aplicación
0 añadidos, 0 cambios y 0 destruidos. El primer plan falló por faltar el varfile
privado de bootstrap y no se aplicó. Se corrigió además el validador de Notes, que
aceptaba un plan fallido vacío: ahora rechaza `errored` y checks fallidos, con prueba
de regresión. Se reutilizó la configuración privada existente, sin eludir el guard
SSH ni modificar accesos. No se publican planes, estados ni logs sensibles.

## Infraestructura, recomendación y pendientes

Otros 17 CT gestionados y 26 configuraciones PVE ajenas mantienen hashes; los
59 targets conservan labels/URLs y están UP. Observación de 180,11 s, 7 muestras:
18 Node, 18 cAdvisor, 19 Blackbox, 18 fuentes CPU válidas y ninguna alerta
FIRING/PENDING. UI sin errores; recursos y acceso LAN conservados.
32 tests locales PASS: 16 de inventario y 16 de provisioning, incluida regresión
de planes fallidos. Terraform fmt/validate, Python y shell comprobados. Estas pruebas
locales se distinguen de generación, reinicio, backups y observación reales.

**Recomendación: mantener Base0.6B para la voz personal ya aceptada**, sin ampliar
RAM ni añadir motores. La narración larga requiere otra validación de estabilidad y
tiempo; fragmentar a 200 caracteres no la acredita. Si el parecido no es aceptable,
[Chatterbox Multilingual](https://github.com/resemble-ai/chatterbox/blob/master/src/chatterbox/mtl_tts.py)
soporta español y una ruta CPU, pero necesita T3 multilingüe, S3Gen, VoiceEncoder y
adaptación del backend; su memoria/velocidad en CT627 no están medidas.
[OpenVoice V2](https://github.com/myshell-ai/OpenVoice/blob/main/docs/USAGE.md)
requiere MeloTTS y conversión de timbre, checkpoints y dependencias adicionales;
tampoco está validado aquí. No se descargó ni instaló ninguna alternativa.

**Fase 7.4 / D069 DONE — Accepted** para el alcance solicitado: perfil personal
único y primera muestra. Siguiente: uso de la voz personal; una prueba de narración
larga queda separada y no se presenta como realizada. Las voces masculinas/femeninas adicionales quedan fuera del
objetivo actual y podrán incorporarse en otra intervención. No commit ni push.

## Evidencias

[Prueba Base](evidence/2026-11-10-d069-pilot-summary.json),
[retirada](evidence/2026-11-10-d069-retirement.json),
[restore previo](evidence/2026-11-10-d069-restore-before.json),
[imagen](evidence/2026-11-10-d069-image-check.json),
[Compose idempotente](evidence/2026-11-10-d069-compose-idempotence.json),
[persistencia y auditoría](evidence/2026-11-10-d069-audit.json),
[navegador](evidence/2026-11-10-d069-browser.json),
[observación](evidence/2026-11-10-d069-observation.json),
[Terraform](evidence/2026-11-10-d069-terraform.json).

[Aceptación auditiva del propietario](evidence/2026-11-10-d069-owner-acceptance.json).

## Backup final y cierre

`/opt/voicebox/backups/d069-final.tar.gz`, SHA256
`dc7dbe40be4d81ec09d511de42fde0c5349d8491e2814365c3043b7f5cf3de6a`,
copiado fuera de PVE y restaurado aisladamente: **134 archivos, 17 symlinks
confinados, SQLite íntegra, sin fallos de claves foráneas, un perfil, una referencia
y dos audios personales completados**. La muestra supervisada es925f8b71; el
snapshot contiene además otro audio del propietario, conservado sin atribuirle
las mediciones ni la aceptación de la prueba supervisada. Referencia y original
privado verificados idénticos por hash.

La aceptación humana llegó después de ese snapshot. Se conserva su suplemento
`/opt/voicebox/backups/d069-acceptance/` con catálogo aceptado, recibo y Notes:
tres archivos verificados mediante manifiesto y copia privada local. Para recuperar
el estado aceptado, restaurar datos del snapshot y reconciliar el catálogo desde
IaC/suplemento. No se presenta el estado pendiente del catálogo histórico como
aceptación perdida ni se fuerza otro backup completo de los mismos pesos.

Notes se actualizó después con la aceptación, de nuevo solo description627 y
segunda aplicación0/0/0. Auditoría final conserva recursos, imagen, perfil,
referencia, muestra, monitorización y configuraciones ajenas. Original y modelos
retenidos, sin datos personales en Git ni pipeline modificado.

[Backup final](evidence/2026-11-10-d069-backup-final.json) ·
[Restore final](evidence/2026-11-10-d069-restore-final.json) ·
[Suplemento de aceptación](evidence/2026-11-10-d069-acceptance-backup.json).
