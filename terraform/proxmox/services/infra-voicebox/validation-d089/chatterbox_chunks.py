"""Bounded internal chunks; no ML imports. Completed WAVs survive later failure."""
import hashlib
import json
import os
import time
from pathlib import Path


def split_text(text, max_chars=150, max_chunks=8):
    if not isinstance(text, str) or not text.strip():
        raise ValueError('Texto vacío')
    if type(max_chars) is not int or type(max_chunks) is not int or min(max_chars, max_chunks) < 1:
        raise ValueError('Límites de fragmentación inválidos')
    if len(text) > max_chars * max_chunks:
        raise ValueError('Texto excede la capacidad de fragmentación')
    chunks = []
    while text:
        if len(text) <= max_chars:
            chunks.append(text)
            break
        lower = max(1, len(text) - max_chars * (max_chunks - len(chunks) - 1))
        # Prefer natural boundaries, but reserve capacity for ALL remaining text.
        preferred = max(lower, max_chars // 2)
        ends = [i for i in range(preferred, max_chars + 1)
                if text[i - 1] in '.!?;\n']
        if not ends:
            ends = [i for i in range(preferred, max_chars + 1) if text[i - 1].isspace()]
        cut = ends[-1] if ends else max_chars
        chunks.append(text[:cut])
        text = text[cut:]
    return chunks


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def atomic_json(path, value):
    part = path.with_suffix('.partial')
    part.write_text(json.dumps(value, sort_keys=True))
    part.chmod(0o600)
    with part.open('rb') as f:
        os.fsync(f.fileno())
    os.replace(part, path)
    fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def write_wav(path, audio, sample_rate):
    import numpy as np
    import soundfile as sf
    audio = np.asarray(audio)
    if sample_rate != 24000 or audio.ndim != 1 or not len(audio) or not np.isfinite(audio).all():
        raise ValueError('WAV inválido: frecuencia, canales o muestras')
    if path.exists():
        raise FileExistsError('No sobrescribir WAV existente')
    part = path.with_suffix('.partial')
    sf.write(part, audio, sample_rate, format='WAV', subtype='PCM_16')
    info = sf.info(part)
    if info.frames != len(audio) or info.channels != 1 or info.samplerate != sample_rate:
        raise ValueError('WAV incompleto')
    part.chmod(0o600)
    with part.open('rb') as f:
        os.fsync(f.fileno())
    os.replace(part, path)
    fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)
    return {'frames': info.frames, 'sample_rate': sample_rate, 'sha256': digest(path)}


def generate_chunks(job, text, generate, policy, metrics, deadline, clock=time.monotonic, identity=None):
    """One model/reference owned by caller. Existing journals require explicit recovery.

    Never retries a chunk. External cgroup watchdog still owns hard cancellation.
    """
    import numpy as np
    import soundfile as sf
    chunks = split_text(text, policy['max_chunk_chars'], policy['max_chunks'])
    directory = job / 'chatterbox-chunks'
    directory.mkdir(mode=0o700)  # Refuse implicit retry, even after a failed attempt.
    journal = {'version': 1, 'text_sha256': hashlib.sha256(text.encode()).hexdigest(),
               'state': 'running', 'identity': identity or {}, 'policy': dict(policy), 'chunks': []}
    manifest = directory / 'manifest.json'
    atomic_json(manifest, journal)

    def guard():
        if (job / 'cancel.flag').exists():
            raise RuntimeError('Generación cancelada')
        if clock() >= deadline:
            raise TimeoutError('Presupuesto global de Chatterbox agotado')

    try:
        for index, chunk in enumerate(chunks):
            guard()
            entry = {'index': index, 'chars': len(chunk),
                     'text_sha256': hashlib.sha256(chunk.encode()).hexdigest(), 'state': 'running'}
            journal['chunks'].append(entry)
            atomic_json(manifest, journal)
            metrics.clear()
            audio, sample_rate = generate(chunk)
            guard()
            if metrics.get('eos') is not True or not 0 < metrics.get('tokens', 0) <= policy['max_tokens']:
                raise RuntimeError('Fragmento sin EOS válido; no publicar WAV')
            if len(audio) / sample_rate > policy['max_chunk_seconds']:
                raise ValueError('Duración de fragmento excedida')
            path = directory / f'{index:03d}.wav'
            entry.update(write_wav(path, audio, sample_rate))
            entry.update(metrics)
            entry.update(state='complete', file=path.name)
            atomic_json(manifest, journal)
        guard()
        arrays = []
        for index, entry in enumerate(journal['chunks']):
            path = directory / entry['file']
            if entry['index'] != index or entry['state'] != 'complete' or digest(path) != entry['sha256']:
                raise ValueError('Fragmentos incompletos o checksum incorrecto')
            audio, sr = sf.read(path, dtype='float32')
            if sr != 24000 or audio.ndim != 1 or len(audio) != entry['frames']:
                raise ValueError('Formato de fragmento incompatible')
            if arrays:
                arrays.append(np.zeros(1200, dtype='float32'))  # Explicit 50 ms pause; no phoneme overlap.
            arrays.append(audio)
        audio = np.concatenate(arrays)
        if len(audio) / 24000 > policy['max_final_seconds']:
            raise ValueError('Duración final excedida')
        guard()
        final = write_wav(job / 'chatterbox.wav', audio, 24000)
        journal.update(state='complete', final=final)
        atomic_json(manifest, journal)
        return {'seconds': final['frames'] / 24000, 'wav_sha256': final['sha256'],
                'chunks': journal['chunks'], 'tokens': sum(c['tokens'] for c in journal['chunks']),
                'eos': True}
    except BaseException as exc:
        if journal['chunks'] and journal['chunks'][-1]['state'] == 'running':
            journal['chunks'][-1].update(metrics)
            journal['chunks'][-1]['state'] = 'failed'
        journal.update(state='failed', error=type(exc).__name__)
        atomic_json(manifest, journal)
        raise
