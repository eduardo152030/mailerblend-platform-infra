# Fase 7.4 — Voicebox real en Proxmox LXC — D063

Estado: **DONE técnico del primer alta real CT627**. Cierre 2026-11-10 13:25 CET (Europe/Madrid).
Fase7 global IN PROGRESS; 7.2/7.3 continúan OUT OF SCOPE. No aceptación humana inventada.

## Resultado operativo

- CT627 infra-voicebox, http://192.168.1.127:17493, web/API privadas en LAN.
- 3vCPU, 2048MiB RAM, 512MiB swap, 50GiB local-lvm, Ubuntu22.04.5LTS.
- Inicio real con1080MiB de plantilla106; aumentos medidos1536→2048MiB conforme
  a la autorización del propietario. No se asignaron8/16GiB.
- Fork fijado `8af7efe62fab8d33e2a5dfbedabaa45f68a5184f`, sin parches de aplicación.
- Imagen exacta fijada en image-lock.json; tag local/voicebox:8af7efe62fab-cpu-d063.
- Docker29.0.2/Compose2.40.3 y Voicebox0.6.0 healthy; modelos fijados/offline.
- Kokoro CPU, español, Dora: **12,94s** para WAV PCM16 mono24kHz de **6,46s**.
  [Audio final](http://192.168.1.127:17493/audio/005163a8-9721-4c8b-8f7b-bfd00b0a10d2).
- Cobertura18Node/18cAdvisor/19Blackbox; 18filas Fleet saludables y ceroUNKNOWN;
  uptime627 frentePVE con diferencia30s, dentro delcontrato45s.
- Observación600,05s/21muestras PASS, sin FIRING/PENDING; segunda aplicación
  Terraform0/0/0, Compose sin recreación/reinicio y monitorización sin escritura/recarga.
- Backup coherente restaurado aisladamente fueraPVE:25archivos verificados, SQLiteok,
  cinco enlaces confinados y tres audios completados. Imagen archivada aparte:
  1206316979bytes, manifiesto y22blobsOCI verificados.
- Tiempo desde declaración del alta: aproximadamente **120.1min**; diagnóstico
  preliminar de la intervención anterior aproximadamente5min, separado.

## Aceptación verificable

| Criterio de la petición | Resultado y evidencia |
|---|---|
| 1. Terraform real | Plan inicial1create/0change/0destroy y creación627 observada |
| 2. SSH por clave | D062 real PASS antes/después del endurecimiento, contraseña deshabilitada |
| 3–6. Docker/web/API | Runtime healthy, API JSON y navegador real PASS |
| 7. Audio real | WAV descargado, hash/formato/duración/señal verificados; [TTS](evidence/2026-11-10-d063-tts.json) |
| 8. Persistencia | Perfil y audio con igual ID/hash tras reinicio; [prueba](evidence/2026-11-10-d063-persistence.json) |
| 9–11. Grafana/uptime/exporters | Fleet/Details dinámicos627, CPUcgroup/RAMLXCFS y uptimePVE; [Fleet](evidence/2026-11-10-d063-fleet.json), [navegador](evidence/2026-11-10-d063-final-browser.json) |
| 12. Preservar17CT | HashesPVE17idénticos y56targets previos idénticos; [preservación](evidence/2026-11-10-d063-preservation.json) |
| 13. IaC reproducible | Inventario/Terraform/SSH/Compose/scripts y modelos fijados; imagen exacta archivada y bloqueada porID/hash |
| 14. Segunda aplicación | Terraform0/0/0, Compose0recreaciones/0reinicios, monitorización0escrituras/recargas |
| 15. Recuperación | Backup/restauraciónaisladaPASS; [restore](evidence/2026-11-10-d063-restore.json), [imagen](evidence/2026-11-10-d063-image-backup.json) |
| 16. Notes/inventario | Notes627 aplicadas porTerraform, solo descripción; [inventario](../inventory/627-LXC-INVENTORY.md) |
| 17. Contrato futuro | API real documentada en inventario; pipeline sin cambios |

[Resultado consolidado](evidence/2026-11-10-d063-result.json),
[estabilidad](evidence/2026-11-10-d063-observation.json),
[idempotencia Compose](evidence/2026-11-10-d063-compose-idempotence.json).
Pruebas locales:16provisioning y15inventario, fmt/validate, promtool/parserBlackbox,
enlaces y diff--check. Planes, estado, logs y backups sensibles permanecen privados.

## Incidencias resueltas y límites

1. DSA heredada provocó fallo de provisioner/taint. Selector corregido con prueba,
   bootstrap recuperado antes de untaint exclusivamente627; no destroy/reemplazo.
2. 1080MiB saturó RAM/swap. El primer intento quedófailed y se conserva enUI/SQLite.
   1536MiB permitióTTS26,98s pero solo13,7%RAMlibre;2048MiB permitió15,40s/12,94s
   y margen suficiente. Reinicios de memoria afectaron solo627.
3. Primera reglaLAN bloqueaba respuestas; corregida con direcciónORIGINAL, sin
   ampliar red ni tocar otras políticas. API sin autenticación integrada acreditada.
4. Verificador de modelos heredaba healthcheckHTTP inaplicable; ahora es efímero
   sin ese check. Sus series antiguas generaronPENDING transitorio, sinFIRING,
   desaparecido antes de la observación final. Umbrales/reglasF5 intactos.
5. Filtro tarfile3.10 rechazó enlacesHF legítimos. Restauración corregida con
   validación de rutas/destinos confinados, sin devices/hardlinks, y hashes completos.
   Una lecturaPVE agotó30s durantecopias; repetición posteriorPASS, sin relajarSSH/TLS.
6. Catálogos IaC previos diferían delruntime en etiquetasCPU yorden. Se adoptó el
   catálogo vivo antes de añadir627; ningún target previo cambió enproducción.

No se afirma escucha/UAT humana, generación concurrente, otros motores/idiomas,
nuevo ensayoTelegram, build limpio bit-a-bit o restore completo enotroLXC. La imagen
archivada garantiza la receta exacta de runtime; los rangos pip upstream siguen
sin ser un lock de construcción nuevo. No crear credenciales o exponerWAN.
Contenedor test-nginx heredado deplantilla conservado en627, puerto8080 IPv4/IPv6;
no se usó como prueba deVoicebox. RangoDHCP/exclusión127 pendiente de contraste
administrativo; no se afirma reservaDHCP creada. DR/retención continua sigueF7.3.

## Archivos del alcance

- IaC: main.tf (etiquetas solo nuevasaltasSSH), inventory/services/infra-voicebox.yml,
  inventory/generated/lxc-notes*.json y docs/inventory/LXC-INVENTORY.md.
- Servicio: services/infra-voicebox/ con Dockerfile.cpu, Compose, deploy, controlLAN,
  preparación/model-lock/image-lock, backup, README yNotes.
- Monitorización: catálogosNode/cAdvisor/sondas, voicebox-inventory.yml y móduloBlackbox.
- Herramientas: generate-lxc-inventory.py, voicebox-monitoring.py, verify-voicebox.py,
  verify-voicebox-browser.py, observe-voicebox.py ycheck-voicebox-backup.py.
- SSH: selectorhostkeys en bootstrap-ssh-guest.py ytestDSA; pruebasinventario para
  crecimiento17→18 yNotes de un servicio observado sin metadatahistórica.
- Documentación: inventario627, runbookaltas, ROADMAP, CURRENT-STATUS, DECISIONS,
  fichaF7, esteinforme y evidenciasD063. Trabajo previoD062 y cambiosajenos conservados.

Sin commit/push, cambios en Pipeline_videos_modulares, apps/DB/recursos deotrosCT,
proxygeneral ni publicación pública. Siguiente: uso interno y revisión del propietario;
futura integración del pipeline u otros motores en una intervención separada.

## Historial de diagnóstico y ejecución, sustituido por el cierre anterior

### Diagnóstico previo D063

Estado: **IN PROGRESS**, 2026-11-10 11:19 CET (Europe/Madrid).

## Autorización aprobada

El propietario autoriza un único LXC nuevo Voicebox, preferentemente627, Terraform
con plan real exclusivamente1create/0change/0destroy, bootstrapD062, Compose,
generación real, persistencia y alta aditiva de monitorización. Sin aplicaciones
existentes, exposición pública, pipeline de vídeos, destrucciones, commit ni push.
Se registra esta ampliación antes de cualquier ejecución productiva. Solo se han
realizado lecturas de diagnóstico; no hay creación ni aplicación.

## Evidencia real y bloqueo

SSH PVE con known_hosts del propietario, StrictHostKeyChecking=yes y BatchMode=yes.
Lectura11:18:34CET:627 ausente de recursos y sin /etc/pve/lxc/627.conf.
Nodo i5-6500,4CPU físicos,16646774784bytes RAM total (15,50GiB).
MemAvailable9185411072bytes (8,55GiB), swap usada4484759552bytes (4,18GiB).
Presión memoria some avg300=0.40 y full avg300=0.33. Un presupuesto adicional de
8GiB deja aproximadamente0,55GiB disponibles;16GiB excede la RAM total.
**No se considera capacidad segura para este alta permanente junto a las cargas
existentes.** Es valoración de riesgo, no prueba de que Kokoro no pueda arrancar.
No se reduce el mínimo solicitado ni se interpreta swap como RAM adicional.
Raíz PVE89% usada,7,15GiB disponibles; local-lvm aproximadamente175GiB libres;
storage directorio aproximadamente1,33TiB libres. Son capacidades puntuales,
no asignaciones ni verificación completa del backend para el nuevo CT.
GPU PCI detectada Intel HD Graphics530; no acredita aceleración compatible ni
passthrough utilizable. No se han modificado dispositivos ni recursos.

## Revisión de fuentes

Fork y upstream HEAD consultados por git ls-remote coinciden en
`8af7efe62fab8d33e2a5dfbedabaa45f68a5184f`. Fork clonado en
`/tmp/voicebox-d063-review`, fuera del repositorio; código fuente sin modificar.
La igualdad de HEAD acredita la misma revisión anunciada, no equivalencia futura.
Fuentes: [fork](https://github.com/eduardo152030/voicebox/tree/8af7efe62fab8d33e2a5dfbedabaa45f68a5184f),
[original](https://github.com/jamiepine/voicebox/tree/8af7efe62fab8d33e2a5dfbedabaa45f68a5184f),
[documentación oficial](https://docs.voicebox.sh/).
Compose CPU:4CPU/8G, loopback17600→17493, restart unless-stopped.
Persistencia declarada: /app/data (DB/perfiles/cache), generaciones con bind propio,
y /home/voicebox/.cache/huggingface. Requiere backup coordinado DB/audio/perfiles/modelos
con prueba de restauración antes de aceptar recuperación.
Dockerfile incluye frontend Bun, Python3.12, ffmpeg/sox, paquetes y repositorios
sin fijación completa: fijar commit por sí solo **no hace reproducible la imagen**.
Pendientes digests de bases, dependencias/modelos y verificación de build CPU real.
Healthcheck hace curl /health: no acredita inferencia ni reinicia por sí solo un
contenedor unhealthy. Debe validarse JSON y generación real por separado.
Motores enumerados en esquema: qwen, qwen_custom_voice, qwen_voice_design, luxtts,
chatterbox, chatterbox_turbo, tada, kokoro y omnivoice; documentación web anuncia8,
por lo que manda la revisión del fork. Candidato inicial: Kokoro82M,
hexgrad/Kokoro-82M, CPU, español, salida24kHz según backend; tamaño real/revisión
de descarga, licencia de cada voz y consumo pendientes. No descargado ni probado.
No se ha identificado autenticación exigida en factory/rutas inspeccionadas;
ClientIdMiddleware y CORS no acreditan control de acceso. Tratar API como sin
autenticación hasta auditoría completa y restringir clientes/red antes de publicar
un puerto LAN. No se ha publicado ningún puerto.

## Contrato futuro propuesto, sin implementación

GET /profiles y /profiles/presets/kokoro para preparar perfil compatible;
POST /generate con profile_id,text,language=es,engine=kokoro devuelve id y status.
No asumir finalización en la respuesta inicial. Seguir SSE
GET /generate/{id}/status o consultar GET /history/{id}; estado completed y
GET /audio/{id} para recuperar el resultado, comprobar formato/duración reales.
El audio_path del servidor no es una ruta local del cliente.
Propuesta cliente: timeout conexión5s, salud15s, presupuesto generación600s a
calibrar con prueba real; reintentar GET con backoff limitado. No repetir POST
ciegamente tras timeout: puede duplicar trabajos; conservar id y reconciliar.
Gestionar404perfil,400incompatibilidad,failed/error y caídas del servicio.
Lotes inicialmente secuenciales, concurrencia pendiente de medición. Preservar
relación vídeo→id→audio. No se ha modificado Pipeline_videos_modulares.

## Resultados y pendientes

No CT creado, IP reservada/validada, URL activa, recursos asignados, Docker/app,
Notes productivas, audio ni tiempo de generación. Tampoco plan real, bootstrap,
segunda aplicación, backups del servicio o integración Prom/Grafana probados.
No cambios productivos en los17CT; no se afirma nueva auditoría completa de su
cobertura. Inventario627 definitivo pendiente; no registrar servicio inexistente
como desplegado. Criterios de aceptación1–17 pendientes.
Tiempo diagnóstico aproximado:5min; implementación productiva no iniciada.

## Alternativas propuestas, pendientes de decisión

1. Ampliar RAM del nodo y revalidar margen/almacenamiento antes de reservar CT/IP.
2. Usar otro nodo con al menos8GiB adicionales y margen para sistema/cargas.
3. Liberar capacidad mediante intervención separada aprobada y medición posterior;
   no parar ni reducir recursos de servicios existentes durante esta petición.

Siguiente: decisión del propietario sobre capacidad. Después revalidar identidad,
red/IP, plantilla106, Docker/LXC y almacenamiento; preparar bundle con new-lxc.py,
validaciones y plan real de único recurso antes de apply. Recuperación tainted según
[runbook](../runbooks/NEW-LXC-PROVISIONING.md), sin reemplazo automático.

## D063 — reanudación aprobada con recursos de plantilla

2026-11-10 (Europe/Madrid). El propietario sustituye el mínimo inicial8GiB:
autoriza comenzar con los recursos de la plantilla y valorar aumentos graduales
según consumo real. CT106 comprobado:3vCPU,1080MiB RAM,512MiB swap,50GiB
local-lvm. 7.4 **IN PROGRESS**; bloqueo previo de capacidad levantado para este
presupuesto, sin afirmar viabilidad TTS hasta probarla. Se conserva alcance único
CT627 y plan1create/0change/0destroy, sin cambios en los17CT existentes.
Siguiente: preparar bundle, validar plan real y ejecutar alta autorizada.

Los diagnósticos/bloqueos anteriores se conservan como historial sustituido.

## D063 — primer CT real creado, aplicación en preparación

CT627 infra-voicebox creado porTerraform desdeCT106:3vCPU,1080MiB RAM,
512MiB swap,50GiB local-lvm,192.168.1.127. SSHporclave verificado, contraseñas
deshabilitadas. Bootstrap recuperado sin recreación tras detectar DSA obsoleta;
16testsPASS. Estado tainted retirado solo tras recuperar/acreditarSSHdelnuevoCT.
Segunda aplicación realTerraform:0altas/0cambios/0destrucciones. EtiquetasIP/orden
normalizadas enIaC exclusivamente para nuevasaltasSSH;17CTlegados sin cambio.
Node/cAdvisor y contratoCPUcgroup/RAMLXCFS627 verificados directamente.
Voicebox aún construyéndose; sin audio ni aceptación declarados. Targets todavía
no activados. Candidato monitorización conbackup/restauraciónaislada, promtool y
parserBlackboxPASS. Sigue7.4INPROGRESS, noDONE. Sin commit/push.

## Aumento progresivo medido —1080→1536MiB

PrimerintentoKokoro:CT1123475456bytesRAM y536637440bytesswap, PSI some31.65/full29.55
(avg10), sinOOMregistrado. Node agotótimeout10s; no se acepta elensayo. Conforme
a instrucción explícita deampliar progresivamente segúnnecesidad, presupuesto627
sube a1536MiB, Compose1200m/1500mcombinada. SoloelCTnuevo; CPU/disco/17CTintactos.
Se exige plan exclusivo627 antes deaplicar, sinreemplazos.

## Segundo escalón —1536→2048MiB

TTSrealPASS a1536MiB:26.98s paraWAV24kHzmono6.46s. SinOOM, peroMemAvailable
221155328/1610612736bytes=13.7% conmodelo cargado; presión real y avisopermanente
HostMemoryPressure previsto si continúa<20%durante10m. No modificar umbralF5.
Siguienteaumento progresivo2048MiB, Compose1600m/2000mcombinada, solo627.
Elproviderreinicia627 almodificar memoria; observado vzreboot duranteprimerescalón.
Backup coherente datos/modelos creado antes deestesegundoescalón; nada de17CT.
