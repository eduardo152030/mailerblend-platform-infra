#!/usr/bin/env python3
"""PVE: instala solo630; reaplicación idéntica no escribe, recarga ni reinicia."""
import pathlib,subprocess,json
root=pathlib.Path('/root/ia-local')
def run(*args,input=None):return subprocess.run(args,input=input,text=True,capture_output=True,check=True).stdout
ini=(root/'models.ini.template').read_text()
tuning=json.loads((root/'performance-tuning.json').read_text()) if (root/'performance-tuning.json').exists() else {}
for alias in ['gemma-4-26b','qwen3.6-35b']:
 if alias in tuning:
  best=tuning[alias]['threads'];best_prompt=tuning[alias]['threads_batch']
  ini=ini.replace('['+alias+']','['+alias+']\nbatch-size = '+str(tuning[alias]['batch_size'])+'\nubatch-size = '+str(tuning[alias]['ubatch_size']))
 else:
  scores={};prompt_scores={}
  for t in [3,4]:
   records=json.loads((root/'bench'/f'{alias}-t{t}.json').read_text());scores[t]=next(x['avg_ts'] for x in records if x['n_gen']==128);prompt_scores[t]=next(x['avg_ts'] for x in records if x['n_prompt']==512)
  best=max(scores,key=scores.get);best_prompt=max(prompt_scores,key=prompt_scores.get)
 ini=ini.replace('['+alias+']','['+alias+']\nthreads = '+str(best)+'\nthreads-batch = '+str(best_prompt))
 print(alias,'hilos TG',best,'hilos PP',best_prompt)
def reconcile(path,text):
 existing=subprocess.run(['pct','exec','630','--','cat',path],text=True,capture_output=True)
 if existing.returncode==0 and existing.stdout==text:return False
 run('pct','exec','630','--','tee',path,input=text);return True
changed_template=reconcile('/etc/llama/gemma-cache.jinja',(root/'gemma-cache.jinja').read_text()) if (root/'gemma-cache.jinja').exists() else False
changed_ini=reconcile('/etc/llama/models.ini',ini)
changed_unit=reconcile('/etc/systemd/system/llama-server.service',(root/'llama-server.service').read_text())
if changed_unit:run('pct','exec','630','--','systemctl','daemon-reload')
enabled=subprocess.run(['pct','exec','630','--','systemctl','is-enabled','--quiet','llama-server']).returncode==0
active=subprocess.run(['pct','exec','630','--','systemctl','is-active','--quiet','llama-server']).returncode==0
if not enabled:run('pct','exec','630','--','systemctl','enable','llama-server')
if not active:run('pct','exec','630','--','systemctl','start','llama-server')
elif changed_ini or changed_unit or changed_template:run('pct','exec','630','--','systemctl','restart','llama-server')
print(json.dumps({'changed_template':changed_template,'changed_ini':changed_ini,'changed_unit':changed_unit,'service_restarted':active and (changed_ini or changed_unit or changed_template),'active':run('pct','exec','630','--','systemctl','is-active','llama-server').strip()}))
