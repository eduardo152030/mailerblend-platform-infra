#!/usr/bin/env python3
"""Dentro de imagen WebUI: cachea revisiones fijas antes del primer arranque offline.
Ejecutar como entrada python de compose run, datos persistentes montados. Sin tokens.
"""
import os,json
from pathlib import Path
from huggingface_hub import snapshot_download
os.umask(0o077)
models=[('intfloat/multilingual-e5-small','614241f622f53c4eeff9890bdc4f31cfecc418b3','embedding',['config.json','modules.json','sentence_bert_config.json','sentencepiece.bpe.model','special_tokens_map.json','tokenizer*','vocab.txt','1_Pooling/*','model.safetensors','pytorch_model.bin']),('Systran/faster-whisper-small','536b0662742c02347bc0e980a01041f333bce120','whisper',None)]
for repo,revision,kind,patterns in models:
 cache=Path('/app/backend/data/cache')/kind/'models';path=Path(snapshot_download(repo,revision=revision,cache_dir=str(cache),allow_patterns=patterns,token=False))
 assert path.name==revision
 # Applications use model names with local_files_only and resolve refs/main.
 reference=path.parent.parent/'refs/main';reference.parent.mkdir(exist_ok=True);reference.write_text(revision);reference.chmod(0o600)
 print(json.dumps({'repo':repo,'revision':revision,'cache_ready':True}))
