# Fase 7.4 — catálogo español y Qwen — D064

Estado: **IN PROGRESS**. Catálogo implementado; Alex aceptado por el propietario.
Retirada de otras tres candidatas pendiente del control previo solicitado después.
La investigación optimizada Qwen continúa en [D065](PHASE7-D065-QWEN-OPTIMIZATION.md).
D063 conserva su cierre histórico del primer provisioning.

## Resultado de voces

Cuatro perfiles nuevos, sin editar ni eliminar el original D063. Texto idéntico:

«Hola, bienvenidos a nuestro canal. Hoy vamos a descubrir cómo funciona esta tecnología
y por qué puede cambiar nuestra forma de trabajar. Vamos a comenzar.»

Todas las muestras son Kokoro82M, WAVPCM16 mono24kHz, seed42, sin efectos ni LLM.
Los tiempos son observados por polling, no benchmarks de precisión subsegundo.
RAM es máximo **muestreado del CT** (no RSS exclusivo del modelo ni pico continuo).

| Voz | Género según catálogo | Preset | Generación | Audio | RAM muestreada | Revisión / muestra |
|---|---|---|---|---|---|---|
| Dora | Femenina (metadato) | ef_dora | 8.47s | 8.90s | 1.585GiB | [Descartada; retirada pendiente de revisión previa](http://192.168.1.127:17493/audio/604dd48d-93f7-4ea8-8447-404a44908edf) |
| Alex | Masculina (metadato) | em_alex | 6.40s | 8.88s | 1.617GiB | [Aceptable para el propietario](http://192.168.1.127:17493/audio/4fbf2a24-e533-4f5e-ba04-b79fd4b91cc4) |
| Santa | Masculina (metadato) | em_santa | 5.73s | 9.10s | 1.596GiB | [Descartada; retirada pendiente de revisión previa](http://192.168.1.127:17493/audio/c98308bf-db33-4008-b14f-79ee5477c176) |
| Emma | Femenina (metadato) | bf_emma | 7.96s | 9.60s | 1.693GiB | [Descartada; retirada pendiente de revisión previa](http://192.168.1.127:17493/audio/ee2fe00b-62c7-4cf3-a4e5-e74393e96736) |

Dora/Alex/Santa son los tres presets etiquetadoses porKokoro. Emma es un preset
británico real probado experimentalmente conlanguagees: no se anunció como nativo
peninsular. El propietario aceptaAlex y solicita retirar las otras3. No asignó edades;
no se etiquetan25–35/35–45 sin evidencia. Tampoco se certifican por separado acento
peninsular o estilos profesional/conversacional/voz enoff. Kokoro ignora instruct;
no se simulan estilos creando nombres distintos para la misma voz.

La limpieza **no se ha ejecutado** tras la nueva instrucción de presentar diagnóstico
antes de más cambios productivos. Se conservan audios, backups y perfiloriginal.
Catálogo declarativo: services/infra-voicebox/voices-catalog.yml; reconciliación por
scripts/voicebox-voices.py. Segunda aplicación:0perfiles/0generaciones nuevas,
IDs y hashes preservados. La retirada deberá excluir explícitamente el originalD063.

## Incidencia Qwen y presupuesto inicial

HTTP400 reproducido antes de cargar modelo: presetKokoro no admiteengineqwen.
El perfil original sigue íntegro. QwenBase requiere perfilcloned con referencia;
CustomVoice requiere presetpropio qwen_custom_voice. Ryan/Vivian/Serena/Aiden
son presets reales: su compatibilidad se comprobó estáticamente, sin publicarlos
como funcionales ni cargar modelos inexistentes.

La instalación tiene qwen-tts0.1.1, torch2.8.0+cpu, transformers4.57.3,
accelerate1.12.0. Ambos backendsCPU fuerzanFP32. Pesos0.6BCustom+codec requieren
4,0097GiB enFP32, y1.7BBase7,8203GiB, antes de runtime. Esto bloquea **esa rutaFP32**,
pero no demuestra inviabilidad deBF16/FP16/cuanti­zación. El propietario pidió reabrir
el análisis optimizado; [D065](PHASE7-D065-QWEN-OPTIMIZATION.md) corrige esa distinción.
Solo se leyeron cabeceras/configuraciones; no se descargaron tensoresQwen completos.

## Recursos y comprobaciones reales

Cuatro muestras a2GiB completaron sinOOM, pero dejaron18,43%RAMdisponible y
HostMemoryPressurePENDING. Bajo el permiso3/4GiB se amplió **solo627 a3072MiB**.
3CPU,512MiBswap,50GiB y límitesCompose1600m/2000m permanecen. Plan real: solo
memory/Notes627,0destrucciones/reemplazos. Elprovider reinició627; perfiles ycuatro
hashes deaudios sobrevivieron. Una generación Dora posterior a3GiB tardó14,74s,
duró8,9s y produjo el mismohash conseed42. No se amplió a4GiB.

Backup previo alajuste yrestoreaisladoPASS:34archivos, seis enlacesHF confinados,
SQLiteok y8audios completados. Originales/backups/modelos preservados. Rollback:
imagenCPU fijadaD063 yplan exclusivo627, sin restaurarSQLite sobre datos nuevos
sin reconciliar. La RAM2GiB previa no ofrecía margen para cuatro voces; el punto
operativo de retorno actual es3GiB. No modificar otrosCT ni umbralesF5.

Después:18Node/18cAdvisor/19BlackboxUP,180s/7muestrasPASS, sinalertas alobservar,
CPUcgroup/RAMLXCFS3072MiB verificados yGrafana627 comprobado en navegador.
17configuracionesPVE ajenas idénticas;627soloRAM/Notes. OOM/oom_kill=0 antes ydespués
del cambio. Los contadoresmax/reclaim pueden incrementarse porfilecache: no se
confunden conOOM ni conRSS delmodelo. Segunda aplicaciónTerraform0/0/0.

## Evidencias, cambios y límites

[Samples](evidence/2026-11-10-d064-samples.json),
[revisión](evidence/2026-11-10-d064-user-review.json),
[backup/restore](evidence/2026-11-10-d064-restore.json),
[preservación](evidence/2026-11-10-d064-preservation.json),
[idempotencia](evidence/2026-11-10-d064-idempotence.json),
[observación](evidence/2026-11-10-d064-observation.json),
[navegador](evidence/2026-11-10-d064-browser.json).
Cambios delalcance: catálogoYAML, model-lock (solo523420bytes devozEmma adicional),
scriptvoicebox-voices ypresupuestoCPU; parámetros opcionales deobservador/navegador;
inventario627/RAM3072/Notes ydocumentaciónroadmap. Código deaplicación eimagen no
modificados. No datos/profiles originales borrados, otrosLXC, reglasPrometheus,
pipeline, publicaciónWAN, commit ni push. No se generó aún narraciónQwen deunminuto.

Siguiente: revisión deD065 antes de aplicar pruebaBF16 o limpieza deperfiles.
