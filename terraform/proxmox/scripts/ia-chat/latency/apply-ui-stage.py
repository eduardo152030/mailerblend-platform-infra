#!/usr/bin/env python3
"""Operador local: aplica etapa declarada a/b/c/e/g en631 y conserva evidencia pública."""
import importlib.util,sys,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];s=importlib.util.spec_from_file_location('stage',ROOT/'scripts/phase6-stage-a.py');t=importlib.util.module_from_spec(s);s.loader.exec_module(t)
stage=sys.argv[1];assert stage in ['a','b','c','e','g']
r=t.remote(631,['docker','exec','-i','-e','IA_CHAT_PROFILE='+(ROOT/'services/infra-webui/config/chat-performance.json').read_text(),'ia-chat-open-webui-1','python','-',stage],(ROOT/'scripts/ia-chat/latency/reconcile-webui.py').read_bytes());d=json.loads(r);print(json.dumps(d));(ROOT/'docs/roadmap/evidence/ia-chat-latency-2026-11-13'/str('config-'+stage+'.json')).write_bytes(r)
