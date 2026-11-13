"""Candidate patch over the EXACT approved D079 app. Local preparation only."""
import argparse
from pathlib import Path


def apply(root):
    path = Path(root) / 'routes/generations.py'
    text = path.read_text()
    assert text.count("data.language != 'es'") == 2, 'Approved route guard differs'
    text = text.replace("data.language != 'es'", "data.language not in ['es', 'en']")
    text = text.replace('Qwen requiere Eduardo/es/semilla42, sin instrucciones',
                        'Qwen requiere Eduardo/es o en/semilla42, sin instrucciones')
    assert '/tts-capabilities' not in text
    text += '''\n\n@router.get('/tts-capabilities')
async def ct627_tts_capabilities():
    from ..backends.qwen_language_policy import capabilities
    from ..backends.isolated_backend import worker_health
    try:
        worker_health()
        ready = True
    except Exception:
        ready = False
    return capabilities(ready)
'''
    compile(text, str(path), 'exec')
    path.write_text(text)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--root', default='/app/backend')
    apply(parser.parse_args().root)
