#!/usr/bin/env python3
"""PVE: guardia de memoria de630 durante una sonda UI; no solicita inferencia."""
import sys,pathlib,importlib.util,time,json,re,subprocess
label=sys.argv[1];assert re.fullmatch('[a-z0-9-]+',label);root=pathlib.Path('/root/ia-local/latency');done=root/(label+'.done');sys.argv=['validate-api.py','library'];sp=importlib.util.spec_from_file_location('api','/root/ia-local/validate-api.py');api=importlib.util.module_from_spec(sp);sp.loader.exec_module(api)
samples=[];violations=[]
while not done.exists():
 m=api.memory();samples.append(m)
 if max(m['ct']['630']['resident_tasks'],sum(p['rss'] for p in m['processes']),sum(p.get('hwm',p['rss']) for p in m['processes']))>=.9*m['ct']['630']['max']:violations.append('RSS/resident/HWM>=90%')
 if len({f for p in m['processes'] for f in p['model_files']})>1:violations.append('Two large models mapped')
 if violations:subprocess.run(['pct','exec','630','--','systemctl','stop','llama-server'],capture_output=True);break
 time.sleep(.5)
d={'samples':samples,'violations':violations,'pass':not violations};(root/(label+'-memory.json')).write_text(json.dumps(d,indent=2)+'\n');print(json.dumps({'label':label,'memory_pass':not violations}));assert not violations
