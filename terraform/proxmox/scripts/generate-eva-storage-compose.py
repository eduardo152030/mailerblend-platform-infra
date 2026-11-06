#!/usr/bin/env python3
"""Compile the reviewed EVA Compose with installed images and an externally preserved network."""
import argparse
import json
from pathlib import Path
import yaml

ROOT=Path(__file__).resolve().parents[1]


def compile_config(base,images):
    if set(images)!=set(base['services']):raise ValueError('Installed-image lock must cover every EVA service exactly.')
    result=__import__('copy').deepcopy(base)
    result['name']='eva-storage-recovery'
    result['networks']={'default':{'name':'eva-network','external':True}}
    for name,service in result['services'].items():
        image=images[name]
        if not image.startswith('sha256:') or len(image)!=71:raise ValueError('Only installed immutable image IDs allowed.')
        service['image']=image
        service['pull_policy']='never'
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--images',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    base=yaml.safe_load((ROOT/'services/infra-eva-assistant-bot/compose/docker-compose.yml').read_text())
    result=compile_config(base,json.loads(args.images.read_text()))
    args.output.write_text(yaml.safe_dump(result,sort_keys=False))
    print('Compiled EVA recovery model with installed images only; no engine operation.')
