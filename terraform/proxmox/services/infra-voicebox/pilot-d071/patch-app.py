"""Minimal pinned overlay: worker adapter, bounded tracked requests and engine UI entry."""
from pathlib import Path
import os
root=Path(os.environ.get('D071_ROOT','/app/backend'))
def patch(name,old,new,count=1):
 p=root/name;s=p.read_text();assert s.count(old)==count,(name,old[:60],s.count(old));p.write_text(s.replace(old,new))
patch('models.py','kokoro|piper|omnivoice','kokoro|piper|openvoice|omnivoice',4)
patch('services/profiles.py','CLONING_ENGINES = {','CLONING_ENGINES = {"openvoice", ')
patch('backends/__init__.py','    "piper": "Piper Spanish Spain",','    "piper": "Piper Spanish Spain",\n    "openvoice": "OpenVoice V2 + MeloES (CPU worker)",')
patch('backends/__init__.py','        elif engine == "piper":','        elif engine == "openvoice":\n            from .openvoice_backend import OpenVoiceBackend\n            backend = OpenVoiceBackend()\n        elif engine == "piper":')
patch('backends/__init__.py','            model_name="piper-es-es",','            model_name="openvoice-es", display_name="OpenVoice V2 + MeloES", engine="openvoice", hf_repo_id="myshell-ai/OpenVoiceV2", size_mb=340, languages=["es"],\n        ),\n        ModelConfig(\n            model_name="piper-es-es",')
patch('routes/models.py','            if config["model_name"] == "piper-es-es":','            if config["model_name"] == "openvoice-es":\n                from ..backends import get_tts_backend_for_engine\n                downloaded = get_tts_backend_for_engine("openvoice")._is_model_cached()\n                size_mb = 340 if downloaded else None\n            if config["model_name"] == "piper-es-es":',2)
patch('services/generation.py','        tts_model = get_tts_backend_for_engine(engine)\n\n        if not tts_model.is_loaded():','        if engine == "openvoice":\n            from ..backends.openvoice_backend import start_context\n            start_context(generation_id)\n        tts_model = get_tts_backend_for_engine(engine)\n\n        if not tts_model.is_loaded():')
# Enforce supported CPU engines at admission, before creating or retrying a row.
patch('routes/generations.py','logger = logging.getLogger(__name__)','''import functools
admission_lock = asyncio.Lock()
def bounded_request(fn):
    @functools.wraps(fn)
    async def call(*args, **kwargs):
        async with admission_lock:
            db = kwargs['db']
            data = kwargs.get('data')
            if data is not None:
                profile = db.query(DBVoiceProfile).filter_by(id=data.profile_id).first()
                engine = data.engine or getattr(profile, 'default_engine', None)
            else:
                gen = db.query(DBGeneration).filter_by(id=kwargs['generation_id']).first()
                engine = getattr(gen, 'engine', None)
            if engine not in ['openvoice', 'kokoro', 'piper']:
                raise HTTPException(409, 'CPU engine not enabled; select OpenVoice for the personal profile')
            if db.query(DBGeneration).filter(DBGeneration.status.in_(['generating', 'loading_model'])).count() >= 2:
                raise HTTPException(429, 'Generation queue full; wait or cancel the current job')
            return await fn(*args, **kwargs)
    return call
logger = logging.getLogger(__name__)''')
for name in ['generate_speech','retry_generation','regenerate_generation']:
 patch('routes/generations.py','async def '+name+'(', '@bounded_request\nasync def '+name+'(')
patch('routes/generations.py','    """Generate speech and stream the WAV audio directly without saving to disk."""','    """Tracked jobs are required for resource control and cancellation."""\n    raise HTTPException(409, "Use POST /generate and tracked job/audio endpoints")')
patch('routes/generations.py','    return {"message": "Generation cancellation requested"}','''    from ..services.task_queue import _running_generation_tasks
    for _ in range(100):
        if generation_id not in _running_generation_tasks:
            break
        await asyncio.sleep(.1)
    else:
        raise HTTPException(503, 'Cancellation not finished; do not start another job')
    if gen.engine == 'openvoice':
        from ..backends import get_tts_backend_for_engine
        state = await get_tts_backend_for_engine('openvoice').api('/generations/'+generation_id+'/cancel', {})
        if state['active_jobs'] != 0:
            raise HTTPException(503, 'Worker still active')
    return {"message": "Generation cancelled; worker stopped"}''')
# Hard block all QwenCPU loads, including model management routes, without deleting weights.
patch('backends/pytorch_backend.py','                if model_size != "0.6B":','                raise ValueError("Qwen CPU disabled after D070; use OpenVoice")\n                if model_size != "0.6B":')
# Separate internal metrics/readiness proxy; no Prometheus configuration changes required.
p=root/'routes/generations.py'
with p.open('a') as f:f.write('''\n\n@router.get('/worker/health')\nasync def worker_health():\n    from ..backends import get_tts_backend_for_engine\n    return await get_tts_backend_for_engine('openvoice').api('/health')\n\n@router.get('/worker/metrics')\nasync def worker_metrics():\n    from fastapi.responses import PlainTextResponse\n    import urllib.request,os\n    def read():\n        return urllib.request.urlopen(os.environ.get('OPENVOICE_URL','http://openvoice:8080')+'/metrics',timeout=5).read().decode()\n    return PlainTextResponse(await asyncio.to_thread(read))\n''')
