#!/usr/bin/env python3
"""Recalcular mínimos FP32 desde conteos de tensores fijados; no descargar ni cargar modelos."""
import json
from pathlib import Path
p=Path(__file__).resolve().parents[1]/'services/infra-voicebox/qwen-resource-budget.json';d=json.loads(p.read_text());budgets={}
for m in d['measurements']:
 expected=sum(m['parameters_by_dtype'].values())*4;assert expected==m['fp32_parameter_bytes'];budgets[m['repo']]=budgets.get(m['repo'],0)+expected
for repo,size in budgets.items():
 print(json.dumps({'repo':repo,'fp32_weights_bytes':size,'fp32_weights_gib':round(size/2**30,4),'ct_ceiling_bytes':4*2**30,'exceeds_ceiling_before_runtime':size>4*2**30,'actual_inference_test':False}))
 assert size>4*2**30
