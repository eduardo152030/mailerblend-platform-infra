#!/usr/bin/env python3
"""Instala únicamente exporters declarados de CT630/631 mediante SSH PVE verificado."""
import importlib.util,json,subprocess,shlex
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
s=importlib.util.spec_from_file_location('stage',ROOT/'scripts/phase6-stage-a.py');t=importlib.util.module_from_spec(s);s.loader.exec_module(t)
for ct,name in [(630,'infra-llm'),(631,'infra-webui')]:
 folder='/root/ia-monitoring';t.remote(ct,['mkdir','-p',folder]);t.remote(ct,['chmod','700',folder])
 for p in (ROOT/'services'/name/'monitoring').iterdir():
  if p.is_file():t.remote(ct,['tee',folder+'/'+p.name],p.read_bytes())
 args=['python3',folder+'/install-monitoring.py','--confirm-new-ct',str(ct)]
 if ct==631:args+=['--approve-containerd-socket']
 print(t.remote(ct,args).decode())
