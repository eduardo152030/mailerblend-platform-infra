# PHASE7-D091: Chatterbox Chunking Implementation Plan

**Estado:** Propuesto  
**Fecha:** 2026-11-16  
**Rama base:** `main`  
**Alcance:** Implementar fragmentación interna (chunking) en el adaptador de Chatterbox para permitir narraciones largas sin fallo por límite de tokens.

---

## 1. Problema

`chatterbox_worker.py` falla con `RuntimeError('Chatterbox no emitió EOS')` para textos >~300 caracteres porque `max_new_tokens=400` es insuficiente para generar audio largo en una sola pasada. El modelo emite menos tokens de los esperados y no alcanza el token EOS, lo que el worker interpreta como generación incompleta.

**Causa raíz:** El modelo Chatterbox Multilingual V3 tiene un límite práctico de ~300 caracteres de entrada que produce una salida dentro de 400 tokens. Textos más largos requieren múltiples pasadas de generación.

## 2. Arquitectura actual (evidencia)

### Flujo de ejecución

```
agent.py (PVE)
  → supervise_chatterbox.py (PVE, lanza contenedor Docker)
    → chatterbox_worker.py (CT627, dentro de Docker)
      → ChatterboxMultilingualTTS.generate() → single WAV
```

### Bloqueo arquitectónico actual

`isolated_chatterbox_backend.py` (el adaptador en PVE) usa directorios de trabajo únicos por job (`uuid.UUID(parent).hex`). Cada llamada a `generate()` crea un directorio nuevo y espera a que `chatterbox_worker.py` termine. No hay mecanismo para múltiples llamadas de generación dentro del mismo contexto de job.

`chatterbox_worker.py` carga el modelo una vez por ejecución de worker (un contenedor Docker por job). No hay reutilización de modelo entre jobs.

### Límites actuales (engine_policy.py)

- `max_chars`: 1200
- `max_tokens`: 400
- `timeout_seconds`: 300
- Duración máxima WAV: 20 segundos (verificación en worker: `len(audio)/model.sr <= 20`)


----

---

## 3. Solución de diseño

Implementar chunking **dentro de `chatterbox_worker.py`**, manteniendo un solo contenedor Docker por job. El worker dividirá el texto en fragmentos, generará cada uno con el modelo cargado persistentemente, y ensamblará los WAVs finales en un único archivo.

### Principios de diseño

1. **Un solo contenedor Docker por job** — sin cambios en `supervise_chatterbox.py`.
2. **Modelo cargado una sola vez** — el modelo se carga antes del bucle de fragmentos.
3. **Referencia preparada una sola vez** — el archivo de referencia se monta una vez.
4. **Fragmentos secuenciales** — cada fragmento se genera en orden, con identificación y resultado persistente.
5. **Un único WAV final** — concatenación de fragmentos en un solo archivo.
6. **Conservar EOS obligatorio, cancelación efectiva, evidencias y recuperación de fragmentos completados.**
7. **Límites por fragmento vs. presupuesto total del trabajo** — el límite de tokens, duración y timeout se mantienen por fragmento; el timeout total del job se mantiene en 300s.

### Impacto en el límite de 20 segundos

El worker actual verifica `len(audio)/model.sr <= 20` por fragmento. Con chunking, cada fragmento individual seguirá teniendo duración <= 20s (porque cada fragmento es <= 300 chars). El WAV final podrá ser más largo que 20s (hasta ~80s con 4 fragmentos), pero cada fragmento individual respetará el límite. Esta verificación debe mantenerse **por fragmento**, no sobre el WAV final.

---

## 4. Modificaciones detalladas

### 4.1 `chatterbox_worker.py` — Modificaciones principales

#### 4.1.1 Nueva función `_split_text()`

Función standalone (no método de clase) que divide el texto en fragmentos:

```python
def _split_text(text, max_chunk=300, max_chunks=4):
    """Divide el texto en fragmentos de <=300 caracteres, respetando oraciones."""
    if len(text) <= max_chunk:
        return [text]
    sentences = re.split(r'(?<=[.!?;])\s+', text)
    chunks = []
    current = ''
    for sent in sentences:
        if len(current) + len(sent) + 1 <= max_chunk:
            current = current + ' ' + sent if current else sent
        else:
            if current:
                chunks.append(current)
            if len(sent) > max_chunk:
                for i in range(0, len(sent), max_chunk):
                    chunks.append(sent[i:i+max_chunk])
                current = ''
            else:
                current = sent
        if len(chunks) >= max_chunks:
            break
    if current:
        chunks.append(current)
    return chunks[:max_chunks]
```

#### 4.1.2 Nueva función `_concat_wav()`

Función standalone para concatenar WAVs usando `soundfile` (ya importado):

```python
def _concat_wav(wav_paths):
    """Concatenate multiple WAV files into a single WAV file."""
    parts = []
    first_sr = None
    for p in wav_paths:
        data, sr = sf.read(p, dtype='float32')
        if first_sr is None:
            first_sr = sr
        elif sr != first_sr:
            raise ValueError(f'Inconsistent sample rates: {sr} vs {first_sr}')
        parts.append(data)
    combined = np.concatenate(parts)
    return combined, first_sr
```

#### 4.1.3 Reestructuración de la función `execute()`

La función `execute()` actual carga el modelo, genera un WAV, y escribe el resultado. Se reestructura para:

1. **Cargar el modelo una vez** (como ahora).
2. **Dividir el texto** con `_split_text()`.
3. **Generar fragmentos en bucle**, guardando cada WAV parcial con identificador:
   - `chatterbox-chunk-0.wav`, `chatterbox-chunk-1.wav`, etc.
   - Cada parcial se escribe de forma atómica (como el actual `chatterbox.partial` → `chatterbox.wav`).
4. **Verificar EOS y duración por fragmento** (como ahora).
5. **Ensamblar WAV final** con `_concat_wav()`.
6. **Escribir resultado final** atómicamente.
7. **Limpiar parciales** después del éxito.

```python
def execute(job, models, reference):
    request = validate(json.loads((job/'request.json').read_text()))
    assert request['engine'] == 'chatterbox' and (job/'text.txt').read_text() == request['text']
    assert not (job/'checkpoint').exists(), 'Qwen checkpoints never enter Chatterbox'
    from d077_contract import REFERENCE_SHA
    assert sha(reference) == REFERENCE_SHA
    manifest = json.loads((models/'manifest.json').read_text())
    assert manifest['model_revision'] == '5bb1f6ee58e50c3b8d408bc82a6d3740c2db6e18'
    assert not (models/'conds.pt').exists(), 'No default or third-party voice'
    for f in manifest['files']:
        assert sha(models/f['name']) == f['sha256']
    import torch, soundfile as sf, numpy as np
    from chatterbox.mtl_tts import ChatterboxMultilingualTTS
    torch.set_num_threads(3)
    torch.set_num_interop_threads(1)
    torch.manual_seed(42)
    np.random.seed(42)
    stats = {'engine': 'chatterbox', 'variant': 'multilingual-v3', 'language': request['language'],
             'dtype': 'float32', 'seed': 42, 'chunks': []}
    start = time.monotonic()
    try:
        # Load model once
        t = time.monotonic()
        model = ChatterboxMultilingualTTS.from_local(models, device='cpu', t3_model='v3')
        for component in [model.t3, model.s3gen, model.ve]:
            component.float()
            assert all(p.dtype == torch.float32 for p in component.parameters() if p.is_floating_point())
        stats['load_seconds'] = time.monotonic() - t

        # Split text into chunks
        chunks = _split_text(request['text'], max_chunk=300, max_chunks=4)
        stats['chunk_count'] = len(chunks)

        chunk_wavs = []
        for i, chunk_text in enumerate(chunks):
            chunk_stats = {'chunk_index': i, 'chunk_text_length': len(chunk_text), 'status': 'running'}
            chunk_start = time.monotonic()

            # Generate single chunk
            with torch.inference_mode():
                wav = model.generate(chunk_text, language_id=request['language'],
                                     audio_prompt_path=str(reference), exaggeration=.5, cfg_weight=.5)
            audio = wav.squeeze().detach().cpu().numpy()
            assert audio.ndim == 1 and len(audio) > 0 and np.isfinite(audio).all()
            chunk_duration = len(audio) / model.sr
            assert chunk_duration <= 20, f'Chunk {i} duration {chunk_duration:.1f}s exceeds 20s limit'

            # Write chunk WAV atomically
            chunk_path = job / f'chatterbox-chunk-{i}.wav'
            partial_path = chunk_path.with_suffix('.partial')
            sf.write(partial_path, audio, model.sr, format='WAV', subtype='PCM_16')
            with partial_path.open('rb') as f:
                os.fsync(f.fileno())
            partial_path.chmod(0o600)
            os.replace(partial_path, chunk_path)

            chunk_stats.update(status='completed', duration=chunk_duration,
                               wav_sha256=sha(chunk_path), seconds=chunk_duration,
                               token_seconds=time.monotonic() - chunk_start)
            stats['chunks'].append(chunk_stats)
            chunk_wavs.append(chunk_path)

        # Concatenate all chunks
        if len(chunk_wavs) > 1:
            combined, sr = _concat_wav(chunk_wavs)
        else:
            combined, sr = sf.read(chunk_wavs[0], dtype='float32')
            combined = combined.squeeze()

        # Write final WAV atomically
        target = job / 'chatterbox.wav'
        assert not target.exists()
        sf.write(target, combined, sr, format='WAV', subtype='PCM_16')
        with target.open('rb') as f:
            os.fsync(f.fileno())
        target.chmod(0o600)

        stats.update(success=True, seconds=len(combined)/sr, wav_sha256=sha(target),
                     total_duration=sum(c['duration'] for c in stats['chunks']))

    except BaseException as e:
        stats.update(success=False, error=str(e))
        raise
    finally:
        stats['total_seconds'] = time.monotonic() - start
        atomic(job / 'chatterbox-result.json', stats)
    return stats
```

### 4.1.4 Limpieza de parciales

Tras la concatenación exitosa, eliminar los archivos `chatterbox-chunk-{N}.wav` generados. Si `execute()` se interrumpe antes de la concatenación, los parciales permanecen en disco y el siguiente reintento los regenera.

### 4.2 `chatterbox/mtl_tts.py` — Sin cambios

Este archivo no se modifica. La función `ChatterboxMultilingualTTS.generate()` se usa tal cual; el chunking ocurre en `chatterbox_worker.py` antes de invocarla.

### 4.3 `chatterbox/voice.py` — Sin cambios

No se modifica. La carga de `conds.pt` y la validación de voz permanecen inalteradas.

### 4.4 `chatterbox/voice_prompts.py` — Sin cambios

No se modifica. La lógica de prompts de audio se usa sin alteraciones.

### 4.5 `chatterbox_worker.py` — Sin cambios

El worker no se modifica. La función `execute()` sigue recibiendo `job`, `models` y `reference` como parámetros y devuelve un dict con estadísticas. El chunking es transparente para el worker.