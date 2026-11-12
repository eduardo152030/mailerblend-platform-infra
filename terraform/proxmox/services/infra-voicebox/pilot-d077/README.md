# D-077 — piloto aislado con checkpoint y decoder independiente

> Antecedente histórico. La operación aprobada se rige por
> [D082](../release-d082/README.md). No ejecutar un despliegue de esta carpeta
> para sustituir automáticamente la versión aceptada.

> Recursos históricos sustituidos por D080: CT62715GiB/3CPU/2GiBswap,
> guardaCT14GiB, workerhard9GiB ystop8,2GiB. Ver
> [D080](../../../docs/roadmap/PHASE7-D080-QWEN-15G.md).

**Estado vigente:** el ensayo autorizado con texto nuevo ya se ejecutó una vez y
la voz fue aceptada. La integración está desplegada; usar
[operación productiva](../production-d077/README.md). No repetir este piloto por
la autorización ya consumida. El resto de esta página conserva el procedimiento
histórico de preparación y sus permisos de aquella etapa.


Preparación y validaciones sintéticas autorizadas. **La generación real todavía no
está autorizada.** Estado, resultados y siguiente ejecución propuestos en el
[informe D-077](../../../docs/roadmap/PHASE7-D077-CHECKPOINT-DECODER.md).

No es una integración con Voicebox: no cambia su imagen, Compose, API ni perfiles.
Todos los accesos remotos usan SSH estricto y exclusivamente `pct exec 627`.

## Componentes

- `checkpoint.py`: NPY int64 sin pickle, manifest y marcador de integridad; commit
  por renombrado atómico de directorio con fsync. Lectura acotada, checksum,
  permisos y dimensiones verificados. Nunca sobrescribe un checkpoint.
- `worker.py`: una etapa por proceso. A usa la API oficial hasta la llamada a
  `speech_tokenizer.decode`, donde persiste y finaliza sin decodificar. B carga
  solo el decoder, aplica chunking y reproduce el recorte oficial de referencia.
- `runtime.py`: versiones/fuentes fijadas, lectura de cabeceras safetensors y
  cargador de las 271 entradas `decoder.*`. No construye encoder ni Talker en B.
- `guards.py` y `supervise.py`: supervisión externa desde PVE, exclusión mutua,
  memoria/RSS/CPU/swap/PSI/OOM, deadlines, cancelación del cgroup propio, PID0 y
  cgroup vacío antes de liberar la etapa. Retira solo el contenedor recién creado.
- `prepare.py`: prepara revisiones privadas inmutables y jobs en CT627; no arranca
  workers. Una segunda aplicación idéntica no cambia la revisión ni los textos.
- `run.py`: transporta supervisor y guardas versionados a PVE mediante stdin.
  Sin `--execute` solo muestra el plan; Talker/decoder exigen además `--real`.
- `trial.py`: futura secuencia A→B, presupuesto combinado nominal900s, reserva de
  tiempo para arranque/cancelación; sin reintentos ni cambio automático a120.
- `validation.py`: layout real en meta y pruebas estructurales con marcadores y
  un parámetro ficticio. No carga pesos reales ni sintetiza audio.

## Datos privados

Job: `/srv/voicebox/pilot-d077/jobs/<job>/`, directorio700, UID999. Fuera de Git,
en disco persistente del CT; `/tmp/numba` es solo caché efímera. El checkpoint
contiene códigos de la referencia: debe protegerse como la grabación original.

```text
checkpoint/
  codes.npy          # [referencia+generación,16], int64
  manifest.json      # split, recorte, modelo, backend, parámetros, hashes
  COMMITTED.json     # hash del manifest; no basta por sí solo, se verifican todos
talker-release.json  # PID0/cgroup vacío y hash del manifest, escrito por supervisor
decoded-300.wav      # futuro resultado B, nunca producido durante preparación
```

No se borran `.partial`, locks interrumpidos, fuentes anteriores ni checkpoints.
Si solo existe un parcial, no se acepta como válido. Inspeccionar y preparar un job
nuevo; no sobrescribir ni repetir Talker automáticamente.

## Validación sin inferencia

Desde la raíz `terraform/proxmox`:

```bash
python3 -m unittest discover -s tests/voicebox -p 'test_d077.py' -v
python3 -m py_compile services/infra-voicebox/pilot-d077/*.py
python3 services/infra-voicebox/pilot-d077/prepare.py
```

Las validaciones remotas ya ejecutadas y sus identificadores están en el informe.
No repetir los mismos identificadores: los resultados y el checkpoint se conservan.

## Próximo ensayo propuesto — requiere autorización de generación real

Job `narracion01` ya preparado con el mismo texto de D076, sin modelos cargados:

```bash
# Idempotente: preparar/verificar únicamente, sin inferencia.
python3 services/infra-voicebox/pilot-d077/prepare.py \
  --job narracion01 --text-file services/infra-voicebox/pilot-d076/trading-text.txt
# Revisión del plan, no ejecuta ninguna etapa.
python3 services/infra-voicebox/pilot-d077/trial.py --job narracion01
```

Solo después de aprobación explícita, proponer:

```bash
python3 services/infra-voicebox/pilot-d077/trial.py --job narracion01 --execute
```

Guardar stdout en un archivo privado fuera de Git. Se propone un presupuesto
global900s; cada etapa descuenta tiempo transcurrido y reserva15s para arranque y
cancelación. La latencia de SSH/cancelación es un riesgo operativo que debe medirse,
no un plazo estricto extremo a extremo ya validado. A sale completamente antes de
B. Si queda menos de30s de presupuesto reservado, B no arranca y se conserva el
checkpoint. No hay retry automático.

Primero usar **300/contexto25**, con los mismos parámetros de generación de D076.
La comparación útil inicial es separación de procesos frente al proceso conjunto.
No usar120 a la vez para atribuir correctamente la mejora de memoria.

Si falla B y existe checkpoint válido, no repetir A. Tras nueva autorización del
decoder, el comando independiente sería, por ejemplo:

```bash
python3 services/infra-voicebox/pilot-d077/run.py decoder \
  --job narracion01 --attempt 02 --chunk 120 --timeout 180 --real --execute
```

Es una propuesta, **no se ejecutó**. Mantener contexto25 y el mismo checkpoint;
guardar resultados300 y120 por separado. No asumir equivalencia acústica sin WAV y
escucha. Si300 ya produjo WAV, no hace falta ejecutar120 para completar el piloto.

Si A fue interrumpido después del commit pero antes del release, se puede recuperar
sin cargar pesos mediante `run.py verify --job narracion01 --attempt 01 --execute`.
La etapa verifica el checkpoint desde otro proceso, comprueba exclusión y crea el
release solo después de PID0. Después, B exige release ligado al manifest actual.
Nunca validar a mano un checkpoint incompleto editando sus hashes.

Cancelar una ejecución interactiva con Ctrl-C activa la salida del supervisor y
la cancelación del cgroup propio; la prueba con padre e hijo está documentada. Una
caída completa del host o Docker requiere revisar el estado antes de reanudar.

La memoria de page cache puede persistir aunque termine A; no se ejecuta drop_caches,
reinicios ni limpieza de otros procesos. Recursos: CT3CPU/10GiB/2GiBswap;
worker3CPU/hard9GiB/sin swap; guardas worker8,2GiB,CT9,5GiB, deltaSwap128MiB,
swap absoluto1920MiB, PSIlocal5%/10s. Los WAV solo se validarán cuando existan; no se
modifica duración, tempo ni pipeline en esta preparación.
