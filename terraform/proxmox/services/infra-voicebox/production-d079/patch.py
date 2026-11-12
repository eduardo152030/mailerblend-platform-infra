"""Pinned, asserted Voicebox overlay. No weights or profile/data changes."""
from pathlib import Path

ROOT = Path("/app/backend")


def patch(name, old, new, count=1):
    p = ROOT / name
    source = p.read_text()
    if source.count(old) != count:
        raise ValueError("Source mismatch: " + name + " / " + old[:50])
    p.write_text(source.replace(old, new))


p = ROOT / "models.py"
source = p.read_text(); start = source.index("class GenerationRequest("); end = source.index("class GenerationResponse(", start)
piece = source[start:end]
if piece.count('default="1.7B"') != 1:
    raise ValueError("GenerationRequest default changed")
p.write_text(source[:start] + piece.replace('default="1.7B"', 'default="0.6B"') + source[end:])


patch("backends/__init__.py",
      "from .pytorch_backend import PyTorchTTSBackend\n\n                backend = PyTorchTTSBackend()",
      "from .isolated_backend import IsolatedQwenBackend\n\n                backend = IsolatedQwenBackend()")
patch("services/generation.py", "        tts_model = get_tts_backend_for_engine(engine)\n\n        if not tts_model.is_loaded():",
      "        if engine == 'qwen':\n            from ..backends.isolated_backend import start_context\n            start_context(generation_id)\n        tts_model = get_tts_backend_for_engine(engine)\n\n        if not tts_model.is_loaded():")
patch("services/generation.py", "        audio, sample_rate = await generate_chunked(tts_model, text, voice_prompt, **gen_kwargs)",
      "        if engine == 'qwen':\n            audio, sample_rate = await tts_model.generate(text, voice_prompt, language=language, seed=seed, instruct=instruct)\n        else:\n            audio, sample_rate = await generate_chunked(tts_model, text, voice_prompt, **gen_kwargs)")
patch("routes/generations.py", '    model_size = (data.model_size or "1.7B") if engine_has_model_sizes(engine) else None',
      '    model_size = (data.model_size or "0.6B") if engine == "qwen" else ((data.model_size or "1.7B") if engine_has_model_sizes(engine) else None)')
patch("routes/generations.py", '    """Generate speech and stream the WAV audio directly without saving to disk."""',
      '    """Generate speech and stream the WAV audio directly without saving to disk."""\n    profile = await profiles.get_profile(data.profile_id, db)\n    if _resolve_generation_engine(data, profile) == "qwen":\n        raise HTTPException(409, "Qwen requiere un trabajo persistente: usa /generate")')
# Admission errors precede row creation and protect the CPU-only deployment.
patch("routes/generations.py", '    engine = _resolve_generation_engine(data, profile)\n    try:',
      '''    engine = _resolve_generation_engine(data, profile)
    if engine not in ['qwen', 'kokoro', 'piper']:
        raise HTTPException(409, 'Motor no habilitado en CT627; usa Qwen0.6B, Kokoro o Piper')
    if engine == 'qwen':
        if data.seed is None:
            data.seed = 42
        if data.profile_id != '1fd00418-2a79-4178-883f-af6c3f5e07ee' or data.language != 'es' or data.seed not in [None,42] or data.instruct:
            raise HTTPException(400, 'Qwen requiere Eduardo/es/semilla42, sin instrucciones')
        if data.model_size not in [None, '0.6B'] or len(data.text)>1200 or data.personality:
            raise HTTPException(400, 'Selecciona Qwen0.6B, texto hasta1200caracteres y personalidad desactivada')
    try:''', count=2)
patch("routes/generations.py", '    return {"message": "Generation cancellation requested"}',
      '''    from ..services.task_queue import _running_generation_tasks
    for _ in range(350):
        if generation_id not in _running_generation_tasks:
            break
        await asyncio.sleep(.1)
    else:
        raise HTTPException(503, 'Cancelación pendiente; no iniciar otra generación')
    return {"message": "Generation cancelled; worker stopped"}''')
# Keep all model-management loads under the existing operation lock; reject other heavy TTS.
patch("backends/__init__.py", "    raw = _get_raw_model_load_func(config)",
      "    if config.engine in TTS_ENGINES and (config.engine not in ['qwen','kokoro','piper'] or (config.engine == 'qwen' and config.model_size != '0.6B')):\n        raise ValueError('Solo Qwen Base0.6B, Kokoro y Piper habilitados en CT627')\n    raw = _get_raw_model_load_func(config)")
with (ROOT / "routes/generations.py").open("a") as f:
    f.write('''\n\n@router.get('/qwen-worker/health')
async def qwen_worker_health():
    from ..backends.isolated_backend import worker_health
    return worker_health()
''')
