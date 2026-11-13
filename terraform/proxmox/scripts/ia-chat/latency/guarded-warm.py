#!/usr/bin/env python3
"""PVE: carga un alias bajo guardas host21GiB y RSS/residente<90%; sin modelos simultáneos."""
import sys,importlib.util,pathlib,json
label=sys.argv[1];model=sys.argv[2];sys.argv=['validate-api.py','library'];sp=importlib.util.spec_from_file_location('api','/root/ia-local/validate-api.py');api=importlib.util.module_from_spec(sp);sp.loader.exec_module(api)
r=api.request_chat(label,model,'Responde solo OK.',max_tokens=8)
path=pathlib.Path('/root/ia-local/latency')/(label+'-memory.json');path.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'model':model,'peak_rss_gib':max(sum(p['rss'] for p in s['processes']) for s in r['samples'])/1024**3,'peak_resident_gib':max(s['ct']['630']['resident_tasks'] for s in r['samples'])/1024**3}))
