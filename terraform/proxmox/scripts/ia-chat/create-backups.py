#!/usr/bin/env python3
"""PVE: dos jobs propios, nunca modifica los ajenos."""
import subprocess,json,pathlib,datetime
def run(*args):return subprocess.run(args,text=True,capture_output=True,check=True).stdout.strip()
def jobs():return json.loads(run('pvesh','get','/cluster/backup','--output-format','json'))
before=jobs();existing={x['id']:x for x in before};created=[]
for id,vmid,schedule,retention in [('ia-chat-webui-631','631','03:30','keep-daily=7,keep-weekly=4'),('ia-chat-llm-630','630','sun 04:00','keep-weekly=4')]:
 expected={'vmid':vmid,'schedule':schedule,'storage':'storage','mode':'snapshot','compress':'zstd','enabled':1,'node':'pve','prune-backups':retention}
 if id not in existing:
  args=['pvesh','create','/cluster/backup','--id',id]
  for k,v in expected.items():args+=['--'+k,str(v)]
  run(*args);created.append(id)
 else:
  for k,v in expected.items():
   actual=existing[id].get(k)
   if k=='prune-backups' and isinstance(actual,dict):assert {key:int(value) for key,value in actual.items()}=={key:int(value) for key,value in (item.split('=') for item in retention.split(','))}
   elif k=='enabled':assert int(actual)==int(v)
   else:assert str(actual)==str(v),(id,k,'deriva: no modificar automáticamente')
after=jobs()
for old in before:
 if old['id'] not in ['ia-chat-webui-631','ia-chat-llm-630']:assert next(x for x in after if x['id']==old['id'])==old
print(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'created':created,'jobs':[x for x in after if x['id'] in ['ia-chat-webui-631','ia-chat-llm-630']],'other_jobs_unchanged':True},indent=2))
