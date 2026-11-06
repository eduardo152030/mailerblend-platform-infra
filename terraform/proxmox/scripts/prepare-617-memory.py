#!/usr/bin/env python3
"""Compatibility adapter; the shared implementation is prepare-aligned-exporters.py."""
import importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
_spec=importlib.util.spec_from_file_location('aligned_exporters',ROOT/'scripts/prepare-aligned-exporters.py')
_shared=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(_shared)
instrument=_shared.instrument
render=_shared.render

if __name__=='__main__':
    import argparse,json
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    audit=next(r for r in json.loads((ROOT/'docs/roadmap/evidence/2026-11-02-rollout-authenticated-preflight.json').read_text()) if r['ct']==617)
    print(json.dumps(render(a.output,audit),indent=2))
