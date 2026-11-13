"""Asserted candidate-only overlay AFTER D083 patch. No deployment operation."""
from pathlib import Path

def replace(root,name,old,new,count=1):
    p=Path(root)/name;s=p.read_text();assert s.count(old)==count,(name,old[:65],s.count(old));p.write_text(s.replace(old,new))

def apply(root):
    # Original registry and history keys are retained; no SQLite migration.
    replace(root,'backends/__init__.py','from .chatterbox_backend import ChatterboxTTSBackend\n\n                backend = ChatterboxTTSBackend()',
            'from .isolated_chatterbox_backend import IsolatedChatterboxBackend\n\n                backend = IsolatedChatterboxBackend()')
    replace(root,'backends/__init__.py',"config.engine not in ['qwen','kokoro','piper']","config.engine not in ['qwen','kokoro','piper','chatterbox']")
    replace(root,'services/generation.py',"if engine == 'qwen':","if engine in ['qwen','chatterbox']:",2)
    replace(root,'routes/generations.py',"engine not in ['qwen', 'kokoro', 'piper']","engine not in ['qwen', 'kokoro', 'piper', 'chatterbox']",2)
    replace(root,'routes/generations.py',"    if engine == 'qwen':\n        if data.seed is None:","    if engine == 'chatterbox':\n        from ..backends.engine_policy import admission\n        try:\n            admission(data)\n            from ..backends.isolated_chatterbox_backend import worker_health\n            worker_health()\n        except ValueError as exc:\n            raise HTTPException(400, str(exc))\n        except Exception as exc:\n            raise HTTPException(409, str(exc))\n    if engine == 'qwen':\n        if data.seed is None:",2)
    replace(root,'routes/generations.py','if _resolve_generation_engine(data, profile) == "qwen":','if _resolve_generation_engine(data, profile) in ["qwen","chatterbox"]:')
    # D083 readiness protocol still protects Qwen; add engine-specific capabilities.
    replace(root,'routes/generations.py','    from ..backends.qwen_language_policy import capabilities','    import time\n    from ..backends.engine_policy import capabilities')
    replace(root,'routes/generations.py','        worker_health()\n        ready = True','        heartbeat = worker_health()')
    replace(root,'routes/generations.py','        ready = False\n    return capabilities(ready)','        heartbeat = {}\n    return capabilities(heartbeat, time.time())')

    # Preserve failed/completed history before rejecting an unsafe reuse of a job ID.
    for marker in ['    if (gen.status or "completed") != "failed":','    if (gen.status or "completed") != "completed":']:
        replace(root,'routes/generations.py',marker,
            "    if (gen.engine or 'qwen') in ['qwen','chatterbox']:\n        raise HTTPException(409, 'Intento conservado. Usa Generar para un nuevo trabajo explícito; no se repite Talker ni se reutilizan checkpoints automáticamente')\n"+marker)
    replace(root,'routes/generations.py','Qwen requiere un trabajo persistente: usa /generate','Motor aislado requiere un trabajo persistente: usa /generate')
    replace(root,'routes/models.py','    """Trigger download of a specific model."""',
        '    """Trigger download of a specific model."""\n    if request.model_name == "chatterbox-tts":\n        from ..backends.isolated_chatterbox_backend import worker_health\n        try:\n            worker_health()\n        except Exception as exc:\n            raise HTTPException(409, str(exc))\n        return {"message": "Chatterbox aislado ya preparado; no hay descarga ni carga automática"}')
    replace(root,'routes/models.py','    """Delete a downloaded model from the HuggingFace cache."""',
        '    """Delete a downloaded model from the HuggingFace cache."""\n    if model_name == "chatterbox-tts":\n        raise HTTPException(409, "Chatterbox se gestiona mediante mantenimiento aislado; no borrar desde esta API")')
    replace(root,'routes/models.py','            statuses.append(\n                models.ModelStatus(',
        '            if config["model_name"] == "chatterbox-tts":\n                from ..backends.isolated_chatterbox_backend import worker_health\n                try:\n                    worker_health(); downloaded = True; size_mb = 3208844550 / 2**20\n                except Exception:\n                    downloaded = False; size_mb = None\n                loaded = False; is_downloading = False\n            statuses.append(\n                models.ModelStatus(',2)

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--root',default='/app/backend');apply(p.parse_args().root)
