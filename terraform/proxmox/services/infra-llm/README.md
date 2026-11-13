# infra-llm — CT 630

Debian 12 sin privilegios; 4 CPU, 22528 MiB RAM, 1024 MiB swap, raíz16GiB.
llama.cpp nativo CPU AVX2, sin Docker. Configuración canónica en `config/` y
`systemd/`; recetas compartidas en [ia-chat](../../scripts/ia-chat/README.md).
Terraform: `svc["infra-llm"]`, declaración `inventory/services/infra-llm.yml`.

DHCP observado192.168.1.67, MAC BC:24:11:6F:79:36. Reservar en router antes de
confiar en persistencia de IP. API `http://192.168.1.67:8080/v1`, clave600 en
`/etc/llama/api.key`. Modelos60GiB en `/models`, solo lectura y backup=0;
reconstrucción mediante URL/bytes/SHA del manifiesto versionado. La clave no va aGit.
Router `--models-max 1`, dos slots; Gemma8192tokens por slot conSWAcompleta, Qwen32768por slot;
descarga por inactividad3600s. El cambio deGemma sacrifica contexto para reutilizar
el historial dentro del margen deRAM. Selección r3: Gemma b2048/ub512 y Qwen b512/ub512;
generación3h/prompt4h, declarada en `config/performance-tuning.json`.
No consultar automáticamente `/metrics?model=...`: puede cargar un modelo.

Node Exporter nativo9100; CPU exclusivamente cgroup v2 textfile, collector.cpu
inactivo y RAM LXCFS. cAdvisor N/A explícito. Blackbox `/health` sin inferencia.
Informe, riesgos y evidencias: [ejecución](../../docs/roadmap/IA-CHAT-EXECUTION-2026-11-13.md).
