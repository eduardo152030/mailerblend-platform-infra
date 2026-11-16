# Cline en Windows con Qwen local

14/11/2026, Europe/Madrid. **Fase 7. IaC Reliability, Security & Disaster Recovery**.
Estado: documentación **DONE**; configuración y aceptación de Cline en Windows **TODO**.
Solo lectura de fuentes y escritura documental: sin llamadas al modelo, descargas,
SSH, cambios de CT/configuración, commit ni push en esta intervención.

## 1. Conexión y prueba manual desde Windows

API base: **`http://192.168.1.67:8080/v1`**, CT **630**, router llama-server.
Model ID exacto: **`qwen3.6-35b`**, pesos **Qwen3.6-35B-A3B UD-IQ4_XS**.
No descargar Qwen3-Coder ni instalar LM Studio para esta conexión.

La clave está en **CT 630 `/etc/llama/api.key`**, permisos 600. El propietario
puede leerla en una consola administrativa existente de ese CT con
`sudo cat /etc/llama/api.key` (o `cat` como root), introducirla en el campo secreto
de Cline y cerrar la consola. No adjuntarla al chat, capturas, repositorio ni `.env`.
La copia de CT 631 `/opt/ia-chat/secrets.env` contiene otros secretos: no volcarla.
Si se usa SSH administrativo, conservar identidad verificada, `BatchMode=yes`,
`StrictHostKeyChecking=yes` y `UserKnownHostsFile=$HOME/.ssh/known_hosts`; no reutilizar
los defaults inseguros del alias PVE. Cline no necesita acceso SSH para llamar a la API.

Pruebas **para ejecutar por el propietario**, desde PowerShell 5.1 o 7. `curl.exe`
evita el alias de PowerShell. El secreto se solicita oculto y se pasa por stdin
al config de curl, sin escribirlo literalmente en el historial o en argumentos.
El chat sí produce inferencia y puede cambiar el modelo residente: cerrar antes Gemma.

```powershell
$base = 'http://192.168.1.67:8080/v1'
$secureKey = Read-Host 'API key de CT 630' -AsSecureString
$ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureKey)
try {
    $key = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr).Trim()
    $curlAuth = 'header = "Authorization: Bearer ' + $key + '"'
    $curlAuth | curl.exe --config - --silent --show-error --fail-with-body `
        --connect-timeout 10 --max-time 30 "$base/models"
    if ($LASTEXITCODE -ne 0) { throw 'Fallo en /models; revisar red/clave antes del chat' }

    $body = @{
        model = 'qwen3.6-35b'
        messages = @(@{ role = 'user'; content = 'Responde solamente: OK' })
        max_tokens = 32
        temperature = 0.6
        top_p = 0.95
        top_k = 20
        min_p = 0.0
        cache_prompt = $true
        chat_template_kwargs = @{ enable_thinking = $false; preserve_thinking = $true }
        stream = $false
    } | ConvertTo-Json -Depth 8 -Compress
    $payload = [IO.Path]::GetTempFileName()
    try {
        [IO.File]::WriteAllText($payload, $body, [Text.UTF8Encoding]::new($false))
        $curlAuth | curl.exe --config - --silent --show-error --fail-with-body `
            --connect-timeout 10 --max-time 1800 `
            -H 'Content-Type: application/json' --data-binary "@$payload" "$base/chat/completions"
        if ($LASTEXITCODE -ne 0) { throw 'Fallo en chat; consultar diagnóstico' }
    } finally { Remove-Item -LiteralPath $payload -ErrorAction SilentlyContinue }
} finally {
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr)
    Remove-Variable key, curlAuth, secureKey -ErrorAction SilentlyContinue
}
```

Esperado: `/models` contiene `qwen3.6-35b`; chat devuelve
`choices[0].message.content` con OK. La lista no prueba que los pesos estén cargados.
El token transita por HTTP: usar solo la LAN de confianza, sin publicar el puerto.
Las variables de texto existen temporalmente en memoria; no activar transcripción.
Si curl antiguo no reconoce `--fail-with-body`, usar `--fail`.

## 2. Configurar Cline paso a paso

1. En VS Code de Windows instalar **Cline**, extensión `saoudrizwan.claude-dev`;
   anotar la versión instalada. Abrir una carpeta de prueba local, sin credenciales.
2. Abrir Cline → engranaje → API Configuration. Elegir **OpenAI Compatible**.
3. Rellenar los campos siguientes y guardar. Si Plan y Act tienen configuraciones
   separadas, repetir en ambos; no dejar un proveedor remoto en uno de ellos.
4. En Settings → Features activar **Use Compact Prompt**, si está disponible para
   ese proveedor. La guía oficial lo recomienda para modelos locales. Si la versión
   solo lo ofrece para Ollama/LM Studio, no cambiar de protocolo ni inventar claves
   JSON: conservar OpenAI Compatible, reducir contexto añadido y registrar la limitación.
5. Empezar en Plan para revisar alcance; pasar a Act para ejecutar la tarea mínima.

| Campo | Valor de inicio |
|---|---|
| API Provider | OpenAI Compatible |
| Base URL | `http://192.168.1.67:8080/v1` |
| OpenAI Compatible API Key / API Key | Clave real de `/etc/llama/api.key` |
| Model ID / Custom Model ID | `qwen3.6-35b` |
| Context Window Size | **32768** |
| Max Output Tokens | **2048**, propuesta conservadora para empezar |
| Temperature | **0.6**, conserva el perfil actual |
| Supports Images | **Sí** para el alias actual; evitar imágenes en la prueba inicial |
| Azure Identity / Azure API version | Desactivado / sin configurar |
| Custom Headers | Vacío; el campo API Key genera Authorization |
| Input / Output Price | 0 si se pide; no representa consumo eléctrico |

El contexto de 32768 incluye sistema, herramientas, historial, archivos, razonamiento
y respuesta. Con 2048 de salida, no presupuestar más de 30720 de entrada; dejar margen
adicional y comenzar muy por debajo. Aumentar salida a 4096 solo para tareas que lo
necesiten, reservando ese espacio de entrada. Cortar una llamada de herramienta por
límite de salida puede producir argumentos incompletos.

**Muestreo:** perfil actual `temperature=0.6`, `top_p=0.95`, `top_k=20`, `min_p=0`.
Cline expone Temperature; el componente OpenAI Compatible consultado no tiene
campos top_p/top_k/min_p. No colocarlos en Custom Headers: son parámetros del body.
Cuando el cliente no los envía, se usan los defaults del servidor. Si una versión
ofrece extra body, los nombres anteriores son los de llama-server; validar la petición
antes de asumir que se aplican. No se ha cambiado ningún valor.

La ficha oficial Qwen recomienda esos valores para **coding preciso con thinking**;
el servidor actual desactiva thinking. Para instruct general recomienda
0.7/0.8/20/0 y presence_penalty=1.5, repetition_penalty=1.0. Son perfiles distintos:
se conserva primero el actual para aislar compatibilidad y latencia; comparar el
perfil instruct queda propuesto, sin afirmar que el actual sea el óptimo oficial
para non-thinking. No añadir repeat_penalty=1.05 del gist automáticamente.

Supports Images sí refleja el mmproj desplegado y la prueba histórica de visión.
No implica que se haya validado la ruta de imágenes de Cline. Browser/Computer Use
puede quedar desactivado; visión y permisos de navegador son conceptos distintos.
La compactación de historial es otra función distinta de Use Compact Prompt y también
consume inferencia; una nueva tarea breve puede ser más barata que resumir una muy larga.

Fuentes: [configuración oficial Cline](https://docs.cline.bot/provider-config/openai-compatible),
[modelos locales y Compact Prompt](https://docs.cline.bot/running-models-locally/overview),
[campos de la interfaz consultada](https://github.com/cline/cline/blob/main/apps/vscode/webview-ui/src/components/settings/providers/OpenAICompatible.tsx).
La versión Windows no está instalada ni inspeccionada en esta intervención; los rótulos
pueden variar y los valores deben verificarse tras guardar.

## 3. Autonomía y seguridad

En una carpeta local aislada, autoaprobar **Read project files** y, tras la primera
prueba revisada, **Edit project files**, con checkpoints. Dejar **Read all files**,
**Edit all files**, browser, MCP y YOLO desactivados. Excluir claves, `.env`, estados
Terraform y backups también del contexto; una instrucción no sustituye aislamiento.

Comandos: empezar con aprobación manual. Solo considerar **Execute safe commands**
para una carpeta sin acceso a producción y pruebas locales conocidas. Cline clasifica
la seguridad mediante el modelo (`requires_approval`), no mediante una allowlist
infranqueable; **Execute all commands** debe seguir desactivado. No autoaprobar SSH,
Terraform apply, despliegues, reinicios, borrados, instalaciones, commit ni push.
Tests/builds pueden ejecutar scripts del repositorio: revisar su contenido primero.

Configurar **Max Requests = 5** en Auto Approve si la versión ofrece el control;
ampliar a 10 solo tras una tarea correcta. Al alcanzar el límite, revisar el diff
antes de continuar. No confundir este contador con tokens o duración. Si no existe
el control, conservar aprobación manual; no simular un límite que no se impone.

Trabajar en una rama de prueba creada por el propietario, por ejemplo
`git switch -c prueba/cline-qwen`, desde una copia limpia. Este workspace ya tiene
cambios ajenos: no usarlo para la prueba ni resetearlos. Una rama no aísla archivos
sin commit; usar otra copia si los hay. Revisar `git diff` antes de aceptar cada tarea.

Una clave SSH/ssh-agent accesible a la terminal puede dar al agente autoridad real
sobre PVE, CT, volúmenes y secretos. No abrir esta prueba en Remote-SSH a Proxmox ni
dar a Cline root/PVE o un MCP de infraestructura. Reglas de texto y checkpoints no
revierten una acción remota. La autorización histórica de otros trabajos no se
transfiere a Cline. [Permisos oficiales](https://docs.cline.bot/features/auto-approve).

## 4. Servidor: estado documentado y propuestas

**Última evidencia operativa: 13/11/2026**; lectura documental el 14/11.
No se ha reconsultado producción ni se presenta Git como verificación actual del CT.

| Parámetro Qwen | Último perfil aplicado/documentado |
|---|---|
| Binario | tag v1.0.0, commit `b1b770d90d94cad9e9ea5b993bdbc383a522fb28`, reporta 1.0.0-dev |
| Router | `--models-max 1`, puerto 8080, API key file |
| Preset efectivo | CT 630 `/etc/llama/models.ini` |
| Contexto total / parallel | 65536 / 2; **32768 por slot** |
| Batch / ubatch | 512 / 512 según selección aplicada |
| Hilos generación / prompt | 3 / 4 según selección aplicada |
| Repack / carga | desactivado / mmap; CPU, n-gpu-layers=0 |
| Jinja | true; plantilla Qwen del GGUF, sin template Coder externo |
| Template kwargs | `enable_thinking=false`, `preserve_thinking=true` |
| Reasoning format | deepseek |
| Proyector | mmproj-F16.gguf; image-max-tokens=128 |
| Idle | 3600 s |
| cache-ram | 0; distinto de la KV cache del slot |
| cache_prompt | true explícito en perfil WebUI; verificar en peticiones de Cline |

[Preset canónico](../../services/infra-llm/config/models.ini.template),
[selección de rendimiento](../../services/infra-llm/config/performance-tuning.json),
[unidad router](../../services/infra-llm/systemd/llama-server.service),
[versiones](../../services/ia-local/versions-installed.json).
La plantilla base contiene ubatch128/threads4: el perfil final aplica las selecciones
512/3 del JSON; no confundir una plantilla sin renderizar con el preset efectivo.

La API chat acepta tools/tool_choice y Jinja prepara su formato; un parser debe
convertir la salida del modelo a `tool_calls` válido si Cline utiliza herramientas
nativas. Cline puede usar protocolo de herramientas textual según versión/modo;
ese caso no demuestra compatibilidad con tools nativos. `reasoning-format=deepseek`
se refiere al razonamiento, no elige por sí solo un parser de funciones.
El `function_calling=legacy` de **WebUI** no configura Cline, que llama directamente
al router. No desactivar las herramientas de Cline para copiar ese ajuste.

**Propuestas TODO, sin aplicación ni nueva autorización de servidor:**

- Probar primero alias actual y tarea mínima. Un alias de texto sin mmproj puede
  ahorrar memoria, pero no es requisito probado para Cline; usaría los mismos pesos,
  no otro modelo descargado, y declararía Supports Images=no. Ya figura en
  [backlog IA-LLM-OPTIMIZE](../roadmap/IA-LLM-OPTIMIZE.md).
- Valorar parallel=1 con ctx-size=65536 para un slot mayor, midiendo memoria/latencia;
  no declarar 65536 en Cline hasta aplicarlo y verificarlo. La ampliación histórica
  a 131072 total excedió el margen RSS del 90% de 22GiB; no repetirla sin evaluación.
- Ante un fallo reproducible de tool_calls, probar plantilla/parser compatible con
  **Qwen3.6 y el commit instalado**, en ensayo acotado con rollback. No instalar
  una plantilla Qwen3-Coder ni flags de vLLM/SGLang en llama-server.
- Comparar muestreo instruct o thinking y extra body/cache solo con pruebas antes/
  después. Preservar el perfil funcional actual y documentar toda propuesta como tal.

## 5. Rendimiento medido y tiempos esperables

[Informe y evidencias de latencia](../roadmap/IA-CHAT-LATENCY-2026-11-13.md),
mediciones del 13/11/2026 (las marcas UTC originales se conservan allí).
Qwen: **pp512=27.148 tokens/s**, **pp2048=26.473 tokens/s**,
**tg128=5.258 tokens/s**, tres repeticiones por benchmark.
TTFT real de **3000 tokens sintéticos nuevos: 139.371 s**, sin caché en `/completion`;
antes 133.432 s. Mejorar el benchmark no mejoró esa medida runtime.
Los saludos WebUI de 2.6–4.2 s no representan prompts de agente.

Estimación orientativa sin caché: lectura entre N/26.473 y N×139.371/3000;
generación G/5.258. No es un benchmark de Cline; no incluye carga fría, cola,
ejecución de comandos ni coste extra de herramientas/thinking.

| Entrada nueva | Lectura / TTFT estimado | Paso con 512 tokens de salida (~97 s adicionales) |
|---:|---:|---:|
| 1000 | 38–46 s | 135–144 s |
| 3000 | 113–139 s; 139 s medidos en prueba sintética | 211–237 s |
| 8000 | 302–372 s | 400–469 s |
| 16000 | 604–743 s | 702–841 s |

2048 tokens de salida pueden consumir ~390 s solo generando; un paso con varias
herramientas puede requerir varias peticiones. La extrapolación pierde precisión con
contextos largos. La caché ayuda al prefijo estable, no elimina lectura de texto nuevo.

**No usar Gemma mientras Cline usa Qwen**, tampoco desde otra pestaña WebUI:
el router solo mantiene un modelo grande; alternar modelos expulsa pesos y cachés,
añade carga fría y hace inválida la expectativa de tiempo en caliente.

## 6. Problemas típicos

| Síntoma | Diagnóstico y actuación del propietario |
|---|---|
| Contexto excedido / HTTP 400 | Confirmar 32768 y reservar salida; quitar archivos/logs masivos, resumir o abrir tarea nueva con alcance corto. No aumentar el número declarado sin ampliar realmente el slot. |
| tool_calls malformados / XML mostrado como texto | Separar protocolo textual Cline de tools nativos; revisar finish_reason, longitud de salida y JSON de argumentos sin secretos. Reintentar una sola tarea pequeña; si falla, detener el bucle y registrar versión/plantilla. Cambiar parser o plantilla es propuesta de servidor, no arreglo aplicado. |
| Timeout antes del primer token | 8k nuevos pueden superar 6 min; streaming no elimina el prefill. Reducir prompt, activar compacto si disponible y configurar timeout del proveedor cuando exista, como se indica debajo. |
| Caché no reutilizada | Comparar tokens nuevos/reutilizados en métricas/logs filtrados; verificar cache_prompt del body, mismo modelo, prefijo y plantilla estables. Cambios en sistema/herramientas/orden/fechas o compactación invalidan el prefijo; slots distintos y eviction también. No forzar todos los chats al slot0 ni confundir cache-ram=0 con ausencia de KV. |
| Primera respuesta lenta tras inactividad | Idle=3600 descarga pesos; esperar carga fría. /models solo enumera modelos. No usar pings continuos ni cambiar el idle sin permiso; una petición manual corta al comenzar una sesión puede cargar Qwen, pero también expulsa Gemma. |
| 401 / conexión rechazada | Usar clave real, URL LAN exacta y comprobar conectividad Windows. No pegar secretos en diagnósticos ni desactivar SSH/TLS para sortear el fallo. |

### Timeout de Cline: procedimiento según versión

En Cline → Settings → API Configuration buscar **Request Timeout** para el proveedor
OpenAI Compatible; si existe, poner **1800 segundos** (o **1800000** solo si el campo
indica milisegundos), guardar y volver a abrir para verificar. Dimensionado para una
entrada de 16k y salida de 2048; no garantiza terminar tareas completas en ese plazo.
Revisar también cualquier proxy intermedio y diferenciar timeout API de timeout de
terminal/MCP. No cambiar configuración del servidor durante este procedimiento.

**Limitación verificada:** el componente OpenAI Compatible de `main` consultado y el
componente de v3.72.0 no muestran un control timeout. Sin conocer la versión instalada
no se puede prometer ese campo ni un setting universal. Si no aparece, buscar en
Settings de VS Code filtrando `@ext:saoudrizwan.claude-dev timeout`; usar solamente
una opción que especifique que afecta a solicitudes OpenAI Compatible. Si tampoco
existe, esa versión no ofrece un ajuste verificado: reducir prompts y valorar una
versión que lo documente; no editar archivos internos de la extensión a ciegas.
No usar `roo-cline.apiRequestTimeout` (Roo), timeout MCP/terminal ni
`API_TIMEOUT_MS` del router Claude Code: no solucionan el timeout de este proveedor.
Registrar el error exacto sin body/headers secretos y detener reintentos automáticos.
[Interfaz v3.72.0](https://github.com/cline/cline/blob/v3.72.0/webview-ui/src/components/settings/providers/OpenAICompatible.tsx).

## 7. Checklist del propietario: cinco pasos

1. **Conexión:** con Gemma cerrado, ejecutar los dos curl de Windows; comprobar alias
   y OK. Guardar fecha/estado HTTP sin clave ni headers de autorización.
2. **Configuración:** verificar Plan/Act con URL, alias, contexto32768, salida2048,
   temperatura0.6 y compacto si está disponible; anotar versión y timeout efectivo.
3. **Aislamiento:** abrir una copia/carpeta Git de prueba limpia en rama propia,
   sin SSH/agentes/secretos; lectura local autoaprobada, límite5 si existe,
   comandos manuales y edición local habilitada solo para esta prueba.
4. **Tarea mínima:** pedir «Crea suma.py con suma(a,b). Crea test_suma.py usando
   unittest para comprobar suma(2,3)=5 y suma(-1,1)=0. Ejecuta
   python -m unittest -v y resume el resultado. No instales paquetes ni uses red».
   Tener Python ya instalado; aprobar manualmente el comando. Verificar creación,
   llamada de herramientas real y dos pruebas PASS; si solo responde con código,
   la autonomía no está validada.
5. **Revisión:** comprobar diff, ausencia de cambios fuera del alcance, tokens y
   tiempos; pedir una corrección breve para observar segundo turno/caché.
   Registrar resultado recibido y detenerse ante bucles. No commit/push automático.

No se han ejecutado estos cinco pasos ni se declara aceptada la integración Windows.
Siguiente: el propietario configura Cline y aporta resultados no sensibles.

## Adaptación de la referencia

[Gist de CodingCanuck](https://gist.github.com/CodingCanuck/bd6f97ec6bb70f29a83b4b729fe5b6f4),
consultado el 14/11/2026; contiene recomendaciones históricas de agosto de 2025.
La parte Cline propone OpenAI Compatible, endpoint local terminado en /v1, clave
ficticia de LM Studio, identificador Coder y contexto manual muy grande; su ejemplo
de servidor usa muestreo0.7/0.8/20/0, penalización1.05, Jinja externo, GPU y262144.
Aquí se conservan proveedor y esquema URL; se sustituyen host, clave, modelo y
contexto por los desplegados. Un millón de tokens no cabe en el slot real.

La plantilla corregida de Coder responde a otro modelo/época; no sustituye la de
Qwen3.6. GPU99 no aplica al servidor CPU. La configuración Claude Code Router y su
timeout no son requisitos de Cline; no instalar ese intermediario. Las advertencias
antiguas sobre Ollama no demuestran un fallo actual de llama.cpp. Tampoco descargar
pesos Coder ni copiar sus límites/penalizaciones como si fueran ajustes de Qwen3.6.
La capacidad de agente depende de herramientas y ejecución efectiva, no solo de chat.

Ficha de parámetros y preservación de razonamiento:
[Qwen oficial](https://huggingface.co/Qwen/Qwen3.6-35B-A3B) y
[copia local consultada](../../services/ia-local/upstream/qwen-model-card.md).
Contrato del servidor: [documentación conservada](../../services/ia-local/upstream/llama-server.md).
Los flags específicos de otros motores no prueban compatibilidad con llama.cpp v1.0.0.
