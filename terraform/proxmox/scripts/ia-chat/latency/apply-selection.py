#!/usr/bin/env python3
"""Operador local: aplica únicamente la selección r3 de630 y valida alias en servicio.
No aplica Terraform ni opera otros CT. Conserva candidatos rechazados por la guarda.
"""
import json,subprocess,shlex
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'docs/roadmap/evidence/ia-chat-latency-2026-11-13';ssh=['ssh','-o','UserKnownHostsFile='+str(Path.home()/'.ssh/known_hosts'),'-o','StrictHostKeyChecking=yes','-o','BatchMode=yes','pve']
def remote(args,body=None):return subprocess.run(ssh+[shlex.join(args)],input=body,capture_output=True)
def put(path,body):
 p=remote(['tee',path],body);assert p.returncode==0
for file in ['select-benchmarks.py','guarded-warm.py','long-prompt.py','swap-report.py','template-prefix-check.py','idle-residency.py']:
 put('/root/ia-local/latency/'+file,(ROOT/'scripts/ia-chat/latency'/file).read_bytes())
p=remote(['python3','/root/ia-local/latency/select-benchmarks.py']);assert p.returncode==0,'Incomplete matrix or invalid proof'
tuning=json.loads(remote(['cat','/root/ia-local/latency/performance-tuning.json']).stdout)
put('/root/ia-local/validate-api.py',(ROOT/'scripts/ia-chat/validate-api.py').read_bytes())
put('/root/ia-local/models.ini.template',(ROOT/'services/infra-llm/config/models.ini.template').read_bytes());put('/root/ia-local/gemma-cache.jinja',(ROOT/'services/infra-llm/config/gemma-cache.jinja').read_bytes());put('/root/ia-local/install-llama.py',(ROOT/'scripts/ia-chat/install-llama.py').read_bytes())
checks=[]
for alias in ['gemma-4-26b','qwen3.6-35b']:
 accepted=False
 for i,candidate in enumerate(tuning[alias]['ranking']):
  tuning[alias].update({k:candidate[k] for k in ['batch_size','ubatch_size']});put('/root/ia-local/performance-tuning.json',json.dumps(tuning,indent=2).encode())
  p=remote(['python3','/root/ia-local/install-llama.py']);assert p.returncode==0,'Install failed; no automatic resource change'
  label='runtime-'+alias+'-'+str(i+1);p=remote(['python3','/root/ia-local/latency/guarded-warm.py',label,alias]);(OUT/(label+'.log')).write_bytes(p.stdout+p.stderr)
  if p.returncode:
   proof=remote(['cat','/root/ia-local/latency/'+label+'-memory.json'])
   # guarded-warm writes successful proof only; the API attempt retains anomaly evidence.
   check=remote(['python3','-c',"import json;d=json.load(open('/root/ia-local/validation-api.json'));r=d.get("+repr(label)+",{});print(json.dumps({'anomalies':r.get('anomalies'),'error':r.get('error')}))"]);detail=json.loads(check.stdout)
   assert detail.get('anomalies'),'Non-memory runtime failure; investigate before proceeding'
   checks.append({'alias':alias,'label':label,'candidate':candidate,'status':'REJECTED','detail':detail});continue
  p=remote(['python3','/root/ia-local/latency/long-prompt.py','long-after-'+alias,alias]);(OUT/('long-after-'+alias+'.log')).write_bytes(p.stdout+p.stderr)
  if p.returncode:
   # Do not hide a failure by selecting a fallback unless the guard itself stopped the model.
   proof=remote(['cat','/root/ia-local/latency/long-after-'+alias+'.json']);detail=json.loads(proof.stdout);assert detail.get('violations'),'Non-memory long-prompt failure'
   checks.append({'alias':alias,'label':label,'candidate':candidate,'status':'REJECTED','detail':'RSS/resident guard stopped service during3000tokens'});continue
  checks.append({'alias':alias,'label':label,'candidate':candidate,'status':'PASS','long_prompt_tokens':3000});accepted=True
  p=remote(['python3','/root/ia-local/latency/swap-report.py',alias+'-loaded-final']);assert p.returncode==0
  break
 assert accepted,'No safe candidate: do not claim complete'
(OUT/'runtime-selection.json').write_text(json.dumps(checks,indent=2)+'\n')
dest=ROOT/'services/infra-llm/config/performance-tuning.json';dest.write_text(json.dumps(tuning,indent=2)+'\n')
put('/root/ia-local/latency/performance-tuning.json',dest.read_bytes());put('/root/ia-local/performance-tuning.json',dest.read_bytes())
summary={key:{field:value[field] for field in ['batch_size','ubatch_size','threads','threads_batch']} for key,value in tuning.items()}
print(json.dumps({'runtime_validated':True,'selection':summary}))
