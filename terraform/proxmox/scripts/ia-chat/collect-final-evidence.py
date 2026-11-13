#!/usr/bin/env python3
"""Copia solo artefactos públicos seleccionados; nunca ficheros auth/env/estado."""
import importlib.util,subprocess,shlex,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];s=importlib.util.spec_from_file_location('stage',ROOT/'scripts/phase6-stage-a.py');t=importlib.util.module_from_spec(s);s.loader.exec_module(t)
ssh=['ssh','-o','UserKnownHostsFile='+str(Path.home()/'.ssh/known_hosts'),'-o','StrictHostKeyChecking=yes','-o','BatchMode=yes','pve'];out=ROOT/'docs/roadmap/evidence/ia-chat-2026-11-13'
for name in ['validation-api.json','rag-stt-concurrent.json','reboot-verified.json','idempotence.json','final-health.json']:
 data=subprocess.check_output(ssh+[shlex.join(['cat','/root/ia-local/'+name])]);json.loads(data);(out/name).write_bytes(data)
config=t.py(631,"import sqlite3,json;d=sqlite3.connect('/opt/ia-chat/data/webui.db');keys=['audio.stt.whisper_model','audio.stt.engine','audio.tts.engine','ui.enable_signup','ui.default_interface_settings','ui.visibility','web.search.enable','web.search.engine','web.search.result_count','rag.embedding_model','rag.top_k'];c={k:(json.loads(v) if isinstance(v,(str,bytes)) else v) for k,v in d.execute('select key,value from config') if k in keys};print(json.dumps({k:c.get(k) for k in keys}))")
(out/'effective-config-final.json').write_bytes(config)
for ct,name in [(630,'infra-llm'),(631,'infra-webui')]:
 p=Path.home()/'.local/share/mailerblend-recovery/ia-chat'/name
 for file in ['verification.json','ssh/verified.json']:(out/(str(ct)+'-'+Path(file).name)).write_bytes((p/file).read_bytes())
print('Evidencia pública seleccionada actualizada')
