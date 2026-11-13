#!/usr/bin/env python3
"""Operador local: sonda sintética UI y journal filtrado por ventana, sin prompts privados."""
import importlib.util,json,sys,subprocess,shlex,re,datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sp=importlib.util.spec_from_file_location('stage',ROOT/'scripts/phase6-stage-a.py');t=importlib.util.module_from_spec(sp);sp.loader.exec_module(t)
label=sys.argv[1];assert re.fullmatch('[a-z0-9-]+',label)
args=['ssh','-o','UserKnownHostsFile='+str(Path.home()/'.ssh/known_hosts'),'-o','StrictHostKeyChecking=yes','-o','BatchMode=yes','pve']
start=t.remote(630,['date','+%s']).decode().strip();model=sys.argv[3] if len(sys.argv)>3 else 'gemma-4-26b';assert model in ['gemma-4-26b','qwen3.6-35b']
cmd=['pct','exec','631','--','docker','exec','-i','-e','IA_PROBE_MODEL='+model,'ia-chat-open-webui-1','python','-',label]
if len(sys.argv)>2:cmd.append(sys.argv[2])
# A separate PVE reader checks RSS/HWM while the real UI stream runs.
watchpath='/root/ia-local/latency/watch-requests.py'
subprocess.run(args+[shlex.join(['tee',watchpath])],input=(ROOT/'scripts/ia-chat/latency/watch-requests.py').read_bytes(),stdout=subprocess.DEVNULL,check=True)
subprocess.run(args+[shlex.join(['python3','-c',"from pathlib import Path;Path('/root/ia-local/latency/"+label+".done').unlink(missing_ok=True)"])],check=True)
watcher=subprocess.Popen(args+[shlex.join(['python3',watchpath,label])],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
try:r=subprocess.run(args+[shlex.join(cmd)],input=(ROOT/'scripts/ia-chat/latency/ui-probe.py').read_bytes(),capture_output=True,timeout=7200)
finally:
 subprocess.run(args+[shlex.join(['touch','/root/ia-local/latency/'+label+'.done'])],check=True)
 watchout,watcherr=watcher.communicate(timeout=30)
assert watcher.returncode==0,'Memory guard failed during UI probe'
P=ROOT/'docs/roadmap/evidence/ia-chat-latency-2026-11-13';P.mkdir(exist_ok=True)
if r.returncode:
 private=Path.home()/'.local/share/mailerblend-recovery/ia-chat/latency';private.mkdir(parents=True,exist_ok=True,mode=0o700);(private/(label+'-error.log')).write_bytes(r.stdout+r.stderr);print('UI probe failed, private log '+str(private/(label+'-error.log')));raise SystemExit(1)
print(r.stdout.decode()[-2500:],flush=True)
result=t.remote(631,['docker','exec','ia-chat-open-webui-1','cat','/app/backend/data/.ia-latency-'+label+'.json']);(P/(label+'.json')).write_bytes(result)
logs=t.remote(630,['journalctl','-u','llama-server','--since','@'+start,'--no-pager','-o','cat']).decode()
rows=[line for line in logs.splitlines() if re.search(r'(n_tokens\s*=|n_past\s*=|prompt eval time|eval time\s*=|POST /v1/chat/completions|selected slot|processing task|release:|cache.*(tokens|size|reuse))',line)]
(P/(label+'-llama.log')).write_text('\n'.join(rows)+'\n');print('journal metric lines',len(rows),flush=True)
