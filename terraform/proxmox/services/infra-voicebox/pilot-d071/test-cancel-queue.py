"""PVE acceptance test: bounded admission and cancellation during native conversion."""
import json,time,urllib.request,urllib.error,subprocess
from pathlib import Path
BASE='http://192.168.1.127:17493';out=Path('/root/voicebox-d071/cancel-queue-02');out.mkdir(mode=0o700,exist_ok=False)
def api(path,value=None):
 with urllib.request.urlopen(urllib.request.Request(BASE+path,data=None if value is None else json.dumps(value).encode(),headers={'Content-Type':'application/json'}),timeout=15) as r:return json.load(r)
def ct(code):return json.loads(subprocess.check_output(['pct','exec','627','--','python3','-c',code],timeout=15))
request={'profile_id':'1fd00418-2a79-4178-883f-af6c3f5e07ee','engine':'openvoice','language':'es','text':'Hola, soy Eduardo Velázquez. Esta es una prueba de mi voz generada mediante inteligencia artificial.','personality':False,'max_chunk_chars':200}
result={'status':'IN_PROGRESS'};ids=[]
try:
 before=ct("import subprocess,json;c=json.loads(subprocess.check_output(['docker','inspect','voicebox','voicebox-openvoice']));print(json.dumps([(x['Id'],x['State']['StartedAt']) for x in c]))")
 first=api('/generate',request)['id'];ids.append(first);second=api('/generate',request)['id'];ids.append(second);result.update(first=first,queued=second)
 try:api('/generate',request);raise AssertionError('Third request accepted beyond queue limit')
 except urllib.error.HTTPError as e:assert e.code==429;result['third_request_http']=429
 result['queued_cancel']=api('/generate/'+second+'/cancel',{})
 start=time.monotonic();native=None
 while time.monotonic()-start<100:
  code="from pathlib import Path;import json;rows=[]\nfor p in Path('/srv/voicebox/openvoice/jobs').glob('*/state.json'):\n d=json.loads(p.read_text())\n if d.get('parent_generation_id')=="+repr(first)+":\n  rows.append({'id':d['id'],'pid':d.get('pid'),'stages':json.loads((p.parent/'progress.json').read_text()) if (p.parent/'progress.json').exists() else []})\nprint(json.dumps(rows))"
  rows=ct(code)
  if rows and any(x['stage']=='owner_embedding_extracted' for x in rows[0]['stages']) and not any(x['stage']=='converted' for x in rows[0]['stages']):native=rows[0];break
  time.sleep(.5)
 assert native and native['pid'],'Did not observe native conversion phase'
 result['worker_before_cancel']=native;t=time.monotonic();result['running_cancel']=api('/generate/'+first+'/cancel',{});result['cancel_seconds']=time.monotonic()-t
 assert api('/history/'+first)['status']=='failed' and api('/history/'+second)['status']=='failed'
 code="import subprocess,json;c=json.loads(subprocess.check_output(['docker','inspect','voicebox','voicebox-openvoice']));print(json.dumps([(x['Id'],x['State']['StartedAt']) for x in c]))";after=ct(code);assert after==before
 check="import os,json;from pathlib import Path\ntry:os.kill("+str(native['pid'])+",0);alive=True\nexcept ProcessLookupError:alive=False\nprint(json.dumps({'inference_pid_alive':alive,'worker_memory_current':int(Path('/sys/fs/cgroup/memory.current').read_text()),'worker_memory_stat':dict(line.split() for line in Path('/sys/fs/cgroup/memory.stat').read_text().splitlines())}))"
 check=json.loads(subprocess.check_output(['pct','exec','627','--','docker','exec','voicebox-openvoice','python','-c',check]));result['after']=check;assert not check['inference_pid_alive'],'Inference PID remains alive';assert int(check['worker_memory_stat']['anon'])<150*2**20,'Anonymous worker memory remains high'
 result.update(status='PASS',after=check,service_container_ids_unchanged=True,service_started_at_unchanged=True,profiles=len(api('/profiles')))
except BaseException as e:
 result.update(status='FAIL',reason=str(e))
 for ident in ids:
  try:api('/generate/'+ident+'/cancel',{})
  except Exception:pass
 subprocess.run(['pct','exec','627','--','bash','/opt/voicebox/pilot-d071/rollback.sh'],check=True,timeout=120);result['rollback']='PASS'
finally:(out/'result.json').write_text(json.dumps(result,indent=2));print(json.dumps(result),flush=True)
