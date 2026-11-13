# IA local para chat

Subproyecto IA-CHAT, Fase 7. IaC Reliability, Security & Disaster Recovery.
Seguimiento: 13 de noviembre de 2026, Europe/Madrid. **Desplegado y validado técnicamente**, con la limitación STT descrita abajo.
La aceptación entre dispositivos y el micrófono real corresponde al propietario.

## Arquitectura

| CT | Nombre | DHCP actual | Recursos | Almacenamiento local-lvm |
|---|---|---|---|---|
| 630 | infra-llm | 192.168.1.67 | 4 CPU; 22528 MiB RAM; 1024 MiB swap | rootfs 16 GiB; modelos 60 GiB |
| 631 | infra-webui | 192.168.1.66 | 2 CPU; 4096 MiB RAM; 1741 MiB swap | rootfs 20 GiB |

Ambos usan Debian 12, contenedores no privilegiados y Europe/Madrid.
El volumen `/models` está en solo lectura y tiene `backup=0`.

- Panel: **http://192.168.1.66:3000**.
- API compatible con OpenAI: **http://192.168.1.67:8080/v1**; requiere API key.
- SearXNG solo está en la red de Compose, sin puerto publicado. Conserva salida a
  internet para consultar buscadores públicos.
- Historial, Knowledge y autenticación persisten en CT 631, `/opt/ia-chat/data`.
- Inferencia, embeddings y STT son locales. Los pesos se descargan de repositorios
  públicos; no se conectan APIs de pago.

Para reducir las copias de pesos en RAM se desactiva el repacking; se usa mmap,
selección de batch/ubatch por modelo en `services/infra-llm/config/performance-tuning.json`.
La matriz r3 compara b512/2048 y ub128/256/512, sin repacking.

Versiones y digests: `images.lock.json`; llama.cpp tag `v1.0.0`, commit efectivo
`b1b770d90d94cad9e9ea5b993bdbc383a522fb28`. El binario se identifica como
`1.0.0-dev` a pesar del tag. Compilación nativa para i5-6500/AVX2.

## Arrancar, parar y consultar logs

Desde PVE, exclusivamente para los CT nuevos:

```sh
pct exec 630 -- systemctl start llama-server
pct exec 630 -- systemctl stop llama-server
pct exec 630 -- journalctl -u llama-server -n 80 --no-pager
pct exec 631 -- sh -c 'cd /opt/ia-chat && docker compose up -d'
pct exec 631 -- sh -c 'cd /opt/ia-chat && docker compose stop'
pct exec 631 -- sh -c 'cd /opt/ia-chat && docker compose logs --tail 50'
```

No compartir logs completos, `docker inspect` ni `compose config` con secretos.

| Secreto | Ubicación | Permisos |
|---|---|---|
| API key | CT 630: `/etc/llama/api.key` | 600 |
| Copia de conexión y clave de sesión | CT 631: `/opt/ia-chat/secrets.env` | 600 |
| Secreto de SearXNG | CT 631: `/opt/ia-chat/searxng/settings.yml` | 600 |

## Modelos y razonamiento

Seleccionar en WebUI o enviar el campo `model` en `/v1/chat/completions`:

- `gemma-4-26b`: modelo de chat por defecto, con su proyector de visión.
- `qwen3.6-35b`: código y razonamiento, también con visión.

El router usa `--models-max 1`. Solo permite un modelo grande cargado y descarga
los pesos tras **3600 segundos** sin actividad. El contexto se divide entre dos slots:
**Gemma16384totales/8192por slot**, conSWAcompleta y plantilla que conserva el prefijo
de pensamiento desactivado; **Qwen65536totales/32768por slot**. Gemma se reduce desde
65536total para que la caché SWA completa respete el margen deRAM. Qwen se redujo desde 131072 al superar su RSS el 90 % del límite.
Gemma usa 3 hilos de generación y 4 de prompt; Qwen 3 y 3, según los benchmarks.
Las mediciones corresponden a las pruebas documentadas, sin certificar contexto lleno
ni dos conversaciones simultáneas.

El preset configura `chat-template-kwargs = {"enable_thinking":false}`.
Para activar por petición:

```json
{"chat_template_kwargs": {"enable_thinking": true}}
```

`reasoning-format = deepseek` separa el razonamiento en `reasoning_content`.
Probado: desactivado devuelve cero caracteres de razonamiento; activado devuelve
`reasoning_content` y responde correctamente la misma pregunta de lógica. En modo router, las métricas del modelo usan `/metrics?model=<alias>`.
No añadir este endpoint a scrapes automáticos: puede cargar pesos. La monitorización
usa Node Exporter/cgroup y `/health` sin inferencia.

Para añadir un modelo: revisar espacio y RAM, descargar y verificar bytes/SHA256,
añadir una sección a `/etc/llama/models.ini` con rutas, proyector compatible,
contexto y hilos aprobados; conservar el máximo de un modelo y validar antes de
usarlo. Modificar el volumen RO requiere un procedimiento autorizado. No reutilizar
un proyector de otro modelo sin comprobar su compatibilidad.

## Primer acceso, móvil y micrófono

Abrir el panel y crear la cuenta del propietario. La primera cuenta persistente
será administradora; Codex no establece credenciales para el propietario.
La prueba entre dispositivos corresponde al propietario y no se declara realizada.
Desde el móvil, conectado a la WiFi de casa, abrir la misma URL e iniciar sesión
con la misma cuenta para acceder al historial del servidor.

Para cerrar el registro: Administración > Configuración > General > permitir
registro, desactivar. Fijar también `ENABLE_SIGNUP: 'false'` en Compose y aplicar
`docker compose up -d` solo en CT 631. Open WebUI 0.13.3 desactiva automáticamente
`ui.enable_signup` al crear el primer administrador; comprobar el estado efectivo,
pues la configuración persistida puede prevalecer sobre las variables de entorno.

Para usar el micrófono por HTTP en Chrome para Windows:

1. Abrir `chrome://flags/#unsafely-treat-insecure-origin-as-secure`.
2. Añadir únicamente `http://192.168.1.66:3000`, habilitar y reiniciar Chrome.
3. Permitir el micrófono cuando lo solicite la interfaz.

HTTPS y acceso desde fuera de casa están fuera de alcance. El idioma por defecto
es español. La búsqueda web está habilitada en el servidor y apagada en cada chat
hasta que se active con el botón. RAG usa embeddings multilingües locales y top-k 3;
STT usa faster-whisper **small/int8**, CPU y español. En el WAV sintético reconoce
«Hola, esto es una nueva» para «Hola, esto es una prueba»: 4/5 palabras, WER 20 %.
Es una transcripción aproximada, no exacta; la calidad con voz real queda pendiente.
TTS no tiene motor de servidor, no reproduce automáticamente y su control se oculta
también al administrador mediante el hook oficial `custom.css`. El micrófono STT
permanece disponible. Títulos, consultas web, etiquetas, seguimientos, autocompletado y consultas RAG
desactivados. Herramientas nativas implícitas desactivadas por defecto en ambos
modelos; la búsqueda se activa explícitamente mediante el botón, en modo legacy.

## Norma manual de memoria y exclusión de CT 627

**CT 627 (Voicebox) está completamente fuera de esta tarea. No detenerlo,
reiniciarlo, modificarlo ni añadirle mecanismos de coordinación.** El propietario
acepta la norma manual de no usar Voicebox simultáneamente con el LLM.

Justo antes de cargar un modelo grande, verificar `MemAvailable` del **host**,
no la memoria virtualizada de LXCFS. Con menos de **21 GiB**, parar e informar;
no liberar memoria actuando sobre otros CT. La suma de límites virtuales no
acredita capacidad física concurrente. En las pruebas se descarga explícitamente
el modelo anterior antes de comprobar la guarda para la siguiente carga.

No usar Gemma mientras el futuro agente nocturno utilice Qwen. Ese agente no se
implementa en esta fase. No ampliar automáticamente la RAM de CT 631: superar
2,7 GiB exige informar y proponer el ajuste al propietario.

## Reservas DHCP pendientes del propietario

No hay un acceso específico al MikroTik en la configuración SSH local. No se han
intentado contraseñas ni alterado otros ajustes del router. Ejecutar en RouterOS:

```routeros
/ip dhcp-server lease make-static [find mac-address="BC:24:11:6F:79:36"]
/ip dhcp-server lease set [find mac-address="BC:24:11:6F:79:36"] comment="infra-llm"
/ip dhcp-server lease make-static [find mac-address="BC:24:11:0D:41:78"]
/ip dhcp-server lease set [find mac-address="BC:24:11:0D:41:78"] comment="infra-webui"
/ip dhcp-server lease print where comment~"infra-"
```

Las direcciones no están garantizadas hasta crear las reservas. Comprobarlas
tras reiniciar y mantener las IP anteriores en todos los componentes.

## Backups y restauración

Jobs creados en HDD `storage`, snapshot/zstd y hora Europe/Madrid: CT 631 diario
a las 03:30 (7 diarios y 4 semanales); CT 630 los domingos a las 04:00 (4 semanales).
Se conservan el backup inicial y otro final de CT 631, sin usuarios ni Knowledge
de prueba. Consultar el informe para archivo, bytes, SHA256 y verificación.
`/models` se excluye de vzdump; conservar el manifiesto de pesos con bytes/hashes.
Los backups de WebUI contienen historial, documentos, autenticación y secretos;
tratarlos como privados y conservar los permisos.

Para restaurar: localizar el vzdump verificado, elegir un **ID nuevo libre** y una
red aislada sin conflictos para la prueba. No restaurar sobre un CT existente sin
una autorización específica:

```sh
pct restore <ID_NUEVO> <ARCHIVO_VERIFICADO> --storage local-lvm --unprivileged 1
```

Revisar la configuración antes de arrancar. CT 630 necesita reconstruir el volumen
`/models` de 60 GiB, descargar y verificar los cuatro ficheros y volver a ponerlo
RO antes de iniciar llama-server. CT 631 necesita revisar la excepción AppArmor
aprobada y conservar sus datos y `secrets.env`. Preservar siempre el backup original.
Completar un vzdump no acredita una restauración funcional; consultar las pruebas
realmente realizadas en el informe.

## Excepción AppArmor aprobada solo para CT 631

Docker no arrancó con el perfil generado por `lxc-pve 6.0.0-1`; crun 1.31 tampoco
resolvió el bloqueo. El propietario autorizó expresamente
`lxc.apparmor.profile: unconfined` **solo en CT 631**, con reinicio de ese CT.
Se conserva el contenedor no privilegiado, los namespaces y seccomp, pero CT 631
carece del confinamiento AppArmor exterior. No extender esta excepción a otros CT
ni actualizar paquetes o perfiles globales bajo esta autorización.

Docker utiliza su runtime oficial runc. El binario crun descargado y su registro
inactivo se conservan como evidencia del intento. Reproducción de la excepción:
`scripts/ia-chat/apparmor-631.py` en PVE después del alta de CT 631.

## Reproducción y control de cambios

Las declaraciones canónicas son `inventory/services/infra-llm.yml` e
`inventory/services/infra-webui.yml`, integradas en `svc` de Terraform e importadas
sin recreación. El módulo admite plantilla Debian12 de archivo, unprivileged,
DHCP y volumen adicional mediante campos opcionales; conserva los valores legacy.
`services/ia-local/inventory.yml` y `provision.py` documentan el bootstrap histórico,
no deben usarse como otro gestor de recursos después de la adopción.

Configuración canónica por servicio en `services/infra-llm` y `services/infra-webui`;
los antiguos paths compartidos son enlaces relativos de compatibilidad. Node Exporter
nativo en ambos y cAdvisor solo631. Targets/reglas y módulos Blackbox se incorporan
aditivamente; Grafana Fleet/Details soportan explícitamente cAdvisor N/A en630.
Documentación en `docs/inventory/630-LXC-INVENTORY.md` y `631-LXC-INVENTORY.md`.
Receta detallada: `scripts/ia-chat/README.md`. No ejecutar deploy-all ni apply global.
TLS verificado con CA pública obtenida por SSH PVE estricto; estado/planes y backups
con secretos fuera Git en directorio privado del operador. Sin commit/push.

## Evidencia técnica y límites

Los cuatro GGUF pasaron bytes/SHA256 al primer intento y permanecen en volumen RO.
API con clave200/sin clave401, ambas lecturas deimagen4821, RAG7731, thinking,
historial/búsqueda tras reboot, mismosIPs, arranque automático e idempotencia: PASS.
RAG y STT simultáneos con exporters: pico631 de2,69GiB residente /2,85GiB working set, sinOOM. Cuenta técnica/Knowledge eliminados.
El administrador del propietario ya existe y se preserva; queda su prueba entre dispositivos.

Para la guarda90% se vigilan el mayor entreRSS y memoria de tareas residentes
(anon+file_mapped+kernel); se registra aparte la caché de archivos no mapeados.
`memory.current` incluye esa caché y puede acercarse al cupo sin dos modelos activos.
La guarda21GiB es delhost **antes** de cada carga; no es un mínimo durante inferencia.
La primera prueba conrepacking se interrumpió por presión, sinOOM; la swap delhost
aumentó. No se actuó sobre swap global ni sobre otrosCT para liberar memoria.

WhisperFP32 se descartó al alcanzar2,97GiB de trabajo y casi1GiB de swap en631.
Perfil small/int8. El propietario aprobó y se aplicaron **4096MiB**, sin reinicio
deWebUI. Nueva prueba RAG/STT:2,510GiB residentes/2,680GiBworking, sinOOM.
Los eventosmax jerárquicos se atribuyen al límite256MiB de cAdvisor; el contador
local del límite delCT permanece en0. No confundir ambas fuentes.
Una restauración funcional completa deCT no se ha ensayado; no confundir integridad
delarchivo ySQLite vivo con haber restaurado un servicio.

Monitorización final:600s/21muestrasPASS, sinanomalias;136consultasGrafanaPASS.
Recepción humana deTelegram para630/631 noensayada: no se declaran nuevas
cadenasCPU aceptadas por tener solo exporters/reglas/paneles.

## Optimización de latencia — IA-CHAT-LATENCY

Matriz r3 completada: Gemma b2048/ub512; Qwen b512/ub512, generación3h/prompt4h.
Prueba runtime3000: picos18,095/19,219GiB (<90%22GiB). Repetición sin cambios: sin
reinicios ni recreaciones; Terraform acotado no-op. Informe: `docs/roadmap/IA-CHAT-LATENCY-2026-11-13.md`.
La ruta real deWebUI pasó de344,401s/5324tokens en el saludo a0,444s/43tokens con
prefijo caliente al desactivar herramientas implícitas y tareas de fondo.
Con caché dehistorial corregida yGemmaSWAcompleta, tres turnos midieron
2,835/1,546/1,200s, reutilizando0/60/243tokens. Una conversación nueva con el modelo
cargado puede necesitar unos segundos de prefilling; prompts largos sin caché
siguen limitados por laCPU. Tras más de1h sin uso, puede existir una nueva carga fría.

Fuente del perfil WebUI: `services/infra-webui/config/chat-performance.json`;
render deCompose yreconciliaciónAPI en `scripts/ia-chat/latency/`. Las claves
persistidas prevalecen sobre el entorno; no basta con editarCompose.
Prompt objetivo con fecha: «Hoy es {{CURRENT_WEEKDAY}}, {{CURRENT_DATE}}.
Responde en español salvo que se te pida otro idioma. Sé directo y conciso.»
Ambas variables existen en v0.13.3; respuesta verificada: «Hoy es viernes» (13/11/2026).
La caché no fija globalmente todos los chats al slot0: se verifica selecciónLCP del
mismo slot en los turnos de una conversación, manteniendo dos slots disponibles.

Medición final con la ruta UI real: Gemma3,571/1,410/1,477s y Qwen4,193/4,039/2,634s
hasta el primer token en tres turnos; una petición por mensaje. Gemma reutiliza
0/77/112tokens y Qwen0/75/120, siempre el mismo slot dentro de cada conversación.
Una frase larga de búsqueda puede devolver cero resultados al usarse literalmente;
con generación de consultas OFF, usar términos de búsqueda breves con el botón.

Prueba de inactividad:300,779s sin inferencias, mismo PID y17,97GiB RSS;
saludo UI posterior1,609s hasta el primer token. Idle configurado3600s.

Búsqueda explícita UI verificada con3URLs, una sola llamada al modelo,785tokens y
49,434s hasta primer token. El objetivo<=10s es para chat corto sin recuperación.

Cuenta y Knowledge técnicos de latencia retirados; JWT anterior401. El administrador,
historial, documentos y propietarios de los modelos originales se conservaron.

## Conversaciones largas con Gemma

Gemma tiene **8192 tokens de contexto por conversación**, compartidos por sistema,
historial, documentos y respuesta. Usa chats cortos y temáticos; carpetas y búsqueda
del historial ayudan a organizarlos y recuperarlos, pero no amplían la memoria del
modelo. El historial sigue guardado aunque su principio quede fuera del contexto.
Los prompts largos pueden tardar más en arrancar cuando deben volver a procesarse;
la caché evita que esa subida sea necesariamente progresiva en cada turno.

Al cambiar de chat, lleva un resumen revisado de objetivos y decisiones. El
[plan de contexto](../../docs/roadmap/IA-CHAT-CONTEXT-PLAN.md) explica los límites,
las opciones futuras y las pruebas pendientes; ninguna ampliación está desplegada.

Swap de CT631 ampliada por autorización a1741MiB (~1,7GiB), sin reinicios.
Fuente: `inventory/services/infra-webui.yml`; reconciliación acotada mediante
`scripts/ia-chat/resize-swap-631.py`. Es cuota del CT sobre la swap del host,
no swap física adicional ni una mejora garantizada de velocidad.
