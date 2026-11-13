"""No automatic enablement: release receipt written only at approved deployment."""
import hashlib,json
from pathlib import Path

def chatterbox_ready(jobs,code):
    try:
        release=json.loads((Path(code)/'chatterbox-release.json').read_text())
        if release.get('enabled') is not True:return {'ready':False,'reason':'Not enabled by approved deployment'}
        env=Path(jobs).parent.parent/'chatterbox-d085'
        for rel,key in [('models/manifest.json','model_manifest_sha256'),('environment-receipt.json','environment_receipt_sha256')]:
            if hashlib.sha256((env/rel).read_bytes()).hexdigest()!=release[key]:raise ValueError('Release mismatch')
        model=json.loads((env/'models/manifest.json').read_text())
        if model.get('model_revision')!='5bb1f6ee58e50c3b8d408bc82a6d3740c2db6e18' or model.get('model_repo')!='ResembleAI/chatterbox':raise ValueError('Wrong model revision')
        receipt=json.loads((env/'environment-receipt.json').read_text())
        if receipt.get('imports')!='PASS' or receipt.get('weight_loads')!=0:raise ValueError('Dependency preflight unavailable')
        if set(release['source_hashes']) != {'agent.py','engine_policy.py','readiness.py','supervise_chatterbox.py','qwen_language_policy.py'}:raise ValueError('Incomplete controller bundle')
        if set(release['worker_hashes']) != {'worker.py','qwen_language_policy.py','d077_contract.py','chatterbox_worker.py','engine_policy.py'}:raise ValueError('Incomplete worker bundle')
        for rel,digest in release['source_hashes'].items():
            if '/' in rel or hashlib.sha256((Path(code)/rel).read_bytes()).hexdigest()!=digest:raise ValueError('Candidate source mismatch')
        for rel,digest in release['worker_hashes'].items():
            if '/' in rel or hashlib.sha256((Path(jobs).parent/'src'/rel).read_bytes()).hexdigest()!=digest:raise ValueError('Worker source mismatch')
        # The venv targets the immutable Docker Python, not the CT/PVE interpreter.
        # exists() would wrongly resolve its absolute symlink in the PVE namespace.
        interpreter=env/'venv/bin/python'
        if not (env/'venv/pyvenv.cfg').is_file() or not interpreter.is_symlink():raise ValueError('Missing isolated environment')
        if interpreter.readlink().as_posix() not in ['/usr/local/bin/python','/usr/local/bin/python3','/usr/local/bin/python3.12']:raise ValueError('Unexpected worker interpreter')
        return {'ready':True,'protocol':'d085-cb-v1','variant':'multilingual-v3','languages':['es','en']}
    except Exception:return {'ready':False,'reason':'Isolated release/dependencies/models unavailable'}
