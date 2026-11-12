# Fase 7.4 — diagnóstico Qwen optimizado — D065

Estado: **DONE diagnóstico y preparación local; prueba productiva NO EJECUTADA**.
2026-11-10 (Europe/Madrid). El propietario exige diagnóstico/recomendación antes de
cambios adicionales. No se han aplicado parcheBF16, nuevos modelosQwen, ampliación
4GiB ni borrado deperfiles tras esa instrucción. Servicio actual:3GiB, Kokoro operativo.
Alex aceptado como voz por el propietario; otros3 candidatos descartados ypendientes
de retirada con muestras/backup preservados. No se inventan edades ni una certificación
peninsular adicional.

## Conclusión y recomendación

**No descartar Qwen0.6B por el cálculoFP32.** Ese cálculo describe el backend activo,
pero una varianteBF16 puede reducir los pesos a aproximadamente2GiB. Recomiendo una
prueba controlada CustomVoice0.6B primero yBase0.6B después, secuencial, dentro de4GiB,
con una imagen candidata yrollback, solo después de revisar esta propuesta.
Es una vía técnicamente plausible, **no viabilidad demostrada**: carga real, pico de
inferencia ytiempo para1minuto todavía no medidos. El rendimiento de estei5AVX2 puede
ser limitante incluso si los pesos caben. No hay prueba de60s ni promesa derealtime.

## Descarga, carga e inferencia son etapas distintas

1. **Descarga:** snapshot_download/hf_hub_download escribe archivos alvolumen
   /srv/voicebox/huggingface sin crearQwen3TTSModel ni tensores delmodelo. Revisiones
   yhashes fijados, max_workers=1, unmodelo cada vez. Base requiere aproximadamente
   2,512GB dedisco yCustomVoice2,494GB, incluido sucodec. ~30GB dedisco libre observados.
   No se habilita descarga global desde laaplicaciónHFoffline; se usaría unhelper
   independiente conred solo para esadescarga. Ningún tensorQwen completo descargado.
2. **Carga:** from_pretrained crea/abre los tensores con eldtype elegido. Elfork
   8af7efe fuerzaCPUfloat32 enpytorch_backend.py yqwen_custom_voice_backend.py.
   qwen-tts0.1.1 reenvía kwargs aTransformers y al speech_tokenizer. Admite solicitar
   BF16/FP16, pero elfork no ofrece un selectorCPU por variable/API: hace falta un
   cambio mínimo reproducible en imagen candidata, no solo cambiarperfil.
3. **Inferencia:** añade KVcache, activaciones, buffers ydecodificación. No se mide
   a partir del tamaño delarchivo ni del tiempo de unoperador pequeño.

Documentación primaria: [descargaHF](https://huggingface.co/docs/huggingface_hub/guides/download),
[Transformers4.57.3](https://huggingface.co/docs/transformers/v4.57.3/en/main_classes/model),
[códigoQwen](https://github.com/QwenLM/Qwen3-TTS).
Las conclusiones de versión se contrastaron además con los archivos instalados.

## Presupuesto, todavía no una medición delmodelo

Cabeceras safetensors: CustomVoice contiene905788672 parámetros en elarchivo principal;
Base914643008; codec170557441. Se contaron tensores, no se cargaron modelos.

| Variante0.6B | Pesos todosFP32 | Pesos todosBF16 | TalkerBF16 ycodecFP32 |
|---|---|---|---|
| CustomVoice0.6B | 4.010GiB | 2.005GiB | 2.323GiB |
| Base0.6B | 4.043GiB | 2.021GiB | 2.339GiB |

A estos mínimos hay que añadir runtime/SO/exporters, buffers de carga e inferencia.
Como **presupuesto de ensayo**, no medición, reservar0,7–1,5GiB adicionales puede
situar el totalBF16 alrededor de2,7–3,6GiB; la carga no se intentará si elbaseline real
no deja margen. UncodecFP32 puede acercar el total al límite: se reevalúa antes de
probarlo, no se fuerza como fallback automático.

El talker tiene28capas,8KVheads yhead_dim128. KVBF16 para1000–1500posiciones consume
aproximadamente109–164MiB (fórmula2×capas×heads×dim×tokens×bytes), no el pico total.
El número real detokens y el caché delpredictor se deben medir. La narración60s da
aproximadamente750frames a12,5Hz. Elcodec instalado ya usa chunked_decode300frames
(~24s) con25frames decontexto. Elfork ofrece max_chunk_chars yprocesamiento secuencial;
usar200 reduce la longitud de cada inferencia sin duplicar modelos. ElWAV final de
60s solo ocupa unos2,9MB enPCM16; los tensores intermedios son elriesgo relevante.

**Corrección importante:** Transformers4.57.3 hace kwargs.pop(low_cpu_mem_usage)
yusa inicializaciónmeta. ElFalse que pasa elfork no demuestra doscopias delmodelo;
cambiarlo aTrue **no es una optimización efectiva en esta instalación**.
Sigue siendo relevante seleccionar eldtype correcto al cargar, sin convertir un
modeloFP32 entero después de ocupar laRAM.

## Precisión y cuantización

- Torch2.8.0+cpu/i5AVX2 pasó linear,conv1d,conv_transpose1d,SDPA yRMSNorm conBF16 yFP16
  en una prueba sintética pequeña. **No se cargóQwen**. RSSpico deeseproceso diagnóstico
  ~218MiB; no es elRSS deQwen ni benchmark de narración.
- BF16 conserva rango dinámicoFP32; es la primera candidata. No hayAVX512_BF16/AMX:
  no se puede extrapolar velocidad deXeon/GPU. [ReferenciaPyTorch](https://pytorch.org/blog/empowering-pytorch-on-intel-xeon-scalable-processors-with-bfloat16/).
- FP16 también pasó operaciones pequeñas, pero tiene menor rango y no está validado
  con todo elmodelo/codec. No ofrece menos bytes queBF16 yno es la primera opción.
- Torch dispone de cuantizaciónCPU, pero no existe una rutaQwen cuantizada integrada
  en estefork. torchao,bitsandbytes yoptimum-quanto no están instalados. Unquantize_dynamic
  genérico después de cargarFP32 mantendría elriesgo de pico previo. Haría falta evaluar
  carga cuantizada ycompatibilidad delmodelo, no asumir que cualquierGGUF/AWQ sirve.
  [PyTorch2.8](https://docs.pytorch.org/docs/2.8/quantization.html). No se instaló nada.

Elparche local depropuesta cambia únicamente las dos rutasQwenCPU aBF16/SDPA y
rechaza tamaños distintos de0.6B. No se aplicó alcódigo desplegado ni se construyó
otraimagen. Elaudio decoder instalado convierte salida aFP32 antes de numpy, evitando
atribuirle sin evidencia un fallo general por salidaBF16.

## Kokoro, perfiles y60segundos

Kokoro puede permanecer **descargado en disco** mientras Qwen estáactivo. Sus archivos,
perfiles y audios no necesitan eliminarse. No mantener ambos modelos residentes en el
primerensayo: POST /models/kokoro/unload libera referencias, pero elallocatorCPU puede
conservarRSS. Medirlo; si no baja lo suficiente, reinicio controlado soloVoicebox para
arrancar sin modelos. No ejecutar descarga/carga dentro delAPI activo sin presupuesto.

CustomVoice requiere perfilpreset propio, por ejemploRyan, engineqwen_custom_voice,
model_size0.6B ylanguagees. Base requiere perfilcloned nuevo, engineqwen yreferencia;
se propone usar una muestraAlex sintética propia, contranscripción conocida, sin
editar/reutilizar elpresetKokoro comosi fueraQwen.

La versión instalada borra instruct enCustomVoice0.6B. Aunque elmodelcard genérico
habla decontrol expresivo, elcódigo real manda: no prometer acentoEspaña porprompt.
Los9speakers nativos sonchino/inglés/japonés/coreano; español está admitido pero
acento/calidad requieren escucha. [Modelcard](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice).

## Prueba propuesta, pendiente de revisión

[Plan concreto](../../services/infra-voicebox/proposals/d064/experiment.json),
[procedimiento yrollback](../../services/infra-voicebox/proposals/d064/README.md),
[parche revisable](../../services/infra-voicebox/proposals/d064/cpu-bf16.patch).

Backup nuevo/restauración ybaseline de18LXC, imagenCPU actual preservada, plan solo627
3→4GiB con reboot documentado. Descargar primeroCustomVoice0.6B sin cargarlo; medir
descarga aparte. CargarloBF16 solo si elbaseline y estimación dejan margen; medir
VmRSS/RssAnon/RssFile/VmHWM, cgroupcurrent/peak/stat/pressure,swap yOOMcada200ms.
Primero piloto~10s (timeout120s tras carga), luego texto ajustado a audio~60s,
secuencial/chunks200, máximo900s deejecución delensayo. Son límites propuestos,
no tiempos de generación medidos ni unSLA aceptado. RTF=tiempogeneración/duraciónreal.

Parada suave antes de3,5GiB y ante crecimiento deswap>64MiB, anomalía deotroCT,
operador no soportado/audio nofinito o pérdida demargen. UncancelHTTP no interrumpe
necesariamente C++ enunhilo: supervisor debe poder detener solo elcandidato yrestaurar
Kokoro. No intentar una carga cuyo presupuesto yaexceda4GiB, ni usarOOMcomoprueba.
Después liberarCustomVoice y repetir porseparado conBase0.6B. Verificar Alex/Kokoro,
persistencia, API,18/18/19 ysegundaaplicación. Si no esseguro, abortar/restaurar, sin
subirpor encima4GiB. No modificar reglasgenerales, pipeline ni otrosLXC.

La retirada autorizada deDora/Santa/Emma queda preparada, sin ejecutar después del
controlprevio solicitado. Exportar susmuestras ybackupantesdeborrar; elDELETEdeperfil
puede afectar generaciones relacionadas. Alex yoriginalD063 quedan protegidos.

[Diagnóstico estructurado](evidence/2026-11-10-d065-diagnosis.json),
[operadoresCPU, no modelos](evidence/2026-11-10-d064-cpu-dtype-smoke.json).
Siguiente: revisión delpropietario antes de cualquier cambio productivo adicional.
