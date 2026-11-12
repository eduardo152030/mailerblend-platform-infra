# Propuesta D064 — prueba Qwen CPU BF16, no aplicada

El propietario exige revisar diagnóstico y recomendación antes de más cambios
productivos. No aplicar este parche ni descargar/cargar modelos desde esta propuesta
sin esa revisión. La aplicación activa conserva la imagen y el código originales.

cpu-bf16.patch se genera contra Voicebox8af7efe y limita las rutas CPU Base y
CustomVoice a0.6B. Cambia dtype aBF16 y atenciónSDPA, admitida por las clases del
paquete instalado. No modifica Kokoro. Compilación sintáctica del candidato PASS;
no constituye una prueba de carga o generación. low_cpu_mem_usage se elimina porque
Transformers4.57.3 descarta ese argumento: no se atribuye ahorro a ese cambio.

experiment.json separa descarga, carga, piloto y narración aproximadamente60s.
El cálculo de pesos BF16 hace plausible investigar ambos0.6B dentro de4GiB;
RSS real, transitorios, KV y activaciones necesitan medición. El i5-6500 AVX2 no
tiene aceleración nativaAVX512_BF16/AMX: el rendimiento puede ser insuficiente.

Antes de ejecutar: backup nuevo y restauración aislada, imagen anterior y archivo
exportado preservados, plan solo627 y revisión del posible reboot al pasar3→4GiB.
Crear imagen candidata con base verificada porID, aplicar parche reproducible y
nuevo lock, conservar imagen aprobada. No instalar paquetes de cuantización a ciegas.

Descargar un solo modelo por vez al caché persistente mediante snapshot_download,
revisión/hash fijados y max_workers=1, sin importar Qwen ni llamar from_pretrained.
Kokoro permanece en disco. Para cargar Qwen, liberar Kokoro de RAM por su API y
medir RSS real; no asumir liberación completa del allocator. Si no queda presupuesto,
reinicio controlado solo de Voicebox para arrancar sin modelos, con interrupción
breve documentada. No mantener dos modelos residentes durante este primer ensayo.

Medir cada etapa por separado: VmRSS/RssAnon/RssFile y VmHWM del proceso, memoria y
pico del cgroup, memory.stat/pressure, swap, eventosOOM, CPU y duración. Muestreo200ms,
con parada suave antes de3,5GiB y ante aumento de swap>64MiB, anomalía deotrosCT,
operador no soportado o audio no finito. No intentar una carga cuyo presupuesto
previo ya exceda el límite. El techo absoluto4GiB permanece invariable.

Primero CustomVoice0.6B con preset propio Ryan ylanguagees; no reutilizar el perfil
Kokoro. Piloto10s y luego narración aproximadamente60s, secuencial ychunks200caracteres.
Después liberar su modelo de RAM y evaluar Base0.6B con perfilcloned nuevo yreferencia
Alex sintetizada por nuestroKokoro, conservando el perfil original. Base necesita
referencia; CustomVoice usa speakers propios. Su0.6B ignora instruct en qwen-tts0.1.1:
no prometer acento peninsular porprompt. Registrar texto, parámetros, IDs, WAV,
duración real, tiempo yRTF, errores ymemoria. Máximo900s para ensayo de60s; si el
piloto falla o excede presupuesto/tiempo, no avanzar alensayo largo.

Rollback a imagen fijada y3GiB según el plan revisado, conservar caches ydatos,
verificar generación Alex/Kokoro, salud y18/18/19. No restaurar SQLite encima de
cambios nuevos del propietario sin reconciliar. Eliminar los tres perfiles nuevos
rechazados solo tras exportar muestras ybackup; no eliminar el originalD063 ni Alex.
Hasta revisión previa permanecen conservados, sin presentarlos como aceptados.

La cancelación HTTP no garantiza interrumpir un kernel en un hilo: el supervisor
debe poder detener solo el contenedor candidato y restaurar Kokoro si se alcanza
un límite. No depender únicamente de /generate/{id}/cancel para evitarOOM.
