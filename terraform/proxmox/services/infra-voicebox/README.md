# Voicebox — CT627

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


Servicio permanente de generación de voz, Fase 7.4 D063.
Web/API: http://192.168.1.127:17493, solo LAN 192.168.1.0/24.
Recursos históricos D069: 3 vCPU, 7168 MiB RAM, 512 MiB swap y 50 GiB local-lvm.
Se comenzó con los 1080 MiB de la plantilla y se amplió según mediciones.

## Histórico D070 — Qwen largo bloqueado

Cancelación API no detenía el hilo de inferencia. Reinicio exclusivo de DockerVoicebox
autorizado, CT627 sin reinicio ydatos intactos. API recuperada; Kokoro/Piper comprobados
con audios breves, sin nuevos perfiles. No repetir largosQwen ni desplegar otro motor
antes de revisar [la comparaciónD070](../../docs/roadmap/PHASE7-D070-CPU-ALTERNATIVES.md).
D069 conserva aceptación de su muestra corta; no supone narración de1min operativa.

## Histórico D069 — exclusivamente voz personal

Perfil único `Eduardo — Mi Voz`, UUID `1fd00418-2a79-4178-883f-af6c3f5e07ee`.
Referencia real persistente y transcripción confirmada. Ocho perfiles anteriores
retirados tras inventario y backup restaurado; motores y catálogos conservados.
Voces adicionales no son requisito vigente y podrán incorporarse en otro alcance.
[Informe D069](../../docs/roadmap/PHASE7-D069-PERSONAL.md) y
[guía personal y contrato API](VOICE-PROFILES.md) prevalecen sobre los antecedentes
D063–D068 inferiores. La primera muestra personal está aceptada expresamente por el propietario;
narración larga sin validar.

## Fuente e imagen base controladas — histórico D063

Fork eduardo152030/voicebox, revisión
8af7efe62fab8d33e2a5dfbedabaa45f68a5184f. No se modifica backend/frontend.
Dockerfile.cpu deriva del upstream con bases por digest, PyTorch/torchaudio CPU
2.8.0 y espeak-ng para Kokoro español. Estas diferencias evitan dependencias CUDA
y añaden el fonemizador requerido por la instalación oficial de Kokoro.

image-lock.json fija el ID exacto de la imagen aceptada y el hash del archivo de
imagen exportado fuera de PVE. deploy.sh rechaza una imagen o Dockerfile distintos.
Los rangos pip del upstream no garantizan un build nuevo idéntico: para reproducir
este runtime se restaura la imagen aprobada. requirements-observed.txt registra las
versiones instaladas, sin presentarlo como un lock de construcción validado.
Un build futuro se prepara como candidato y requiere revisar un nuevo tag/lock;
no se actualiza silenciosamente la imagen desplegada.

## Despliegue y reconciliación

Tras Terraform y bootstrap SSH D062, copiar los archivos de este directorio a
/opt/voicebox dentro de CT627 mediante SSH estricto con el known_hosts del bundle.
No ejecutar deploy.sh en PVE ni en otro LXC. El script comprueba el hostname,
checkout limpio y revisión, imagen, reglas LAN y modelos antes de reconciliar
únicamente el servicio voicebox. Conserva datos y no usa force-recreate.

Si la imagen no existe, transferir el archivo aprobado y ejecutar:

```sh
VOICEBOX_IMAGE_ARCHIVE=/ruta/privada/voicebox-image.tar.gz /opt/voicebox/deploy.sh
```

El hash se comprueba antes de docker load. En una instalación existente basta
/opt/voicebox/deploy.sh. La segunda ejecución real conserva ID, StartedAt y
RestartCount de Voicebox y cAdvisor. El verificador de modelos es un contenedor
efímero sin healthcheck HTTP; no es un servicio de aplicación nuevo.

## Datos, modelos y seguridad

/srv/voicebox/data conserva SQLite, perfiles, referencias, configuración y audios.
/srv/voicebox/huggingface conserva el modelo y las voces; model-lock.json fija
hexgrad/Kokoro-82M y sus tres voces españolas por revisión/tamaño/hash.
prepare-models.py verifica los archivos; el servidor funciona con HF_HUB_OFFLINE=1.
Otros motores, idiomas y concurrencia requieren evaluación y modelos adicionales.

Compose centraliza variables y límites: 3 CPU, 1600 MiB de RAM y 2000 MiB de RAM+swap
para la aplicación. El CT dispone además del presupuesto para Docker/exporters/SO.
No necesita secretos nuevos ni API comercial. La API no tiene autenticación
entrante acreditada: lan-only.sh y su unidad systemd restringen solo las peticiones
ORIGINAL de 17493 a la LAN, sin bloquear respuestas ni cambiar otras políticas.
No hay proxy ni publicación WAN. Para ampliar acceso hacen falta autenticación,
TLS, autorización y límites de peticiones.

## Operación y recuperación

```sh
docker compose -f /opt/voicebox/compose.yml ps
docker compose -f /opt/voicebox/compose.yml logs --tail 50 voicebox
python3 /opt/voicebox/backup.py --output /opt/voicebox/backups/NUEVA-CAPTURA
```

El backup exige no tener generaciones activas; usa SQLite backup e incluye datos,
modelos y configuración. No sobrescribe capturas. Copiar el archivo fuera del CT
y validar con scripts/check-voicebox-backup.py en un destino nuevo. Se verifican
paths confinados, hashes, enlaces internos, integridad SQLite y audios completados.
La restauración aislada de D063 conserva tres audios completados y cinco enlaces HF.
La imagen exacta tiene una exportación separada, con 22 blobs OCI verificados.

Actualizar exige backup coherente, candidato fijado y conservación de la imagen
anterior; recrear solo Voicebox y verificar persistencia e idempotencia. El rollback
usa la imagen anterior y datos compatibles; una migración SQLite exige restauración
coordinada. Nunca down -v, prune, borrado de modelos ni destroy automático.
RPO/RTO y retención global no se definen en esta alta.

[Inventario y contrato API](../../docs/inventory/627-LXC-INVENTORY.md) ·
[Notes](NOTES.md) · [Informe D063](../../docs/roadmap/PHASE7-D063-VOICEBOX.md).

## D064/D065 — voces ypropuestaQwen

voices-catalog.yml declara cuatro candidatas reales (Emma esbritánica experimental
enespañol). Alex aceptado porelpropietario; otras3 descartadas pero no borradas tras
laexigencia de diagnóstico/recomendación antes demás cambios productivos. Elperfil
originalD063 permaneceintacto. scripts/voicebox-voices.py reconcilia sin editar
perfiles existentes, reutilizaIDs demuestras yno repitePOST tras una solicitud registrada.
Model-lock incorpora solo523420bytes adicionales devozEmma, sin modelosQwen.

proposals/d064 contiene parcheBF16 yplan NO aplicados. La instalación activa sigue
CPUfloat32 paraQwen;4.57.3 ignora low_cpu_mem_usage. BF16/SDPA para0.6B merece prueba
separada dentro de4GiB, con carga/inferencia aún sinmedir. No ejecutar propuestas
ni limpieza antes de larevisión solicitada.
[Diagnóstico](../../docs/roadmap/PHASE7-D065-QWEN-OPTIMIZATION.md).

## Estado vigente D067

Prevalece [el informe D067](../../docs/roadmap/PHASE7-D067-QWEN-6G.md) sobre las
propuestas históricas anteriores. Se ensayó CustomVoice0.6B BF16/SDPA con6GiB:
cargaPASS, cortaTIMEOUT600s sinWAV, sinOOM. Final3GiB porrollback, originalKokoro
activa, candidata parada. Identidades reales en `voice-identities.yml`; masculino
conmuestra, femeninoSerena bloqueado sinmuestra, personal aún sinperfil ni grabación.
[Procedimiento de grabación/clonación/API y privacidad](VOICE-PROFILES.md).
No repetir piloto ni ejecutar Base por interpretar los parches preparados como
aceptación. Los tres perfiles rechazadosD064 siguen conservados, sinborrados.


## Histórico D068 — sustituido por el alcance personal D069

[Informe D068](../../docs/roadmap/PHASE7-D068-VOICEBOX.md). CT627 tiene7GiB; CPU3,
swap512MiB ydisco50GiB conservados. CustomVoice sigue sin audio aceptado: diagnóstico
finito mostró códigos reales yentrada encodec, pero las protecciones de presión/swap
detuvieron los ensayos. No se repitieron600s sin información ni se forzó másRAM.
La imagen operativa es la overlayPiperR2 fijada por `image-lock.json`; originalD063
conservada. CustomVoiceCPU falla rápido con explicación en lugar de forzar pesos.

Piper1.8.0 soporta porAPI el preset femenino es_ES-sharvard F; Kokoro/Alex conservados.
Selección real en `voice-identities.yml`. Un modeloTTS residente; generación serializada
porservidor ymutaciones de modelo rechazadas con409 durante trabajo. APIclient
`scripts/voicebox-narrate.py` probado paraambosroles, sin integrar elpipeline.
Piper entregaWAVPCM16mono22050Hz; Kokoro24000Hz. No suponer24kHz para cualquier motor.

Producción usaCompose con imagen aprobada, CPU3,RAM6200MiB yRAM+swap6600MiB:
400MiB de swap Docker comoantes, dentro del CT7GiB/swap512. Es un techo, no reserva.
El build deriva de laimagen original +overlayPiper con solo2wheels verificados,
CPU ONNX ymodelo77MB. La receta deoverlay vive en `pilot-d068/piper`; `deploy.sh`
comprueba imagen,fuentes,wheels ypesos fijados y no reconstruye silenciosamente.
No ejecutar `docker compose build` con fuentes flotantes: recuperar laimagen exacta
archivada o preparar/revisar otraimagen conforme el procedimiento delproyecto.

Backup exige cola vacía y conservaSQLite coherente, datos/modelos,KokoroHF,
originales privados cuandoexistan y `overlay-d068` (código,wheels,guías,flujoowner).
El verificador debackup admite ycomprueba las frecuencias reales por motor,
no confunde unWAVPiper22050 conunerror por no serKokoro24000. Restaurar rutas de
`overlay-d068` a `/opt/voicebox/pilot-d068` y recetas/locks al mismoárbol, junto a
los datos ylas referencias de la misma captura. MantenerWAV/DB/UUID coordinados.

El rollback usa `/opt/voicebox/d068-rollback` con receta,imagen yfuentes exactas de
la última versión estable. Elsupervisor deactivación ejecuta recuperación si falta
el marcador dePASS técnico; no implica aceptación auditiva. No borrar volúmenes,
modelos,imágenes ni perfiles rechazados. La restauración antigua `pilot-d068/restore.sh`
pertenece a los ensayos previos conimagenD063; no es elprocedimiento deactualización
sobre laoverlay aceptada. Ver elrollbackPiper coordinado yel informe vigentes.

[Guía de grabaciones, clonación y API](VOICE-PROFILES.md). Base0.6B preparado en
BF16/codecFP32 conguard de referencias reales; no descargado ni cargado. La subida
actualiza elUUID real y elcatálogo persistente; la prueba devozpropia ysu calidad
permanecen pendientes de grabaciones reales. No se crea unperfil personal ficticio.
