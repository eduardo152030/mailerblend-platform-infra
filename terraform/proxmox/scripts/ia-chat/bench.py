#!/usr/bin/env python3
"""PVE: guarda host21GiB antes de cada carga; benchmarks secuenciales630."""
import pathlib,subprocess,json,datetime,time
out=pathlib.Path('/root/ia-local/bench');out.mkdir(exist_ok=True)
models={'gemma-4-26b':'/models/gemma-4-26b-a4b/gemma-4-26B-A4B-it-qat-UD-Q4_K_XL.gguf','qwen3.6-35b':'/models/qwen3.6-35b-a3b/Qwen3.6-35B-A3B-UD-IQ4_XS.gguf'}
for alias,model in models.items():
 for threads in [3,4]:
  dest=out/f'{alias}-t{threads}.json'
  if dest.exists():
   data=json.loads(dest.read_text());assert len(data)==2;print('Verificado existente '+dest.name,flush=True);continue
  if subprocess.run(['pct','exec','630','--','systemctl','is-active','--quiet','llama-server'],capture_output=True).returncode==0:raise SystemExit('HALT: detener primero llama-server630 antes de un benchmark real')
  available=int(next(x.split()[1] for x in pathlib.Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')))*1024
  record={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'alias':alias,'threads':threads,'host_memavailable_bytes':available}
  with (out/'guards.jsonl').open('a') as f:f.write(json.dumps(record)+'\n')
  if available<21*1024**3:raise SystemExit('HALT: MemAvailable<21GiB antes de benchmark '+alias)
  print(json.dumps(record),flush=True)
  logpath=out/f'{alias}-t{threads}.log'
  if logpath.exists():logpath.rename(out/f'{alias}-t{threads}-previous-{int(time.time())}.log')
  with logpath.open('w') as log:
   p=subprocess.run(['pct','exec','630','--','/opt/llama.cpp/build/bin/llama-bench','-m',model,'-p','512','-n','128','-t',str(threads),'-r','1','-b','512','-ub','128','--repack','0','-lm','mmap','-o','json'],capture_output=True,text=True)
   log.write(p.stderr)
  if p.returncode:raise SystemExit('HALT benchmark rc='+str(p.returncode))
  data=json.loads(p.stdout);assert len(data)==2
  dest.write_text(json.dumps(data,indent=2)+'\n')
  print('PASS '+dest.name+' '+str([(x.get('n_prompt'),x.get('n_gen'),x.get('avg_ts')) for x in data]),flush=True)
