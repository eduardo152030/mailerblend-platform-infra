"""Candidate D083: shared language admission; no ML imports or side effects."""
import json
import hashlib
from pathlib import Path

OWNER = '1fd00418-2a79-4178-883f-af6c3f5e07ee'
LANGUAGES = {'es': 'Spanish', 'en': 'English'}


def language_name(code):
    if not isinstance(code, str) or code not in LANGUAGES:
        raise ValueError('Qwen en CT627 admite únicamente es/Spanish y en/English')
    return LANGUAGES[code]


def validate_request(request):
    language_name(request.get('language'))
    if request.get('profile_id') != OWNER or type(request.get('seed')) is not int or request['seed'] != 42:
        raise ValueError('Qwen requiere Eduardo y semilla42')
    if request.get('engine', 'qwen') != 'qwen' or request.get('model_size') != '0.6B':
        raise ValueError('Solo Qwen Base0.6B puede usar este worker/checkpoint')
    if request.get('instruct') or request.get('personality'):
        raise ValueError('Instrucciones y personalidad no habilitadas')
    if not isinstance(request.get('text'), str) or not 1 <= len(request['text']) <= 1200:
        raise ValueError('Texto Qwen debe contener1..1200caracteres')
    return request


def request_for_worker(job):
    request = validate_request(json.loads((Path(job) / 'request.json').read_text()))
    if (Path(job) / 'text.txt').read_text() != request['text']:
        raise ValueError('Request/text integrity mismatch')
    return request, language_name(request['language'])


def checkpoint_language(meta):
    """Read new metadata or a historical Spanish Qwen checkpoint, never Chatterbox."""
    if meta.get('model', {}).get('id') != 'Qwen/Qwen3-TTS-12Hz-0.6B-Base':
        raise ValueError('Checkpoint de otro motor/modelo no compatible con Qwen')
    gen = meta.get('generation', {})
    code = gen.get('language_code')
    if code is None:
        code = next((k for k, v in LANGUAGES.items() if v == gen.get('language')), None)
    if language_name(code) != gen.get('language'):
        raise ValueError('Checkpoint language code/name mismatch')
    return code


def capabilities(qwen_ready):
    # Installing a package is NOT permission or evidence of a working Chatterbox worker.
    return {'qwen': {'ready': bool(qwen_ready), 'languages': ['es', 'en'], 'model_sizes': ['0.6B']},
            'kokoro': {'ready': True}, 'piper': {'ready': True},
            'chatterbox': {'ready': False, 'reason': 'No validated isolated worker/model for CT627'},
            'chatterbox_turbo': {'ready': False, 'reason': 'No validated isolated worker/model for CT627'}}


WORKER_PROTOCOL = 'd083-es-en-v1'
EXPECTED_WORKER_SHA256 = 'a4f09cbe11652e88af1a45ab376d9634741d5953d8fba7aef2b6cff792de7c91'


def policy_fingerprint():
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
